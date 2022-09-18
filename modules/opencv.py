# 基于FLANN的匹配器(FLANN based Matcher)定位图片
import json
import time

import numpy as np
import cv2
import requests
from matplotlib import pyplot as plt

MIN_MATCH_COUNT = 8  # 设置最低特征点匹配数量为10
plt.switch_backend('agg')
def matchimage(queryImage, trainImage):
    template = cv2.imread(queryImage, 0)  # queryImage
    target = cv2.imread(trainImage, 0)  # trainImage
    # Initiate SIFT detector创建sift检测器
    sift = cv2.xfeatures2d.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(target, None)
    # 创建设置FLANN匹配
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    # 舍弃大于0.7的匹配
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)
    if len(good) > MIN_MATCH_COUNT:
        # 获取关键点的坐标
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        # 计算变换矩阵和MASK
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        h, w = template.shape
        # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        cv2.polylines(target, [np.int32(dst)], True, 0, 2, cv2.LINE_AA)
    else:
        return False, len(good)
    draw_params = dict(matchColor=(0, 255, 0),
                       singlePointColor=None,
                       matchesMask=matchesMask,
                       flags=2)
    result = cv2.drawMatches(template, kp1, target, kp2, good, None, **draw_params)
    plt.imshow(result, 'gray')
    now = int(time.time())
    plt.savefig(f'piccache/{now}.png')
    return True, f'piccache/{now}.png'

def matchjacket(queryImage=None, url=None):
    if url is not None:
        resp = requests.get(url)
        now = int(time.time())
        with open(f'piccache/{now}.png', 'wb') as f:
            f.write(resp.content)
        queryImage = f'piccache/{now}.png'
    jacketdir = 'data/assets/sekai/assetbundle/resources/startapp/music/jacket/jacket_s_%03d/jacket_s_%03d.png'
    with open('masterdata/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    match = [0, 0, '']
    for music in musics:
        print(music['id'], music['title'])
        result = matchimage(queryImage, jacketdir % (music['id'], music['id']))
        if result[0]:
            return music['title'], result[1]
        elif result[1] > match[1]:
            match = [music['id'], result[1], music['title']]
    if match[1] > 0:
        return match[2], jacketdir % (match[0], match[0])
    else:
        return False, ''