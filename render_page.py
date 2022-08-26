import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell
from more_itertools import chunked
import json

def on_reload():
    os.makedirs('pages', exist_ok=True)
    template = env.get_template('template.html')

    with open('media/book_info/book_info.json', 'r') as file:
        parsed_books = json.load(file)

    books_titles = list(chunked(parsed_books.keys(), 2))
    books_titles_by_pages = list(chunked(books_titles, 5))

    for page_num, title_pairs in enumerate(books_titles_by_pages, 1):
        rendered_page = template.render(
            parsed_books=parsed_books,
            title_pairs=title_pairs,
            pages_count=len(books_titles_by_pages),
            current_page=page_num,
        )
        with open(f'pages/index{page_num}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)
    print('Site rebuilt')

if __name__=='__main__':
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    on_reload()

    server = Server()
    server.watch('media/', on_reload)
    server.watch('template.html', on_reload)
    server.serve()
