import os.path
import threading
from argparse import Namespace
from os.path import join

import requests

import config
from ct.ChurchTools import ChurchTools


def fetch_all_songs(page: int):
    l = ct._do_get(f'/songs?page={page}')
    ls = l.json()
    for s in ls['data']:
        for a in s['arrangements']:
            for f in a['files']:
                ext = f['name'].split('.')[-1]
                if len(ext) > 8 or ' ' in ext:
                    ext = 'none'
                response = requests.get(f['fileUrl'], stream=True, headers=ct._headers)
                if ext == 'txt' and '['.encode('utf-8') not in response.content:
                    ext = 'text'
                if not os.path.exists(join('/onedrive', ext)):
                    os.makedirs(join('/onedrive', ext), exist_ok=True)
                with open(join('/onedrive', ext, f['name']), 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        out_file.write(chunk)
    print(f'Page {page} downloaded\n', end='')


config.args.parsed = Namespace(config=open('./ctla_config.json'))
config.load()
ct = ChurchTools()
l = ct._do_get('/songs')
ls = l.json()
pages = ls['meta']['pagination']['lastPage']
threads = []

for i in range(pages):
    t = threading.Thread(target=fetch_all_songs, args=(i + 1,))
    threads.append(t)

# Start each thread
for t in threads:
    t.start()

# Wait for all threads to finish
for t in threads:
    t.join()
