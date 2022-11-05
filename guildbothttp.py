import bot_api
import server
from bot_api.utils import yaml_util
from modules.config import piccacheurl, charturl, asseturl

token = yaml_util.read('yamls/config.yaml')
bot = bot_api.BotApp(token['bot']['id'], token['bot']['token'], token['bot']['secret'],
                     is_sandbox=False, debug=False, api_return_pydantic=True,
                     inters=[bot_api.Intents.GUILDS, bot_api.Intents.AT_MESSAGES, bot_api.Intents.GUILD_MEMBERS])


app = server.BotServer(bot, ip_call="127.0.0.1", port_call=11416, ip_listen="127.0.0.1", port_listen=1988,
                       allow_push=True)

# # 开始注册事件, 可以选择需要的进行注册
app.reg_bot_at_message()  # 艾特消息事件
# app.reg_guild_member_add()  # 成员增加事件
# app.reg_guild_member_remove()  # 成员减少事件
#
# # 以下事件与onebot差别较大
# app.reg_guild_create()  # Bot加入频道事件
# app.reg_guild_update()  # 频道信息更新事件
# app.reg_guild_delete()  # Bot离开频道/频道被解散事件
# app.reg_channel_create()  # 子频道创建事件
# app.reg_channel_update()  # 子频道信息更新事件
# app.reg_channel_delete()  # 子频道删除事件

@app.bot.receiver(bot_api.structs.Codes.SeverCode.image_to_url)  # 注册一个图片转url方法
def img_to_url(img_path: str):
    # 用处: 发送图片时, 使用图片cq码[CQ:image,file=]或[CQ:image,url=]
    # 装饰器作用为: 解析cq码中图片的路径(网络图片则下载到本地), 将绝对路径传给本函数, 自行操作后, 返回图片url, sdk将使用此url发送图片
    # 若不注册此方法, 则无法发送图片。
    # [CQ:image,file=file:///E:\工程文件夹2\bot\unibot\piccache\pjskinfo73.png]
    # if 'cache' in img_path:
    #     file = img_path[img_path.find("cache")+6:]
    #     return piccacheurl + file
    # elif 'charts' in img_path:
    #     file = img_path[img_path.find("charts")+7:]
    #     return charturl + file
    # elif 'resources' in img_path:
    #     file = img_path[img_path.find("resources")+10:]
    #     return asseturl + file
    return img_path

# 注册事件结束


app.listening_server_start()  # HTTP API 服务器启动
app.bot.start()  # Bot启动