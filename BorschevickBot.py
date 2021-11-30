import telebot
import os
import inspect
import sys

bot = telebot.TeleBot("2147259007:AAEVsREyP6oCv5-YCxIyk45DyoTtW-4ui1s", parse_mode=None)


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

        src = get_my_dir() + os.path.sep + file_info.file_path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, "Фото добавлено")

    except Exception as e:
        bot.reply_to(message, str(e))


bot.infinity_polling()
