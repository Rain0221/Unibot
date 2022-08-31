import datetime
import json
import os.path
import sqlite3
import time
import traceback

import pytz
import requests
import yaml

from modules.config import apiurl, predicturl, proxies, ispredict, enapiurl, twapiurl

rankline = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000,
            10000, 20000, 30000, 40000, 50000, 100000, 100000000]
predictline = [100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000, 10000, 20000, 30000, 40000, 50000, 100000, 100000000]

def timeremain(time):
    if time < 60:
        return f'{int(time)}秒'
    elif time < 60*60:
        return f'{int(time / 60)}分{int(time % 60)}秒'
    elif time < 60*60*24:
        hours = int(time / 60 / 60)
        remain = time - 3600 * hours
        return f'{int(time / 60 / 60)}小时{int(remain / 60)}分{int(remain % 60)}秒'
    else:
        days = int(time / 3600 / 24)
        remain = time - 3600 * 24 * days
        return f'{int(days)}天{timeremain(remain)}'


def currentevent(server):
    if server == 'jp':
        with open('masterdata/events.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif server == 'tw':
        with open('../twapi/masterdata/events.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif server == 'en':
        with open('../enapi/masterdata/events.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    for i in range(0, len(data)):
        startAt = data[i]['startAt']
        endAt = data[i]['closedAt']
        now = int(round(time.time() * 1000))
        remain = ''
        if not startAt < now < endAt:
            continue
        if data[i]['startAt'] < now < data[i]['aggregateAt']:
            status = 'going'
            remain = timeremain((data[i]['aggregateAt'] - now) / 1000)
        elif data[i]['aggregateAt'] < now < data[i]['aggregateAt'] + 600000:
            status = 'counting'
        else:
            status = 'end'
        return {'id': data[i]['id'], 'status': status, 'remain': remain}


def eventtrack():
    event = currentevent('jp')
    if event['status'] == 'going':
        eventid = event['id']
        if not os.path.exists(f'yamls/event/{eventid}'):
            os.makedirs(f'yamls/event/{eventid}')
        try:
            with open(f'yamls/event/{eventid}/chafang.yaml') as f:
                users = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            return
        for targetid in users:
            try:
                resp = requests.get(f'{apiurl}/user/%7Buser_id%7D/event/{eventid}/ranking?targetUserId={targetid}')
                ranking = json.loads(resp.content)
                now = int(time.time())
                try:
                    with open(f'yamls/event/{eventid}/{targetid}.yaml') as f:
                        userscores = yaml.load(f, Loader=yaml.FullLoader)
                except FileNotFoundError:
                    userscores = {}
                userscores[now] = ranking['rankings'][0]['score']
                with open(f'yamls/event/{eventid}/{targetid}.yaml', 'w', encoding='utf-8') as f:
                    yaml.dump(userscores, f)
            except:
                traceback.print_exc()

def chafang(targetid=None, targetrank=None):
    event = currentevent('jp')
    eventid = event['id']
    if targetid is None:
        resp = requests.get(f'{apiurl}/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={targetrank}')
        ranking = json.loads(resp.content)
        targetid = ranking['rankings'][0]['userId']
    else:
        resp = requests.get(f'{apiurl}/user/%7Buser_id%7D/event/{eventid}/ranking?targetUserId={targetid}')
        ranking = json.loads(resp.content)
    username = ranking['rankings'][0]['name']
    if event['status'] == 'going':
        try:
            with open(f'yamls/event/{eventid}/{targetid}.yaml') as f:
                userscores = yaml.load(f, Loader=yaml.FullLoader)
            lasttime = 0
            twentybefore = 0
            hourbefore = 0
            text = f'{username} - {targetid}\n'
            for time in userscores:
                lasttime = time
            for time in userscores:
                if -20 < time - (lasttime - 20 * 60) < 20:
                    twentybefore = time
            for time in userscores:
                if -20 < time - (lasttime - 60 * 60) < 20:
                    hourbefore = time
            lastupdate = 0
            count = 0
            pts = []
            for time in userscores:
                count += 1
                if count == 1:
                    lastupdate = userscores[time]
                else:
                    if userscores[time] != lastupdate:
                        pts.append(userscores[time]-lastupdate)
                        lastupdate = userscores[time]
            if len(pts) >= 10:
                ptsum = 0
                for i in range(len(pts)-10, len(pts)):
                    ptsum += pts[i]
                text += f'近10次平均pt：{(ptsum / 10)/10000}W\n'
            if hourbefore != 0:
                text += f'时速: {(userscores[lasttime] - userscores[hourbefore])/10000}W\n'
            if twentybefore != 0:
                text += f'20min*3时速: {((userscores[lasttime] - userscores[twentybefore])*3)/10000}W\n'
            return text
        except FileNotFoundError:
            return '该玩家没有加入查询'

def getstoptime(targetid=None, targetrank=None):
    event = currentevent('jp')
    eventid = event['id']
    if targetid is None:
        resp = requests.get(f'{apiurl}/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={targetrank}')
        ranking = json.loads(resp.content)
        targetid = ranking['rankings'][0]['userId']
    else:
        resp = requests.get(f'{apiurl}/user/%7Buser_id%7D/event/{eventid}/ranking?targetUserId={targetid}')
        ranking = json.loads(resp.content)
    username = ranking['rankings'][0]['name']
    try:
        with open(f'yamls/event/{eventid}/{targetid}.yaml') as f:
            userscores = yaml.load(f, Loader=yaml.FullLoader)
        lastupdate = 0
        count = 0
        stop = {}
        stopcount = 0
        stopping = False
        for time in userscores:
            count += 1
            if count == 1:
                lastupdate = time
            else:
                if userscores[time] == userscores[lastupdate]:
                    if time - lastupdate > 5 * 60:
                        if not stopping:
                            stopcount += 1
                            stopping = True
                            stop[stopcount] = {'start': 0, 'end': 0}
                            stop[stopcount]['start'] = lastupdate
                else:
                    lastupdate = time
                    if stopping:
                        stop[stopcount]['end'] = time
                        stopping = False
        text = f'{username} - {targetid}\n'
        if len(stop) != 0:
            for count in stop:
                start = stop[count]['start']
                starttime = datetime.datetime.fromtimestamp(start,
                                           pytz.timezone('Asia/Shanghai')).strftime('%m/%d %H:%M:%S')
                end = stop[count]['end']
                endtime = datetime.datetime.fromtimestamp(end,
                                           pytz.timezone('Asia/Shanghai')).strftime('%m/%d %H:%M:%S')
                text += f'{count}. {starttime} ~ {endtime}\n'
            return text
        else:
            return text + '未停车'

    except FileNotFoundError:
        return '该玩家没有加入查询'


def gettime(userid, server='jp'):
    if server == 'jp' or server == 'en':
        try:
            passtime = int(userid[:-3]) / 1024 / 4096
        except ValueError:
            return 0
        return 1600218000 + int(passtime)
    elif server == 'tw':
        try:
            passtime = int(userid) / 1024 / 1024 / 4096
        except ValueError:
            return 0
        return int(passtime)


def verifyid(userid, server='jp'):
    registertime = gettime(userid, server)
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
    event = currentevent('jp')
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

def sk(targetid=None, targetrank=None, secret=False, server='jp'):
    event = currentevent(server)
    eventid = event['id']
    if event['status'] == 'counting':
        return '活动分数统计中，不要着急哦！'
    if server == 'jp':
        url = apiurl
    elif server == 'en':
        url = enapiurl
    elif server == 'tw':
        url = twapiurl
    if targetid is not None:
        if not verifyid(targetid, server):
            bind = getqqbind(targetid, server)
            if bind is None:
                return '查不到捏'
            elif bind[2]:
                return '查不到捏，可能是不给看'
            else:
                targetid = bind[1]
        resp = requests.get(f'{url}/user/%7Buser_id%7D/event/{eventid}/ranking?targetUserId={targetid}')
    else:
        resp = requests.get(f'{url}/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={targetrank}')
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
        if server == 'tw':
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
        resp = requests.get(f'{url}/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={upper}')
        ranking = json.loads(resp.content)
        linescore = ranking['rankings'][0]['score']
        deviation = (linescore - score) / 10000
        msg = msg + f'\n上一档排名{upper}的分数为{linescore/10000}W，相差{deviation}W'
    if rank < 100000:
        if rank == rankline[i]:
            lower = rankline[i + 1]
        else:
            lower = rankline[i]
        resp = requests.get(f'{url}/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={lower}')
        ranking = json.loads(resp.content)
        linescore = ranking['rankings'][0]['score']
        deviation = (score - linescore) / 10000
        msg = msg + f'\n下一档排名{lower}的分数为{linescore/10000}W，相差{deviation}W'

    if event['status'] == 'going' and ispredict and server == 'jp':
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
    if event['status'] == 'going':
        msg = msg + '\n活动还剩' + event['remain']
    return msg

def teamcount():
    event = currentevent('jp')
    eventid = event['id']
    resp = requests.get(f'{apiurl}/api/cheerful-carnival-team-count/{eventid}')
    data = json.loads(resp.content)

    with open('masterdata/cheerfulCarnivalTeams.json', 'r', encoding='utf-8') as f:
        Teams = json.load(f)
    with open('yamls/translate.yaml', encoding='utf-8') as f:
        trans = yaml.load(f, Loader=yaml.FullLoader)
    text = ''
    for Counts in data['cheerfulCarnivalTeamMemberCounts']:
        TeamId = Counts['cheerfulCarnivalTeamId']
        memberCount = Counts['memberCount']
        try:
            translate = f"({trans['cheerfulCarnivalTeams'][TeamId]})"
        except KeyError:
            translate = ''
        for i in Teams:
            if i['id'] == TeamId:
                text += i['teamName'] + translate + " " + str(memberCount)+ '人\n'
                break
    return text

def getqqbind(qqnum, server):
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    if server == 'jp':
        cursor = c.execute(f'SELECT * from bind where qqnum=?', (qqnum,))
    elif server == 'tw':
        cursor = c.execute(f'SELECT * from twbind where qqnum=?', (qqnum,))
    elif server == 'en':
        cursor = c.execute(f'SELECT * from enbind where qqnum=?', (qqnum,))
    for row in cursor:
        conn.close()
        return row


def bindid(qqnum, userid, server):
    if not verifyid(userid, server):
        return '你这ID有问题啊'
    if server == 'jp':
        server = ''
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from {server}bind where qqnum=?', (qqnum,))
    alreadyin = False
    for raw in cursor:
        alreadyin = True
    if alreadyin:
        c.execute(f'UPDATE {server}bind SET userid=? WHERE qqnum=?', (userid, qqnum))
    else:
        sql_add = f'insert into {server}bind(qqnum,userid,isprivate) values(?, ?, ?)'
        c.execute(sql_add, (str(qqnum), str(userid), 0))
    conn.commit()
    conn.close()
    return "绑定成功！"

def setprivate(qqnum, isprivate, server):
    if server == 'jp':
        server = ''
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from {server}bind where qqnum=?', (qqnum,))
    alreadyin = False
    for raw in cursor:
        alreadyin = True
    if alreadyin:
        c.execute(f'UPDATE {server}bind SET isprivate=? WHERE qqnum=?', (isprivate, qqnum))
    else:
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True
