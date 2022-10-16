import configparser
import logging
from aiogram import Dispatcher, Bot, types

logging.basicConfig(level=logging.DEBUG)

parser = configparser.ConfigParser()
parser.read("config.ini")
TOKEN = parser["telegram"]["key"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    logging.debug(message)
    await message.answer(message, "Здравствуйте, поговорите что-нибудь, а я попробую это превратить в текст.")

@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    filename = str(uuid.uuid4())
    file_name_full="./voice/"+filename+".ogg"
    file_name_full_converted="./ready/"+filename+".wav"
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    print(f'filename {filename}\nfile_name_full {file_name_full}\nfile_name_full_converted {file_name_full_converted}\nfile_info {file_info}')
    with open(file_name_full, 'wb') as new_file:
        new_file.write(downloaded_file)
    os.system("ffmpeg -i "+file_name_full+"  "+file_name_full_converted)