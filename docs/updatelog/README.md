---
sidebar: false
---
# 更新日志

::: tip
该页面可能更新比较缓慢，最新更新信息可查看[Github Commit记录](https://github.com/watagashi-uni/Unibot/commits/main)
:::

### 2022-09-01
完善`查房`，`查水表`功能

新增`分数线`命令，可绘制前200名活动分数时间线

### 2022-08-31
新增`5v5人数`命令，可查看5v5实时人数

新增`时速`命令，可查看近一小时的实时时速

新增`查房`，`查水表`功能，可查看前200名近一小时时速，20min*3时速，周回数，开车/停车时间，停车时间段等

### 2022-08-30
频道bot使用http API与群bot共用代码，功能会同步更新

外服功能模块合并

### 2022-08-28
一号机戳一戳会回复随机knd语音

### 2022-08-26
b30改版 生成有曲绘的直观大图

### 2022-08-25
新增`event`命令，可查看活动信息

### 2022-08-24
`sk`功能支持艾特

### 2022-08-21
`pjskinfo`改版，添加vocal信息

### 2022-08-17
`sk`显示活动剩余时间
sdvx网站的谱面预览加黑底

### 2022-08-16
恢复`彩虹生成`功能

### 2022-08-14

添加台服支持（稳定性未知）：在命令前加`tw`即可查询台服信息，如`tw绑定`, `twsk`, `tw逮捕`, `twpjsk进度`, `twpjskprofile`

### 2022-08-12
修复没有打过每日挑战的号pjskprofile报错

添加国际服支持：在命令前加`en`即可查询国际服信息，如`en绑定`, `ensk`, `en逮捕`, `enpjsk进度`, `enpjskprofile`

谱面预览匹配度小于 60% 不回复

### 2022-08-10

难度排行不显示无数据的歌曲

### 2022-08-08
新增`查bpm`命令，如`查bpm240`

设置词云只在被请求后导入用户自定义词典

修复CQ码未写全导致的`生成`功能不可用

### 2022-08-07
更换 python sdk 适应多 bot 环境

### 2022-08-06
新增`pjsk进度ex`命令，可以查看expert难度打歌进度

Sekai Viewer 的谱面预览加白底防止部分手机透明显示问题

### 2022-08-02
将`JSONDecodeError`视为网络故障回复网不好

匹配翻译时分割斜杠符号左右分开匹配

### 2022-08-01
修复了上次修复产生的无法看卡图的bug

### 2022-07-31
修复了随机看卡图会随机出剧透卡图的bug

### 2022-07-12 ~ 2022-07-31
重构Bot代码，验证了自动更新资源的稳定性，所有资源来源改为本地资源库。开源Unibot功能模块代码

### 2022-7-12
自建资源库，理论上masterdata与assets自动更新，所有资源不再请求其他网站

### 2022-7-10
正式将数据查询接口更换为自建的API

### 2022-7-9
自建查分接口测试中，部分时段的请求使用自建接口，将视稳定性决定是否长期使用

### 2022-7-8
中间有很多改动不大的微调，比如格式之类的调整和修复一些小bug，就不一一赘述了

预测修改了来源：https://3-3.dev/

适配了pjskprofile功能生成cp牌时底色颜色

### 2022-4-10
新增猜卡面（只猜角色）

- `pjsk猜卡面`

- `pjsk猜卡面+宽度(1-1000)`

### 2022-4-7
增加歌曲难度偏差值排行，热度排行查询

- `热度排行` 查看歌曲热度排行TOP40

- `难度排行 定数 难度`查看当前难度偏差值排行

  - 如`难度排行 26 expert`，难度可省略，默认为master，需小写

>数据来源：profile.pjsekai.moe

### 2022-4-6

pjskinfo加入当前歌曲玩家游玩，热度等信息

>数据来源：profile.pjsekai.moe

### 2022-4-5

新增playinfo命令，查看当前歌曲玩家游玩，热度等信息（数据会一直更新）

>数据来源：profile.pjsekai.moe


### 2022-4-3
pjskprofile图片加入称号（cp称号底图暂时使用同一个纯色）


### 2022-4-2
逮捕和pjskprofile模块的数据来源由"userMusics"转为"userMusicResults"，解决了未解锁歌曲多人live打过的数据算不进去的bug

### 2022-3-30
增加rank match相关命令，逮捕增加显示当前rank match排位

- `rk+id` 查询rank match相关信息
- `rk+排名` 查询rank match对应排名相关信息

### 2022-3-29
pjsk进度功能升级为图片形式


### 2022-3-28
新增倒放猜曲功能，发送“pjsk倒放猜曲”既可体验

### 2022-3-21
因为实际没找到什么用处而且过于刷屏，取消积分相关功能。

新增听歌猜曲功能，发送“pjsk听歌猜曲”既可体验

### 2022-3-15
1. 由于已经被封号一天，考虑到风控问题，暂时关闭积分，赛马，抽卡，ycm功能，猜曲功能加了频率限制

2. 考虑到查询速率问题，限制了所有调用接口的频率

3. 添加"pjsk进度"命令


### 2022-3-9
修复大bug：pjskinfo中作词作曲编曲全部错误列为编曲人

### 2022-2-28
最近的几次小更新：

1. 修复了官方移除rarity字段导致的抽卡不正常问题

2. 查分指令小调整

3. 加了几个开关

### 2022-2-2
和歌曲查询有关的命令，如pjskinfo，猜曲回答等支持模糊查询了（如匹配到昵称还是先使用昵称），不用一首歌为了匹配方便设置很多相似昵称了。

⚠模糊查询可能返回错误结果，不要寄太大的希望在上面

### 2022-1-27
抽卡支持生日池，新增100连抽卡，100连/200连显示四星是地多少抽抽到的

### 2022-1-14
1. 新增"pjskprofile"命令，可生成个人资料图片（一分钟内最多生成两次）

2. 查时间不加id时可以查自己绑定账号的时间

### 2022-1-12
误绑率严重，不再支持sk+id命令绑定，绑定请使用绑定+id

### 2022-1-10
1. 新增仅群内可用的角色昵称设置，优先度高于全群昵称。（记忆方法：group character set）

- `grcharaset[新昵称]to[已有昵称]` 设置仅当前群可用昵称

- `grcharadel[已有昵称]` 删除仅当前群可用昵称

- `看[昵称]` 随机角色卡图

- `charainfo[昵称]` 查看该角色群内和全群昵称

2. 猜曲猜错的时候分“找不到昵称”和“能找到昵称但是猜错了”两种情况提醒

3. 查歌曲信息改为图片发送+文字昵称（要使用原本的查询请使用"/pjskinfo"指令）

4. 推特推送检测模块重写，推送图片大致不变，以往一分钟内只能推送一个账号发送的一个消息，现在可以不遗漏地推送多个账号发送的多个消息（不知道有没有bug，可能仍然遗漏）

### 2021-12-30
修复了Fes卡池模拟抽卡当期概率近似翻倍的bug

### 2021-12-28
为防止歌曲角色的昵称数据库被乱加奇怪的内容/被恶意破坏，同时很方便的找到昵称设置人，从2021/12/29开始，所有歌曲昵称设置，角色昵称设置的日志内容将会在每日日志页面按日公示（页面手动更新，延迟不定可能到第二天晚上），包括设置时间、模糊处理(部分打码)后的设置人、具体设置内容。

角色昵称设置权限变为所有人都可设置，同时原命令误触发率很高，故修改命令：

- `charaset昵称to角色名(可以是现有昵称)`

- `charadel昵称`

删除了一些"xx老婆"和一些意义不明的角色昵称，角色昵称全bot通用且今后会记录日志公示，请谨慎设置。

### 2021-12-22
合并两个bot数据库，目前两个bot数据互通。

新增命令"sk预测" 可查看预测线，查分在活动开始一天之后会显示预测线。

预测信息来自https://sekai.best/eventtracker

### 2021-12-13
模拟抽卡可以模拟任意卡池了，只需要在命令最后加卡池id即可

- `sekai抽卡+卡池id` 对应卡池模拟十连

- `sekai200连+卡池id` 对应卡池模拟200抽（只显示四星）

- `sekai反抽卡+卡池id` 对应卡池反转2星4星概率

>注：没有被抽过的卡池第一次抽需要下载数据，耗时可能较长，生日卡池尚未适配

>卡池id可去<https://sekai.best/gacha> 进入对应卡池页面查看网址最后的数字，如网址是“<https://sekai.best/gacha/159>”，卡池id就是159

### 2021-12-10
新增谱面预览来源：<https://sdvx.in/prsk.html>（使用“谱面预览2”命令即可查看）

- `[xxxx]谱面预览2`//查看当前昵称歌曲的master谱面预览（来源：sdvx.in/prsk.html）

- `[xxxx]ex谱面预览2`//查看当前昵称歌曲的expert谱面预览

### 2021-12-3
新增抽卡/查分/ycm功能开关，新增“不给看”功能，新增使用条款及隐私条款

### 2021-11-26
适配QQ频道

### 2021-11-12
更新查分和逮捕命令，使用Circle Lin的用户数据查询接口

### 2021-11-04
猜曲实现多群同时游玩

### 2021-11-03
开放bot二号机

### 2021-9-29
加入PJSK玩家ID查创号时间功能

### 2021-9-4
加入模拟抽卡功能，加入master以下难度查看功能

- `[xxxx]ex谱面预览` 查看当前昵称歌曲的expert谱面预览

- `[xxxx]hd谱面预览` 查看当前昵称歌曲的hard谱面预览

- `[xxxx]nm谱面预览` 查看当前昵称歌曲的normal谱面预览

- `[xxxx]ez谱面预览` 查看当前昵称歌曲的easy谱面预览

### 2021-7-18
由于有群管理员反应猜曲刷屏严重，故加入群猜曲开关功能。管理员可在群内发送“关闭本群猜曲” “打开本群猜曲”打开或关闭本群的猜曲功能。
猜曲专用群（可随意猜曲刷屏），群号：883721511 ，在关闭猜曲的群内触发猜曲命令的回复中会包含该群号

### 2021-7-5
新增pjskinfo指令：pjskinfo+昵称（查看当前昵称的歌曲，并列出当前歌曲所有昵称）

### 2021-7-4
由于之前的手动截图猜曲可玩性太低（一首只有两张）故取消，原"pjsk困难猜曲"改为"pjsk猜曲"，新增pjsk猜曲排行榜，pjsk阴间猜曲排行榜，pjsk猜谱面排行榜（从7月4日开始计算）

### 2021-7-1
新增pjsk猜谱面，bot帮助页面上线

### 2021-6-28
新增随机裁切猜曲，新增阴间猜曲（随机裁切黑白）

### 2021-6-26
初版pjsk猜曲，每首曲子手动截两张图进行游戏