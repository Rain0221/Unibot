import dd_query

# dd = dd_query.GetUserFollowingVTB("chinosk")
# dd = dd_query.DDImageGenerate("DD情报局")

# 生成图片路径, 关注vtb数量, 关注up总数
# image_path, vtb_following_count, total_following_count = dd.image_generate()

if __name__ == "__main__":
    while True:
        query_user = input("请输入待查询用户的B站名:")
        dd = dd_query.DDImageGenerate(query_user, max_follow_list=2000)
        print(dd.total_following_vtb)
        #image_path, vtb_following_count, total_following_count = dd.image_generate()
        #print(f"图片已生成, 并保存到了: {image_path}")
        #print(f"{dd.username} 总共关注了 {total_following_count} 位up主, 其中 {vtb_following_count} 位是vtb。\n")
