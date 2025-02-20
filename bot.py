from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from random import randint
from typing import Dict, List, Optional, Tuple

import telebot
from telebot import types
from bs4 import BeautifulSoup
from requests_tor import RequestsTor


@dataclass
class UserState:
    search_type: int = 0
    book_format: int = 0
    book_name: str = ""
    author: Optional[str] = None


class FlibustaClient:
    def __init__(self, search_url: str, base_url: str) -> None:
        self.search_url = search_url
        self.base_url = base_url
        self.rt = RequestsTor()

    def _get_soup(self, url: str) -> BeautifulSoup:
        response = self.rt.get(url)
        return BeautifulSoup(response.text, "html.parser")

    def search(
        self, query: str
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        lst_fb2: List[str] = []
        lst_epub: List[str] = []
        lst_name: List[str] = []
        lst_ath: List[str] = []
        lst_ppp: List[str] = []
        soup = self._get_soup(self.search_url + query)
        list_links: List[str] = []
        for li in soup.find_all("li"):
            if "/a/" in str(li) and "/b/" in str(li):
                parts = str(li).split('<a href="/a/')
                if parts[1] not in lst_ppp:
                    link_val = parts[0].split('<a href="')[1].split('">')[0]
                    list_links.append(link_val)
                    lst_ppp.append(parts[1])
        links = list_links[:5]
        lst_ppp.clear()
        return self._books_links(links, lst_fb2, lst_epub, lst_name, lst_ath)

    def _books_links(
        self,
        links: List[str],
        lst_fb2: List[str],
        lst_epub: List[str],
        lst_name: List[str],
        lst_ath: List[str],
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        for el in links:
            soup = self._get_soup(self.base_url + el)
            for a in soup.find_all("a"):
                href = a.get("href")
                if href.startswith("/b/"):
                    if href.endswith("fb2"):
                        lst_fb2.append(self.base_url + href)
                    elif href.endswith("epub"):
                        lst_epub.append(self.base_url + href)
            for h1 in soup.find_all("h1"):
                if "fb2" in str(soup) and "class" in str(h1):
                    text = str(h1).replace(">", "%").replace("<", "%")
                    parts = text.split("%")
                    name = parts[2].split("(")[0]
                    if "/" in name:
                        lst_name.append(name.split("/")[0])
                    elif "\\" in name:
                        lst_name.append(name.split("\\")[0])
                    elif '"' in name:
                        lst_name.append(name.split('"')[1])
                    else:
                        lst_name.append(name[:-1])
            for a in soup.find_all("a"):
                if ("fb2" in str(soup) and "title" not in str(a)
                        and "/a/" in str(a) and "all" not in str(a)):
                    text = str(a).replace(">", "%").replace("<", "%")
                    parts = text.split("%")
                    lst_ath.append(parts[2].split()[-1])
                    break
        return lst_fb2, lst_epub, lst_name, lst_ath

    def search_by_author(
        self, query: str, author: str
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        lst_fb2: List[str] = []
        lst_epub: List[str] = []
        lst_name: List[str] = []
        lst_ath: List[str] = []
        lst_ppp: List[str] = []
        soup = self._get_soup(self.search_url + query)
        list_links: List[str] = []
        for li in soup.find_all("li"):
            if "/a/" in str(li) and "/b/" in str(li):
                parts = str(li).split('<a href="/a/')
                fau = parts[1].split(">")
                fau2 = fau[1].split("<")
                n = fau2[0].split()[-1]
                if str(author).lower() in str(n).lower():
                    link_val = parts[0].split('<a href="')[1].split('">')[0]
                    list_links.append(link_val)
                    lst_ppp.append(parts[1])
        links = list_links[:5]
        lst_ppp.clear()
        return self._books_links(links, lst_fb2, lst_epub, lst_name, lst_ath)

    def download_file(self, file_url: str, folder_path: Path) -> str:
        response = self.rt.get(file_url)
        filename = file_url.split("/")[-1]
        filepath = folder_path / filename
        with open(filepath, "wb") as f:
            f.write(response.content)
        return str(filepath)

    def fb2_download(self, query: str, folder_path: Path) -> Optional[str]:
        lst_fb2, _, _, _ = self.search(query)
        if not lst_fb2:
            return None
        c = randint(0, 9000000)
        full_path = folder_path / f"papka_{c}"
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
        else:
            full_path = folder_path / f"papka_{c + 16}"
            full_path.mkdir(parents=True, exist_ok=True)
        file_url = lst_fb2[0]
        return self.download_file(file_url, full_path)

    def epub_download(self, query: str, folder_path: Path) -> Optional[str]:
        lst_fb2, lst_epub, _, _ = self.search(query)
        if not lst_epub:
            return None
        c = randint(0, 9000000)
        full_path = folder_path / f"papka_{c}"
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
        else:
            full_path = folder_path / f"papka_{c + 16}"
            full_path.mkdir(parents=True, exist_ok=True)
        file_url = lst_epub[0]
        return self.download_file(file_url, full_path)

    def fb22_download(
        self, query: str, author: str, folder_path: Path
    ) -> Optional[str]:
        lst_fb2, _, _, _ = self.search_by_author(query, author)
        if not lst_fb2:
            return None
        c = randint(0, 9000000)
        full_path = folder_path / f"papka_{c}"
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
        else:
            full_path = folder_path / f"papka_{c + 16}"
            full_path.mkdir(parents=True, exist_ok=True)
        file_url = lst_fb2[0]
        return self.download_file(file_url, full_path)

    def epub2_download(
        self, query: str, author: str, folder_path: Path
    ) -> Optional[str]:
        lst_fb2, lst_epub, _, _ = self.search_by_author(query, author)
        if not lst_epub:
            return None
        c = randint(0, 9000000)
        full_path = folder_path / f"papka_{c}"
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
        else:
            full_path = folder_path / f"papka_{c + 16}"
            full_path.mkdir(parents=True, exist_ok=True)
        file_url = lst_epub[0]
        return self.download_file(file_url, full_path)


class TelegramBotHandler:
    def __init__(
        self, token: str, client: FlibustaClient, download_folder: Path
    ) -> None:
        self.bot = telebot.TeleBot(token)
        self.client = client
        self.download_folder = download_folder
        self.user_states: Dict[int, UserState] = {}
        self.register_handlers()

    def register_handlers(self) -> None:
        @self.bot.message_handler(commands=["start"])
        def start_handler(message: types.Message) -> None:
            self.user_states[message.chat.id] = UserState()
            markup = types.ReplyKeyboardMarkup(
                one_time_keyboard=True, resize_keyboard=True
            )
            markup.add("1", "2")
            self.bot.send_message(
                message.chat.id,
                "Выберите тип поиска:\n"
                "1 – по названию книги\n"
                "2 – по названию и автору",
                reply_markup=markup,
            )
            self.bot.register_next_step_handler(
                message, self.process_search_type
            )

    def process_search_type(self, message: types.Message) -> None:
        chat_id = message.chat.id
        text = message.text.strip()
        if text not in ["1", "2"]:
            self.bot.send_message(chat_id, "Пожалуйста, выберите вариант 1 или 2.")
            return
        self.user_states[chat_id].search_type = int(text)
        markup = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True
        )
        markup.add("1", "2")
        self.bot.send_message(
            chat_id,
            "Выберите формат книги:\n1 – fb2\n2 – epub",
            reply_markup=markup,
        )
        self.bot.register_next_step_handler(message, self.process_book_format)

    def process_book_format(self, message: types.Message) -> None:
        chat_id = message.chat.id
        text = message.text.strip()
        if text not in ["1", "2"]:
            self.bot.send_message(chat_id, "Пожалуйста, выберите вариант 1 или 2.")
            return
        self.user_states[chat_id].book_format = int(text)
        self.bot.send_message(chat_id, "Введите название книги:")
        self.bot.register_next_step_handler(message, self.process_book_name)

    def process_book_name(self, message: types.Message) -> None:
        chat_id = message.chat.id
        self.user_states[chat_id].book_name = message.text.strip()
        if self.user_states[chat_id].search_type == 2:
            self.bot.send_message(chat_id, "Введите фамилию автора:")
            self.bot.register_next_step_handler(message, self.process_author)
        else:
            self.process_download(chat_id)

    def process_author(self, message: types.Message) -> None:
        chat_id = message.chat.id
        self.user_states[chat_id].author = message.text.strip()
        self.process_download(chat_id)

    def process_download(self, chat_id: int) -> None:
        state = self.user_states[chat_id]
        self.bot.send_message(
            chat_id,
            "Происходит поиск и скачивание книги, пожалуйста, подождите..."
        )
        file_path: Optional[str] = None
        try:
            match (state.search_type, state.book_format):
                case (1, 1):
                    file_path = self.client.fb2_download(
                        state.book_name, self.download_folder
                    )
                case (1, 2):
                    file_path = self.client.epub_download(
                        state.book_name, self.download_folder
                    )
                case (2, 1):
                    file_path = self.client.fb22_download(
                        state.book_name, state.author, self.download_folder
                    )
                case (2, 2):
                    file_path = self.client.epub2_download(
                        state.book_name, state.author, self.download_folder
                    )
            if file_path and Path(file_path).exists():
                with open(file_path, "rb") as doc:
                    self.bot.send_document(chat_id, doc)
                self.bot.send_message(chat_id, "Книга успешно загружена.")
            else:
                self.bot.send_message(
                    chat_id,
                    "Не удалось найти или скачать книгу. "
                    "Попробуйте уточнить запрос."
                )
        except Exception as e:
            self.bot.send_message(chat_id, f"Произошла ошибка: {e}")
        self.user_states.pop(chat_id, None)

    def run(self) -> None:
        self.bot.polling()


if __name__ == "__main__":
    DOWNLOAD_FOLDER = Path("downloads")
    if not DOWNLOAD_FOLDER.exists():
        DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    SEARCH_URL = (
        "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion/"
        "booksearch?ask="
    )
    BASE_URL = (
        "http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion"
    )
    client = FlibustaClient(SEARCH_URL, BASE_URL)
    bot_handler = TelegramBotHandler(
        "7218060489:AAEx4jhciHiBh1Vxpo-MVkHHkHXObcR2dxg",
        client,
        DOWNLOAD_FOLDER,
    )
    bot_handler.run()
