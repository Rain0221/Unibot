import datetime
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler


def time_printer(str):
    timeArray = time.localtime(time.time())
    Time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    print(Time, str)


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
    scheduler = BlockingScheduler()
    scheduler.add_job(cleancache, 'interval', seconds=300, id='cleancache')
    scheduler.start()
