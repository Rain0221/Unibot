import datetime
import os
import random
import sqlite3
import time

from PIL import Image

from modules.gacha import getcharaname
from modules.pjskinfo import logtohtml, writelog


def charainfo(alias, qunnum=''):
    resp = aliastocharaid(alias, qunnum)
    qunalias = ''
    allalias = ''
    if resp[0] == 0:
        return "找不到你说的角色哦"
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from qunalias where charaid={resp[0]} AND qunnum="{qunnum}"')
    for row in cursor:
        qunalias = qunalias + row[1] + "，"

    cursor = c.execute(f'SELECT * from charaalias where charaid={resp[0]}')
    for row in cursor:
        allalias = allalias + row[0] + "，"

    conn.close()
    return f"{resp[1]}\n全群昵称：{allalias[:-1]}\n本群昵称：{qunalias[:-1]}"

def charadel(alias, qqnum=None):
    resp = aliastocharaid(alias)
    if resp[0] == 0:
        return "找不到你说的角色哦，如删除仅本群可用昵称请使用grcharadel"
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    c.execute(f'DELETE from charaalias where alias="{alias}"')
    conn.commit()
    conn.close()
    timeArray = time.localtime(time.time())
    Time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    writelog(f'[{Time}] {qqnum}: 删除了{resp[1]}的昵称:{alias}')
    return "删除成功！"

def grcharadel(alias, qunnum=''):
    charaid = 0
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from qunalias where alias="{alias}" AND qunnum="{qunnum}"')
    for row in cursor:
        charaid = row[2]
    if charaid == 0:
        conn.close()
        return "找不到你说的角色哦，如删除全群可用昵称请使用charadel"
    c.execute(f'DELETE from qunalias where alias="{alias}" AND qunnum="{qunnum}"')
    conn.commit()
    conn.close()
    return "删除成功！"


def aliastocharaid(alias, qunnum=''):
    charaid = 0
    name = ''
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from qunalias where alias="{alias}" AND qunnum="{qunnum}"')
    for row in cursor:
        charaid = row[2]
    if charaid == 0:
        cursor = c.execute(f'SELECT * from charaalias where alias="{alias}"')
        for row in cursor:
            charaid = row[1]
    if charaid != 0:
        name = getcharaname(charaid)
    conn.close()
    return charaid, name

def charaset(newalias, oldalias, qqnum=None):
    resp = aliastocharaid(oldalias)
    if resp[0] == 0:
        return "找不到你说的角色哦，如删除仅本群可用昵称请使用grcharadel"
    charaid = resp[0]
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from charaalias where alias="{newalias}"')
    # 看一下新的昵称在不在 在就更新 不在就增加
    alreadyin = False
    for raw in cursor:
        alreadyin = True
    if alreadyin:
        c.execute(f'UPDATE charaalias SET charaid={charaid} WHERE alias= "{newalias}"')
    else:
        sql_add = 'insert into charaalias(ALIAS,CHARAID) values(?, ?)'
        c.execute(sql_add, (newalias, charaid))
    conn.commit()
    conn.close()
    timeArray = time.localtime(time.time())
    Time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    writelog(f'[{Time}] {qqnum}: {newalias}->{resp[1]}')
    return f"设置成功！(全群可用)\n{newalias}->{resp[1]}\n如果设置不合适的昵称将会被拉黑哦，删除命令：charadel昵称"


def grcharaset(newalias, oldalias, qunnum):
    resp = aliastocharaid(oldalias)
    if resp[0] == 0:
        return "找不到你说的角色哦，如删除仅本群可用昵称请使用grcharadel"
    charaid = resp[0]
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from qunalias where alias="{newalias}" AND qunnum="{qunnum}"')
    # 看一下新的昵称在不在 在就更新 不在就增加
    alreadyin = False
    for raw in cursor:
        alreadyin = True
    if alreadyin:
        c.execute(f'UPDATE qunalias SET charaid={charaid} WHERE alias="{newalias}" AND qunnum="{qunnum}"')
    else:
        sql_add = 'insert into qunalias(QUNNUM,ALIAS,CHARAID) values(?, ?, ?)'
        c.execute(sql_add, (str(qunnum), newalias, charaid))
    conn.commit()
    conn.close()
    return f"设置成功！(仅本群可用)\n{newalias}->{resp[1]}"

def get_card(charaid):
    if random.randint(0, 1) == 1:
        path = 'data/assets/sekai/assetbundle/resources/startapp/character/member'
        target = []
        files = os.listdir(path)
        files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
        for i in files_dir:
            if i[:6] == 'res0' + charaid.zfill(2):
                target.append(i)
        path = path + "/" + target[random.randint(0, len(target) - 1)]
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
        target = []
        files = os.listdir(path)
        files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
        for i in files_dir:
            if i[:6] == 'res0' + charaid.zfill(2):
                target.append(i)
        path = path + "/" + target[random.randint(0, len(target) - 1)]
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