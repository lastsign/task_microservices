FROM python

RUN mkdir /app
COPY bot.py ysk.py triton_client.py requirements.txt config.ini /app/

WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install pytelegrambotapi tritonclient geventhttpclient SoundFile pyyaml --upgrade

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc libsndfile1 

EXPOSE 50051
ENTRYPOINT [ "python", "bot.py" ]
