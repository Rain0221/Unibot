import os
import json
import random
from datetime import datetime
from json import JSONDecodeError
import asyncio
import aiocqhttp
import aiofiles
import aiohttp
import requests
import re
import time
import traceback
import yaml
from aiocqhttp import CQHttp, Event
from chachengfen import dd_query
from modules.api import gacha
from modules.chara import charaset, grcharaset, charadel, charainfo, grcharadel, aliastocharaid, get_card, cardidtopic, \
    findcard, getvits
from modules.config import whitelist, block, msggroup, aliasblock, groupban, asseturl, verifyurl, distributedurl, apiurl
from modules.cyo5000 import cyo5000
from modules.kk import kkwhitelist, kankan, uploadkk
from modules.opencv import matchjacket
from modules.otherpics import geteventpic
from modules.gacha import getcharaname, getallcurrentgacha, getcurrentgacha, fakegacha
from modules.homo import generate_homo
from modules.musics import hotrank, levelrank, parse_bpm, aliastochart, idtoname, notecount, tasseiritsu, findbpm, \
    getcharttheme, setcharttheme
from modules.pjskguess import getrandomjacket, cutjacket, getrandomchart, cutchartimg, getrandomcard, cutcard, \
    getrandommusic, cutmusic
from modules.pjskinfo import aliastomusicid, pjskset, pjskdel, pjskalias, pjskinfo, writelog
from modules.profileanalysis import daibu, rk, pjskjindu, pjskprofile, pjskb30, r30
from modules.sendmail import sendemail
from modules.sk import sk, getqqbind, bindid, setprivate, skyc, verifyid, gettime, teamcount, currentevent, chafang, \
    getstoptime, ss, drawscoreline
from modules.texttoimg import texttoimg, ycmimg
from modules.twitter import newesttwi
from apscheduler.schedulers.asyncio import AsyncIOScheduler

if os.path.basename(__file__) == 'bot.py':
    bot = CQHttp()
    botdebug = False
else:
    guildhttpport = 1988
    bot = CQHttp(api_root=f'http://127.0.0.1:{guildhttpport}')
    botdebug = True
botdir = os.getcwd()

pjskguess = {}
charaguess = {}
ciyunlimit = {}
groupaudit = {}
gachalimit = {'lasttime': '', 'count': 0}
pokelimit = {'lasttime': '', 'count': 0}
vitslimit = {'lasttime': '', 'count': 0}
admin = [1103479519]
mainbot = [1513705608]
requestwhitelist = []  # 邀请加群白名单 随时设置 不保存到文件

botname = {
    1513705608: '一号机',
    3506606538: '三号机',
    "9892212940143267151": '频道bot'
}
guildbot = "9892212940143267151"
send1 = False
send3 = False
opencvmatch = False

async def geturl(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            print(res.status)
            text = await res.text()
            return text

@bot.on_message('group')
async def handle_msg(event: Event):
    if event.self_id == guildbot:
        return
    global blacklist
    global botdebug
    if event.user_id in block:
        # print('黑名单成员已拦截')
        return
    if event.message == '/delete unibot':
        info = await bot.get_group_member_info(self_id=event.self_id, group_id=event.group_id, user_id=event.user_id)
        if info['role'] == 'owner' or info['role'] == 'admin':
            await bot.send(event, 'Bye~')
            await bot.set_group_leave(self_id=event.self_id, group_id=event.group_id)
        else:
            await bot.send(event, '你没有权限，该命令需要群主/管理员')
    if event.raw_message == '关闭娱乐':
        info = await bot.get_group_member_info(self_id=event.self_id, group_id=event.group_id, user_id=event.user_id)
        if info['role'] == 'owner' or info['role'] == 'admin':
            if event.group_id in blacklist['ettm']:  # 如果在黑名单
                await bot.send(event, '已经关闭过了')
                return
            blacklist['ettm'].append(event.group_id)  # 加到黑名单
            with open('yamls/blacklist.yaml', "w") as f:
                yaml.dump(blacklist, f)
            await bot.send(event, '关闭成功')
        else:
            await bot.send(event, '此命令需要群主或管理员权限')
        return
    if event.raw_message == '开启娱乐':
        info = await bot.get_group_member_info(self_id=event.self_id, group_id=event.group_id, user_id=event.user_id)
        if info['role'] == 'owner' or info['role'] == 'admin':
            if event.group_id not in blacklist['ettm']:  # 如果不在黑名单
                await bot.send(event, '已经开启过了')
                return
            blacklist['ettm'].remove(event.group_id)  # 从黑名单删除
            with open('yamls/blacklist.yaml', "w") as f:
                yaml.dump(blacklist, f)
            await bot.send(event, '开启成功')
        else:
            await bot.send(event, '此命令需要群主或管理员权限')
        return
    if event.raw_message == '关闭sk':
        info = await bot.get_group_member_info(self_id=event.self_id, group_id=event.group_id, user_id=event.user_id)
        if info['role'] == 'owner' or info['role'] == 'admin':
            if event.group_id in blacklist['sk']:  # 如果在黑名单
                await bot.send(event, '已经关闭过了')
                return
            blacklist['sk'].append(event.group_id)  # 加到黑名单
            with open('yamls/blacklist.yaml', "w") as f:
                yaml.dump(blacklist, f)
            await bot.send(event, '关闭成功')
        else:
            await bot.send(event, '此命令需要群主或管理员权限')
        return
    if event.raw_message == '开启sk':
        info = await bot.get_group_member_info(self_id=event.self_id, group_id=event.group_id, user_id=event.user_id)
        if info['role'] == 'owner' or info['role'] == 'admin':
            if event.group_id not in blacklist['sk']:  # 如果不在黑名单
                await bot.send(event, '已经开启过了')
                return
            blacklist['sk'].remove(event.group_id)  # 从黑名单删除
            with open('yamls/blacklist.yaml', "w") as f:
                yaml.dump(blacklist, f)
            await bot.send(event, '开启成功')
        else:
            await bot.send(event, '此命令需要群主或管理员权限')
        return
    if event.raw_message == '开启debug' and event.user_id in admin:
        botdebug = True
        await bot.send(event, '开启成功')
    if event.raw_message == '关闭debug' and event.user_id in admin:
        botdebug = False
        await bot.send(event, '关闭成功')
    if event.raw_message[:6] == 'verify' and event.group_id == 467602419 and event.self_id in mainbot:
        verify = event.message[event.message.find("verify") + len("verify"):].strip()
        resp = await geturl(f'{verifyurl}verify?qq={event.user_id}&verify={verify}')
        if resp == 'token验证成功':
            await geturl(f'{distributedurl}refresh')
        await bot.send(event, resp)
    if event.message[:5] == '/vits':
        if event.self_id not in mainbot:
            return
        global vitslimit
        nowtime = f"{str(datetime.now().hour).zfill(2)}{str(datetime.now().minute).zfill(2)}"
        lasttime = vitslimit['lasttime']
        count = vitslimit['count']
        if nowtime == lasttime and count >= 7:
            print(vitslimit)
            await bot.send(event, '达到每分钟调用上限')
            return
        if nowtime != lasttime:
            count = 0
        vitslimit['lasttime'] = nowtime
        vitslimit['count'] = count + 1
        print(vitslimit)
        para = event.message[event.message.find("/vits") + len("/vits"):].strip().split(' ')
        wavdir = await getvits(para[0], para[1])
        if wavdir[0]:
            await bot.send(event, fr"[CQ:record,file={wavdir[1]},cache=0]")
        else:
            if wavdir[1] != '':
                await bot.send(event, wavdir[1])
            else:
                await bot.send(event, '疑似内存占用太高自动结束了')
        return

@bot.on_message('group')
def sync_handle_msg(event):
    if event.self_id == guildbot:
        event.message = event.message[event.message.find(f"qq={guildbot}") + len(f"qq={guildbot}]"):].strip()
    global pjskguess
    global charaguess
    global ciyunlimit
    global gachalimit
    global blacklist
    global requestwhitelist
    if botdebug:
        timeArray = time.localtime(time.time())
        Time = time.strftime("[%Y-%m-%d %H:%M:%S]", timeArray)
        try:
            print(Time, botname[event.self_id] + '收到消息', event.group_id, event.user_id, event.message.replace('\n', ''))
        except KeyError:
            print(Time, '测试bot收到消息', event.group_id, event.user_id, event.message.replace('\n', ''))
    if event.group_id in groupban and event.self_id in mainbot:
        # print('黑名单群已拦截')
        return
    if event.user_id in block:
        # print('黑名单成员已拦截')
        return
    if event.message[0:1] == '/':
        event.message = event.message[1:]
    try:
        # -----------------------功能测试-----------------------------
        # if event.message == 'test':
        #     sendmsg(event, event.sender['nickname'] + event.sender['card'])
        # -----------------------结束测试-----------------------------
        if event.message == 'help':
            if event.self_id == guildbot:
                sendmsg(event, 'bot帮助文档：https://docs.unipjsk.com/guild/')
            else:
                sendmsg(event, 'bot帮助文档：https://docs.unipjsk.com/')
            return
        if event.message[:8] == 'pjskinfo' or event.message[:4] == 'song':
            if event.message[:8] == 'pjskinfo':
                resp = aliastomusicid(event.message[event.message.find("pjskinfo") + len("pjskinfo"):].strip())
            else:
                resp = aliastomusicid(event.message[event.message.find("song") + len("song"):].strip())
            if resp['musicid'] == 0:
                sendmsg(event, '没有找到你要的歌曲哦')
                return
            else:
                leak = pjskinfo(resp['musicid'])
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
                sendmsg(event,
                        text + fr"[CQ:image,file=file:///{botdir}\piccache\pjskinfo\{resp['musicid']}.png,cache=0]")
            return
        if event.message[:7] == 'pjskset' and 'to' in event.message:
            if event.user_id in aliasblock:
                sendmsg(event, '你因乱设置昵称已无法使用此功能')
                return
            event.message = event.message[7:]
            para = event.message.split('to')
            if event.sender['card'] == '':
                username = event.sender['nickname']
            else:
                username = event.sender['card']
            if event.self_id == guildbot:
                resp = requests.get(f'http://127.0.0.1:{guildhttpport}/get_guild_info?guild_id={event.guild_id}')
                qun = resp.json()
                resp = pjskset(para[0], para[1], event.user_id, username, f"{qun['name']}({event.guild_id})内")
                sendmsg(event, resp)
            else:
                qun = bot.sync.get_group_info(self_id=event.self_id, group_id=event.group_id)
                resp = pjskset(para[0], para[1], event.user_id, username, f"{qun['group_name']}({event.group_id})内")
                sendmsg(event, resp)
            return
        if event.message[:7] == 'pjskdel':
            if event.user_id in aliasblock:
                sendmsg(event, '你因乱设置昵称已无法使用此功能')
                return
            event.message = event.message[7:]
            if event.sender['card'] == '':
                username = event.sender['nickname']
            else:
                username = event.sender['card']
            if event.self_id == guildbot:
                resp = requests.get(f'http://127.0.0.1:{guildhttpport}/get_guild_info?guild_id={event.guild_id}')
                qun = resp.json()
                resp = pjskdel(event.message, event.user_id, username, f"{qun['name']}({event.guild_id})内")
                sendmsg(event, resp)
            else:
                qun = bot.sync.get_group_info(self_id=event.self_id, group_id=event.group_id)
                resp = pjskdel(event.message, event.user_id, username, f"{qun['group_name']}({event.group_id})内")
                sendmsg(event, resp)
            return
        if event.message[:9] == 'pjskalias':
            event.message = event.message[9:]
            resp = pjskalias(event.message)
            sendmsg(event, resp)
            return
        if event.message == '词云' and event.self_id in mainbot:
            sendmsg(event, '发送 /今日词云、/昨日词云、/本周词云、/本月词云、/年度词云 或 /历史词云 即可获取词云。\n'
                           '如果想获取自己的词云，可在上述指令前添加 我的，如 /我的今日词云')
            return
        if event.message[:8] == "sekai真抽卡":
            if event.self_id not in mainbot:
                return
            if event.group_id in blacklist['ettm']:
                return
            if event.user_id not in whitelist and event.group_id not in whitelist and event.self_id != guildbot:
                nowtime = f"{str(datetime.now().hour).zfill(2)}{str(datetime.now().minute).zfill(2)}"
                lasttime = gachalimit['lasttime']
                count = gachalimit['count']
                if nowtime == lasttime and count >= 2:
                    sendmsg(event, f'技能冷却中，剩余cd:{60 - datetime.now().second}秒（一分钟内所有群只能抽两次）')
                    return
                if nowtime != lasttime:
                    count = 0
                gachalimit['lasttime'] = nowtime
                gachalimit['count'] = count + 1
            sendmsg(event, '了解')
            gachaid = event.message[event.message.find("sekai真抽卡") + len("sekai真抽卡"):].strip()
            if gachaid == '':
                result = gacha()
            else:
                currentgacha = getallcurrentgacha()
                targetgacha = None
                for gachas in currentgacha:
                    if int(gachas['id']) == int(gachaid):
                        targetgacha = gachas
                        break
                if targetgacha is None:
                    sendmsg(event, '你指定的id现在无法完成无偿十连')
                    return
                else:
                    result = gacha(targetgacha)
            sendmsg(event, result)
            return
        if event.message == "时速":
            texttoimg(ss(), 300, 'ss')
            sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\ss.png,cache=0]")
            return
        if event.message == "sk预测":
            texttoimg(skyc(), 500, 'skyc')
            sendmsg(event, 'sk预测' + fr"[CQ:image,file=file:///{botdir}\piccache\skyc.png,cache=0]")
            return
        elif event.message[:8] == 'findcard':
            event.message = event.message[event.message.find("findcard") + len("findcard"):].strip()
            para = event.message.split(' ')
            resp = aliastocharaid(para[0], event.group_id)
            if resp[0] != 0:
                if len(para) == 1:
                    sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\{findcard(resp[0], None)},cache=0]")
                elif len(para) == 2:
                    if para[1] == '一星' or para[1] == '1':
                        sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\{findcard(resp[0], 'rarity_1')},cache=0]")
                    elif para[1] == '二星' or para[1] == '2':
                        sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\{findcard(resp[0], 'rarity_2')},cache=0]")
                    elif para[1] == '三星' or para[1] == '3':
                        sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\{findcard(resp[0], 'rarity_3')},cache=0]")
                    elif para[1] == '四星' or para[1] == '4':
                        sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\{findcard(resp[0], 'rarity_4')},cache=0]")
                    elif '生日' in para[1] or 'birthday' in para[1]:
                        sendmsg(event,
                                fr"[CQ:image,file=file:///{botdir}\piccache\{findcard(resp[0], 'rarity_birthday')},cache=0]")
                    else:
                        sendmsg(event, '命令不正确')
            else:
                sendmsg(event, '找不到你说的角色哦')
            return
        # ---------------------- 服务器判断 -------------------------
        server = 'jp'
        if event.message[:2] == "jp":
            event.message = event.message[2:]
        if event.message[:2] == "tw":
            event.message = event.message[2:]
            server = 'tw'
        elif event.message[:2] == "en":
            event.message = event.message[2:]
            server = 'en'
        # -------------------- 多服共用功能区 -----------------------
        if event.message[:2] == "sk":
            if event.group_id in blacklist['sk'] and server == 'jp':
                return
            if event.message == "sk":
                bind = getqqbind(event.user_id, server)
                if bind is None:
                    sendmsg(event, '你没有绑定id！')
                    return
                result = sk(bind[1], None, bind[2], server, False, event.user_id, True)
                if 'piccache' in result:
                    sendmsg(event, fr"[CQ:image,file=file:///{botdir}\{result},cache=0]")
                else:
                    sendmsg(event, result)
            else:
                event.message = event.message[event.message.find("sk") + len("sk"):].strip()
                userids = event.message.split(' ')
                if len(userids) > 8:
                    sendmsg(event, '少查一点吧')
                    return
                if len(userids) == 1:
                    userid = re.sub(r'\D', "", event.message)
                    if userid == '':
                        sendmsg(event, '你这id有问题啊')
                        return
                    if int(userid) > 10000000:
                        result = sk(userid, None, False, server, False, event.user_id, True)
                    else:
                        result = sk(None, userid, True, server, False, event.user_id, True)
                    if 'piccache' in result:
                        sendmsg(event, fr"[CQ:image,file=file:///{botdir}\{result},cache=0]")
                    else:
                        sendmsg(event, result)
                    return
                else:
                    result = ''
                    for userid in userids:
                        userid = re.sub(r'\D', "", userid)
                        if userid == '':
                            sendmsg(event, '你这id有问题啊')
                            return
                        if int(userid) > 10000000:
                            result += sk(userid, None, False, server, True, event.user_id)
                        else:
                            result += sk(None, userid, True, server, True, event.user_id)
                        result += '\n\n'
                    sendmsg(event, result[:-2])
                    return
        if event.message[:2] == "绑定":
            userid = event.message.replace("绑定", "")
            userid = re.sub(r'\D', "", userid)
            sendmsg(event, bindid(event.user_id, userid, server))
            return
        if event.message == "不给看":
            if setprivate(event.user_id, 1, server):
                sendmsg(event, '不给看！')
            else:
                sendmsg(event, '你还没有绑定哦')
            return
        if event.message == "给看":
            if setprivate(event.user_id, 0, server):
                sendmsg(event, '给看！')
            else:
                sendmsg(event, '你还没有绑定哦')
            return
        if event.message[:2] == "逮捕":
            if event.group_id in blacklist['sk'] and server == 'jp':
                return
            if event.message == "逮捕":
                bind = getqqbind(event.user_id, server)
                if bind is None:
                    sendmsg(event, '查不到捏，可能是没绑定')
                    return
                result = daibu(bind[1], bind[2], server, event.user_id)
                sendmsg(event, result)
            else:
                userid = event.message.replace("逮捕", "")
                if '[CQ:at' in userid:
                    qq = re.sub(r'\D', "", userid)
                    bind = getqqbind(qq, server)
                    if bind is None:
                        sendmsg(event, '查不到捏，可能是没绑定')
                        return
                    elif bind[2] and qq != str(event.user_id):
                        sendmsg(event, '查不到捏，可能是不给看')
                        return
                    else:
                        result = daibu(bind[1], bind[2], server, event.user_id)
                        sendmsg(event, result)
                        return
                userid = re.sub(r'\D', "", userid)
                if userid == '':
                    sendmsg(event, '你这id有问题啊')
                    return
                if int(userid) > 10000000:
                    result = daibu(userid, False, server, event.user_id)
                else:
                    result = daibu(userid, False, server, event.user_id)
                sendmsg(event, result)
            return
        if event.message == "pjsk进度":
            bind = getqqbind(event.user_id, server)
            if bind is None:
                sendmsg(event, '查不到捏，可能是没绑定')
                return
            pjskjindu(bind[1], bind[2], 'master', server, event.user_id)
            sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\{bind[1]}jindu.png,cache=0]")
            return
        if event.message == "pjsk进度ex":
            bind = getqqbind(event.user_id, server)
            if bind is None:
                sendmsg(event, '查不到捏，可能是没绑定')
                return
            pjskjindu(bind[1], bind[2], 'expert', server, event.user_id)
            sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\{bind[1]}jindu.png,cache=0]")
            return
        if event.message == "pjsk b30":
            bind = getqqbind(event.user_id, server)
            if bind is None:
                sendmsg(event, '查不到捏，可能是没绑定')
                return
            pjskb30(bind[1], bind[2], False, server, event.user_id)
            sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\{bind[1]}b30.png,cache=0]")
            return
        if event.message.startswith("pjsk r30"):
            if event.user_id not in whitelist and event.group_id not in whitelist:
                return
            if event.message == "pjsk r30":
                bind = getqqbind(event.user_id, server)
                if bind is None:
                    sendmsg(event, '查不到捏，可能是没绑定')
                    return
                sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\{r30(bind[1], bind[2], server, event.user_id)}.png,cache=0]")
            else:
                userid = event.message[event.message.find("pjsk r30") + len("pjsk r30"):].strip()
                sendmsg(event,
                        fr"[CQ:image,file=file:///{botdir}\piccache\{r30(userid, False, server, event.user_id)}.png,cache=0]")
            return
        if event.message == "pjskprofile" or event.message == "个人信息":
            bind = getqqbind(event.user_id, server)
            if bind is None:
                sendmsg(event, '查不到捏，可能是没绑定')
                return
            pjskprofile(bind[1], bind[2], server, event.user_id)
            sendmsg(event, f"[CQ:image,file=file:///{botdir}/piccache/{bind[1]}profile.jpg,cache=0]")
            return

        # ----------------------- 恢复原命令 ---------------------------
        if server == 'tw' or server == 'en':
            event.message = server + event.message
        # -------------------- 结束多服共用功能区 -----------------------
        if event.message[:2] == "查房" or event.message[:2] == "cf":
            if event.group_id in blacklist['sk'] and event.message[:2] == "查房":
                return
            if event.message[:2] == "cf":
                event.message = '查房' + event.message[2:]
            private = False
            if event.message == "查房":
                bind = getqqbind(event.user_id, 'jp')
                if bind is None:
                    sendmsg(event, '你没有绑定id！')
                    return
                userid = bind[1]
                private = bind[2]
            else:
                userid = event.message.replace("查房", "")
                userid = re.sub(r'\D', "", userid)
            if userid == '':
                sendmsg(event, '你这id有问题啊')
                return
            if int(userid) > 10000000:
                result = chafang(userid, None, private)
            else:
                result = chafang(None, userid)
            sendmsg(event, result)
            return
        graphstart = 0
        if event.message[:4] == '24小时':
            graphstart = time.time() - 60 * 60 * 24
            event.message = event.message[4:]
        if event.message[:3] == "分数线":
            if event.message == "分数线":
                bind = getqqbind(event.user_id, 'jp')
                if bind is None:
                    sendmsg(event, '你没有绑定id！')
                    return
                userid = bind[1]
            else:
                userid = event.message.replace("分数线", "")
            if userid == '':
                sendmsg(event, '你这id有问题啊')
                return
            userids = userid.split(' ')
            if len(userids) == 1:
                userid = re.sub(r'\D', "", userid)
                if int(userid) > 10000000:
                    result = drawscoreline(userid, None, None, graphstart)
                else:
                    result = drawscoreline(None, userid, None, graphstart)
                if result:
                    sendmsg(event, fr"[CQ:image,file=file:///{botdir}\{result},cache=0]")
                else:
                    sendmsg(event, "你要查询的玩家未进入前200，暂无数据")
                return
            else:
                result = drawscoreline(None, userids[0], userids[1], graphstart)
                if result:
                    sendmsg(event, fr"[CQ:image,file=file:///{botdir}\{result},cache=0]")
                else:
                    sendmsg(event, "你要查询的玩家未进入前200，暂无数据")
                return
        if event.message[:3] == "查水表" or event.message[:3] == "csb":
            if event.group_id in blacklist['sk'] and event.message[:3] == "查水表":
                return
            if event.message[:3] == "csb":
                event.message = '查水表' + event.message[3:]
            private = False
            if event.message == "查水表":
                bind = getqqbind(event.user_id, 'jp')
                if bind is None:
                    sendmsg(event, '你没有绑定id！')
                    return
                userid = bind[1]
                private = bind[2]
            else:
                userid = event.message.replace("查水表", "")
                userid = re.sub(r'\D', "", userid)
            if userid == '':
                sendmsg(event, '你这id有问题啊')
                return
            if int(userid) > 10000000:
                result = getstoptime(userid, None, False, private)
            else:
                result = getstoptime(None, userid)
            if result:
                texttoimg(result, 500, f'csb{userid}')
                sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\csb{userid}.png,cache=0]")
            else:
                sendmsg(event, "你要查询的玩家未进入前200，暂无数据")
            return
        if event.message == '5v5人数':
            sendmsg(event, teamcount())
        if event.message[:5] == 'event':
            eventid = event.message[event.message.find("event") + len("event"):].strip()
            eventid = re.sub(r'\D', "", eventid)
            try:
                if eventid == '':
                    picdir = geteventpic(None)
                else:
                    picdir = geteventpic(int(eventid))
            except FileNotFoundError:
                traceback.print_exc()
                sendmsg(event, f"未找到活动资源图片，请等待更新")
                return
            if picdir:
                sendmsg(event, fr"[CQ:image,file=file:///{botdir}\{picdir},cache=0]")
            else:
                sendmsg(event, f"未找到活动或生成失败")
            return
        if event.message[:2] == "rk":
            if event.message == "rk":
                bind = getqqbind(event.user_id, 'jp')
                if bind is None:
                    sendmsg(event, '你没有绑定id！')
                    return
                result = rk(bind[1], None, bind[2])
                sendmsg(event, result)
            else:
                userid = event.message.replace("rk", "")
                userid = re.sub(r'\D', "", userid)
                if userid == '':
                    sendmsg(event, '你这id有问题啊')
                    return
                if int(userid) > 10000000:
                    result = rk(userid)
                else:
                    result = rk(None, userid)
                sendmsg(event, result)
            return
        try:
            if event.message == "热度排行":
                hotrank()
                sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\hotrank.png,cache=0]")
                return
            if event.message[:4] == "难度排行" or event.message[2:6] == "难度排行":
                if event.message[:2].lower() == 'fc':
                    fcap = 1
                elif event.message[:2].lower() == 'ap':
                    fcap = 2
                else:
                    fcap = 0
                event.message = event.message[event.message.find("难度排行") + len("难度排行"):].strip()
                para = event.message.split(" ")
                if len(para) == 1:
                    success = levelrank(int(event.message), 'master', fcap)
                else:
                    success = levelrank(int(para[0]), para[1], fcap)
                if success:
                    if len(para) == 1:
                        sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\{para[0]}master{fcap}.png,cache=0]")
                    else:
                        sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\{para[0]}{para[1]}{fcap}.png,cache=0]")
                else:
                    sendmsg(event, '参数错误，指令：/难度排行 定数 难度，'
                                   '难度支持的输入: easy, normal, hard, expert, master，如/难度排行 28 expert')
                return
        except:
            sendmsg(event, '参数错误，指令：/难度排行 定数 难度，'
                           '难度支持的输入: easy, normal, hard, expert, master，如/难度排行 28 expert')

        if event.message[:7] == 'pjskbpm' or (event.message[:3] == 'bpm' and event.self_id == guildbot):
            parm = event.message[event.message.find("bpm") + len("bpm"):].strip()
            resp = aliastomusicid(parm)
            if resp['musicid'] == 0:
                sendmsg(event, '没有找到你要的歌曲哦')
                return
            else:
                bpm = parse_bpm(resp['musicid'])
                text = ''
                for bpms in bpm[1]:
                    text = text + ' - ' + str(bpms['bpm']).replace('.0', '')
                text = f"{resp['name']}\n匹配度:{round(resp['match'], 4)}\nBPM: " + text[3:]
                sendmsg(event, text)
            return
        if "谱面预览2" in event.message:
            picdir = aliastochart(event.message.replace("谱面预览2", ''), True)
            if picdir is not None:  # 匹配到歌曲
                if len(picdir) == 2:  # 有图片
                    sendmsg(event, picdir[0] + fr"[CQ:image,file=file:///{botdir}\{picdir[1]},cache=0]")
                else:
                    sendmsg(event, picdir + "\n暂无谱面图片 请等待更新"
                                            "\n（温馨提示：谱面预览2只能看master与expert）")
            else:  # 匹配不到歌曲
                sendmsg(event, "没有找到你说的歌曲哦")
            return
        if event.message[:4] == 'card':
            cardid = event.message[event.message.find("card") + len("card"):].strip()
            pics = cardidtopic(int(cardid))
            print(pics)
            for pic in pics:
                sendmsg(event, fr"[CQ:image,file=file:///{botdir}\{pic},cache=0]")
            return
        if event.message[:4] == "谱面预览" or event.message[-4:] == "谱面预览" :
            qun = True
            if event.self_id == guildbot:
                qun = False
            picdir = aliastochart(event.message.replace("谱面预览", ''), False, qun, getcharttheme(event.user_id))
            if picdir is not None:  # 匹配到歌曲
                if len(picdir) == 2:  # 有图片
                    sendmsg(event, picdir[0] + fr"[CQ:image,file=file:///{botdir}\{picdir[1]},cache=0]")
                elif picdir == '':
                    sendmsg(event, f'[CQ:poke,qq={event.user_id}]')
                    return
                else:
                    sendmsg(event, picdir + "\n暂无谱面图片 请等待更新")
            else:  # 匹配不到歌曲
                sendmsg(event, "没有找到你说的歌曲哦")
            return
        if event.message[:5] == "theme":
            theme = event.message[event.message.find("theme") + len("theme"):].strip()
            sendmsg(event, setcharttheme(event.user_id, theme))
            return
        if event.message[:3] == "查时间":
            userid = event.message[event.message.find("查时间") + len("查时间"):].strip()
            if userid == '':
                bind = getqqbind(event.user_id, server)
                if bind is None:
                    sendmsg(event, '你没有绑定id！')
                    return
                userid = bind[1]
            userid = re.sub(r'\D', "", userid)
            if userid == '':
                sendmsg(event, '你这id有问题啊')
                return
            if verifyid(userid):
                sendmsg(event, time.strftime('注册时间：%Y-%m-%d %H:%M:%S',
                                             time.localtime(gettime(userid))))
            else:
                sendmsg(event, '你这id有问题啊')
            return
        if event.message[:8] == 'charaset' and 'to' in event.message:
            if event.user_id in aliasblock:
                sendmsg(event, '你因乱设置昵称已无法使用此功能')
                return
            event.message = event.message[8:]
            para = event.message.split('to')
            if event.sender['card'] == '':
                username = event.sender['nickname']
            else:
                username = event.sender['card']
            if event.self_id == guildbot:
                resp = requests.get(f'http://127.0.0.1:{guildhttpport}/get_guild_info?guild_id={event.guild_id}')
                qun = resp.json()
                sendmsg(event,
                        charaset(para[0], para[1], event.user_id, username, f"{qun['name']}({event.guild_id})内"))
            else:
                qun = bot.sync.get_group_info(self_id=event.self_id, group_id=event.group_id)
                sendmsg(event, charaset(para[0], para[1], event.user_id, username, f"{qun['group_name']}({event.group_id})内"))
            return
        if event.message[:10] == 'grcharaset' and 'to' in event.message:
            event.message = event.message[10:]
            para = event.message.split('to')
            if event.self_id == guildbot:
                sendmsg(event, grcharaset(para[0], para[1], event.guild_id))
            else:
                sendmsg(event, grcharaset(para[0], para[1], event.group_id))
            return
        if event.message[:8] == 'charadel':
            if event.user_id in aliasblock:
                sendmsg(event, '你因乱设置昵称已无法使用此功能')
                return
            event.message = event.message[8:]
            if event.sender['card'] == '':
                username = event.sender['nickname']
            else:
                username = event.sender['card']
            if event.self_id == guildbot:
                resp = requests.get(f'http://127.0.0.1:{guildhttpport}/get_guild_info?guild_id={event.guild_id}')
                qun = resp.json()
                sendmsg(event,
                        charadel(event.message, event.user_id, username, f"{qun['name']}({event.guild_id})内"))
            else:
                qun = bot.sync.get_group_info(self_id=event.self_id, group_id=event.group_id)
                sendmsg(event, charadel(event.message, event.user_id, username, f"{qun['group_name']}({event.group_id})内"))
            return
        if event.message[:10] == 'grcharadel':
            event.message = event.message[10:]
            if event.self_id == guildbot:
                sendmsg(event, grcharadel(event.message, event.guild_id))
            else:
                sendmsg(event, grcharadel(event.message, event.group_id))
            return
        if event.message[:9] == 'charainfo':
            event.message = event.message[9:]
            if event.self_id == guildbot:
                sendmsg(event, charainfo(event.message, event.guild_id))
            else:
                sendmsg(event, charainfo(event.message, event.group_id))
            return
        if event.message == '看33':
            return
            sendmsg(event, f"[CQ:image,file=file:///{botdir}/pics/33{random.randint(0, 1)}.gif,cache=0]")
            return
        if event.message == '推车':
            ycmimg()
            sendmsg(event, f"[CQ:image,file=file:///{botdir}/piccache/ycm.png,cache=0]")
            return
        if event.message[:4] == 'homo':
            if event.self_id not in mainbot and event.self_id != guildbot:
                return
            if event.group_id in blacklist['ettm']:
                return
            event.message = event.message[event.message.find("homo") + len("homo"):].strip()
            try:
                sendmsg(event, event.message + '=' + generate_homo(event.message))
            except ValueError:
                return
            return
        if "生成" in event.message:
            if event.message[:2] == "生成":
                rainbow = False
            elif event.message[:4] == "彩虹生成":
                rainbow = True
            else:
                return
            if event.group_id in blacklist['ettm']:
                return
            event.message = event.message[event.message.find("生成") + len("生成"):].strip()
            para = event.message.split(" ")
            now = int(time.time() * 1000)
            if len(para) < 2:
                para = event.message.split("/")
                if len(para) < 2:
                    sendmsg(event, '请求不对哦，/生成 这是红字 这是白字')
                    return
            cyo5000(para[0], para[1], f"piccache/{now}.png", rainbow)
            sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache\{now}.png,cache=0]")
            return
        if event.message[:3] == "ccf":
            if event.self_id not in mainbot and event.self_id != guildbot:
                return
            if event.group_id in blacklist['ettm']:
                return
            event.message = event.message[event.message.find("ccf") + len("ccf"):].strip()
            dd = dd_query.DDImageGenerate(event.message)
            image_path, vtb_following_count, total_following_count = dd.image_generate()
            sendmsg(event, f"{dd.username} 总共关注了 {total_following_count} 位up主, 其中 {vtb_following_count} 位是vtb。\n"
                           f"注意: 由于b站限制, bot最多只能拉取到最近250个关注。因此可能存在数据统计不全的问题。"
                    + fr"[CQ:image,file=file:///{image_path},cache=0]")
            return
        if event.message[:5] == "白名单添加" and event.user_id in whitelist:
            event.message = event.message[event.message.find("白名单添加") + len("白名单添加"):].strip()
            requestwhitelist.append(int(event.message))
            sendmsg(event, '添加成功: ' + event.message)
            return
        if event.message[:3] == "达成率":
            event.message = event.message[event.message.find("达成率") + len("达成率"):].strip()
            para = event.message.split(' ')
            if len(para) < 5:
                return
            sendmsg(event, tasseiritsu(para))
            return
        if event.message[:2] == '机翻' and event.message[-2:] == '推特':
            if event.user_id not in whitelist and event.group_id not in whitelist:
                return
            if '最新' in event.message:
                event.message = event.message.replace('最新', '')
            twiid = event.message[2:-2]
            try:
                twiid = newesttwi(twiid, True)
                sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache/{twiid}.png,cache=0]")
            except:
                sendmsg(event, '查不到捏，可能是你id有问题或者bot卡了')
            return
        if event.message[-4:] == '最新推特':
            if event.user_id not in whitelist and event.group_id not in whitelist:
                return
            try:
                twiid = newesttwi(event.message.replace('最新推特', '').replace(' ', ''))
                sendmsg(event, fr"[CQ:image,file=file:///{botdir}\piccache/{twiid}.png,cache=0]")
            except:
                sendmsg(event, '查不到捏，可能是你id有问题或者bot卡了')
            return
        if event.message[:4] == '封面匹配':
            global opencvmatch
            if not opencvmatch:
                try:
                    opencvmatch = True
                    sendmsg(event, f'[CQ:reply,id={event.message_id}]了解，查询中（输出只对有效输入负责）')
                    url = event.message[event.message.find('url=') + 4:event.message.find(']')]
                    title, picdir = matchjacket(url=url)
                    if title:
                        if 'assets' in picdir:
                            sendmsg(event, f"[CQ:reply,id={event.message_id}]匹配点过少，该曲为最有可能匹配的封面：\n" + fr"{title}[CQ:image,file=file:///{botdir}\{picdir},cache=0]")
                        else:
                            sendmsg(event, fr"[CQ:reply,id={event.message_id}]{title}[CQ:image,file=file:///{botdir}\{picdir},cache=0]")
                    else:
                        sendmsg(event, f'[CQ:reply,id={event.message_id}]找不到捏')
                except Exception as a:
                    traceback.print_exc()
                    sendmsg(event, '出问题了捏\n' + repr(a))
                opencvmatch = False
            else:
                sendmsg(event, f'当前有正在匹配的进程，请稍后再试')
            return
        if event.message[:3] == '查物量':
            sendmsg(event, notecount(int(event.message[3:])))
            return
        if event.message[:4] == '查bpm':
            sendmsg(event, findbpm(int(event.message[4:])))
            return
        if event.message[:2] == '看看':
            if event.group_id in kkwhitelist:
                url = kankan(event.message[event.message.find('看看') + len('看看'):].strip())
                if url is not None:
                    sendmsg(event, f"[CQ:image,file={url},cache=1]")
            return
        if event.message[:2] == '上传':
            if event.group_id in kkwhitelist:
                if '[CQ:image' in event.message:
                    foldername = event.message[event.message.find('上传') + len('上传'):].strip()
                    foldername = foldername[:foldername.find('[CQ:image')]
                    url = event.message[event.message.find('url=') + len('url='):event.message.find(']')]
                    filename = f'{event.user_id}_{int(time.time()*100)}.jpg'
                    uploadkk(url, filename, foldername)
                    sendmsg(event, "上传成功")
        if event.message[:1] == '看' or event.message[:2] == '来点':
            if event.user_id not in whitelist and event.group_id not in whitelist and event.self_id != guildbot:
                return
            event.message = event.message.replace('看', '', 1)
            event.message = event.message.replace('来点', '', 1)
            resp = aliastocharaid(event.message, event.group_id)
            if resp[0] != 0:
                cardurl = get_card(resp[0])
                if 'cutout' not in cardurl:
                    cardurl = cardurl.replace('png', 'jpg')
                sendmsg(event, fr"[CQ:image,file=file:///{botdir}\{cardurl},cache=0]")
            return
        if 'pjsk抽卡' in event.message or 'sekai抽卡' in event.message:
            if event.user_id not in whitelist and event.group_id not in whitelist and event.self_id != guildbot:
                return
            gachaid = event.message[event.message.find("抽卡") + len("抽卡"):].strip()
            gachaid = re.sub(r'\D', "", gachaid)
            if gachaid == '':
                currentgacha = getcurrentgacha()
                msg = fakegacha(int(currentgacha['id']), 10, False, True)
            else:
                msg = fakegacha(int(gachaid), 10, False, True)
            sendmsg(event, msg[0] + fr"[CQ:image,file=file:///{botdir}\{msg[1]},cache=0]")
            return
        if 'pjsk反抽卡' in event.message or 'sekai反抽卡' in event.message:
            if event.user_id not in whitelist and event.group_id not in whitelist and event.self_id != guildbot:
                return
            gachaid = event.message[event.message.find("抽卡") + len("抽卡"):].strip()
            gachaid = re.sub(r'\D', "", gachaid)
            if gachaid == '':
                currentgacha = getcurrentgacha()
                msg = fakegacha(int(currentgacha['id']), 10, True, True)
            else:
                msg = fakegacha(int(gachaid), 10, True, True)
            sendmsg(event, msg[0] + fr"[CQ:image,file=file:///{botdir}\{msg[1]},cache=0]")
            return
        if (event.message[0:5] == 'sekai' or event.message[0:4] == 'pjsk') and '连' in event.message:
            if event.user_id not in whitelist and event.group_id not in whitelist and event.self_id != guildbot:
                return
            gachaid = event.message[event.message.find("连") + len("连"):].strip()
            num = event.message[:event.message.find('连')].replace('sekai', '').replace('pjsk', '')
            num = re.sub(r'\D', "", num)
            if int(num) > 200:
                sendmsg(event, '太多了，少抽一点吧！')
                return
            if gachaid == '':
                currentgacha = getcurrentgacha()
                sendmsg(event, fakegacha(int(currentgacha['id']), int(num), False))
            else:
                sendmsg(event, fakegacha(int(gachaid), int(num), False))
            return
        if event.message == '更新日志' and event.user_id in admin:
            writelog()
            sendmsg(event, '更新成功')
            return

        # 猜曲
        if event.message == 'pjsk猜谱面' or event.message == 'pjsk猜曲 3':
            if event.user_id not in whitelist and event.group_id not in whitelist and event.self_id != guildbot:
                return
            try:
                isgoing = charaguess[event.group_id]['isgoing']
                if isgoing:
                    sendmsg(event, '已经开启猜卡面！')
                    return
            except KeyError:
                pass

            try:
                isgoing = pjskguess[event.group_id]['isgoing']
                if isgoing:
                    sendmsg(event, '已经开启猜曲！')
                    return
                else:
                    musicid = getrandomchart()
                    pjskguess[event.group_id] = {'isgoing': True, 'musicid': musicid,
                                                 'starttime': int(time.time()), 'selfid': event.self_id}
            except KeyError:
                musicid = getrandomchart()
                pjskguess[event.group_id] = {'isgoing': True, 'musicid': musicid, 'starttime': int(time.time()), 'selfid': event.self_id}
            cutchartimg(musicid, event.group_id)
            sendmsg(event, 'PJSK谱面竞猜（随机裁切）\n艾特我+你的答案以参加猜曲（不要使用回复）\n\n你有50秒的时间回答\n可手动发送“结束猜曲”来结束猜曲'
                    + fr"[CQ:image,file=file:///{botdir}\piccache/{event.group_id}.png,cache=0]")
            return
        if event.message == 'pjsk猜卡面' or event.message == 'pjsk猜曲 4':
            if event.user_id not in whitelist and event.group_id not in whitelist and event.self_id != guildbot:
                return
            try:
                isgoing = pjskguess[event.group_id]['isgoing']
                if isgoing:
                    sendmsg(event, '已经开启猜曲！')
                    return
            except KeyError:
                pass
            # getrandomcard() return characterId, assetbundleName, prefix, cardRarityType
            try:
                isgoing = charaguess[event.group_id]['isgoing']
                if isgoing:
                    sendmsg(event, '已经开启猜曲！')
                    return
                else:
                    cardinfo = getrandomcard()
                    charaguess[event.group_id] = {'isgoing': True, 'charaid': cardinfo[0],
                                                  'assetbundleName': cardinfo[1], 'prefix': cardinfo[2],
                                                  'starttime': int(time.time()), 'selfid': event.self_id}
            except KeyError:
                cardinfo = getrandomcard()
                charaguess[event.group_id] = {'isgoing': True, 'charaid': cardinfo[0],
                                              'assetbundleName': cardinfo[1],
                                              'prefix': cardinfo[2], 'starttime': int(time.time()), 'selfid': event.self_id}

            charaguess[event.group_id]['istrained'] = cutcard(cardinfo[1], cardinfo[3], event.group_id)
            sendmsg(event, 'PJSK猜卡面\n你有30秒的时间回答\n艾特我+你的答案（只猜角色）以参加猜曲（不要使用回复）\n发送「结束猜卡面」可退出猜卡面模式'
                    + fr"[CQ:image,file=file:///{botdir}\piccache/{event.group_id}.png,cache=0]")
            return
        if (event.message[-2:] == '猜曲' or event.message[-4:-2] == '猜曲') and event.message[:4] == 'pjsk':
            if event.user_id not in whitelist and event.group_id not in whitelist and event.self_id != guildbot:
                return
            if event.self_id == guildbot:
                if '听歌猜曲' in event.message or '倒放猜曲' in event.message:
                    sendmsg(event, "由于暂无好的频道bot发送语音的办法，请在群聊中使用该功能")
                    return
            try:
                isgoing = charaguess[event.group_id]['isgoing']
                if isgoing:
                    sendmsg(event, '已经开启猜卡面！')
                    return
            except KeyError:
                pass

            try:
                isgoing = pjskguess[event.group_id]['isgoing']
                if isgoing:
                    sendmsg(event, '已经开启猜曲！')
                    return
                else:
                    if event.message == 'pjsk听歌猜曲' or event.message == 'pjsk倒放猜曲':
                        musicid, assetbundleName = getrandommusic()
                    else:
                        musicid = getrandomjacket()
                    pjskguess[event.group_id] = {'isgoing': True, 'musicid': musicid,
                                                 'starttime': int(time.time()), 'selfid': event.self_id}
            except KeyError:
                if event.message == 'pjsk听歌猜曲' or event.message == 'pjsk倒放猜曲':
                    musicid, assetbundleName = getrandommusic()
                else:
                    musicid = getrandomjacket()
                pjskguess[event.group_id] = {'isgoing': True, 'musicid': musicid, 'starttime': int(time.time()), 'selfid': event.self_id}

            if event.message == 'pjsk猜曲':
                cutjacket(musicid, event.group_id, size=140, isbw=False)
            elif event.message == 'pjsk阴间猜曲' or event.message == 'pjsk猜曲 2':
                cutjacket(musicid, event.group_id, size=140, isbw=True)
            elif event.message == 'pjsk非人类猜曲':
                cutjacket(musicid, event.group_id, size=30, isbw=False)
            elif event.message == 'pjsk听歌猜曲':
                cutmusic(assetbundleName, event.group_id)
                sendmsg(event, 'PJSK听歌识曲竞猜 （随机裁切）\n艾特我+你的答案以参加猜曲（不要使用回复）\n\n你有50秒的时间回答\n可手动发送“结束猜曲”来结束猜曲')
                sendmsg(event, fr"[CQ:record,file=file:///{botdir}/piccache/{event.group_id}.mp3,cache=0]")
                return
            elif event.message == 'pjsk倒放猜曲':
                cutmusic(assetbundleName, event.group_id, True)
                sendmsg(event, 'PJSK倒放识曲竞猜 （随机裁切）\n艾特我+你的答案以参加猜曲（不要使用回复）\n\n你有50秒的时间回答\n可手动发送“结束猜曲”来结束猜曲')
                sendmsg(event, fr"[CQ:record,file=file:///{botdir}/piccache/{event.group_id}.mp3,cache=0]")
                return
            else:
                cutjacket(musicid, event.group_id, size=140, isbw=False)
            sendmsg(event, 'PJSK曲绘竞猜 （随机裁切）\n艾特我+你的答案以参加猜曲（不要使用回复）\n\n你有50秒的时间回答\n可手动发送“结束猜曲”来结束猜曲'
                    + fr"[CQ:image,file=file:///{botdir}/piccache/{event.group_id}.png,cache=0]")
            return

        if event.message == '结束猜曲':
            try:
                isgoing = pjskguess[event.group_id]['isgoing']
                if isgoing:
                    picdir = f"data/assets/sekai/assetbundle/resources/startapp/music/jacket/" \
                             f"jacket_s_{str(pjskguess[event.group_id]['musicid']).zfill(3)}/" \
                             f"jacket_s_{str(pjskguess[event.group_id]['musicid']).zfill(3)}.png"
                    text = '正确答案：' + idtoname(pjskguess[event.group_id]['musicid'])
                    pjskguess[event.group_id]['isgoing'] = False
                    sendmsg(event, text + fr"[CQ:image,file=file:///{botdir}\{picdir},cache=0]")
            except KeyError:
                pass
            return
        if event.message == '结束猜卡面':
            try:
                isgoing = charaguess[event.group_id]['isgoing']
                if isgoing:
                    if charaguess[event.group_id]['istrained']:
                        picdir = 'data/assets/sekai/assetbundle/resources/startapp/' \
                                 f"character/member/{charaguess[event.group_id]['assetbundleName']}/card_after_training.jpg"
                    else:
                        picdir = 'data/assets/sekai/assetbundle/resources/startapp/' \
                                 f"character/member/{charaguess[event.group_id]['assetbundleName']}/card_normal.jpg"
                    text = f"正确答案：{charaguess[event.group_id]['prefix']} - {getcharaname(charaguess[event.group_id]['charaid'])}"
                    charaguess[event.group_id]['isgoing'] = False

                    sendmsg(event, text + fr"[CQ:image,file=file:///{botdir}\{picdir},cache=0]")
            except KeyError:
                pass
            return
        # 判断艾特自己
        if event.message[:len(f'[CQ:at,qq={event.self_id}]')] == f'[CQ:at,qq={event.self_id}]' or event.self_id == guildbot:
            # 判断有没有猜曲
            try:
                isgoing = pjskguess[event.group_id]['isgoing']
                if isgoing:
                    answer = event.message[event.message.find("]") + len("]"):].strip()
                    resp = aliastomusicid(answer)
                    if resp['musicid'] == 0:
                        sendmsg(event, '没有找到你说的歌曲哦')
                        return
                    else:
                        if resp['musicid'] == pjskguess[event.group_id]['musicid']:
                            text = f'[CQ:at,qq={event.user_id}] 您猜对了'
                            if int(time.time()) > pjskguess[event.group_id]['starttime'] + 45:
                                text = text + '，回答已超时'
                            picdir = f"data/assets/sekai/assetbundle/resources/startapp/music/jacket/" \
                                     f"jacket_s_{str(pjskguess[event.group_id]['musicid']).zfill(3)}/" \
                                     f"jacket_s_{str(pjskguess[event.group_id]['musicid']).zfill(3)}.png"
                            text = text + '\n正确答案：' + idtoname(pjskguess[event.group_id]['musicid'])
                            pjskguess[event.group_id]['isgoing'] = False
                            sendmsg(event, text + fr"[CQ:image,file=file:///{botdir}\{picdir},cache=0]")
                        else:
                            text = f"[CQ:at,qq={event.user_id}] 您猜错了，答案不是{idtoname(resp['musicid'])}哦"
                            if int(time.time()) > pjskguess[event.group_id]['starttime'] + 45:
                                text = text + '，回答已超时'
                                picdir = f"data/assets/sekai/assetbundle/resources/startapp/music/jacket/" \
                                         f"jacket_s_{str(pjskguess[event.group_id]['musicid']).zfill(3)}/" \
                                         f"jacket_s_{str(pjskguess[event.group_id]['musicid']).zfill(3)}.png"
                                text = text + '\n正确答案：' + idtoname(pjskguess[event.group_id]['musicid']) + fr"[CQ:image,file=file:///{botdir}\{picdir},cache=0]"
                                pjskguess[event.group_id]['isgoing'] = False
                            sendmsg(event, text)
                    return
            except KeyError:
                pass
            # 判断有没有猜卡面
            try:
                isgoing = charaguess[event.group_id]['isgoing']
                if isgoing:
                    # {'isgoing', 'charaid', 'assetbundleName', 'prefix', 'starttime'}
                    answer = event.message[event.message.find("]") + len("]"):].strip()
                    if event.self_id == guildbot:
                        resp = aliastocharaid(answer, event.guild_id)
                    else:
                        resp = aliastocharaid(answer, event.group_id)
                    if resp[0] == 0:
                        sendmsg(event, '没有找到你说的角色哦')
                        return
                    else:
                        if resp[0] == charaguess[event.group_id]['charaid']:
                            text = f'[CQ:at,qq={event.user_id}] 您猜对了'
                            if int(time.time()) > charaguess[event.group_id]['starttime'] + 45:
                                text = text + '，回答已超时'
                            if charaguess[event.group_id]['istrained']:
                                picdir = 'data/assets/sekai/assetbundle/resources/startapp/' \
                                         f"character/member/{charaguess[event.group_id]['assetbundleName']}/card_after_training.jpg"
                            else:
                                picdir = 'data/assets/sekai/assetbundle/resources/startapp/' \
                                         f"character/member/{charaguess[event.group_id]['assetbundleName']}/card_normal.jpg"
                            text = text + f"\n正确答案：{charaguess[event.group_id]['prefix']} - {resp[1]}"
                            charaguess[event.group_id]['isgoing'] = False
                            sendmsg(event, text + fr"[CQ:image,file=file:///{botdir}\{picdir},cache=0]")
                        else:
                            text = f"[CQ:at,qq={event.user_id}] 您猜错了，答案不是{resp[1]}哦"
                            if int(time.time()) > charaguess[event.group_id]['starttime'] + 45:
                                text = text + '，回答已超时'
                                if charaguess[event.group_id]['istrained']:
                                    picdir = 'data/assets/sekai/assetbundle/resources/startapp/' \
                                             f"character/member/{charaguess[event.group_id]['assetbundleName']}/card_after_training.jpg"
                                else:
                                    picdir = 'data/assets/sekai/assetbundle/resources/startapp/' \
                                             f"character/member/{charaguess[event.group_id]['assetbundleName']}/card_normal.jpg"
                                text = text + f"\n正确答案：{charaguess[event.group_id]['prefix']} - {getcharaname(charaguess[event.group_id]['charaid'])}" + fr"[CQ:image,file=file:///{botdir}\{picdir},cache=0]"
                                charaguess[event.group_id]['isgoing'] = False
                            sendmsg(event, text)
                    return
            except KeyError:
                pass
        if event.message == f'[CQ:at,qq={event.self_id}] ':
            sendmsg(event, 'bot帮助文档：https://docs.unipjsk.com/')
            return
    except (requests.exceptions.ConnectionError, JSONDecodeError):
        sendmsg(event, '查不到数据捏，好像是bot网不好')
    except Exception as a:
        traceback.print_exc()
        if repr(a) == "KeyError('status')":
            sendmsg(event, '图片发送失败，请再试一次')
        else:
            sendmsg(event, '出问题了捏\n' + repr(a))


def sendmsg(event, msg):
    global send1
    global send3
    timeArray = time.localtime(time.time())
    Time = time.strftime("\n[%Y-%m-%d %H:%M:%S]", timeArray)
    try:
        print(Time, botname[event.self_id] + '收到命令', event.group_id, event.user_id, event.message.replace('\n', ''))
        print(botname[event.self_id] + '发送群消息', event.group_id, msg.replace('\n', ''))
    except KeyError:
        print(Time, '测试bot收到命令', event.group_id, event.user_id, event.message.replace('\n', ''))
        print('测试bot发送群消息', event.group_id, msg.replace('\n', ''))

    try:
        if event.self_id == guildbot:
            bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id, message=f'[CQ:reply,id={event.message_id}]' + msg)
        else:
            bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id, message=msg)
        if event.self_id == 1513705608:
            send1 = False
        elif event.self_id == 3506606538:
            send3 = False
    except aiocqhttp.exceptions.ActionFailed:
        if event.self_id == 1513705608:
            print('一号机发送失败')
            if send1 is not True:
                print('即将发送告警邮件')
                sendemail(botname[event.self_id] + '群消息发送失败', str(event.group_id) + msg)
                send1 = True
            else:
                print('告警邮件发过了')
        elif event.self_id == 3506606538:
            print('三号机发送失败')
            if send3 is not True:
                print('即将发送告警邮件')
                sendemail(botname[event.self_id] + '群消息发送失败', str(event.group_id) + msg)
                send3 = True
            else:
                print('告警邮件发过了')


@bot.on_notice('group_increase')  # 群人数增加事件
async def handle_group_increase(event: Event):
    if event.self_id == guildbot:
        return
    if event.user_id == event.self_id:  # 自己被邀请进群
        if event.group_id in requestwhitelist:
            await bot.send_group_msg(self_id=event.self_id, group_id=msggroup, message=f'我已加入群{event.group_id}')
        else:
            await bot.send_group_msg(self_id=event.self_id, group_id=event.group_id, message='未经审核的邀请，已自动退群')
            await bot.set_group_leave(self_id=event.self_id, group_id=event.group_id)
            await bot.send_group_msg(self_id=event.self_id, group_id=msggroup,
                                     message=f'有人邀请我加入群{event.group_id}，已自动退群')


@bot.on_request('group')  # 加群请求或被拉群
async def handle_group_request(event: Event):
    if event.self_id == guildbot:
        return
    print(event.sub_type, event.message)
    if event.sub_type == 'invite':  # 被邀请加群
        if event.group_id in requestwhitelist:
            await bot.set_group_add_request(self_id=event.self_id, flag=event.flag, sub_type=event.sub_type,
                                            approve=True)
            await bot.send_group_msg(self_id=event.self_id, group_id=msggroup,
                                     message=f'{event.user_id}邀请我加入群{event.group_id}，已自动同意')
        else:
            await bot.set_group_add_request(self_id=event.self_id, flag=event.flag, sub_type=event.sub_type,
                                            approve=False)
            await bot.send_group_msg(self_id=event.self_id, group_id=msggroup,
                                     message=f'{event.user_id}邀请我加入群{event.group_id}，已自动拒绝')
    elif event.sub_type == 'add':  # 有人加群
        if event.group_id == 883721511 or event.group_id == 647347636:
            try:
                if groupaudit[event.user_id] >= 4:
                    await bot.set_group_add_request(self_id=event.self_id, flag=event.flag, sub_type=event.sub_type,
                                                    approve=False,
                                                    reason=f'多次回答错误，你已被本群暂时拉黑')
                    await bot.send_group_msg(self_id=event.self_id, group_id=msggroup,
                                             message=f'{event.user_id}申请加群\n多次回答错误，已被暂时拉黑')
                    return
            except:
                pass
            answer = event.comment[event.comment.find("答案：") + len("答案："):].strip()
            answer = re.sub(r'\D', "", answer)
            async with aiofiles.open('masterdata/musics.json', 'r', encoding='utf-8') as f:
                contents = await f.read()
            musics = json.loads(contents)
            now = time.time() * 1000
            count = 0
            for music in musics:
                if music['publishedAt'] < now:
                    count += 1
            print(count)
            if count - 5 < int(answer) < count + 5:
                await bot.set_group_add_request(self_id=event.self_id, flag=event.flag, sub_type=event.sub_type,
                                                approve=True)
                await bot.send_group_msg(self_id=event.self_id, group_id=msggroup,
                                         message=f'{event.user_id}申请加群\n{event.comment}\n误差<5，已自动通过')
            else:
                try:
                    groupaudit[event.user_id]
                except:
                    groupaudit[event.user_id] = 0

                await bot.set_group_add_request(self_id=event.self_id, flag=event.flag, sub_type=event.sub_type,
                                                approve=False, reason=f'回答错误，请认真回答(使用阿拉伯数字)，你还有{3-groupaudit[event.user_id]}次机会')
                await bot.send_group_msg(self_id=event.self_id, group_id=msggroup,
                                         message=f'{event.user_id}申请加群\n{event.comment}\n误差>5，已自动拒绝')
                groupaudit[event.user_id] += 1
        elif event.group_id == 467602419:
            answer = event.comment[event.comment.find("答案：") + len("答案："):].strip()
            if 'Mrs4s/go-cqhttp' in answer:
                await bot.set_group_add_request(self_id=event.self_id, flag=event.flag, sub_type=event.sub_type,
                                                approve=True)
                await bot.send_group_msg(self_id=event.self_id, group_id=msggroup,
                                         message=f'{event.user_id}申请加群\n{event.comment}\n已自动通过')
            else:
                await bot.send_group_msg(self_id=event.self_id, group_id=msggroup,
                                         message=f'{event.user_id}申请加群\n{event.comment}\n，无法判定')


@bot.on_notice('group_ban')
async def handle_group_ban(event: Event):
    if event.self_id == guildbot:
        return
    print(event.group_id, event.operator_id, event.user_id, event.duration)
    if event.user_id == event.self_id:
        await bot.set_group_leave(self_id=event.self_id, group_id=event.group_id)
        await bot.send_group_msg(self_id=event.self_id, group_id=msggroup,
                                 message=f'我在群{event.group_id}内被{event.operator_id}禁言{event.duration / 60}分钟，已自动退群')

@bot.on_notice()
async def handle_poke(event: Event):
    if event.self_id == guildbot:
        return
    if event.sub_type == 'poke' and event.target_id == event.self_id:
        if event.self_id in mainbot:
            global pokelimit
            nowtime = f"{str(datetime.now().hour).zfill(2)}{str(datetime.now().minute).zfill(2)}"
            lasttime = pokelimit['lasttime']
            count = pokelimit['count']
            if nowtime == lasttime and count >= 5:
                print(pokelimit)
                print('达到每分钟戳一戳发语音上限')
                return
            if nowtime != lasttime:
                count = 0
            pokelimit['lasttime'] = nowtime
            pokelimit['count'] = count + 1
            print(pokelimit)
            await bot.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                 message=fr"[CQ:record,file=file:///{botdir}/chara/kndvoice/{random.choice(os.listdir('chara/kndvoice/'))},cache=0]")

async def autopjskguess():
    global pjskguess
    global charaguess
    now = time.time()
    for group in pjskguess:
        if pjskguess[group]['isgoing'] and pjskguess[group]['starttime'] + 50 < now:
            picdir = f"{asseturl}/startapp/music/jacket/" \
                     f"jacket_s_{str(pjskguess[group]['musicid']).zfill(3)}/" \
                     f"jacket_s_{str(pjskguess[group]['musicid']).zfill(3)}.png"
            text = '时间到，正确答案：' + idtoname(pjskguess[group]['musicid'])
            pjskguess[group]['isgoing'] = False
            try:
                await bot.send_group_msg(self_id=pjskguess[group]['selfid'], group_id=group, message=text + fr"[CQ:image,file={picdir},cache=0]")
            except:
                pass

    for group in charaguess:
        if charaguess[group]['isgoing'] and charaguess[group]['starttime'] + 30 < now:
            if charaguess[group]['istrained']:
                picdir = f'{asseturl}/startapp/' \
                         f"character/member/{charaguess[group]['assetbundleName']}/card_after_training.jpg"
            else:
                picdir = f'{asseturl}/startapp/' \
                         f"character/member/{charaguess[group]['assetbundleName']}/card_normal.jpg"
            text = f"时间到，正确答案：{charaguess[group]['prefix']} - " + \
                   getcharaname(charaguess[group]['charaid'])
            charaguess[group]['isgoing'] = False
            try:
                await bot.send_group_msg(self_id=charaguess[group]['selfid'], group_id=group, message=text + fr"[CQ:image,file={picdir},cache=0]")
            except:
                pass


with open('yamls/blacklist.yaml', "r") as f:
    blacklist = yaml.load(f, Loader=yaml.FullLoader)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
scheduler = AsyncIOScheduler()
if os.path.basename(__file__) == 'bot.py':
    scheduler.add_job(autopjskguess, 'interval', seconds=4)
scheduler.start()
if os.path.basename(__file__) == 'bot.py':
    bot.run(host='127.0.0.1', port=1234, debug=False, loop=loop)
else:
    bot.run(host='127.0.0.1', port=11416, debug=False, loop=loop)