import random
import time
import json

from modules.config import piccacheurl
from modules.otherpics import gachapic


def getcard(data, cardid, para):
    for i in data:
        if i['id'] == cardid:
            return i[para]


def getcharaname(characterid):
    with open('masterdata/gameCharacters.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in data:
        if i['id'] == characterid:
            try:
                return i['firstName'] + i['givenName']
            except KeyError:
                return i['givenName']


def getcurrentgacha():
    gachas = []
    with open('masterdata/gachas.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in range(0, len(data)):
        startAt = data[i]['startAt']
        endAt = data[i]['endAt']
        now = int(round(time.time() * 1000))
        if int(startAt) < now < int(endAt):
            for gachaBehaviors in data[i]['gachaBehaviors']:
                if (gachaBehaviors['costResourceType'] == 'jewel'
                        and gachaBehaviors['gachaBehaviorType'] == 'over_rarity_3_once'
                        and gachaBehaviors['costResourceQuantity'] == 3000):
                    if len(data[i]['gachaPickups']) > 2 and data[i]['name'][:4] != '[復刻]':
                        gachas.append({'id': str(data[i]['id']), 'gachaBehaviorsid': str(gachaBehaviors['id']),
                                       'name': data[i]['name']})
    length = len(gachas)
    return gachas[length - 1]

def getallcurrentgacha():
    gachas = []
    with open('masterdata/gachas.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in range(0, len(data)):
        startAt = data[i]['startAt']
        endAt = data[i]['endAt']
        now = int(round(time.time() * 1000))
        if int(startAt) < now < int(endAt):
            for gachaBehaviors in data[i]['gachaBehaviors']:
                if (gachaBehaviors['costResourceType'] == 'jewel'
                        and gachaBehaviors['gachaBehaviorType'] == 'over_rarity_3_once'
                        and gachaBehaviors['costResourceQuantity'] == 3000):
                    gachas.append({'id': str(data[i]['id']), 'gachaBehaviorsid': str(gachaBehaviors['id']),
                                   'name': data[i]['name']})
    return gachas


def fakegacha(gachaid, num, reverse=False, selfbot=False):  # 仅支持普通活动抽卡
    with open('masterdata/gachas.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    gacha = None
    birthday = False
    for i in range(0, len(data)):
        if data[i]['id'] == gachaid:
            gacha = data[i]
    if gacha is None:
        return f'找不到编号为{gachaid}的卡池，命令:/sekai抽卡 /sekaiXX连 /sekai反抽卡，三个命令后面都可以加卡池id'
    rate4 = 0
    rate3 = 0
    for i in range(0, len(gacha['gachaCardRarityRates'])):
        if gacha['gachaCardRarityRates'][i]['cardRarityType'] == 'rarity_4':
            rate4 = gacha['gachaCardRarityRates'][i]['rate']
            break
        if gacha['gachaCardRarityRates'][i]['cardRarityType'] == 'rarity_birthday':
            rate4 = gacha['gachaCardRarityRates'][i]['rate']
            birthday = True
            break
    for i in range(0, len(gacha['gachaCardRarityRates'])):
        if gacha['gachaCardRarityRates'][i]['cardRarityType'] == 'rarity_3':
            rate3 = gacha['gachaCardRarityRates'][i]['rate']
    if reverse:
        rate4 = 100 - rate4 - rate3
    with open('masterdata/cards.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)
    reality2 = []
    reality3 = []
    reality4 = []
    allweight = 0
    for detail in gacha['gachaDetails']:
        for card in cards:
            if card['id'] == detail['cardId']:
                if card['cardRarityType'] == 'rarity_2':
                    reality2.append({'id': card['id'], 'prefix': card['prefix'], 'charaid': card['characterId']})
                elif card['cardRarityType'] == 'rarity_3':
                    reality3.append({'id': card['id'], 'prefix': card['prefix'], 'charaid': card['characterId']})
                else:
                    allweight = allweight + detail['weight']
                    reality4.append({'id': card['id'], 'prefix': card['prefix'],
                                     'charaid': card['characterId'], 'weight': detail['weight']})
    alltext = ''
    keytext = ''
    baodi = True
    count4 = 0
    count3 = 0
    count2 = 0
    result = []
    for i in range(1, num + 1):
        if i % 10 == 0 and baodi and reverse is not True:
            baodi = False
            rannum = random.randint(0, int(rate4 + rate3) * 2) / 2
        else:
            rannum = random.randint(0, 100)
        if rannum < rate4:  # 四星
            count4 += 1
            baodi = False
            nowweight = 0
            rannum2 = random.randint(0, allweight - 1)
            for j in range(0, len(reality4)):
                nowweight = nowweight + reality4[j]['weight']
                if nowweight >= rannum2:
                    if birthday:
                        alltext = alltext + "🎀"
                        keytext = keytext + "🎀"
                    else:
                        alltext = alltext + "★★★★"
                        keytext = keytext + "★★★★"
                    if reality4[j]['weight'] == 400000:
                        alltext = alltext + "[当期]"
                        keytext = keytext + "[当期]"
                    alltext = alltext + f"{reality4[j]['prefix']} - {getcharaname(reality4[j]['charaid'])}\n"
                    keytext = keytext + f"{reality4[j]['prefix']} - {getcharaname(reality4[j]['charaid'])}(第{i}抽)\n"
                    result.append(reality4[j]['id'])
                    break
        elif rannum < rate4 + rate3:  # 三星
            count3 += 1
            rannum2 = random.randint(0, len(reality3) - 1)
            alltext = alltext + f"★★★{reality3[rannum2]['prefix']} - {getcharaname(reality3[rannum2]['charaid'])}\n"
            result.append(reality3[rannum2]['id'])
        else:  # 二星
            count2 += 1
            rannum2 = random.randint(0, len(reality3) - 1)
            alltext = alltext + f"★★{reality2[rannum2]['prefix']} - {getcharaname(reality2[rannum2]['charaid'])}\n"
            result.append(reality2[rannum2]['id'])

    if num == 10:
        now = int(time.time()*1000)
        gachapic(result, now)
        if selfbot:
            return f"[{gacha['name']}]", f"piccache/{now}.jpg"
        else:
            return f"[{gacha['name']}]\n[CQ:image,file={piccacheurl}{now}.jpg,cache=0]"
    elif num < 10:
        return f"[{gacha['name']}]\n{alltext}"
    else:
        if birthday:
            return f"[{gacha['name']}]\n{num}抽模拟抽卡，只显示抽到的四星如下:\n{keytext}\n生日卡：{count4} 三星：{count3} 二星：{count2}"
        else:
            return f"[{gacha['name']}]\n{num}抽模拟抽卡，只显示抽到的四星如下:\n{keytext}\n四星：{count4} 三星：{count3} 二星：{count2}"


if __name__ == '__main__':
    # print(fakegacha(67, 10, False))
    print(getallcurrentgacha())