# -*- coding: utf-8 -*-
import requests
import logging
import os
import time
import re
from pyquery import PyQuery as pq
import chardet
import json
import pymongo
from multiprocessing import Pool

# 这个网站的结构比较简单，后端是php，没什么多余的请求，纯粹是php请求达出来的，还准备了网站地图，实在很方便你爬
# 我决定先把下载地址提取出来，包括作品的信息，然后存到mongodb。
# 然后用powershell调用多线程下载工具进行下载

# 设置日志
log = logging.getLogger('zxcs')
log.setLevel(logging.DEBUG)

rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
log_path = 'log'
if not os.path.exists(log_path):
    os.mkdir(log_path)
# print(log_path)
log_name = rq + '.log'
logfile = os.path.join(log_path, log_name)
filehandler = logging.FileHandler(logfile, mode='w')
filehandler.setLevel(logging.WARNING)

# 定义错误的输出格式
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
filehandler.setFormatter(formatter)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
consoleHandler.setLevel(logging.DEBUG)

log.addHandler(filehandler)
log.addHandler(consoleHandler)
# 书籍按照标签分类的url，还有分类名的字典作为列表每一个元素，到时候创建分类文件夹的时候要用
# 格式如下
# {url:
# tag:}
tagList = []

# 1.获取所有tag的url信息,用字典存储


def get_tag_url():
    response = requests.get(r'http://www.zxcs.me/map.html')
    mapStr = response.content.decode('utf8')
    doc = pq(mapStr)
    tagDom = doc('#tags ul')
    linkList = tagDom('a')
    for aDom in linkList.items():
        linkStr = aDom.attr('href')
        tag = aDom.text()[:4]
        tagInfo = {
            'url': linkStr,
            'tag': tag
        }
        log.debug('add tag info:%s' % tagInfo)
        # log.warn('sss')
        tagList.append(tagInfo)
    # print(type(tagDom('a')))
    # print(chardet.detect(response.content))
    # logging.debug()


def save_to_json(obj, path):
    log.debug('save json to path'+path)
    with open(path, 'w', encoding='utf8')as f:
        f.write(json.dumps(obj))
    f.close()
    log.debug('save to json complete')


# 获得某标签所有的linklist，并且存储到taglist的字典里面
# 获取每个tag下的所有链接,同样用字典

def get_all_tag_link():
    for taginfo in tagList:
        linkList = get_one_tag_link(taginfo)
        taginfo['linklist'] = linkList
        # print(len(linkList))
        # print(tagList)


def get_one_tag_link(taginfo):
    tag = taginfo['tag']
    url = r'http://www.zxcs.me/tag/'+tag+'/page/1'
    pageStr = requests.get(url).text
    # doc=pq(pageStr)
    # pageSpan=doc('#pagenavi a')
    # print(pageStr)
    tmplinkList = []
    doc = pq(pageStr)
    aDomList = doc('#plist dt a')
    for link in aDomList.items():
        # print(link.attr('href'))
        tmplinkList.append(link.attr('href'))
    # print('list',tmplinkList)
    pagePattern = re.compile('/page/(\d+)"')
    pageNumList = re.findall(pagePattern, pageStr)
    if len(pageNumList) == 0:
        log.debug('总页数1页')
    else:
        pagenum = int(pageNumList[-1])
        log.debug('总页数%s页' % pagenum)
        if pagenum > 1:
            for index in range(1, pagenum+1):
                log.debug('获取第%d页的书籍链接' % index)
                links = get_one_page_links(
                    r'http://www.zxcs.me/tag/'+tag+'/page/'+str(index))
                # log.debug('第%d页获得%d个链接'%(index,len(links)))
                for link in links:
                    tmplinkList.append(link)
        log.debug('该tag下所有链接的总数是：%d' % len(tmplinkList))
        log.debug('linklist'+str(tmplinkList))
    return tmplinkList


def get_one_page_links(pageUrl):
    pageStr = requests.get(pageUrl).text
    # doc=pq(pageStr)
    # pageSpan=doc('#pagenavi a')
    # print(pageStr)
    tmplinkList = []
    doc = pq(pageStr)
    aDomList = doc('#plist dt a')
    for link in aDomList.items():
        tmplinkList.append(link.attr('href'))
    return tmplinkList


def get_one_bookInfo(link, tag):
    try:
        res = requests.get(link)
    except Exception as e:
        log.error('get bookinfo error,retry:'+link, +str(e))
    pageStr = res.content.decode('utf8')
    doc = pq(pageStr)
    downloadPage = doc('.down_2 a').attr('href')
    title = doc('#content h1').text()
    desp = doc('#content').text()
    twoLink = get_download_link(downloadPage)
    link1 = twoLink[0]
    link2 = twoLink[1]
    bookInfo = {
        'tag': tag,
        'title': title,
        'desp': desp,
        'link1': link1,
        'link2': link2,
        'bookurl': link
    }
    # log.debug(bookInfo)
    return bookInfo

    # log.debug(str(div))


def get_download_link(downloadPage):
    try:
        response = requests.get(downloadPage)
    except Exception as e:
        log.error('get download link error ,retry:'+downloadPage+str(e))
        get_download_link(downloadPage)
    pageStr = response.text
    # print(pageStr)
    doc = pq(pageStr)
    tmplinksList = []
    links = doc('.downfile a')
    for alink in links.items():
        tmplinksList.append(alink.attr('href'))
    log.debug('get download link succeed:'+str(tmplinksList))
    if len(tmplinksList) != 2:
        log.fatal('not enough link')
    return tmplinksList


def load_tagListWithLinks():
    with open('tagListWithLinks.json', 'r', encoding='utf8')as f:
        tagList = json.loads(f.read())
    f.close()
    return tagList


def get_book_tag(bookurl):
    htmlStr = requests.get(bookurl).text
    doc = pq(htmlStr)
    aList = doc('.date a')
    tag = aList[2].text
    return tag

# def exist_book(bookurl):


def loadErrorLog():
    with open('log/202112011833.log', 'r+', encoding='utf8') as f:
        logstr = f.read()
        # linkerror: http: // www.zxcs.me / post / 3707Document is empty
        bookurlPattern = re.compile('(http.*?\d+)', re.S)
        bookurlList = re.findall(bookurlPattern, logstr)

        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client['zxcsSpider']
        collection = db['bookinfo']

        for link in filteredBookurlList:
            tag = get_book_tag(link)
            bookinfo = get_one_bookInfo(link, tag)
            ps1path = tag + '.ps1'
            # ps1append = ''
            newline = '\naria2c "-s2 %s" "%s" ' % (
                bookinfo['link1'], bookinfo['link2'])
            with open(ps1path, 'a', encoding='utf16')as f:
                f.write(newline)
            f.close()
            insert_result = collection.insert_one(bookinfo)
            log.debug(str(insert_result))


def main():
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['zxcsSpider']
    collection = db['bookinfo']
    allBookInfoList = []
    # log.info('start spider')
    # get_tag_url()
    # save_to_json(tagList,'tagList.json')
    # get_one_bookInfo(r'http://www.zxcs.me/post/11069')
    # get_download_link('http://www.zxcs.me/download.php?id=11069')
    # get_all_tag_link()
    # save_to_json(tagList,'tagListWithLinks.json')
    # get_one_tag_link({'tag':'西方奇幻','url':'http://www.zxcs.me/tag/%E8%A5%BF%E6%96%B9%E5%A5%87%E5%B9%BB'})

    # tagList = load_tagListWithLinks()
    # index = 0
    # for i,tmp in enumerate(tagList):
    #     if tmp['tag']=='两宋元明':
    #         index=i
    # tagList=tagList[index:]
    get_tag_url()
    get_all_tag_link()
    for tag in tagList:
        ps1Name = tag['tag']+'.ps1'
        ps1Str = 'mkdir "%s";cd "%s"' % (tag['tag'], tag['tag'])
        linklist = tag['linklist']
        for link in linklist:
            if collection.count({'bookurl': link}) != 0:
                continue
            # 已下载的书跳过
            # if collection.find_one({'bookurl': link}):
            #     print(f'skip: tag{tag},url:{link}')
            #     continue
            try:
                bookinfo = get_one_bookInfo(link, tag['tag'])
                one_download_str = 'aria2c -s2 "%s" "%s" ' % (
                    bookinfo['link1'], bookinfo['link2'])
                ps1Str += '\n'+one_download_str
                allBookInfoList.append(bookinfo)
                insert_result = collection.insert_one(bookinfo)
                log.debug(str(insert_result))
            except Exception as e:
                log.error('deal with link error:'+link+str(e))
        if (len(ps1Str) > 20):
            with open(ps1Name, 'w', encoding='utf16')as f:
                f.write(ps1Str)


if __name__ == "__main__":
    # main()
    # get_one_tag_link({'tag': '原生幻想'})
    # loadErrorLog()
    main()
