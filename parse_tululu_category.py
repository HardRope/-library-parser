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
    parser = argparse.ArgumentParser(description='Parse books from https://tululu.org/l55/ - fantastic genre.')
    parser.add_argument('-start_page', '-s', default=1, type=int, help='Start page. Default = 1.')
    parser.add_argument('-end_page', '-e', default=5, type=int, help='Finish page. Default = 5.')
    parser.add_argument('-si', '--skip_imgs',
                        action='store_const',
                        default=False,
                        const=True,
                        help='Cancel loading images.'
                        )
    parser.add_argument('-st', '--skip_txt',
                        action='store_const',
                        default=False,
                        const=True,
                        help='Cancel loading books.'
                        )
    parser.add_argument('-df', '--dest_folder', default=Path.cwd(), help='Path to save books, imges and json.')
    parser.add_argument('-jp', '--json_path', help='Path to save json file.')
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


def get_book_parse(url, book_page_url, skip_image, skip_txt):
    '''Download book, image and return parsed book information'''
    book_page_response = requests.get(book_page_url)
    book_page_response.raise_for_status()
    check_for_redirect(book_page_response)
    book_info = parse_book_page(book_page_url, book_page_response)

    if not skip_txt:
        download_book(url, books_path, book_id, book_info['title'])
    if not skip_image:
        download_image(book_info['img_url'], images_path, book_id, book_info['title'])
    return book_info


def get_paths(namespace):
    if os.path.exists(namespace.dest_folder):
        save_path = namespace.dest_folder
    else:
        logging.info(f'Ошибка в указанном пути {namespace.dest_folder}. Попробуйте снова.\n' )
        raise SystemExit

    books_path = create_directory('books', save_path=save_path)
    images_path = create_directory('images', save_path=save_path)

    if not namespace.json_path:
        json_path = create_directory('book_info', save_path=save_path)
    elif os.path.exists(namespace.json_path):
        json_path = namespace.json_path
    else:
        logging.info(f'Ошибка в указанном пути {namespace.json_path}. Попробуйте снова.\n')
        raise SystemExit

    return books_path, images_path, json_path


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    books_path, images_path, json_path = get_paths(namespace)

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
        while flag:
            try:
                parsed_book = get_book_parse(url, book_page_url, namespace.skip_imgs, namespace.skip_txt)
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

        parsed_books[parsed_book['title']] = {
            'genres': parsed_book['genres'],
            'author': parsed_book['author'],
            'comments': parsed_book['comments']
        }

    save_json_path = Path(json_path) / 'book_info.json'
    with open(save_json_path, 'w') as file:
        json.dump(parsed_books, file, indent=4, ensure_ascii=False)