import telebot
import os
import inspect
import sys
from PIL import Image
import face_recognition
import numpy as np
from io import BytesIO
import random
from time import time
import librosa
import io
import soundfile as sf
from scipy.io.wavfile import read, write

bot = telebot.TeleBot("2147259007:AAEVsREyP6oCv5-YCxIyk45DyoTtW-4ui1s", parse_mode=None)
ORDINATA = ['Ars longa, vita brevis.',
            'Per aspera ad astra.',
            'Usus est optimus magister.',
            'Contra malum mortis non est medicamentum in hortis.',
            'Alea jacta est.',
            'Non ducor, duco.',
            'Etiam si omnes, ego non.']

def show_faces(face_locations, image, message):
    for face_location in face_locations:
        top, right, bottom, left = face_location

        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        pil_image.save('FindedFace.jpg')
        photo = open('FindedFace.jpg', 'rb')
        bot.send_photo(message.chat.id, photo, 'Лицо с этой фотографии:', message.id)


def get_my_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False):
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_my_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


try:
    os.mkdir(get_my_dir() + os.path.sep + 'photos')
except FileExistsError:
    pass


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        bot.reply_to(message, "Сейчас поищу лица на этой фотографии...")
        image = np.array(Image.open(BytesIO(downloaded_file)))
        face_locations = face_recognition.face_locations(image)

        if len(face_locations) > 0:
            src = get_my_dir() + os.path.sep + file_info.file_path
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.reply_to(message, "Я вижу людей на этой фотографии, сохраню ее на сервере для дальнейших исследований")
            show_faces(face_locations, image, message)

        else:
            bot.reply_to(message, "Кажется, на этой фотографии нет лиц... ну или человеческих лиц")

    except Exception as e:
        bot.reply_to(message, str(e))


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        bot.reply_to(message, "Сохраню это на сервере и попрошу кого-нибудь перевести, ведь я понимаю только латинский язык. " + ORDINATA[random.randint(0, len(ORDINATA) - 1)])
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        #FIXME
        #signal_gm = np.frombuffer(downloaded_file, dtype='float64')
        #sf.write('new_file.wav', signal_gm, 16000)
        #FIXME

        try:
            os.mkdir(get_my_dir() + os.path.sep + str(message.chat.id))
        except FileExistsError:
            pass
        with open(f'{message.chat.id}_{int(time())}.wav', 'wb') as new_file:
            new_file.write(downloaded_file)
    except Exception as e:
        bot.reply_to(message, str(e))


bot.infinity_polling()
