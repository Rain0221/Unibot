# 频道bot使用文档
>  本文档将引导您使用 UniBot QQ频道版

- `UniBot`是一款功能型机器人, 主要提供《世界计划 多彩舞台》日服，国际服，台服（稳定性测试中）相关查询服务。
- 简便指令触发方法：在频道内输入斜杠 `/` ，系统会自动拉取指令列表，点击即可自动艾特并输入指令。
- 所有命令不带斜杠也能触发，但带斜杠点击指令列表会更方便。
- 机器人只需要打开"创建消息"权限即可使用所有功能，无需打开接受机器人推送开关（无主动消息）
- 如果发现任何滥用行为（包括但不限于频繁使用超过正常需求的查分指令），我们保留停止对该用户继续提供服务的权利。

::: warning 注意
使用机器人功能必须艾特机器人（不支持复制艾特信息）

频道bot与群bot共用同一套消息处理程序，一些新功能可能没有在此页面更新但已经可以使用，可配合[群bot帮助文档](/usage/)查看
:::

## 查询pjsk歌曲信息
>热度，难度偏差等统计信息来自 [profile.pjsekai.moe](https://profile.pjsekai.moe/)

### pjskinfo
- `pjskinfo+曲名` 或 `song+曲名` 查看当前歌曲详细信息，玩家游玩，热度等信息(图片版)，并列出当前歌曲所有昵
- `bpm+曲名` 查看当前歌曲的bpm
### 谱面预览
- `谱面预览 曲名 难度` 查询对应曲名，难度的谱面预览
  - `难度`支持的输入: `easy`, `norml`, `hard`, `expert`, `master`, `ex`, `nm`, `hd`, `ex`, `ma`
  - 如果查询`master`可省略难度
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
- `grcharaset新昵称to已有昵称` 设置仅当前频道可用角色昵称
- `grcharadel已有昵称` 删除仅当前频道可用角色昵称
- `charainfo昵称` 查看该角色频道内和全群昵称

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
- `查时间+id` 查询对应账号注册时间
### 活动查询
- `sk+id` 查询排名（此命令不会绑定id）
- `sk+排名` 查询对应排名分数
- `sk预测` 查看预测线，预测信息来自[3-3.dev](https://3-3.dev/)
### 打歌情况查询
- `逮捕@[xxx]` 如果此人绑定过id，就可以看TA的ex与master难度fc，ap数，排位信息
- `逮捕+id` 查看对应id的ex与master难度fc，ap数，排位信息
- `pjsk进度` 生成绑定id的master打歌进度图片（fc/ap/clear/all)
- `pjskprofile` 或 `个人信息` 生成绑定id的profile图片
- `pjsk b30` 生成绑定id的best30图片
### 隐私相关
- `不给看` 不允许他人逮捕自己，但自己还是可以逮捕自己，使用sk查分和逮捕自己时不会显示id
- `给看`

## pjsk竞猜
::: tip 随机截取曲绘/卡面竞猜

请在规定时间内回答，由于主动消息限制，bot不会自动结束猜曲，如果回答超时会自动结束并提示超时

设置猜曲234指令旨在方便通过斜杠指令+数字方便触发功能，无需每次输入完整指令
:::
- pjsk猜曲（截彩色曲绘）：`/pjsk猜曲`
- pjsk阴间猜曲（截黑白曲绘）：`/pjsk猜曲 2` 或 `/pjsk阴间猜曲`
- pjsk非人类猜曲（截30*30）：`/pjsk非人类猜曲`
- pjsk猜谱面：`/pjsk猜曲` 3 或 `/pjsk猜谱面`
- pjsk猜卡面：`/pjsk猜曲` 4 或 `/pjsk猜卡面`

## pjsk模拟抽卡
- `sekai抽卡` 模拟十连
- `sekaiXX连` 模拟`XX`抽（只显示四星）,`XX`接受的输入为`1-400`
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
- SDK: [chinosk114514/QQ-official-guild-bot](https://github.com/chinosk114514/QQ-official-guild-bot)
### 数据来源
- 预测线: [33Kit](https://3-3.dev/)
- 歌曲达成率，难度偏差，热度等信息: [Project Sekai Profile](https://profile.pjsekai.moe/)
- 谱面预览: [Sekai Viewer](https://sekai.best/), [プロセカ譜面保管所](https://sdvx.in/prsk.html)