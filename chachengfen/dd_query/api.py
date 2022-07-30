import requests
import os
from configobj import ConfigObj
import json
import time

spath = os.path.split(__file__)[0]

class DObj:
    def __init__(self, filename):
        self.filename = filename
        self.config = ConfigObj(filename, encoding='UTF8')

    def readobj(self, section, item, default: str = "") -> str:
        config = self.config
        try:
            res = config[section][item]
        except:
            res = default
        return res

    def writeobj(self, section, item, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][item] = value
        self.config.write()


def user_search(username):
    url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=bili_user&keyword={username}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    }
    response = requests.request("GET", url, headers=headers)
    return response.text

def get_user_following_list(vmid, ps=50, pn=1, sessdata=""):
    url = f"http://api.bilibili.com/x/relation/followings?vmid={vmid}&ps={ps}&pn={pn}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    }
    if sessdata != "":
        headers["Cookie"] = f"SESSDATA={sessdata};"
    response = requests.request("GET", url, headers=headers)
    return response.text

def get_biliuser_info(mid):
    url = f"http://api.bilibili.com/x/space/acc/info?mid={mid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    }
    response = requests.request("GET", url, headers=headers)
    return response.text

def get_same_following(uid, sessdata, ps=50, pn=1):
    """
    获取共同关注
    :param uid: 待查询UID
    :param sessdata: 自己的Cookie - SESSDATA
    :param ps: 每页数, 50
    :param pn: 页码, 默认1
    """
    url = f"http://api.bilibili.com/x/relation/same/followings?vmid={uid}&ps={ps}&pn={pn}"
    headers = {
        'Cookie': f'SESSDATA={sessdata};'
    }
    response = requests.request("GET", url, headers=headers)
    return response.text

def relation_modify(uid, mtype: int, csrf, sessdata):
    """
    关注/取消关注
    :param uid: 对方UID
    :param mtype: 1关注, 2取消
    :param csrf: csrf, 就是Cookie - bili_jct
    :param sessdata: Cookie - SESSDATA
    """
    url = "https://api.bilibili.com/x/relation/modify"
    payload = f'fid={uid}&act={mtype}&re_src=15&csrf={csrf}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
        'Cookie': f'SESSDATA={sessdata};',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

def get_all_vtb_info_jsonstr():
    if not os.path.isdir(f"{spath}/cache"):
        os.mkdir(f"{spath}/cache")

    config = DObj(f"{spath}/cache/cache.ini")
    last_time = int(config.readobj("cache", "last_update_time", "0"))
    time_now = int(time.time())
    if time_now - last_time > 21600:
        url = "https://api.vtbs.moe/v1/info"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
        }
        proxies = {
            'http': f'127.0.0.1:7890',
            'https': f'127.0.0.1:7890'
        }
        '''
        proxies = {
            'http': f'{sets.BotBaseSettings.Proxy.host}:{sets.BotBaseSettings.Proxy.port}',
            'https': f'{sets.BotBaseSettings.Proxy.host}:{sets.BotBaseSettings.Proxy.port}'
        }
        '''
        response = requests.request("GET", url, headers=headers, proxies=proxies)
        try:
            data = json.loads(response.text)
            if type(data) == list:
                if len(data) > 1000:
                    with open(f"{spath}/cache/vtb_data_simple.json", "w", encoding="utf8") as f:
                        f.write(response.text)
                    config.writeobj("cache", "last_update_time", str(int(time.time())))
        except Exception as e:
            print(e)
        return response.text
    else:
        print("检测到有效缓存")
        with open(f"{spath}/cache/vtb_data_simple.json", "r", encoding="utf8") as f:
            return f.read()

def get_all_vtb_info():
    jsonstr = get_all_vtb_info_jsonstr()
    ret = []
    data = json.loads(jsonstr)
    for v in data:
        if "mid" not in v:
            continue

        ret.append(v)
    return json.dumps(ret, ensure_ascii=False)

