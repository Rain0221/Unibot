from PIL import Image, ImageFont, ImageDraw, ImageOps
from .get_data import *
import requests
import random
import colorsys
from io import BytesIO
import os

spath = os.path.split(__file__)[0]

class DDImageGenerate(GetUserFollowingVTB):
    def __init__(self, username, max_follow_list=2000):
        super().__init__(username, max_follow_list=max_follow_list)

    @staticmethod
    def timestamp_to_text(timestamp: int, _format="%Y-%m-%d %H:%M:%S"):
        if timestamp > 9999999999:
            timestamp = timestamp / 1000
        ret = time.strftime(_format, time.localtime(timestamp))
        return ret

    @staticmethod
    def paste_image(pt, im, x, y, w=-1, h=-1, with_mask=True):
        w = im.width if w == -1 else w
        h = im.height if h == -1 else h
        im = im.resize((w, h))
        pt.paste(im, (x, y, x + w, y + h), im.convert("RGBA") if with_mask else None)

    @staticmethod
    def mask_img(img: Image, mask_path: str, size=None) -> Image:
        imsize = img.size if size is None else size
        border = Image.open(mask_path).resize(imsize, Image.ANTIALIAS).convert('L')
        invert = ImageOps.invert(border)
        img.putalpha(invert)
        return img

    def single_card(self, vdata: models.VTBInfo):
        pt = Image.new("RGBA", (704, 195), (238, 228, 229))
        draw = ImageDraw.Draw(pt)

        try:
            im = Image.open(BytesIO(requests.get(vdata.topPhoto).content))
            self.paste_image(pt, im, 0, 0, 704, 110)  # 头图
        except Exception as e:
            print(f"获取空间头图失败", e)

        im = Image.open(f"{spath}/src/bw_small.png")
        self.paste_image(pt, im, 0, 23, 704, 87)  # 头图黑底

        try:
            im = Image.open(BytesIO(requests.get(vdata.face).content))
            im = self.mask_img(im.resize((156, 156)), f"{spath}/src/mask/black_mask.png")
            self.paste_image(pt, im, 0, 0, 195, 195)  # 头像
        except Exception as e:
            print(f"获取头像失败", e)

        font = ImageFont.truetype(f"{spath}/src/font/msyh.ttc", size=15)  # UID, RID
        draw.text(xy=(205, 47), text=f"UID: {vdata.mid}  RID: {vdata.roomid}", fill=(255, 255, 255), font=font)

        font = ImageFont.truetype(f"{spath}/src/font/msyh.ttc", size=34)
        draw.text(xy=(205, 63), text=vdata.uname, fill=(255, 255, 255), font=font)  # 用户名

        font = ImageFont.truetype(f"{spath}/src/font/msyh.ttc", size=13)
        p_text = f"简介: {vdata.sign}".replace("\n", "  ")
        t_w, t_h = font.getsize(p_text)
        if t_w > 488:
            while t_w > 477:
                p_text = p_text[:-1]
                t_w, t_h = font.getsize(p_text)
            p_text = f"{p_text}..."
        draw.text(xy=(204, 123), text=p_text, fill=(0, 0, 0), font=font)  # 简介

        font = ImageFont.truetype(f"{spath}/src/font/msyh.ttc", size=21)
        draw.text(xy=(204, 151), text=f"粉丝数: {vdata.follower}  大航海: {vdata.guardNum}",
                  fill=(0, 0, 0), font=font)  # 粉丝数, 大航海数

        f_day = int((time.time() - vdata.mtime) / 86400)
        if not self.is_limit:
            f_day = "未知"
        p_text = f"关注天数： {f_day}"

        font = ImageFont.truetype(f"{spath}/src/font/msyh.ttc", size=15)
        t_w, t_h = font.getsize(p_text)
        draw.text(xy=(684 - t_w, 155), text=p_text, fill=(0, 0, 0), font=font)

        return pt

    def image_generate(self):
        line_count = int(len(self.follow_list) / 2)
        line_count += 1 if len(self.follow_list) % 2 != 0 else 0

        color_hsb_h = random.randint(0, 360)
        color_rgb = colorsys.hsv_to_rgb(color_hsb_h / 360, 0.16, 240)  # 进行一个颜色的随
        color_rgb = (int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]))
        pt = Image.new("RGBA", (1200, 371 + 198 * line_count), color_rgb)
        draw = ImageDraw.Draw(pt)

        im = Image.open(BytesIO(requests.get(self.user_mainpage_data.top_photo).content))
        self.paste_image(pt, im, -157, 0, 1514, 236, True)  # 头图

        im = Image.open(f"{spath}/src/bw_large.png")
        self.paste_image(pt, im, 0, 51, 1200, 188)  # 头图黑底

        im = Image.open(BytesIO(requests.get(self.user_mainpage_data.face).content))
        im = self.mask_img(im.resize((156, 156)), f"{spath}/src/mask/black_mask.png")
        self.paste_image(pt, im, 37, 51, 175, 175)  # 头像


        font = ImageFont.truetype(f"{spath}/src/font/msyh.ttc", size=80)
        draw.text(xy=(228, 80), text=self.username, fill=(255, 255, 255), font=font)  # 用户名

        font = ImageFont.truetype(f"{spath}/src/font/msyh.ttc", size=20)
        p_text = f"简介: {self.user_mainpage_data.sign}".replace("\n", "  ")
        if self.user_mainpage_data.fans_medal.medal is not None:
            p_text = f"粉丝勋章: {self.user_mainpage_data.fans_medal.medal.medal_name} " \
                     f"[{self.user_mainpage_data.fans_medal.medal.level}]   {p_text}"
        t_w, t_h = font.getsize(p_text)
        if t_w > 900:
            while t_w > 860:
                p_text = p_text[:-1]
                t_w, t_h = font.getsize(p_text)
            p_text = f"{p_text}..."
        draw.text(xy=(228, 181), text=p_text, fill=(255, 255, 255), font=font)  # 粉丝勋章/个签

        im = Image.open(f"{spath}/src/bf.png")
        self.paste_image(pt, im, 31, 277, 12, 56)


        p_x = 0
        p_y = 0
        count = 0
        t_follow = len(self.follow_list)
        count2 = 0
        for v in self.follow_list:
            if v.mid == 401742377 or v.mid == 161775300:
                continue
            count2 += 1
            print(f"获取数据: {count + 1}/{t_follow}")
            im = self.single_card(v)
            self.paste_image(pt, im, 31 + 595 * p_x, 371 + 198 * p_y, 542, 151)

            count += 1
            p_x += 1

            if p_x >= 2:
                p_x = 0
                p_y += 1
        font = ImageFont.truetype(f"{spath}/src/font/msyh.ttc", size=53)
        draw.text(xy=(58, 266), text=f"关注列表 ({count2})", fill=(0, 0, 0), font=font)  # 关注列表
        font = ImageFont.truetype(f"{spath}/src/font/msyh.ttc", size=15)
        p_text = f"数据来源: bilibili & vtbs.moe      统计于: {self.timestamp_to_text(int(time.time()))}      " \
                 f"Generated by Chieri Bot"
        draw.text(xy=(43, pt.height - 30), text=p_text,
                  fill=(0, 0, 0), font=font)

        pt = pt.convert("RGB")
        save_name = f"{spath}/temp/{self.username}.jpg"

        pt.save(save_name, quality=95)
        return save_name, count2, self.total_following  # 文件名, 关注vtb数, 总关注数
