import os
import json
import random
from datetime import datetime
from json import JSONDecodeError

import aiocqhttp
import aiofiles
import requests
import re
import time
import traceback
import yaml
from aiocqhttp import CQHttp, Event
from chachengfen import dd_query
from modules.api import gacha
from modules.chara import charaset, grcharaset, charadel, charainfo, grcharadel, aliastocharaid, get_card
from modules.config import whitelist, wordcloud, block, msggroup
from modules.cyo5000 import genImage
from modules.gacha import getcharaname, getallcurrentgacha, getcurrentgacha, fakegacha
from modules.homo import generate_homo
from modules.musics import hotrank, levelrank, parse_bpm, aliastochart, idtoname, notecount, tasseiritsu
from modules.pjskguess import getrandomjacket, cutjacket, getrandomchart, cutchartimg, getrandomcard, cutcard
from modules.pjskinfo import aliastomusicid, drawpjskinfo, pjskset, pjskdel, pjskalias
from modules.profileanalysis import daibu, rk, pjskjindu, pjskprofile, pjskb30
from modules.sendmail import sendemail
from modules.sk import sk, getqqbind, bindid, setprivate, skyc, verifyid, gettime
from modules.texttoimg import texttoimg, ycmimg
from modules.twitter import newesttwi
from wordCloud.generate import ciyun

bot = CQHttp()
botdir = os.getcwd()

pjskguess = {}
charaguess = {}
ciyunlimit = {}
gachalimit = {'lasttime': '', 'count': 0}
admin = [1103479519]
mainbot = [1513705608]
requestwhitelist = []  # 邀请加群白名单 随时设置 不保存到文件
groupban = [467602419]
botname = {
    1513705608: '一号机',
    3506606538: '三号机'
}

send = False


@bot.on_message('group')
async def _(event: Event):
    if event.group_id in wordcloud:
        if 'CQ:' not in event.raw_message and '&#' not in event.raw_message:
            async with aiofiles.open(f'wordCloud/{event.group_id}.txt', 'a', encoding='utf-8') as f:
                await f.write(event.message + '\n')


@bot.on_message('group')
def sync_handle_msg(event):
    global pjskguess
    global charaguess
    global ciyunlimit
    global gachalimit
    # global blacklist
    global requestwhitelist
    timeArray = time.localtime(time.time())
    Time = time.strftime("[%Y-%m-%d %H:%M:%S]", timeArray)
    print(Time, botname[event.self_id] + '收到消息', event.group_id, event.user_id, event.message.replace('\n', ''))
    if event.group_id in groupban:
        print('黑名单群已拦截')
        return
    if event.user_id in block:
        print('黑名单成员已拦截')
        return
    if event.message[0:1] == '/':
        event.message = event.message[1:]
    try:
        if event.message == '词云':
            if event.group_id not in wordcloud:
                sendmsg(event, '该群未开启词云功能，请联系bot主人手动开启')
                return
            try:
                lasttime = ciyunlimit[event.group_id]
                if time.time() - lasttime < 3600:
                    sendmsg(event, '上一次查还没过多久捏。别急')
                    return
            except KeyError:
                pass
            ciyunlimit[event.group_id] = time.time()
            ciyun(event.group_id)
            bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                    message=fr"[CQ:image,file=file:///{botdir}\piccache\{event.group_id}cy.png,cache=0]")
        if event.message == 'help':
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
                leak = drawpjskinfo(resp['musicid'])
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
                bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                        message=text + fr"[CQ:image,file=file:///{botdir}\piccache\pjskinfo{resp['musicid']}.png,cache=0]")
            return
        if event.message[:7] == 'pjskset' and 'to' in event.message:
            event.message = event.message[7:]
            para = event.message.split('to')
            resp = pjskset(para[0], para[1], event.user_id)
            sendmsg(event, resp)
            return
        if event.message[:7] == 'pjskdel':
            event.message = event.message[7:]
            resp = pjskdel(event.message, event.user_id)
            sendmsg(event, resp)
            return
        if event.message[:9] == 'pjskalias':
            event.message = event.message[9:]
            resp = pjskalias(event.message)
            sendmsg(event, resp)
            return
        if event.message == "sekai真抽卡":
            if event.self_id not in mainbot:
                return
            nowtime = f"{str(datetime.now().hour).zfill(2)}{str(datetime.now().minute).zfill(2)}"
            lasttime = gachalimit['lasttime']
            count = gachalimit['count']
            if nowtime == lasttime and count >= 2:
                sendmsg(event, f'技能冷却中，剩余cd:{60 - datetime.now().second}秒（一分钟内所有群只能抽两次）')
                return
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
        if event.message == "sk预测":
            texttoimg(skyc(), 500, 'skyc')
            bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                    message='sk预测' + fr"[CQ:image,file=file:///{botdir}\piccache\skyc.png,cache=0]")
            return
        if event.message[:2] == "sk":
            if event.message == "sk":
                bind = getqqbind(event.user_id)
                if bind is None:
                    sendmsg(event, '你没有绑定id！')
                    return
                result = sk(bind[1], None, bind[2])
                sendmsg(event, result)
            else:
                userid = event.message.replace("sk", "")
                userid = re.sub(r'\D', "", userid)
                if userid == '':
                    sendmsg(event, '你这id有问题啊')
                    return
                if int(userid) > 10000000:
                    result = sk(userid)
                else:
                    result = sk(None, userid)
                sendmsg(event, result)
                return
        if event.message[:2] == "rk":
            if event.message == "rk":
                bind = getqqbind(event.user_id)
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
        if event.message[:2] == "绑定":
            userid = event.message.replace("绑定", "")
            userid = re.sub(r'\D', "", userid)
            sendmsg(event, bindid(event.user_id, userid))
            return
        if event.message == "不给看":
            if setprivate(event.user_id, 1):
                sendmsg(event, '不给看！')
            else:
                sendmsg(event, '你还没有绑定哦')
            return
        if event.message == "给看":
            if setprivate(event.user_id, 0):
                sendmsg(event, '给看！')
            else:
                sendmsg(event, '你还没有绑定哦')
            return
        if event.message[:2] == "逮捕":
            if event.message == "逮捕":
                bind = getqqbind(event.user_id)
                if bind is None:
                    sendmsg(event, '查不到捏，可能是没绑定')
                    return
                result = daibu(bind[1], bind[2])
                sendmsg(event, result)
            else:
                userid = event.message.replace("逮捕", "")
                if '<@!' in userid:
                    qq = re.sub(r'\D', "", userid)
                    bind = getqqbind(qq)
                    if bind is None:
                        sendmsg(event, '查不到捏，可能是没绑定')
                        return
                    elif bind[2] and qq != str(event.user_id):
                        sendmsg(event, '查不到捏，可能是不给看')
                        return
                    else:
                        result = daibu(bind[1], bind[2])
                        sendmsg(event, result)
                        return
                userid = re.sub(r'\D', "", userid)
                if userid == '':
                    sendmsg(event, '你这id有问题啊')
                    return
                if int(userid) > 10000000:
                    result = daibu(userid)
                else:
                    result = daibu(userid)
                sendmsg(event, result)
            return
        if event.message == "pjsk进度":
            bind = getqqbind(event.user_id)
            if bind is None:
                sendmsg(event, '查不到捏，可能是没绑定')
                return
            pjskjindu(bind[1], bind[2])
            bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                    message=fr"[CQ:image,file=file:///{botdir}\piccache\{bind[1]}jindu.png,cache=0]")
            return
        if event.message == "pjsk b30":
            bind = getqqbind(event.user_id)
            if bind is None:
                sendmsg(event, '查不到捏，可能是没绑定')
                return
            pjskb30(bind[1], bind[2])
            bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                    message=fr"[CQ:image,file=file:///{botdir}\piccache\{bind[1]}b30.png,cache=0]")
            return
        if event.message == "热度排行":
            hotrank()
            bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                    message=fr"[CQ:image,file=file:///{botdir}\piccache\hotrank.png,cache=0]")
            return
        if "难度排行" in event.message:
            if event.message[:2] == 'fc':
                fcap = 1
            elif event.message[:2] == 'ap':
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
                    bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                            message=fr"[CQ:image,file=file:///{botdir}\piccache\{para[0]}master{fcap}.png,cache=0]")
                else:
                    bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                            message=fr"[CQ:image,file=file:///{botdir}\piccache\{para[0]}{para[1]}{fcap}.png,cache=0]")
            else:
                sendmsg(event, '参数错误，指令：/难度排行 定数 难度，'
                               '难度支持的输入: easy, normal, hard, expert, master，如/难度排行 28 expert')
            return
        if event.message == "pjskprofile" or event.message == "个人信息":
            bind = getqqbind(event.user_id)
            if bind is None:
                sendmsg(event, '查不到捏，可能是没绑定')
                return
            pjskprofile(bind[1], bind[2])
            bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                    message=fr"[CQ:image,file=file:///{botdir}\piccache\{bind[1]}profile.png,cache=0]")
            return
        if event.message[:7] == 'pjskbpm' or event.message[:3] == 'bpm':
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
            dir = aliastochart(event.message.replace("谱面预览2", ''), True)
            if dir is not None:  # 匹配到歌曲
                if len(dir) == 2:  # 有图片
                    bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                            message=dir[0] + fr"[CQ:image,file=file:///{botdir}\{dir[1]},cache=0]")
                else:
                    sendmsg(event, dir + "\n暂无谱面图片 请等待更新"
                                         "\n（温馨提示：谱面预览2只能看master与expert）")
            else:  # 匹配不到歌曲
                sendmsg(event, "没有找到你说的歌曲哦")
            return
        if "谱面预览" in event.message:
            dir = aliastochart(event.message.replace("谱面预览", ''))
            if dir is not None:  # 匹配到歌曲
                if len(dir) == 2:  # 有图片
                    bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                            message=dir[0] + fr"[CQ:image,file=file:///{botdir}\{dir[1]},cache=0]")
                else:
                    sendmsg(event, dir + "\n暂无谱面图片 请等待更新")
            else:  # 匹配不到歌曲
                sendmsg(event, "没有找到你说的歌曲哦")
            return
        if "查时间" in event.message:
            userid = event.message[event.message.find("查时间") + len("查时间"):].strip()
            if userid == '':
                bind = getqqbind(event.user_id)
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
            event.message = event.message[8:]
            para = event.message.split('to')
            sendmsg(event, charaset(para[0], para[1], event.user_id))
            return
        if event.message[:10] == 'grcharaset' and 'to' in event.message:
            event.message = event.message[10:]
            para = event.message.split('to')
            sendmsg(event, grcharaset(para[0], para[1], event.group_id))
            return
        if event.message[:8] == 'charadel':
            event.message = event.message[8:]
            sendmsg(event, charadel(event.message, event.user_id))
            return
        if event.message[:10] == 'grcharadel':
            event.message = event.message[10:]
            sendmsg(event, grcharadel(event.message, event.group_id))
            return
        if event.message[:9] == 'charainfo':
            event.message = event.message[9:]
            sendmsg(event, charainfo(event.message, event.group_id))
            return
        if event.message == '看33':
            bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                    message=fr"[CQ:image,file=file:///{botdir}\pics/33{random.randint(0, 1)}.gif,cache=0]")
            return
        if event.message[:1] == '看' or event.message[:2] == '来点':
            if event.user_id not in whitelist and event.group_id not in whitelist:
                return
            event.message = event.message.replace('看', '')
            event.message = event.message.replace('来点', '')
            resp = aliastocharaid(event.message, event.group_id)
            if resp[0] != 0:
                cardurl = get_card(resp[0])
                if 'cutout' not in cardurl:
                    cardurl = cardurl.replace('png', 'jpg')
                bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                        message=fr"[CQ:image,file=file:///{botdir}\{cardurl},cache=0]")
            return
        if event.message == '推车':
            ycmimg()
            bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                    message='' + fr"[CQ:image,file=file:///{botdir}\piccache\ycm.jpg")
            return
        if event.message[:2] == "生成":
            event.message = event.message[event.message.find("生成") + len("生成"):].strip()
            para = event.message.split(" ")
            now = int(time.time() * 1000)
            if len(para) < 2:
                para = event.message.split("/")
                if len(para) < 2:
                    sendmsg(event, '请求不对哦，/生成 这是红字 这是白字')
                    return
            genImage(para[0], para[1]).save(f"piccache/{now}.png,cache=0]")
            bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                    message=fr"[CQ:image,file=file:///{botdir}\piccache\{now}.png,cache=0]")
            return
        if event.message[:4] == 'homo':
            if event.self_id not in mainbot:
                return
            # if event.group_id in blacklist[event.self_id]['ettm']:
            #     return
            event.message = event.message[event.message.find("homo") + len("homo"):].strip()
            try:
                bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                        message=event.message + '=' + generate_homo(event.message))
            except ValueError:
                return
            return
        if event.message[:3] == "ccf":
            if event.self_id not in mainbot:
                return
            event.message = event.message[event.message.find("ccf") + len("ccf"):].strip()
            dd = dd_query.DDImageGenerate(event.message)
            image_path, vtb_following_count, total_following_count = dd.image_generate()
            bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                    message=f"{dd.username} 总共关注了 {total_following_count} 位up主, 其中 {vtb_following_count} 位是vtb。\n"
                                            f"注意: 由于b站限制, bot最多只能拉取到最近250个关注。因此可能存在数据统计不全的问题。"
                                            + fr"[CQ:image,file=file:///{image_path},cache=0]")
            return
        if event.message[:5] == "白名单添加" and event.user_id in admin:
            event.message = event.message[event.message.find("白名单添加") + len("白名单添加"):].strip()
            requestwhitelist.append(int(event.message))
            sendmsg(event, '添加成功: ' + event.message)
        if event.message[:3] == "达成率":
            event.message = event.message[event.message.find("达成率") + len("达成率"):].strip()
            para = event.message.split(' ')
            if len(para) < 5:
                return
            sendmsg(event, tasseiritsu(para))
            return
        if event.message[:2] == '机翻' and event.message[-2:] == '推特':
            if event.self_id not in mainbot:
                return
            if '最新' in event.message:
                event.message = event.message.replace('最新', '')
            twiid = event.message[2:-2]
            try:
                id = newesttwi(twiid, True)
                bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                        message=fr"[CQ:image,file=file:///{botdir}\piccache/{id}.png,cache=0]")
            except:
                sendmsg(event, '查不到捏，可能是你id有问题或者bot卡了')
            return
        if event.message[-4:] == '最新推特':
            if event.self_id not in mainbot:
                return
            try:
                id = newesttwi(event.message.replace('最新推特', '').replace(' ', ''))
                bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id,
                                        message=fr"[CQ:image,file=file:///{botdir}\piccache/{id}.png,cache=0]")
            except:
                sendmsg(event, '查不到捏，可能是你id有问题或者bot卡了')
            return
        # if 'pjsk抽卡' in event.message or 'sekai抽卡' in event.message:
        #     gachaid = event.message[event.message.find("抽卡") + len("抽卡"):].strip()
        #     gachaid = re.sub(r'\D', "", gachaid)
        #     if gachaid == '':
        #         currentgacha = getcurrentgacha()
        #         sendmsg(event,fakegacha(int(currentgacha['id']), 10, False))
        #     else:
        #         sendmsg(event,fakegacha(int(gachaid), 10, False))
        #     return
        # if 'pjsk反抽卡' in event.message or 'sekai反抽卡' in event.message:
        #     gachaid = event.message[event.message.find("抽卡") + len("抽卡"):].strip()
        #     gachaid = re.sub(r'\D', "", gachaid)
        #     if gachaid == '':
        #         currentgacha = getcurrentgacha()
        #         sendmsg(event,fakegacha(int(currentgacha['id']), 100, True))
        #     else:
        #         sendmsg(event,fakegacha(int(gachaid), 100, True))
        #     return
        # if (event.message[0:5] == 'sekai' or event.message[0:4] == 'pjsk') and '连' in event.message:
        #     gachaid = event.message[event.message.find("连") + len("连"):].strip()
        #     num = event.message[:event.message.find('连')].replace('sekai', '').replace('pjsk', '')
        #     num = re.sub(r'\D', "", num)
        #     if int(num) > 400:
        #         sendmsg(event,'太多了，少抽一点吧！')
        #         return
        #     if gachaid == '':
        #         currentgacha = getcurrentgacha()
        #         sendmsg(event,fakegacha(int(currentgacha['id']), int(num), False))
        #     else:
        #         sendmsg(event,fakegacha(int(gachaid), int(num), False))
        #     return

    except (requests.exceptions.ConnectionError, JSONDecodeError):
        sendmsg(event, '查不到数据捏，好像是bot网不好')
    except Exception as a:
        traceback.print_exc()
        sendmsg(event, '出问题了捏\n' + repr(a))


def sendmsg(event, msg):
    global send
    print(botname[event.self_id] + '发送群消息', event.group_id, msg.replace('\n', ''))
    try:
        bot.sync.send_group_msg(self_id=event.self_id, group_id=event.group_id, message=msg)
        send = False
    except aiocqhttp.exceptions.ActionFailed:
        print('发送失败')
        if send is not True:
            print('即将发送告警邮件')
            sendemail(botname[event.self_id] + '群消息发送失败', str(event.group_id) + msg)
            send = True
        else:
            print('告警邮件发过了')

bot.run(host='127.0.0.1', port=1234, debug=False)
