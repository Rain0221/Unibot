import datetime
import difflib
import json
import sqlite3
import time

import pytz
from PIL import Image, ImageFont, ImageDraw
import requests
import yaml

from modules.pjskinfo import musiclength
from modules.sk import verifyid

apiurl = 'http://127.0.0.1:5001/api'

rankline = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000,
            10000, 20000, 30000, 40000, 50000, 100000, 100000000]
predictline = [100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000, 10000, 20000, 30000, 40000, 50000, 100000, 100000000]

class musicinfo(object):

    def __init__(self):
        self.id = 0
        self.title = ''
        self.lyricist = ''
        self.composer = ''
        self.arranger = ''
        self.publishedAt = 0
        self.hot = 0
        self.hotAdjust = 0
        self.length = 0
        self.fullPerfectRate = [0, 0, 0, 0, 0]
        self.fullComboRate = [0, 0, 0, 0, 0]
        self.clearRate = [0, 0, 0, 0, 0]
        self.playLevel = [0, 0, 0, 0, 0]
        self.noteCount = [0, 0, 0, 0, 0]
        self.playLevelAdjust = [0, 0, 0, 0, 0]
        self.fullComboAdjust = [0, 0, 0, 0, 0]
        self.fullPerfectAdjust = [0, 0, 0, 0, 0]
        self.fillerSec = 0

def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def enaliastomusicid(alias):
    if alias[:1] == ' ':
        alias = alias[1:]
    if alias[-1:] == ' ':
        alias = alias[:-1]
    if alias == '':
        return {'musicid': 0, 'match': 0, 'name': '', 'translate': ''}
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from pjskalias where alias=? COLLATE NOCASE', (alias,))
    for row in cursor:
        with open('../enapi/masterdata/musics.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        name = ''
        for musics in data:
            if musics['id'] != row[1]:
                continue
            name = musics['title']
            break
        with open('yamls/translate.yaml', encoding='utf-8') as f:
            trans = yaml.load(f, Loader=yaml.FullLoader)['musics']
        try:
            translate = trans[row[1]]
            if translate == name:
                translate = ''
        except KeyError:
            translate = ''
        conn.close()
        return {'musicid': row[1], 'match': 1, 'name': name, 'translate': translate}
    conn.close()
    return enmatchname(alias)


def enmatchname(alias):
    match = {'musicid': 0, "match": 0, 'name': ''}
    with open('../enapi/masterdata/musics.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open('yamls/translate.yaml', encoding='utf-8') as f:
        trans = yaml.load(f, Loader=yaml.FullLoader)['musics']

    for musics in data:
        name = musics['title']
        similar = string_similar(alias.lower(), name.lower())
        if similar > match['match']:
            match['match'] = similar
            match['musicid'] = musics['id']
            match['name'] = musics['title']
        try:
            translate = trans[musics['id']]
            if '/' in translate:
                alltrans = translate.split('/')
                for i in alltrans:
                    similar = string_similar(alias.lower(), i.lower())
                    if similar > match['match']:
                        match['match'] = similar
                        match['musicid'] = musics['id']
                        match['name'] = musics['title']
            else:
                similar = string_similar(alias.lower(), translate.lower())
                if similar > match['match']:
                    match['match'] = similar
                    match['musicid'] = musics['id']
                    match['name'] = musics['title']
        except KeyError:
            pass
    try:
        match['translate'] = trans[match['musicid']]
        if match['translate'] == match['name']:
            match['translate'] = ''
    except KeyError:
        match['translate'] = ''
    return match



def encurrentevent():
    with open('../enapi/masterdata/events.json', 'r', encoding='utf-8') as f:
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

def ensk(targetid=None, targetrank=None, secret=False):
    event = encurrentevent()
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
        with open('../enapi/masterdata/cheerfulCarnivalTeams.json', 'r', encoding='utf-8') as f:
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
    return msg

class userprofile(object):

    def __init__(self):
        self.name = ''
        self.rank = 0
        self.userid = ''
        self.twitterId = ''
        self.word = ''
        self.userDecks = [0, 0, 0, 0, 0]
        self.special_training = [False, False, False, False, False]
        self.full_perfect = [0, 0, 0, 0, 0]
        self.full_combo = [0, 0, 0, 0, 0]
        self.clear = [0, 0, 0, 0, 0]
        self.mvpCount = 0
        self.superStarCount = 0
        self.userProfileHonors = {}
        self.characterRank = {}
        self.characterId = 0
        self.highScore = 0
        self.masterscore = {}
        self.expertscore = {}
        for i in range(26, 37):
            self.masterscore[i] = [0, 0, 0, 0]
        for i in range(21, 32):
            self.expertscore[i] = [0, 0, 0, 0]

    def getprofile(self, userid):
        resp = requests.get(f'{apiurl}/user/{userid}/profile')
        data = json.loads(resp.content)
        # with open('piccache\profile.json', 'r', encoding='utf-8') as f:
        #     data = json.load(f)
        self.name = data['user']['userGamedata']['name']
        self.twitterId = data['userProfile']['twitterId']
        self.userid = userid
        self.word = data['userProfile']['word']
        self.rank = data['user']['userGamedata']['rank']
        try:
            self.characterId = data['userChallengeLiveSoloResults'][0]['characterId']
            self.highScore = data['userChallengeLiveSoloResults'][0]['highScore']
        except:
            pass
        self.characterRank = data['userCharacters']
        self.userProfileHonors = [{},{},{}]
        for i in range(0, 3):
            try:
                honorid = data['userProfile'][f'honorId{i+1}']
                for honor in data['userHonors']:
                    if honor['honorId'] == honorid:
                        self.userProfileHonors[i] = honor
            except:
                pass

        # print(self.userProfileHonors)
        with open('../enapi/masterdata/musics.json', 'r', encoding='utf-8') as f:
            allmusic = json.load(f)
        with open('../enapi/masterdata/musicDifficulties.json', 'r', encoding='utf-8') as f:
            musicDifficulties = json.load(f)
        result = {}
        now = int(time.time() * 1000)
        for music in allmusic:
            result[music['id']] = [0, 0, 0, 0, 0]
            if music['publishedAt'] < now:
                found = [0, 0]
                for diff in musicDifficulties:
                    if music['id'] == diff['musicId'] and diff['musicDifficulty'] == 'expert':
                        playLevel = diff['playLevel']
                        self.expertscore[playLevel][3] = self.expertscore[playLevel][3] + 1
                        found[0] = 1
                    elif music['id'] == diff['musicId'] and diff['musicDifficulty'] == 'master':
                        playLevel = diff['playLevel']
                        self.masterscore[playLevel][3] = self.masterscore[playLevel][3] + 1
                        found[1] = 1
                    if found == [1, 1]:
                        break
        for music in data['userMusicResults']:
            musicId = music['musicId']
            musicDifficulty = music['musicDifficulty']
            playResult = music['playResult']
            self.mvpCount = self.mvpCount + music['mvpCount']
            self.superStarCount = self.superStarCount + music['superStarCount']
            if musicDifficulty == 'easy':
                diffculty = 0
            elif musicDifficulty == 'normal':
                diffculty = 1
            elif musicDifficulty == 'hard':
                diffculty = 2
            elif musicDifficulty == 'expert':
                diffculty = 3
            else:
                diffculty = 4
            if playResult == 'full_perfect':
                if result[musicId][diffculty] < 3:
                    result[musicId][diffculty] = 3
            elif playResult == 'full_combo':
                if result[musicId][diffculty] < 2:
                    result[musicId][diffculty] = 2
            elif playResult == 'clear':
                if result[musicId][diffculty] < 1:
                    result[musicId][diffculty] = 1
        for music in result:
            for i in range(0, 5):
                if result[music][i] == 3:
                    self.full_perfect[i] = self.full_perfect[i] + 1
                    self.full_combo[i] = self.full_combo[i] + 1
                    self.clear[i] = self.clear[i] + 1
                elif result[music][i] == 2:
                    self.full_combo[i] = self.full_combo[i] + 1
                    self.clear[i] = self.clear[i] + 1
                elif result[music][i] == 1:
                    self.clear[i] = self.clear[i] + 1
                if i == 4:
                    for diff in musicDifficulties:
                        if music == diff['musicId'] and diff['musicDifficulty'] == 'master':
                            playLevel = diff['playLevel']
                            break
                    if result[music][i] == 3:
                        self.masterscore[playLevel][0] += 1
                        self.masterscore[playLevel][1] += 1
                        self.masterscore[playLevel][2] += 1
                    elif result[music][i] == 2:
                        self.masterscore[playLevel][1] += 1
                        self.masterscore[playLevel][2] += 1
                    elif result[music][i] == 1:
                        self.masterscore[playLevel][2] += 1
                elif i == 3:
                    for diff in musicDifficulties:
                        if music == diff['musicId'] and diff['musicDifficulty'] == 'expert':
                            playLevel = diff['playLevel']
                            break
                    if result[music][i] == 3:
                        self.expertscore[playLevel][0] += 1
                        self.expertscore[playLevel][1] += 1
                        self.expertscore[playLevel][2] += 1
                    elif result[music][i] == 2:
                        self.expertscore[playLevel][1] += 1
                        self.expertscore[playLevel][2] += 1
                    elif result[music][i] == 1:
                        self.expertscore[playLevel][2] += 1
        for i in range(0, 5):
            self.userDecks[i] = data['userDecks'][0][f'member{i + 1}']
            for userCards in data['userCards']:
                if userCards['cardId'] != self.userDecks[i]:
                    continue
                if userCards['defaultImage'] == "special_training":
                    self.special_training[i] = True


def endaibu(targetid=None, secret=False):
    try:
        profile = userprofile()
        profile.getprofile(targetid)
    except (json.decoder.JSONDecodeError, IndexError):
        return '未找到玩家'
    if secret:
        text = f"{profile.name}\n"
    else:
        text = f"{profile.name} - {targetid}\n"
    text = text + f"expert进度:FC {profile.full_combo[3]}/{profile.clear[3]}," \
                  f" AP{profile.full_perfect[3]}/{profile.clear[3]}\n" \
                  f"master进度:FC {profile.full_combo[4]}/{profile.clear[4]}," \
                  f" AP{profile.full_perfect[4]}/{profile.clear[4]}\n"
    # 32ap = profile.masterscore[32][0]
    # 32fc = profile.masterscore[32][1]
    ap33plus = profile.masterscore[33][0] + profile.masterscore[34][0] + profile.masterscore[35][0] + \
               profile.masterscore[36][0]
    fc33plus = profile.masterscore[33][1] + profile.masterscore[34][1] + profile.masterscore[35][1] + \
               profile.masterscore[36][1]
    if ap33plus != 0:
        text = text + f"\nLv.33及以上AP进度：{ap33plus}/{profile.masterscore[33][3] + profile.masterscore[34][3] + profile.masterscore[35][3] + profile.masterscore[36][3]}"
    if fc33plus != 0:
        text = text + f"\nLv.33及以上FC进度：{fc33plus}/{profile.masterscore[33][3] + profile.masterscore[34][3] + profile.masterscore[35][3] + profile.masterscore[36][3]}"
    if profile.masterscore[32][0] != 0:
        text = text + f"\nLv.32AP进度：{profile.masterscore[32][0]}/{profile.masterscore[32][3]}"
    if profile.masterscore[32][1] != 0:
        text = text + f"\nLv.32FC进度：{profile.masterscore[32][1]}/{profile.masterscore[32][3]}"
    return text


def enpjskjindu(userid, private=False, diff='master'):
    profile = userprofile()
    profile.getprofile(userid)
    if private:
        id = '保密'
    else:
        id = userid
    if diff == 'master':
        img = Image.open(r'pics/bgmaster.png')
    else:
        img = Image.open(r'pics/bgexpert.png')
    with open('../enapi/masterdata/cards.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)
    try:
        assetbundleName = ''
        for i in cards:
            if i['id'] == profile.userDecks[0]:
                assetbundleName = i['assetbundleName']
        if profile.special_training[0]:
            cardimg = Image.open(r'data\assets\sekai\assetbundle\resources'
                                 fr'\startapp\thumbnail\chara\{assetbundleName}_after_training.png')
        else:
            cardimg = Image.open(r'data\assets\sekai\assetbundle\resources'
                                 fr'\startapp\thumbnail\chara\{assetbundleName}_normal.png')
        cardimg = cardimg.resize((117, 117))
        r, g, b, mask = cardimg.split()
        img.paste(cardimg, (67, 57), mask)
    except FileNotFoundError:
        pass
    draw = ImageDraw.Draw(img)
    font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 31)
    draw.text((216, 55), profile.name, fill=(0, 0, 0), font=font_style)
    font_style = ImageFont.truetype(r"fonts\FOT-RodinNTLGPro-DB.ttf", 15)
    draw.text((216, 105), 'id:' + id, fill=(0, 0, 0), font=font_style)
    font_style = ImageFont.truetype(r"fonts\FOT-RodinNTLGPro-DB.ttf", 26)
    draw.text((314, 138), str(profile.rank), fill=(255, 255, 255), font=font_style)
    font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 35)
    if diff == 'master':
        levelmin = 26
    else:
        levelmin = 21
        profile.masterscore = profile.expertscore
    for i in range(0, 6):
        text_width = font_style.getsize(str(profile.masterscore[i + levelmin][0]))
        text_coordinate = (int(183 - text_width[0] / 2), int(295 + 97 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin][0]), fill=(228, 159, 251), font=font_style)

        text_width = font_style.getsize(str(profile.masterscore[i + levelmin][1]))
        text_coordinate = (int(183 + 78 - text_width[0] / 2), int(295 + 97 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin][1]), fill=(254, 143, 249), font=font_style)

        text_width = font_style.getsize(str(profile.masterscore[i + levelmin][2]))
        text_coordinate = (int(183 + 2 * 78 - text_width[0] / 2), int(295 + 97 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin][2]), fill=(255, 227, 113), font=font_style)

        text_width = font_style.getsize(str(profile.masterscore[i + levelmin][3]))
        text_coordinate = (int(183 + 3 * 78 - text_width[0] / 2), int(295 + 97 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin][3]), fill=(108, 237, 226), font=font_style)

    for i in range(0, 5):
        text_width = font_style.getsize(str(profile.masterscore[i + levelmin + 6][0]))
        text_coordinate = (int(683 - text_width[0] / 2), int(300 + 96.4 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin + 6][0]), fill=(228, 159, 251), font=font_style)

        text_width = font_style.getsize(str(profile.masterscore[i + levelmin + 6][1]))
        text_coordinate = (int(683 + 78 - text_width[0] / 2), int(300 + 96.4 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin + 6][1]), fill=(254, 143, 249), font=font_style)

        text_width = font_style.getsize(str(profile.masterscore[i + levelmin + 6][2]))
        text_coordinate = (int(683 + 2 * 78 - text_width[0] / 2), int(300 + 96.4 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin + 6][2]), fill=(255, 227, 113), font=font_style)

        text_width = font_style.getsize(str(profile.masterscore[i + levelmin + 6][3]))
        text_coordinate = (int(683 + 3 * 78 - text_width[0] / 2), int(300 + 96.4 * i - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.masterscore[i + levelmin + 6][3]), fill=(108, 237, 226), font=font_style)
    img.save(fr'piccache\{userid}jindu.png')


def enpjskprofile(userid, private=False):
    profile = userprofile()
    profile.getprofile(userid)
    if private:
        id = '保密'
    else:
        id = userid
    img = Image.open(r'pics/bg.png')
    with open('../enapi/masterdata/cards.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)
    try:
        assetbundleName = ''
        for i in cards:
            if i['id'] == profile.userDecks[0]:
                assetbundleName = i['assetbundleName']
        if profile.special_training[0]:
            cardimg = Image.open(r'data\assets\sekai\assetbundle\resources'
                                 fr'\startapp\thumbnail\chara\{assetbundleName}_after_training.png')
        else:
            cardimg = Image.open(r'data\assets\sekai\assetbundle\resources'
                                 fr'\startapp\thumbnail\chara\{assetbundleName}_normal.png')
        cardimg = cardimg.resize((151, 151))
        r, g, b, mask = cardimg.split()
        img.paste(cardimg, (118, 51), mask)
    except FileNotFoundError:
        pass
    draw = ImageDraw.Draw(img)
    font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 45)
    draw.text((295, 45), profile.name, fill=(0, 0, 0), font=font_style)
    font_style = ImageFont.truetype(r"fonts\FOT-RodinNTLGPro-DB.ttf", 20)
    draw.text((298, 116), 'id:' + id, fill=(0, 0, 0), font=font_style)
    font_style = ImageFont.truetype(r"fonts\FOT-RodinNTLGPro-DB.ttf", 34)
    draw.text((415, 157), str(profile.rank), fill=(255, 255, 255), font=font_style)
    font_style = ImageFont.truetype(r"fonts\FOT-RodinNTLGPro-DB.ttf", 22)
    draw.text((182, 318), str(profile.twitterId), fill=(0, 0, 0), font=font_style)

    font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Medium.otf", 24)
    if len(profile.word) > 17:
        draw.text((132, 388), profile.word[:17], fill=(0, 0, 0), font=font_style)
        draw.text((132, 424), profile.word[17:], fill=(0, 0, 0), font=font_style)
    else:
        draw.text((132, 388), profile.word, fill=(0, 0, 0), font=font_style)

    for i in range(0, 5):
        try:
            assetbundleName = ''
            for j in cards:
                if j['id'] == profile.userDecks[i]:
                    assetbundleName = j['assetbundleName']
            if profile.special_training[i]:
                cardimg = Image.open(r'data\assets\sekai\assetbundle\resources'
                                     fr'\startapp\thumbnail\chara\{assetbundleName}_after_training.png')
            else:
                cardimg = Image.open(r'data\assets\sekai\assetbundle\resources'
                                     fr'\startapp\thumbnail\chara\{assetbundleName}_normal.png')
            # cardimg = cardimg.resize((151, 151))
            r, g, b, mask = cardimg.split()
            img.paste(cardimg, (111 + 128 * i, 488), mask)
        except FileNotFoundError:
            pass
    font_style = ImageFont.truetype(r"fonts\FOT-RodinNTLGPro-DB.ttf", 27)
    for i in range(0, 5):
        text_width = font_style.getsize(str(profile.clear[i]))
        text_coordinate = (int(170 + 132 * i - text_width[0] / 2), int(735 - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.clear[i]), fill=(0, 0, 0), font=font_style)

        text_width = font_style.getsize(str(profile.full_combo[i]))
        text_coordinate = (int(170 + 132 * i - text_width[0] / 2), int(735 + 133 - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.full_combo[i]), fill=(0, 0, 0), font=font_style)

        text_width = font_style.getsize(str(profile.full_perfect[i]))
        text_coordinate = (int(170 + 132 * i - text_width[0] / 2), int(735 + 2 * 133 - text_width[1] / 2))
        draw.text(text_coordinate, str(profile.full_perfect[i]), fill=(0, 0, 0), font=font_style)

    character = 0
    font_style = ImageFont.truetype(r"fonts\FOT-RodinNTLGPro-DB.ttf", 29)
    for i in range(0, 5):
        for j in range(0, 4):
            character = character + 1
            characterRank = 0
            for charas in profile.characterRank:
                if charas['characterId'] == character:
                    characterRank = charas['characterRank']
                    break
            text_width = font_style.getsize(str(characterRank))
            text_coordinate = (int(920 + 183 * j - text_width[0] / 2), int(686 + 88 * i - text_width[1] / 2))
            draw.text(text_coordinate, str(characterRank), fill=(0, 0, 0), font=font_style)
    for i in range(0, 2):
        for j in range(0, 4):
            character = character + 1
            characterRank = 0
            for charas in profile.characterRank:
                if charas['characterId'] == character:
                    characterRank = charas['characterRank']
                    break
            text_width = font_style.getsize(str(characterRank))
            text_coordinate = (int(920 + 183 * j - text_width[0] / 2), int(510 + 88 * i - text_width[1] / 2))
            draw.text(text_coordinate, str(characterRank), fill=(0, 0, 0), font=font_style)
            if character == 26:
                break
    draw.text((952, 141), f'{profile.mvpCount}回', fill=(0, 0, 0), font=font_style)
    draw.text((1259, 141), f'{profile.superStarCount}回', fill=(0, 0, 0), font=font_style)
    try:
        chara = Image.open(rf'chara\chr_ts_{profile.characterId}.png')
        chara = chara.resize((70, 70))
        r, g, b, mask = chara.split()
        img.paste(chara, (952, 293), mask)
        draw.text((1032, 315), str(profile.highScore), fill=(0, 0, 0), font=font_style)
    except:
        pass


    try:
        honorpic = generatehonor(profile.userProfileHonors[0], True)
        honorpic = honorpic.resize((266, 56))
        r, g, b, mask = honorpic.split()
        img.paste(honorpic, (104, 228), mask)
    except:
        pass
    try:
        honorpic = generatehonor(profile.userProfileHonors[1], False)
        honorpic = honorpic.resize((126, 56))
        r, g, b, mask = honorpic.split()
        img.paste(honorpic, (375, 228), mask)
    except:
        pass
    try:
        honorpic = generatehonor(profile.userProfileHonors[2], False)
        honorpic = honorpic.resize((126, 56))
        r, g, b, mask = honorpic.split()
        img.paste(honorpic, (508, 228), mask)
    except:
        pass

    img.save(f'piccache/{userid}profile.png')
    return


def generatehonor(honor, ismain=True):
    star = False
    backgroundAssetbundleName = ''
    assetbundleName = ''
    groupId = 0
    honorRarity = 0
    honorType = ''

    try:
        honor['profileHonorType']
    except:
        honor['profileHonorType'] = 'normal'
    if honor['profileHonorType'] == 'normal':
        # 普通牌子
        with open('../enapi/masterdata/honors.json', 'r', encoding='utf-8') as f:
            honors = json.load(f)
        with open('../enapi/masterdata/honorGroups.json', 'r', encoding='utf-8') as f:
            honorGroups = json.load(f)
        for i in honors:
            if i['id'] == honor['honorId']:
                assetbundleName = i['assetbundleName']
                groupId = i['groupId']
                honorRarity = i['honorRarity']
                try:
                    level2 = i['levels'][1]['level']
                    star = True
                except IndexError:
                    pass
                for j in honorGroups:
                    if j['id'] == i['groupId']:
                        try:
                            backgroundAssetbundleName = j['backgroundAssetbundleName']
                        except KeyError:
                            backgroundAssetbundleName = ''
                        honorType = j['honorType']
                        break
        # 数据读取完成
        if ismain:
            # 大图
            if honorRarity == 'low':
                frame = Image.open(r'pics/frame_degree_m_1.png')
            elif honorRarity == 'middle':
                frame = Image.open(r'pics/frame_degree_m_2.png')
            elif honorRarity == 'middle':
                frame = Image.open(r'pics/frame_degree_m_3.png')
            else:
                frame = Image.open(r'pics/frame_degree_m_4.png')
            if backgroundAssetbundleName == '':
                rankpic = None
                pic = Image.open(r'data\assets\sekai\assetbundle\resources'
                                 fr'\startapp\honor\{assetbundleName}\degree_main.png')
                try:
                    rankpic = Image.open(r'data\assets\sekai\assetbundle\resources'
                                         fr'\startapp\honor\{assetbundleName}\rank_main.png')
                except FileNotFoundError:
                    pass
                r, g, b, mask = frame.split()
                if honorRarity == 'low':
                    pic.paste(frame, (8, 0), mask)
                else:
                    pic.paste(frame, (0, 0), mask)
                if rankpic is not None:
                    r, g, b, mask = rankpic.split()
                    pic.paste(rankpic, (0, 0), mask)
            else:
                pic = Image.open(r'data\assets\sekai\assetbundle\resources'
                                 fr'\startapp\honor\{backgroundAssetbundleName}\degree_main.png')
                rankpic = Image.open(r'data\assets\sekai\assetbundle\resources'
                                     fr'\startapp\honor\{assetbundleName}\rank_main.png')
                r, g, b, mask = frame.split()
                if honorRarity == 'low':
                    pic.paste(frame, (8, 0), mask)
                else:
                    pic.paste(frame, (0, 0), mask)
                r, g, b, mask = rankpic.split()
                pic.paste(rankpic, (190, 0), mask)
            if honorType == 'character' or honorType == 'achievement':
                if star is True:
                    for i in range(0, honor['honorLevel']):
                        lv = Image.open(r'pics/icon_degreeLv.png')
                        r, g, b, mask = lv.split()
                        pic.paste(lv, (54 + 16 * i, 63), mask)
        else:
            # 小图
            if honorRarity == 'low':
                frame = Image.open(r'pics/frame_degree_s_1.png')
            elif honorRarity == 'middle':
                frame = Image.open(r'pics/frame_degree_s_2.png')
            elif honorRarity == 'middle':
                frame = Image.open(r'pics/frame_degree_s_3.png')
            else:
                frame = Image.open(r'pics/frame_degree_s_4.png')
            if backgroundAssetbundleName == '':
                rankpic = None
                pic = Image.open(r'data\assets\sekai\assetbundle\resources'
                                 fr'\startapp\honor\{assetbundleName}\degree_sub.png')
                try:
                    rankpic = Image.open(r'data\assets\sekai\assetbundle\resources'
                                         fr'\startapp\honor\{assetbundleName}\rank_sub.png')
                except FileNotFoundError:
                    pass
                r, g, b, mask = frame.split()
                if honorRarity == 'low':
                    pic.paste(frame, (8, 0), mask)
                else:
                    pic.paste(frame, (0, 0), mask)
                if rankpic is not None:
                    r, g, b, mask = rankpic.split()
                    pic.paste(rankpic, (0, 0), mask)
            else:
                pic = Image.open(r'data\assets\sekai\assetbundle\resources'
                                 fr'\startapp\honor\{backgroundAssetbundleName}\degree_sub.png')
                rankpic = Image.open(r'data\assets\sekai\assetbundle\resources'
                                     fr'\startapp\honor\{assetbundleName}\rank_sub.png')
                r, g, b, mask = frame.split()
                if honorRarity == 'low':
                    pic.paste(frame, (8, 0), mask)
                else:
                    pic.paste(frame, (0, 0), mask)
                r, g, b, mask = rankpic.split()
                pic.paste(rankpic, (34, 42), mask)
            if honorType == 'character' or honorType == 'achievement':
                if star is True:
                    if honor['honorLevel'] < 5:
                        for i in range(0, honor['honorLevel']):
                            lv = Image.open(r'pics/icon_degreeLv.png')
                            r, g, b, mask = lv.split()
                            pic.paste(lv, (54 + 16 * i, 63), mask)
                    else:
                        for i in range(0, 5):
                            lv = Image.open(r'pics/icon_degreeLv.png')
                            r, g, b, mask = lv.split()
                            pic.paste(lv, (54 + 16 * i, 63), mask)
                        for i in range(0, honor['honorLevel'] - 5):
                            lv = Image.open(r'pics/icon_degreeLv6.png')
                            r, g, b, mask = lv.split()
                            pic.paste(lv, (54 + 16 * i, 63), mask)
    else:
        # cp牌子
        with open('../enapi/masterdata/bondsHonors.json', 'r', encoding='utf-8') as f:
            bondsHonors = json.load(f)
            for i in bondsHonors:
                if i['id'] == honor['honorId']:
                    gameCharacterUnitId1 = i['gameCharacterUnitId1']
                    gameCharacterUnitId2 = i['gameCharacterUnitId2']
                    honorRarity = i['honorRarity']
                    break
        if ismain:
            # 大图
            if honor['bondsHonorViewType'] == 'reverse':
                pic = bondsbackground(gameCharacterUnitId2, gameCharacterUnitId1)
            else:
                pic = bondsbackground(gameCharacterUnitId1, gameCharacterUnitId2)
            chara1 = Image.open(rf'chara\chr_sd_{str(gameCharacterUnitId1).zfill(2)}_01\chr_sd_'
                                rf'{str(gameCharacterUnitId1).zfill(2)}_01.png')
            chara2 = Image.open(rf'chara\chr_sd_{str(gameCharacterUnitId2).zfill(2)}_01\chr_sd_'
                                rf'{str(gameCharacterUnitId2).zfill(2)}_01.png')
            if honor['bondsHonorViewType'] == 'reverse':
                chara1, chara2 = chara2, chara1
            r, g, b, mask = chara1.split()
            pic.paste(chara1, (0, -40), mask)
            r, g, b, mask = chara2.split()
            pic.paste(chara2, (220, -40), mask)
            if honorRarity == 'low':
                frame = Image.open(r'pics/frame_degree_m_1.png')
            elif honorRarity == 'middle':
                frame = Image.open(r'pics/frame_degree_m_2.png')
            elif honorRarity == 'middle':
                frame = Image.open(r'pics/frame_degree_m_3.png')
            else:
                frame = Image.open(r'pics/frame_degree_m_4.png')
            r, g, b, mask = frame.split()
            if honorRarity == 'low':
                pic.paste(frame, (8, 0), mask)
            else:
                pic.paste(frame, (0, 0), mask)
            wordbundlename = f"honorname_{str(gameCharacterUnitId1).zfill(2)}" \
                             f"{str(gameCharacterUnitId2).zfill(2)}_{str(honor['bondsHonorWordId']%100).zfill(2)}_01"
            word = Image.open(rf'data\assets\sekai\assetbundle\resources\startapp'
                                 fr'\bonds_honor\word\{wordbundlename}.png')
            r, g, b, mask = word.split()
            pic.paste(word, (int(190-(word.size[0]/2)), int(40-(word.size[1]/2))), mask)
            for i in range(0, honor['honorLevel']):
                lv = Image.open(r'pics/icon_degreeLv.png')
                r, g, b, mask = lv.split()
                pic.paste(lv, (54 + 16 * i, 63), mask)
        else:
            # 小图
            if honor['bondsHonorViewType'] == 'reverse':
                pic = bondsbackground(gameCharacterUnitId2, gameCharacterUnitId1, False)
            else:
                pic = bondsbackground(gameCharacterUnitId1, gameCharacterUnitId2, False)
            chara1 = Image.open(rf'chara\chr_sd_{str(gameCharacterUnitId1).zfill(2)}_01\chr_sd_'
                                rf'{str(gameCharacterUnitId1).zfill(2)}_01.png')
            chara2 = Image.open(rf'chara\chr_sd_{str(gameCharacterUnitId2).zfill(2)}_01\chr_sd_'
                                rf'{str(gameCharacterUnitId2).zfill(2)}_01.png')
            if honor['bondsHonorViewType'] == 'reverse':
                chara1, chara2 = chara2, chara1
            chara1 = chara1.resize((120, 102))
            r, g, b, mask = chara1.split()
            pic.paste(chara1, (-5, -20), mask)
            chara2 = chara2.resize((120, 102))
            r, g, b, mask = chara2.split()
            pic.paste(chara2, (60, -20), mask)
            if honorRarity == 'low':
                frame = Image.open(r'pics/frame_degree_s_1.png')
            elif honorRarity == 'middle':
                frame = Image.open(r'pics/frame_degree_s_2.png')
            elif honorRarity == 'middle':
                frame = Image.open(r'pics/frame_degree_s_3.png')
            else:
                frame = Image.open(r'pics/frame_degree_s_4.png')
            r, g, b, mask = frame.split()
            if honorRarity == 'low':
                pic.paste(frame, (8, 0), mask)
            else:
                pic.paste(frame, (0, 0), mask)
            if honor['honorLevel'] < 5:
                for i in range(0, honor['honorLevel']):
                    lv = Image.open(r'pics/icon_degreeLv.png')
                    r, g, b, mask = lv.split()
                    pic.paste(lv, (54 + 16 * i, 63), mask)
            else:
                for i in range(0, 5):
                    lv = Image.open(r'pics/icon_degreeLv.png')
                    r, g, b, mask = lv.split()
                    pic.paste(lv, (54 + 16 * i, 63), mask)
                for i in range(0, honor['honorLevel'] - 5):
                    lv = Image.open(r'pics/icon_degreeLv6.png')
                    r, g, b, mask = lv.split()
                    pic.paste(lv, (54 + 16 * i, 63), mask)
    return pic

def bondsbackground(chara1, chara2, ismain=True):
    if ismain:
        pic1 = Image.open(rf'bonds\{str(chara1)}.png')
        pic2 = Image.open(rf'bonds\{str(chara2)}.png')
        pic2 = pic2.crop((190, 0, 380, 80))
        pic1.paste(pic2, (190, 0))
    else:
        pic1 = Image.open(rf'bonds\{str(chara1)}_sub.png')
        pic2 = Image.open(rf'bonds\{str(chara2)}_sub.png')
        pic2 = pic2.crop((90, 0, 380, 80))
        pic1.paste(pic2, (90, 0))
    return pic1

def enpjskb30(userid, private=False):
    resp = requests.get(f'{apiurl}/user/{userid}/profile')
    data = json.loads(resp.content)
    # with open('piccache\profile.json', 'r', encoding='utf-8') as f:
    #     data = json.load(f)
    name = data['user']['userGamedata']['name']
    with open(r'masterdata/realtime/musicDifficulties.json', 'r', encoding='utf-8') as f:
        diff = json.load(f)
    for i in range(0, len(diff)):
        try:
            diff[i]['playLevelAdjust']
        except KeyError:
            diff[i]['playLevelAdjust'] = 0
            diff[i]['fullComboAdjust'] = 0
            diff[i]['fullPerfectAdjust'] = 0
    for i in range(0, len(diff)):
        diff[i]['result'] = 0
        diff[i]['rank'] = 0
        diff[i]['fclevel+'] = diff[i]['playLevel'] + diff[i]['fullComboAdjust']
        diff[i]['aplevel+'] = diff[i]['playLevel'] + diff[i]['fullPerfectAdjust']
    diff.sort(key=lambda x: x["aplevel+"], reverse=True)
    highest = 0
    for i in range(0, 30):
        highest = highest + diff[i]['aplevel+']
    highest = round(highest / 30, 2)
    with open(r'masterdata/realtime/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    for music in data['userMusicResults']:
        playResult = music['playResult']
        musicId = music['musicId']
        musicDifficulty = music['musicDifficulty']
        i = 0
        for i in range(0, len(diff)):
            if diff[i]['musicId'] == musicId and diff[i]['musicDifficulty'] == musicDifficulty:
                break
        if playResult == 'full_perfect':
            diff[i]['result'] = 2
            diff[i]['rank'] = diff[i]['aplevel+']
        elif playResult == 'full_combo':
            if diff[i]['result'] < 1:
                diff[i]['result'] = 1
                diff[i]['rank'] = diff[i]['fclevel+'] * 0.95
    diff.sort(key=lambda x: x["rank"], reverse=True)
    text = ''
    musictitle = ''
    rank = 0
    for i in range(0, 30):
        rank = rank + diff[i]['rank']
        for j in musics:
            if j['id'] == diff[i]['musicId']:
                musictitle = j['title']
        if diff[i]['playLevelAdjust'] != 0:
            if diff[i]['result'] == 2:
                text = text + f"{musictitle} [{diff[i]['musicDifficulty'].upper()} {diff[i]['playLevel']}]" \
                              f" AP ({round(diff[i]['aplevel+'], 1)})\n"
            if diff[i]['result'] == 1:
                text = text + f"{musictitle} [{diff[i]['musicDifficulty'].upper()} {diff[i]['playLevel']}]" \
                              f" FC ({round(diff[i]['fclevel+'], 1)}×0.95)\n"
        else:
            if diff[i]['result'] == 2:
                text = text + f"{musictitle} [{diff[i]['musicDifficulty'].upper()} {diff[i]['playLevel']}]" \
                              f" AP ({round(diff[i]['aplevel+'], 1)}.?)\n"
            if diff[i]['result'] == 1:
                text = text + f"{musictitle} [{diff[i]['musicDifficulty'].upper()} {diff[i]['playLevel']}]" \
                              f" FC ({round(diff[i]['fclevel+'], 1)}.?×0.95)\n"
    rank = round(rank / 30, 2)
    if private:
        title = name
    else:
        title = name + ' - ' + userid
    title = title + '\n你的ranking为' + str(rank)
    IMG_SIZE = (750, int(190 + text.count('\n') * 31.5))
    img = Image.new('RGB', IMG_SIZE, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(r'fonts\SourceHanSansCN-Medium.otf', 22)
    draw.text((20, 15), title, '#000000', font)
    font = ImageFont.truetype(r'fonts\FOT-RodinNTLGPro-DB.ttf', 22)
    draw.text((20, 95), text, '#000000', font, spacing=10)
    font = ImageFont.truetype(r'fonts\SourceHanSansCN-Medium.otf', 22)
    # draw.text((20, int(85 + text.count('\n') * 31.5)), '当前理论值为' + str(highest), '#000000', font)
    font = ImageFont.truetype(r'fonts\SourceHanSansCN-Medium.otf', 15)
    draw.text((20, int(125 + text.count('\n') * 31.5)), '注：FC权重为0.95，非官方算法，仅供参考娱乐\n'
                                                       '数据来源：https://profile.pjsekai.moe/ '
                                                       '※定数每次统计时可能会改变', '#000000', font)
    img.save(fr'piccache\{userid}b30.png')

def endrawpjskinfo(musicid):
    info = musicinfo()

    with open(r'../enapi/masterdata/musics.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for music in data:
        if music['id'] != musicid:
            continue
        info.title = music['title']
        info.lyricist = music['lyricist']
        info.composer = music['composer']
        info.arranger = music['arranger']
        info.publishedAt = music['publishedAt']
        info.fillerSec = music['fillerSec']



    with open(r'../enapi/masterdata/musicDifficulties.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in range(0, len(data)):
        if data[i]['musicId'] != musicid:
            continue
        info.playLevel = [data[i]['playLevel'], data[i + 1]['playLevel'],
                          data[i + 2]['playLevel'], data[i + 3]['playLevel'], data[i + 4]['playLevel']]
        info.noteCount = [data[i]['noteCount'], data[i + 1]['noteCount'],
                          data[i + 2]['noteCount'], data[i + 3]['noteCount'], data[i + 4]['noteCount']]
        break
    now = int(time.time() * 1000)
    leak = False
    if now < info.publishedAt:
        img = Image.open(r'pics/leak.png')
        leak = True
    else:
        img = Image.open(r'pics/pjskinfoen.png')
    try:
        jacket = Image.open(r'data\assets\sekai\assetbundle\resources'
                            fr'\startapp\music\jacket\jacket_s_{str(musicid).zfill(3)}\jacket_s_{str(musicid).zfill(3)}.png')
        jacket = jacket.resize((650, 650))
        img.paste(jacket, (80, 47))
    except FileNotFoundError:
        pass

    if len(info.title)/2 < 12:
        size = 90
        font_style = ImageFont.truetype(r"fonts\KOZGOPRO-BOLD.OTF", size)
        highplus = 0
    else:
        size = int(90 - (len(info.title)/2 - 12) * 4.5)
        font_style = ImageFont.truetype(r"fonts\KOZGOPRO-BOLD.OTF", size)
        text_width = font_style.getsize(info.title)
        if text_width[1] != 90:
            highplus = (90 - text_width[1]) / 2
        else:
            highplus = 0
    draw = ImageDraw.Draw(img)
    # 标题
    draw.text((760, 100 + highplus), info.title, fill=(1, 255, 221), font=font_style)
    # 作词作曲编曲
    font_style = ImageFont.truetype(r"fonts\KOZGOPRO-BOLD.OTF", 40)
    draw.text((930, 268), info.lyricist, fill=(255, 255, 255), font=font_style)
    draw.text((930, 350), info.composer, fill=(255, 255, 255), font=font_style)
    draw.text((930, 430), info.arranger, fill=(255, 255, 255), font=font_style)
    # 长度
    info.length = musiclength(musicid, info.fillerSec)
    if info.length:
        length = f'{round(info.length, 1)}秒 ({int(info.length / 60)}分{round(info.length - int(info.length / 60) * 60, 1)}秒)'
    else:
        length = 'No data'
    draw.text((928, 514), length, fill=(255, 255, 255), font=font_style)
    # 上线时间
    if info.publishedAt < 1638914400000:
        info.publishedAt = 1638914400000
    Time = datetime.datetime.fromtimestamp(info.publishedAt / 1000,
                                           pytz.timezone('Asia/Shanghai')).strftime('%Y/%m/%d %H:%M:%S (UTC+8)')
    draw.text((930, 593), Time, fill=(255, 255, 255), font=font_style)

    # 难度
    font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 60)
    for i in range(0, 5):
        text_width = font_style.getsize(str(info.playLevel[i]))
        text_coordinate = (int((132 + 138 * i) - text_width[0] / 2), int(873 - text_width[1] / 2))
        draw.text(text_coordinate, str(info.playLevel[i]), fill=(1, 255, 221), font=font_style)
    font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 45)
    for i in range(0, 5):
        text_width = font_style.getsize(str(info.noteCount[i]))
        text_coordinate = (int((132 + 138 * i) - text_width[0] / 2), int(960 - text_width[1] / 2))
        draw.text(text_coordinate, str(info.noteCount[i]), fill=(67, 70, 101), font=font_style)

    if info.clearRate[0] != 0:

        if info.hotAdjust > 0.5:
            hotpic = Image.open(r'pics/hot.png')
        elif info.hotAdjust > 0:
            hotpic = Image.open(r'pics/hot3.png')
        elif info.hotAdjust > -1:
            hotpic = Image.open(r'pics/hot2.png')
        elif info.hotAdjust > -2:
            hotpic = Image.open(r'pics/hot1.png')
        else:
            hotpic = Image.open(r'pics/hot0.png')

        if info.hot == 0:
            hot = '最新最热'
            hotpic = Image.open(r'pics/new.png')
        else:
            hot = str(round(info.hot))

        hotpic = hotpic.resize((48, 48))
        r, g, b, mask = hotpic.split()
        font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 28)
        text_width = font_style.getsize(str(hot))
        text_coordinate = (int(1170 - text_width[0] / 2), int(760 - text_width[1] / 2))
        draw.text(text_coordinate, hot, fill=(67, 70, 101), font=font_style)
        if info.hotAdjust > 0.5:
            if info.hotAdjust > 2:
                text_coordinate = (int(1173 + text_width[0] / 2), int(757 - text_width[1] / 2))
                img.paste(hotpic, text_coordinate, mask)
                text_coordinate = (int(1213 + text_width[0] / 2), int(757 - text_width[1] / 2))
                img.paste(hotpic, text_coordinate, mask)
                text_coordinate = (int(1253 + text_width[0] / 2), int(757 - text_width[1] / 2))
                img.paste(hotpic, text_coordinate, mask)
            elif info.hotAdjust > 1:
                text_coordinate = (int(1173 + text_width[0] / 2), int(757 - text_width[1] / 2))
                img.paste(hotpic, text_coordinate, mask)
                text_coordinate = (int(1213 + text_width[0] / 2), int(757 - text_width[1] / 2))
                img.paste(hotpic, text_coordinate, mask)
            else:
                text_coordinate = (int(1173 + text_width[0] / 2), int(757 - text_width[1] / 2))
                img.paste(hotpic, text_coordinate, mask)
        else:
            text_coordinate = (int(1180 + text_width[0] / 2), int(757 - text_width[1] / 2))
            img.paste(hotpic, text_coordinate, mask)
        for i in range(0, 5):
            clearrate = f'{round(info.clearRate[i] * 100, 1)}%'
            fcrate = f'{round(info.fullComboRate[i] * 100, 1)}%'
            aprate = f'{round(info.fullPerfectRate[i] * 100, 1)}%'
            levelplus = str(round(info.playLevel[i] + info.playLevelAdjust[i], 1))
            text_width = font_style.getsize(str(clearrate))
            text_coordinate = (int(1006 + 116 * i - text_width[0] / 2), int(822 - text_width[1] / 2))
            draw.text(text_coordinate, clearrate, fill=(67, 70, 101), font=font_style)

            text_width = font_style.getsize(str(fcrate))
            text_coordinate = (int(1006 + 116 * i - text_width[0] / 2), int(883 - text_width[1] / 2))
            draw.text(text_coordinate, fcrate, fill=(67, 70, 101), font=font_style)

            text_width = font_style.getsize(str(aprate))
            text_coordinate = (int(1006 + 116 * i - text_width[0] / 2), int(944 - text_width[1] / 2))
            draw.text(text_coordinate, aprate, fill=(67, 70, 101), font=font_style)

            text_width = font_style.getsize(str(levelplus))
            text_coordinate = (int(1006 + 116 * i - text_width[0] / 2), int(1005 - text_width[1] / 2))
            draw.text(text_coordinate, levelplus, fill=(67, 70, 101), font=font_style)

        for i in range(3, 5):
            fclevelplus = str(round(info.playLevel[i] + info.fullComboAdjust[i], 1))
            aplevelplus = str(round(info.playLevel[i] + info.fullPerfectAdjust[i], 1))
            text_width = font_style.getsize(str(fclevelplus))
            text_coordinate = (int(1388 + 116 * i - text_width[0] / 2), int(948 - text_width[1] / 2))
            draw.text(text_coordinate, fclevelplus, fill=(67, 70, 101), font=font_style)

            text_width = font_style.getsize(str(aplevelplus))
            text_coordinate = (int(1388 + 116 * i - text_width[0] / 2), int(1005 - text_width[1] / 2))
            draw.text(text_coordinate, aplevelplus, fill=(67, 70, 101), font=font_style)

        font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 20)
        for i in range(0, 5):
            if info.playLevelAdjust[i] > 1.5:
                adjust = "++"
            elif info.playLevelAdjust[i] > 0.5:
                adjust = "+"
            elif info.playLevelAdjust[i] < -1.5:
                adjust = "--"
            elif info.playLevelAdjust[i] < -0.5:
                adjust = "-"
            else:
                adjust = ""
            if adjust != "":
                text_width = font_style.getsize(str(adjust))
                text_coordinate = (int((132 + 138 * i) - text_width[0] / 2), int(915 - text_width[1] / 2))
                draw.text(text_coordinate, str(adjust), fill=(1, 255, 221), font=font_style)
    img.save(fr'piccache\enpjskinfo{musicid}.png')
    return leak

def enbindid(qqnum, userid):
    if not verifyid(userid):
        return '你这ID有问题啊'
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from enbind where qqnum=?', (qqnum,))
    alreadyin = False
    for raw in cursor:
        alreadyin = True
    if alreadyin:
        c.execute(f'UPDATE enbind SET userid=? WHERE qqnum=?', (userid, qqnum))
    else:
        sql_add = 'insert into enbind(qqnum,userid,isprivate) values(?, ?, ?)'
        c.execute(sql_add, (str(qqnum), str(userid), 0))
    conn.commit()
    conn.close()
    return "绑定成功！"

def ensetprivate(qqnum, isprivate):
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from enbind where qqnum=?', (qqnum,))
    alreadyin = False
    for raw in cursor:
        alreadyin = True
    if alreadyin:
        c.execute(f'UPDATE enbind SET isprivate=? WHERE qqnum=?', (isprivate, qqnum))
    else:
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True

def engetqqbind(qqnum):
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from enbind where qqnum=?', (qqnum,))
    for row in cursor:
        conn.close()
        return row