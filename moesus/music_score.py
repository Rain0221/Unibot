import json
import os
import re
import time
import traceback

import cairosvg
import argparse

from moesus import chart

note_sizes = {
    'easy': 2.0,
    'normal': 1.5,
    'hard': 1.25,
    'expert': 1.0,
    'master': 0.875,
}


def parse(music_id, difficulty, theme, savepng=True, jacketdir=None, title=None, artist=None):
    with open(f'data/assets/sekai/assetbundle/resources/startapp/music/music_score/{str(music_id).zfill(4)}_01/{difficulty}', 'r', encoding='utf-8') as f:
        sustext = f.read()
    lines = sustext.splitlines()

    if jacketdir is None:
        jacketdir = '../../../../data/assets/sekai/assetbundle/resources/startapp/music/jacket/%s/%s.png'

    with open ('masterdata/musics.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in data:
        if i['id'] == music_id:
            music = i
            break
    try:
        if music['composer'] == music['arranger']:
            artist = music['composer']
        elif music['composer'] in music['arranger'] or music['composer'] == '-':
            artist = music['arranger']
        elif music['arranger'] in music['composer'] or music['arranger'] == '-':
            artist = music['composer']
        else:
            artist = '%s / %s' % (music['composer'], music['arranger'])
    except:
        music = {'title': title, 'assetbundleName': 'jacket_s_%03d' % music_id}

    playlevel = '?'
    with open ('masterdata/musicDifficulties.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in data:
        if i['musicId'] == music_id and i['musicDifficulty'] == difficulty:
            playlevel = i["playLevel"]

    sus = chart.SUS(
        lines,
        note_size=note_sizes[difficulty],
        note_host='../../notes',
        **({
            'title': music['title'],
            'artist': artist,
            'difficulty': difficulty,
            'playlevel': playlevel,
            'jacket': jacketdir % (music['assetbundleName'], music['assetbundleName'])
        }),
    )

    try:
        with open('moesus/rebases/%s.json' % music_id, encoding='utf-8') as f:
            rebase = json.load(f)
    except:
        rebase = None

    try:
        with open('moesus/rebases/%s.lyric' % music_id, encoding='utf-8') as f:
            sus.words = chart.load_lyric(f.readlines())
    except:
        pass

    if rebase:
        sus.score = sus.score.rebase([
            chart.Event(
                bar=event.get('bar'),
                bpm=event.get('bpm'),
                bar_length=event.get('barLength'),
                sentence_length=event.get('sentenceLength'),
                section=event.get('section'),
            )
            for event in rebase.get('events', [])
        ], offset=rebase.get('offset', 0))

    file_name = 'charts/moe/%s/%d/%s' % (theme, music_id, difficulty)
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    themehint = True
    if theme == 'svg' or theme == 'pjskguess':
        with open(f'moesus/chart/white/css/sus.css', encoding='utf-8') as f:
            style_sheet = f.read()
        with open(f'moesus/chart/white/css/master.css') as f:
            style_sheet += '\n' + f.read()
        themehint = False
    elif theme == 'color':
        with open(f'moesus/chart/{theme}/css/sus.css', encoding='utf-8') as f:
            style_sheet = f.read()
        with open(f'moesus/chart/{theme}/css/{difficulty}.css') as f:
            style_sheet += '\n' + f.read()
    else:
        with open(f'moesus/chart/{theme}/css/sus.css', encoding='utf-8') as f:
            style_sheet = f.read()
        with open(f'moesus/chart/{theme}/css/master.css') as f:
            style_sheet += '\n' + f.read()

    sus.export(file_name + '.svg', style_sheet=style_sheet, themehint=themehint)
    if savepng:
        cairosvg.svg2png(url=file_name + '.svg', write_to=file_name + '.png', scale=1.3)

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

def genGuessChart(music_id):
    difficulty = 'master'
    with open(f'data/assets/sekai/assetbundle/resources/startapp/music/music_score/{str(music_id).zfill(4)}_01/{difficulty}', 'r', encoding='utf-8') as f:
        sustext = f.read()
    lines = sustext.splitlines()
    mainbpm = parse_bpm(music_id)[0]
    for i in range(0, len(lines)):
        if lines[i].startswith('#BPM'):
            lines[i] = lines[i][:8] + str(mainbpm)

    jacketdir = '../../../../data/assets/sekai/assetbundle/resources/startapp/music/jacket/%s/%s.png'

    with open ('masterdata/musics.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in data:
        if i['id'] == music_id:
            music = i
            break
    try:
        if music['composer'] == music['arranger']:
            artist = music['composer']
        elif music['composer'] in music['arranger'] or music['composer'] == '-':
            artist = music['arranger']
        elif music['arranger'] in music['composer'] or music['arranger'] == '-':
            artist = music['composer']
        else:
            artist = '%s / %s' % (music['composer'], music['arranger'])
    except:
        music = {'title': title, 'assetbundleName': 'jacket_s_%03d' % music_id}

    playlevel = '?'
    with open ('masterdata/musicDifficulties.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in data:
        if i['musicId'] == music_id and i['musicDifficulty'] == difficulty:
            playlevel = i["playLevel"]

    sus = chart.SUS(
        lines,
        note_size=note_sizes[difficulty],
        note_host='../../notes',
        **({
            'title': music['title'],
            'artist': artist,
            'difficulty': difficulty,
            'playlevel': playlevel,
            'jacket': jacketdir % (music['assetbundleName'], music['assetbundleName'])
        }),
    )

    rebase = None

    file_name = 'charts/moe/%s/%d/%s' % ('guess', music_id, difficulty)
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    with open(f'moesus/chart/white/css/sus.css', encoding='utf-8') as f:
        style_sheet = f.read()
    with open(f'moesus/chart/white/css/master.css') as f:
        style_sheet += '\n' + f.read()

    sus.export(file_name + '.svg', style_sheet=style_sheet, themehint=False)
    cairosvg.svg2png(url=file_name + '.svg', write_to=file_name + '.png', scale=1.3)


if __name__ == '__main__':
    start = time.time()
    musicid = 131
    parse(musicid, 'master', 'white')
    # parse(musicid, 'expert')
    # parse(musicid, 'hard')
    # parse(musicid, 'normal')
    # parse(musicid, 'easy')
    print(time.time() - start)
