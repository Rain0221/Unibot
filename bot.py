import json
import os
import random
import time
import re
import asyncio
import traceback
from datetime import datetime

import requests
import yaml
from nakuru import (
    CQHTTP,
    GroupMessage,
    GroupMemberIncrease,
    GroupRequest,
    GroupMemberBan
)
import aiofiles
from nakuru.entities.components import Plain, Image
from chachengfen import dd_query
from modules.api import gacha
from modules.chara import charaset, grcharaset, charadel, charainfo, grcharadel, aliastocharaid
from modules.config import whitelist, wordcloud, block, msggroup
from modules.cyo5000 import genImage
from modules.gacha import getcharaname, getallcurrentgacha
from modules.homo import generate_homo
from modules.musics import hotrank, levelrank, parse_bpm, aliastochart, idtoname, notecount, tasseiritsu
from modules.pjskguess import getrandomjacket, cutjacket, getrandomchart, cutchartimg, getrandomcard, cutcard
from modules.pjskinfo import aliastomusicid, drawpjskinfo, pjskset, pjskdel, pjskalias
from modules.profileanalysis import daibu, rk, pjskjindu, pjskprofile, pjskb30
from modules.sk import sk, getqqbind, bindid, setprivate, skyc, verifyid, gettime
from modules.texttoimg import texttoimg, ycmimg
from modules.twitter import newesttwi
from wordCloud.generate import ciyun

if os.path.basename(__file__) == 'bot.py':
    unibot = CQHTTP(
        host="127.0.0.1",
        port=1234,
        http_port=5678
    )
    print('一号机启动')
else:
    unibot = CQHTTP(
        host="127.0.0.1",
        port=2345,
        http_port=6789
    )
    print('三号机启动')

pjskguess = {}
charaguess = {}
ciyunlimit = {}
gachalimit = {'lasttime': '', 'count': 0}
admin = [1103479519]
mainbot = [1513705608]
allbot = [1513705608, 3506606538]  # 排除测试账号的消息回复
requestwhitelist = []  # 邀请加群白名单 随时设置 不保存到文件
groupban = [467602419]

@unibot.receiver("GroupMessage")
async def _(app: CQHTTP, source: GroupMessage):
    global pjskguess
    global charaguess
    global ciyunlimit
    global gachalimit
    global blacklist
    global requestwhitelist
    print(source.group_id, source.user_id, source.raw_message)
    if source.group_id in groupban:
        print('黑名单群已拦截')
        return
    if source.user_id in block:
        print('黑名单成员已拦截')
        return
    if source.self_id not in allbot:  # 排除测试账号的消息回复
        return
    if source.group_id in wordcloud:
        if 'CQ:' not in source.raw_message and '&#' not in source.raw_message:
            async with aiofiles.open(f'wordCloud/{source.group_id}.txt', 'a', encoding='utf-8') as f:
                await f.write(source.raw_message + '\n')

    if source.raw_message[0:1] == '/':
        source.raw_message = source.raw_message[1:]
    try:
        if source.raw_message == '词云':
            if source.group_id not in wordcloud:
                await app.sendGroupMessage(source.group_id, '该群未开启词云功能，请联系bot主人手动开启')
                return
            try:
                lasttime = ciyunlimit[source.group_id]
                if time.time() - lasttime < 3600:
                    await app.sendGroupMessage(source.group_id, '上一次查还没过多久捏。别急')
                    return
            except KeyError:
                pass
            ciyunlimit[source.group_id] = time.time()
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, ciyun, source.group_id)
            await app.sendGroupMessage(source.group_id, [
                Plain(text=''),
                Image.fromFileSystem(fr"piccache\{source.group_id}cy.png")
            ])
        if source.raw_message == 'help':
            await app.sendGroupMessage(source.group_id, '帮助文档：https://bot.unijzlsx.com/')
            return
        if source.raw_message[:8] == 'pjskinfo':
            source.raw_message = source.raw_message[source.raw_message.find("pjskinfo") + len("pjskinfo"):].strip()
            resp = aliastomusicid(source.raw_message)
            if resp['musicid'] == 0:
                await app.sendGroupMessage(source.group_id, '没有找到你要的歌曲哦')
                return
            else:
                loop = asyncio.get_event_loop()
                future = loop.run_in_executor(None, drawpjskinfo, resp['musicid'])
                leak = await future
                if resp['match'] < 0.8:
                    text = '你要找的可能是：'
                else:
                    text = ""
                if leak:
                    text = text + f"匹配度:{round(resp['match'], 4)}\n⚠该内容为剧透内容"
                else:
                    if resp['translate'] == '':
                        text = text + f"{resp['name']}\n匹配度:{round(resp['match'], 4)}"
                    else:
                        text = text + f"{resp['name']} ({resp['translate']})\n匹配度:{round(resp['match'], 4)}"
                await app.sendGroupMessage(source.group_id, [
                    Plain(text=text),
                    Image.fromFileSystem(fr"piccache\pjskinfo{resp['musicid']}.png")
                ])
            return
        if source.raw_message[:4] == '谱面文件':
            source.raw_message = source.raw_message[source.raw_message.find("谱面文件") + len("谱面文件"):].strip()
            resp = aliastomusicid(source.raw_message)
            if resp['musicid'] == 0:
                await app.sendGroupMessage(source.group_id, '没有找到你要的歌曲哦')
                return
            else:
                await app.sendGroupMessage(source.group_id, f"{resp['name']}\n匹配度:{round(resp['match'], 4)}\n")
                await app.sendGroupMessage(source.group_id, f"https://assets.sekai.unijzlsx.com/?dir=startapp"
                                                            fr"\music\music_score\{str(resp['musicid']).zfill(4)}_01")
        if source.raw_message[:7] == 'pjskset' and 'to' in source.raw_message:
            source.raw_message = source.raw_message[7:]
            para = source.raw_message.split('to')
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, pjskset, para[0], para[1], source.user_id)
            resp = await future
            await app.sendGroupMessage(source.group_id, resp)
            return
        if source.raw_message[:7] == 'pjskdel':
            source.raw_message = source.raw_message[7:]
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, pjskdel, source.raw_message, source.user_id)
            resp = await future
            await app.sendGroupMessage(source.group_id, resp)
            return
        if source.raw_message[:9] == 'pjskalias':
            source.raw_message = source.raw_message[9:]
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, pjskalias, source.raw_message)
            resp = await future
            await app.sendGroupMessage(source.group_id, resp)
            return
        if source.raw_message[:8] == "sekai真抽卡":
            if source.self_id not in mainbot:
                return
            if source.group_id in blacklist[source.self_id]['ettm']:
                return
            nowtime = f"{str(datetime.now().hour).zfill(2)}{str(datetime.now().minute).zfill(2)}"
            lasttime = gachalimit['lasttime']
            count = gachalimit['count']
            if nowtime == lasttime and count >= 2:
                await app.sendGroupMessage(source.group_id,
                                           f'技能冷却中，剩余cd:{60 - datetime.now().second}秒（一分钟内所有群只能抽两次）')
                return
            gachalimit['lasttime'] = nowtime
            gachalimit['count'] = count + 1
            await app.sendGroupMessage(source.group_id, '了解')
            gachaid = source.raw_message[source.raw_message.find("sekai真抽卡") + len("sekai真抽卡"):].strip()
            if gachaid == '':
                loop = asyncio.get_event_loop()
                future = loop.run_in_executor(None, gacha)
                result = await future
            else:
                currentgacha = getallcurrentgacha()
                targetgacha = None
                for gachas in currentgacha:
                    if int(gachas['id']) == int(gachaid):
                        targetgacha = gachas
                        break
                if targetgacha is None:
                    await app.sendGroupMessage(source.group_id, '你指定的id现在无法完成无偿十连')
                    return
                else:
                    loop = asyncio.get_event_loop()
                    future = loop.run_in_executor(None, gacha, targetgacha)
                    result = await future

            await app.sendGroupMessage(source.group_id, result)
            return
        if source.raw_message == "sk预测":
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, texttoimg, skyc(), 500, 'skyc')
            await future
            await app.sendGroupMessage(source.group_id, [
                Plain(text=''),
                Image.fromFileSystem(fr"piccache\skyc.png")
            ])
            return
        if source.raw_message[:2] == "sk":
            if source.group_id in blacklist[source.self_id]['sk']:
                return
            if source.raw_message == "sk":
                bind = getqqbind(source.user_id)
                if bind is None:
                    await app.sendGroupMessage(source.group_id, '你没有绑定id！')
                    return
                loop = asyncio.get_event_loop()
                future = loop.run_in_executor(None, sk, bind[1], None, bind[2])
                result = await future
                await app.sendGroupMessage(source.group_id, result)
            else:
                userid = source.raw_message.replace("sk", "")
                userid = re.sub(r'\D', "", userid)
                if userid == '':
                    await app.sendGroupMessage(source.group_id, '你这id有问题啊')
                    return
                loop = asyncio.get_event_loop()
                if int(userid) > 10000000:
                    future = loop.run_in_executor(None, sk, userid)
                else:
                    future = loop.run_in_executor(None, sk, None, userid)
                result = await future
                await app.sendGroupMessage(source.group_id, result)
            return
        if source.raw_message[:2] == "rk":
            if source.raw_message == "rk":
                bind = getqqbind(source.user_id)
                if bind is None:
                    await app.sendGroupMessage(source.group_id, '你没有绑定id！')
                    return
                loop = asyncio.get_event_loop()
                future = loop.run_in_executor(None, rk, bind[1], None, bind[2])
                result = await future
                await app.sendGroupMessage(source.group_id, result)
            else:
                userid = source.raw_message.replace("rk", "")
                userid = re.sub(r'\D', "", userid)
                if userid == '':
                    await app.sendGroupMessage(source.group_id, '你这id有问题啊')
                    return
                loop = asyncio.get_event_loop()
                if int(userid) > 10000000:
                    future = loop.run_in_executor(None, rk, userid)
                else:
                    future = loop.run_in_executor(None, rk, None, userid)
                result = await future
                await app.sendGroupMessage(source.group_id, result)
            return
        if source.raw_message[:2] == "绑定":
            userid = source.raw_message.replace("绑定", "")
            userid = re.sub(r'\D', "", userid)
            await app.sendGroupMessage(source.group_id, bindid(source.user_id, userid))
            return
        if source.raw_message == "不给看":
            if setprivate(source.user_id, 1):
                await app.sendGroupMessage(source.group_id, '不给看！')
            else:
                await app.sendGroupMessage(source.group_id, '你还没有绑定哦')
            return
        if source.raw_message == "给看":
            if setprivate(source.user_id, 0):
                await app.sendGroupMessage(source.group_id, '给看！')
            else:
                await app.sendGroupMessage(source.group_id, '你还没有绑定哦')
            return
        if source.raw_message[:2] == "逮捕":
            if source.raw_message == "逮捕":
                bind = getqqbind(source.user_id)
                if bind is None:
                    await app.sendGroupMessage(source.group_id, '查不到捏，可能是没绑定')
                    return
                loop = asyncio.get_event_loop()
                future = loop.run_in_executor(None, daibu, bind[1], bind[2])
                result = await future
                await app.sendGroupMessage(source.group_id, result)
            else:
                userid = source.raw_message.replace("逮捕", "")
                if '[CQ:at' in userid:
                    qq = re.sub(r'\D', "", userid)
                    bind = getqqbind(qq)
                    if bind is None:
                        await app.sendGroupMessage(source.group_id, '查不到捏，可能是没绑定')
                        return
                    elif bind[2] and qq != str(source.user_id):
                        await app.sendGroupMessage(source.group_id, '查不到捏，可能是不给看')
                        return
                    else:
                        loop = asyncio.get_event_loop()
                        future = loop.run_in_executor(None, daibu, bind[1], bind[2])
                        result = await future
                        await app.sendGroupMessage(source.group_id, result)
                        return
                userid = re.sub(r'\D', "", userid)
                if userid == '':
                    await app.sendGroupMessage(source.group_id, '你这id有问题啊')
                    return
                loop = asyncio.get_event_loop()
                if int(userid) > 10000000:
                    future = loop.run_in_executor(None, daibu, userid)
                else:
                    future = loop.run_in_executor(None, daibu, userid)
                result = await future
                await app.sendGroupMessage(source.group_id, result)
            return
        if source.raw_message == "pjsk进度":
            bind = getqqbind(source.user_id)
            if bind is None:
                await app.sendGroupMessage(source.group_id, '查不到捏，可能是没绑定')
                return
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, pjskjindu, bind[1], bind[2])
            await future
            await app.sendGroupMessage(source.group_id, [
                Plain(text=''),
                Image.fromFileSystem(fr"piccache\{bind[1]}jindu.png")
            ])
            return
        if source.raw_message == "pjsk b30":
            bind = getqqbind(source.user_id)
            if bind is None:
                await app.sendGroupMessage(source.group_id, '查不到捏，可能是没绑定')
                return
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, pjskb30, bind[1], bind[2])
            await future
            await app.sendGroupMessage(source.group_id, [
                Plain(text=''),
                Image.fromFileSystem(fr"piccache\{bind[1]}b30.png")
            ])
            return
        if source.raw_message == "热度排行":
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, hotrank)
            await future
            await app.sendGroupMessage(source.group_id, [
                Plain(text=''),
                Image.fromFileSystem(fr"piccache\hotrank.png")
            ])
            return
        if "难度排行" in source.raw_message:
            if source.raw_message[:2] == 'fc':
                fcap = 1
            elif source.raw_message[:2] == 'ap':
                fcap = 2
            else:
                fcap = 0
            para = source.raw_message[source.raw_message.find("难度排行") + len("难度排行"):].strip().split(" ")
            loop = asyncio.get_event_loop()
            if len(para) == 1:
                future = loop.run_in_executor(None, levelrank, int(para[0]), 'master', fcap)
            else:
                future = loop.run_in_executor(None, levelrank, int(para[0]), para[1], fcap)
            success = await future
            if success:
                if len(para) == 1:
                    await app.sendGroupMessage(source.group_id, [
                        Plain(text=''),
                        Image.fromFileSystem(fr"piccache\{para[0]}master{fcap}.png")
                    ])
                else:
                    await app.sendGroupMessage(source.group_id, [
                        Plain(text=''),
                        Image.fromFileSystem(fr"piccache\{para[0]}{para[1]}{fcap}.png")
                    ])
            else:
                await app.sendGroupMessage(source.group_id,
                                           '参数错误，指令：/难度排行 定数 难度，'
                                           '难度支持的输入: easy, normal, hard, expert, master，如/难度排行 28 expert')
            return
        if source.raw_message == "pjskprofile":
            bind = getqqbind(source.user_id)
            if bind is None:
                await app.sendGroupMessage(source.group_id, '查不到捏，可能是没绑定')
                return
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, pjskprofile, bind[1], bind[2])
            await future
            await app.sendGroupMessage(source.group_id, [
                Plain(text=''),
                Image.fromFileSystem(fr"piccache\{bind[1]}profile.png")
            ])
            return
        if source.raw_message[:7] == 'pjskbpm':
            resp = aliastomusicid(source.raw_message[7:])
            if resp['musicid'] == 0:
                await app.sendGroupMessage(source.group_id, '没有找到你要的歌曲哦')
                return
            else:
                bpm = parse_bpm(resp['musicid'])
                text = ''
                for bpms in bpm[1]:
                    text = text + ' - ' + str(bpms['bpm']).replace('.0', '')
                text = f"{resp['name']}\n匹配度:{round(resp['match'], 4)}\nBPM: " + text[3:]
                await app.sendGroupMessage(source.group_id, text)
            return
        if source.raw_message[:5] == "谱面预览2" or source.raw_message[-5:] == "谱面预览2":
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, aliastochart, source.raw_message.replace("谱面预览2", ''), True)
            dir = await future
            if dir is not None:  # 匹配到歌曲
                if len(dir) == 2:  # 有图片
                    await app.sendGroupMessage(source.group_id, [
                        Plain(text=dir[0]),
                        Image.fromFileSystem(dir[1])
                    ])
                else:
                    await app.sendGroupMessage(source.group_id, dir + "\n暂无谱面图片 请等待更新"
                                                                      "\n（温馨提示：谱面预览2只能看master与expert）")
            else:  # 匹配不到歌曲
                await app.sendGroupMessage(source.group_id, "没有找到你说的歌曲哦")
            return
        if source.raw_message[:4] == "谱面预览" or source.raw_message[-4:] == "谱面预览":
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, aliastochart, source.raw_message.replace("谱面预览", ''))
            dir = await future
            if dir is not None:  # 匹配到歌曲
                if len(dir) == 2:  # 有图片
                    await app.sendGroupMessage(source.group_id, [
                        Plain(text=dir[0]),
                        Image.fromFileSystem(dir[1])
                    ])
                else:
                    await app.sendGroupMessage(source.group_id, dir + "\n暂无谱面图片 请等待更新")
            else:  # 匹配不到歌曲
                await app.sendGroupMessage(source.group_id, "没有找到你说的歌曲哦")
            return
        if source.raw_message[:8] == 'charaset' and 'to' in source.raw_message:
            source.raw_message = source.raw_message[8:]
            para = source.raw_message.split('to')
            await app.sendGroupMessage(source.group_id, charaset(para[0], para[1], source.user_id))
            return
        if source.raw_message[:10] == 'grcharaset' and 'to' in source.raw_message:
            source.raw_message = source.raw_message[10:]
            para = source.raw_message.split('to')
            await app.sendGroupMessage(source.group_id, grcharaset(para[0], para[1], source.group_id))
            return
        if source.raw_message[:8] == 'charadel':
            source.raw_message = source.raw_message[8:]
            await app.sendGroupMessage(source.group_id, charadel(source.raw_message, source.user_id))
            return
        if source.raw_message[:10] == 'grcharadel':
            source.raw_message = source.raw_message[10:]
            await app.sendGroupMessage(source.group_id, grcharadel(source.raw_message, source.group_id))
            return
        if source.raw_message[:9] == 'charainfo':
            source.raw_message = source.raw_message[9:]
            await app.sendGroupMessage(source.group_id, charainfo(source.raw_message, source.group_id))
            return
        if source.raw_message == '推车':
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, ycmimg)
            await future
            await app.sendGroupMessage(source.group_id, [
                Plain(text=''),
                Image.fromFileSystem('piccache/ycm.jpg')
            ])
            return
        if source.raw_message[:3] == '查物量':
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, notecount, int(source.raw_message[3:]))
            text = await future
            await app.sendGroupMessage(source.group_id, text)
        if "查时间" in source.raw_message:
            userid = source.raw_message[source.raw_message.find("查时间") + len("查时间"):].strip()
            if userid == '':
                bind = getqqbind(source.user_id)
                if bind is None:
                    await app.sendGroupMessage(source.group_id, '你没有绑定id！')
                    return
                userid = bind[1]
            userid = re.sub(r'\D', "", userid)
            if userid == '':
                await app.sendGroupMessage(source.group_id, '你这id有问题啊')
                return
            if verifyid(userid):
                await app.sendGroupMessage(source.group_id, time.strftime('注册时间：%Y-%m-%d %H:%M:%S',
                                                                          time.localtime(gettime(userid))))
            else:
                await app.sendGroupMessage(source.group_id, '你这id有问题啊')
            return
        if source.raw_message[:2] == "生成":
            if source.group_id in blacklist[source.self_id]['ettm']:
                return
            source.raw_message = source.raw_message[source.raw_message.find("生成") + len("生成"):].strip()
            para = source.raw_message.split(" ")
            now = int(time.time() * 1000)
            if len(para) < 2:
                para = source.raw_message.split("/")
                if len(para) < 2:
                    await app.sendGroupMessage(source.group_id, '请求不对哦，/生成 这是红字 这是白字')
                    return
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, genImage, para[0], para[1])
            pic = await future
            pic.save(f"piccache/{now}.png")
            await app.sendGroupMessage(source.group_id, [
                Plain(text=''),
                Image.fromFileSystem(f'piccache/{now}.png')
            ])
            return
        if source.raw_message[:4] == 'homo':
            if source.self_id not in mainbot:
                return
            if source.group_id in blacklist[source.self_id]['ettm']:
                return
            source.raw_message = source.raw_message[source.raw_message.find("homo") + len("homo"):].strip()
            try:
                await app.sendGroupMessage(source.group_id,
                                           source.raw_message + '=' + generate_homo(source.raw_message))
            except ValueError:
                return
            return
        if source.raw_message[:3] == "ccf":
            if source.self_id not in mainbot:
                return
            source.raw_message = source.raw_message[source.raw_message.find("ccf") + len("ccf"):].strip()
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, dd_query.DDImageGenerate, source.raw_message)
            dd = await future
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(None, dd.image_generate)
            image_path, vtb_following_count, total_following_count = await future
            await app.sendGroupMessage(source.group_id, [
                Plain(text=f"{dd.username} 总共关注了 {total_following_count} 位up主, 其中 {vtb_following_count} 位是vtb。\n"
                           f"注意: 由于b站限制, bot最多只能拉取到最近250个关注。因此可能存在数据统计不全的问题。"),
                Image.fromFileSystem(image_path)
            ])
            return
        if source.raw_message[:5] == "白名单添加" and source.user_id in admin:
            source.raw_message = source.raw_message[source.raw_message.find("白名单添加") + len("白名单添加"):].strip()
            requestwhitelist.append(int(source.raw_message))
            await app.sendGroupMessage(source.group_id, '添加成功: ' + source.raw_message)
        if source.raw_message[:3] == "达成率":
            source.raw_message = source.raw_message[source.raw_message.find("达成率") + len("达成率"):].strip()
            para = source.raw_message.split(' ')
            if len(para) < 5:
                return
            await app.sendGroupMessage(source.group_id, tasseiritsu(para))
            return
        if source.raw_message == '看33':
            await app.sendGroupMessage(source.group_id, [
                Plain(text=''),
                Image.fromFileSystem(f'pics/33{random.randint(0, 1)}.gif')
            ])
        if source.raw_message[:2] == '机翻' and source.raw_message[-2:] == '推特':
            if source.self_id not in mainbot:
                return
            if '最新' in source.raw_message:
                source.raw_message = source.raw_message.replace('最新', '')
            twiid = source.raw_message[2:-2]
            try:
                loop = asyncio.get_event_loop()
                future = loop.run_in_executor(None, newesttwi, twiid, True)
                id = await future
                await app.sendGroupMessage(source.group_id, [
                    Plain(text=''),
                    Image.fromFileSystem(f'piccache/{id}.png')
                ])
            except:
                await app.sendGroupMessage(source.group_id, '查不到捏，可能是你id有问题或者bot卡了')
            return
        if source.raw_message[-4:] == '最新推特':
            if source.self_id not in mainbot:
                return
            try:
                loop = asyncio.get_event_loop()
                future = loop.run_in_executor(None, newesttwi, source.raw_message.replace('最新推特', '').replace(' ', ''))
                id = await future
                await app.sendGroupMessage(source.group_id, [
                    Plain(text=''),
                    Image.fromFileSystem(f'piccache/{id}.png')
                ])
            except:
                await app.sendGroupMessage(source.group_id, '查不到捏，可能是你id有问题或者bot卡了')
            return
        if source.raw_message == '关闭娱乐':
            info = await app.getGroupMemberInfo(source.group_id, source.user_id)
            if info.role == 'owner' or info.role == 'admin':
                if source.group_id in blacklist[source.self_id]['ettm']:  # 如果在黑名单
                    await app.sendGroupMessage(source.group_id, '已经关闭过了')
                    return
                blacklist[source.self_id]['ettm'].append(source.group_id)  # 加到黑名单
                with open('yamls/blacklist.yaml', "w") as f:
                    yaml.dump(blacklist, f)
                await app.sendGroupMessage(source.group_id, '关闭成功')
            else:
                await app.sendGroupMessage(source.group_id, '此命令需要群主或管理员权限')
            return
        if source.raw_message == '开启娱乐':
            info = await app.getGroupMemberInfo(source.group_id, source.user_id)
            if info.role == 'owner' or info.role == 'admin':
                if source.group_id not in blacklist[source.self_id]['ettm']:  # 如果不在黑名单
                    await app.sendGroupMessage(source.group_id, '已经开启过了')
                    return
                blacklist[source.self_id]['ettm'].remove(source.group_id)  # 从黑名单删除
                with open('yamls/blacklist.yaml', "w") as f:
                    yaml.dump(blacklist, f)
                await app.sendGroupMessage(source.group_id, '开启成功')
            else:
                await app.sendGroupMessage(source.group_id, '此命令需要群主或管理员权限')
            return
        if source.raw_message == '关闭sk':
            info = await app.getGroupMemberInfo(source.group_id, source.user_id)
            if info.role == 'owner' or info.role == 'admin':
                if source.group_id in blacklist[source.self_id]['sk']:  # 如果在黑名单
                    await app.sendGroupMessage(source.group_id, '已经关闭过了')
                    return
                blacklist[source.self_id]['sk'].append(source.group_id)  # 加到黑名单
                with open('yamls/blacklist.yaml', "w") as f:
                    yaml.dump(blacklist, f)
                await app.sendGroupMessage(source.group_id, '关闭成功')
            else:
                await app.sendGroupMessage(source.group_id, '此命令需要群主或管理员权限')
            return
        if source.raw_message == '开启sk':
            info = await app.getGroupMemberInfo(source.group_id, source.user_id)
            if info.role == 'owner' or info.role == 'admin':
                if source.group_id not in blacklist[source.self_id]['sk']:  # 如果不在黑名单
                    await app.sendGroupMessage(source.group_id, '已经开启过了')
                    return
                blacklist[source.self_id]['sk'].remove(source.group_id)  # 从黑名单删除
                with open('yamls/blacklist.yaml', "w") as f:
                    yaml.dump(blacklist, f)
                await app.sendGroupMessage(source.group_id, '开启成功')
            else:
                await app.sendGroupMessage(source.group_id, '此命令需要群主或管理员权限')
            return
        #
        # if source.raw_message[:1] == '看' or source.raw_message[:2] == '来点':
        #     source.raw_message = source.raw_message.replace('看', '')
        #     source.raw_message = source.raw_message.replace('来点', '')
        #     resp = aliastocharaid(source.raw_message, source.group_id)
        #     if resp[0] != 0:
        #         await app.sendGroupMessage(source.group_id, [
        #             Plain(text=''),
        #             Image.fromFileSystem(get_card(str(resp[0])))
        #         ])

        # 猜曲
        if source.raw_message[-2:] == '猜曲' and source.raw_message[:4] == 'pjsk':
            if source.user_id not in whitelist and source.group_id not in whitelist:
                return
            try:
                isgoing = charaguess[source.group_id]['isgoing']
                if isgoing:
                    await app.sendGroupMessage(source.group_id, '已经开启猜卡面！')
                    return
            except KeyError:
                pass

            try:
                isgoing = pjskguess[source.group_id]['isgoing']
                if isgoing:
                    await app.sendGroupMessage(source.group_id, '已经开启猜曲！')
                    return
                else:
                    musicid = getrandomjacket()
                    pjskguess[source.group_id] = {'isgoing': True, 'musicid': musicid, 'starttime': int(time.time())}
            except KeyError:
                musicid = getrandomjacket()
                pjskguess[source.group_id] = {'isgoing': True, 'musicid': musicid, 'starttime': int(time.time())}
            if source.raw_message == 'pjsk猜曲':
                cutjacket(musicid, source.group_id, size=140, isbw=False)
            elif source.raw_message == 'pjsk阴间猜曲':
                cutjacket(musicid, source.group_id, size=140, isbw=True)
            elif source.raw_message == 'pjsk非人类猜曲':
                cutjacket(musicid, source.group_id, size=30, isbw=False)
            await app.sendGroupMessage(source.group_id, [
                Plain(text='PJSK曲绘竞猜 （随机裁切）\n艾特我+你的答案以参加猜曲（不要使用回复）\n\n你有50秒的时间回答\n可手动发送“结束猜曲”来结束猜曲'),
                Image.fromFileSystem(f'piccache/{source.group_id}.png')
            ])
            return
        if source.raw_message == 'pjsk猜谱面':
            if source.user_id not in whitelist and source.group_id not in whitelist:
                return
            try:
                isgoing = charaguess[source.group_id]['isgoing']
                if isgoing:
                    await app.sendGroupMessage(source.group_id, '已经开启猜卡面！')
                    return
            except KeyError:
                pass

            try:
                isgoing = pjskguess[source.group_id]['isgoing']
                if isgoing:
                    await app.sendGroupMessage(source.group_id, '已经开启猜曲！')
                    return
                else:
                    musicid = getrandomchart()
                    pjskguess[source.group_id] = {'isgoing': True, 'musicid': musicid, 'starttime': int(time.time())}
            except KeyError:
                musicid = getrandomchart()
                pjskguess[source.group_id] = {'isgoing': True, 'musicid': musicid, 'starttime': int(time.time())}
            cutchartimg(musicid, source.group_id)
            await app.sendGroupMessage(source.group_id, [
                Plain(text='PJSK谱面竞猜（随机裁切）\n艾特我+你的答案以参加猜曲（不要使用回复）\n\n你有50秒的时间回答\n可手动发送“结束猜曲”来结束猜曲'),
                Image.fromFileSystem(f'piccache/{source.group_id}.png')
            ])
            return
        if source.raw_message == 'pjsk猜卡面':
            if source.user_id not in whitelist and source.group_id not in whitelist:
                return
            try:
                isgoing = pjskguess[source.group_id]['isgoing']
                if isgoing:
                    await app.sendGroupMessage(source.group_id, '已经开启猜曲！')
                    return
            except KeyError:
                pass
            # getrandomcard() return characterId, assetbundleName, prefix, cardRarityType
            try:
                isgoing = charaguess[source.group_id]['isgoing']
                if isgoing:
                    await app.sendGroupMessage(source.group_id, '已经开启猜曲！')
                    return
                else:
                    cardinfo = getrandomcard()
                    charaguess[source.group_id] = {'isgoing': True, 'charaid': cardinfo[0],
                                                   'assetbundleName': cardinfo[1], 'prefix': cardinfo[2],
                                                   'starttime': int(time.time())}
            except KeyError:
                cardinfo = getrandomcard()
                charaguess[source.group_id] = {'isgoing': True, 'charaid': cardinfo[0], 'assetbundleName': cardinfo[1],
                                               'prefix': cardinfo[2], 'starttime': int(time.time())}

            charaguess[source.group_id]['istrained'] = cutcard(cardinfo[1], cardinfo[3], source.group_id)
            await app.sendGroupMessage(source.group_id, [
                Plain(text='PJSK猜卡面\n你有30秒的时间回答\n艾特我+你的答案（只猜角色）以参加猜曲（不要使用回复）\n发送「结束猜卡面」可退出猜卡面模式'),
                Image.fromFileSystem(f'piccache/{source.group_id}.png')
            ])
            print(charaguess)
            return
        if source.raw_message == '结束猜曲':
            try:
                isgoing = pjskguess[source.group_id]['isgoing']
                if isgoing:
                    dir = f"data/assets/sekai/assetbundle/resources/startapp/music/jacket/" \
                          f"jacket_s_{str(pjskguess[source.group_id]['musicid']).zfill(3)}/" \
                          f"jacket_s_{str(pjskguess[source.group_id]['musicid']).zfill(3)}.png"
                    text = '正确答案：' + idtoname(pjskguess[source.group_id]['musicid'])
                    pjskguess[source.group_id]['isgoing'] = False
                    await app.sendGroupMessage(source.group_id, [
                        Plain(text=text),
                        Image.fromFileSystem(dir)
                    ])
            except KeyError:
                pass
            return
        if source.raw_message == '结束猜卡面':
            try:
                isgoing = charaguess[source.group_id]['isgoing']
                if isgoing:
                    if charaguess[source.group_id]['istrained']:
                        dir = 'data/assets/sekai/assetbundle/resources/startapp/' \
                              f"character/member/{charaguess[source.group_id]['assetbundleName']}/card_after_training.jpg"
                    else:
                        dir = 'data/assets/sekai/assetbundle/resources/startapp/' \
                              f"character/member/{charaguess[source.group_id]['assetbundleName']}/card_normal.jpg"
                    text = f"正确答案：{charaguess[source.group_id]['prefix']} - {getcharaname(charaguess[source.group_id]['charaid'])}"
                    charaguess[source.group_id]['isgoing'] = False

                    await app.sendGroupMessage(source.group_id, [
                        Plain(text=text),
                        Image.fromFileSystem(dir)
                    ])
            except KeyError:
                pass
            return
        # 判断艾特自己
        if f'[CQ:at,qq={source.self_id}]' in source.raw_message:
            # 判断有没有猜曲
            try:
                isgoing = pjskguess[source.group_id]['isgoing']
                if isgoing:
                    answer = source.raw_message[source.raw_message.find("]") + len("]"):].strip()
                    resp = aliastomusicid(answer)
                    if resp['musicid'] == 0:
                        await app.sendGroupMessage(source.group_id, '没有找到你说的歌曲哦')
                        return
                    else:
                        if resp['musicid'] == pjskguess[source.group_id]['musicid']:
                            text = f'[CQ:at,qq={source.user_id}] 您猜对了'
                            if int(time.time()) > pjskguess[source.group_id]['starttime'] + 45:
                                text = text + '，回答已超时'
                            dir = f"data/assets/sekai/assetbundle/resources/startapp/music/jacket/" \
                                  f"jacket_s_{str(pjskguess[source.group_id]['musicid']).zfill(3)}/" \
                                  f"jacket_s_{str(pjskguess[source.group_id]['musicid']).zfill(3)}.png"
                            text = text + '\n正确答案：' + idtoname(pjskguess[source.group_id]['musicid'])
                            pjskguess[source.group_id]['isgoing'] = False
                            await app.sendGroupMessage(source.group_id, [
                                Plain(text=text),
                                Image.fromFileSystem(dir)
                            ])
                        else:
                            await app.sendGroupMessage(source.group_id,
                                                       f"[CQ:at,qq={source.user_id}] 您猜错了，答案不是{idtoname(resp['musicid'])}哦")
            except KeyError:
                pass

            # 判断有没有猜卡面
            try:
                isgoing = charaguess[source.group_id]['isgoing']
                if isgoing:
                    # {'isgoing', 'charaid', 'assetbundleName', 'prefix', 'starttime'}
                    answer = source.raw_message[source.raw_message.find("]") + len("]"):].strip()
                    resp = aliastocharaid(answer)
                    if resp[0] == 0:
                        await app.sendGroupMessage(source.group_id, '没有找到你说的角色哦')
                        return
                    else:
                        if resp[0] == charaguess[source.group_id]['charaid']:
                            text = f'[CQ:at,qq={source.user_id}] 您猜对了'
                            if int(time.time()) > charaguess[source.group_id]['starttime'] + 45:
                                text = text + '，回答已超时'
                            if charaguess[source.group_id]['istrained']:
                                dir = 'data/assets/sekai/assetbundle/resources/startapp/' \
                                      f"character/member/{charaguess[source.group_id]['assetbundleName']}/card_after_training.jpg"
                            else:
                                dir = 'data/assets/sekai/assetbundle/resources/startapp/' \
                                      f"character/member/{charaguess[source.group_id]['assetbundleName']}/card_normal.jpg"
                            text = text + f"\n正确答案：{charaguess[source.group_id]['prefix']} - {resp[1]}"
                            charaguess[source.group_id]['isgoing'] = False
                            await app.sendGroupMessage(source.group_id, [
                                Plain(text=text),
                                Image.fromFileSystem(dir)
                            ])
                        else:
                            await app.sendGroupMessage(source.group_id,
                                                       f"[CQ:at,qq={source.user_id}] 您猜错了，答案不是{resp[1]}哦")

            except KeyError:
                pass

    except requests.exceptions.ConnectionError:
        await app.sendGroupMessage(source.group_id, r'查不到数据捏，好像是bot网不好')
    except Exception as a:
        traceback.print_exc()
        await app.sendGroupMessage(source.group_id, '出问题了捏\n' + repr(a))


@unibot.receiver('GroupMemberIncrease')  # 群人数增加事件
async def _(app: CQHTTP, source: GroupMemberIncrease):
    if source.user_id == source.self_id:  # 自己被邀请进群
        if source.group_id in requestwhitelist:
            await app.sendGroupMessage(msggroup, f'我已加入群{source.group_id}')
        else:
            await app.sendGroupMessage(source.group_id, '加群过多，现开启白名单机制，请进群883721511私聊群主，仅接受坑内相关大群请求。已自动退群')
            await app.leave(source.group_id)
            await app.sendGroupMessage(msggroup, f'有人邀请我加入群{source.group_id}，已自动退群')

@unibot.receiver('GroupRequest')  # 加群请求或被拉群
async def _(app: CQHTTP, source: GroupRequest):
    if source.sub_type == 'invite':  # 被邀请加群
        if source.group_id in requestwhitelist:
            await app.setGroupRequest(source.flag, source.sub_type, True)
            await app.sendGroupMessage(msggroup, f'{source.user_id}邀请我加入群{source.group_id}，已自动同意')
        else:
            await app.setGroupRequest(source.flag, source.sub_type, False)
            await app.sendGroupMessage(msggroup, f'{source.user_id}邀请我加入群{source.group_id}，已自动拒绝')
    elif source.sub_type == 'add':  # 有人加群
        if source.group_id == 883721511 or source.group_id == 647347636:
            answer = source.comment[source.comment.find("答案：") + len("答案："):].strip()
            answer = re.sub(r'\D', "", answer)
            async with aiofiles.open('masterdata/musics.json', 'r', encoding='utf-8') as f:
                contents = await f.read()
            musics = json.loads(contents)
            now = time.time()*1000
            count = 0
            for music in musics:
                if music['publishedAt'] < now:
                    count += 1
            print(count)
            if count-5 < int(answer) < count+5:
                await app.setGroupRequest(source.flag, source.sub_type, True)
                await app.sendGroupMessage(source.group_id, f'{source.user_id}申请加群\n{source.comment}\n误差<5，已自动通过')
            else:
                await app.setGroupRequest(source.flag, source.sub_type, False, '回答错误，请认真回答(使用阿拉伯数字)')
                await app.sendGroupMessage(source.group_id, f'{source.user_id}申请加群\n{source.comment}\n误差>5，已自动拒绝')
        elif source.group_id == 467602419:
            answer = source.comment[source.comment.find("答案：") + len("答案："):].strip()
            if 'Mrs4s/go-cqhttp' in answer:
                await app.setGroupRequest(source.flag, source.sub_type, True)
                await app.sendGroupMessage(source.group_id, f'{source.user_id}申请加群\n{source.comment}\n已自动通过')
            else:
                await app.sendGroupMessage(source.group_id, f'[CQ:at,qq=1103479519]{source.user_id}申请加群\n{source.comment}\n，无法判定')

@unibot.receiver('GroupMemberBan')  # 群成员被禁言
async def _(app: CQHTTP, source: GroupMemberBan):
    if source.user_id == source.self_id:
        await app.leave(source.group_id)
        await app.sendGroupMessage(msggroup, f'我在群{source.group_id}内被{source.operator_id}禁言{source.duration/60}分钟，已自动退群')


with open('yamls/blacklist.yaml', "r") as f:
    blacklist = yaml.load(f, Loader=yaml.FullLoader)
unibot.run()
