import requests
import urllib3
import arrow


base = 'https://www.digitalconcerthall.com/en/concert/{}'
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

time = str(arrow.utcnow().format('YYYYMMDDHHmmss'))
PAGINATION_LIMIT = 500

f = None
for i in range(11000, 53100):
    index = str(i)
    if i % PAGINATION_LIMIT == 0:
        if f:
            f.close()

        f = open('result-{}-{}.txt'.format(time, i // PAGINATION_LIMIT), 'w')

    response = requests.get(base.format(index), verify=False)
    if response.status_code == 200:
        f.write('successful {}\n'.format(index))
    else:
        f.write('failure {}\n'.format(index))
