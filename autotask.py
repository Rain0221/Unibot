import datetime
import hashlib
import json
import os
import time

import requests
from apscheduler.schedulers.blocking import BlockingScheduler

from modules.config import proxies


def time_printer(str):
    timeArray = time.localtime(time.time())
    Time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    print(Time, str)

def detectplaydata():
    time_printer('检查playdata更新')
    try:
        jsondata = requests.get('https://gitlab.com/pjsekai/database/musics/-/raw/main/musicDifficulties.json',
                                proxies=proxies)
        json.loads(jsondata.text)
    except:
        print('playdata下载失败')
        return

    with open('masterdata/realtime/musicDifficulties.json', 'rb') as f:
        data = f.read()
    if hashlib.md5(data).hexdigest() != hashlib.md5(jsondata.content).hexdigest():
        print('更新musicDifficulties.json')
        with open("masterdata/realtime/musicDifficulties.json", "wb") as f:
            f.write(jsondata.content)

    try:
        jsondata = requests.get('https://gitlab.com/pjsekai/database/musics/-/raw/main/musics.json',
                                proxies=proxies)
        json.loads(jsondata.text)
    except:
        print('playdata下载失败')
        return

    with open('masterdata/realtime/musics.json', 'rb') as f:
        data = f.read()
    if hashlib.md5(data).hexdigest() != hashlib.md5(jsondata.content).hexdigest():
        print('更新musics.json')
        with open("masterdata/realtime/musics.json", "wb") as f:
            f.write(jsondata.content)

def get_filectime(file):
    return datetime.datetime.fromtimestamp(os.path.getctime(file))


def cleancache(path='piccache/'):
    nowtime = datetime.datetime.now()
    deltime = datetime.timedelta(seconds=300)
    nd = nowtime - deltime
    for root, firs, files in os.walk(path):
        for file in files:
            if file[-4:] == '.png':
                filectime = get_filectime(path + file)
                if filectime < nd:
                    os.remove(path + file)
                    print(f"删除{file} (缓存{nowtime - filectime})")
                else:
                    print(f"跳过{file} (缓存{nowtime - filectime})")


if __name__ == '__main__':
    cleancache()
    detectplaydata()
    scheduler = BlockingScheduler()
    scheduler.add_job(detectplaydata, 'interval', seconds=300, id='playinfocheck')
    scheduler.add_job(cleancache, 'interval', seconds=300, id='cleancache')
    scheduler.start()
