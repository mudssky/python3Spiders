# -*- coding: utf-8 -*-
import requests
# import time
import os
import json
from pyquery import PyQuery as pq
from multiprocessing import Pool
import time
import re
rjidList=[]
urlList=[]
infoList=[]
htmlPathList = []
def read_rjid(rjidList,filename):
    '''
    从文件中把rjid读入到列表
    :param rjidList: 用于存放rjid的列表
    :param filename: 要读取的文件的名字
    :return:
    '''
    with open(filename,'r',encoding='utf16')as f:
        for rjid in f.readlines():
            rjidList.append(rjid.strip())
    f.close()
    print('读取rjid信息到列表','ok')

def get_urlList(rjidList):
    '''
    通过rjidList列表构造url列表
    :param rjidList:
    :return:
    '''
    for id in rjidList:
        url = 'https://www.dlsite.com/maniax/work/=/product_id/{0}.html'.format(id)
        urlList.append(url)
        print(url)
    print ('拼接获取url列表成功')
    print(urlList)
def getPages(urlList):
    '''
    for循环请求urlList的所有页面并保存
    :param urlList:
    :return:
    '''
    for url in urlList:
        print(url)
        html = requests.get(url).text
        save_page(html,url)
def get_page(url):
    '''
    获取一个指定url的页面并保存
    :param url:
    :return:
    '''
    try:
        res = requests.get(url)
    except Exception as e:
        print(e)
        print('请求url出错，重试',url)
        get_page(url)
        return
    if(res.status_code==200):
        html = res.text
        print('200', url)
        save_page(html,url)
    else:
        html=str(res.status_code)
        print(res.status_code, url)
        save_page2(html,url,'404')
def save_page(html,url):
    '''
    将获取的html文本，命名 rjid.html，从url中取得
    :param html:
    :param url:
    :return:
    '''
    filename = url.split('/')[-1]
    with open(os.path.join('html',filename),'w',encoding='utf8') as f:
        f.write(html)
    f.close()
    print('正在保存html：',filename)
def save_page2(html,url,directory):
    '''
    将获取的html文本，命令为url rjid.html，从url中取得
    :param html:
    :param url:
    :param directory:
    :return:
    '''
    filename = url.split('/')[-1]
    with open(os.path.join(directory,filename),'w',encoding='utf8') as f:
        f.write(html)
    f.close()
    print('正在保存html：',filename)
def parse_a_page(path):
    '''
    解析获得的页面，把有用的信息加到infoList列表
    :param path:
    :return:
    '''
    global infoList
    with open(path,'r',encoding='utf8') as f:
        html = f.read()
    f.close()
    # print(html)
    doc = pq(html)
    desp = doc('.work_article.work_story').text()
    # python .encode('unicode-escape')可以将全角转化为unicode码
    # 为了把标题中【】和其中中包含的内容替换成空，因为里面的内容大多是广告折扣之类
    title = re.sub('\u3010.*\u3011','',doc('title').text())
    work_outline_dom = doc('#work_outline')
    trList = work_outline_dom.children()
    message = (trList.text().replace('\n',':').replace(' ','\n'))
    # print(work_outline_dom.text())
    # trList = work_outline_dom.children().items()
    # list = [i for i in trList]
    # tdList= work_outline_dom.find('td')
    # print(tdList)
    # list = [i for i in tdList.items()]
    # print(list)
    info = {
      'rjid':os.path.basename(path)[:-4],
      'title':title,
     'message':message,
      'desp':desp
    }
    print('info',info)
    infoList.append(info)
    # pyquery遍历列表元素要用items方法
    # for tr in trList.items():
        # print(tr.find('td'))
def saveToJson(infoList):
    '''
    保存信息列表infoList为json文件
    :param infoList:
    :return:
    '''
    with open('infoList.json', 'w') as f:
        f.write(json.dumps(infoList))
        print('infoList.json save completed')
    f.close()
def main():
    oldEjidList=[]
    if not os.path.exists('html'):
        os.mkdir('html')
    if not os.path.exists('404'):
        os.mkdir('404')
    # read_rjid(oldEjidList,'rjid.txt')
    # for x in range(100000,241666):
    #     rjid = 'RJ'+str(x)
    #     if rjid not in oldEjidList:
    #         rjidList.append(rjid)

    for x in range(1,100000):
        xlen=len(str(x))
        if(6>xlen):
            rjid='RJ'+(6-xlen)* '0' +str(x)
        else:
            rjid = 'RJ'+str(x)
        print(rjid)
        if rjid not in oldEjidList:
            rjidList.append(rjid)
    # time.sleep(5)
    print('新列表长度',len(rjidList))
    get_urlList(rjidList)
    pool =Pool()
    pool.map(get_page,urlList)
    for filename in os.listdir('html'):
      htmlPathList.append(os.path.join('html',filename))
    for path in htmlPathList:
        parse_a_page(path)
    # pool = Pool()
    # pool.map(parse_a_page,htmlPathList)
    print('总共解析信息数目:',len(infoList))
    for index,info in enumerate(infoList):
      # with open('details.txt','a',encoding='utf8')as f1 , open('catalog.txt','a',encoding='utf8')as f2:
      with open('details.txt','a',encoding='utf8')as f,open('catalog.txt','a',encoding='utf8')as f2:
          infoStr = '#'+str(index)+'\n'+'rjid:'+info['rjid']+'\n'+'title:'+info['title']+'\n'+'message:'+info['message']+'\n'+'desp:'+info['desp']+'\n\n'
          print(infoStr)
          f.write(infoStr)
          infoStr2=info['rjid']+' '+info['title']+'\n'
          f2.write(infoStr2)
          f.close()
          f2.close()
    print('ok')
    saveToJson(infoList)
    print('json save completed')
    os.system("pause")

if __name__ == '__main__':
    main()