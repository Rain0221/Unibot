import time
import functools
import threading

import api
import utils
import thread_manager


summary_musics = {}
summary_music_difficulties = {}
summary_honors = {}
summary_bonds_honors = {}

summary_musics_lock = threading.Lock()
summary_music_difficulties_lock = threading.Lock()
summary_honors_lock = threading.Lock()
summary_bonds_honors_lock = threading.Lock()


def function(a):
    with api.Sekai.get_from_pool() as sekai:
        profile = sekai('GET', '/api/user/%s/profile' % a)

    for user_music in profile['userMusics']:
        result_music = {
            'musicId': user_music['musicId'],
            'mvpCount': 0,
            'superStarCount': 0,
        }

        for user_music_difficulty_status in user_music['userMusicDifficultyStatuses']:
            if not user_music_difficulty_status['userMusicResults']:
                continue

            result_music_difficulty = {
                'musicId': user_music['musicId'],
                'musicDifficulty': user_music_difficulty_status['musicDifficulty'],
                'fullComboFlg': False,
                'fullPerfectFlg': False,
            }

            for user_music_result in user_music_difficulty_status['userMusicResults']:
                result_music['mvpCount'] += user_music_result['mvpCount']
                result_music['superStarCount'] += user_music_result['superStarCount']

                result_music_difficulty['fullComboFlg'] |= user_music_result['fullComboFlg']
                result_music_difficulty['fullPerfectFlg'] |= user_music_result['fullPerfectFlg']

            with summary_music_difficulties_lock:
                summary_music_difficulty = summary_music_difficulties[(
                    user_music['musicId'], result_music_difficulty['musicDifficulty'])]
                summary_music_difficulty['count'] += 1
                summary_music_difficulty['fullComboCount'] += int(result_music_difficulty['fullComboFlg'])
                summary_music_difficulty['fullPerfectCount'] += int(result_music_difficulty['fullPerfectFlg'])

        with summary_musics_lock:
            summary_music = summary_musics[user_music['musicId']]
            summary_music['count'] += 1
            summary_music['mvpCount'] += result_music['mvpCount']
            summary_music['superStarCount'] += result_music['superStarCount']

    for user_honor in profile['userHonors']:
        with summary_honors_lock:
            summary_honor = summary_honors[user_honor['honorId']]
            summary_honor['count'] += 1
            summary_honor['levels'][user_honor['level']] += 1

    for user_bonds_honor in profile['userBondsHonors']:
        with summary_bonds_honors_lock:
            summary_bonds_honor = summary_bonds_honors[user_bonds_honor['bondsHonorId']]
            summary_bonds_honor['count'] += 1
            summary_bonds_honor['levels'][user_bonds_honor['level']] += 1


def run(function, event_id, rank_from, rank_to, n_threads=16):
    threading.Thread(target=thread_manager.start_thread, args=(thread_manager.thread, function, n_threads)).start()

    thread_manager.progress.total = rank_to - rank_from

    for i in range(rank_from, rank_to, 200):
        with api.Sekai.get_from_pool() as sekai:
            rankings = sekai('GET', '/api/user/{user_id}/event/%s/ranking?targetRank=%s&lowerLimit=%s&higherLimit=%s' % (
                event_id, i+100, 100, 99))
            for ranking in rankings['rankings']:
                thread_manager.pool.put(ranking['userId'])

    thread_manager.pool.join()


@functools.lru_cache()
def get_event_id():
    now = time.time()
    event_ids = [
        event['id']
        for event in api.Sekai.get_database('events')
        if event['aggregateAt'] / 1000 < now
    ]
    return max(event_ids)


def get_ranks():
    rank_per_page = 10000
    rank_total = 200000

    for rank_from in range(0, rank_total, rank_per_page):
        rank_to = rank_from + rank_per_page
        if not utils.get_database('pjsekai_profile')['profileSummaries'].find_one({
            'eventId': get_event_id(),
            'rankFrom': rank_from,
            'rankTo': rank_to,
        }):
            return rank_from, rank_to

    return None, None


def handle():
    event_id = get_event_id()

    for music in api.Sekai.get_database('musics'):
        summary_musics[music['id']] = {
            'musicId': music['id'],
            'count': 0,
            'mvpCount': 0,
            'superStarCount': 0,
        }

    for music_difficulty in api.Sekai.get_database('musicDifficulties'):
        summary_music_difficulties[(music_difficulty['musicId'], music_difficulty['musicDifficulty'])] = {
            'musicId': music_difficulty['musicId'],
            'musicDifficulty': music_difficulty['musicDifficulty'],
            'count': 0,
            'fullComboCount': 0,
            'fullPerfectCount': 0,
        }

    for honor in api.Sekai.get_database('honors'):
        summary_honors[honor['id']] = {
            'honorId': honor['id'],
            'count': 0,
            'levels': {
                level['level']: 0
                for level in honor['levels']
            }
        }

    for bonds_honor in api.Sekai.get_database('bondsHonors'):
        summary_bonds_honors[bonds_honor['id']] = {
            'bondsHonorId': bonds_honor['id'],
            'count': 0,
            'levels': {
                level['level']: 0
                for level in bonds_honor['levels']
            }
        }

    rank_from, rank_to = get_ranks()

    print(event_id, rank_from, rank_to)

    if rank_from is None or rank_to is None:
        return

    run(function, event_id, rank_from, rank_to, n_threads=32)

    for summary_honor in summary_honors.values():
        summary_honor['levels'] = [
            {
                'level': level,
                'count': count,
            }
            for level, count in summary_honor['levels'].items()
        ]

    for summary_bonds_honor in summary_bonds_honors.values():
        summary_bonds_honor['levels'] = [
            {
                'level': level,
                'count': count,
            }
            for level, count in summary_bonds_honor['levels'].items()
        ]

    utils.get_database('pjsekai_profile')['profileSummaries'].insert_one({
        'eventId': event_id,
        'rankFrom': rank_from,
        'rankTo': rank_to,

        'musics': list(summary_musics.values()),
        'musicDifficulties': list(summary_music_difficulties.values()),
        'honors': list(summary_honors.values()),
        'bondsHonors': list(summary_bonds_honors.values()),
    })

    return True


if __name__ == '__main__':
    threading.Thread(target=api.Sekai.init_pool, args=(32, )).start()

    while handle():
        ...
