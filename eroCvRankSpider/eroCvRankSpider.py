# -*- coding: utf-8 -*-
import requests
import os
import gzip
import sqlite3
import re
import time
from pyquery import PyQuery as pq
from multiprocessing import Pool


list404 = []
def get_one_page(url):
    global list404
    try:
        res = requests.get(url)
    except Exception as e:
        print('请求url出现错误,重新请求',url)
        print(e)
        get_one_page(url)
        return
    print(res.headers)
    if res.status_code == 200:
        # html = decode_gzip(res.content)
        html = res.content.decode('utf8')
        save_one_page(url,html,'html')
        print('200',url)
    else:
        html = '404'
        print(res.status_code,url)
        list404.append(url)
        save_one_page(url,html,'404')
    print(html)

def decode_gzip(html):
    try:
        decoded = gzip.decompress(html).decode('utf-8')
    except :
        print('解码为utf8')
        decoded = html.decode("utf-8")
    return decoded
def save_one_page(url,html,directory=''):
    filename = url.split('/')[-1] +'.html'
    path = os.path.join(directory,filename)
    with open(path,'w',encoding='utf8') as f:
        f.write(html)
    f.close()
    print('保存完成',path)

def pase_one_page(filename,cursor):
    with open(os.path.join('html',filename),'r',encoding='utf8') as f:
        htmlStr = f.read()
    f.close()
    doc = pq(htmlStr)
    title_pattern = re.compile('<title>(.*?)</title>',re.S)
    rawtitle = re.findall(title_pattern,htmlStr)[0]
    title = rawtitle[:-8]
    page_url = r'http://voice.amone.info/game/detail/'+ filename.split('.')[0]

    cover_url_pattern = re.compile('game_cover.*?<img.*?data-src="(.*?)"', re.S)
    cover_url_list = re.findall(cover_url_pattern,htmlStr)
    if cover_url_list :
        cover_url = cover_url_list[0]
    else:
        cover_url = ''

    maker_pattern = re.compile('メーカー</th>.*?<td>.*?<a.*?>(.*?)<')
    maker_list = re.findall(maker_pattern,htmlStr)
    if maker_list :
        maker = maker_list[0]
    else:
        maker = ''

    official_website_pattern = re.compile('公式サイト</th>.*?<td>.*?<a.*?>(.*?)<')
    official_website_list = re.findall(official_website_pattern, htmlStr)
    if official_website_list:
        official_website = official_website_list[0]
    else:
        official_website = ''

    sales_day_pattern = re.compile('発売日</th>.*?<td>(.*?)<')
    sales_day_list =  re.findall(sales_day_pattern, htmlStr)
    if sales_day_list:
        sales_day = sales_day_list[0]
    else:
        sales_day = ''

    sales_page_pattern = re.compile('販売ページ</th>.*?<a.*?href="(.*?)"')
    sales_page_list = re.findall(sales_page_pattern, htmlStr)
    if sales_page_list:
        sales_page = sales_page_list[0]
    else:
        sales_page = ''
    # 插入游戏信息
    sql = r'''insert into game (page_url,cover_url,title,maker,sales_day,official_website,sales_page)values("{0}","{1}","{2}","{3}","{4}","{5}","{6}");
      '''.format(page_url, cover_url, title, maker, sales_day, official_website,sales_page)
    print('excute sql', sql)
    cursor.execute(sql)
    game_id = cursor.lastrowid
    print('effect',cursor.rowcount,'rows','game_id',game_id)
    imgSample = doc('.sample')
    if  imgSample:
        imgSampleHtml = imgSample.html()
    else:
        imgSampleHtml=''


    img_pattern= re.compile('data-src="(.*?)"',re.S)
    img_list = re.findall(img_pattern,imgSampleHtml)
    print(img_list)
    for img_url in img_list:
        print('insert',img_url,game_id)
        cursor.execute('insert into "game-img" (img_url,game_id)values("{0}","{1}")'.format(img_url,game_id))

    game_cv_pattern = re.compile('<td>(.*?)</td>.*?<a.*?>(.*?)<', re.S)
    voice_table=doc('.table-voice')
    if voice_table:
        game_cv_list = re.findall(game_cv_pattern,voice_table.html())
        for cv in game_cv_list:
            print("excute",cv[0],cv[1],game_id)
            cursor.execute('insert into "game-cv" (character_name,cv_name,game_id,game_title)values("{0}","{1}","{2}")'.format(cv[0],cv[1], game_id,title))
    else:
        print("cv-table not found")
    # print('game_cv',game_cv_list)
    print('sales_page:',sales_page)
    print('sales_day:',sales_day)
    print('official_website:', official_website)
    print('maker:',maker)
    print('cover_url:',cover_url)
    print('page_url:',page_url)
    print('game表信息插入成功')

def main():
    urlList = []
    if not os.path.exists('html'):
        os.mkdir('html')
    if not os.path.exists('404'):
        os.mkdir('404')
    urlbase = 'http://voice.amone.info/game/detail/'
    # urlList = [urlbase+str(x) for x in range(1,25000)]
    with open('1.txt','r',encoding='utf8') as f:
        file = f.read()
        list = file.split('\n')
        for x in range(1,25000):
            if str(x) not in list:
                urlList.append(urlbase+str(x))
        # list = file.split('\n')
        # print(len(list))
        print(len(urlList))
    f.close()
    # get_one_page(urlbase+'3')
    # urlList =['']
    # for url in urlList:
    #     print(url)
    pool = Pool()
    pool.map(get_one_page,urlList)
    save_one_page('404/404',str(list404))

def save_all_to_sqlite():
    conn = sqlite3.connect('galgame.db')
    cursor = conn.cursor()
    htmlList = os.listdir('html')
    for html in htmlList:
        pase_one_page(html, cursor)
    cursor.close()
    conn.commit()
    conn.close()
def download_cover_from_sqlite3(cursor):
    cursor.execute('select id,cover_url from game where cover_url is not null and cover_url is not "" ')
    urllist = cursor.fetchall()
    print(list)
def download_cover(item,cursor):
    pictureUrl = item[1]
    game_id=item[0]
    filename = str(time.time())+item[1][-4:]
    path = os.path.join('cover',filename)
    if os.path.exists(path):
        print('图片已存在，跳过下载')
        return
    pic = requests.get(pictureUrl).content
    print('len',len(pic),path)
    with open (path,'wb')as f:
        f.write(pic)
    f.close()
    print(game_id, 'gal封面下载完成：',pictureUrl)
    sql = 'update  game set cover_path = "{0}" where id ={1}'.format(path,game_id)
    print(sql)
    cursor.execute(sql)
def redownload_cover():
    if not os.path.exists('cover'):
        os.mkdir('cover')
    rootPtah = os.path.abspath('.')
    conn = sqlite3.connect('galgame.db')
    cursor = conn.cursor()
    cursor.execute('select id,cover_url,cover_path from game where cover_path is not null and cover_path is not "" ')
    path_list = cursor.fetchall()
    for item in path_list:
        # windowsPath = item[2].replace('\\','/')
        print(item)
        if os.path.exists(item[2]):
            filesize = os.path.getsize(item[2])
            print('filezie',filesize)
            if filesize:
                print('文件大小正常')
            else:
                os.remove(item[2])
                download_cover((item[0], item[1]), cursor)
                conn.commit()
                print('delete', item[2], 'redownload', item[0], item[1])
        else:
            download_cover((item[0],item[1]),cursor)
            print('path not exsits,redownload and upadte',item[0],item[1],item[2])
            conn.commit()

def get_all_cover():
    if not os.path.exists('cover'):
        os.mkdir('cover')
    conn = sqlite3.connect('galgame.db')
    cursor = conn.cursor()
    # download_cover_from_sqlite3(cursor)
    cursor.execute('select id,cover_url from game where cover_url is not null and cover_url is not "" ')
    url_list = cursor.fetchall()
    for item in url_list:
        download_cover(item,cursor)
        conn.commit()
    # print(urllist)
    cursor.close()
    conn.close()
if __name__ == '__main__':
    # filenameList = os.listdir('html')
    # with open('html/23839.html','r',encoding='utf8') as f:
    #     htmlStr = f.read()
    #     pase_one_page(htmlStr)
    redownload_cover()


