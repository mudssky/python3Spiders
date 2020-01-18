# -*- coding: utf-8 -*-
import re
import requests
import time
import os
import json
from multiprocessing import Pool
'''
1.从个人主页获取歌曲详情页url
观察全民k歌的个人页，发现歌曲信息的dom节点并非一次加载，页面下方有个加载更多选项
打开f12，发现每点击一次会加载一个jsonp请求，获取8个歌曲数据
http://node.kg.qq.com/cgi/fcgi-bin/fcg_login_info?jsonpCallback=callback_0&g_tk=5381&outCharset=utf-8&format=jsonp&g_tk_openkey=2093477440&_=1544893333500
http://node.kg.qq.com/cgi/fcgi-bin/kg_ugc_get_homepage?jsonpCallback=callback_2&g_tk=5381&outCharset=utf-8&format=jsonp&type=get_ugc&start=2&num=8&touin=&share_uid=639d9982252432893d&g_tk_openkey=2093477440&_=1544893336103
http://node.kg.qq.com/cgi/fcgi-bin/kg_ugc_get_homepage?jsonpCallback=callback_3&g_tk=5381&outCharset=utf-8&format=jsonp&type=get_ugc&start=3&num=8&touin=&share_uid=639d9982252432893d&g_tk_openkey=2093477440&_=1544893341610
...
http://node.kg.qq.com/cgi/fcgi-bin/kg_ugc_get_homepage?jsonpCallback=callback_24&g_tk=5381&outCharset=utf-8&format=jsonp&type=get_ugc&start=24&num=8&touin=&share_uid=639d9982252432893d&g_tk_openkey=2093477440&_=1544893372591
发现后面的查询字符串，改变的参数只有3个 jsonpCallback=callback_24 callback函数的名字，以及start参数开始的位置，还有最后一个参数明显是unix时间戳
其实还有一个应该也是会变的，就是share_uid

分析这个jsonp发现里面的shareid正好是每首歌曲页面的url中的s参数
http://node.kg.qq.com/play?s=IxMAyhI-hzNhtIHJ&g_f=personal


2.从歌曲详情页获取音频文件源地址
在浏览器f12中搜索audio就找到了播放器元素
但是全民k歌的h5播放器不是随着页面直接加载的，而是js创建的..
抱着试试的心态，将音频原始地址response的页面中检索，结果发现创建播放器的js代码就嵌入在页面中，可以用正则匹配这部分代码
取其中的地址

3.所有需要的信息都收集完了，开启多进程下载


程序运行需要改3个变量，歌曲总数songsNum，还有cookies,还需要你的个人页url
其实两个变量个人页url和cookies也可以实现，但是还要从请求中解析太麻烦了，有需求再改吧。
'''
# 个人歌曲总数，整除8是因为每次请求获取8个数据，这里计算出for循环的请求次数
songsNum=185//8#填入你的个人歌曲总数

# 个人的cookies
cookieStr = '填入你的cookies'
# 用户页面的url
userUrl = '填入你用户页面地址'
# 用户url中的uid参数
share_uid= userUrl.split('=')[1]
# 存放解析后的cookies对象
cookies={}
# 存放请求jsonp接口获得的jsonp字符串
jsonpStrList=[]
# 存放获得歌曲的真实下载地址
songUrls=[]

songInfoList=[]
'''
songInfoList = {
'title':
'shareid':
'songurl'
}
'''

def parse_cookieStr(cookieStr,cookies):
    '''
    把浏览器请求头复制的cookie字符串解析成cookies字典
    :param cookieStr:
    :param cookies:
    :return:
    '''
    for tmp in cookieStr.split(';'):
        name, value = tmp.strip().split('=', 1)
        cookies[name] = value


def get_first8_songs_info(songInfoList,userUrl,cookies):
    '''
    获取个人主页首页的8首歌shareid和title，并加入到songInfoList
    因为qmkg的前8首歌在jsonp请求中没有找到，可能是后端直接渲染的
    :param songInfoList:
    :param userUrl:
    :param cookies:
    :return:
    '''
    userHtml = requests.get(userUrl).text
    # print(userHtml)
    pattarn = re.compile('<li.*?mod_playlist__item.*?data-shareid="(.*?)".*?mod_playlist__title.*?href="(.*?)".*?>(.*?)<',re.S)
    list = re.findall(pattarn,userHtml)
    for info in list:
        songInfoList.append({
            'title':info[2],
            'shareid':info[0]
        })
    print('添加前8首歌完成：',songInfoList)

def get_all_jsonp(songNum, jsonpList, share_uid, cookies):
    '''
    根据jsonp的请求规则请求，获得返回的jsonp字符串加入到jsonpList
    :param songNum: 歌曲数量，根据这个可以构造所有的jsonp链接
    :param jsonpList:
    :param share_uid:
    :param cookies:
    :return:
    '''

    for i in range(2, songsNum + 1):
        url = r'http://node.kg.qq.com/cgi/fcgi-bin/kg_ugc_get_homepage?jsonpCallback=callback_' + str(
            i) + '&g_tk=5381&outCharset=utf-8&format=jsonp&type=get_ugc&start=' + str(
            i) + '&num=8&touin=&'+share_uid+'&g_tk_openkey=2093477440&_=' + \
              str(time.time() * 1000).split('.')[0]
        # print(url)
        jsonpStr = requests.get(url, cookies=cookies).text
        # print(jsonpStr)
        jsonpList.append(jsonpStr)
        print('jsonpList:',jsonpList)
        with open('jsonp.txt', 'a', encoding='utf8') as f:
            f.write(jsonpStr + '\n')
        f.close()


def saveToJson(list,filename):
    '''
    给定列表和一个文件名，在当前文件夹下建立对应的文件保存列表为json
    :param infoList:
    :param filename:
    :return:
    '''
    with open(filename, 'w',encoding='utf8') as f:
        f.write(json.dumps(list))
        print(filename,'save completed')
    f.close()

def parse_jsonp(jsonpList,songInfoList):
    '''
    TODO
    太麻烦了，还要再写一次正则
    :param jsonpList:
    :param songInfoList:
    :return:
    '''
    pass

def parse_jsonpTxt(songInfoList):
    '''
    应急用函数
    如果程序执行过程出错，但是jsonp.txt文件生成了，可以用这个函数抢救一下，解析jsonp.txt文件获取要下载的信息
    将jsonp请求到的数据解析成json,并且加入到歌曲信息，因为每一个步骤请求都保存了数据
    :param songInfoList:
    :return:
    '''
    with open('jsonp.txt', 'r', encoding='utf8') as f:
        jsonpStr = f.read()
        pattern = re.compile('.*?"shareid".*?"(.*?)".*?"title".*?"(.*?)"', re.S)
        # print(re.findall(pattern,jsonpStr))
        json = re.findall(pattern, jsonpStr)
        with open('json.txt', 'w', encoding='utf8') as f:
            f.write(str(json))
        f.close()
        for tuple in json:
            songInfoList.append({
                'title': tuple[1],
                'shareid': tuple[0]
            })
        # saveToJson(songInfoList,'songInfoList.json')
        print('jsonp parse completed')

def get_the_song_url(songInfoList,cookies):
    '''
    从songInfoList中取得shareid组成歌曲详情页地址，解析获得歌曲真实下载地址，并且加入到songInfoList中
    完成后把songInfoList存储到songInfoListjson文件，方便以后使用
    :param songInfoList:
    :param cookies:
    :return:
    '''
    for index,song in enumerate(songInfoList):
        url = 'http://node.kg.qq.com/play?s='+song['shareid']+'&g_f=personal'
        songPageHtml = requests.get(url,cookies=cookies).text
        pattern = re.compile('.*?"playurl".*?"(.*?)"',re.S)
        songUrl = re.findall(pattern,songPageHtml)[0]
        songInfoList[index]['songurl']=songUrl
        print(index,'获取歌曲url信息',songInfoList[index])

    saveToJson(json.dumps(songInfoList),'songInfoList.json')
    # with open('songInfoList.json', 'w', encoding='utf8') as f:
    #     try:
    #         f.write(json.dumps(songInfoList))
    #     except Exception as e:
    #         print('json 解析错误:',e)
    # f.close()
def download_songs(songInfo):
    '''
    下载歌曲，保存到设定哪个好的目录中
    歌曲名用title+shareid的形式，保证文件名不会重名
    :param songInfo:
    :return:
    '''
    global cookies
    # 创建文件夹作为耗时操作，多进程创建文件夹会出问题，可能会出现竞争导致重复创建的异常，
    # if not os.path.exists('qmkg_m4a'):
    #     os.mkdir('qmkg_m4a')
    try:
        song = requests.get(songInfo['songurl'],cookies=cookies).content
        print('下载完成:',songInfo['title'])
    except Exception as e:
        print('requests请求出错',e)
        print('下载出错的歌曲信息：',str(songInfo))
        return
    with open('./qmkg_m4a/'+songInfo['title']+','+songInfo['shareid']+'.m4a','wb') as f:
        f.write(song)
    f.close()

def get_songInfoList_from_json(songInfoList):
    '''
    应急用函数，从songInfoList.json文件中读取数据到songInfoList中
    :param songInfoList:
    :return:
    '''
    with open('songInfoList.json','r')as f:
        list =json.loads(f.read())
        print(list)
    return list
    f.close()

def main():
    # 解析cookie信息
    parse_cookieStr(cookieStr,cookies)
    # 获取前8首歌信息
    get_first8_songs_info(songInfoList,userUrl,cookies)
    # 获取其余歌曲的jsonp响应
    get_all_jsonp(songsNum,jsonpStrList, share_uid,cookies)
    # 解析保存的jsonptxt里面的信息到songInfoList
    parse_jsonpTxt(songInfoList)
    # 取得歌曲url，添加到歌曲信息列表songInfoList
    get_the_song_url(songInfoList,cookies)
    # 提前创建好下载的文件夹，避免多进程竞争创建出现异常
    if not os.path.exists('qmkg_m4a'):
        os.mkdir('qmkg_m4a')
    # 开启进程池，多进程下载
    pool =Pool()
    pool.map(download_songs,songInfoList)

if __name__ == '__main__':
    main()

