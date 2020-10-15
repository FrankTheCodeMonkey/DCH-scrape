import requests
import urllib3
import arrow
import re
import argparse
import csv
import traceback
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = 'https://www.digitalconcerthall.com/en/concert/{}'
schema = [
    'concert_date',
    'concert_title',
    'concert_artist',
    'repertoire_file',
    'repertoire_title',
    'repertoire_artist',
    'repertoire_duration',
]

EDUCATION = {
     '52651', '52033', '51962', '51699', '51482', '51364', '23519', '23870', '23837', '23819', '22419', '22626', '22564', '21055', '21028', '21073', '17418', '17408', '4103', '17322', '4087', '4083', '2583', '2877', '2866', '2862', '65', '1734', '1587', '1572', '58', '63', '1588', '1737', '64',
}

FILMS = {
     '371', '370', '369', '368', '250', '307', '215', '366', '308', '367', '365', '364', '363', '362', '360', '359', '358', '306', '357', '356', '304', '300', '233', '232', '302', '301', '231', '230', '225', '223', '227', '226', '211', '203', '213', '114', '104', '101', '74', '108', '109', '110', '113', '355', '354', '352', '353', '351', '350', '115', '112', '229', '228'
}


def scape_concert(concert_id):
    if concert_id in EDUCATION:
        return []

    if concert_id in FILMS:
        return []

    print('current id', concert_id)
    def _clean(s):
        semi_cleaned = s.strip().replace('\n', '').replace('\t', '').replace('\r', '')
        return ' '.join(semi_cleaned.split())

    response = requests.get(base_url.format(concert_id), verify=False)
    soup = BeautifulSoup(response.text.encode('utf-8'), features='html.parser')

    data = {}
    data['concert_title'] = str(soup.h1.get_text())
    data['concert_artist'] = str(soup.find_all('p', { 'class': 'mainArtist' })[0].get_text(" | "))
    data['concert_date'] = str(soup.find_all('p', { 'class': 'concertMeta' })[0].get_text())

    result = []

    # Process individual piece
    for piece in soup.find_all('div', { 'id': re.compile('[0-9]+\-[0-9]+'.format(concert_id)) }):
        base_params = data.copy()

        additional_params = {}

        # ID we'll use for the file name
        additional_params['repertoire_file'] = piece['id']

        # Title of the piece
        piece_title = _clean(piece.find('h2').get_text())
        if "min." in piece_title:
            additional_params['repertoire_title'] = piece_title

        # Performer of this particular piece
        artist = piece.find('p', { 'class': 'artists' })
        artist = '' if not artist else _clean(artist.get_text())

        additional_params['repertoire_artist'] = artist
        additional_params['repertoire_duration'] = piece.get('data-duration', '')

        base_params.update(additional_params)
        result.append(base_params)

    return result


def start_scraping(name, start=None, end=None):
    with open(name, 'r') as f:
        valid_ids = f.read().split('\n')

        start = start or 0
        end = end or len(valid_ids)
        valid_ids = valid_ids[start:end]

        time = str(arrow.utcnow().format('YYYYMMDDHHmmss'))
        with open('catalogue-{}.csv'.format(time), 'w', newline='') as csv_file:
            with open('failed-{}.txt'.format(time), 'w', newline='') as failed_file:
                writer = csv.DictWriter(csv_file, schema, quoting=csv.QUOTE_ALL)
                writer.writeheader()

                for concert_id in valid_ids:
                    try:
                        concert_pieces = scape_concert(concert_id)
                        if not concert_pieces:
                            failed_file.write('SKIPPED: {}\n'.format(concert_id))

                        for piece in concert_pieces:
                            writer.writerow(piece)
                    except Exception as e:
                        traceback.print_exc()
                        failed_file.write('FAILED: {}\n'.format(concert_id))
                        failed_file.write(traceback.format_exc())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--start', type=int, required=False)
    parser.add_argument('--end', type=int, required=False)
    args = parser.parse_args()

    start_scraping(args.file, start=args.start, end=args.end)
