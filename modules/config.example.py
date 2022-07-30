apiurl = 'https://sekai.jzlsx.cn/api'
# 游戏api请求地址
predicturl = 'https://xxxxxxxx/predict.json'
# 预测线地址
proxy = '127.0.0.1:7890'
proxies = {
    'http': 'http://' + proxy,
    'https': 'http://' + proxy
}
# 不用代理改None
ispredict = True
bearer_token = ''  # 需注册推特开发者
piccacheurl = ''  # 频道bot发送图片url前缀（带/）
charturl = ''  # 频道bot发送谱面预览url前缀（带/）
asseturl = 'https://assets.sekai.unijzlsx.com/'  # pjsk资源文件地址
whitelist = []
wordcloud = []  # 词云开启群
loghtml = ''  # 昵称设置日志保存目录
rsshub = ''  # rsshub地址
twitterlist = ''  # 抓取的推特列表地址
googleapiskey = ''  # 谷歌开发者key
# 百度翻译APP ID
appID = ''
# 百度翻译密钥
secretKey = ''
block = []  # bot拉黑
msggroup = 123  # 发送bot管理消息的群
