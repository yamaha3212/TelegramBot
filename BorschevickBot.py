import telebot
import os
import inspect
import sys
from PIL import Image
import face_recognition
import numpy as np
from io import BytesIO
import random
import sqlite3

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

try:
    os.mkdir(get_my_dir() + os.path.sep + 'voice')
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
        con = sqlite3.connect('chatvoices.db')
        cur = con.cursor()
        try:
            cur.execute('''CREATE TABLE voisemessages
                           (uid integer, voicemessage text)''')
        except sqlite3.OperationalError:
            pass
        bot.reply_to(message, "Сохраню это на сервере и попрошу кого-нибудь перевести, ведь я понимаю только латинский "
                              "язык. " + ORDINATA[random.randint(0, len(ORDINATA) - 1)])
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        try:
            os.mkdir(get_my_dir() + os.path.sep + 'voice' + os.path.sep + str(message.chat.id), mode=777)
        except FileExistsError:
            pass
        cur.execute(f'SELECT * FROM voisemessages WHERE uid={message.chat.id}')
        results = cur.fetchall()
        src = get_my_dir() + os.path.sep + 'voice' + os.path.sep + str(message.chat.id) + os.path.sep + f'audio_message_{len(results)}.wav '
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        cur.execute(
            f"INSERT INTO voisemessages (uid, voicemessage) VALUES ({message.chat.id}, 'audio_message_{len(results)}.wav ')")
        con.commit()
    except Exception as e:
        bot.reply_to(message, str(e))


bot.infinity_polling()
