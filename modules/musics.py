import datetime
import io
import json
import os
import re
import sqlite3
import time
import traceback

import requests
from PIL import Image, ImageDraw, ImageFont
from dateutil.tz import tzlocal

from modules.config import proxies
from modules.pjskinfo import aliastomusicid
from moesus.music_score import parse


def hotrank():
    with open('masterdata/realtime/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    for i in range(0, len(musics)):
        try:
            musics[i]['hot']
        except KeyError:
            musics[i]['hot'] = 0
    musics.sort(key=lambda x: x["hot"], reverse=True)
    text = ''
    for i in range(0, 40):
        text = text + f"{i + 1} {musics[i]['title']} ({int(musics[i]['hot'])})\n"

    IMG_SIZE = (500, 40 + 33 * 34)
    img = Image.new('RGB', IMG_SIZE, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('fonts/SourceHanSansCN-Medium.otf', 18)
    draw.text((20, 20), '热度排行Top40', '#000000', font, spacing=10)
    font = ImageFont.truetype('fonts/FOT-RodinNTLGPro-DB.ttf', 18)
    draw.text((20, 53), text, '#000000', font, spacing=10)
    font = ImageFont.truetype('fonts/SourceHanSansCN-Medium.otf', 15)
    updatetime = time.localtime(os.path.getmtime(r"masterdata/realtime/musics.json"))
    draw.text((20, 1100), '数据来源：https://profile.pjsekai.moe/\nUpdated in '
              + time.strftime("%Y-%m-%d %H:%M:%S", updatetime), '#000000', font)
    img.save(f'piccache/hotrank.png')


def idtoname(musicid):
    with open('masterdata/realtime/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    for i in musics:
        if i['id'] == musicid:
            return i['title']
    return ''


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


def levelrank(level, difficulty, fcap=0):
    target = []
    with open('masterdata/realtime/musicDifficulties.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open('masterdata/realtime/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    for i in data:
        if i['playLevel'] == level and i['musicDifficulty'] == difficulty:
            try:
                i['playLevelAdjust']
                target.append(i)
            except KeyError:
                pass
    if fcap == 0:
        title = f'{difficulty.upper()} {level}难度排行（仅供参考）'
        target.sort(key=lambda x: x["playLevelAdjust"], reverse=True)
    elif fcap == 1:
        title = f'{difficulty.upper()} {level}FC难度排行（仅供参考）'
        target.sort(key=lambda x: x["fullComboAdjust"], reverse=True)
    else:
        title = f'{difficulty.upper()} {level}AP难度排行（仅供参考）'
        target.sort(key=lambda x: x["fullPerfectAdjust"], reverse=True)
    text = ''
    musictitle = ''
    for i in target:
        for j in musics:
            if j['id'] == i['musicId']:
                musictitle = j['title']
                break
        if fcap == 0:
            text = text + f"{musictitle} ({round(i['playLevel'] + i['playLevelAdjust'], 1)})\n"
        elif fcap == 1:
            text = text + f"{musictitle} ({round(i['playLevel'] + i['fullComboAdjust'], 1)})\n"
        else:
            text = text + f"{musictitle} ({round(i['playLevel'] + i['fullPerfectAdjust'], 1)})\n"
    if text == '':
        return False
    IMG_SIZE = (500, int(100 + text.count('\n') * 31.5))
    img = Image.new('RGB', IMG_SIZE, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('fonts/SourceHanSansCN-Medium.otf', 22)
    draw.text((20, 15), title, '#000000', font, spacing=10)
    font = ImageFont.truetype('fonts/FOT-RodinNTLGPro-DB.ttf', 22)
    draw.text((20, 55), text, '#000000', font, spacing=10)
    font = ImageFont.truetype('fonts/SourceHanSansCN-Medium.otf', 15)
    updatetime = time.localtime(os.path.getmtime(r"masterdata/realtime/musicDifficulties.json"))
    draw.text((20, int(45 + text.count('\n') * 31.5)), '数据来源：https://profile.pjsekai.moe/\nUpdated in '
              + time.strftime("%Y-%m-%d %H:%M:%S", updatetime), '#000000', font)
    img.save(f'piccache/{level}{difficulty}{fcap}.png')
    return True


# from https://gitlab.com/pjsekai/musics/-/blob/main/music_bpm.py
def parse_bpm(music_id):
    try:
        with open('data/assets/sekai/assetbundle/resources'
                  '/startapp/music/music_score/%04d_01/expert' % music_id, encoding='utf-8') as f:
            r = f.read()
    except FileNotFoundError:
        return 0, [{'time': 0.0, 'bpm': '无数据'}], 0

    score = {}
    max_time = 0
    for line in r.split('\n'):
        match: re.Match = re.match(r'#(...)(...?)\s*\:\s*(\S*)', line)
        if match:
            time, key, value = match.groups()
            score[(time, key)] = value
            if time.isdigit():
                max_time = max(max_time, int(time) + 1)

    bpm_palette = {}
    for time, key in score:
        if time == 'BPM':
            bpm_palette[key] = float(score[(time, key)])

    bpm_events = {}
    for time, key in score:
        if time.isdigit() and key == '08':
            value = score[(time, key)]
            length = len(value) // 2

            for i in range(length):
                bpm_key = value[i * 2:(i + 1) * 2]
                if bpm_key == '00':
                    continue
                bpm = bpm_palette[bpm_key]
                t = int(time) + i / length
                bpm_events[t] = bpm

    bpm_sequence = [{
        'time': time,
        'bpm': bpm,
    } for time, bpm in sorted(bpm_events.items())]

    for i in range(len(bpm_sequence)):
        if i > 0 and bpm_sequence[i]['bpm'] == bpm_sequence[i - 1]['bpm']:
            bpm_sequence[i]['deleted'] = True

    bpm_sequence = [bpm_event for bpm_event in bpm_sequence if bpm_event.get('deleted') != True]

    bpms = {}
    for i in range(len(bpm_sequence)):
        bpm = bpm_sequence[i]['bpm']
        if bpm not in bpms:
            bpms[bpm] = 0.0

        if i + 1 < len(bpm_sequence):
            bpms[bpm] += (bpm_sequence[i + 1]['time'] - bpm_sequence[i]['time']) / bpm
        else:
            bpms[bpm] += (max_time - bpm_sequence[i]['time']) / bpm

    sorted_bpms = sorted([(bpms[bpm], bpm) for bpm in bpms], reverse=True)
    mean_bpm = sorted_bpms[0][1]

    return mean_bpm, bpm_sequence, max_time


def getchart(musicid, difficulty, theme='white'):
    path = f'charts/moe/{theme}/{musicid}/{difficulty}.png'
    if os.path.exists(path):  # 本地有缓存
        return path
    else:  # 本地无缓存
        parse(musicid, difficulty, theme)  # 生成moe
        return path

def getcharttheme(qqnum):
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from chartprefer where qqnum=?', (qqnum,))
    for row in cursor:
        conn.close()
        return row[1]
    return 'white'

def gensvg():
    with open('masterdata/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    for music in musics:
        for diff in ['master', 'expert', 'hard', 'normal', 'easy']:
            if not os.path.exists(f'charts/moe/svg/{music["id"]}/{diff}.svg'):
                print('生成谱面', music['id'], diff)
                parse(music['id'], diff, 'svg', False, 'https://assets.unipjsk.com/startapp/music/jacket/%s/%s.png')


def setcharttheme(qqnum, theme):
    if theme != 'white' and theme != 'black' and theme != 'color':
        return '白色主题：/theme white\n黑色主题：/theme black\n彩色主题：/theme color'
    conn = sqlite3.connect('pjsk.db')
    c = conn.cursor()
    try:
        c.execute(f'insert into chartprefer (qqnum, prefer) values(?, ?)', (str(qqnum), theme))
    except sqlite3.IntegrityError:
        c.execute(f'update chartprefer set prefer=? where qqnum=?', (theme, str(qqnum)))
    conn.commit()
    conn.close()
    return f'{theme}主题设置成功'

def getsdvxchart(musicid, difficulty):
    try:
        if difficulty == 'master' or difficulty == 'expert':
            if os.path.exists(f'charts/sdvxInCharts/{musicid}/{difficulty}.png'):  # sdvx.in本地有缓存
                return f'charts/sdvxInCharts/{musicid}/{difficulty}.png'
            else:  # 无缓存，尝试下载
                timeid = idtotime(musicid)
                if difficulty == 'master':
                    data = requests.get(f'https://sdvx.in/prsk/obj/data{str(timeid).zfill(3)}mst.png',
                                        proxies=proxies)
                else:
                    data = requests.get(f'https://sdvx.in/prsk/obj/data{str(timeid).zfill(3)}exp.png',
                                        proxies=proxies)
                if data.status_code == 200:  # 下载到了
                    bg = requests.get(f"https://sdvx.in/prsk/bg/{str(timeid).zfill(3)}bg.png",
                                      proxies=proxies)
                    bar = requests.get(f"https://sdvx.in/prsk/bg/{str(timeid).zfill(3)}bar.png",
                                       proxies=proxies)
                    bgpic = Image.open(io.BytesIO(bg.content))
                    datapic = Image.open(io.BytesIO(data.content))
                    barpic = Image.open(io.BytesIO(bar.content))
                    r, g, b, mask = datapic.split()
                    bgpic.paste(datapic, (0, 0), mask)
                    r, g, b, mask = barpic.split()
                    bgpic.paste(barpic, (0, 0), mask)
                    dirs = f'charts/sdvxInCharts/{musicid}'
                    if not os.path.exists(dirs):
                        os.makedirs(dirs)
                    r, g, b, mask = bgpic.split()
                    final = Image.new('RGB', bgpic.size, (0, 0, 0))
                    final.paste(bgpic, (0, 0), mask)
                    final.save(f'charts/sdvxInCharts/{musicid}/{difficulty}.png')
                    return f'charts/sdvxInCharts/{musicid}/{difficulty}.png'
                else:  # 没下载到
                    return None
        else:  # 其他难度
            return None
    except:
        return None


def idtotime(musicid):
    with open('masterdata/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    musics.sort(key=lambda x: x["publishedAt"])
    for i in range(0, len(musics)):
        if musics[i]['id'] == musicid:
            return i + 1
    return 0


def downloadviewerchart(musicid, difficulty):
    try:
        try:
            re = requests.get(f'https://storage.sekai.best/sekai-music-charts/{str(musicid).zfill(4)}/{difficulty}.png',
                              proxies=proxies)
        except:
            re = requests.get(f'https://storage.sekai.best/sekai-music-charts/{str(musicid).zfill(4)}/{difficulty}.png',
                              proxies=None)
        if re.status_code == 200:
            dirs = rf'charts/SekaiViewer/{musicid}'
            if not os.path.exists(dirs):
                os.makedirs(dirs)
            if difficulty == 'master':
                svg = requests.get(f'https://storage.sekai.best/sekai-music-charts/{str(musicid).zfill(4)}/{difficulty}.svg',
                                   proxies=proxies)
                i = 0
                while True:
                    i = i + 1
                    if svg.text.count(f'{str(i).zfill(3)}</text>') == 0:
                        break
                row = int((i - 2) / 4)
                print(row)
                pic = Image.open(io.BytesIO(re.content))
                r, g, b, mask = pic.split()
                final = Image.new('RGB', pic.size, (255, 255, 255))
                final.paste(pic, (0, 0), mask)
                final = final.resize((160 * row + 32, 1300))
                final.save(f'charts/SekaiViewer/{musicid}/{difficulty}.png')
            else:
                pic = Image.open(io.BytesIO(re.content))
                r, g, b, mask = pic.split()
                final = Image.new('RGB', pic.size, (255, 255, 255))
                final.paste(pic, (0, 0), mask)
                final.save(f'charts/SekaiViewer/{musicid}/{difficulty}.png')
            return True
        else:
            return False
    except:
        return False


def aliastochart(full, sdvx=False, qun=False, theme='white'):
    if full[-2:] == 'ex':
        alias = full[:-2]
        diff = 'expert'
    elif full[-2:] == 'hd':
        alias = full[:-2]
        diff = 'hard'
    elif full[-2:] == 'nm':
        alias = full[:-2]
        diff = 'normal'
    elif full[-2:] == 'ez':
        alias = full[:-2]
        diff = 'easy'
    elif full[-2:] == 'ma':
        alias = full[:-2]
        diff = 'master'
    elif full[-6:] == 'expert':
        alias = full[:-6]
        diff = 'expert'
    elif full[-4:] == 'hard':
        alias = full[:-4]
        diff = 'hard'
    elif full[-6:] == 'normal':
        alias = full[:-6]
        diff = 'normal'
    elif full[-4:] == 'easy':
        alias = full[:-4]
        diff = 'easy'
    elif full[-6:] == 'master':
        alias = full[:-6]
        diff = 'master'
    else:
        alias = full
        diff = 'master'
    resp = aliastomusicid(alias)
    if qun and resp['match'] < 0.6:
        return ''
    if resp['musicid'] == 0:
        return None  # 找不到歌曲 return None
    else:
        text = resp['name'] + ' ' + diff.upper() + '\n' + '匹配度: ' + str(round(resp['match'], 4))
        if sdvx:
            dir = getsdvxchart(resp['musicid'], diff)
        else:
            dir = getchart(resp['musicid'], diff, theme)
        if dir is not None:
            bpm = parse_bpm(resp['musicid'])
            bpmtext = ''
            for bpms in bpm[1]:
                bpmtext = bpmtext + ' - ' + str(bpms['bpm']).replace('.0', '')
            if 'SekaiViewer' in dir:
                text = text + '\nBPM: ' + bpmtext[3:] + '\n谱面图片来自Sekai Viewer'
            elif 'sdvxInCharts' in dir:
                text = text + '\nBPM: ' + bpmtext[3:] + '\n谱面图片来自プロセカ譜面保管所'
            elif 'moe' in dir:
                text = text + '\nBPM: ' + bpmtext[3:] + '\n谱面图片来自ぷろせかもえ！ (开发中)'
            else:
                text = text + '\nBPM: ' + bpmtext[3:] + '\n该自动生成的谱面预览没有长条斜率，部分中继点位置显示不正确，仅供参考。其他谱面预览源暂未更新'
            return text, dir  # 有图 return俩
        else:
            return text  # 无图 return歌曲信息


def notecount(count):
    text = ''
    with open('masterdata/musicDifficulties.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in data:
        if i['noteCount'] == count:
            text += f"{idtoname(i['musicId'])}[{(i['musicDifficulty'].upper())} {i['playLevel']}]\n"
    if text == '':
        return '没有找到'
    else:
        return text


def tasseiritsu(para):
    intpara = [int(x) for x in para]
    ritsu = (3 * intpara[0] + 2 * intpara[1] + intpara[2]) / (3 * sum(intpara))
    if ritsu < 0.94:
        grade = 'D'
    elif ritsu < 0.97:
        grade = 'C'
    elif ritsu < 0.98:
        grade = 'B'
    elif ritsu < 0.985:
        grade = 'A'
    elif ritsu < 0.99:
        grade = 'S'
    elif ritsu < 0.9925:
        grade = 'S+'
    elif ritsu < 0.995:
        grade = 'SS'
    elif ritsu < 0.9975:
        grade = 'SS+'
    elif ritsu < 0.999:
        grade = 'SSS'
    elif ritsu < 1:
        grade = 'SSS+'
    else:
        grade = 'MAX'
    return f'达成率{grade}\n{round(ritsu * 100, 4)}%/100%'


def findbpm(targetbpm):
    bpm = {}
    text = ''
    with open('masterdata/realtime/musics.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for music in data:
        bpm[music['id']] = parse_bpm(music['id'])[1]
    for musicid in bpm:
        for i in bpm[musicid]:
            if int(i['bpm']) == targetbpm:
                bpmtext = ''
                for bpms in bpm[musicid]:
                    bpmtext += ' - ' + str(bpms['bpm']).replace('.0', '')
                text += f"{idtoname(musicid)}: {bpmtext[3:]}\n"
                break
    if text == '':
        return '没有找到'
    return text


def updaterebase():
    print('\nupdate rebase')
    offset = 0
    timeformat = "%Y-%m-%dT%H:%M:%S.%f%z"
    deletelist = []
    failcount = 0
    while True:
        try:
            resp = requests.get(f'https://gitlab.com/pjsekai/musics/-/refs/main/logs_tree/rebases?format=json&offset={offset}', proxies=proxies)
            offset += 25
            data = resp.json()
            if not data:
                break
            for file in data:
                musicid = int(file['file_name'][:file['file_name'].find('.')])
                if os.path.exists('moesus/rebases/' + file['file_name']):
                    commit_time = datetime.datetime.strptime(file['commit']['committed_date'], timeformat)
                    filetime = datetime.datetime.fromtimestamp(os.path.getmtime('moesus/rebases/' + file['file_name'])).replace(tzinfo=tzlocal())
                    if commit_time > filetime:
                        download_rebase(file['file_name'])
                        if musicid not in deletelist:
                            deletelist.append(musicid)
                else:
                    download_rebase(file['file_name'])
                    if musicid not in deletelist:
                        deletelist.append(musicid)
            failcount = 0
        except:
            failcount += 1
            traceback.print_exc()
            print('下载失败')
            if failcount > 4:
                break
    updatecharts(deletelist)


def download_rebase(file_name):
    print('更新' + file_name)
    for i in range(0, 4):
        try:
            resp = requests.get(f'https://gitlab.com/pjsekai/musics/-/raw/main/rebases/{file_name}?inline=false', proxies=proxies)
            with open('moesus/rebases/' + file_name, 'wb') as f:
                f.write(resp.content)
            return
        except:
            traceback.print_exc()

def updatecharts(deletelist):
    for musicid in deletelist:
        for theme in ['black', 'white', 'color', 'svg']:
            for diff in ['easy', 'normal', 'hard', 'expert', 'master']:
                for fileformat in ['png', 'svg']:
                    path = f'charts/moe/{theme}/{musicid}/{diff}.{fileformat}'
                    if os.path.exists(path):
                        os.remove(path)
                        if theme != 'svg' and diff == 'master' and fileformat == 'svg':
                            print('更新' + path)
                            parse(musicid, diff, theme)
    gensvg()


if __name__ == '__main__':
    path = '../charts/sdvxInCharts'
    target = []
    files = os.listdir(path)
    files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
    count = 0
    for i in files_dir:
        count += 1
        chartfiles = os.listdir(path + "/" + i)
        files_file = [f for f in chartfiles if os.path.isfile(os.path.join(path + "/" + i, f))]
        print(f'{count}/{len(files_dir)}', i, files_file)
        for j in files_file:
            pic = Image.open(f'{path}/{i}/{j}')
            r, g, b, mask = pic.split()
            final = Image.new('RGB', pic.size, (0, 0, 0))
            final.paste(pic, (0, 0), mask)
            final.save(f'{path}/{i}/{j}')




