# -*- coding: utf-8 -*-
import requests
import re
import json
import os
from multiprocessing import Pool
'''
下载音泉的radio音频，从节目详情页把要下载的节目id添加到pragram列表中运行即可
自动在当前文件夹下创建目录，目录为“节目名+主持人”，文件名为“节目回数+[播放时间]+邀请嘉宾“
运行完后，会把相关信息保存到当前目录的infoList.json文件，下次启动时用于判断节目更新状况

国内需要翻墙才能使用，需要python运行环境，以及第三方requests库
例如
越夸越牛逼的广播，详情页url 为 http://www.onsen.ag/program/home/ 加到节目列表的id为 home

onsen.ag使用的是jquery.ajax发送jsonp请求，页面引入了top.index.js和top.play.js文件，分析这两个文件，可以得到最后请求jsonp的格式为url = r'http://www.onsen.ag/data/api/getMovieInfo/'+id+'?callback=callback'
解析获得的jsonp可以从中找到音频的下载地址。

音泉非会员只能听普通广播，而且可以免费听最近一次，这个api就是获取最近一次广播的信息的效果。
'''
# 存放要下载节目的id
pragramIdList=[
    'aurora',
    'vac',
    'otomain',
    'danger',
    'home'
]
# 存放jsonp请求的url地址
jsonpUrlList=[]
#存放获取到的jsonp字符串
jsonpList=[]

'''
有用信息的字典
{
mp3url
count
guest
personality
title
upadte
}
'''
# 存放最后要下载的节目信息
infoList=[]

def getNewInfoList(pragramIdList,jsonpUrlList):
    '''
    通过节目列表里面的id拼接jsonp请求url，并且添加到jsonpUrlList里
    :param pragramIdList:
    :param jsonpUrlList:
    :return:
    '''
    for id in pragramIdList:
        url = r'http://www.onsen.ag/data/api/getMovieInfo/'+id+'?callback=callback'
        jsonpUrlList.append(url)
    print ('jsonpUrlList：',jsonpUrlList)

def getJsonpList(jsonpUrlList,jsonpList):
    '''
    对jsonpUrlList中的地址发起请求，获取jsonp字符串加到jsonpList里
    :param jsonpUrlList:
    :param jsonpList:
    :return:
    '''
    for url in  jsonpUrlList:
        jsonp = requests.get(url).text
        jsonpList.append(jsonp)
    print('jsonpStrList:',jsonpList)

def parseJsonpToJson(jsonpStr):
    '''
    输入jsonp参数，利用re模块解析里面的json，返回去掉外层函数包裹的json字符串
    :param jsonpStr:
    :return: jsonStr
    '''
    pattarn=re.compile('.*?({.*}).*',re.S)
    jsonStr = re.match(pattarn,jsonpStr).group(1)
    return jsonStr

def saveToJson(infoList):
    '''
    将本次请求到的节目信息储存，下次启动可用于检查更新
    :param infoList:
    :return:
    '''
    with open('infoList.json', 'w') as f:
        f.write(json.dumps(infoList))
        print('infoList.json save completed')
    f.close()
def getInfoList(infoList,jsonpList):
    '''
    遍历jsonp列表解析json，筛选形成一个节目信息的字典并且添加到infoList中
    判断节目有没有更新，如果没有更新，就清空infoList列表，并且打印提示信息
    如果节目发生更新，就同样清空infoList列表，将json文件中提取的list和清空之前的infoLIst的对比，把新增加的节目放到infoList中
    :param infoList:
    :param jsonpList:
    :return:
    '''
    for jsonp in jsonpList:
        jsonStr = parseJsonpToJson(jsonp)
        jsonDict = json.loads(jsonStr)
        infoList.append({
            'title':jsonDict['title'],
            'personality':jsonDict['personality'],
            'guest':jsonDict['guest'],
            'audioUrl':jsonDict['moviePath']['pc'],
            'count':jsonDict['count'],
            'update':jsonDict['update'],
            'schedule':jsonDict['schedule'],
            'pictureUrl':jsonDict['thumbnailPath']
        })
    if not os.path.exists('infoList.json'):
        print('json文件未发现，保存到json文件')
        # print(json.loads(jsonStr))
        saveToJson(infoList)
    else:
        if(isUpdated(infoList)):
            with open('infoList.json', 'r') as fi:
                oldInfoList = json.loads(fi.read())
                print(oldInfoList)
            fi.close()
            # 旧的json文件已经读取到oldInfoList，在清空列表之前，把新数据保存
            saveToJson(infoList)
            newList =[]
            # 这部分只考虑了节目数量多少来判断，而不是遍历两个列表对比，这样导致，如果是代码内的节目因为不更新删掉，但是程序还是会默认执行一次多余的更新,而且列表的顺序发生变化可能会导致程序错误
            # 可以采用再储存一个节目列表的方式，不过改动起来有些麻烦了，或者在字典外层再包一个字典，用节目代号做键，不过改起来过于麻烦了，还是算了，将就着用，以后删节目的时候，同时删json和程序文件就行了。
            # 还有就是json作为存储文件，每次基本上只存程序运行中的数据结构，而不是把过去的信息也像日记一样记录下来，不适合持久存储，查询也不方便，以后数据存储还是要用数据库
            for index, info in enumerate(infoList):
                if(index>=len(oldInfoList)):
                    newList.append(info)
                else:
                    if (info['count'] != oldInfoList[index]['count']):
                        newList.append(info)
            # 清空列表，再将临时变量里的内容都添加进去
            infoList.clear()
            for info in newList:
                infoList.append(info)
        else:
            # 没有更新的时候也要清空列表
            infoList.clear()
            print('当前的节目没有新的更新')

def isUpdated(infoList):
    with open('infoList.json', 'r') as fi:
        oldInfoList = json.loads(fi.read())
    fi.close()
    # print(oldInfoList)
    # print(infoList)
    # 当旧的信息个数小于新信息时，直接判断发生了更新
    res = len(infoList)-len(oldInfoList)
    if res>0:
        print('节目有新的更新','需下载数量:',res)
        return True
    for index, info in enumerate(infoList):
        # print(index ,info)
        # print(info['count'],oldInfoList[index]['count'])
        if ( info['count'] != oldInfoList[index]['count']):
            return True
    return False

def download_infoList(info):
    dirname = info['title']+' '+info['personality']
    cleanDirname = re.sub('[\/:*?"<>|]', '-', dirname)
    if  not os.path.exists(cleanDirname):
        os.mkdir(cleanDirname)
    # 文件扩展名获取暂时用从获取url末尾四个字符来实现
    filename = info['count']+'['+info['update']+']'+info['guest']+info['audioUrl'][-4:]
    with open(os.path.join(cleanDirname,filename),'wb') as f:
        # 请求的是https地址，关闭认证
        print('正在下载',info['title'],info['count'])
        # 下载稍大文件，开启流模式
        res = requests.get(info['audioUrl'],verify=False,stream=True)
        resHeaders = res.headers
        total = int(resHeaders['Content-Length'])
        print(info['title'],'文件大小:',str(total/1000),'kb')
        downloaded_size = 0;
        for chunk in res.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
                f.flush()
                downloaded_size+=len(chunk)
                print(info['title'],'下载进度:%d/%d kb'%(downloaded_size/1024,total/1024))
    f.close()
    if (downloaded_size == total):
        print('='*100)
        print(info['title'], 'download succeed')
        print('='*100)
    else:
        print('x'*100)
        print(info['title'], 'failed,some contents  not get  %d/%d' % (downloaded_size, total))
        # 下面这句话存在歧义，python解释成创建一个局部变量info ，赋值为{}，所以对实际info不会生效
        # print('已清空此info对象，重新执行本程序即可')
        # info={}
        # 修改count的值，重启程序比对会发现数据和最新的不同，自动重新下载
        info['count']='failed'
        print('x'*100)
    pictureUrl =r'http://www.onsen.ag'+ info['pictureUrl']
    coverFilename = info['personality']+'cover'+info['pictureUrl'][-4:]
    cleanCoverName = re.sub('[\/:*?"<>|]', '-', coverFilename)
    picPath = os.path.join(cleanDirname,cleanCoverName)
    download_cover(pictureUrl,picPath)

def download_cover(pictureUrl,path):
    if os.path.exists(path):
        print('图片已存在，跳过下载')
        return
    pic = requests.get(pictureUrl).content
    with open (path,'wb')as f:
        f.write(pic)
    f.close()
    print('广播封面下载完成：',pictureUrl)

def main():
    getNewInfoList(pragramIdList,jsonpUrlList)
    getJsonpList(jsonpUrlList,jsonpList)
    getInfoList(infoList,jsonpList)
    print('final infoList:',infoList)
    # for info in infoList:
    #     download_infoList(info)
    print('本次更新了',len(infoList),'个节目：')
    for info in infoList:
        print(info['update'],info['title'],info['count'],info['guest'])
    pool=Pool()
    pool.map(download_infoList,infoList)


if __name__ == '__main__':
    main()