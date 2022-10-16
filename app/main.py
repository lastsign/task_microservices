import os
import requests

from fastapi import FastAPI
from pydantic import BaseModel

import configparser
import logging

import telebot

from ysk import speech_to_text

logging.basicConfig(level=logging.DEBUG)

parser = configparser.ConfigParser()
parser.read("config.ini")
ACCESS_KEY = parser["telegram"]["key"]

bot = telebot.TeleBot(ACCESS_KEY, num_threads=6)

app = FastAPI()

class ContactForm(BaseModel):
    name: str
    email: str
    message: str

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "johndoe@example.com",
                "message": "I need your help."
            }
        }


@app.post("/")
async def contact_telegram(contact_form: ContactForm):
    url = 'https://api.telegram.org/bot{}/sendMessage'.format(ACCESS_KEY)

    name = contact_form.name
    email = contact_form.email
    message = contact_form.message

    text = "{}\n{}\n\n{}".format(name, email, message)

    params = {
        'chat_id': CHAT_ID,
        'text': text,
        'disable_web_page_preview': True,
        'protect_content': True
    }

    r = requests.get(url, params=params)

    return {"message": "Message sent successfully."}

@bot.message_handler(content_types=["text"])
def handle_text(message: telebot.types.Message):
    logging.debug(message)
    bot.reply_to(message, "Увы, бот воспринимает только голос и команды, начинающиеся на \"/\".")