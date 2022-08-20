import argparse
import json
import logging
import time
import os

from pathlib import Path
from urllib.parse import urljoin, quote

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename as sanitize

def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def create_directory(save_dir, save_path=Path.cwd()):
    dir_path = Path(save_path) / save_dir
    Path.mkdir(dir_path, parents=True, exist_ok=True)
    return dir_path


def create_parser():
    parser = argparse.ArgumentParser(description='Parse books from tululu.org')
    parser.add_argument('-start_id', '-s', default=0, type=int, help='Start book id. Default = 0')
    parser.add_argument('-end_id', '-e', default=10, type=int, help='Finish book id. Default = 10')
    return parser


def download_book(url, dir_path, book_id, book_title):
    book_response = requests.get(url, params={'id': book_id})
    book_response.raise_for_status()
    check_for_redirect(book_response)

    file_name = f'''{book_id}. {book_title}'.txt'''
    save_book_path = dir_path / file_name
    with open(save_book_path, 'wb') as file:
        file.write(book_response.content)
    return save_book_path

def download_image(image_url, dir_path, book_id, book_title):
    book_image_response = requests.get(image_url)
    book_image_response.raise_for_status()
    check_for_redirect(book_image_response)

    file_name = f'''{book_id}. {book_title}.jpg'''
    save_img_path = dir_path / file_name
    with open(save_img_path, 'wb') as file:
        file.write(book_image_response.content)
    return save_img_path


def get_book_comments(soup):
    comments_block = soup.find_all(class_='texts')
    comments = [comment.find(class_='black').text for comment in comments_block]
    return comments


def get_book_genres(soup):
    genres_block = soup.find(id='content').find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres_block]
    return genres


def parse_book_page(url, response):
    '''Return book's information: title, author, genre, comments and img_url'''
    soup = BeautifulSoup(response.text, 'lxml')

    book_header = soup.find('h1')
    title, author = book_header.text.split(' \xa0 :: \xa0 ')
    image_relative_url = soup.find(class_='bookimage').find('img')['src']

    parsed_book = {
        'title': sanitize(title),
        'genres': get_book_genres(soup),
        'author': author,
        'img_url': urljoin(url, image_relative_url),
        'comments': get_book_comments(soup)
    }
    return parsed_book


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = create_parser()
    namespace = parser.parse_args()

    books_path = create_directory('books')
    images_path = create_directory('images')
    json_path = create_directory('book_info')

    parsed_books = {}
    save_json_path = json_path / 'book_info.json'

    for book_id in range(namespace.start_id, namespace.end_id + 1):  #Add 1 to include last book in range
        url = f'https://tululu.org/txt.php'
        book_page_url = f'https://tululu.org/b{book_id}/'

        flag = True
        while flag == True:
            try:
                book_page_response = requests.get(book_page_url)
                book_page_response.raise_for_status()
                check_for_redirect(book_page_response)
                parsed_book = parse_book_page(book_page_url, book_page_response)

                book_file_path = download_book(url, books_path, book_id, parsed_book['title'])
                image_file_path = download_image(parsed_book['img_url'], images_path, book_id, parsed_book['title'])
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
            'comments': parsed_book['comments'],
            'image_url': image_file_path.as_uri(),
            'txt_url': book_file_path.as_uri(),
        }

    with open(save_json_path, 'w') as file:
        json.dump(parsed_books, file, indent=4, ensure_ascii=False)
