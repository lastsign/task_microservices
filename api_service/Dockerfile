FROM python

RUN mkdir /service
COPY protobufs/ /service/protobufs/
COPY api_service/ /service/api_service/
COPY ca.pem /service/api_service/

WORKDIR /service/api_service
RUN pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
           --grpc_python_out=. ../protobufs/api_service.proto
RUN openssl req -nodes -newkey rsa:4096 -subj /CN=api_service \
                -keyout server.key -out server.csr
RUN --mount=type=secret,id=ca.key \
    openssl x509 -req -in server.csr -CA ca.pem -CAkey /run/secrets/ca.key \
                 -set_serial 1 -out server.pem

EXPOSE 50051
ENTRYPOINT [ "python", "api_service.py" ]
