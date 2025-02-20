from random import randint
from typing import List, Tuple, Optional
from pathlib import Path

import telebot
from telebot import types
from bs4 import BeautifulSoup
from requests_tor import RequestsTor


# Укажите здесь ваш токен Telegram-бота
BOT_TOKEN = "7218060489:AAEx4jhciHiBh1Vxpo-MVkHHkHXObcR2dxg"
bot = telebot.TeleBot(BOT_TOKEN)


# Папка для сохранения загружаемых файлов (при необходимости измените путь)
folder = Path("downloads")
if not folder.exists():
    folder.mkdir(parents=True, exist_ok=True)


# URL для поиска и скачивания (для сайта Flibusta по сети Tor)
url = (
    "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/"
    "booksearch?ask="
)
url2 = (
    "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion"
)


def search(s: str, lst_fb2: List[str], lst_epub: List[str],
           lst_name: List[str], lst_ath: List[str],
           lst_ppp: List[str]
           ) -> Tuple[List[str], List[str], List[str], List[str]]:
    list_links: List[str] = []
    rt = RequestsTor()
    response = rt.get(url + s)
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("li"):
        if "/a/" in str(link) and "/b/" in str(link):
            s_part = str(link).split('<a href="/a/')
            if s_part[1] not in lst_ppp:
                g = s_part[0].split('<a href="')
                u = g[1].split('">')
                list_links.append(u[0])
                lst_ppp.append(s_part[1])
    links = list_links[:5]
    lst_ppp.clear()
    return books_links(links, lst_fb2, lst_epub, lst_name, lst_ath)


def books_links(links: List[str], lst_fb2: List[str], lst_epub: List[str],
                lst_name: List[str], lst_ath: List[str]
                ) -> Tuple[List[str], List[str], List[str], List[str]]:
    rt = RequestsTor()
    for el in links:
        response = rt.get(url2 + el)
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a"):
            u = link.get("href")
            if u.startswith("/b/") and u.endswith("fb2"):
                lst_fb2.append(url2 + u)
            elif u.startswith("/b/") and u.endswith("epub"):
                lst_epub.append(url2 + u)
        for link in soup.find_all("h1"):
            if "fb2" in str(soup):
                if "class" in str(link):
                    w = str(link).replace(">", "%")
                    e = w.replace("<", "%")
                    y = e.split("%")
                    r = y[2].split("(")
                    name = r[0]
                    if "/" in name:
                        lst_name.append(name.split("/")[0])
                    elif "\\" in name:
                        lst_name.append(name.split("\\")[0])
                    elif '"' in name:
                        lst_name.append(name.split('"')[1])
                    else:
                        lst_name.append(name[:-1])
        for link in soup.find_all("a"):
            if "fb2" in str(soup):
                if ("title" not in str(link) and "/a/" in str(link)
                        and "all" not in str(link)):
                    w = str(link).replace(">", "%")
                    e = w.replace("<", "%")
                    r = e.split("%")
                    name = r[2]
                    n = name.split()
                    lst_ath.append(n[-1])
                    break
    return lst_fb2, lst_epub, lst_name, lst_ath


def search2(s: str, lst_fb2: List[str], lst_epub: List[str],
            lst_name: List[str], lst_ath: List[str],
            lst_ppp: List[str], a: str
            ) -> Tuple[List[str], List[str], List[str], List[str]]:
    list_links: List[str] = []
    rt = RequestsTor()
    response = rt.get(url + s)
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("li"):
        if "/a/" in str(link) and "/b/" in str(link):
            s_part = str(link).split('<a href="/a/')
            fau = s_part[1].split(">")
            fau_2 = fau[1].split("<")
            n = fau_2[0].split()[-1]
            if str(a).lower() in str(n).lower():
                g = s_part[0].split('<a href="')
                u = g[1].split('">')
                list_links.append(u[0])
                lst_ppp.append(s_part[1])
    links = list_links[:5]
    lst_ppp.clear()
    return books_links2(links, lst_fb2, lst_epub, lst_name, lst_ath)


def books_links2(links: List[str], lst_fb2: List[str], lst_epub: List[str],
                 lst_name: List[str], lst_ath: List[str]
                 ) -> Tuple[List[str], List[str], List[str], List[str]]:
    rt = RequestsTor()
    for el in links:
        response = rt.get(url2 + el)
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a"):
            u = link.get("href")
            if u.startswith("/b/") and u.endswith("fb2"):
                lst_fb2.append(url2 + u)
            elif u.startswith("/b/") and u.endswith("epub"):
                lst_epub.append(url2 + u)
        for link in soup.find_all("h1"):
            if "fb2" in str(soup):
                if "class" in str(link):
                    w = str(link).replace(">", "%")
                    e = w.replace("<", "%")
                    y = e.split("%")
                    r = y[2].split("(")
                    name = r[0]
                    if "/" in name:
                        lst_name.append(name.split("/")[0])
                    elif "\\" in name:
                        lst_name.append(name.split("\\")[0])
                    elif '"' in name:
                        lst_name.append(name.split('"')[1])
                    elif "[" in name:
                        o = name.split("[")
                        if o[0]:
                            lst_name.append(o[0])
                        if len(o) > 1 and o[1]:
                            lst_name.append(o[1])
                        if len(o) > 2 and o[2]:
                            lst_name.append(o[2])
                    else:
                        lst_name.append(name[:-1])
        for link in soup.find_all("a"):
            if "fb2" in str(soup):
                if ("title" not in str(link) and "/a/" in str(link)
                        and "all" not in str(link)):
                    w = str(link).replace(">", "%")
                    e = w.replace("<", "%")
                    r = e.split("%")
                    name = r[2]
                    n = name.split()
                    lst_ath.append(n[-1])
                    break
    return lst_fb2, lst_epub, lst_name, lst_ath


def download_file(file_url: str, full_path: Path) -> str:
    rt = RequestsTor()
    response = rt.get(file_url)
    filename = file_url.split("/")[-1]
    filepath = full_path / filename
    with open(filepath, "wb") as f:
        f.write(response.content)
    return str(filepath)


def fb2_download(query: str, folder_path: Path) -> Optional[str]:
    lst_fb2: List[str] = []
    lst_epub: List[str] = []
    lst_name: List[str] = []
    lst_ath: List[str] = []
    lst_ppp: List[str] = []
    fb2_links, _, _, _ = search(
        query,
        lst_fb2,
        lst_epub,
        lst_name,
        lst_ath,
        lst_ppp,
    )
    if not fb2_links:
        return None
    c = randint(0, 9000000)
    full_path = Path(folder_path) / f"papka_{c}"
    if not full_path.exists():
        full_path.mkdir(parents=True, exist_ok=True)
    else:
        full_path = Path(folder_path) / f"papka_{c + 16}"
        full_path.mkdir(parents=True, exist_ok=True)
    file_url = fb2_links[0]
    filepath = download_file(file_url, full_path)
    return filepath


def epub_download(query: str, folder_path: Path) -> Optional[str]:
    lst_fb2: List[str] = []
    lst_epub: List[str] = []
    lst_name: List[str] = []
    lst_ath: List[str] = []
    lst_ppp: List[str] = []
    fb2_links, epub_links, _, _ = search(
        query,
        lst_fb2,
        lst_epub,
        lst_name,
        lst_ath,
        lst_ppp,
    )
    if not epub_links:
        return None
    c = randint(0, 9000000)
    full_path = Path(folder_path) / f"papka_{c}"
    if not full_path.exists():
        full_path.mkdir(parents=True, exist_ok=True)
    else:
        full_path = Path(folder_path) / f"papka_{c + 16}"
        full_path.mkdir(parents=True, exist_ok=True)
    file_url = epub_links[0]
    filepath = download_file(file_url, full_path)
    return filepath


def fb22_download(query: str, author: str, folder_path: Path) -> Optional[str]:
    lst_fb2: List[str] = []
    lst_epub: List[str] = []
    lst_name: List[str] = []
    lst_ath: List[str] = []
    lst_ppp: List[str] = []
    fb2_links, _, _, _ = search2(
        query,
        lst_fb2,
        lst_epub,
        lst_name,
        lst_ath,
        lst_ppp,
        author,
    )
    if not fb2_links:
        return None
    c = randint(0, 9000000)
    full_path = Path(folder_path) / f"papka_{c}"
    if not full_path.exists():
        full_path.mkdir(parents=True, exist_ok=True)
    else:
        full_path = Path(folder_path) / f"papka_{c + 16}"
        full_path.mkdir(parents=True, exist_ok=True)
    file_url = fb2_links[0]
    filepath = download_file(file_url, full_path)
    return filepath


def epub2_download(query: str, author: str, folder_path: Path) -> Optional[str]:
    lst_fb2: List[str] = []
    lst_epub: List[str] = []
    lst_name: List[str] = []
    lst_ath: List[str] = []
    lst_ppp: List[str] = []
    fb2_links, epub_links, _, _ = search2(
        query,
        lst_fb2,
        lst_epub,
        lst_name,
        lst_ath,
        lst_ppp,
        author,
    )
    if not epub_links:
        return None
    c = randint(0, 9000000)
    full_path = Path(folder_path) / f"papka_{c}"
    if not full_path.exists():
        full_path.mkdir(parents=True, exist_ok=True)
    else:
        full_path = Path(folder_path) / f"papka_{c + 16}"
        full_path.mkdir(parents=True, exist_ok=True)
    file_url = epub_links[0]
    filepath = download_file(file_url, full_path)
    return filepath


# Словарь для хранения промежуточных данных пользователя (состояния диалога)
user_states: dict = {}


@bot.message_handler(commands=["start"])
def start_handler(message: types.Message) -> None:
    user_states[message.chat.id] = {}
    markup = types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True
    )
    markup.add("1", "2")
    bot.send_message(
        message.chat.id,
        "Выберите тип поиска:\n"
        "1 – по названию книги\n"
        "2 – по названию и автору",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_search_type)


def process_search_type(message: types.Message) -> None:
    chat_id = message.chat.id
    text = message.text.strip()
    if text not in ["1", "2"]:
        bot.send_message(chat_id, "Пожалуйста, выберите вариант 1 или 2.")
        return
    user_states[chat_id]["search_type"] = int(text)
    markup = types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True
    )
    markup.add("1", "2")
    bot.send_message(
        chat_id,
        "Выберите формат книги:\n"
        "1 – fb2\n"
        "2 – epub",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_book_format)


def process_book_format(message: types.Message) -> None:
    chat_id = message.chat.id
    text = message.text.strip()
    if text not in ["1", "2"]:
        bot.send_message(chat_id, "Пожалуйста, выберите вариант 1 или 2.")
        return
    user_states[chat_id]["book_format"] = int(text)
    bot.send_message(chat_id, "Введите название книги:")
    bot.register_next_step_handler(message, process_book_name)


def process_book_name(message: types.Message) -> None:
    chat_id = message.chat.id
    book_name = message.text.strip()
    user_states[chat_id]["book_name"] = book_name
    if user_states[chat_id]["search_type"] == 2:
        bot.send_message(chat_id, "Введите фамилию автора:")
        bot.register_next_step_handler(message, process_author)
    else:
        process_download(chat_id)


def process_author(message: types.Message) -> None:
    chat_id = message.chat.id
    author = message.text.strip()
    user_states[chat_id]["author"] = author
    process_download(chat_id)


def process_download(chat_id: int) -> None:
    search_type = user_states[chat_id]["search_type"]
    book_format = user_states[chat_id]["book_format"]
    book_name = user_states[chat_id]["book_name"]
    folder_path = folder
    file_path: Optional[str] = None
    bot.send_message(
        chat_id,
        "Происходит поиск и скачивание книги, пожалуйста, подождите..."
    )
    try:
        if search_type == 1:
            if book_format == 1:
                file_path = fb2_download(book_name, folder_path)
            elif book_format == 2:
                file_path = epub_download(book_name, folder_path)
        elif search_type == 2:
            author = user_states[chat_id]["author"]
            if book_format == 1:
                file_path = fb22_download(book_name, author, folder_path)
            elif book_format == 2:
                file_path = epub2_download(book_name, author, folder_path)
        if file_path and Path(file_path).exists():
            with open(file_path, "rb") as doc:
                bot.send_document(chat_id, doc)
            bot.send_message(chat_id, "Книга успешно загружена.")
        else:
            bot.send_message(
                chat_id,
                "Не удалось найти или скачать книгу. "
                "Попробуйте уточнить запрос."
            )
    except Exception as e:
        bot.send_message(
            chat_id,
            f"Произошла ошибка: {e}"
        )
    user_states.pop(chat_id, None)


if __name__ == "__main__":
    bot.polling()
