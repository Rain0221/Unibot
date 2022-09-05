import re
import json
import traceback
import tqdm
import requests

import utils


def parse_bpm(music_id):
    url = 'https://asset3.pjsekai.moe/music/music_score/%04d_01/master' % music_id
    r = requests.get(url)
    if r.status_code != 200:
        return

    score = {}
    bar_count = 0
    for line in r.text.split('\n'):
        match: re.Match = re.match(r'#(...)(...?)\s*\:\s*(\S*)', line)
        if match:
            bar, key, value = match.groups()
            score[(bar, key)] = value
            if bar.isdigit():
                bar_count = max(bar_count, int(bar) + 1)

    bpm_palette = {}
    for bar, key in score:
        if bar == 'BPM':
            bpm_palette[key] = float(score[(bar, key)])

    bpm_events = {}
    for bar, key in score:
        if bar.isdigit() and key == '08':
            value = score[(bar, key)]
            length = len(value) // 2

            for i in range(length):
                bpm_key = value[i*2:(i+1)*2]
                if bpm_key == '00':
                    continue
                bpm = bpm_palette[bpm_key]
                t = int(bar) + i / length
                bpm_events[t] = bpm

    bpm_events = [{
        'bar': bar,
        'bpm': bpm,
    } for bar, bpm in sorted(bpm_events.items())]

    for i in range(len(bpm_events)):
        if i > 0 and bpm_events[i]['bpm'] == bpm_events[i-1]['bpm']:
            bpm_events[i]['deleted'] = True

    bpm_events = [bpm_event for bpm_event in bpm_events if bpm_event.get('deleted') != True]

    bpms = {}
    for i in range(len(bpm_events)):
        bpm = bpm_events[i]['bpm']
        if bpm not in bpms:
            bpms[bpm] = 0.0

        if i+1 < len(bpm_events):
            bpm_events[i]['duration'] = (bpm_events[i+1]['bar'] - bpm_events[i]['bar']) / bpm * 4 * 60
        else:
            bpm_events[i]['duration'] = (bar_count - bpm_events[i]['bar']) / bpm * 4 * 60

        bpms[bpm] += bpm_events[i]['duration']

    sorted_bpms = sorted([(bpms[bpm], bpm) for bpm in bpms], reverse=True)
    bpm_main = sorted_bpms[0][1]
    duration = sum([bpm[0] for bpm in sorted_bpms])

    return bpm_main, bpm_events, bar_count, duration


def handle():
    for music in tqdm.tqdm(utils.get_database('pjsekai')['musics'].find({})):
        if not utils.get_database('pjsekai_musics')['musicBPMs'].find_one({'musicId':  music['id']}):
            try:
                bpm, bpms, bar_count, duration = parse_bpm(music['id'])
            except:
                traceback.print_exc()
                continue

            utils.get_database('pjsekai_musics')['musicBPMs'].update_one({
                'musicId': music['id'],
            }, {
                '$set': {
                    'musicId': music['id'],
                    'bpm': bpm,
                    **({'bpms': bpms} if len(bpms) > 1 else {}),
                    'barCount': bar_count,
                    'duration': duration,
                },
                '$unset': {
                    **({'bpms': 1} if len(bpms) == 1 else {}),
                }
            }, upsert=True)


if __name__ == '__main__':
    handle()
