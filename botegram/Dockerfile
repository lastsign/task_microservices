FROM python

RUN mkdir /app
COPY bot.py /app/
COPY ysk.py /app/
COPY triton_client.py /app/
COPY requirements.txt /app/


WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install pytelegrambotapi --upgrade
RUN pip install tritonclient --upgrade
RUN pip install geventhttpclient --upgrade
RUN pip install SoundFile --upgrade
RUN pip install pyyaml --upgrade

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc libsndfile1 

EXPOSE 50051
ENTRYPOINT [ "python", "bot.py" ]
