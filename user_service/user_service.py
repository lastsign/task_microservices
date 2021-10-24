import os

from flask import Flask, render_template, request, send_from_directory
import grpc
import numpy as np
import random

from api_service_pb2 import Data, DataRequest, Empty, EmptyRequest
from api_service_pb2_grpc import ApiServiceStub

app = Flask(__name__)

api_service_host = os.getenv("API_SERVICE_HOST", "localhost")
with open("client.key", "rb") as fp:
    client_key = fp.read()
with open("client.pem", "rb") as fp:
    client_cert = fp.read()
with open("ca.pem", "rb") as fp:
    ca_cert = fp.read()
creds = grpc.ssl_channel_credentials(ca_cert, client_key, client_cert)
api_service_channel = grpc.secure_channel(
    f"{api_service_host}:55051", creds
)
api_service_client = ApiServiceStub(api_service_channel)

@app.route("/", methods=['GET', 'POST'])
def render_homepage():
    if request.method == 'POST':
        api_service_request = DataRequest(id=random.randrange(1, 1001))
        api_service_response = api_service_client.Get(api_service_request)
        text = request.form['query']
        if request.form.get('action1') == 'Score':
            a = api_service_response.rec[0].a
            b = api_service_response.rec[0].b
            try:
                c = float(text)
            except ValueError:
                c = random.uniform(-2, 2)
            return render_template(
                "homepage.html",
                text=f'{round(1 / (1 + np.exp(-(a + b + c))), 6)}',
                label=f'sigmoid score',
                numbers=[f'a: {round(a, 6)}', f'b: {round(b, 6)}', f'c: {round(c, 6)}']
            )
    elif request.method == 'GET':
        api_service_request = EmptyRequest()
        api_service_client.Init(api_service_request)
        return render_template(
            "homepage.html",
            text='', label='', numbers=''
        )
