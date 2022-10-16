FROM python

RUN mkdir /app
COPY botegram/ /app/

WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r requirements.txt --upgrade

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc libsndfile1 ffmpeg

WORKDIR /app/botegram/

EXPOSE 50051
ENTRYPOINT ["python", "bot.py"]