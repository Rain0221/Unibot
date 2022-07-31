import re

'''
作用：生成无可视长条节点的sus谱面文件

先去 https://suspatcher.unijzlsx.com/ 抓取谱面，
该网站抓取的sus去掉了所有air，skills，fever，fever chance键

接着将谱面文件放到相应文件夹下，运行该脚本删除可视节点

最后将谱面文件用 https://sus2img.paltee.net/ 转换为图片

仅作为 Sekai Viewer 和 プロセカ谱面保管所 都没更新谱面时的补救
'''

def removevisual(dir):
    with open(dir, encoding='utf-8') as f:
        sus = f.read()
    lines = sus.split('\n')
    newsus = ''
    for line in lines:
        pattern = re.compile(r'(?<=#\d\d\d)3')
        if len(pattern.findall(line)) == 1:
            print(line)
            after = line[line.find(':')+1:]
            newafter = ''
            for i in range(0, int(len(after)/2)):
                if after[2*i] == '3':
                    newafter += '5'+after[2*i+1]
                else:
                    newafter += after[2*i:2*i+2]
            line = line[:line.find(':')+1] + newafter
            print(line)
        newsus += line + '\n'
    # print(out)
    with open(dir, 'w', encoding='utf-8') as f:
        f.write(newsus)

def processidchart(musicid):
    removevisual(f'../charts/sus/{musicid}/master.sus')
    removevisual(f'../charts/sus/{musicid}/expert.sus')

if __name__ == '__main__':
    processidchart(240)