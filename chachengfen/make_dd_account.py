import random

import dd_query
import json
import time
import os

spath = os.path.split(__file__)[0]


def output_users_left(vtbdata, start: int):
    _count = 0
    output = []
    if not os.path.isdir(f"{spath}/output"):
        os.mkdir(f"{spath}/output")
    out_name = f"{spath}/output/{int(time.time())}.json"

    for _v in vtbdata:
        _count += 1
        if _count < start:
            continue
        output.append(_v)

    with open(out_name, "w", encoding="utf8") as _f:
        json.dump(output, _f, ensure_ascii=False)
    print(f"未关注的 {len(output)} 位vtb数据已输出到 {out_name} 更换账号后您可以使用此数据继续关注")


self_userid = input("请输入自身用户ID:")
self_sessdata = input("请输入SESSDATA:")
self_bili_jct = input("请输入bili_jct:")

self_following_list = []

if int(input("是否检查自身关注列表, 以跳过已关注用户? 是-1, 否-0:")):
    for i in range(40):
        data = json.loads(dd_query.api.get_user_following_list(self_userid, ps=50, pn=i + 1, sessdata=self_sessdata))
        if int(data["code"]) == 22007:  # 5页限制
            print("用户ID不正确")
            exit(-1)
        elif int(data["code"]) != 0:
            raise dd_query.errors.APIError(f"检查自身关注列表出错: {data['message']}")

        get_list = data["data"]["list"]
        total_following = data["data"]["total"]
        if not get_list:
            break
        else:
            # self_follow_list += [dd_query.models.FollowingUserInfo(**u) for u in get_list]
            self_following_list += [u["mid"] for u in get_list]
        time.sleep(0.5)
    print(f"检查完毕, 该账号目前关注了 {len(self_following_list)} 位用户")


vdata_path = input("请输入要使用的vtb数据路径, 留空则使用默认数据:").strip()

if vdata_path == "":
    vtb_data = json.loads(dd_query.api.get_all_vtb_info())
else:
    with open(vdata_path, "r", encoding="utf8") as f:
        vtb_data = json.load(f)

count = 0
total_vtb_count = len(vtb_data)
start_count = input("从第几位开始?默认为0:")
start_count = int(start_count) if start_count != "" else 0

for v in vtb_data:
    count += 1
    mid = v["mid"]
    if mid in self_following_list:
        print(mid, "已关注, 将跳过", f"{count}/{total_vtb_count}")
        continue
    if count < start_count:
        print(mid, "手动跳过", f"{count}/{total_vtb_count}")
        continue

    response = json.loads(dd_query.api.relation_modify(mid, 1, self_bili_jct, self_sessdata))
    scode = int(response["code"])
    if scode == 0:
        print(mid, "关注成功", f"{count}/{total_vtb_count}")
    elif scode == 22009:
        print(mid, "关注失败, 关注用户已达上限, 请更换账号", f"{count}/{total_vtb_count}")
        output_users_left(vtb_data, count)
        break
    elif scode == 22013:
        print(mid, "账号已注销", f"{count}/{total_vtb_count}")
    else:
        print(mid, f"关注失败: {scode}", response, f"{count}/{total_vtb_count}")
        if int(input("是否要停止进程? 是-1, 否-0:")):
            if int(input("是否输出未关注数据? 是-1, 否-0:")):
                output_users_left(vtb_data, count)
            break

    time.sleep(random.randint(5, 25) / 10)


if int(input("是否将本次获取的vtb数据添加至following_list.json? 是-1, 否-0:")):
    if os.path.isfile(f"{spath}/cookies/following_list.json"):
        with open(f"{spath}/cookies/following_list.json", "r", encoding="utf8") as f:
            rdata = json.load(f)
    else:
        rdata = []
    rdata += vtb_data
    rdata = list(set(rdata))
    with open(f"{spath}/cookies/following_list.json", "w", encoding="utf8") as f:
        json.dump(rdata, f, ensure_ascii=False)
