apiurl = 'https://sekai.jzlsx.cn/api'
# 游戏api请求地址
predicturl = 'https://xxxxxxxx/predict.json'
# 预测线地址，有需要可找33申请：https://3-3.dev/pjsk-predict
proxy = '127.0.0.1:7890'
proxies = {
    'http': 'http://' + proxy,
    'https': 'http://' + proxy
}
# 不用代理改None
ispredict = True
bearer_token = ''  # 需注册推特开发者（推车用）
piccacheurl = ''  # 频道bot发送图片url前缀（带/）（频道bot用）
charturl = ''  # 频道bot发送谱面预览url前缀（带/）（频道bot用）
asseturl = 'https://assets.sekai.unijzlsx.com/'  # pjsk资源文件地址（频道bot用）
whitelist = []  # 群bot猜曲白名单
wordcloud = []  # 词云开启群
loghtml = ''  # 昵称设置日志保存目录
rsshub = ''  # rsshub地址（推特推送用 详见https://github.com/watagashi-uni/twitterpush）
twitterlist = ''  # 抓取的推特列表地址（推特推送用 详见https://github.com/watagashi-uni/twitterpush）
googleapiskey = ''  # 谷歌开发者key（推特推送用 详见https://github.com/watagashi-uni/twitterpush）
# 百度翻译APP ID
appID = ''  # 机翻推特命令用
# 百度翻译密钥
secretKey = ''  # 机翻推特命令用
block = []  # bot拉黑
msggroup = 123  # 发送bot管理消息的群
