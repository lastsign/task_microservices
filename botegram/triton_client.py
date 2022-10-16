import soundfile
import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import yaml, sys, time, json, argparse
import numpy as np
import tritonclient.http

from functools import partial
from tritonclient.utils import np_to_triton_dtype, InferenceServerException
from utils.speech_utils import AudioSegment, postprocess


def request_generator(prtc_client, batch_audio_samples, batch_max_num_audio_samples):
    inputs=[]    
    inputs.append(prtc_client.InferInput("AUDIO_SIGNAL", batch_audio_samples.shape, np_to_triton_dtype(batch_audio_samples.dtype)))
    inputs.append(prtc_client.InferInput("NUM_SAMPLES", batch_max_num_audio_samples.shape, np_to_triton_dtype(batch_max_num_audio_samples.dtype)))
    inputs[0].set_data_from_numpy(batch_audio_samples)
    inputs[1].set_data_from_numpy(batch_max_num_audio_samples)

    outputs=[]
    outputs.append(prtc_client.InferRequestedOutput("TRANSCRIPT"))
    
    return inputs, outputs


def audio_batch_generator_from_file(prtc_client, batch_size, audio_idx, filenames):
    last_request = False
    batch_audio_samples=[]
    batch_num_audio_samples=[]
    batch_filenames=[]
    batch_max_num_audio_samples = 0
    
    os.system(f"ffmpeg -y -i {filenames[audio_idx]}.ogg -vn {filenames[audio_idx]}.wav")
    os.system(f"ffmpeg -y -i {filenames[audio_idx]}.wav -af \"highpass=f=200, lowpass=f=3000\" {filenames[audio_idx]}_200_3000.wav")
    filenames[audio_idx] += "_200_3000"
    os.system(f"ffmpeg -y -i {filenames[audio_idx]}.wav -af \"aformat=sample_fmts=s16:sample_rates=16000\" {filenames[audio_idx]}_16_16000.wav")
    filenames[audio_idx] += "_16_16000"

    for _ in range(batch_size):
        filename = filenames[audio_idx]
        audio = AudioSegment.from_file(f'{filename}.wav', offset=0, duration=0).samples.astype("float16")

        audio_idx = (audio_idx + 1) % len(filenames)
        if audio_idx == 0:
            last_request = True

        batch_audio_samples.append(audio) 
        batch_num_audio_samples.append(len(audio))
        batch_filenames.append(filename)
        
    max_num_samples = max([len(x) for x in batch_audio_samples])

    batch_audio_samples = np.asarray(list(map(lambda x: np.concatenate((x, np.random.normal(np.mean(x), np.std(x), max_num_samples - len(x)))), batch_audio_samples))).astype("float16")  
    batch_max_num_audio_samples = np.expand_dims(np.full(batch_size, max_num_samples).astype("int32"), axis=1) 

    inputs, outputs = request_generator(prtc_client, batch_audio_samples, batch_max_num_audio_samples)

    return audio_idx, inputs, outputs, last_request

def triton_client(protocol, batch_size):

    model_name = "jasper-onnx-ensemble"

    print("==")
    print("protocol: {}".format(protocol))
    print("batch size: {}".format(batch_size))
    
    if batch_size > 8: raise ValueError("batch size must be <= 8 for model")
    
    filter_speed = 1
    labels = [" ", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "'", "<BLANK>"]
    prtc_client = tritonclient.http
    url = "triton_service:8000"

    try:
        triton_client = prtc_client.InferenceServerClient(url=url, verbose=True)
    except Exception as e:
        print("Failed to create the client: {}".format(e))
    print("Is the client alive? ", triton_client.is_server_live())
    print("==\n")

    with open("jasper_10x5dr.yaml", 'r') as r:
        try:
            cfg = yaml.safe_load(r)
        except yaml.YAMLError as err:
            print(err)
    
    filenames = []
    req_cnt = 0
    audio_idx = 0
    last_request = False
    
    filenames = ['new_file']
    print("{} audio files are chosen for simiplicity.".format(len(filenames)))
    print("Start inferenceing ...")
    time.sleep(3)
    
    while not last_request:
        
        audio_idx, inputs, outputs, last_request = audio_batch_generator_from_file(prtc_client, batch_size, audio_idx, filenames)
        
        req_cnt += 1 
        stime = time.time()
        try:

            result = triton_client.infer(model_name=model_name, 
                                            inputs=inputs, 
                                            request_id=str(req_cnt),
                                            outputs=outputs)

            etime = time.time()
            req_id = result.get_response()['id']
            prediction = result.as_numpy("TRANSCRIPT")
            results = postprocess(prediction, labels)
            print("==")
            print("request_id: {}".format(req_id))
            print("batch_size: {}".format(batch_size))
            print("inference time: {} ms".format(etime - stime))
            print("==")
            print("Inference is done.")
            return results

        except InferenceServerException as err:
            print("Inference failed: " + str(err))
