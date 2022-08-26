# -library-parser
 
Program wrote to download books and parse information about it from
[tululu.org](https://tululu.org/). 
After running program, it will create 3 directories: `book_info`, `books` and `images`.

1. `book_info` - contain json-file with information about book you downloaded. 
   
   ```
       "title": {
        "book_id": int
        "genres": [
            list_of_book_genres
        ],
        "author": "author_name",
        "comments": [
             list_of_comments_from_site
        ]
    },
   ```
   
2. `books` - dir with book files in format `{id}. {title}.txt`.

3. `images` - books covers in `jpg` format.

For better working, program check book's availability, and miss unused id's.

In case of connection problem, it's stop parsing and tries to reconnect for current book page 
every 60 secs.

## Install

1. Download code.
2. Install required libs by console command.
  
   ```
   pip install -r requirements.txt
   ```

## Run the programm:

To parse book by these id's, use `parse_tululu_books.py` file:

   ```commandline
   python parse_tululu_books.py -h
   
  -h, --help            show this help message and exit
  -start_id START_ID, -s START_ID
                        Start book id. Default = 0
  -end_id END_ID, -e END_ID
                        Finish book id. Default = 10
  -si, --skip_imgs      Cancel loading images.
  -st, --skip_txt       Cancel loading books.
  -df DEST_FOLDER, --dest_folder DEST_FOLDER
                        Path to save books, imges and json.
  -jp JSON_PATH, --json_path JSON_PATH
                        Path to save json file.
   ```

`Start_id` and `end_id` is a books id's from website, for example
   book at these page `https://tululu.org/b1` have id == 1. 

Otherwise, you can use genre parser `parse_tululu_category.py`. 
It downloads fantastic books from [fantastic books](https://tululu.org/l55/) by pages:

```commandline
  python parse_tululu_category.py -h

  -h, --help            show this help message and exit
  -start_page START_PAGE, -s START_PAGE
                        Start page. Default = 1
  -end_page END_PAGE, -e END_PAGE
                        Finish page. Default = 5
  -si, --skip_imgs      Cancel loading images
  -st, --skip_txt       Cancel loading books
  -df DEST_FOLDER, --dest_folder DEST_FOLDER
                        Path to save books, imges and json
  -jp JSON_PATH, --json_path JSON_PATH
                        Path to save json file
```

## Site creating

You can create your own site with parsed books!

For this you must put parsed books (`txt`, `images` and `json` files) to `-library-parser/media/` folder 
(directories `books`, `images` and `book_info`) and run the renderer

```commandline
python render_page.py
```

It creates folder `pages` with created `html`-files and run local server. First page of created site will be:

```
127.0.0.1:5500/pages/index1.html
```

To stop local server just type `Ctrl-C` in your console.

Example of created site here -> [Big-big library](https://hardrope.github.io/-library-parser/pages/index1.html)

![img.png](/static/site_example.png)

## Project Goals

The code is written for educational purposes on online-course for 
web-developers [dvmn.org](https://dvmn.org/).
