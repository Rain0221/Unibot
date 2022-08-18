import json
import os
import random
import sqlite3
import time

from PIL import Image

from modules.gacha import getcharaname
from modules.pjskinfo import writelog
from modules.texttoimg import texttoimg


def cardidtopic(cardid):
    with open('masterdata/cards.json', 'r', encoding='utf-8') as f:
        allcards = json.load(f)
    assetbundleName = ''
    for card in allcards:
        if card['id'] == cardid:
            assetbundleName = card['assetbundleName']
    if assetbundleName == '':
        return []
    path = 'data/assets/sekai/assetbundle/resources/startapp/character/member'
    path = path + "/" + assetbundleName
    files = os.listdir(path)
    files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]
    if 'card_after_training.png' in files_file:
        return [path + '/card_normal.png', path + '/card_after_training.png']
    else:
        return [path + '/card_normal.png']

def cardtype(cardid, cardCostume3ds, costume3ds):
    # 普通0 限定1
    costume = []
    for i in cardCostume3ds:
        if i['cardId'] == cardid:
            costume.append(i['costume3dId'])
    for costumeid in costume:
        for model in costume3ds:
            if model['id'] == costumeid:
                if model['partType'] == 'hair':
                    return 1
    return 0

def findcard(charaid, cardRarityType=None):
    with open('masterdata/cards.json', 'r', encoding='utf-8') as f:
        allcards = json.load(f)
    with open(f'masterdata/cardCostume3ds.json', 'r', encoding='utf-8') as f:
        cardCostume3ds = json.load(f)
    with open(f'masterdata/costume3ds.json', 'r', encoding='utf-8') as f:
        costume3ds = json.load(f)
    allcards.sort(key=lambda x: x["releaseAt"], reverse=True)
    name = getcharaname(charaid)
    text = ''
    for card in allcards:
        if card['characterId'] == charaid:
            cardtypenum = cardtype(card['id'], cardCostume3ds, costume3ds)
            limit = ''
            if cardtypenum == 1:
                limit = '[限定]'
            rarity = ''
            if card['cardRarityType'] == 'rarity_1':
                rarity = '★'
            elif card['cardRarityType'] == 'rarity_2':
                rarity = '★★'
            elif card['cardRarityType'] == 'rarity_3':
                rarity = '★★★'
            elif card['cardRarityType'] == 'rarity_4':
                rarity = '★★★★'
            elif card['cardRarityType'] == 'rarity_birthday':
                rarity = '生日卡'
            if cardRarityType is not None:
                if card['cardRarityType'] == cardRarityType:
                    text += f"{card['id']}: {limit}{rarity} {card['prefix']} - {name}\n"
            else:
                text += f"{card['id']}: {limit}{rarity} {card['prefix']} - {name}\n"
    texttoimg(text[:-1], 700, f'{charaid}{cardRarityType}')
    return f'{charaid}{cardRarityType}.png'



def charainfo(alias, qunnum=''):
    resp = aliastocharaid(alias, qunnum)
    qunalias = ''
    allalias = ''
    if resp[0] == 0:
        return "找不到你说的角色哦"
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f"SELECT * from qunalias where charaid=? AND qunnum=?", (resp[0], qunnum))
    for row in cursor:
        qunalias = qunalias + row[1] + "，"

    cursor = c.execute(f"SELECT * from charaalias where charaid=?", (resp[0],))
    for row in cursor:
        allalias = allalias + row[0] + "，"

    conn.close()
    return f"{resp[1]}\n全群昵称：{allalias[:-1]}\n本群昵称：{qunalias[:-1]}"

def charadel(alias, qqnum=None, username='', qun='群与用户名未知，可能来自分布式'):
    resp = aliastocharaid(alias)
    if resp[0] == 0:
        return "找不到你说的角色哦，如删除仅本群可用昵称请使用grcharadel"
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    c.execute(f"DELETE from charaalias where alias=?", (alias,))
    conn.commit()
    conn.close()
    timeArray = time.localtime(time.time())
    Time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    writelog(f'[{Time}] {qun} {username}({qqnum}): 删除了{resp[1]}的昵称:{alias}')
    return "删除成功！\n已记录bot文档中公开的实时日志，乱删将被拉黑"

def grcharadel(alias, qunnum=''):
    charaid = 0
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f"SELECT * from qunalias where alias=? AND qunnum=?", (alias, qunnum))
    for row in cursor:
        charaid = row[2]
    if charaid == 0:
        conn.close()
        return "找不到你说的角色哦，如删除全群可用昵称请使用charadel"
    c.execute(f"DELETE from qunalias where alias=? AND qunnum=?", (alias, qunnum))
    conn.commit()
    conn.close()
    return "删除成功！"


def aliastocharaid(alias, qunnum=''):
    charaid = 0
    name = ''
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f"SELECT * from qunalias where alias=? AND qunnum=?", (alias, qunnum))
    for row in cursor:
        charaid = row[2]
    if charaid == 0:
        cursor = c.execute(f"SELECT * from charaalias where alias=?", (alias,))
        for row in cursor:
            charaid = row[1]
    if charaid != 0:
        name = getcharaname(charaid)
    conn.close()
    return charaid, name

def charaset(newalias, oldalias, qqnum=None, username='', qun='群与用户名未知，可能来自分布式'):
    resp = aliastocharaid(oldalias)
    if resp[0] == 0:
        return "找不到你说的角色哦，如删除仅本群可用昵称请使用grcharadel"
    charaid = resp[0]
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f"SELECT * from charaalias where alias=?", (newalias,))
    # 看一下新的昵称在不在 在就更新 不在就增加
    alreadyin = False
    for raw in cursor:
        alreadyin = True
    if alreadyin:
        c.execute(f"UPDATE charaalias SET charaid=? WHERE alias= ?", (charaid, newalias))
    else:
        sql_add = 'insert into charaalias(ALIAS,CHARAID) values(?, ?)'
        c.execute(sql_add, (newalias, charaid))
    conn.commit()
    conn.close()
    timeArray = time.localtime(time.time())
    Time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    writelog(f'[{Time}] {qun} {username}({qqnum}): {newalias}->{resp[1]}')
    return f"设置成功！(全群可用)\n{newalias}->{resp[1]}\n已记录bot文档中公开的实时日志，设置不合适的昵称将会被拉黑"


def grcharaset(newalias, oldalias, qunnum):
    resp = aliastocharaid(oldalias)
    if resp[0] == 0:
        return "找不到你说的角色哦，如删除仅本群可用昵称请使用grcharadel"
    charaid = resp[0]
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f"SELECT * from qunalias where alias=? AND qunnum=?", (newalias, qunnum))
    # 看一下新的昵称在不在 在就更新 不在就增加
    alreadyin = False
    for raw in cursor:
        alreadyin = True
    if alreadyin:
        c.execute(f"UPDATE qunalias SET charaid=? WHERE alias=? AND qunnum=?", (charaid, newalias, qunnum))
    else:
        sql_add = 'insert into qunalias(QUNNUM,ALIAS,CHARAID) values(?, ?, ?)'
        c.execute(sql_add, (str(qunnum), newalias, charaid))
    conn.commit()
    conn.close()
    return f"设置成功！(仅本群可用)\n{newalias}->{resp[1]}"

def get_card(charaid):
    with open('masterdata/cards.json', 'r', encoding='utf-8') as f:
        allcards = json.load(f)
    cardsdata = []
    for i in allcards:
        if i['characterId'] == charaid:
            cardsdata.append({
                'prefix': i['prefix'],
                'assetbundleName': i['assetbundleName'],
                'releaseAt': i['releaseAt'],
            })
    rannum = random.randint(0, len(cardsdata) - 1)
    while cardsdata[rannum]['releaseAt'] > int(time.time() * 1000):
        print(cardsdata[rannum]['prefix'], '重抽')
        rannum = random.randint(0, len(cardsdata) - 1)
    if random.randint(0, 1) == 1:
        path = 'data/assets/sekai/assetbundle/resources/startapp/character/member'
        path = path + "/" + cardsdata[rannum]['assetbundleName']
        files = os.listdir(path)
        files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]
        if 'card_after_training.png' in files_file:
            if random.randint(0, 1) == 1:
                path = path + '/card_after_training.png'
            else:
                path = path + '/card_normal.png'
        else:
            path = path + '/card_normal.png'
        if not os.path.exists(path[:-3] + 'jpg'):  # 频道bot最多发送4MB 这里转jpg缩小大小
            im = Image.open(path)
            im = im.convert('RGB')
            im.save(path[:-3] + 'jpg', quality=95)
    else:
        path = 'data/assets/sekai/assetbundle/resources/startapp/character/member_cutout_trm'
        path = path + "/" + cardsdata[rannum]['assetbundleName']
        files = os.listdir(path)
        files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]
        if 'after_training.png' in files_file:
            if random.randint(0, 1) == 1:
                path = path + '/after_training.png'
            else:
                path = path + '/normal.png'
        else:
            path = path + '/normal.png'
    return path
