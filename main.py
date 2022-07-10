from pathlib import Path
import requests

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


if __name__ == '__main__':
    dir_path = create_directory()

    for id in range(1, 11):
        url = f'https://tululu.org/txt.php'
        response = download_book(url, id)
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        file_name = str(id) + '.txt'
        save_path = dir_path / file_name

        with open(save_path, 'wb') as file:
            file.write(response.content)


