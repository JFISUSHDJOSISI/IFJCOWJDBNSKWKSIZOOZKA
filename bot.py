import os
import time
import telebot
import requests
import random
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from telebot import types

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
BOT_TOKEN = '7147982361:AAFRdFskA7pN7c5okQnfElGDnDCgQDBeH80'

bot = telebot.TeleBot(BOT_TOKEN)

def create_session_with_retries():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def get_random_emoji():
    # Список эмодзи для рандомного выбора
    emojis = ['🔥', '⚡', '☀️', '💥', '🌠', '✨', '🎊', '🎉', '🚀', '🌟']
    return random.choice(emojis)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот для скачивания файлов. Просто отправь мне прямую ссылку на файл, и я скачаю его для тебя.")

@bot.message_handler(func=lambda message: True)
def download_file(message):
    url = message.text.strip()

    if not url.startswith(('http://', 'https://')):
        bot.reply_to(message, "Пожалуйста, отправьте корректную ссылку, начинающуюся с http:// или https://")
        return

    try:
        # Отправляем сообщение о начале скачивания
        status_message = bot.reply_to(message, "Начинаю скачивание файла...")

        # Создаем сессию с повторными попытками
        session = create_session_with_retries()

        # Скачиваем файл с заголовками
        response = session.get(url, stream=True)
        response.raise_for_status()

        # Получаем имя файла из заголовка Content-Disposition, если оно есть
        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition:
            filename = content_disposition.split('filename=')[-1].strip('"')
        else:
            # Если Content-Disposition отсутствует, используем имя файла из URL
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = 'file.bin'  # Используем 'file.bin', если имя не определено

        # Получаем размер файла
        total_size = int(response.headers.get('content-length', 0))

        # Инициализируем переменные для отслеживания прогресса
        block_size = 12500000  # 12,5 МБ, что соответствует 100 Мбит/с при условии, что соединение поддерживает такую скорость
        downloaded_size = 0
        start_time = time.time()

        # Создаем кнопку с рандомными эмодзи и ссылкой
        markup = types.InlineKeyboardMarkup()
        button_text = f"{get_random_emoji()} Скачиваю файл {get_random_emoji()}"
        button = types.InlineKeyboardButton(button_text, url=url)
        markup.add(button)

        # Обновляем сообщение с кнопкой
        bot.edit_message_text(chat_id=message.chat.id, message_id=status_message.message_id, text="Прогресс скачивания:", reply_markup=markup)

        # Сохраняем файл
        with open(filename, 'wb') as file:
            for data in response.iter_content(block_size):
                size = file.write(data)
                downloaded_size += size

                # Обновляем статус каждые 0.5 секунды
                if time.time() - start_time > 0.5:
                    percentage = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                    speed = downloaded_size / (time.time() - start_time)
                    estimated_time = (total_size - downloaded_size) / speed if speed > 0 else 0

                    status_text = f"Скачано: {downloaded_size / 1024 / 1024:.2f} МБ"
                    if total_size > 0:
                        status_text += f" из {total_size / 1024 / 1024:.2f} МБ\n"
                        status_text += f"Прогресс: {percentage:.1f}%\n"
                    else:
                        status_text += "\n"
                    status_text += f"Скорость: {speed / 1024 / 1024:.2f} МБ/с\n"
                    if estimated_time > 0:
                        status_text += f"Осталось примерно: {estimated_time:.0f} секунд"

                    # Обновляем кнопку с новыми эмодзи
                    button_text = f"{get_random_emoji()} Скачиваю файл {get_random_emoji()}"
                    button = types.InlineKeyboardButton(button_text, url=url)
                    markup = types.InlineKeyboardMarkup()
                    markup.add(button)

                    bot.edit_message_text(chat_id=message.chat.id, message_id=status_message.message_id, text=status_text, reply_markup=markup)
                    start_time = time.time()

        # Отправляем файл пользователю
        with open(filename, 'rb') as file:
            bot.send_document(message.chat.id, file)

        # Удаляем файл после отправки
        os.remove(filename)

        # Обновляем кнопку после завершения скачивания
        button_text = f"{get_random_emoji()} Файл успешно скачан {get_random_emoji()}"
        button = types.InlineKeyboardButton(button_text, callback_data="download_complete")
        markup = types.InlineKeyboardMarkup()
        markup.add(button)
        bot.edit_message_text(chat_id=message.chat.id, message_id=status_message.message_id, text="Скачивание завершено!", reply_markup=markup)

    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Произошла ошибка при скачивании файла: {str(e)}")
    except Exception as e:
        bot.reply_to(message, f"Произошла неизвестная ошибка: {str(e)}")

if __name__ == '__main__':
    bot.polling(none_stop=True)
