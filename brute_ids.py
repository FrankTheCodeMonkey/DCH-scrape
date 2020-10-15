"""
Literally just brute for the ID and look for the 200s and 404s
"""
import requests
import urllib3
import arrow


base = 'https://www.digitalconcerthall.com/en/concert/{}'
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

time = str(arrow.utcnow().format('YYYYMMDDHHmmss'))
PAGINATION_LIMIT = 500

# TODO: PLEASE MAINTAIN
CURRENT_ID_MAX = 53100

f = None
for i in range(0, CURRENT_ID_MAX):
    index = str(i)
    if i % PAGINATION_LIMIT == 0:
        if f:
            f.close()

        file_name = 'result-{}-{}.txt'.format(time, i // PAGINATION_LIMIT)
        f = open(file_name, 'w')
        print('current file', file_name)

    response = requests.get(base.format(index), verify=False)
    if response.status_code == 200:
        f.write('successful {}\n'.format(index))
    else:
        f.write('failure {}\n'.format(index))
