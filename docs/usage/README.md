# 功能列表

>  本文档将引导您使用 UniBot
> 
- UniBot是一款功能型机器人, 主要提供《世界计划 多彩舞台》日服，国际服，台服（稳定性测试中）相关查询服务。
- 使用该Bot，即意味着你同意[使用条款](/licence/)及[隐私条款](/privacy/)

::: warning 注意
该bot没有开放任何私聊功能

由于风控严重，猜曲，猜卡面，看卡图，模拟抽卡功能已开启白名单模式。如你所在的群未开启以上功能，请使用官方平台的频道bot游玩
:::

::: tip 关于bot分布式部署

群bot由于风控严重不再接受新群邀请，如需要可使用[分布式客户端](/distributed/)自行部署

:::

::: tip 关于频道版
bot频道版已上线，[点击进入](https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&appChannel=share&inviteCode=7Pe26&appChannel=share&businessType=9&from=181074&biz=ka&shareSource=5)Unibot频道使用，[使用文档](/guild/)
:::

## 查询pjsk歌曲信息
>热度，难度偏差等统计信息来自 [profile.pjsekai.moe](https://profile.pjsekai.moe/)

### pjskinfo
- `pjskinfo+曲名` 查看当前歌曲详细信息，玩家游玩，热度等信息(图片版)，并列出当前歌曲所有昵称（可使用`song+曲名`）
- `pjskbpm+曲名` 查看当前歌曲的bpm（频道可直接使用`bpm+曲名`）
- `查bpm+数字` 查询对应bpm所有歌曲
### 谱面预览
- `谱面预览 曲名 难度` 查询对应曲名，难度的谱面预览（来源：[Sekai Viewer](https://sekai.best/)）
  - `难度`支持的输入: `easy`, `norml`, `hard`, `expert`, `master`, `ex`, `nm`, `hd`, `ex`, `ma`
  - 如果查询`master`可省略难度
- `谱面预览2 曲名 难度` 查询对应曲名，难度的谱面预览（来源：[プロセカ譜面保管所](sdvx.in/prsk.html)）
### 各种排行
- `热度排行` 查看歌曲热度排行TOP40
- `难度排行 定数 难度` 查看当前难度偏差值排行（如难度排行 26 expert，难度可省略，默认为master，需小写）
- `fc难度排行 定数 难度` 查看当前难度FC偏差值排行（如fc难度排行 26 expert，难度可省略，默认为master，需小写）
- `ap难度排行 定数 难度` 查看当前难度AP偏差值排行（如ap难度排行 26 expert，难度可省略，默认为master，需小写）
### 昵称设置

- `pjskset昵称to歌名`
- `pjskdel昵称` 删除对应昵称
- `charaset昵称to角色名(可以是现有昵称)` 设置角色所有群通用昵称,如`charasetkndto宵崎奏`
- `charadel昵称` 删除角色所有群通用昵称
- `grcharaset新昵称to已有昵称` 设置仅当前群可用角色昵称
- `grcharadel已有昵称` 删除仅当前群可用角色昵称
- `charainfo昵称` 查看该角色群内和全群昵称

::: warning 注意
如使用pjskdel命令，请仅删除确实不合适的昵称，很多猜曲用的快捷昵称删除后会造成诸多不便

所有歌曲昵称设置，角色昵称设置的日志内容将会在[实时日志](/dailylog/)页面按日公示
:::


## 查询玩家信息

> 在命令前加`en`即可查询国际服信息，如`en绑定`, `ensk`, `en逮捕`, `enpjsk进度`, `enpjskprofile`

> ⚠稳定性未知
> 
> 在命令前加`tw`即可查询台服信息，如`tw绑定`, `twsk`, `tw逮捕`, `twpjsk进度`, `twpjskprofile`

- `绑定+id` 绑定id
### 活动查询
- >由于和其他bot命令重合，`sk`,`逮捕`,`查房`,`查水表`功能可由管理员在群内发送`关闭sk` `开启sk`来开关该功能
- `sk+id` 查询排名（此命令不会绑定id）
- `sk+排名` 查询对应排名分数
- `sk预测` 查看预测线，预测信息来自[3-3.dev](https://3-3.dev/)
- `时速` 查询档线近一小时的实时时速
- `5v5人数` 可查看5v5实时人数
- `查房+id`,`查房+排名` 可查询前200周回情况，时速，平均pt等
- `查水表+id`,`查水表+排名` 可查询前200停车情况
- `分数线+id`,`分数线+排名` 可绘制前200活动分数随时间增长的折线图
### 打歌情况查询
- `逮捕@[xxx]` 如果此人绑定过id，就可以看TA的ex与master难度fc，ap数，排位信息
- `逮捕+id` 查看对应id的ex与master难度fc，ap数，排位信息
- `pjsk进度` 生成绑定id的master打歌进度图片（fc/ap/clear/all)
- `pjskprofile` 生成绑定id的profile图片（可使用`个人信息`）
- `pjsk b30` 生成绑定id的best30图片
### 隐私相关
- `不给看` 不允许他人逮捕自己，但自己还是可以逮捕自己，使用sk查分和逮捕自己时不会显示id
- `给看`

## pjsk竞猜
::: warning 注意
由于风控问题，猜曲，猜卡面，看卡图，模拟抽卡功能已开启白名单模式。如你所在的群未开启以上功能，请使用官方平台的频道bot游玩
:::

::: warning 关于频道版猜曲
请在规定时间内回答，由于主动消息限制，bot不会自动结束猜曲，如果回答超时会自动结束并提示超时

设置猜曲234指令旨在频道内方便通过斜杠指令+数字方便触发功能，无需每次输入完整指令
:::

- pjsk猜曲（截彩色曲绘）：`pjsk猜曲`
- pjsk阴间猜曲（截黑白曲绘）：`pjsk阴间猜曲` 或 `/pjsk猜曲 2`
- pjsk非人类猜曲（截30*30）：`pjsk非人类猜曲`
- pjsk猜谱面：`pjsk猜谱面` 或 `/pjsk猜曲 3`
- pjsk猜卡面：`pjsk猜卡面` 或 `/pjsk猜曲 4`
- pjsk听歌猜曲（频道不可用）：`pjsk听歌猜曲`
- pjsk倒放猜曲（频道不可用）：`pjsk倒放猜曲`

## pjsk模拟抽卡
> 十连抽卡模拟会生成图片
- `sekai抽卡` 模拟十连
- `sekaiXX连` 模拟`XX`抽（只显示四星）,`XX`接受的输入为`1-200`（频道内`1-400`）
- `sekai反抽卡` 反转2星4星概率
- `sekai抽卡+卡池id` 对应卡池模拟十连
- `sekai100连+卡池id` 对应卡池模拟100抽（只显示四星）
- `sekai200连+卡池id` 对应卡池模拟200抽（只显示四星）
- `sekai反抽卡+卡池id` 对应卡池反转2星4星概率

::: tip 关于卡池id
卡池id可去<https://sekai.best/gacha> 进入对应卡池页面查看网址最后的数字，如网址是<https://sekai.best/gacha/159>，卡池id就是159
:::

## 随机卡图
- `看[角色昵称]` 或 `来点[角色昵称]`

## 其他
- `生成 这是红字 这是白字` 生成5000兆円欲しい！风格的文字表情包
- `彩虹生成 这是红字 这是白字` 可以自己试试

## 关于
- 开发者: [綿菓子ウニ](https://space.bilibili.com/622551112)
- 交流群:`883721511`
- Unibot频道: [点击进入](https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&appChannel=share&inviteCode=7Pe26&appChannel=share&businessType=9&from=181074&biz=ka&shareSource=5)
### 使用框架
- 框架: [Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
- SDK: [nonebot/aiocqhttp](https://github.com/nonebot/aiocqhttp)
### 数据来源
- 预测线: [33Kit](https://3-3.dev/)
- 歌曲达成率，难度偏差，热度等信息: [Project Sekai Profile](https://profile.pjsekai.moe/)
- 谱面预览: [Sekai Viewer](https://sekai.best/), [プロセカ譜面保管所](https://sdvx.in/prsk.html)