import json
import os
import random
import time

from PIL import Image
from mutagen.mp3 import MP3
from pydub import AudioSegment
from modules.musics import isleak


def getrandomchartold():
    path = 'charts/SekaiViewer'
    target = []
    files = os.listdir(path)
    files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
    for i in files_dir:
        chartfiles = os.listdir(path + "/" + i)
        files_file = [f for f in chartfiles if os.path.isfile(os.path.join(path + "/" + i, f))]
        if 'master.png' in files_file:
            target.append(i)
    # return f"{path}/{target[random.randint(0, len(target))]}/master.png"
    musicid = int(target[random.randint(0, len(target) - 1)])
    if isleak(musicid):
        print('leak重抽')
        return getrandomchart()
    else:
        return musicid


def cutchartimgold(musicid, qunnum):
    img = Image.open(f'charts/SekaiViewer/{musicid}/master.png')
    # pic = pic.resize((160 * row + 32, 1300))
    row = int((img.size[0] - 32) / 160)
    rannum = random.randint(2, row - 1)
    img = img.crop((32 + 160 * (rannum - 1), 0, 32 + 160 * (rannum - 1) + 110, img.size[1]))
    img1 = img.crop((0, 0, 110, 650))
    img2 = img.crop((0, 650, 110, 1300))
    final = Image.new('RGB', (220, 640), (255, 255, 255))
    final.paste(img2, (0, 0))
    final.paste(img1, (110, -10))
    final.save(f'piccache/{qunnum}.png')

def getrandomchart():
    path = 'charts/moe/guess'
    target = []
    files = os.listdir(path)
    files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
    for i in files_dir:
        chartfiles = os.listdir(path + "/" + i)
        files_file = [f for f in chartfiles if os.path.isfile(os.path.join(path + "/" + i, f))]
        if 'master.png' in files_file:
            target.append(i)
    # return f"{path}/{target[random.randint(0, len(target))]}/master.png"
    musicid = int(target[random.randint(0, len(target) - 1)])
    if isleak(musicid):
        print('leak重抽')
        return getrandomchart()
    else:
        return musicid


def cutchartimg(musicid, qunnum):
    img = Image.open(f'charts/moe/guess/{musicid}/master.png')
    row = round((img.size[0] - 93.254) / 280.8)
    rannum = random.randint(2, row - 1)
    img = img.crop((int(94 + 280.8 * (rannum - 1)), 48, int(94 + 280.8 * (rannum - 1) + 190), img.size[1] - 295))
    img1 = img.crop((0, 0, 190, int(img.size[1] / 2) + 20))
    img2 = img.crop((0, int(img.size[1] / 2) - 20, 190, img.size[1]))
    final = Image.new('RGB', (410, int(img.size[1] / 2) - 10), (255, 255, 255))
    final.paste(img2, (10, 0))
    final.paste(img1, (210, -26))
    #final.show()
    final.save(f'piccache/{qunnum}.png')


def getrandomjacket():
    path = 'data/assets/sekai/assetbundle/resources/startapp/music/jacket'
    target = []
    files = os.listdir(path)
    files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
    for i in files_dir:
        target.append(i)
    # return f"{path}/{target[random.randint(0, len(target))]}/master.png"
    musicid = int(target[random.randint(0, len(target) - 1)][-3:])
    if isleak(musicid):
        print('leak重抽')
        return getrandomjacket()
    else:
        return musicid


def cutjacket(musicid, qunnum, size=140, isbw=False):
    img = Image.open('data/assets/sekai/assetbundle/resources'
                     f'/startapp/music/jacket/jacket_s_{str(musicid).zfill(3)}/jacket_s_{str(musicid).zfill(3)}.png')
    ran1 = random.randint(0, img.size[0] - size)
    ran2 = random.randint(0, img.size[1] - size)
    img = img.crop((ran1, ran2, ran1 + size, ran2 + size))
    if isbw:
        img = img.convert("L")
    img.save(f'piccache/{qunnum}.png')


def getrandomcard():
    with open('masterdata/cards.json', 'r', encoding='utf-8') as f:
        cardsdata = json.load(f)
    rannum = random.randint(0, len(cardsdata) - 1)
    while (cardsdata[rannum]['releaseAt'] > int(time.time() * 1000)
           or cardsdata[rannum]['cardRarityType'] == 'rarity_1'
           or cardsdata[rannum]['cardRarityType'] == 'rarity_2'):
        print('重抽')
        rannum = random.randint(0, len(cardsdata) - 1)
    return cardsdata[rannum]['characterId'], cardsdata[rannum]['assetbundleName'], cardsdata[rannum]['prefix'], cardsdata[rannum]['cardRarityType']


def cutcard(assetbundleName, cardRarityType, qunnum, size=250):
    istrained = False
    if cardRarityType == 'rarity_birthday':
        path = 'data/assets/sekai/assetbundle/resources/startapp/' \
               f'character/member/{assetbundleName}/card_normal.png'
    else:
        if random.randint(0, 1) == 1:
            path = 'data/assets/sekai/assetbundle/resources/startapp/' \
                   f'character/member/{assetbundleName}/card_after_training.png'
            istrained = True
        else:
            path = 'data/assets/sekai/assetbundle/resources/startapp/' \
                   f'character/member/{assetbundleName}/card_normal.png'
    print(path)
    img = Image.open(path)
    img = img.convert('RGB')
    if not os.path.exists(path[:-3] + 'jpg'):
        print('转jpg')
        img.save(path[:-3] + 'jpg', quality=95)
    ran1 = random.randint(0, img.size[0] - size)
    ran2 = random.randint(0, img.size[1] - size)
    img = img.crop((ran1, ran2, ran1 + size, ran2 + size))
    img.save(f'piccache/{qunnum}.png')
    return istrained

def defaultvocal(musicid):
    with open('masterdata/musicVocals.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    assetbundleName = ''
    for vocal in data:
        if vocal['musicId'] == musicid:
            if vocal['musicVocalType'] == 'sekai' or vocal['musicVocalType'] == 'instrumental':
                return vocal['assetbundleName']
            elif vocal['musicVocalType'] == 'original_song' or vocal['musicVocalType'] == 'virtual_singer':
                assetbundleName = vocal['assetbundleName']
    return assetbundleName

def getrandommusic():
    path = 'data/assets/sekai/assetbundle/resources/ondemand/music/long'
    with open('masterdata/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    target = []
    for music in musics:
        if music['publishedAt'] < time.time() * 1000:
            target.append(music['id'])
    while True:
        musicid = target[random.randint(0, len(target) - 1)]
        assetbundleName = defaultvocal(musicid)
        if os.path.exists(f'{path}/{assetbundleName}/{assetbundleName}.mp3'):
            break
    return musicid, assetbundleName

def cutmusic(assetbundleName, qunnum, reverse=False):
    path = 'data/assets/sekai/assetbundle/resources/ondemand/music/long'
    musicpath = f'{path}/{assetbundleName}/{assetbundleName}.mp3'
    length = MP3(musicpath).info.length
    music = AudioSegment.from_mp3(musicpath)
    starttime = random.randint(20, int(length) - 10)
    if reverse:
        cut = music[starttime * 1000: starttime * 1000 + 5000]
        cut = cut.reverse()
    else:
        cut = music[starttime * 1000: starttime * 1000 + 1700]
    cut.export(f"piccache/{qunnum}.mp3",format="mp3")
    # TODO: 自动清理音频缓存
# print(getrandomjacket())
# cutjacket(getrandomjacket(), 1232232, 140, True)

