import io
import json
import os
import re
import time

import requests
from PIL import Image, ImageDraw, ImageFont

from modules.config import proxies
from modules.pjskinfo import aliastomusicid


def hotrank():
    with open(r'masterdata/realtime/musics.json', 'r', encoding='utf-8') as f:
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
    font = ImageFont.truetype(r'fonts/SourceHanSansCN-Medium.otf', 18)
    draw.text((20, 20), '热度排行Top40', '#000000', font, spacing=10)
    font = ImageFont.truetype(r'fonts/FOT-RodinNTLGPro-DB.ttf', 18)
    draw.text((20, 53), text, '#000000', font, spacing=10)
    font = ImageFont.truetype(r'fonts/SourceHanSansCN-Medium.otf', 15)
    updatetime = time.localtime(os.path.getmtime(r"masterdata/realtime/musics.json"))
    draw.text((20, 1100), '数据来源：https://profile.pjsekai.moe/\nUpdated in '
              + time.strftime("%Y-%m-%d %H:%M:%S", updatetime), '#000000', font)
    img.save(f'piccache/hotrank.png')


def idtoname(musicid):
    with open(r'masterdata/realtime/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    for i in musics:
        if i['id'] == musicid:
            return i['title']
    return ''


def isleak(musicid):
    with open(r'masterdata/musics.json', 'r', encoding='utf-8') as f:
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
    with open(r'masterdata/realtime/musicDifficulties.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(r'masterdata/realtime/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    for i in data:
        if i['playLevel'] == level and i['musicDifficulty'] == difficulty:
            target.append(i)
    for i in range(0, len(target)):
        try:
            target[i]['playLevelAdjust']
        except KeyError:
            target[i]['playLevelAdjust'] = 0
            target[i]['fullComboAdjust'] = 0
            target[i]['fullPerfectAdjust'] = 0
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
    font = ImageFont.truetype(r'fonts/SourceHanSansCN-Medium.otf', 22)
    draw.text((20, 15), title, '#000000', font, spacing=10)
    font = ImageFont.truetype(r'fonts/FOT-RodinNTLGPro-DB.ttf', 22)
    draw.text((20, 55), text, '#000000', font, spacing=10)
    font = ImageFont.truetype(r'fonts/SourceHanSansCN-Medium.otf', 15)
    updatetime = time.localtime(os.path.getmtime(r"masterdata/realtime/musicDifficulties.json"))
    draw.text((20, int(45 + text.count('\n') * 31.5)), '数据来源：https://profile.pjsekai.moe/\nUpdated in '
              + time.strftime("%Y-%m-%d %H:%M:%S", updatetime), '#000000', font)
    img.save(f'piccache/{level}{difficulty}{fcap}.png')
    return True


# from https://gitlab.com/pjsekai/musics/-/blob/main/music_bpm.py
def parse_bpm(music_id):
    try:
        with open(r'data/assets/sekai/assetbundle/resources'
                  r'/startapp/music/music_score/%04d_01/expert' % music_id, encoding='utf-8') as f:
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


def getchart(musicid, difficulty):
    try:
        if difficulty == 'master' or difficulty == 'expert':
            if os.path.exists(f'charts/SekaiViewer/{musicid}/{difficulty}.png'):  # 本地有缓存
                return f'charts/SekaiViewer/{musicid}/{difficulty}.png'
            else:  # 本地无缓存
                if downloadviewerchart(musicid, difficulty):  # sekai viewer下载成功
                    return f'charts/SekaiViewer/{musicid}/{difficulty}.png'
                else:  # sekai viewer下载失败 尝试sdvx.in
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
                            bgpic.save(f'charts/sdvxInCharts/{musicid}/{difficulty}.png')
                            return f'charts/sdvxInCharts/{musicid}/{difficulty}.png'
                        else:  # 没下载到
                            if os.path.exists(f'charts/sus/{musicid}/{difficulty}.png'):  # 本地有缓存
                                return f'charts/sus/{musicid}/{difficulty}.png'
                            else:
                                return None
        else:  # 其他难度
            if os.path.exists(f'charts/SekaiViewer/{musicid}/{difficulty}.png'):  # 本地有缓存
                return f'charts/SekaiViewer/{musicid}/{difficulty}.png'
            else:  # 本地无缓存
                if downloadviewerchart(musicid, difficulty):  # sekai viewer下载成功
                    return f'charts/SekaiViewer/{musicid}/{difficulty}.png'
                else:  # sekai viewer下载失败
                    return None
    except:
        return None


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
                    bgpic.save(f'charts/sdvxInCharts/{musicid}/{difficulty}.png')
                    return f'charts/sdvxInCharts/{musicid}/{difficulty}.png'
                else:  # 没下载到
                    return None
        else:  # 其他难度
            return None
    except:
        return None


def idtotime(musicid):
    with open(r'masterdata/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    musics.sort(key=lambda x: x["publishedAt"])
    for i in range(0, len(musics)):
        if musics[i]['id'] == musicid:
            return i + 1
    return 0


def downloadviewerchart(musicid, difficulty):
    try:
        try:
            re = requests.get(f'https://minio.dnaroma.eu/sekai-music-charts/{str(musicid).zfill(4)}/{difficulty}.png',
                              proxies=proxies)
        except:
            re = requests.get(f'https://minio.dnaroma.eu/sekai-music-charts/{str(musicid).zfill(4)}/{difficulty}.png',
                              proxies=None)
        if re.status_code == 200:
            dirs = rf'charts/SekaiViewer/{musicid}'
            if not os.path.exists(dirs):
                os.makedirs(dirs)
            if difficulty == 'master':
                svg = requests.get(f'https://minio.dnaroma.eu/sekai-music-charts/{str(musicid).zfill(4)}/{difficulty}.svg',
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


def aliastochart(full, sdvx=False):
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
    if resp['musicid'] == 0:
        return None  # 找不到歌曲 return None
    else:
        text = resp['name'] + ' ' + diff.upper() + '\n' + '匹配度: ' + str(round(resp['match'], 4))
        if sdvx:
            dir = getsdvxchart(resp['musicid'], diff)
        else:
            dir = getchart(resp['musicid'], diff)
        if dir is not None:
            bpm = parse_bpm(resp['musicid'])
            bpmtext = ''
            for bpms in bpm[1]:
                bpmtext = bpmtext + ' - ' + str(bpms['bpm']).replace('.0', '')
            if 'SekaiViewer' in dir:
                text = text + '\nBPM: ' + bpmtext[3:] + '\n谱面图片来自Sekai Viewer'
            elif 'sdvxInCharts' in dir:
                text = text + '\nBPM: ' + bpmtext[3:] + '\n谱面图片来自プロセカ譜面保管所'
            else:
                text = text + '\nBPM: ' + bpmtext[3:] + '\n目前两个PJSK谱面预览来源均未更新，' \
                                                        '暂时使用来自CHUNITHM谱面转换器生成的图片（长条没有斜率显示，边缘多出一条轨道）'
            return text, dir  # 有图 return俩
        else:
            return text  # 无图 return歌曲信息


def notecount(count):
    text = ''
    with open(r'masterdata/musicDifficulties.json', 'r', encoding='utf-8') as f:
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
    with open(r'masterdata/realtime/musics.json', 'r', encoding='utf-8') as f:
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

if __name__ == '__main__':
    # downloadviewerchart(49, 'master')
    print(tasseiritsu([1224, 0, 1, 0, 0]))
    # print(getchart(248, 'master'))
