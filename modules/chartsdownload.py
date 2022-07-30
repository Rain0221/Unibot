import json

from modules.musics import getchart

with open(r'masterdata/musics.json', 'r', encoding='utf-8') as f:
    musics = json.load(f)
i = 0
for music in musics:
    i = i + 1
    print(f"{i}/{len(musics)} {getchart(music['id'], 'master')}")
