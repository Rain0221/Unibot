# 功能列表

>  本文档将引导您使用 UniBot
> 
- 使用该Bot，即意味着你同意[使用条款](/licence/)及[隐私条款](/privacy/)

::: warning 注意
该bot没有开放任何私聊功能

猜曲，猜卡面，看卡图，模拟抽卡功能请使用官方平台的频道bot游玩

不再接受新群邀请，如需要可使用[分布式客户端](/distributed/)自行部署
:::

::: tip 关于频道版
bot频道版已上线，[点击进入](https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&appChannel=share&inviteCode=7Pe26&appChannel=share&businessType=9&from=181074&biz=ka&shareSource=5)Unibot频道使用，[使用文档](/guild/)
:::

## 查询pjsk歌曲信息
>玩家游玩，热度，难度偏差等统计信息来自 [profile.pjsekai.moe](https://profile.pjsekai.moe/)

### pjskinfo
- `pjskinfo+曲名` 查看当前歌曲详细信息，玩家游玩，热度等信息(图片版)，并列出当前歌曲所有昵
- `pjskbpm+曲名` 查看当前歌曲的bpm
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
由于角色昵称用到的场景（猜卡面，看卡图等）在群Bot内因为风控被砍，实际用处不大，所以新分布式客户端不支持角色昵称相关操作

如使用pjskdel命令，请仅删除确实不合适的昵称，很多猜曲用的快捷昵称删除后会造成诸多不便

所有歌曲昵称设置，角色昵称设置的日志内容将会在[实时日志](/dailylog/)页面按日公示
:::

## 查询玩家信息
- `绑定+id` 绑定id
### 活动查询
- >由于和其他bot命令重合，`sk`功能可由管理员在群内发送`关闭sk` `开启sk`来开关该功能
- `sk+id` 查询排名（此命令不会绑定id）
- `sk+排名` 查询对应排名分数
- `sk预测` 查看预测线，预测信息来自[3-3.dev](https://3-3.dev/)
### 打歌情况查询
- `逮捕@[xxx]` 如果此人绑定过id，就可以看TA的ex与master难度fc，ap数，排位信息
- `逮捕+id` 查看对应id的ex与master难度fc，ap数，排位信息
- `pjsk进度` 生成绑定id的master打歌进度图片（fc/ap/clear/all)
- `pjskprofile` 生成绑定id的profile图片 为减少服务器负担一分钟只能使用两次
### 隐私相关
- `不给看` 不允许他人逮捕自己，但自己还是可以逮捕自己，使用sk查分和逮捕自己时不会显示id
- `给看`

## 其他
::: warning 注意
由于风控问题，pjsk竞猜，随机卡图，模拟抽卡等功能在群内停用，请在频道使用这些功能

[频道版使用文档](/guild/)
:::

## 关于
- 开发者: [綿菓子ウニ](https://space.bilibili.com/622551112)
- 交流群:`883721511`
- Unibot频道: [点击进入](https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&appChannel=share&inviteCode=7Pe26&appChannel=share&businessType=9&from=181074&biz=ka&shareSource=5)
### 使用框架
- 框架: [Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
- SDK: [Lxns-Network/nakuru-project](https://github.com/Lxns-Network/nakuru-project)
### 数据来源
- 预测线: [33Kit](https://3-3.dev/)
- 玩家游玩，热度等信息: [Project Sekai Profile](https://profile.pjsekai.moe/)
- 谱面预览: [Sekai Viewer](https://sekai.best/), [プロセカ譜面保管所](https://sdvx.in/prsk.html)