import argparse
import json

from pathlib import Path
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename as sanitize

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id', default=0, type=int)
    parser.add_argument('end_id', default=10, type=int)
    return parser


def create_directory(save_dir):
    dir_path = Path.cwd() / save_dir
    Path.mkdir(dir_path, parents=True, exist_ok=True)
    return dir_path


def save_file(path, content):
    with open(path, 'wb') as file:
        file.write(content)


def check_for_redirect(response):
    if response.status_code != 200:
        raise requests.HTTPError


def download_book(url, id):
    params = {'id': id }
    response = requests.get(url, params=params, allow_redirects=False)
    response.raise_for_status()
    return response


def download_book_image(url):
    response = requests.get(url)
    response.raise_for_status()
    return response


def get_book_comments(soup):
    comments = []
    comments_block = soup.find_all(class_='texts')
    for comment in comments_block:
        text = comment.find(class_='black').text
        comments.append(text)
    return comments


def get_book_genres(soup):
    genres_block = soup.find(id='content').find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres_block]
    return genres


def parse_book_page(url, response):
    '''Return book's name and author'''
    soup = BeautifulSoup(response.text, 'lxml')

    book_header = soup.find('h1')
    title, author = book_header.text.split(' \xa0 :: \xa0 ')
    image_relative_url = soup.find(class_='bookimage').find('img')['src']

    serialize_book = {
        'title': sanitize(title),
        'genres': get_book_genres(soup),
        'author': author,
        'img_url': urljoin(url, image_relative_url),
        'comments': get_book_comments(soup)
    }
    return serialize_book


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()

    books_path = create_directory('books')
    images_path = create_directory('images')
    json_path = create_directory('book_info')

    serialized_books = {}
    save_json_path = json_path / 'book_info.json'

    for id in range(namespace.start_id + 1, namespace.end_id + 1):
        url = f'https://tululu.org/txt.php'
        book_page_url = f'https://tululu.org/b{id}/'

        book_response = download_book(url, id)
        try:
            check_for_redirect(book_response)
        except requests.HTTPError:
            continue

        serialize_book = parse_book_page(book_page_url, requests.get(book_page_url))
        file_name = f'''{id}. {serialize_book['title']}'.txt'''

        image_url = serialize_book['img_url']
        image_name = f'''{id}. {serialize_book['title']}.jpg'''

        save_book_path = books_path / file_name
        save_image_path = images_path / image_name

        save_file(save_book_path, book_response.content)
        save_file(save_image_path, download_book_image(image_url).content)

        serialized_books[serialize_book['title']] = {
            'genres': serialize_book['genres'],
            'author': serialize_book['author'],
            'comments': serialize_book['comments']
        }

    # save_file(save_json_path, serialized_books)
    with open(save_json_path, 'w') as file:
        json.dump(serialized_books, file, indent=4, ensure_ascii=False)