import os
import configparser
import logging

import requests
import telebot

from ysk import speech_to_text

from triton_client import triton_client

logging.basicConfig(level=logging.DEBUG)

parser = configparser.ConfigParser()
parser.read("config.ini")
ACCESS_KEY = parser["telegram"]["key"]

bot = telebot.TeleBot(ACCESS_KEY, num_threads=4)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    logging.debug(message)
    bot.reply_to(message, "Здравствуйте, поговорите что-нибудь, а я попробую это превратить в текст.")


@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):

    logging.debug(message)
    fromname = message.from_user.username

    try:
        file_info = bot.get_file(message.voice.file_id)
        fbytes = bot.download_file(file_info.file_path)
        with open('new_file.ogg', 'wb') as wb:
            wb.write(fbytes)

        try:
            text = triton_client(protocol='http', batch_size=1, async_mode=False)
            logging.debug(f"This is what I heard: [%s]" % text)
            bot.reply_to(message, "Я распознал это так: [" + str(text) + "]")
        except Exception as se:
            logging.error("STT failed: %s" % str(se), exc_info=True)
            raise se

    except Exception as e:
        logging.error("Can't save voice", exc_info=True)
        bot.reply_to(message, "Не получилось ответить по этой причине: [%s]" % str(e))


@bot.message_handler(content_types=["text"])
def handle_text(message: telebot.types.Message):
    logging.debug(message)
    bot.reply_to(message, "Увы, бот воспринимает только голос и команды, начинающиеся на \"/\".")


bot.polling()