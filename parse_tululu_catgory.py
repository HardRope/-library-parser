import argparse
import json
import logging
import re
import time

from pathlib import Path
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename as sanitize

from main import (
    check_for_redirect,
    create_directory,
    parse_book_page,
    download_book,
    download_image
)


def get_books_urls(url, response):
    soup = BeautifulSoup(response, 'lxml')
    soup_of_books = soup.find_all(class_='d_book')

    parsed_urls = []
    for book_soup in soup_of_books:
        book_relative_url = book_soup.find('a')['href']
        book_url = urljoin(url, book_relative_url)
        book_id = re.findall(r'\d+', book_relative_url)[0]
        parsed_urls.append((book_id, book_url))
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
    print(books_urls)

    books_path = create_directory('books')
    images_path = create_directory('images')
    json_path = create_directory('book_info')

    parsed_books = {}

    for book_id, book_page_url in books_urls:
        url = f'https://tululu.org/txt.php'
        # book_page_url = f'https://tululu.org/b{book_id}/'

        flag = True
        while flag == True:
            try:
                book_page_response = requests.get(book_page_url)
                book_page_response.raise_for_status()
                check_for_redirect(book_page_response)
                book_info = parse_book_page(book_page_url, book_page_response)

                download_book(url, books_path, book_id, book_info['title'])
                download_image(book_info['img_url'], images_path, book_id, book_info['title'])
                break
            except requests.ConnectionError:
                logging.info('Проблема подключения. Повторная попытка через 60 секунд.')
                time.sleep(60)
                continue
            except requests.HTTPError:
                logging.info(f'Книга с id {book_id} отсутствует на сайте.')
                flag = False
        else:
            continue

        parsed_books[book_info['title']] = {
            'genres': book_info['genres'],
            'author': book_info['author'],
            'comments': book_info['comments']
        }

    save_json_path = json_path / 'book_info.json'
    with open(save_json_path, 'w') as file:
        json.dump(parsed_books, file, indent=4, ensure_ascii=False)