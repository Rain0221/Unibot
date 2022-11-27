# 分布式客户端使用文档
使用此客户端, 您可以用自己的QQ号搭建一个Unibot

## 准备工作
::: warning 注意

部署本项目需要一定的电脑基础，会读文档

该教程已经过大量用户验证无问题，一步步跟着走就能部署好。如果出现问题建议先排除自己的问题，或者到分布式用户群里问问群友怎么解决

:::

### 获取一台服务器
你需要一台24h不关机的电脑，否则关机这段时间bot将无法工作

Windows 电脑需要运行 Windows 8 或 Windows server 2012 以上版本的系统（更低版本实测无法运行）
Linux 有 Ubuntu 20.04 (Python 3.8) 和 Ubuntu 22.04 (Python 3.10) 打包的两个版本，建议使用 Ubuntu 18 或以上系统，在较低版本 Ubuntu 和其他较低版本 linux 中可能提示缺少 GLIBC 对应版本，安装非常麻烦，不推荐使用。


### 下载客户端和申请token
请加群467602419在群文件下载客户端，按照群公告的步骤自助申请token

## 配置客户端
你需要将客户端放在一个文件夹内，在这个文件夹下新建一个`token.yaml`，用你喜欢的编辑器打开，填上以下的设置
```yaml
token: xxxxxx
port: 2525
blacklist:
- 123456
- 234567
whitelist:
- 345678
pjskguesstime: 50
charaguesstime: 30
```
其中，`token` 填写申请的token，`port` 填写你要通信的端口号，不懂可直接填写`2525`，如果你有要关闭bot的群，则需要按照格式配置 `blacklist` 项，不需要可以删除只保留上面两行。

模拟抽卡，猜曲，看卡图等功能需要添加 `whitelist` 项，并填入白名单群号。以上配置如果改动需要重启客户端生效

猜曲时间，猜卡面时间可自定义，如无需要可不配置。

准备就绪后可尝试启动客户端，如果没有问题会显示如下日志

```text
[xxxx-xx-xx xx:xx:xx,xxx] Running on http://127.0.0.1:2525 (CTRL + C to quit)
```

::: warning 注意

不要关闭客户端，必须启动客户端才能使用 bot

:::

## 配置 GO-CQHTTP

### 下载 [GO-CQHTTP](https://github.com/Mrs4s/go-cqhttp/releases)

如果上面的链接无法打开，你也可以在群文件下载

>如果你不知道这是什么，善用搜索引擎.

### 使用反向 WebSocket
打开 cqhttp 按提示创建bat文件，打开后, 通信方式选择: 反向WS

在 CQHTTP 配置文件中，填写 `ws_reverse_url` 值为 `ws://127.0.0.1:你的端口/ws/`，这里 `你的端口` 应改为上面填的端口号。

然后，如果有的话，删掉 `ws_reverse_event_url` 和 `ws_reverse_api_url` 这两个配置项。

最后的连接服务列表应该是这样的格式
```yaml
# 连接服务列表
servers:
  # 添加方式，同一连接方式可添加多个，具体配置说明请查看文档
  #- http: # http 通信
  #- ws:   # 正向 Websocket
  #- ws-reverse: # 反向 Websocket
  #- pprof: #性能分析服务器
  # 反向WS设置
  - ws-reverse:
      # 反向WS Universal 地址
      # 注意 设置了此项地址后下面两项将会被忽略
      universal: ws://127.0.0.1:2525/ws/
      # 重连间隔 单位毫秒
      reconnect-interval: 3000
      middlewares:
        <<: *default # 引用默认中间件
```

之后，在确保客户端已打开的情况下，打开cqhttp，按提示登录qq后，客户端应该会出现一行这样的日志
```text
[xxxx-xx-xx xx:xx:xx,xxx] 127.0.0.1:xxxxx GET /ws/ 1.1 101 - 515
```

## 测试对话

在有机器人的群里发送命令，比如`sk`，如果一切正常，ta 应该会回复你。

如果没有回复，请检查客户端运行是否报错、cqhttp 日志是否报错。如果都没有报错，则可能是机器人账号被腾讯风控，需要在同一环境中多登录一段时间。