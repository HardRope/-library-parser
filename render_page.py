from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape

import json

if __name__=='__main__':
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open('book_info/book_info.json', 'r') as file:
        parsed_books_json = file.read()
    parsed_books = json.loads(parsed_books_json)

    rendered_page = template.render(
        parsed_books=parsed_books,
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    print('Готово')
