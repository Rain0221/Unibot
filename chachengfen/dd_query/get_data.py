from . import api, models, errors
import time
import json
import sqlite3
import os
from threading import Thread

def on_new_thread(f):
    def task_qwq(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
    return task_qwq


class DDAccount:
    def __init__(self, uid, sessdata, bili_jct, full_cookie, following_count):
        self.uid: str = uid
        self.sessdata: str = sessdata
        self.bili_jct: str = bili_jct
        self.full_cookie: str = full_cookie
        self.following_count: models.t.Optional[int] = following_count


class GetUserFollowingVTB:
    def __init__(self, username: str, max_follow_list=2000):
        self.username = username
        self.max_follow_list = max_follow_list
        self.userdata = self.get_userinfo()
        self.userid = self.userdata.mid
        dd_accounts = self.get_ddaccount()
        if dd_accounts:
            self.is_limit = False
            self.follow_list, self.total_following, self.total_following_vtb = self.get_all_same_following(dd_accounts)
        else:
            self.is_limit = True
            self.follow_list, self.total_following, self.total_following_vtb = self.get_user_following()
        self.follow_list, self.total_vtb_count = self.check_vtb_list()
        self.user_mainpage_data = self.get_user_mainpage_data()
        self.update_following()

    def get_userinfo(self):
        try:
            data = json.loads(api.user_search(self.username))
            if "result" not in data["data"]:
                raise errors.UserNotFound(f"没有找到相关用户: {self.username}")
            result = data["data"]["result"]
            self.username = data["data"]["result"][0]["uname"]
            return models.SerachBiliUserResult(**result[0])

        except json.JSONDecodeError:
            raise errors.APIError("用户信息拉取失败")
        except IndexError:
            raise errors.UserNotFound(f"没有找到用户: {self.username}")

    def get_user_mainpage_data(self):
        data = json.loads(api.get_biliuser_info(self.userid))
        return models.UserMainPageInfo(**data["data"])

    def get_user_following(self) -> models.t.Tuple[models.t.List[models.FollowingUserInfo], int, int]:
        """
        获取关注列表(无需cookie, 只能获取最近250个)
        :return: 关注vtb列表, 总关注数, vtb关注数
        """
        following = []
        total_following = 0
        total_following_vtb = 0
        for i in range(5):
            data = json.loads(api.get_user_following_list(self.userid, ps=50, pn=i + 1))
            if int(data["code"]) == 22007:  # 5页限制
                break
            elif int(data["code"]) == 22115:
                raise errors.UserBan(data["message"])
            elif int(data["code"]) != 0:
                raise errors.APIError(data["message"])

            get_list = data["data"]["list"]
            total_following = data["data"]["total"]
            if not get_list:
                break
            else:
                total_following_vtb += len(get_list)
                if not len(following) >= self.max_follow_list:
                    following += [models.FollowingUserInfo(**u) for u in get_list]
            time.sleep(0.5)
        return following[:self.max_follow_list], total_following, total_following_vtb  # 关注vtb列表, 总关注数, vtb关注数

    def get_all_same_following(self, dds: models.t.List[DDAccount]):
        following: models.t.List[models.FollowingUserInfo] = []
        total_following_vtb = 0
        for dd in dds:
            try:
                f_list, f_count = self.get_same_following(dd)
                if not len(following) >= self.max_follow_list:
                    following += f_list
                total_following_vtb += f_count
            except errors.APIError as e:
                print("获取共同关注失败, 改为获取普通列表", e)
                self.is_limit = True
                return self.get_user_following()
            except errors.UserBan as e:
                print("用户已设置隐私，结束查找")
                return [], 0, 0

        data = json.loads(api.get_user_following_list(self.userid))
        total_following = data["data"]["total"]
        _fis = []
        _fid = []
        for _f in following:
            if _f.mid in _fid:
                continue
            _fid.append(_f.mid)
            _fis.append(_f)
        following = sorted(_fis, key=lambda x: x.mtime, reverse=True)
        return following[:self.max_follow_list], total_following, total_following_vtb

    def get_same_following(self, dd: DDAccount) -> models.t.Tuple[models.t.List[models.FollowingUserInfo], int]:
        """
        获取共同关注
        """
        following = []
        total_following_vtb = 0
        for i in range(40):
            data = json.loads(api.get_same_following(self.userid, dd.sessdata, ps=50, pn=i + 1))
            if int(data["code"]) == 22115:
                 print("用户已设置隐私，无法查看")
                 raise errors.UserBan(data["message"])
            elif int(data["code"]) != 0:
                raise errors.APIError(data["message"])
            get_list = data["data"]["list"]
            total_following_vtb = data["data"]["total"]
            if not get_list:
                break
            else:
                following += [models.FollowingUserInfo(**u) for u in get_list]
            time.sleep(0.5)

        data = json.loads(api.get_user_following_list(dd.uid))
        self_following_count = data["data"]["total"]
        self.update_account_following_count(dd.uid, self_following_count)

        return following, total_following_vtb

    def check_vtb_list(self) -> models.t.Tuple[models.t.List[models.VTBInfo], int]:
        vtb_list = []
        vtb_data = json.loads(api.get_all_vtb_info())
        for v in vtb_data:
            if v["mid"] == 401742377:
                continue
            vtb_list.append(v["mid"])
        vtb_total_count = len(vtb_list)
        vtb_following = []
        for u in self.follow_list:
            if u.mid in vtb_list:
                vdata = vtb_data[vtb_list.index(u.mid)]
                vtb_following.append(models.VTBInfo(u.mtime, **vdata))
        return vtb_following, vtb_total_count

    @staticmethod
    def get_ddaccount():
        conn = sqlite3.connect(f"{api.spath}/cookies/bili_dd_account.db")
        cursor = conn.cursor()
        data = cursor.execute("SELECT uid, SESSDATA, bili_jct, full_cookie, following_count FROM dds").fetchall()
        accounts = [DDAccount(*u) for u in data]
        cursor.close()
        conn.close()
        return accounts

    @staticmethod
    def update_account_following_count(uid: str, count: int):
        conn = sqlite3.connect(f"{api.spath}/cookies/bili_dd_account.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE dds set following_count = ? WHERE uid = ?", [count, uid])
        conn.commit()
        cursor.close()
        conn.close()

    @on_new_thread
    def update_following(self):
        config = api.DObj(f"{api.spath}/cache/cache.ini")
        last_time = int(config.readobj("cache", "last_update_time", "0"))
        time_now = int(time.time())
        if time_now - last_time > 600:
            if os.path.isfile(f"{api.spath}/cookies/following_list.json"):
                def add_follow(uid) -> bool:
                    accounts = self.get_ddaccount()
                    for n in range(len(accounts)):
                        account = accounts[n]
                        if 0 <= account.following_count < 2000:
                            req = json.loads(api.relation_modify(uid, 1, account.bili_jct, account.sessdata))
                            if req["code"] != 0:
                                continue
                            else:
                                self.update_account_following_count(account.uid, account.following_count + 1)
                                return True
                    return False

                with open(f"{api.spath}/cookies/following_list.json", "r", encoding="utf8") as f:
                    following_data = json.load(f)
                all_vtb = json.loads(api.get_all_vtb_info())
                following_vtb_list = []
                for v in following_data:
                    following_vtb_list.append(v["mid"])

                for v in all_vtb:
                    v_uid = v["mid"]
                    if v_uid not in following_vtb_list:
                        if add_follow(v_uid):
                            following_data.append(v)

                with open(f"{api.spath}/cookies/following_list.json", "w", encoding="utf8") as f:
                    json.dump(following_data, f, ensure_ascii=False)
