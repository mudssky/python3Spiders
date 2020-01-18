# -*- coding: utf-8 -*-
import requests
import time
import os
import json
# from string import Template
from pyquery import PyQuery as pq
from multiprocessing import Pool
import re
# pyinstaller needed ,for multoprocessing
import multi_process_support
rgidList=[]
urlList=[]
infoList=[]
htmlPathList = []
def read_rjid(rgidList,filename):
    with open(filename,'r',encoding='utf16')as f:
        for rgid in f.readlines():
            rgidList.append(rgid.strip())
    f.close()
    print('读取rjid信息到列表','ok')

def get_urlList(rgidList):
    for id in rgidList:
        url = 'https://www.dlsite.com/maniax/work/=/product_id/{0}.html'.format(id)
        urlList.append(url)
        print(url)
    print ('拼接获取url列表成功')
    print(urlList)
def getPages(urlList):
    for url in urlList:
        print(url)
        html = requests.get(url).text
        save_page(html,url)
def get_page(url):
    html = requests.get(url).text
    save_page(html,url)

def save_page(html,url):
    filename = url.split('/')[-1]
    with open(os.path.join('html',filename),'w',encoding='utf8') as f:
        f.write(html)
    f.close()
    print('正在保存html：',filename)

def parse_a_page(path):
    global infoList
    with open(path,'r',encoding='utf8') as f:
        html = f.read()
    f.close()
    # print(html)
    doc = pq(html)
    desp = doc('.work_article.work_story').text()
    # python .encode('unicode-escape')可以将全角转化为unicode码
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
      'rgid':os.path.basename(path)[:-4],
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
    with open('infoList.json', 'w') as f:
        f.write(json.dumps(infoList))
        print('infoList.json save completed')
    f.close()
def main():
    # parse_a_page(os.path.join('html','RJ115388.html'))
    # print('ok')
    if not os.path.exists('html'):
        os.mkdir('html')
    read_rjid(rgidList,'rjidList.txt')
    get_urlList(rgidList)
    pool =Pool()
    pool.map(get_page,urlList)
    for filename in os.listdir('html'):
      htmlPathList.append(os.path.join('html',filename))
    for path in htmlPathList:
        parse_a_page(path)
    # pool = Pool()
    # pool.map(parse_a_page,htmlPathList)
    print('总共解析信息数目:',len(infoList))
    saveToJson(infoList)
    for index,info in enumerate(infoList):
      # with open('details.txt','a',encoding='utf8')as f1 , open('catalog.txt','a',encoding='utf8')as f2:
      with open('details.txt','a',encoding='utf8')as f,open('catalog.txt','a',encoding='utf8')as f2:
          infoStr = '#'+str(index)+'\n'+'rgid:'+info['rgid']+'\n'+'title:'+info['title']+'\n'+'message:'+info['message']+'\n'+'desp:'+info['desp']+'\n\n'
          print(infoStr)
          f.write(infoStr)
          infoStr2=info['rgid']+' '+info['title']+'\n'
          f2.write(infoStr2)
          f.close()
          f2.close()
          # str1 = '#'+str(index)+'\n'
          # 'start '+info['rgid']+'\n'+
          # 'title:'+info['title']+'\n'+
          # strTmp = ('#${index}\n'
          #         'rgid: ${info["rgid"]}\n'
          #         'title: ${info["title"]}\n'
          #         'offeringDate: ${info["offeringDate"]}\n'
          #         'scenario: ${info["scenario"]} cv: ${info["cv"]}\n'
          #         'age: ${info["age"} categories: ${info["catagories"}\n'
          #         'desp: ${indo["desp"]}\n\n')
          # str1 = Template(strTmp,info)
          # f1.write(str1.safe_substitute(info,index))
          # str2 = '[${info["rgid"]],${info["title"],${offeringDate}\n}'
          # f2.write(str2.safe_substitute(strTmp, index))
          # f1.close()
          # f2.close()
    print('ok')
    os.system("pause")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()