import os.path
from argparse import Namespace
import requests
import config
from ct.ChurchTools import ChurchTools
import threading

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
                if not os.path.exists(ext):
                    os.mkdir(ext)
                with open(f'{ext}/{f['name']}', 'wb') as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        out_file.write(chunk)

config.args.parsed = Namespace(config=open('../ctla_config.json'))
config.load()
ct = ChurchTools()
l = ct._do_get('/songs')
ls = l.json()
pages = ls['meta']['pagination']['lastPage']
threads = []

for i in range(pages):
    t = threading.Thread(target=fetch_all_songs, args=(i+1,))
    threads.append(t)

# Start each thread
for t in threads:
    t.start()

# Wait for all threads to finish
for t in threads:
    t.join()