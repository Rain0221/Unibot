import os
import json
import math
import traceback
import numpy

import api
import utils
import regression


event_alpha_0 = (5 ** 0.5 - 1) / 2


def handle():
    profile_summaries = list(utils.get_database('pjsekai_profile')['profileSummaries'].find({}))
    music_bpms = {
        music['musicId']: music
        for music in utils.get_database('pjsekai_musics')['musicBPMs'].find({}, {'_id': False})
    }

    max_event_id = 0
    for profile_summary in profile_summaries:
        max_event_id = max(max_event_id, profile_summary['eventId'])
    max_event_end_time = api.Sekai.get_database('events', key='id')[max_event_id]['aggregateAt']

    musics = {}
    for music in api.Sekai.get_database('musics'):
        musics[music['id']] = {
            **music,
            'count': 0,
            'availableCount': 0,
            'clearCount': 0,
            'mvpCount': 0,
            'superStarCount': 0,
            'genre': [],
            **music_bpms[music['id']],
        }

    for music_tag in api.Sekai.get_database('musicTags'):
        if music_tag['musicTag'] != 'all':
            musics[music_tag['musicId']]['genre'].append(music_tag['musicTag'])

    for music in musics.values():
        if len(music['genre']) == 0:
            music['genre'] = 'other'
        elif len(music['genre']) == 1:
            music['genre'] = music['genre'][0]
        elif len(music['genre']) == 2 and 'vocaloid' in music['genre']:
            music['genre'].remove('vocaloid')
            music['genre'] = music['genre'][0]
        else:
            music['genre'] = 'other'

    music_difficulties = {}
    for music_difficulty in api.Sekai.get_database('musicDifficulties'):
        music_difficulties[(music_difficulty['musicId'], music_difficulty['musicDifficulty'])] = {
            **music_difficulty,
            'count': 0,
            'clearCount': 0,
            'fullComboCount': 0,
            'fullPerfectCount': 0,
        }

    for profile_summary in profile_summaries:
        event_alpha = event_alpha_0 ** (max_event_id - profile_summary['eventId'])
        count = (profile_summary['rankTo'] - profile_summary['rankFrom'])

        for user_music in profile_summary['musics']:
            music = musics[user_music['musicId']]

            music['count'] += event_alpha * count
            music['availableCount'] += event_alpha * user_music['count']
            music['mvpCount'] += event_alpha * user_music['mvpCount']
            music['superStarCount'] += event_alpha * user_music['superStarCount']

        for user_music_difficulty in profile_summary['musicDifficulties']:
            music_difficulty = music_difficulties[user_music_difficulty['musicId'],
                                                  user_music_difficulty['musicDifficulty']]

            music_difficulty['count'] += event_alpha * count
            music_difficulty['clearCount'] += event_alpha * user_music_difficulty['count']
            music_difficulty['fullComboCount'] += event_alpha * user_music_difficulty['fullComboCount']
            music_difficulty['fullPerfectCount'] += event_alpha * user_music_difficulty['fullPerfectCount']

    # music hot

    available_points = []
    multi_live_points = []
    for music in musics.values():
        published_times = regression.HotEstimator.published_times(music['publishedAt'], max_event_end_time)
        music['publishedTime'], music['publishedTimeAdjust'] = published_times
        music['hotIgnore'] = music['publishedTime'] <= 0 or music['publishedTimeAdjust'] <= 0
        if music['hotIgnore']:
            continue

        if music['releaseConditionId'] == 5:
            music['availableRate'] = music['availableCount'] / music['count']
            r = 1 / (1 - music['availableRate']) ** 2
            music['availableHot'] = math.log(r / (music['publishedTime'] / (1000 * 60 * 60 * 24) + 10))
            available_points.append(music['availableHot'])

        r = (music['mvpCount'] + music['superStarCount']) / music['availableCount']
        music['multiLiveHot'] = math.log(r / (music['publishedTimeAdjust'] / (1000 * 60 * 60 * 24) + 10))
        multi_live_points.append(music['multiLiveHot'])

    available_estimator = regression.HotEstimator(available_points)
    multi_live_estimator = regression.HotEstimator(multi_live_points)

    for music in musics.values():
        if music['hotIgnore']:
            continue

        if music['releaseConditionId'] == 5:
            music['availableHot'] = available_estimator.estimate(music['availableHot'])
            music['multiLiveHot'] = multi_live_estimator.estimate(music['multiLiveHot'])
            music['hotAdjust'] = (
                + music['availableHot'] * 0.5
                + music['multiLiveHot'] * 0.5
            )
        else:
            music['multiLiveHot'] = multi_live_estimator.estimate(music['multiLiveHot'])
            music['hotAdjust'] = (
                + music['multiLiveHot'] * 1.0
            )

        music['hot'] = math.exp(music['hotAdjust']) * 1000.0

    # music difficulty play level

    full_combo_points = []
    full_perfect_points = []
    for music_difficulty in music_difficulties.values():
        published_time = musics[music_difficulty['musicId']]['publishedTime']
        if not published_time / (1000 * 60 * 60 * 24) > 1:
            continue

        music_difficulty['clearRate'] = music_difficulty['clearCount'] / music_difficulty['count']
        music_difficulty['fullComboRate'] = music_difficulty['fullComboCount'] / music_difficulty['clearCount']
        music_difficulty['fullPerfectRate'] = music_difficulty['fullPerfectCount'] / music_difficulty['clearCount']

        adjust_count = regression.LevelEstimator.adjust_count(
            music_difficulty['playLevel'],
            music_difficulty['musicDifficulty'],
            music_difficulty['count'],
            musics[music_difficulty['musicId']]['availableCount'],
            music_difficulty['clearCount'],
        )

        adjust_constant = regression.LevelEstimator.adjust_constant(
            music_difficulty['playLevel'],
            music_difficulty['musicDifficulty'],
            multi_live_hot=musics[music_difficulty['musicId']].get('multiLiveHot', 0),
            published_time=published_time,
        )

        try:
            music_difficulty['fullComboAdjust'] = math.atanh(1 - (
                + music_difficulty['fullComboCount'] / adjust_count * 2
            )) + adjust_constant
            music_difficulty['fullPerfectAdjust'] = math.atanh(1 - (
                + music_difficulty['fullPerfectCount'] / adjust_count * 2
            )) + adjust_constant

        except ValueError:
            traceback.print_exc()
            print(music_difficulty)
            continue

        full_combo_points.append((
            music_difficulty['fullComboAdjust'],
            regression.LevelEstimator.adjust_level_by_music_difficulty(
                music_difficulty['playLevel'], music_difficulty['musicDifficulty']),
        ))
        full_perfect_points.append((
            music_difficulty['fullPerfectAdjust'],
            regression.LevelEstimator.adjust_level_by_music_difficulty(
                music_difficulty['playLevel'], music_difficulty['musicDifficulty']),
        ))

    full_combo_estimator = regression.LevelEstimator(full_combo_points)
    full_perfect_estimator = regression.LevelEstimator(full_perfect_points)

    for music_difficulty in music_difficulties.values():
        if 'fullComboAdjust' in music_difficulty:
            music_difficulty['fullComboAdjust'] = full_combo_estimator.estimate(
                music_difficulty['fullComboAdjust'], music_difficulty['playLevel'], music_difficulty['musicDifficulty'])
            music_difficulty['fullPerfectAdjust'] = full_perfect_estimator.estimate(
                music_difficulty['fullPerfectAdjust'], music_difficulty['playLevel'], music_difficulty['musicDifficulty'])
            music_difficulty['playLevelAdjust'] = (
                + music_difficulty['fullComboAdjust'] * 2/3
                + music_difficulty['fullPerfectAdjust'] * 1/3
            )

    os.makedirs('public', exist_ok=True)

    with open('public/musics.json', 'w') as f:
        json.dump(list(musics.values()), f, indent=4)

    with open('public/musicDifficulties.json', 'w') as f:
        json.dump(list(music_difficulties.values()), f, indent=4)


if __name__ == '__main__':
    handle()
