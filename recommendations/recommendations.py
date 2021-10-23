from concurrent import futures
import random

import grpc
from grpc_interceptor import ExceptionToStatusInterceptor
from grpc_interceptor.exceptions import NotFound
import mysql.connector
import json

from recommendations_pb2 import (
    Data,
    DataResponse,
    Empty,
    EmptyResponse
)
import recommendations_pb2_grpc


class RecommendationService(recommendations_pb2_grpc.RecommendationsServicer):

    def Recommend(self, request, context):
        mydb = mysql.connector.connect(
            host="mysqldb",
            user="root",
            password="p@ssw0rd1",
            database="inventory"
        )
        cursor = mydb.cursor()
        cursor.execute(f"SELECT * FROM data WHERE id={int(request.id)}")
        exe = cursor.fetchone()
        cursor.close()
        return DataResponse(rec=[Data(id=exe[0], a=exe[1], b=exe[2])])

    def Init(self, request, context):

        mydb = mysql.connector.connect(
            host="mysqldb",
            user="root",
            password="p@ssw0rd1"
        )
        cursor = mydb.cursor()

        cursor.execute("DROP DATABASE IF EXISTS inventory")
        cursor.execute("CREATE DATABASE inventory")
        cursor.close()

        mydb = mysql.connector.connect(
            host="mysqldb",
            user="root",
            password="p@ssw0rd1",
            database="inventory"
        )
        cursor = mydb.cursor()

        cursor.execute("DROP TABLE IF EXISTS data")
        cursor.execute("CREATE TABLE data (id INTEGER AUTO_INCREMENT PRIMARY KEY, a DOUBLE, b DOUBLE)")
        for i in range(1000):
            cursor.execute(f"INSERT INTO data (a, b) VALUES ({random.uniform(-2., 2.)}, {random.uniform(-2., 2.)})")
        mydb.commit()
        cursor.close()
        return EmptyResponse(res=[Empty()])


def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    recommendations_pb2_grpc.add_RecommendationsServicer_to_server(
        RecommendationService(), server
    )

    with open("server.key", "rb") as fp:
        server_key = fp.read()
    with open("server.pem", "rb") as fp:
        server_cert = fp.read()
    with open("ca.pem", "rb") as fp:
        ca_cert = fp.read()

    creds = grpc.ssl_server_credentials(
        [(server_key, server_cert)],
        root_certificates=ca_cert,
        require_client_auth=True,
    )
    server.add_secure_port("[::]:55051", creds)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
