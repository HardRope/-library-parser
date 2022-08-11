import argparse
import json
import logging
import os
import re
import time

from pathlib import Path
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename as sanitize

from parse_tululu_books import (
    check_for_redirect,
    create_directory,
    parse_book_page,
    download_book,
    download_image
)

def create_parser():
    parser = argparse.ArgumentParser(description='Parse books from https://tululu.org/l55/ - fantastic genre')
    parser.add_argument('-start_page', '-s', default=1, type=int, help='Start page. Default = 1')
    parser.add_argument('-end_page', '-e', default=5, type=int, help='Finish page. Default = 5')
    parser.add_argument('-si', '--skip_imgs', action='store_const', default=True, const=False, help='Cancel loading images')
    parser.add_argument('-st', '--skip_txt', action='store_const', default=True, const=False, help='Cancel loading books')
    parser.add_argument('-df', '--dest_folder', help='Path to save books, imges and json')
    parser.add_argument('-jp', '--json_path', help='Path to save json file')
    return parser


def get_books_ids(response):
    soup = BeautifulSoup(response, 'lxml')
    soup_of_books = soup.select('.d_book')

    parsed_urls = []
    for book_soup in soup_of_books:
        book_relative_url = book_soup.select_one('a')['href']

        book_id = re.findall(r'\d+', book_relative_url)
        parsed_urls.extend(book_id)
    return parsed_urls


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    if not namespace.dest_folder:
        save_path = Path.cwd()
    elif namespace.dest_folder and os.path.exists(namespace.dest_folder):
        save_path = namespace.dest_folder
    else:
        print(f'Ошибка в указанном пути {namespace.dest_folder}. Попробуйте снова.' )
        raise SystemExit

    books_path = create_directory('books', save_path=save_path)
    images_path = create_directory('images', save_path=save_path)

    if namespace.json_path and os.path.exists(namespace.json_path):
        json_path = namespace.json_path
    elif namespace.json_path and not os.path.exists(namespace.json_path):
        print(f'Ошибка в указанном пути {namespace.json_path}. Попробуйте снова.')
        raise SystemExit
    else:
        json_path = create_directory('book_info', save_path=save_path)

    books_ids = []
    parsed_books = {}

    for page in range(namespace.start_page, namespace.end_page + 1): #Add 1 to include last page in range
        try:
            url = f'https://tululu.org/l55/{page}/'
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)

            books_ids.extend(get_books_ids(response.text))
        except requests.ConnectionError:
            logging.info(f'Проблема подключения. Страница {page} не скачана.')
            continue
        except requests.HTTPError:
            logging.info(f'Страница {page} отсутствует на сайте.')
            continue

    for book_id in books_ids:
        url = f'https://tululu.org/txt.php'
        book_page_url = f'https://tululu.org/b{book_id}/'

        flag = True
        while flag == True:
            try:
                book_page_response = requests.get(book_page_url)
                book_page_response.raise_for_status()
                check_for_redirect(book_page_response)
                book_info = parse_book_page(book_page_url, book_page_response)

                if namespace.skip_imgs:
                    download_book(url, books_path, book_id, book_info['title'])
                if namespace.skip_txt:
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

    save_json_path = Path(json_path) / 'book_info.json'
    with open(save_json_path, 'w') as file:
        json.dump(parsed_books, file, indent=4, ensure_ascii=False)