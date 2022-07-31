import json
import sqlite3
import time

import requests
import yaml

from modules.config import apiurl, predicturl, proxies, ispredict

rankline = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000,
            10000, 20000, 30000, 40000, 50000, 100000, 100000000]
predictline = [100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000, 10000, 20000, 30000, 40000, 50000, 100000, 100000000]


def currentevent():
    with open('masterdata/events.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in range(0, len(data)):
        startAt = data[i]['startAt']
        endAt = data[i]['closedAt']
        now = int(round(time.time() * 1000))
        if not startAt < now < endAt:
            continue
        if data[i]['startAt'] < now < data[i]['aggregateAt']:
            status = 'going'
        elif data[i]['aggregateAt'] < now < data[i]['aggregateAt'] + 600000:
            status = 'counting'
        else:
            status = 'end'
        return {'id': data[i]['id'], 'status': status}


def gettime(userid):
    try:
        passtime = int(userid[:-3]) / 1024 / 4096
    except ValueError:
        return 0
    return 1600218000 + int(passtime)


def verifyid(userid):
    registertime = gettime(userid)
    now = int(time.time())
    if registertime <= 1601438400 or registertime >= now:
        return False
    else:
        return True


def ssyc(targetrank, eventid):
    try:
        with open('data/ssyc.yaml') as f:
            cachedata = yaml.load(f, Loader=yaml.FullLoader)
        cachetime = cachedata['cachetime']
        now = int(time.time())
        timepass = now - cachetime
        if timepass < 60 * 30 + 10:
            return cachedata[targetrank]
    except FileNotFoundError:
        cachedata = {}
    predict = json.loads(requests.get(predicturl, proxies=proxies).content)
    if predict['data']['eventId'] != eventid:
        now = int(time.time())
        cachedata['cachetime'] = now
        for i in range(0, 16):
            cachedata[predictline[i]] = 0
        with open('data/ssyc.yaml', 'w') as f:
            yaml.dump(cachedata, f)
        return 0
    cachedata['cachetime'] = int(predict['data']['ts'] / 1000)
    for i in range(0, 16):
        cachedata[predictline[i]] = predict['data'][str(predictline[i])]
    with open('data/ssyc.yaml', 'w') as f:
        yaml.dump(cachedata, f)
    return predict['data'][str(targetrank)]

def skyc():
    text = ''
    event = currentevent()
    eventid = event['id']
    if event['status'] != 'going':
        return '预测暂时不可用'
    try:
        with open('data/ssyc.yaml') as f:
            cachedata = yaml.load(f, Loader=yaml.FullLoader)
        if cachedata[100] == 0:
            return '预测暂时不可用'
        cachetime = cachedata['cachetime']
        now = int(time.time())
        timepass = now - cachetime
        if timepass < 60 * 30 + 10:
            for i in range(0, len(predictline)-1):
                text = text + f'{predictline[i]}名预测：{cachedata[predictline[i]]}\n'
            timeArray = time.localtime(cachetime)
            text = text + '\n预测线来自xfl03(3-3.dev)\n预测生成时间为' + time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            return text
    except FileNotFoundError:
        cachedata = {}
    predict = json.loads(requests.get(predicturl, proxies=proxies).content)
    if predict['data']['eventId'] != eventid:
        now = int(time.time())
        cachedata['cachetime'] = now
        for i in range(0, 16):
            cachedata[predictline[i]] = 0
        with open('data/ssyc.yaml', 'w') as f:
            yaml.dump(cachedata, f)
        return '预测暂时不可用'
    cachedata['cachetime'] = int(predict['data']['ts'] / 1000)
    for i in range(0, 16):
        cachedata[predictline[i]] = predict['data'][str(predictline[i])]
    with open('data/ssyc.yaml', 'w') as f:
        yaml.dump(cachedata, f)

    for i in range(0, len(predictline) - 1):
        text = text + f'{predictline[i]}名预测：{cachedata[predictline[i]]}\n'
    timeArray = time.localtime(cachedata['cachetime'])
    text = text + '\n预测线来自xfl03(3-3.dev)\n预测生成时间为' + time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return text

def sk(targetid=None, targetrank=None, secret=False):
    event = currentevent()
    eventid = event['id']
    if event['status'] == 'counting':
        return '活动分数统计中，不要着急哦！'
    if targetid is not None:
        if not verifyid(targetid):
            return '你这ID有问题啊'
        resp = requests.get(f'{apiurl}/user/%7Buser_id%7D/event/{eventid}/ranking?targetUserId={targetid}')
    else:
        resp = requests.get(f'{apiurl}/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={targetrank}')
    ranking = json.loads(resp.content)
    try:
        name = ranking['rankings'][0]['name']
        rank = ranking['rankings'][0]['rank']
        score = ranking['rankings'][0]['score']
        userId = str(ranking['rankings'][0]['userId'])
    except IndexError:
        return '查不到数据捏，可能这期活动没打'
    try:
        TeamId = ranking['rankings'][0]['userCheerfulCarnival']['cheerfulCarnivalTeamId']
        with open('masterdata/cheerfulCarnivalTeams.json', 'r', encoding='utf-8') as f:
            Teams = json.load(f)
        with open('yamls/translate.yaml', encoding='utf-8') as f:
            trans = yaml.load(f, Loader=yaml.FullLoader)
        try:
            translate = f"({trans['cheerfulCarnivalTeams'][TeamId]})"
        except KeyError:
            translate = ''
        for i in Teams:
            if i['id'] == TeamId:
                teamname = '队伍为' + i['teamName'] + translate + "，"
                break
    except KeyError:
        teamname = ''
    if not secret:
        userId = ' - ' + userId
    else:
        userId = ''
    msg = f'{name}{userId}\n{teamname}分数{score / 10000}W，排名{rank}'
    for i in range(0, 31):
        if rank < rankline[i]:
            break

    if rank > 1:
        if rank == rankline[i - 1]:
            upper = rankline[i - 2]
        else:
            upper = rankline[i - 1]
        resp = requests.get(f'{apiurl}/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={upper}')
        ranking = json.loads(resp.content)
        linescore = ranking['rankings'][0]['score']
        deviation = (linescore - score) / 10000
        msg = msg + f'\n上一档排名{upper}的分数为{linescore/10000}W，相差{deviation}W'
    if rank < 100000:
        if rank == rankline[i]:
            lower = rankline[i + 1]
        else:
            lower = rankline[i]
        resp = requests.get(f'{apiurl}/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={lower}')
        ranking = json.loads(resp.content)
        linescore = ranking['rankings'][0]['score']
        deviation = (score - linescore) / 10000
        msg = msg + f'\n下一档排名{lower}的分数为{linescore/10000}W，相差{deviation}W'
    if event['status'] == 'going' and ispredict:
        for i in range(0, 17):
            if rank < predictline[i]:
                break
        linescore = 0
        if rank > 100:
            upper = predictline[i - 1]
            linescore = ssyc(upper, eventid)
            if linescore != 0:
                msg = msg + f'\n\n{upper}名预测{linescore/10000}W'
        if rank < 100000:
            if rank == predictline[i]:
                lower = predictline[i + 1]
            else:
                lower = predictline[i]
            linescore = ssyc(lower, eventid)
            if linescore != 0:
                msg = msg + f'\n{lower}名预测{linescore/10000}W'
        if linescore != 0:
            msg = msg + f'\n预测线来自xfl03(3-3.dev)'
    return msg

def getqqbind(qqnum):
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from bind where qqnum="{qqnum}"')
    for row in cursor:
        conn.close()
        return row


def bindid(qqnum, userid):
    if not verifyid(userid):
        return '你这ID有问题啊'
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from bind where qqnum="{qqnum}"')
    alreadyin = False
    for raw in cursor:
        alreadyin = True
    if alreadyin:
        c.execute(f'UPDATE bind SET userid="{userid}" WHERE qqnum="{qqnum}"')
    else:
        sql_add = 'insert into bind(qqnum,userid,isprivate) values(?, ?, ?)'
        c.execute(sql_add, (str(qqnum), str(userid), 0))
    conn.commit()
    conn.close()
    return "绑定成功！"

def setprivate(qqnum, isprivate):
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from bind where qqnum="{qqnum}"')
    alreadyin = False
    for raw in cursor:
        alreadyin = True
    if alreadyin:
        c.execute(f'UPDATE bind SET isprivate={isprivate} WHERE qqnum="{qqnum}"')
    else:
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True
