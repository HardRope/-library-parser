from pathlib import Path

import requests

def create_directory(save_dir='books'):
    dir_path = Path.cwd() / save_dir
    Path.mkdir(dir_path, parents=True, exist_ok=True)
    return dir_path


def download_book(url, path):
    response = requests.get(url)
    response.raise_for_status()

    with open(path, 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    dir_path = create_directory()

    for id in range(1, 11):
        url = f'https://tululu.org/txt.php?id={id}'
        file_name = str(id) + '.txt'
        save_path = dir_path / file_name
        download_book(url, save_path)
