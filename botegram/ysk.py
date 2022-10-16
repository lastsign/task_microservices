# -*- coding: utf-8 -*-
"""
    All YandexSpeechKit-related stuff is here
"""

import json
import urllib.request

import asyncio

# import grpc
# from grpc import aio

# from tritonclient.grpc import service_pb2 as predict_pb2
# from tritonclient.grpc import service_pb2_grpc as prediction_service_pb2_grpc

import argparse
import sys

import tritonclient.http as httpclient
from tritonclient.utils import InferenceServerException

# # This called from an asyncio event loop as normal.
# def async my_infer(image_np):
#     async with aio.insecure_channel("localhost:8001") as channel:
#     stub = prediction_service_pb2_grpc.GRPCInferenceServiceStub(channel)
#     # Setup the request with input/outputs as normal (not shown to simplify).
#             # ...
#         response  = await stub.ModelInfer(request)
#     return response

def speech_to_text(filename=None, bytes=None, topic='general', lang='ru-RU', key=None):

    # choosing the source of bytes for sending to the STT system
    if filename is not None:
        with open(filename, "rb") as f:
            data = f.read()
    elif bytes is not None:
        data = bytes
    else:
        raise Exception("Neither filename nor byte representation are passed to the STT method.")

    params = "&".join([f"topic={topic}", f"lang={lang}"])

    try:
        triton_client = httpclient.InferenceServerClient(url="localhost:8000",
                                                         verbose=True)
    except Exception as e:
        print("context creation failed: " + str(e))
        sys.exit(1)
    
    model_name = 'simple'

    # There are seven models in the repository directory
    if len(triton_client.get_model_repository_index()) != 7:
        sys.exit(1)

    triton_client.load_model(model_name)
    if not triton_client.is_model_ready(model_name):
        sys.exit(1)

    # Request to load the model with override config in original name
    # Send the config with wrong format
    try:
        config = "\"parameters\": {\"config\": {{\"max_batch_size\": \"16\"}}}"
        triton_client.load_model(model_name, config=config)
    except InferenceServerException as e:
        if "failed to load" not in e.message():
            sys.exit(1)
    else:
        print("Expect error occurs for invald override config.")
        sys.exit(1)

    # Send the config with the correct format
    config = "{\"max_batch_size\":\"16\"}"
    triton_client.load_model(model_name, config=config)

    # Check that the model with original name is changed.
    # The value of max_batch_size should be changed from "8" to "16".
    updated_model_config = triton_client.get_model_config(model_name)
    if updated_model_config['max_batch_size'] != 16:
        print("Expect max_batch_size = 16, got: {}".format(
            updated_model_config['max_batch_size']))
        sys.exit(1)

    triton_client.unload_model(model_name)
    if triton_client.is_model_ready(model_name):
        sys.exit(1)

    # Trying to load wrong model name should emit exception
    try:
        triton_client.load_model("wrong_model_name")
    except InferenceServerException as e:
        if "failed to load" in e.message():
            print("PASS: model control")
    else:
        sys.exit(1)
    # url = urllib.request.Request("0.0.0.0:8000", data=data)
    # # url.add_header("Authorization", "Api-Key %s" % key)
    # url.add_header("Transfer-Encoding", "chunked")

    # response_data = urllib.request.urlopen(url).read().decode('UTF-8')
    # decoded_data = json.loads(response_data)

    # if decoded_data.get("error_code") is None:
    #     return decoded_data.get("result")
    # else:
    #     raise Exception(json.dumps(decoded_data))