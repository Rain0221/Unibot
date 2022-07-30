<div align="center">
  <img width="256" src="./docs/.vuepress/public/logo.png" alt="logo">

# Unibot
一款基于 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 与 [nakuru-project](https://github.com/Lxns-Network/nakuru-project/) 的多功能 QQ 群 PJSK 机器人

[使用文档](https://bot.unijzlsx.com/) · [交流群](https://qm.qq.com/cgi-bin/qm/qr?k=Osy7KwWvvLWYTjBFJH3MQwkAqgAIV7rT&jump_from=webapi) · [交流频道](https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&appChannel=share&inviteCode=7Pe26&appChannel=share&businessType=9&from=181074&biz=ka&shareSource=5)
</div>

## 已实现功能
具体可参考[使用文档](https://bot.unijzlsx.com/)
- [x] 歌曲信息查询
- [x] 谱面预览查询
- [x] 别名系统
- [x] 玩家排名查询
- [x] 注册时间查询
- [x] 推歌进度查询
- [x] 生成MASTER难度进度图片
- [x] 生成profile图片
- [x] 隐私模式
- [x] 模拟抽卡
- [x] 猜曲/猜谱面/猜卡面游戏
- [x] 抽卡
- [x] 随机卡图
- [x] 生成5000兆风格文字图

## 关于本项目
bot依赖的别名/绑定数据库、游戏API实现、本地资源库、自动更新数据解包等模块由于各种原因没有开源，所以无法自行部署。你可以尝试使用[分布式客户端](https://bot.unijzlsx.com/distributed/)搭建一个Unibot，或者稍微修改一下其中一些功能，移植一些模块到你自己的机器人。

其中推特推送单独开源并配有部署文档：[watagashi-uni/twitterpush](https://github.com/watagashi-uni/twitterpush)

如你的项目需要资源库可使用 [assets.sekai.unijzlsx.com](http://assets.sekai.unijzlsx.com/) 或 [Sekai Viewer](https://sekai.best/asset_viewer)、[pjsek.ai](https://pjsek.ai/assets) 的资源库，api 可使用 [sekai.jzlsx.cn/api](https://sekai.jzlsx.cn/api)，使用方法请参考对应功能的代码。

masterDB 可使用 [Sekai-World/sekai-master-db-diff](https://github.com/Sekai-World/sekai-master-db-diff)

## 支持与贡献

觉得好用可以给这个项目点个 Star 。

有意见或者建议也欢迎提交 [Issues](https://github.com/watagashi-uni/Unibot/issues) 和 [Pull requests](https://github.com/watagashi-uni/Unibot/pulls)。

## 特别感谢
- [Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp): 基于 [Mirai](https://github.com/mamoe/mirai) 以及 [MiraiGo](https://github.com/Mrs4s/MiraiGo) 的 [OneBot](https://github.com/howmanybots/onebot/blob/master/README.md) Golang 原生实现 
- [Lxns-Network/nakuru-project](https://github.com/Lxns-Network/nakuru-project)：一款为 go-cqhttp 的正向 WebSocket 设计的 Python SDK
- [chinosk114514/QQ-official-guild-bot](https://github.com/chinosk114514/QQ-official-guild-bot): QQ官方频道机器人SDK
- [chinosk114514/chachengfen](https://github.com/chinosk114514/chachengfen): 成分查询器
- [chinosk114514/homo114514](https://github.com/chinosk114514/homo114514): 恶臭数字论证器
- [SkywalkerSpace/emoji2pic-python](https://github.com/SkywalkerSpace/emoji2pic-python): Apple emoji and text to picture
- [fuqiuai/wordCloud](https://github.com/fuqiuai/wordCloud): 用python进行文本分词并生成词云