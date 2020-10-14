import requests
import urllib3
import arrow
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def clean(s):
    semi_cleaned = s.strip().replace('\n', '').replace('\t', '').replace('\r', '')
    return ' '.join(semi_cleaned.split())




url = 'https://www.digitalconcerthall.com/en/concert/22419'
response = requests.get(url, verify=False)

soup = BeautifulSoup(response.text.encode('utf-8'), features='html.parser')

data = {}
data['title'] = str(soup.h1.get_text())
data['artist'] = str(soup.find_all('p', { 'class': 'mainArtist' })[0].get_text(" | "))
data['date'] = str(soup.find_all('p', { 'class': 'concertMeta' })[0].get_text())
data['repertoire'] = []


for piece in soup.find_all('div', { 'id': re.compile('22419*') }):
    obj = {}

    obj['file'] = piece['id']

    piece_title = clean(piece.find('h2').get_text())
    if "min." in piece_title:
        obj['title'] = piece_title

    artist = piece.find('p', { 'class': 'artists' })
    artist = '' if not artist else clean(piece.find('h2').get_text())

    obj['artist'] = artist
    obj['duration'] = piece['data-duration']

    data['repertoire'].append(obj)


print(data)