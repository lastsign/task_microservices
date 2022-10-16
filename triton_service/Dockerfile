FROM python

RUN mkdir /app
COPY bot.py /app/
COPY ask.py /app/
COPY triton_client.py /app/

WORKDIR /app
# RUN pip install -r requirements.txt

EXPOSE 50051
ENTRYPOINT [ "python", "bot.py" ]
