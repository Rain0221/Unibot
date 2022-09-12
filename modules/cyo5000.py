import requests

from modules.config import proxies, cyo5000url


def cyo5000(para0, para1, filename, israinbow=False):
    if israinbow:
        url = f'{cyo5000url}image?top={para0}&bottom={para1}&noalpha=true&rainbow=true'
    else:
        url = f'{cyo5000url}image?top={para0}&bottom={para1}&noalpha=true'
    resp = requests.get(url, proxies=proxies)
    if 'Bad Request' in resp.text:
        url = f'{cyo5000url}image?top=Bad Request&bottom=Bad Request&noalpha=true'
        resp = requests.get(url, proxies=proxies)
    with open(filename, 'wb') as f:
        f.write(resp.content)

if __name__ == '__main__':
    cyo5000('啊啊啊啊啊', '啊啊啊啊啊', '../piccache/11.png')