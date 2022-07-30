import sqlite3

uid = int(input("请输入用户uid:"))
SESSDATA = input("请输入SESSDATA:")
bili_jct = input("请输入bili_jct:")
following_count = int(input("请输入关注数:"))
full_cookie = input("请输入完整cookie:")

conn = sqlite3.connect(f"./dd_query/cookies/bili_dd_account.db")
cursor = conn.cursor()

cursor.execute('insert into dds (uid, SESSDATA, bili_jct, full_cookie, following_count) values (?, ?, ?, ?, ?)',
               (uid, SESSDATA, bili_jct, full_cookie, following_count))
conn.commit()
cursor.close()
conn.close()
