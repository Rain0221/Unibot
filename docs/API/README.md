# Unibot API 使用文档
>本文档将引导您使用 UniBot 相关 API

API域名：`api.unipjsk.com`

## 曲库API

昵称获取歌曲id

`GET /getsongid/{alias}`

例如：`GET /getsongid/消失`

返回：
```json
{"status":"success","musicId":49,"match":1,"title":"初音ミクの消失","translate":"初音未来的消失"}
```

如果昵称未匹配，返回status为false

```json
{"status":"false"}
```


## 歌曲id获取昵称


`GET /getalias2/{musicId}`

例如：`GET /getalias/128`

返回：
```json
[{"id": 1, "alias": "brand new day"}, {"id": 2, "alias": "bnd"}, {"id": 3, "alias": "3932"}, {"id": 4, "alias": "⭐"}, {"id": 5, "alias": "必恩第"}]
```

>`getalias`为旧接口，返回纯文本，不建议使用

## 查询活动得分信息

::: warning 注意
请注意不要修改`/api/user/`后的`{user_id}`否则会请求失败，下同
::: 

指定用户id：`GET /api/user/{user_id}/event/{eventid}/ranking?targetUserId={targetUserId}`

指定排名：`GET /api/user/{user_id}/event/{eventid}/ranking?targetRank={targetRank}`

例如：`GET /api/user/{user_id}/event/63/ranking?targetUserId=5152947432357899`

`GET /api/user/{user_id}/event/63/ranking?targetRank=1000`

## 查询排位信息


指定用户id：`GET /api/user/{user_id}/rank-match-season/{rank-match-season}/ranking?targetUserId={targetUserId}`


指定排名：`GET /api/user/{user_id}/rank-match-season/{rank-match-season}/ranking?targetRank={targetRank}`


例如：`GET /api/user/{user_id}/rank-match-season/3/ranking?targetUserId=5152947432357899`

`GET /api/user/{user_id}/rank-match-season/3/ranking?targetRank=2`



## 查询个人Profile信息


`GET /api/user/{targetUserId}/profile`


例如 `GET /api/user/5152947432357899/profile`


此接口返回大量数据，如个人介绍、卡组信息、角色等级、自定义profile、打歌信息等
