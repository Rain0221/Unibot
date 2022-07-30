# [成分查询器](https://github.com/chinosk114514/chachengfen)

- 一键生成vtb关注列表图片, 快速查成分！
- 关注列表使用B站接口查询，vtb数据通过[vtbs.moe](https://vtbs.moe/)获取
- 用途: 你可以快速自查, 或者查别人。你还可以稍微修改一下, 把它做到Bot上



# 用法

- `Python 3`环境
- 输入`pip install -r requirements.txt`安装依赖

```
requests
configobj
pydantic
Pillow
```

- 最简单的用法

```python
import dd_query

dd = dd_query.DDImageGenerate("DD情报局")

# 生成图片路径, 关注vtb数量, 关注up总数
image_path, vtb_following_count, total_following_count = dd.image_generate()
```

- 您也可以直接运行`main.py`



# 添加账户

- 众所周知, 查询别人的关注列表, 只能查询前5页, 也就是250个人. 251及以后的关注是查不到的. 因此会出现数据遗漏的情况
- 但是, 查询共同关注是没有限制的. 所以, 只要用几个账号关注所有vtb, 就可以查到完整的数据了
- 如果你懒得折腾, 也可以直接用, 只查前250个人也不少了

## 添加方法

- 首先准备至少两个B站账号, 分别获取这些账号的`UID`, `cookies`

  - `UID`的获取不再赘述。`cookie`中的`SESSDATA`和`bili_jct`请单独复制出来
- 运行`make_dd_account.py`, 按照中文提示, 在对应地方填入信息, 脚本将自动关注所有vtb
- 一个账号关注满, 需要切换账户时, 脚本会导出未关注的vtb数据, 再次运行脚本, 根据提示将导出的vtb数据路径填入即可
- 账户关注完成后, 使用数据库软件打开`dd_query/cookies/bili_dd_account.db`, 在表内添加账号即可。cookie的有效期大约是半年, cookie失效后在数据库更新一下即可



# 已知问题

- 图片有点丑, 欢迎会排版的耶叶PR
- 使用`查看共同关注`的方式无法获取用户关注时间.



# 效果预览

![](https://raw.githubusercontent.com/chinosk114514/chachengfen/main/dd_query/temp/000.jpg)

