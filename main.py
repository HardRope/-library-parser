from pathlib import Path
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename as sanitize

def create_directory(save_dir='books'):
    dir_path = Path.cwd() / save_dir
    Path.mkdir(dir_path, parents=True, exist_ok=True)
    return dir_path


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
    genres_blok = soup.find(id='content').find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres_blok]
    return genres


def get_book_info(url):
    '''Return book's name and author'''

    response = requests.get(url)
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
    books_path = create_directory()
    images_path = create_directory('images')

    for id in range(1, 11):
        url = f'https://tululu.org/txt.php'
        book_page_url = f'https://tululu.org/b{id}/'

        book_response = download_book(url, id)
        try:
            check_for_redirect(book_response)
        except requests.HTTPError:
            continue

        serialize_book = get_book_info(book_page_url)
        file_name = f'''{id}. {serialize_book['title']}'.txt'''
        save_book_path = books_path / file_name

        with open(save_book_path, 'wb') as file:
            file.write(book_response.content)

        image_url = serialize_book['img_url']
        image_name = f'''{id}. {serialize_book['title']}.jpg'''
        save_image_path = images_path/ image_name

        with open(save_image_path, 'wb') as file:
            file.write(download_book_image(image_url).content)
