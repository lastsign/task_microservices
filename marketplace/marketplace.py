import os

from flask import Flask, render_template, request
import grpc
import numpy as np
import random

from recommendations_pb2 import Data, DataRequest, Empty, EmptyRequest
from recommendations_pb2_grpc import RecommendationsStub

app = Flask(__name__)

recommendations_host = os.getenv("RECOMMENDATIONS_HOST", "localhost")
with open("client.key", "rb") as fp:
    client_key = fp.read()
with open("client.pem", "rb") as fp:
    client_cert = fp.read()
with open("ca.pem", "rb") as fp:
    ca_cert = fp.read()
creds = grpc.ssl_channel_credentials(ca_cert, client_key, client_cert)
recommendations_channel = grpc.secure_channel(
    f"{recommendations_host}:55051", creds
)
recommendations_client = RecommendationsStub(recommendations_channel)


@app.route("/", methods=['GET', 'POST'])
def render_homepage():
    if request.method == 'POST':
        recommendations_request = DataRequest(id=random.randrange(1, 1001))
        recommendations_response = recommendations_client.Recommend(
            recommendations_request
        )
        text = request.form['query']
        if request.form.get('action1') == 'Score':
            a = recommendations_response.rec[0].a
            b = recommendations_response.rec[0].b
            try:
                c = float(text)
            except ValueError:
                c = random.uniform(-2, 2)
            return render_template(
                "homepage.html",
                recommendations=f'{round(1 / (1 + np.exp(-(a + b + c))), 6)}'
            )
    elif request.method == 'GET':
        recommendations_request = EmptyRequest()
        recommendations_response = recommendations_client.Init(
            recommendations_request
        )
        return render_template(
            "homepage.html",
            recommendations=f'init db'
        )
