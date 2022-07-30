from pydantic import BaseModel
import typing as t

class SerachBiliUserResult(BaseModel):
    type: str  # bili_user
    mid: int
    uname: str
    usign: str  # 个签
    fans: int
    videos: int
    upic: str  # 头像 //i0.hdslb.com/bfs/face/b4a3e737e56cda1f122727ba4b73f4a2168f1135.jpg 对, 就是没有http
    verify_info: str
    level: int
    gender: int
    is_upuser: int
    is_live: t.Optional[int]
    room_id: t.Optional[int]
    res: t.Optional[t.List]  # 视频列表
    official_verify: t.Optional[t.Dict]
    # hit_columns: t.Optional[t.List]


class FollowingUserInfo(BaseModel):
    mid: int
    attribute: int
    mtime: int
    # tag: t.List
    special: int
    # contract_info: t.Dict
    uname: str
    face: str  # 头像URL
    sign: str
    # official_verify: t.Dict
    # vip: t.Dict


class UserFansMedalMedal(BaseModel):
    uid: int
    target_id: int
    medal_id: int
    level: int
    medal_name: str
    medal_color: int
    # 还有其它的, 但是没用, 懒得搞了

class UserFansMedal(BaseModel):
    show: bool
    wear: bool
    medal: t.Optional[UserFansMedalMedal]

class UserMainPageInfo(BaseModel):
    mid: int
    name: str
    sex: str
    face: str
    face_nft: int
    sign: str
    rank: int
    level: int
    fans_badge: bool
    fans_medal: UserFansMedal
    top_photo: str


class VTBInfo(BaseModel):
    mtime: t.Optional[int]  # 开始关注的时间
    mid: int
    uuid: str
    uname: str
    video: int
    roomid: int
    sign: str
    # notice: t.Optional[str]
    face: str
    rise: int
    topPhoto: str
    archiveView: int
    follower: int
    liveStatus: bool
    recordNum: int
    guardNum: int
    # lastLive: t.Dict
    guardChange: int
    # guardType: t.List
    # online: t.Union[int, bool]
    title: str
    time: int
    liveStartTime: int

    def __init__(self, mtime=0, **data):
        super().__init__(**data)
        self.mtime = mtime
