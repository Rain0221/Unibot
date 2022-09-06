import json
import os
import time
import cairosvg


from moesus import chart

note_sizes = {
    'easy': 2.0,
    'normal': 1.5,
    'hard': 1.25,
    'expert': 1.0,
    'master': 0.875,
}


def parse(music_id, difficulty, theme):
    with open(rf'data\assets\sekai\assetbundle\resources\startapp\music\music_score\{str(music_id).zfill(4)}_01\{difficulty}', 'r', encoding='utf-8') as f:
        sustext = f.read()
    lines = sustext.splitlines()

    with open (r'masterdata\musics.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in data:
        if i['id'] == music_id:
            music = i
    if music['composer'] == music['arranger']:
        artist = music['composer']
    elif music['composer'] in music['arranger']:
        artist = music['arranger']
    elif music['arranger'] in music['composer']:
        artist = music['composer']
    else:
        artist = '%s / %s' % (music['composer'], music['arranger'])

    with open (r'masterdata\musicDifficulties.json', 'r', encoding='utf-8') as f:
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
            'jacket': '../../../../data/assets/sekai/assetbundle/resources/startapp/music/jacket/%s/%s.png' % (music['assetbundleName'], music['assetbundleName'])
        }),
    )

    try:
        with open('moesus/rebases.json') as f:
            rebases: list = json.load(f)
        for rebase in rebases:
            if rebase['musicId'] == music_id:
                break
        else:
            raise NotImplementedError
    except:
        rebase = None
        # utils.get_database('pjsekai_musics')['musicRebases'].find_one({
        #     'musicId': music_id,
        # })

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

    with open(f'moesus/chart/{theme}/css/sus.css', encoding='utf-8') as f:
        style_sheet = f.read()

    if theme == 'color':
        with open(f'moesus/chart/{theme}/css/{difficulty}.css') as f:
            style_sheet += '\n' + f.read()
    else:
        with open(f'moesus/chart/{theme}/css/master.css') as f:
            style_sheet += '\n' + f.read()

    sus.export(file_name + '.svg', style_sheet=style_sheet)

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
