import json
import time
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import requests

from modules.config import apiurl, enapiurl, twapiurl
from modules.sk import verifyid
assetpath = 'data/assets/sekai/assetbundle/resources'
rankmatchgrades = {
    1: 'ビギナー(初学者)',
    2: 'ブロンズ(青铜)',
    3: 'シルバー(白银)',
    4: 'ゴールド(黄金)',
    5: 'プラチナ(白金)',
    6: 'ダイヤモンド(钻石)',
    7: 'マスター(大师)'
}


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

    def getprofile(self, userid, server):
        if server == 'jp':
            url = apiurl
            masterdatadir = 'masterdata'
        elif server == 'en':
            url = enapiurl
            masterdatadir = '../enapi/masterdata'
        elif server == 'tw':
            url = twapiurl
            masterdatadir = '../twapi/masterdata'
        resp = requests.get(f'{url}/user/{userid}/profile')
        data = json.loads(resp.content)
        # with open('piccache\profile.json', 'r', encoding='utf-8') as f:
        #     data = json.load(f)
        self.name = data['user']['userGamedata']['name']

        try:
            self.twitterId = data['userProfile']['twitterId']
        except:
            pass

        self.userid = userid

        try:
            self.word = data['userProfile']['word']
        except:
            pass

        self.rank = data['user']['userGamedata']['rank']
        try:
            self.characterId = data['userChallengeLiveSoloResults'][0]['characterId']
            self.highScore = data['userChallengeLiveSoloResults'][0]['highScore']
        except:
            pass
        self.characterRank = data['userCharacters']
        if server == 'en':
            self.userProfileHonors = [{}, {}, {}]
            for i in range(0, 3):
                try:
                    honorid = data['userProfile'][f'honorId{i + 1}']
                    for honor in data['userHonors']:
                        if honor['honorId'] == honorid:
                            self.userProfileHonors[i] = honor
                except:
                    pass
        else:
            self.userProfileHonors = data['userProfileHonors']
        # print(self.userProfileHonors)
        with open(f'{masterdatadir}/musics.json', 'r', encoding='utf-8') as f:
            allmusic = json.load(f)
        with open(f'{masterdatadir}/musicDifficulties.json', 'r', encoding='utf-8') as f:
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


def currentrankmatch():
    with open('masterdata/rankMatchSeasons.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in range(0, len(data)):
        startAt = data[i]['startAt']
        endAt = data[i]['closedAt']
        now = int(round(time.time() * 1000))
        if not startAt < now < endAt:
            continue
        return data[i]['id']
    return data[len(data) - 1]['id']


def daibu(targetid=None, secret=False, server='jp'):
    if not verifyid(targetid, server):
        return '你这ID有问题啊'
    try:
        profile = userprofile()
        profile.getprofile(targetid, server)
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
    return text + "\n\n" + rk(targetid, None, secret, True)


def rk(targetid=None, targetrank=None, secret=False, isdaibu=False):
    rankmatchid = currentrankmatch()
    if targetid is not None:
        if not verifyid(targetid):
            return '你这ID有问题啊'
        resp = requests.get(f'{apiurl}/user/%7Buser_id%7D/rank-match-season/{rankmatchid}/'
                            f'ranking?targetUserId={targetid}')
    else:
        resp = requests.get(f'{apiurl}/user/%7Buser_id%7D/rank-match-season/{rankmatchid}/'
                            f'ranking?targetRank={targetrank}')
    try:
        data = json.loads(resp.content)
        ranking = data['rankings'][0]['userRankMatchSeason']
        grade = int((ranking['rankMatchTierId'] - 1) / 4) + 1
    except IndexError:
        return '未参加当期排位赛'
    if grade > 7:
        grade = 7
    gradename = rankmatchgrades[grade]
    kurasu = ranking['rankMatchTierId'] - 4 * (grade - 1)
    if not kurasu:
        kurasu = 4
    winrate = ranking['winCount'] / (ranking['winCount'] + ranking['loseCount'])
    if not isdaibu:
        if targetid is None:
            text = data['rankings'][0]['name'] + '\n'
        else:
            if secret:
                text = f"{data['rankings'][0]['name']}\n"
            else:
                text = f"{data['rankings'][0]['name']} - {data['rankings'][0]['userId']}\n"
    else:
        text = ''
    if grade == 7:
        text = text + f"{gradename}🎵×{ranking['tierPoint']}\n排名：{data['rankings'][0]['rank']}\n"
    else:
        text = text + f"{gradename}Class {kurasu}({ranking['tierPoint']}/5)\n排名：{data['rankings'][0]['rank']}\n"
    text = text + f"Win {ranking['winCount']} | Draw {ranking['drawCount']} | "
    if ranking['penaltyCount'] == 0:
        text = text + f"Lose {ranking['loseCount']}\n"
    else:
        text = text + f"Lose {ranking['loseCount'] - ranking['penaltyCount']}+{ranking['penaltyCount']}\n"
    text = text + f'胜率(除去平局)：{round(winrate * 100, 2)}%\n'
    text = text + f"最高连胜：{ranking['maxConsecutiveWinCount']}\n"
    return text


def pjskjindu(userid, private=False, diff='master', server='jp'):
    profile = userprofile()
    profile.getprofile(userid, server)
    if private:
        id = '保密'
    else:
        id = userid
    if diff == 'master':
        img = Image.open(r'pics/bgmaster.png')
    else:
        img = Image.open(r'pics/bgexpert.png')
    with open('masterdata/cards.json', 'r', encoding='utf-8') as f:
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


def pjskprofile(userid, private=False, server='jp'):
    profile = userprofile()
    profile.getprofile(userid, server)
    if private:
        id = '保密'
    else:
        id = userid
    img = Image.open(r'pics/bg.png')
    with open('masterdata/cards.json', 'r', encoding='utf-8') as f:
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
    if server == 'en':
        try:
            honorpic = generatehonor(profile.userProfileHonors[0], True, server)
            honorpic = honorpic.resize((266, 56))
            r, g, b, mask = honorpic.split()
            img.paste(honorpic, (104, 228), mask)
        except:
            pass
        try:
            honorpic = generatehonor(profile.userProfileHonors[1], False, server)
            honorpic = honorpic.resize((126, 56))
            r, g, b, mask = honorpic.split()
            img.paste(honorpic, (375, 228), mask)
        except:
            pass
        try:
            honorpic = generatehonor(profile.userProfileHonors[2], False, server)
            honorpic = honorpic.resize((126, 56))
            r, g, b, mask = honorpic.split()
            img.paste(honorpic, (508, 228), mask)
        except:
            pass
    else:
        for i in profile.userProfileHonors:
            if i['seq'] == 1:
                try:
                    honorpic = generatehonor(i, True, server)
                    honorpic = honorpic.resize((266, 56))
                    r, g, b, mask = honorpic.split()
                    img.paste(honorpic, (104, 228), mask)
                except:
                    pass

        for i in profile.userProfileHonors:
            if i['seq'] == 2:
                try:
                    honorpic = generatehonor(i, False, server)
                    honorpic = honorpic.resize((126, 56))
                    r, g, b, mask = honorpic.split()
                    img.paste(honorpic, (375, 228), mask)
                except:
                    pass

        for i in profile.userProfileHonors:
            if i['seq'] == 3:
                try:
                    honorpic = generatehonor(i, False, server)
                    honorpic = honorpic.resize((126, 56))
                    r, g, b, mask = honorpic.split()
                    img.paste(honorpic, (508, 228), mask)
                except:
                    pass

    img.save(fr'piccache\{userid}profile.png')
    return


def generatehonor(honor, ismain=True, server='jp'):
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
        with open('masterdata/honors.json', 'r', encoding='utf-8') as f:
            honors = json.load(f)
        with open('masterdata/honorGroups.json', 'r', encoding='utf-8') as f:
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
                    pic.paste(rankpic, (190, 0), mask)
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
                if server == 'en':
                    honorlevel = honor['level']
                else:
                    honorlevel = honor['honorLevel']
                if star is True:
                    for i in range(0, honorlevel):
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
                    pic.paste(rankpic, (34, 42), mask)
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
                    if server == 'en':
                        honorlevel = honor['level']
                    else:
                        honorlevel = honor['honorLevel']
                    if honorlevel < 5:
                        for i in range(0, honorlevel):
                            lv = Image.open(r'pics/icon_degreeLv.png')
                            r, g, b, mask = lv.split()
                            pic.paste(lv, (54 + 16 * i, 63), mask)
                    else:
                        for i in range(0, 5):
                            lv = Image.open(r'pics/icon_degreeLv.png')
                            r, g, b, mask = lv.split()
                            pic.paste(lv, (54 + 16 * i, 63), mask)
                        for i in range(0, honorlevel - 5):
                            lv = Image.open(r'pics/icon_degreeLv6.png')
                            r, g, b, mask = lv.split()
                            pic.paste(lv, (54 + 16 * i, 63), mask)
    else:
        # cp牌子
        with open('masterdata/bondsHonors.json', 'r', encoding='utf-8') as f:
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
            maskimg = Image.open('pics/mask_degree_main.png')
            r, g, b, mask = maskimg.split()
            pic.putalpha(mask)
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
            maskimg = Image.open('pics/mask_degree_sub.png')
            r, g, b, mask = maskimg.split()
            pic.putalpha(mask)
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

def pjskb30(userid, private=False, returnpic=False, server='jp'):
    if server == 'jp':
        url = apiurl
    elif server == 'en':
        url = enapiurl
    elif server == 'tw':
        url = twapiurl
    resp = requests.get(f'{url}/user/{userid}/profile')
    data = json.loads(resp.content)
    # with open('piccache\profile.json', 'r', encoding='utf-8') as f:
    #     data = json.load(f)
    name = data['user']['userGamedata']['name']
    if server == 'en':
        userProfileHonors = [{}, {}, {}]
        for i in range(0, 3):
            try:
                honorid = data['userProfile'][f'honorId{i + 1}']
                for honor in data['userHonors']:
                    if honor['honorId'] == honorid:
                        userProfileHonors[i] = honor
            except:
                pass
    else:
        userProfileHonors = data['userProfileHonors']
    rank = data['user']['userGamedata']['rank']
    userDecks = [0, 0, 0, 0, 0]
    special_training = [False, False, False, False, False]
    for i in range(0, 5):
        userDecks[i] = data['userDecks'][0][f'member{i + 1}']
        for userCards in data['userCards']:
            if userCards['cardId'] != userDecks[i]:
                continue
            if userCards['defaultImage'] == "special_training":
                special_training[i] = True
    pic = Image.open('pics/b30.png')
    if private:
        id = '保密'
    else:
        id = userid
    with open('masterdata/cards.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)
    try:
        assetbundleName = ''
        for i in cards:
            if i['id'] == userDecks[0]:
                assetbundleName = i['assetbundleName']
        if special_training[0]:
            cardimg = Image.open(f'{assetpath}/startapp/thumbnail/chara/{assetbundleName}_after_training.png')
            cutoutimg = Image.open(f'{assetpath}/startapp/character/member_cutout_trm/{assetbundleName}/after_training.png')
        else:
            cardimg = Image.open(f'{assetpath}/startapp/thumbnail/chara/{assetbundleName}_normal.png')
            cutoutimg = Image.open(f'{assetpath}/startapp/character/member_cutout_trm/{assetbundleName}/normal.png')
        cutoutimg = cutoutimg.resize((int(cutoutimg.size[0]*0.47), int(cutoutimg.size[1]*0.47)))
        r, g, b, mask = cutoutimg.split()
        pic.paste(cutoutimg, (770, 15), mask)

        cardimg = cardimg.resize((116, 116))
        r, g, b, mask = cardimg.split()
        pic.paste(cardimg, (68, 70), mask)
    except FileNotFoundError:
        pass
    draw = ImageDraw.Draw(pic)
    font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 35)
    draw.text((215, 65), name, fill=(0, 0, 0), font=font_style)
    font_style = ImageFont.truetype(r"fonts\FOT-RodinNTLGPro-DB.ttf", 15)
    draw.text((218, 118), 'id:' + id, fill=(0, 0, 0), font=font_style)
    font_style = ImageFont.truetype(r"fonts\FOT-RodinNTLGPro-DB.ttf", 28)
    draw.text((314, 150), str(rank), fill=(255, 255, 255), font=font_style)

    if server == 'en':
        try:
            honorpic = generatehonor(userProfileHonors[0], True, server)
            honorpic = honorpic.resize((226, 48))
            r, g, b, mask = honorpic.split()
            pic.paste(honorpic, (59, 226), mask)
        except:
            pass
        try:
            honorpic = generatehonor(userProfileHonors[1], False, server)
            honorpic = honorpic.resize((107, 48))
            r, g, b, mask = honorpic.split()
            pic.paste(honorpic, (290, 226), mask)
        except:
            pass
        try:
            honorpic = generatehonor(userProfileHonors[2], False, server)
            honorpic = honorpic.resize((107, 48))
            r, g, b, mask = honorpic.split()
            pic.paste(honorpic, (403, 226), mask)
        except:
            pass
    else:
        for i in userProfileHonors:
            if i['seq'] == 1:
                try:
                    honorpic = generatehonor(i, True, server)
                    honorpic = honorpic.resize((226, 48))
                    r, g, b, mask = honorpic.split()
                    pic.paste(honorpic, (59, 226), mask)
                except:
                    pass

        for i in userProfileHonors:
            if i['seq'] == 2:
                try:
                    honorpic = generatehonor(i, False, server)
                    honorpic = honorpic.resize((107, 48))
                    r, g, b, mask = honorpic.split()
                    pic.paste(honorpic, (290, 226), mask)
                except:
                    pass

        for i in userProfileHonors:
            if i['seq'] == 3:
                try:
                    honorpic = generatehonor(i, False, server)
                    honorpic = honorpic.resize((107, 48))
                    r, g, b, mask = honorpic.split()
                    pic.paste(honorpic, (403, 226), mask)
                except:
                    pass

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
    if server == 'jp':
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
        found = False
        for i in range(0, len(diff)):
            if diff[i]['musicId'] == musicId and diff[i]['musicDifficulty'] == musicDifficulty:
                found = True
                break
        if found:
            if playResult == 'full_perfect':
                diff[i]['result'] = 2
                diff[i]['rank'] = diff[i]['aplevel+']
            elif playResult == 'full_combo':
                if diff[i]['result'] < 1:
                    diff[i]['result'] = 1
                    diff[i]['rank'] = diff[i]['fclevel+'] * 0.95

    diff.sort(key=lambda x: x["rank"], reverse=True)
    rank = 0
    shadow = Image.new("RGBA", (320, 130), (0, 0, 0, 0))
    shadow.paste(Image.new("RGBA", (310, 120), (0, 0, 0, 50)), (5, 5))
    shadow = shadow.filter(ImageFilter.GaussianBlur(3))
    if server == 'en':
        with open(r'../enapi/masterdata/musics.json', 'r', encoding='utf-8') as f:
            musics = json.load(f)
    for i in range(0, 30):
        rank = rank + diff[i]['rank']
        single = b30single(diff[i], musics)
        r, g, b, mask = shadow.split()
        pic.paste(shadow, ((int(52 + (i % 3) * 342)), int(307 + int(i / 3) * 142)), mask)
        pic.paste(single, ((int(53+(i%3)*342)), int(309+int(i/3)*142)))
    rank = round(rank / 30, 2)

    font_style = ImageFont.truetype("fonts/SourceHanSansCN-Medium.otf", 16)
    if server == 'jp':
        textadd = f'，当前理论值为{highest}'
    else:
        textadd = ''
    draw.text((50, 1722), f'注：FC权重为0.95，非官方算法，仅供参考娱乐{textadd}', fill='#00CCBB',
              font=font_style)
    draw.text((50, 1752), '定数来源：https://profile.pjsekai.moe/  ※定数每次统计时可能会改变', fill='#00CCBB',
              font=font_style)
    rankimg = Image.new("RGBA", (120, 55), (100, 110, 180, 0))
    draw = ImageDraw.Draw(rankimg)
    font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 35)
    text_width = font_style.getsize(str(rank))
    # 硬核画文字边框
    draw.text((int(60 - text_width[0] / 2) + 3, int(20 - text_width[1] / 2)), str(rank), fill=(61, 74, 162, 210),
              font=font_style)
    draw.text((int(60 - text_width[0] / 2) - 3, int(20 - text_width[1] / 2)), str(rank), fill=(61, 74, 162, 210),
              font=font_style)
    draw.text((int(60 - text_width[0] / 2), int(20 - text_width[1] / 2) + 3), str(rank), fill=(61, 74, 162, 210),
              font=font_style)
    draw.text((int(60 - text_width[0] / 2), int(20 - text_width[1] / 2) - 3), str(rank), fill=(61, 74, 162, 210),
              font=font_style)
    draw.text((int(60 - text_width[0] / 2) - 2, int(20 - text_width[1] / 2) - 2), str(rank), fill=(61, 74, 162, 210),
              font=font_style)
    draw.text((int(60 - text_width[0] / 2) + 2, int(20 - text_width[1] / 2) + 2), str(rank), fill=(61, 74, 162, 210),
              font=font_style)
    draw.text((int(60 - text_width[0] / 2) - 2, int(20 - text_width[1] / 2) + 2), str(rank), fill=(61, 74, 162, 210),
              font=font_style)
    draw.text((int(60 - text_width[0] / 2) + 2, int(20 - text_width[1] / 2) - 2), str(rank), fill=(61, 74, 162, 210),
              font=font_style)
    rankimg = rankimg.filter(ImageFilter.GaussianBlur(1.2))
    draw = ImageDraw.Draw(rankimg)
    draw.text((int(60 - text_width[0] / 2), int(20 - text_width[1] / 2)), str(rank), fill=(255, 255, 255), font=font_style)
    r, g, b, mask = rankimg.split()
    pic.paste(rankimg, (565, 142), mask)
    # pic.show()
    pic = pic.convert("RGB")
    if returnpic:
        return pic
    pic.save(fr'piccache\{userid}b30.png')

def b30single(diff, musics):
    color = {
        'master': (187, 51, 238),
        'expert': (238, 67, 102),
        'hard': (254, 170, 0),
        'normal': (51, 187, 238),
        'easy': (102, 221, 17),
    }
    musictitle = ''
    for j in musics:
        if j['id'] == diff['musicId']:
            musictitle = j['title']
    pic = Image.new("RGB", (620, 240), (255, 255, 255))
    if diff['result'] == 2 or diff['result'] == 1:
        draw = ImageDraw.Draw(pic)
        font = ImageFont.truetype(r'fonts\YuGothicUI-Semibold.ttf', 48)
        size = font.getsize(musictitle)
        if size[0] > 365:
            musictitle = musictitle[:int(len(musictitle)*(345/size[0]))] + '...'
        draw.text((238, 84), musictitle, '#000000', font)
        # print(musictitle, font.getsize(musictitle))
        jacket = Image.open(f'{assetpath}/startapp/thumbnail/music_jacket/jacket_s_{str(diff["musicId"]).zfill(3)}.png')
        jacket = jacket.resize((186, 186))
        pic.paste(jacket, (32, 28))

        draw.ellipse((5, 5, 5+60, 5+60), fill=color[diff['musicDifficulty']])
        font = ImageFont.truetype(r'fonts\SourceHanSansCN-Bold.otf', 38)
        text_width = font.getsize(str(diff['playLevel']))
        text_coordinate = (int(36 - text_width[0] / 2), int(28 - text_width[1] / 2))
        draw.text(text_coordinate, str(diff['playLevel']), (255, 255, 255), font)

        draw.ellipse((242, 32, 286, 76), fill=color[diff['musicDifficulty']])
        draw.rectangle((262, 32, 334, 76), fill=color[diff['musicDifficulty']])
        draw.ellipse((312, 32, 356, 76), fill=color[diff['musicDifficulty']])


        if diff['playLevelAdjust'] != 0:
            if diff['result'] == 2:
                resultpic = Image.open('pics/AllPerfect.png')
                draw.text((259, 24), str(round(diff['aplevel+'], 1)), (255, 255, 255), font)
                draw.text((370, 24), '→ ' + str(round(diff['aplevel+'], 1)), (0, 0, 0), font)
            if diff['result'] == 1:
                resultpic = Image.open('pics/FullCombo.png')
                draw.text((259, 24), str(round(diff['fclevel+'], 1)), (255, 255, 255), font)
                draw.text((370, 24), '→ ' + str(round(diff['fclevel+'] * 0.95, 1)), (0, 0, 0), font)
        else:
            if diff['result'] == 2:
                resultpic = Image.open('pics/AllPerfect.png')
                draw.text((259, 24), f'{round(diff["aplevel+"], 1)}.?', (255, 255, 255), font)
                draw.text((370, 24), f'→ {round(diff["aplevel+"], 1)}.0', (0, 0, 0), font)
            if diff['result'] == 1:
                resultpic = Image.open('pics/FullCombo.png')
                draw.text((259, 24), f'{round(diff["fclevel+"], 1)}.?', (255, 255, 255), font)
                draw.text((370, 24), f'→ {round(diff["fclevel+"] * 0.95, 1)}', (0, 0, 0), font)
        r, g, b, mask = resultpic.split()
        pic.paste(resultpic, (238, 154), mask)
    pic = pic.resize((310, 120))
    return pic

if __name__ == '__main__':
    pass
