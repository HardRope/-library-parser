import argparse
import json
import logging
import time

from pathlib import Path
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename as sanitize

from .main import check_for_redirect

def get_books_urls(url, response):
    soup = BeautifulSoup(response, 'lxml')
    soup_of_books = soup.find_all(class_='d_book')

    parsed_urls = []
    for book_soup in soup_of_books:
        book_relative_url = book_soup.find('a')['href']
        book_url = urljoin(url, book_relative_url)
        parsed_urls.append(book_url)
    return parsed_urls


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    books_urls = []

    for page in range(1, 5):
        try:
            url = f'https://tululu.org/l55/{page}/'
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)

            books_urls.extend(get_books_urls(url, response.text))
        except requests.ConnectionError:
            logging.info(f'Проблема подключения. Страница {url} не скачана')
            continue
        except requests.HTTPError:
            logging.info(f'Страница {url} отсутствует на сайте.')
            continue
    print(*books_urls, sep = '\n')