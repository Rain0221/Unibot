import datetime
import re
import time
from io import BytesIO

import html2text
import requests
from PIL import Image, ImageDraw, ImageFont
import os
import json
# https://github.com/twitterdev/Twitter-API-v2-sample-code/blob/main/Recent-Search/recent_search.py
# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
import xmltodict

from modules.config import bearer_token, proxies, rsshub, twitterlist, googleapiskey
from emoji2pic import Emoji2Pic
from modules.translate import baiduAPI_translate_main

search_url = "https://api.twitter.com/2/tweets/search/recent"

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
query_params = {'query': '#プロセカ協力', 'tweet.fields': 'created_at'}

class ImgText:
    font = ImageFont.truetype("fonts/SourceHanSansCN-Medium.otf", 30)

    def __init__(self, text, width=950, color=(0, 0, 0)):
        # 预设宽度 可以修改成你需要的图片宽度
        self.width = width
        # 文本
        self.text = text

        self.color = color
        # 段落 , 行数, 行高
        self.duanluo, self.note_height, self.line_height, self.line_count = self.split_text()

    def get_duanluo(self, text):
        txt = Image.new('RGB', (100, 100), (255, 255, 255))
        draw = ImageDraw.Draw(txt)
        # 所有文字的段落
        duanluo = ""
        # 宽度总和
        sum_width = 0
        # 几行
        line_count = 1
        # 行高
        line_height = 0
        for char in text:
            width, height = draw.textsize(char, ImgText.font)
            sum_width += width
            if sum_width > self.width:  # 超过预设宽度就修改段落 以及当前行数
                line_count += 1
                sum_width = 0
                duanluo += '\n'
            if line_count > 4:
                duanluo = duanluo[:-3] + '...'
                break
            duanluo += char
            line_height = max(height, line_height)
        if not duanluo.endswith('\n'):
            duanluo += '\n'
        return duanluo, line_height, line_count-1

    def split_text(self):
        # 按规定宽度分组
        line_count = 0
        max_line_height, total_lines = 0, 0
        allText = []
        for text in self.text.split('\n'):
            duanluo, line_height, line_count = self.get_duanluo(text)
            max_line_height = max(line_height, max_line_height)
            total_lines += line_count
            allText.append((duanluo, line_count))
        line_height = max_line_height
        total_height = total_lines * line_height
        return allText, total_height, line_height, line_count

    def draw_text(self):
        """
        绘图以及文字
        :return:
        """
        if self.line_count == 0:
            note_img = Image.new('RGB', (self.width+50, 80), (255, 255, 255))
        else:
            note_img = Image.new('RGB', (self.width+50, 80 + self.line_count * 30), (255, 255, 255))
        draw = ImageDraw.Draw(note_img)
        # 左上角开始
        x, y = 0, 0
        for duanluo, line_count in self.duanluo:
            draw.text((x, y), duanluo, fill=self.color, font=ImgText.font)
            y += self.line_height * line_count
        return note_img


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params, proxies=proxies)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def gentwiimg(twitterdata, translate=False):
    isRT = False
    IMG_SIZE = (1080, 4000)
    img = Image.new('RGB', IMG_SIZE, (255, 255, 255))
    draw = ImageDraw.Draw(img)

    text = html2text.html2text(twitterdata['description'])
    text = text.replace('<', '\n').replace('>', '')
    pic = []
    picnum = text.count('![]')
    for i in range(0, picnum):
        url = text[text.find('![]') + 4:text.find('orig)') + 4].replace('&amp;name=orig', '')
        pic.append(url)
        text = text.replace(f'\n![]({url})', '')
    while text[-1:] == '\n':
        text = text.rstrip('\n')
    if text[:2] == "RT":
        isRT = True
        text = text[text.find('\n'):]
    if translate:
        text = baiduAPI_translate_main(text, 'zh')
    instance = Emoji2Pic(text=text, font='fonts/SourceHanSansCN-Medium.otf', emoji_folder='AppleEmoji')
    textimg = instance.make_img()
    img.paste(textimg, (0, 140))

    userid = twitterdata['link'].replace('https://twitter.com/', '')
    userid = userid[:userid.find('/')]
    font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 40)
    draw.text((220, 110), '@' + userid, fill=(120, 120, 120), font=font_style)
    iconwide = 130
    mask = Image.new('RGBA', (iconwide, iconwide), color=(0, 0, 0, 0))
    # 画一个圆
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, iconwide, iconwide), fill=(0, 0, 0, 255))
    userinfo = getuserinfo(userid)
    icon = requests.get(userinfo[0], proxies=proxies)
    iconimg = Image.open(BytesIO(icon.content))
    iconimg = iconimg.resize((iconwide, iconwide))
    img.paste(iconimg, (60, 45), mask)
    author = userinfo[1][9:]
    if len(author) > 16:
        author = author[:16] + '...'
    font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 50)
    draw.text((220, 40), author, fill=(0, 0, 0), font=font_style)

    high = 245 + textimg.size[1]
    print()
    if '<video src=' in twitterdata['description']:
        url = twitterdata['description'][
              twitterdata['description'].find('poster="') + len('poster="'):twitterdata['description'].find(
                  '"></video>')].replace('&amp;name=orig', '')
        picre = requests.get(url, proxies=proxies)
        pic = Image.open(BytesIO(picre.content))
        if pic.size[1] < pic.size[0]:
            pic = pic.resize((950, int(950 * pic.size[1] / pic.size[0])))
            img.paste(pic, (60, 175 + textimg.size[1]))
            high = 270 + textimg.size[1] + pic.size[1]
        else:
            pic = pic.resize((int(1400 * pic.size[0] / pic.size[1]), 1400))
            img.paste(pic, (int(540 - pic.size[0] / 2), 175 + textimg.size[1]))
            high = 270 + textimg.size[1] + pic.size[1]
        play = Image.open('pics/play.png')
        play = play.resize((150, 150))
        r, g, b, mask = play.split()
        img.paste(play, (460, 80 + textimg.size[1] + int(pic.size[1] / 2)), mask)
    elif picnum == 1:
        picre = requests.get(pic[0], proxies=proxies)
        pic = Image.open(BytesIO(picre.content))
        if pic.size[1] < pic.size[0]:
            pic = pic.resize((950, int(950 * pic.size[1] / pic.size[0])))
            img.paste(pic, (60, 175 + textimg.size[1]))
            high = 270 + textimg.size[1] + pic.size[1]
        else:
            pic = pic.resize((int(1400 * pic.size[0] / pic.size[1]), 1400))
            img.paste(pic, (int(540 - pic.size[0] / 2), 175 + textimg.size[1]))
            high = 270 + textimg.size[1] + pic.size[1]
    elif picnum == 2:
        picre1 = requests.get(pic[0], proxies=proxies)
        pic1 = Image.open(BytesIO(picre1.content))
        pic1 = piccutsize(pic1, 470, 470)
        img.paste(pic1, (60, 175 + textimg.size[1]))

        picre2 = requests.get(pic[1], proxies=proxies)
        pic2 = Image.open(BytesIO(picre2.content))
        pic2 = piccutsize(pic2, 470, 470)
        img.paste(pic2, (60 + 470, 175 + textimg.size[1]))
        high = 270 + textimg.size[1] + 470
    elif picnum == 3:
        picre1 = requests.get(pic[0], proxies=proxies)
        pic1 = Image.open(BytesIO(picre1.content))
        pic1 = piccutsize(pic1, 470, 470)
        img.paste(pic1, (60, 175 + textimg.size[1]))

        picre2 = requests.get(pic[1], proxies=proxies)
        pic2 = Image.open(BytesIO(picre2.content))
        pic2 = piccutsize(pic2, 470, 470)
        img.paste(pic2, (60 + 470, 175 + textimg.size[1]))

        picre3 = requests.get(pic[1], proxies=proxies)
        pic3 = Image.open(BytesIO(picre3.content))
        pic3 = piccutsize(pic3, 940, 470)
        img.paste(pic3, (60, 175 + 470 + textimg.size[1]))

        high = 270 + textimg.size[1] + 470 * 2
    elif picnum == 4:
        picre1 = requests.get(pic[0], proxies=proxies)
        pic1 = Image.open(BytesIO(picre1.content))
        pic1 = piccutsize(pic1, 470, 470)
        img.paste(pic1, (60, 175 + textimg.size[1]))

        picre2 = requests.get(pic[1], proxies=proxies)
        pic2 = Image.open(BytesIO(picre2.content))
        pic2 = piccutsize(pic2, 470, 470)
        img.paste(pic2, (60 + 470, 175 + textimg.size[1]))

        picre3 = requests.get(pic[2], proxies=proxies)
        pic3 = Image.open(BytesIO(picre3.content))
        pic3 = piccutsize(pic3, 470, 470)
        img.paste(pic3, (60, 175 + 470 + textimg.size[1]))

        picre4 = requests.get(pic[3], proxies=proxies)
        pic4 = Image.open(BytesIO(picre4.content))
        pic4 = piccutsize(pic4, 470, 470)
        img.paste(pic4, (60 + 470, 175 + 470 + textimg.size[1]))

        high = 270 + textimg.size[1] + 470 * 2
    elif 'youtu.be/' in text:
        pattern = re.compile('(?<=youtu.be/)([a-zA-Z0-9-_=]+)')
        youtubeid = pattern.search(text).group()
        redata = requests.get(f'https://www.googleapis.com/youtube/v3/videos?id={youtubeid}&part=snippet%2CcontentDetails%2Cstatistics&key={googleapiskey}', proxies=proxies)
        youtubedata = json.loads(redata.content)
        picre = requests.get(youtubedata['items'][0]['snippet']['thumbnails']['medium']['url'], proxies=proxies)
        pic = Image.open(BytesIO(picre.content))
        pic = pic.resize((950, int(950 * pic.size[1] / pic.size[0])))
        img.paste(pic, (60, 235 + textimg.size[1]))

        play = Image.open('pics/play.png')
        play = play.resize((150, 150))
        r, g, b, mask = play.split()
        img.paste(play, (460, 140 + textimg.size[1] + int(pic.size[1] / 2)), mask)

        play = Image.open('pics/youtube.png')
        img.paste(play, (50, 160 + textimg.size[1]))

        font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 40)
        draw.text((60, 250 + textimg.size[1] + pic.size[1]),
                  youtubedata['items'][0]['snippet']['title'], fill=(0, 0, 0), font=font_style)

        n = ImgText(youtubedata['items'][0]['snippet']['description'].replace('\n', ' '))
        des = n.draw_text()
        img.paste(des, (60, 320 + textimg.size[1] + pic.size[1]))

        play = Image.open('pics/getyoutube.png')
        play = play.resize((1000, int(1000*play.size[1]/play.size[0])))
        img.paste(play, (40, 300 + textimg.size[1] + pic.size[1] + des.size[1]))

        high = 500 + textimg.size[1] + pic.size[1] + des.size[1]

    utc_date = datetime.datetime.strptime(twitterdata['pubDate'], "%a, %d %b %Y %H:%M:%S GMT")
    local_date = utc_date + datetime.timedelta(hours=8)
    time_str = local_date.strftime("%H:%M") + '・' + local_date.strftime("%Y-%m-%d")
    font_style = ImageFont.truetype(r"fonts\SourceHanSansCN-Bold.otf", 35)
    draw.text((55, high - 70),
              time_str + '・Generated by Unibot', fill=(100, 100, 100), font=font_style)
    img = img.crop((0, 0, 1080, high))
    if isRT:
        n = ImgText(twitterdata['author'] + '转推了', width=850, color=(100, 100, 100))
        rt = n.draw_text()
        imgnew = Image.new('RGB', (img.size[0], img.size[1] + rt.size[1] - 20), (255, 255, 255))
        rticon = Image.open('pics/rt.png')
        imgnew.paste(rticon, (65, 0))
        imgnew.paste(rt, (150, 0))
        imgnew.paste(img, (0, rt.size[1] - 20))
        imgnew.save(f"piccache/{twitterdata['link'][twitterdata['link'].find('tus/') + 4:]}.png")
        return
    img.save(f"piccache/{twitterdata['link'][twitterdata['link'].find('tus/') + 4:]}.png")
    return

def newesttwi(twitterid, translate=False):
    rss = requests.get(rsshub + 'twitter/user/' + twitterid, proxies=proxies)
    listjson = xmltodict.parse(rss.text)
    gentwiimg(listjson['rss']['channel']['item'][0], translate)
    link = listjson['rss']['channel']['item'][0]['link']
    twiid = link[link.find('status/') + 7:]
    return twiid

def piccutsize(pic, wide, high):
    if pic.size[0] / pic.size[1] < wide / high:
        pic = pic.resize((wide, int(wide * pic.size[1] / pic.size[0])))
        add = int((pic.size[1] - high) / 2)
        pic = pic.crop((0, add, wide, high + add))
    if pic.size[0] / pic.size[1] > wide / high:
        pic = pic.resize((int(high * pic.size[0] / pic.size[1]), high))
        add = int((pic.size[0] - wide) / 2)
        pic = pic.crop((add, 0, wide + add, high))

    return pic


def getuserinfo(userid):
    rss = requests.get(rsshub + 'twitter/user/' + userid, proxies=proxies)
    listjson = xmltodict.parse(rss.text)
    return listjson['rss']['channel']['image']['url'].replace('normal', '400x400'), listjson['rss']['channel']['title']


if __name__ == '__main__':
    rss = requests.get(rsshub + 'twitter/list/' + twitterlist, proxies=proxies)
    listjson = xmltodict.parse(rss.text)
    print(listjson)
    # with open('piccache/miru.xml', 'r', encoding='utf-8') as f:
    #     listjson = xmltodict.parse(f.read())
    # for i in range(5, 10):
    #     gentwiimg(listjson['rss']['channel']['item'][i])
    # gentwiimg(listjson['rss']['channel']['item'][4])
    # twitter = html2text.html2text(listjson['rss']['channel']['item'][3]['description'])
    # instance = Emoji2Pic(text=twitter, font='fonts/SourceHanSansCN-Medium.otf', emoji_folder='AppleEmoji')
    # img = instance.make_img()
    # img.show()
