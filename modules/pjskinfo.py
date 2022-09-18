import datetime
import json
import os
import sqlite3
import difflib
import time
from mutagen.mp3 import MP3
import pytz
from PIL import Image, ImageFont, ImageDraw
import yaml

from modules.config import loghtml


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


def aliastomusicid(alias):
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
        with open('masterdata/musics.json', 'r', encoding='utf-8') as f:
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
    return matchname(alias)


def matchname(alias):
    match = {'musicid': 0, "match": 0, 'name': ''}
    with open('masterdata/musics.json', 'r', encoding='utf-8') as f:
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

def get_filectime(file):
    return datetime.datetime.fromtimestamp(os.path.getmtime(file))

def isleak(musicid):
    with open('masterdata/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    for i in musics:
        if i['id'] == musicid:
            if int(time.time() * 1000) < i['publishedAt']:
                return True
            else:
                return False
    return True

def pjskinfo(musicid):
    if os.path.exists(f'piccache/pjskinfo/{musicid}.png'):
        pjskinfotime = get_filectime(f'piccache/pjskinfo/{musicid}.png')
        playdatatime = get_filectime('masterdata/realtime/musics.json')
        with open('masterdata/musics.json', 'r', encoding='utf-8') as f:
            musics = json.load(f)
        for i in musics:
            if i['id'] == musicid:
                publishedAt = i['publishedAt'] / 1000
        if pjskinfotime > playdatatime:  # 缓存后数据未变化
            if time.time() < publishedAt:  # 捷豹
                return True
            else:  # 已上线
                if pjskinfotime.timestamp() < publishedAt:  # 缓存是上线前的
                    return drawpjskinfo(musicid, False)
                return False
        else:
            return drawpjskinfo(musicid, False)
    else:
        return drawpjskinfo(musicid, False)

def drawpjskinfo(musicid, olddir=True):
    info = musicinfo()
    with open('masterdata/realtime/musics.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for music in data:
        if music['id'] == musicid:
            info.title = music['title']
            info.lyricist = music['lyricist']
            info.composer = music['composer']
            info.arranger = music['arranger']
            info.publishedAt = music['publishedAt']
            info.fillerSec = music['fillerSec']
            try:
                info.hot = music['hot']
                info.hotAdjust = music['hotAdjust']
            except KeyError:
                pass
            break
    if info.title == '':
        with open('masterdata/musics.json', 'r', encoding='utf-8') as f:
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


    with open('masterdata/realtime/musicDifficulties.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in range(0, len(data)):
        if data[i]['musicId'] == musicid:
            info.playLevel = [data[i]['playLevel'], data[i + 1]['playLevel'],
                              data[i + 2]['playLevel'], data[i + 3]['playLevel'], data[i + 4]['playLevel']]
            info.noteCount = [data[i]['noteCount'], data[i + 1]['noteCount'],
                              data[i + 2]['noteCount'], data[i + 3]['noteCount'], data[i + 4]['noteCount']]
            try:
                info.playLevelAdjust = [data[i]['playLevelAdjust'], data[i + 1]['playLevelAdjust'],
                                        data[i + 2]['playLevelAdjust'], data[i + 3]['playLevelAdjust'],
                                        data[i + 4]['playLevelAdjust']]
                info.fullComboAdjust = [data[i]['fullComboAdjust'], data[i + 1]['fullComboAdjust'],
                                        data[i + 2]['fullComboAdjust'], data[i + 3]['fullComboAdjust'],
                                        data[i + 4]['fullComboAdjust']]
                info.fullPerfectAdjust = [data[i]['fullPerfectAdjust'], data[i + 1]['fullPerfectAdjust'],
                                          data[i + 2]['fullPerfectAdjust'], data[i + 3]['fullPerfectAdjust'],
                                          data[i + 4]['fullPerfectAdjust']]
            except KeyError:
                pass
            break
    if info.playLevel[0] == 0:
        with open('masterdata/musicDifficulties.json', 'r', encoding='utf-8') as f:
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
        img = Image.open('pics/leak.png')
        leak = True
    else:
        if info.playLevelAdjust[0] == 0:
            img = Image.open('pics/pjskinfonew.png')
        else:
            img = Image.open('pics/pjskinfo.png')
    try:
        jacket = Image.open('data/assets/sekai/assetbundle/resources'
                            f'/startapp/music/jacket/jacket_s_{str(musicid).zfill(3)}/jacket_s_{str(musicid).zfill(3)}.png')
        jacket = jacket.resize((650, 650))
        img.paste(jacket, (80, 47))
    except FileNotFoundError:
        pass
    font_style = ImageFont.truetype("fonts/KOZGOPRO-BOLD.OTF", 90)
    size = font_style.getsize(info.title)
    if size[0] < 1150:
        highplus = 0
    else:
        size = int(90 * (1150 / size[0]))
        font_style = ImageFont.truetype("fonts/KOZGOPRO-BOLD.OTF", size)
        text_width = font_style.getsize(info.title)
        if text_width[1] != 90:
            highplus = (90 - text_width[1]) / 2
        else:
            highplus = 0
    draw = ImageDraw.Draw(img)
    # 标题
    draw.text((760, 100 + highplus), info.title, fill=(1, 255, 221), font=font_style)
    # 作词作曲编曲
    font_style = ImageFont.truetype("fonts/KOZGOPRO-BOLD.OTF", 40)
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
    if info.publishedAt < 1601438400000:
        info.publishedAt = 1601438400000
    Time = datetime.datetime.fromtimestamp(info.publishedAt / 1000,
                                           pytz.timezone('Asia/Shanghai')).strftime('%Y/%m/%d %H:%M:%S (UTC+8)')
    draw.text((930, 593), Time, fill=(255, 255, 255), font=font_style)

    # 难度
    font_style = ImageFont.truetype("fonts/SourceHanSansCN-Bold.otf", 60)
    for i in range(0, 5):
        text_width = font_style.getsize(str(info.playLevel[i]))
        text_coordinate = (int((132 + 138 * i) - text_width[0] / 2), int(873 - text_width[1] / 2))
        draw.text(text_coordinate, str(info.playLevel[i]), fill=(1, 255, 221), font=font_style)
    font_style = ImageFont.truetype("fonts/SourceHanSansCN-Bold.otf", 45)
    for i in range(0, 5):
        text_width = font_style.getsize(str(info.noteCount[i]))
        text_coordinate = (int((132 + 138 * i) - text_width[0] / 2), int(960 - text_width[1] / 2))
        draw.text(text_coordinate, str(info.noteCount[i]), fill=(67, 70, 101), font=font_style)

    if info.playLevelAdjust[0] != 0:

        if info.hotAdjust > 0.5:
            hotpic = Image.open('pics/hot.png')
        elif info.hotAdjust > 0:
            hotpic = Image.open('pics/hot3.png')
        elif info.hotAdjust > -1:
            hotpic = Image.open('pics/hot2.png')
        elif info.hotAdjust > -2:
            hotpic = Image.open('pics/hot1.png')
        else:
            hotpic = Image.open('pics/hot0.png')

        if info.hot == 0:
            hot = '最新最热'
            hotpic = Image.open('pics/new.png')
        else:
            hot = str(round(info.hot))

        hotpic = hotpic.resize((48, 48))
        r, g, b, mask = hotpic.split()
        font_style = ImageFont.truetype("fonts/SourceHanSansCN-Bold.otf", 28)
        text_width = font_style.getsize(str(hot))
        text_coordinate = (int(1760 - text_width[0]), int(805 - text_width[1] / 2))
        if hot == '最新最热':
            text_coordinate = (1680, 786)
        draw.text(text_coordinate, hot, fill=(67, 70, 101), font=font_style)
        if info.hotAdjust > 0.5:
            if info.hotAdjust > 2:
                text_coordinate = (int(1720 + text_width[0] / 2), int(802 - text_width[1] / 2))
                img.paste(hotpic, text_coordinate, mask)
                text_coordinate = (int(1755 + text_width[0] / 2), int(802 - text_width[1] / 2))
                img.paste(hotpic, text_coordinate, mask)
                text_coordinate = (int(1790 + text_width[0] / 2), int(802 - text_width[1] / 2))
                img.paste(hotpic, text_coordinate, mask)
            elif info.hotAdjust > 1:
                text_coordinate = (int(1745 + text_width[0] / 2), int(802 - text_width[1] / 2))
                img.paste(hotpic, text_coordinate, mask)
                text_coordinate = (int(1785 + text_width[0] / 2), int(802 - text_width[1] / 2))
                img.paste(hotpic, text_coordinate, mask)
            else:
                text_coordinate = (int(1755 + text_width[0] / 2), int(802 - text_width[1] / 2))
                img.paste(hotpic, text_coordinate, mask)
        else:
            text_coordinate = (int(1755 + text_width[0] / 2), int(802 - text_width[1] / 2))
            img.paste(hotpic, text_coordinate, mask)

        for i in range(3, 5):
            levelplus = str(round(info.playLevel[i] + info.playLevelAdjust[i], 1))
            fclevelplus = str(round(info.playLevel[i] + info.fullComboAdjust[i], 1))
            aplevelplus = str(round(info.playLevel[i] + info.fullPerfectAdjust[i], 1))

            text_width = font_style.getsize(str(levelplus))
            text_coordinate = (int(1363 + 116 * i - text_width[0] / 2), int(864 - text_width[1] / 2))
            draw.text(text_coordinate, levelplus, fill=(67, 70, 101), font=font_style)

            text_width = font_style.getsize(str(fclevelplus))
            text_coordinate = (int(1363 + 116 * i - text_width[0] / 2), int(922 - text_width[1] / 2))
            draw.text(text_coordinate, fclevelplus, fill=(67, 70, 101), font=font_style)

            text_width = font_style.getsize(str(aplevelplus))
            text_coordinate = (int(1363 + 116 * i - text_width[0] / 2), int(980 - text_width[1] / 2))
            draw.text(text_coordinate, aplevelplus, fill=(67, 70, 101), font=font_style)

        font_style = ImageFont.truetype("fonts/SourceHanSansCN-Bold.otf", 20)
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
    vocals = vocalimg(musicid)
    r, g, b, mask = vocals.split()
    if vocals.size[1] < 320:
        img.paste(vocals, (758, 710), mask)
    else:
        img.paste(vocals, (758, 670), mask)
    if olddir:
        img.save(f'piccache/pjskinfo{musicid}.png')
    else:
        img.save(f'piccache/pjskinfo/{musicid}.png')
    return leak

def vocalimg(musicid):
    with open('masterdata/musicVocals.json', 'r', encoding='utf-8') as f:
        musicVocals = json.load(f)
    with open('masterdata/outsideCharacters.json', 'r', encoding='utf-8') as f:
        outsideCharacters = json.load(f)
    pos = 20
    row = 0
    height = [20, 92, 164, 236, 308]
    cut = [0, 0]
    vs = 0
    sekai = 0
    noan = True

    for vocal in musicVocals:
        if vocal['musicId'] == musicid:
            if vocal['musicVocalType'] == "original_song":
                vs += 1
            elif vocal['musicVocalType'] == "sekai":
                sekai += 1
            elif vocal['musicVocalType'] == "virtual_singer":
                vs += 1
            elif vocal['musicVocalType'] == "instrumental":
                img = Image.open('pics/inst.png')
                return img
            else:
                noan = False
                break
    if vs > 1:
        noan = False

    if noan:
        font_style = ImageFont.truetype("fonts/SourceHanSansCN-Bold.otf", 35)
        img = Image.open('pics/vocal.png')
        if vs == 0:
            draw = ImageDraw.Draw(img)
            draw.text((220, 102), 'SEKAI Ver. ONLY', fill=(227, 246, 251), font=font_style)
        if sekai == 0:
            draw = ImageDraw.Draw(img)
            draw.text((165, 257), 'Virtual Singer Ver. ONLY', fill=(227, 246, 251), font=font_style)
        for vocal in musicVocals:
            if vocal['musicId'] == musicid:
                vocalimg = Image.new('RGBA', (750, 85), color=(0, 0, 0, 0))
                draw = ImageDraw.Draw(vocalimg)
                innerpos = 0
                for chara in vocal['characters']:
                    if chara['characterType'] == 'game_character':
                        chara = Image.open(f'chara/chr_ts_{chara["characterId"]}.png').resize((70, 70))
                        r, g, b, mask = chara.split()
                        vocalimg.paste(chara, (innerpos + 5, 8), mask)
                        innerpos += 80
                    else:
                        try:
                            chara = Image.open(f'chara/outsideCharacters/{chara["characterId"]}.png').resize((70, 70))
                            r, g, b, mask = chara.split()
                            vocalimg.paste(chara, (innerpos + 5, 8), mask)
                            innerpos += 80
                        except:
                            for i in outsideCharacters:
                                if i['id'] == chara['characterId']:
                                    draw.text((innerpos + 8, 20), i['name'], fill=(67, 70, 101), font=font_style)
                                    innerpos += 8 + font_style.getsize(str(i['name']))[0]
                vocalimg = vocalimg.crop((0, 0, innerpos + 15, 150))
                r, g, b, mask = vocalimg.split()
                if vocal['musicVocalType'] == "original_song" or vocal['musicVocalType'] == "virtual_singer":
                    img.paste(vocalimg, (370 - int(vocalimg.size[0] / 2), 162 - int(vocalimg.size[1] / 2)), mask)
                elif vocal['musicVocalType'] == "sekai":
                    img.paste(vocalimg, (370 - int(vocalimg.size[0] / 2), 317 - int(vocalimg.size[1] / 2)), mask)
    else:
        font_style = ImageFont.truetype("fonts/SourceHanSansCN-Bold.otf", 27)
        img = Image.new('RGBA', (720, 380), color=(0, 0, 0, 0))
        for vocal in musicVocals:
            if vocal['musicId'] == musicid:
                vocalimg = Image.new('RGBA', (700, 70), color=(0, 0, 0, 0))
                draw = ImageDraw.Draw(vocalimg)
                if vocal['musicVocalType'] == "original_song":
                    text = '原曲版'
                elif vocal['musicVocalType'] == "sekai":
                    text = 'SEKAI版'
                elif vocal['musicVocalType'] == "virtual_singer":
                    text = 'V版'
                elif vocal['musicVocalType'] == "april_fool_2022":
                    text = '2022愚人节版'
                elif vocal['musicVocalType'] == "another_vocal":
                    text = '其他'
                elif vocal['musicVocalType'] == "instrumental":
                    text = '无人声伴奏'
                else:
                    text = vocal['musicVocalType']
                innerpos = 25 + font_style.getsize(str(text))[0]
                draw.text((20, 20), text, fill=(67, 70, 101), font=font_style)
                for chara in vocal['characters']:
                    if chara['characterType'] == 'game_character':
                        chara = Image.open(f'chara/chr_ts_{chara["characterId"]}.png').resize((60, 60))
                        r, g, b, mask = chara.split()
                        vocalimg.paste(chara, (innerpos + 5, 8), mask)
                        innerpos += 65
                    else:
                        try:
                            chara = Image.open(f'chara/outsideCharacters/{chara["characterId"]}.png').resize((60, 60))
                            r, g, b, mask = chara.split()
                            vocalimg.paste(chara, (innerpos + 5, 8), mask)
                            innerpos += 65
                        except:
                            for i in outsideCharacters:
                                if i['id'] == chara['characterId']:
                                    draw.text((innerpos + 8, 20), i['name'], fill=(67, 70, 101), font=font_style)
                                    innerpos += 8 + font_style.getsize(str(i['name']))[0]
                vocalimg = vocalimg.crop((0, 0, innerpos + 15, 72))
                r, g, b, mask = vocalimg.split()

                if pos + vocalimg.size[0] > 720:
                    pos = 20
                    row += 1
                img.paste(vocalimg, (pos, height[row]), mask)
                if pos + vocalimg.size[0] > cut[0]:
                    cut[0] = pos + vocalimg.size[0]
                pos += vocalimg.size[0]
                if (vocal['musicVocalType'] == "sekai" or vocal['musicVocalType'] == "original_song"
                    or vocal['musicVocalType'] == "virtual_singer") and pos != 20:
                    pos = 20
                    row += 1
        if pos == 20:
            row -= 1
        cut[1] = height[row] + 65
        img = img.crop((0, 0, cut[0] + 10, cut[1] + 10))
    return img

def pjskset(newalias, oldalias, qqnum=None, username='', qun='群与用户名未知，可能来自旧版分布式'):
    if newalias[:1] == ' ':
        newalias = newalias[1:]
    if newalias[-1:] == ' ':
        newalias = newalias[:-1]
    resp = aliastomusicid(oldalias)
    if resp['musicid'] == 0:
        return "找不到你要设置的歌曲，请使用正确格式：pjskinfo新昵称to旧昵称"
    musicid = resp['musicid']
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f"SELECT * from pjskalias where alias=? COLLATE NOCASE", (newalias,))
    alreadyin = False
    for raw in cursor:
        alreadyin = True
    if alreadyin:
        c.execute(f"UPDATE pjskalias SET musicid=? WHERE alias = ? COLLATE NOCASE", (musicid, newalias))
    else:
        sql_add = 'insert into pjskalias(ALIAS,MUSICID) values(?, ?)'
        c.execute(sql_add, (newalias, musicid))
    conn.commit()
    conn.close()
    with open('masterdata/musics.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    title = ''
    for music in data:
        if music['id'] != musicid:
            continue
        title = music['title']
    timeArray = time.localtime(time.time())
    Time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    writelog(f'[{Time}] {qun} {username}({qqnum}): {newalias}->{title}')
    return f"设置成功！{newalias}->{title}\n已记录bot文档中公开的实时日志，设置不合适的昵称将会被拉黑"


def pjskdel(alias, qqnum=None, username='', qun='群与用户名未知，可能来自分布式'):
    if alias[:1] == ' ':
        alias = alias[1:]
    if alias[-1:] == ' ':
        alias = alias[:-1]
    resp = aliastomusicid(alias)
    if resp['match'] != 1:
        return "找不到你要设置的歌曲，请使用正确格式：pjskdel昵称"
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    c.execute(f"DELETE from pjskalias where alias=? COLLATE NOCASE", (alias,))
    conn.commit()
    conn.close()
    timeArray = time.localtime(time.time())
    Time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    if str(qqnum) == '1103479519':
        writelog(f'[{Time}] 管理员删除了{resp["name"]}的昵称：{alias}')
        return "删除成功！"
    writelog(f'[{Time}] {qun} {username}({qqnum}): 删除了{resp["name"]}的昵称：{alias}')
    return "删除成功！\n已记录bot文档中公开的实时日志，乱删将被拉黑"


def pjskalias(alias, musicid=None):
    if musicid is None:
        resp = aliastomusicid(alias)
        if resp['musicid'] == 0:
            return "找不到你说的歌曲哦"
        musicid = resp['musicid']
        if resp['translate'] == '':
            returnstr = f"{resp['name']}\n匹配度:{round(resp['match'], 4)}\n"
        else:
            returnstr = f"{resp['name']} ({resp['translate']})\n匹配度:{round(resp['match'], 4)}\n"
    else:
        returnstr = ''
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from pjskalias where musicid=? COLLATE NOCASE', (musicid,))
    for raw in cursor:
        returnstr = returnstr + raw[0] + "，"
    conn.close()
    return returnstr[:-1]

def pjskalias2(alias, musicid=None):
    if musicid is None:
        resp = aliastomusicid(alias)
        if resp['musicid'] == 0:
            return "找不到你说的歌曲哦"
        musicid = resp['musicid']
        if resp['translate'] == '':
            returnstr = f"{resp['name']}\n匹配度:{round(resp['match'], 4)}\n"
        else:
            returnstr = f"{resp['name']} ({resp['translate']})\n匹配度:{round(resp['match'], 4)}\n"
    else:
        returnstr = ''
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from pjskalias where musicid=? COLLATE NOCASE', (musicid,))
    count = 0
    data = []
    for raw in cursor:
        count += 1
        data.append({'id': count, 'alias': raw[0]})
    conn.close()
    return data

def txt2html(txt):
    # 来自https://www.it610.com/article/1502111.htm
    def escape(txt):
        txt = txt.replace('&', '&#38;')
        txt = txt.replace(' ', '&#160;')
        txt = txt.replace('<', '&#60;')
        txt = txt.replace('>', '&#62;')
        txt = txt.replace('"', '&#34;')
        txt = txt.replace('\'', '&#39;')
        return txt
    txt = escape(txt)
    lines = txt.split('\n')
    for i, line in enumerate(lines):
        lines[i] = line + '</br>'
    txt = ''.join(lines)
    return r'<!doctype html><html><head><meta charset="utf-8"><title>日志</title></head><body>' + txt + '</body></html>'

def writelog(text=None):
    today = datetime.datetime.today()
    if text is not None:
        with open(f'logs/{today.year}{str(today.month).zfill(2)}.txt', 'a', encoding='utf-8') as f:
            print(text, file=f)
    logtohtml(f'logs/{today.year}{str(today.month).zfill(2)}.txt')

def logtohtml(dir):
    with open(dir, 'r', encoding='utf-8') as f:
        log = f.read()
    today = datetime.datetime.today()
    with open(f"{loghtml}{today.year}{str(today.month).zfill(2)}.html", 'w', encoding='utf-8') as f:
        f.write(txt2html(log))

def musiclength(musicid, fillerSec=0):
    audiodir = 'data/assets/sekai/assetbundle/resources/ondemand/music/long'
    try:
        with open('masterdata/musicVocals.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for vocal in data:
            if vocal['musicId'] == musicid:
                audio = MP3(fr"{audiodir}\{vocal['assetbundleName']}\{vocal['assetbundleName']}.mp3")
                return audio.info.length - fillerSec
        return 0
    except:
        return 0

if __name__ == '__main__':
    # print(musiclength(49))
    # logtohtml()
    # pjskset('ws32', 'wonders')
    # print(pjskdel('ws32'))
    # resp = aliastomusicid('16bit')

    # resp = aliastomusicid('てらてら')
    # drawpjskinfo(resp['musicid'])
    #print(pjskalias('机关枪'))
    pass
