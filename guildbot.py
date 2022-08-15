import re
import time
import traceback

import requests
from json import JSONDecodeError
import bot_api
from bot_api.utils import yaml_util
from modules.api import gacha
from modules.config import piccacheurl, charturl, asseturl
from modules.cyo5000 import cyo5000

from modules.gacha import getcharaname, fakegacha, getcurrentgacha
from modules.chara import charaset, grcharaset, charadel, charainfo, grcharadel, aliastocharaid, get_card
from modules.musics import hotrank, levelrank, parse_bpm, aliastochart, idtoname
from modules.pjskguess import getrandomjacket, cutjacket, getrandomchart, cutchartimg, getrandomcard, cutcard
from modules.pjskinfo import aliastomusicid, drawpjskinfo, pjskset, pjskdel, pjskalias
from modules.profileanalysis import daibu, rk, pjskjindu, pjskprofile, pjskb30
from modules.sk import sk, getqqbind, bindid, setprivate, skyc, gettime, verifyid
from modules.texttoimg import texttoimg, ycmimg

token = yaml_util.read('yamls/config.yaml')
bot = bot_api.BotApp(token['bot']['id'], token['bot']['token'], token['bot']['secret'],
                     is_sandbox=False, debug=False, api_return_pydantic=True,
                     inters=[bot_api.Intents.GUILDS, bot_api.Intents.AT_MESSAGES, bot_api.Intents.GUILD_MEMBERS])
pjskguess = {}
charaguess = {}


@bot.receiver(bot_api.structs.Codes.SeverCode.BotGroupAtMessage)
def get_at_message(chain: bot_api.structs.Message):
    global pjskguess
    global charaguess
    chain.content = chain.content[chain.content.find(">") + len(">"):].strip()
    bot.logger(f"收到来自频道:{chain.guild_id} 子频道: {chain.channel_id} "
               f"内用户: {chain.author.username}({chain.author.id}) 的消息: {chain.content} ({chain.id})")
    qunnum = int(chain.channel_id)
    # if "你好" in chain.content:
    #    bot.api_send_message(chain.channel_id, chain.id, "hello world!")
    if chain.content[0:1] == '/':
        chain.content = chain.content[1:]
    try:
        if chain.content == 'help':
            bot.api_send_message(chain.channel_id, chain.id, 'bot帮助文档：https://bot.unijzlsx.com/guild/')
            return
        if chain.content[:8] == 'pjskinfo' or chain.content[:4] == 'song':
            if chain.content[:8] == 'pjskinfo':
                resp = aliastomusicid(chain.content[chain.content.find("pjskinfo") + len("pjskinfo"):].strip())
            else:
                resp = aliastomusicid(chain.content[chain.content.find("song") + len("song"):].strip())
            if resp['musicid'] == 0:
                bot.api_send_message(chain.channel_id, chain.id, '没有找到你要的歌曲哦')
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
                bot.api_send_message(chain.channel_id, chain.id, text, f"{piccacheurl}pjskinfo{resp['musicid']}.png")
            return
        if chain.content[:7] == 'pjskset' and 'to' in chain.content:
            # 频道bot不需要昵称设置黑名单 只允许在官方频道设置 发现有人乱设踢了就好了
            if chain.channel_id != '6781353':
                bot.api_send_message(chain.channel_id, chain.id, '为方便管理，请在bot频道的设置昵称专用区使用该命令\n点击bot头像即可查看bot频道')
                return
            chain.content = chain.content[7:]
            para = chain.content.split('to')
            resp = pjskset(para[0], para[1], chain.author.id, chain.author.username, 'bot官方频道内')
            bot.api_send_message(chain.channel_id, chain.id, resp)
            return
        if chain.content[:7] == 'pjskdel':
            if chain.channel_id != '6781353':
                bot.api_send_message(chain.channel_id, chain.id, '为方便管理，请在bot频道的设置昵称专用区使用该命令\n点击bot头像即可查看bot频道')
                return
            chain.content = chain.content[7:]
            resp = pjskdel(chain.content, chain.author.id, chain.author.username, 'bot官方频道内')
            bot.api_send_message(chain.channel_id, chain.id, resp)
            return
        if chain.content[:9] == 'pjskalias':
            chain.content = chain.content[9:]
            resp = pjskalias(chain.content)
            bot.api_send_message(chain.channel_id, chain.id, resp)
            return
        if chain.content == "sekai真抽卡":
            return
            result = gacha()
            bot.api_send_message(chain.channel_id, chain.id, result)
            return
        if chain.content == "sk预测":
            texttoimg(skyc(), 500, 'skyc')
            bot.api_send_message(chain.channel_id, chain.id, 'sk预测', f"{piccacheurl}skyc.png")
            return
        if chain.content[:2] == "sk":
            if chain.content == "sk":
                bind = getqqbind(chain.author.id)
                if bind is None:
                    bot.api_send_message(chain.channel_id, chain.id, '你没有绑定id！')
                    return
                result = sk(bind[1], None, bind[2])
                bot.api_send_message(chain.channel_id, chain.id, result.replace('(3-3.dev)', ''))
                # 频道bot不允许未经审核的url
            else:
                userid = chain.content.replace("sk", "")
                userid = re.sub(r'\D', "", userid)
                if userid == '':
                    bot.api_send_message(chain.channel_id, chain.id, '你这id有问题啊')
                    return
                if int(userid) > 10000000:
                    result = sk(userid)
                else:
                    result = sk(None, userid)
                bot.api_send_message(chain.channel_id, chain.id, result.replace('(3-3.dev)', ''))
                # 频道bot不允许未经审核的url
                return
        if chain.content[:2] == "rk":
            if chain.content == "rk":
                bind = getqqbind(chain.author.id)
                if bind is None:
                    bot.api_send_message(chain.channel_id, chain.id, '你没有绑定id！')
                    return
                result = rk(bind[1], None, bind[2])
                bot.api_send_message(chain.channel_id, chain.id, result)
            else:
                userid = chain.content.replace("rk", "")
                userid = re.sub(r'\D', "", userid)
                if userid == '':
                    bot.api_send_message(chain.channel_id, chain.id, '你这id有问题啊')
                    return
                if int(userid) > 10000000:
                    result = rk(userid)
                else:
                    result = rk(None, userid)
                bot.api_send_message(chain.channel_id, chain.id, result)
            return
        if chain.content[:2] == "绑定":
            userid = chain.content.replace("绑定", "")
            userid = re.sub(r'\D', "", userid)
            bot.api_send_message(chain.channel_id, chain.id, bindid(chain.author.id, userid))
            return
        if chain.content == "不给看":
            if setprivate(chain.author.id, 1):
                bot.api_send_message(chain.channel_id, chain.id, '不给看！')
            else:
                bot.api_send_message(chain.channel_id, chain.id, '你还没有绑定哦')
            return
        if chain.content == "给看":
            if setprivate(chain.author.id, 0):
                bot.api_send_message(chain.channel_id, chain.id, '给看！')
            else:
                bot.api_send_message(chain.channel_id, chain.id, '你还没有绑定哦')
            return
        if chain.content[:2] == "逮捕":
            if chain.content == "逮捕":
                bind = getqqbind(chain.author.id)
                if bind is None:
                    bot.api_send_message(chain.channel_id, chain.id, '查不到捏，可能是没绑定')
                    return
                result = daibu(bind[1], bind[2])
                bot.api_send_message(chain.channel_id, chain.id, result)
            else:
                userid = chain.content.replace("逮捕", "")
                if '<@!' in userid:
                    qq = re.sub(r'\D', "", userid)
                    bind = getqqbind(qq)
                    if bind is None:
                        bot.api_send_message(chain.channel_id, chain.id, '查不到捏，可能是没绑定')
                        return
                    elif bind[2] and qq != str(chain.author.id):
                        bot.api_send_message(chain.channel_id, chain.id, '查不到捏，可能是不给看')
                        return
                    else:
                        result = daibu(bind[1], bind[2])
                        bot.api_send_message(chain.channel_id, chain.id, result)
                        return
                userid = re.sub(r'\D', "", userid)
                if userid == '':
                    bot.api_send_message(chain.channel_id, chain.id, '你这id有问题啊')
                    return
                if int(userid) > 10000000:
                    result = daibu(userid)
                else:
                    result = daibu(userid)
                bot.api_send_message(chain.channel_id, chain.id, result)
            return
        if chain.content == "pjsk进度":
            bind = getqqbind(chain.author.id)
            if bind is None:
                bot.api_send_message(chain.channel_id, chain.id, '查不到捏，可能是没绑定')
                return
            pjskjindu(bind[1], bind[2])
            bot.api_send_message(chain.channel_id, chain.id, 'pjsk进度', f"{piccacheurl}{bind[1]}jindu.png")
            print(f"{piccacheurl}{bind[1]}jindu.png")
            return
        if chain.content == "pjsk b30":
            bind = getqqbind(chain.author.id)
            if bind is None:
                bot.api_send_message(chain.channel_id, chain.id, '查不到捏，可能是没绑定')
                return
            pjskb30(bind[1], bind[2])
            bot.api_send_message(chain.channel_id, chain.id, "pjsk b30", f"{piccacheurl}{bind[1]}b30.png")
            return
        try:
            if chain.content == "热度排行":
                hotrank()
                bot.api_send_message(chain.channel_id, chain.id, "热度排行", f"{piccacheurl}hotrank.png")
                return
            if "难度排行" in chain.content:
                if chain.content[:2] == 'fc':
                    fcap = 1
                elif chain.content[:2] == 'ap':
                    fcap = 2
                else:
                    fcap = 0
                chain.content = chain.content[chain.content.find("难度排行") + len("难度排行"):].strip()
                para = chain.content.split(" ")
                if len(para) == 1:
                    success = levelrank(int(chain.content), 'master', fcap)
                else:
                    success = levelrank(int(para[0]), para[1], fcap)
                if success:
                    if len(para) == 1:
                        bot.api_send_message(chain.channel_id, chain.id, '难度排行',
                                             f"{piccacheurl}{para[0]}master{fcap}.png")
                    else:
                        bot.api_send_message(chain.channel_id, chain.id, '难度排行',
                                             f"{piccacheurl}{para[0]}{para[1]}{fcap}.png")
                else:
                    bot.api_send_message(chain.channel_id, chain.id,
                                         '参数错误，指令：/难度排行 定数 难度，'
                                         '难度支持的输入: easy, normal, hard, expert, master，如/难度排行 28 expert')
                return
        except:
            bot.api_send_message(chain.channel_id, chain.id,
                                 '参数错误，指令：/难度排行 定数 难度，'
                                 '难度支持的输入: easy, normal, hard, expert, master，如/难度排行 28 expert')
        if chain.content == "pjskprofile" or chain.content == "个人信息":
            bind = getqqbind(chain.author.id)
            if bind is None:
                bot.api_send_message(chain.channel_id, chain.id, '查不到捏，可能是没绑定')
                return
            pjskprofile(bind[1], bind[2])
            bot.api_send_message(chain.channel_id, chain.id, "pjskprofile", f"{piccacheurl}{bind[1]}profile.png")
            return
        if chain.content[:7] == 'pjskbpm' or chain.content[:3] == 'bpm':
            parm = chain.content[chain.content.find("bpm") + len("bpm"):].strip()
            resp = aliastomusicid(parm)
            if resp['musicid'] == 0:
                bot.api_send_message(chain.channel_id, chain.id, '没有找到你要的歌曲哦')
                return
            else:
                bpm = parse_bpm(resp['musicid'])
                text = ''
                for bpms in bpm[1]:
                    text = text + ' - ' + str(bpms['bpm']).replace('.0', '')
                text = f"{resp['name']}\n匹配度:{round(resp['match'], 4)}\nBPM: " + text[3:]
                bot.api_send_message(chain.channel_id, chain.id, text)
            return
        if "谱面预览2" in chain.content:
            dir = aliastochart(chain.content.replace("谱面预览2", ''), True)
            if dir is not None:  # 匹配到歌曲
                if len(dir) == 2:  # 有图片
                    bot.api_send_message(chain.channel_id, chain.id, dir[0], dir[1].replace('charts/', charturl))
                else:
                    bot.api_send_message(chain.channel_id, chain.id, dir + "\n暂无谱面图片 请等待更新"
                                                                           "\n（温馨提示：谱面预览2只能看master与expert）")
            else:  # 匹配不到歌曲
                bot.api_send_message(chain.channel_id, chain.id, "没有找到你说的歌曲哦")
            return
        if "谱面预览" in chain.content:
            dir = aliastochart(chain.content.replace("谱面预览", ''))
            if dir is not None:  # 匹配到歌曲
                if len(dir) == 2:  # 有图片
                    bot.api_send_message(chain.channel_id, chain.id, dir[0], dir[1].replace('charts/', charturl))
                else:
                    bot.api_send_message(chain.channel_id, chain.id, dir + "\n暂无谱面图片 请等待更新")
            else:  # 匹配不到歌曲
                bot.api_send_message(chain.channel_id, chain.id, "没有找到你说的歌曲哦")
            return
        elif "查时间" in chain.content:
            userid = chain.content[chain.content.find("查时间") + len("查时间"):].strip()
            if userid == '':
                bind = getqqbind(chain.author.id)
                if bind is None:
                    bot.api_send_message(chain.channel_id, chain.id, '你没有绑定id！')
                    return
                userid = bind[1]
            userid = re.sub(r'\D', "", userid)
            if userid == '':
                bot.api_send_message(chain.channel_id, chain.id, '你这id有问题啊')
                return
            if verifyid(userid):
                bot.api_reply_message(chain, time.strftime('注册时间：%Y-%m-%d %H:%M:%S',
                                                           time.localtime(gettime(userid))))
            else:
                bot.api_send_message(chain.channel_id, chain.id, '你这id有问题啊')
            return
        if chain.content[:8] == 'charaset' and 'to' in chain.content:
            if chain.channel_id != '6781353':
                bot.api_send_message(chain.channel_id, chain.id, '为方便管理，请在bot频道的设置昵称专用区使用该命令\n点击bot头像即可查看bot频道')
                return
            chain.content = chain.content[8:]
            para = chain.content.split('to')
            bot.api_send_message(chain.channel_id, chain.id, charaset(para[0], para[1], chain.author.id, chain.author.username, 'bot官方频道内'))
            return
        if chain.content[:10] == 'grcharaset' and 'to' in chain.content:
            chain.content = chain.content[10:]
            para = chain.content.split('to')
            bot.api_send_message(chain.channel_id, chain.id, grcharaset(para[0], para[1], chain.guild_id))
            return
        if chain.content[:8] == 'charadel':
            if chain.channel_id != '6781353':
                bot.api_send_message(chain.channel_id, chain.id, '为方便管理，请在bot频道的设置昵称专用区使用该命令\n点击bot头像即可查看bot频道')
                return
            chain.content = chain.content[8:]
            bot.api_send_message(chain.channel_id, chain.id, charadel(chain.content, chain.author.id, chain.author.username, 'bot官方频道内'))
            return
        if chain.content[:10] == 'grcharadel':
            chain.content = chain.content[10:]
            bot.api_send_message(chain.channel_id, chain.id, grcharadel(chain.content, chain.guild_id))
            return
        if chain.content[:9] == 'charainfo':
            chain.content = chain.content[9:]
            bot.api_send_message(chain.channel_id, chain.id, charainfo(chain.content, chain.guild_id))
            return
        if chain.content[:1] == '看' or chain.content[:2] == '来点':
            chain.content = chain.content.replace('看', '')
            chain.content = chain.content.replace('来点', '')
            resp = aliastocharaid(chain.content, chain.guild_id)
            if resp[0] != 0:
                cardurl = get_card(resp[0])
                if 'cutout' not in cardurl:
                    cardurl = cardurl.replace('png', 'jpg')
                bot.api_send_message(chain.channel_id, chain.id, '',
                                     cardurl.replace('data/assets/sekai/assetbundle/resources/', asseturl))
            return
        if chain.content == '推车':
            ycmimg()
            bot.api_send_message(chain.channel_id, chain.id, '', f"{piccacheurl}ycm.png")
            return
        if "生成" in chain.content:
            if chain.content[:2] == "生成":
                rainbow = False
            elif chain.content[:4] == "彩虹生成":
                rainbow = True
            else:
                return
            chain.content = chain.content[chain.content.find("生成") + len("生成"):].strip()
            para = chain.content.split(" ")
            now = int(time.time() * 1000)
            if len(para) < 2:
                para = chain.content.split("/")
                if len(para) < 2:
                    bot.api_send_message(chain.channel_id, chain.id, '请求不对哦，/生成 这是红字 这是白字')
                    return
            cyo5000(para[0], para[1], f"piccache/{now}.png", rainbow)
            bot.api_send_message(chain.channel_id, chain.id, "", f"{piccacheurl}{now}.png")
            return
        if 'pjsk抽卡' in chain.content or 'sekai抽卡' in chain.content:
            gachaid = chain.content[chain.content.find("抽卡") + len("抽卡"):].strip()
            gachaid = re.sub(r'\D', "", gachaid)
            if gachaid == '':
                currentgacha = getcurrentgacha()
                bot.api_send_message(chain.channel_id, chain.id, fakegacha(int(currentgacha['id']), 10, False))
            else:
                bot.api_send_message(chain.channel_id, chain.id, fakegacha(int(gachaid), 10, False))
            return
        if 'pjsk反抽卡' in chain.content or 'sekai反抽卡' in chain.content:
            gachaid = chain.content[chain.content.find("抽卡") + len("抽卡"):].strip()
            gachaid = re.sub(r'\D', "", gachaid)
            if gachaid == '':
                currentgacha = getcurrentgacha()
                bot.api_send_message(chain.channel_id, chain.id, fakegacha(int(currentgacha['id']), 10, True))
            else:
                bot.api_send_message(chain.channel_id, chain.id, fakegacha(int(gachaid), 10, True))
            return
        if (chain.content[0:5] == 'sekai' or chain.content[0:4] == 'pjsk') and '连' in chain.content:
            gachaid = chain.content[chain.content.find("连") + len("连"):].strip()
            num = chain.content[:chain.content.find('连')].replace('sekai', '').replace('pjsk', '')
            num = re.sub(r'\D', "", num)
            if int(num) > 400:
                bot.api_send_message(chain.channel_id, chain.id, '太多了，少抽一点吧！')
                return
            if gachaid == '':
                currentgacha = getcurrentgacha()
                bot.api_send_message(chain.channel_id, chain.id, fakegacha(int(currentgacha['id']), int(num), False))
            else:
                bot.api_send_message(chain.channel_id, chain.id, fakegacha(int(gachaid), int(num), False))
            return



        # 猜曲
        if ('猜曲' in chain.content and chain.content[:4] == 'pjsk'
                and chain.content != 'pjsk猜曲 3' and chain.content != 'pjsk猜曲 4'):
            try:
                isgoing = charaguess[qunnum]['isgoing']
                if isgoing:
                    bot.api_send_message(chain.channel_id, chain.id, '已经开启猜卡面！')
                    return
            except KeyError:
                pass

            try:
                isgoing = pjskguess[qunnum]['isgoing']
                if isgoing:
                    bot.api_send_message(chain.channel_id, chain.id, '已经开启猜曲！')
                    return
                else:
                    musicid = getrandomjacket()
                    pjskguess[qunnum] = {'isgoing': True, 'musicid': musicid,
                                         'starttime': int(time.time())}
            except KeyError:
                musicid = getrandomjacket()
                pjskguess[qunnum] = {'isgoing': True, 'musicid': musicid, 'starttime': int(time.time())}
            if chain.content == 'pjsk猜曲' or chain.content == 'pjsk猜曲 1':
                cutjacket(musicid, chain.channel_id, size=140, isbw=False)
            elif chain.content == 'pjsk阴间猜曲' or chain.content == 'pjsk猜曲 2':
                cutjacket(musicid, chain.channel_id, size=140, isbw=True)
            elif chain.content == 'pjsk非人类猜曲':
                cutjacket(musicid, chain.channel_id, size=30, isbw=False)
            else:
                cutjacket(musicid, chain.channel_id, size=140, isbw=False)
            bot.api_send_message(chain.channel_id, chain.id,
                                 'PJSK曲绘竞猜 （随机裁切）\n艾特我+你的答案以参加猜曲（不要使用回复）\n\n你有50秒的时间回答\n可手动发送“结束猜曲”来结束猜曲',
                                 f'{piccacheurl}{chain.channel_id}.png')
            return
        if chain.content == 'pjsk猜谱面' or chain.content == 'pjsk猜曲 3':
            try:
                isgoing = charaguess[qunnum]['isgoing']
                if isgoing:
                    bot.api_send_message(chain.channel_id, chain.id, '已经开启猜卡面！')
                    return
            except KeyError:
                pass

            try:
                isgoing = pjskguess[qunnum]['isgoing']
                if isgoing:
                    bot.api_send_message(chain.channel_id, chain.id, '已经开启猜曲！')
                    return
                else:
                    musicid = getrandomchart()
                    pjskguess[qunnum] = {'isgoing': True, 'musicid': musicid,
                                         'starttime': int(time.time())}
            except KeyError:
                musicid = getrandomchart()
                pjskguess[qunnum] = {'isgoing': True, 'musicid': musicid, 'starttime': int(time.time())}
            cutchartimg(musicid, chain.channel_id)
            bot.api_send_message(chain.channel_id, chain.id,
                                 'PJSK谱面竞猜（随机裁切）\n艾特我+你的答案以参加猜曲（不要使用回复）\n\n你有50秒的时间回答\n可手动发送“结束猜曲”来结束猜曲',
                                 f'{piccacheurl}{chain.channel_id}.png')
            return
        if chain.content == 'pjsk猜卡面' or chain.content == 'pjsk猜曲 4':
            try:
                isgoing = pjskguess[qunnum]['isgoing']
                if isgoing:
                    bot.api_send_message(chain.channel_id, chain.id, '已经开启猜曲！')
                    return
            except KeyError:
                pass
            # getrandomcard() return characterId, assetbundleName, prefix, cardRarityType
            try:
                isgoing = charaguess[qunnum]['isgoing']
                if isgoing:
                    bot.api_send_message(chain.channel_id, chain.id, '已经开启猜曲！')
                    return
                else:
                    cardinfo = getrandomcard()
                    charaguess[qunnum] = {'isgoing': True, 'charaid': cardinfo[0],
                                          'assetbundleName': cardinfo[1], 'prefix': cardinfo[2],
                                          'starttime': int(time.time())}
            except KeyError:
                cardinfo = getrandomcard()
                charaguess[qunnum] = {'isgoing': True, 'charaid': cardinfo[0],
                                      'assetbundleName': cardinfo[1], 'prefix': cardinfo[2],
                                      'starttime': int(time.time())}

            charaguess[qunnum]['istrained'] = cutcard(cardinfo[1], cardinfo[3], chain.channel_id)
            bot.api_send_message(chain.channel_id, chain.id,
                                 'PJSK猜卡面\n你有30秒的时间回答\n艾特我+你的答案（只猜角色）以参加猜曲（不要使用回复）\n发送「结束猜卡面」可退出猜卡面模式',
                                 f'{piccacheurl}{chain.channel_id}.png')
            print(charaguess)
            return
        if chain.content == '结束猜曲':
            try:
                isgoing = pjskguess[qunnum]['isgoing']
                if isgoing:
                    dir = f"{asseturl}/startapp/music/jacket/" \
                          f"jacket_s_{str(pjskguess[qunnum]['musicid']).zfill(3)}/" \
                          f"jacket_s_{str(pjskguess[qunnum]['musicid']).zfill(3)}.png"
                    text = '正确答案：' + idtoname(pjskguess[qunnum]['musicid'])
                    pjskguess[qunnum]['isgoing'] = False
                    bot.api_send_message(chain.channel_id, chain.id, text, dir)
            except KeyError:
                pass
            return
        if chain.content == '结束猜卡面':
            try:
                isgoing = charaguess[qunnum]['isgoing']
                if isgoing:
                    if charaguess[qunnum]['istrained']:
                        dir = f'{asseturl}/startapp/' \
                              f"character/member/{charaguess[qunnum]['assetbundleName']}/card_after_training.jpg"
                    else:
                        dir = f'{asseturl}/startapp/' \
                              f"character/member/{charaguess[qunnum]['assetbundleName']}/card_normal.jpg"
                    text = f"正确答案：{charaguess[qunnum]['prefix']} - {getcharaname(charaguess[qunnum]['charaid'])}"
                    charaguess[qunnum]['isgoing'] = False

                    bot.api_send_message(chain.channel_id, chain.id, text, dir)
            except KeyError:
                pass
            return
        # 频道版本已经把艾特自己的前缀删了 直接判断
        # 判断有没有猜曲
        try:
            isgoing = pjskguess[qunnum]['isgoing']
            if isgoing:
                answer = chain.content[chain.content.find("]") + len("]"):].strip()
                resp = aliastomusicid(answer)
                if resp['musicid'] == 0:
                    bot.api_send_message(chain.channel_id, chain.id, '没有找到你说的歌曲哦')
                    return
                else:
                    if resp['musicid'] == pjskguess[qunnum]['musicid']:
                        text = f'<@!{chain.author.id}> 您猜对了'
                        if int(time.time()) > pjskguess[qunnum]['starttime'] + 45:
                            text = text + '，回答已超时'
                        dir = f"{asseturl}/startapp/music/jacket/" \
                              f"jacket_s_{str(pjskguess[qunnum]['musicid']).zfill(3)}/" \
                              f"jacket_s_{str(pjskguess[qunnum]['musicid']).zfill(3)}.png"
                        text = text + '\n正确答案：' + idtoname(pjskguess[qunnum]['musicid'])
                        pjskguess[qunnum]['isgoing'] = False
                        bot.api_send_message(chain.channel_id, chain.id, text, dir)
                    else:
                        bot.api_send_message(chain.channel_id, chain.id,
                                             f"<@!{chain.author.id}> 您猜错了，答案不是{idtoname(resp['musicid'])}哦")
        except KeyError:
            pass

        # 判断有没有猜卡面
        try:
            isgoing = charaguess[qunnum]['isgoing']
            if isgoing:
                # {'isgoing', 'charaid', 'assetbundleName', 'prefix', 'starttime'}
                answer = chain.content[chain.content.find("]") + len("]"):].strip()
                resp = aliastocharaid(answer)
                if resp[0] == 0:
                    bot.api_send_message(chain.channel_id, chain.id, '没有找到你说的角色哦')
                    return
                else:
                    if resp[0] == charaguess[qunnum]['charaid']:
                        text = f'<@!{chain.author.id}> 您猜对了'
                        if int(time.time()) > charaguess[qunnum]['starttime'] + 45:
                            text = text + '，回答已超时'
                        if charaguess[qunnum]['istrained']:
                            dir = f'{asseturl}/startapp/' \
                                  f"character/member/{charaguess[qunnum]['assetbundleName']}/card_after_training.jpg"
                        else:
                            dir = f'{asseturl}/startapp/' \
                                  f"character/member/{charaguess[qunnum]['assetbundleName']}/card_normal.jpg"
                        text = text + f"\n正确答案：{charaguess[qunnum]['prefix']} - {resp[1]}"
                        charaguess[qunnum]['isgoing'] = False
                        bot.api_send_message(chain.channel_id, chain.id, text, dir)
                    else:
                        bot.api_send_message(chain.channel_id, chain.id,
                                             f"<@!{chain.author.id}> 您猜错了，答案不是{resp[1]}哦")
        except KeyError:
            pass
    except (requests.exceptions.ConnectionError, JSONDecodeError):
        bot.api_send_message(chain.channel_id, chain.id, r'查不到数据捏，好像是bot网不好')
    except Exception as a:
        traceback.print_exc()
        bot.api_send_message(chain.channel_id, chain.id, '出问题了捏\n' + repr(a))


bot.start()
