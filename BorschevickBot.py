import telebot
import os
import inspect
import sys
from PIL import Image
import face_recognition
import numpy as np
from io import BytesIO

bot = telebot.TeleBot("2147259007:AAEVsREyP6oCv5-YCxIyk45DyoTtW-4ui1s", parse_mode=None)


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
def handle_docs_photo(message):
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


bot.infinity_polling()
