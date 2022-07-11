from pathlib import Path
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


def get_book_info(id):
    '''Return book's name and author'''

    response = requests.get(f'https://tululu.org/b{id}/')
    soup = BeautifulSoup(response.text, 'lxml')
    name = soup.find('h1')
    title, author = name.text.split(' \xa0 :: \xa0 ')

    serialize_book = {
        'title': sanitize(title),
        'author': author,
    }
    return serialize_book


if __name__ == '__main__':
    dir_path = create_directory()

    for id in range(1, 11):
        url = f'https://tululu.org/txt.php'
        response = download_book(url, id)
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        serialize_book = get_book_info(id)
        file_name = f'''{id}. {serialize_book['title']}'.txt'''
        save_path = dir_path / file_name

        with open(save_path, 'wb') as file:
            file.write(response.content)


