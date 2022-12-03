import base64
import json
import random

import requests

from modules.config import proxies, novelAI_token


def novelAI_img2img(img_path, output):
    with open(img_path, 'rb') as f:
        image_data = f.read()
        base64_data = base64.b64encode(image_data)  # base64编码

    data = {
        "input":"masterpiece, best quality",
        "model":"nai-diffusion",
        "parameters":{
            "width": 512,
            "height": 512,
            "scale": 11,
            "sampler":"k_euler_ancestral",
            "steps": 50,
            "seed": random.randint(10000, 1000000000),
            "n_samples": 1,
            "strength": random.randint(50, 70) / 100,
            "noise": random.randint(10, 30) / 100,
            "ucPreset": 0,
            "qualityToggle": True,
            "image": str(base64_data, 'utf-8'),
            "uc":"nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"
        }
    }

    headers = {
        'authorization': novelAI_token,
        'content-type': 'application/json'
    }

    resp = requests.request('POST', url='https://api.novelai.net/ai/generate-image', headers=headers, data=json.dumps(data), proxies=proxies)
    resptext = resp.text
    newbase64 = resptext[resptext.find('data:') + 5:-2]

    with open(output, 'wb') as file:
        jiema = base64.b64decode(bytes(newbase64, 'utf-8'))  # 解码
        file.write(jiema)