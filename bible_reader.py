import logging
from collections import OrderedDict
from urllib import quote
import json
import requests
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session


SAVED_REQUESTS = {}

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.intent("ReadPassage")
def read_bible(book, chapterOne, verseOne=None, chapterTwo=None, verseTwo=None):
    # https://getbible.net/json?scrip=Acts%203:17&ver=nasb

    # prep inputs
    book = quote(book)
    chapterOne = quote(chapterOne)

    if verseOne:
        verseOne = quote(verseOne)

    if chapterTwo:
        chapterTwo = quote(chapterTwo)

    if verseTwo:
        verseTwo = quote(verseTwo)

    # Build the URL
    req_url = 'https://getbible.net/json?ver=nasb'
    if not any([verseOne, chapterTwo, verseTwo]):
        # Read a whole chapter
        req_url += '&scrip={0!s}%20{1!s}'.format(book, chapterOne)
    elif verseOne and not any([chapterTwo, verseTwo]):
        # Read a single verse
        req_url += '&scrip={0!s}%20{1!s}:{2!s}'.format(book, chapterOne, verseOne)
    elif verseOne and verseTwo and not chapterTwo:
        # Read multiple verses in the same chapter
        req_url += '&scrip={0!s}%20{1!s}:{2!s}-{3!s}'.format(book, chapterOne, verseOne, verseTwo)
    elif chapterTwo and not any([verseOne, verseTwo]):
        # Reach multiple chapters
        req_url += '&scrip={0!s}%20{1!s}-{2!s}'.format(book, chapterOne, chapterTwo)
    elif chapterTwo and verseTwo and not verseOne:
        # Read an entire chapter until another chapter and verse
        req_url += '&scrip={0!s}%20{1!s}-{2!s}:{3!s}'.format(book, chapterOne, chapterTwo, verseTwo)
    else:
        # Read a passage from chapter/verse to chapter/verse
        req_url += '&scrip={0!s}%20{1!s}:{2!s}-{3!s}:{4!s}'.format(book, chapterOne, verseOne, chapterTwo, verseTwo)

    print req_url

    res = requests.get(req_url)
    print res.status_code

    if res.text == 'NULL':
        return statement(render_template('notfound'))

    # Strip its response
    st = res.content.strip('(').rstrip(';').rstrip(')')
    js = json.loads(st)

    verses = []
    if 'book' in js:
        for book in js['book']:
            for verse_n, verse in OrderedDict(sorted(book['chapter'].items(), key=lambda t: t[0])).items():
                verses.append(verse['verse'].strip('\"'))
    else:
        for verse_n, verse in OrderedDict(sorted(js['chapter'].items(), key=lambda t: t[0])).items():
            verses.append(verse['verse'].strip('\"'))

    print verses
    return statement(' '.join(verses))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
