import datetime
import textwrap
from emoji2pic import Emoji2Pic
from modules.profileanalysis import daibu
from modules.sk import skyc
from modules.twitter import connect_to_endpoint
from PIL import Image, ImageDraw, ImageFont

def ycmimg():
    c = ''
    search_url = "https://api.twitter.com/2/tweets/search/recent"
    query_params = {'query': '#プロセカ協力', 'tweet.fields': 'created_at'}
    json_response = connect_to_endpoint(search_url, query_params)
    count = 0
    for datas in json_response['data']:
        count = count + 1
        utc_date = datetime.datetime.strptime(datas['created_at'], "%Y-%m-%dT%H:%M:%S.000Z")
        local_date = utc_date + datetime.timedelta(hours=8)
        c = c + str((datetime.datetime.now() - local_date).seconds) + '秒前' + '\n'
        c = c + datas['text'].replace("　", "  ") + '\n——————————————————————\n'
        if count == 6:
            break

    instance = Emoji2Pic(text=c, font='fonts\SourceHanSansCN-Medium.otf', emoji_folder='AppleEmoji')
    img = instance.make_img()
    img.save('piccache/ycm.png')

def texttoimg(text, width, savefilename):
    IMG_SIZE = (width, 40 + (text.count('\n') + 1) * 34)
    img_1 = Image.new('RGB', IMG_SIZE, (255, 255, 255))
    draw = ImageDraw.Draw(img_1)
    font = ImageFont.truetype(r'fonts\SourceHanSansCN-Medium.otf', 25)
    draw.text((20, 20), text, '#000000', font)
    img_1.save(fr'piccache\{savefilename}.png')

if __name__ == '__main__':
    ycmimg()
