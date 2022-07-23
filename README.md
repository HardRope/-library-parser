# -library-parser
 
Programm writed to download books and parse information about it from
[tululu.org](https://tululu.org/). 
After running programm, it create 3 directories: `book_info`, `books` and `images`.

1. `book_info` - contain json-file with information about book you downloaded. 
   
   ```
       "title": {
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

For better working, programm check book's availability, and miss unused id's.

In case of connection problem, it's stop parsing and tries to reconnect for current book page 
every 60 secs.

## Install

1. Download code.
2. Install required libs by console command.
   
    ```
   pip install -r requirements.txt
   ```

3. Run the programm:

    ```
   python main.py [start_id] [end_id]
   ```
   
    `Start_id` and `end_id` is a books id's from website, for example
   book at these page `https://tululu.org/b1` have id == 1. 

## Project Goals

The code is written for educational purposes on online-course for 
web-developers [dvmn.org](https://dvmn.org/).
