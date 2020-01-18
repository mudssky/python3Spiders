import requests
import os
import sys
import re
import html
import os
import time
import pymongo
from pyquery import PyQuery as pq
from multiprocessing import Pool


class GetchuSpider():
    def __init__(self,getchu_url,file_path='',collection=''):
        self.getchu_url=getchu_url
        self.file_path=file_path
        # self.getchu_id=getchu_url.split('=')[1][:-3] or file_path.split('\\')[-1][:-5] or ''
        # self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.collection=''
        if collection:
            self.collection = collection
        else:
            raise('didnt give a  certain db ')
        if getchu_url:
            self.getchu_id = getchu_url.split('=')[1][:-3]
        elif file_path:
            self.getchu_id=file_path.split('\\')[-1][:-5]
        else:
            raise ('please give a getchu_url or file path')

    def get_one_page(self):
        page_url=self.getchu_url
        try:
            response = requests.get(page_url)
            content_length=response.headers['content-length']
            if int(content_length)<1300:
                print('content_length',content_length)
                return ''
            resText=response.text
        except Exception as e:
            print('get url error',page_url,e)
            print('retry...')
            return self.get_one_page(page_url)
        # cleanHtml=resText.encode('utf8')
        return resText

    def save_page(self,htmlStr):
        page_url=self.getchu_url
        if not os.path.exists('html'):
            os.mkdir('html')
        filename=page_url.split('=')[1][:-3]+'.html'
        print(filename)
        path=os.path.join('html',filename)
        with open(path,'w',encoding='utf8')as f:
            f.write(htmlStr)
        f.close()
        print('save completed',filename)


    def getFindedStr(self,findedList):
        if len(findedList)==0:
            return ''
        else:
            return findedList[0]


    def parse_one_page(self,htmlStr):

        unescapedHtmlStr=html.unescape(htmlStr)
        doc=pq(unescapedHtmlStr)
        soft_table =doc('#soft_table')
        soft_table_html=soft_table.html()
        # # print('html:',soft_table_html)
        # # print(soft_table)
        # # print('#'*50)


        # 获得getchu_id
        # getchu_id=filePath.split('\\')[-1][:-5]
        getchu_id=int(self.getchu_id)
        # print('getchu_id:',getchu_id)

        # 匹配标题
        title=soft_table('#soft-title').text().strip('（このタイトルの関連商品）').strip('\n')
        # print('title:',title)

        # 匹配品牌
        brandsite = ''
        brand_dom = soft_table('#brandsite')
        brand = brand_dom.text()
        # print('brand',brand)
        site = brand_dom.attr('href')
        if site:
            brandsite = site

        # 匹配定价
        price_pattern =  re.compile(r'定価：.*?<td.*?>(.*?)</td',re.S)
        price_list = re.findall(price_pattern,soft_table_html)
        price=self.getFindedStr(price_list)
        # print('price:',price)

        # 匹配发售日
        on_sale=soft_table('#tooltip-day').text()
        # print('on_sale:',on_sale)

        # 匹配媒体形式
        midea_pattern=re.compile(r'メディア：.*?<td.*?>(.*?)</td',re.S)
        midea_list=re.findall(midea_pattern,soft_table_html)
        midea=self.getFindedStr(midea_list)
        # print('midea:',midea)

        # 匹配类别
        genre_pattern=re.compile(r'ジャンル：.*?<td.*?>(.*?)</td',re.S)
        genre_list=re.findall(genre_pattern,soft_table_html)
        # # print('genre_list:',genre_list)
        genre = self.getFindedStr(genre_list)
        # print('genre:',genre)

        # 匹配JAN码
        jan_code_pattern=re.compile(r'JANコード：.*?<td.*?>(.*?)</td',re.S)
        jan_code_list=re.findall(jan_code_pattern,soft_table_html)
        jan_code=self.getFindedStr(jan_code_list)
        # print('jan_code:',jan_code)

        # 匹配原画列表
        painter_str_pattern = re.compile(r'原画：.*?<td.*?>(.*?)</td',re.S)
        painter_str_list=re.findall(painter_str_pattern,soft_table_html)
        painter_str=self.getFindedStr(painter_str_list)

        if painter_str:
            aText_pattern=re.compile(r'a.*?>(.*?)</a',re.S)
            painter_list=re.findall(aText_pattern,painter_str)
            # painters=pq(painter_str)
            # painter_list=painters('a').text()
        else:
            painter_list=[]

        # print('painter_list:', painter_list)

        # 匹配脚本家列表
        scenario_list_html_pattern=re.compile(r'シナリオ：.*?<td.*?/td',re.S)
        scenario_list_html_list=re.findall(scenario_list_html_pattern,soft_table_html)
        scenario_list_html=self.getFindedStr(scenario_list_html_list)

        if scenario_list_html:
            scenario_list_pattern = re.compile(r'<a.*?>(.*?)</a',re.S)
            scenario_list=re.findall(scenario_list_pattern,scenario_list_html)
        else:
            scenario_list=[]

        # print('scenario_list:',scenario_list)

        # 匹配特典
        specials_pattern = re.compile(r'商品同梱特典：.*?<td.*?>(.*?)</td',re.S)
        specials_list=re.findall(specials_pattern,soft_table_html)
        specials=self.getFindedStr(specials_list)
        # print('specials:',specials)

        # 匹配备注
        bikou=soft_table('.bikoubody').text().replace('\n',',')
        # print('bikou:',bikou)

        # 匹配动作环境
        system_requirements_pattern=re.compile(r'製品仕様／動作環境.*?<table.*?>(.*?)</table',re.S)
        system_requirements_list=re.findall(system_requirements_pattern,soft_table_html)
        system_requirements_html=self.getFindedStr(system_requirements_list)

        if(system_requirements_html):
            system_requirements=pq(system_requirements_html).text().replace('\n',',')
        else:
            system_requirements=''
        # print('system_requirements:',system_requirements)

        # 匹配品番
        series_number_pattern=re.compile(r'品番：.*?<td.*?>(.*?)</td',re.S)
        series_number_list=re.findall(series_number_pattern,soft_table_html)
        series_number=self.getFindedStr(series_number_list)
        # print('series_number:',series_number)

        # 匹配类别标签列表
        category_list_html_pattern=re.compile(r'カテゴリ：.*?<td.*?>(.*?)一覧',re.S)
        category_list_html_list=re.findall(category_list_html_pattern,soft_table_html)
        category_list_html=self.getFindedStr(category_list_html_list)
        # print('category_list_html:',category_list_html)
        if category_list_html:
            category_list_pattern=re.compile(r'<a.*?>(.*?)</a',re.S)
            category_list=re.findall(category_list_pattern,category_list_html)
        else:
            category_list=[]
        # print('category_list:',category_list)

        # 匹配子类别列表
        subgenre_html_pattern=re.compile(r'サブジャンル.*?<td(.*?)一覧',re.S)
        subgenre_html_list=re.findall(subgenre_html_pattern,soft_table_html)
        subgenre_html=self.getFindedStr(subgenre_html_list)

        if subgenre_html:
            subgenre_list_pattern=re.compile(r'<a.*?>(.*?)</a',re.S)
            subgenre_list=re.findall(subgenre_list_pattern,subgenre_html)
        else:
            subgenre_list=[]
        # print('subgenre_list:',subgenre_list)

        # 匹配作品介绍
        introduction_html_pattern=re.compile(r'作品紹介</div>.*?<div.*?>(.*?)</div',re.S)
        introduction_html_list=re.findall(introduction_html_pattern,unescapedHtmlStr)
        introduction_html=self.getFindedStr(introduction_html_list)
        # # print(introduction_html)
        if introduction_html:
            # # print(introduction_html)
            introduction=pq(introduction_html).text()
        else:
            introduction=''
        # print('introduction:',introduction)

        # 匹配story
        story_html_pattern = re.compile(r'ストーリー</div>.*?<div.*?>(.*?)</div',re.S)
        story_html_list=re.findall(story_html_pattern,unescapedHtmlStr)
        story_html=self.getFindedStr(story_html_list)
        if story_html:
            story=pq(story_html).text()
        else:
            story=''
        # print('story:',story)

        # 匹配角色信息
        chara_list=[]
        chara_html_pattern=re.compile(r'キャラクター.*?</div.*?<table.*?>(.*?)</table>',re.S|re.IGNORECASE)
        chara_html_list=re.findall(chara_html_pattern,unescapedHtmlStr)
        chara_html=self.getFindedStr(chara_html_list)
        # # print('chara_html:',chara_html)
        if chara_html:
            chara_doc=pq(chara_html)
            chara_texts=chara_doc('.chara-text')
            for chara_text in chara_texts.items():
                chara_name_text=chara_text('.chara-name').text()
                chara_name=chara_name_text
                chara_cv = ''
                chara_yumi = ''
                chara_cv_pattern=re.compile(r'CV：(.*)$',re.S)
                chara_cv_list=re.findall(chara_cv_pattern,chara_name_text)
                chara_cv=self.getFindedStr(chara_cv_list)

                chara_yumi_pattern=re.compile(r'（(.*?)）',re.S)
                chara_yumi_list=re.findall(chara_yumi_pattern,chara_name_text)
                chara_yumi=self.getFindedStr(chara_yumi_list)

                if '（'in chara_name_text:
                    chara_name_pattern=re.compile(r'^(.*)（',re.S)
                    chara_name_list=re.findall(chara_name_pattern,chara_name_text)
                    chara_name=self.getFindedStr(chara_name_list)
                elif 'CV'in chara_name_text:
                    chara_name_pattern = re.compile(r'^(.*)CV', re.S)
                    chara_name_list = re.findall(chara_name_pattern, chara_name_text)
                    chara_name = self.getFindedStr(chara_name_list)
                else:
                    chara_name=chara_name_text

                chara_name.replace('\u3000','').strip()


                chara_desp = chara_text('dd').text()
                chara_img = chara_text.parent('tr').find('img').attr('src')
                chara = {'name': chara_name,
                         'yumi': chara_yumi,
                         'cv': chara_cv,
                         'name_text': chara_name_text,
                         'desp': chara_desp,
                         'img': chara_img,
                         }
                chara_list.append(chara)
        else:
            pass
        # print('chara_list:',chara_list)

        # 匹配封面
        cover_html_pattern=re.compile(r'<td.*?text-align:center;margin-left:5px;vertical-align:top;width:300px;.*?>(.*?)</td',re.S|re.IGNORECASE)
        cover_html_list=re.findall(cover_html_pattern,soft_table_html)
        cover_html=self.getFindedStr(cover_html_list)
        if cover_html:
            cover_url=pq(cover_html).find('img').attr('src')
        else:
            cover_url=''
        # print('cover_url:',cover_url)

        # 匹配样品图片列表
        sampleimg_list=[]
        sampleImg_html_pattern=re.compile(r'サンプル画像.*?<div.*?>(.*?)</div',re.S|re.IGNORECASE)
        sampleImg_html_list=re.findall(sampleImg_html_pattern,unescapedHtmlStr)
        sampleImg_html=self.getFindedStr(sampleImg_html_list)
        if sampleImg_html:
            sampleImgDoc=pq(sampleImg_html)
            for sampleimg in sampleImgDoc('img').items():
                sampleimg_list.append(sampleimg.attr('src'))
        else:
            pass
        # print('sampleimg_list:',sampleimg_list)

        # 匹配时长，getchu除了gal还有一些里番，这些视频具有时长属性
        duration_pattern=re.compile(r'時間：.*?<td.*?>(.*?)</td',re.S)
        duration_list=re.findall(duration_pattern,soft_table_html)
        duration=self.getFindedStr(duration_list)
        # print('duration:',duration)

        # 匹配收录内容，如果是cd会有这类信息
        content_list_html_pattern=re.compile(r'収録内容.*?<div.*?>(.*?)</div',re.S|re.IGNORECASE)
        content_list_html_list=re.findall(content_list_html_pattern,unescapedHtmlStr)
        content_list_html=self.getFindedStr(content_list_html_list)
        if content_list_html:
            content_list=pq(content_list_html).text()
        else:
            content_list=''
        # print('content_list:',content_list)

        # 匹配商品介绍，如果是cd，bd之类会有这个信息
        goods_introduction_html_pattern = re.compile(r'商品紹介</div>.*?<div.*?>(.*?)</div', re.S)
        goods_introduction_html_list = re.findall(goods_introduction_html_pattern, unescapedHtmlStr)
        goods_introduction_html = self.getFindedStr(goods_introduction_html_list)
        # # print(goods_introduction_html)
        if goods_introduction_html:
            # # print(goods_introduction_html)
            goods_introduction = pq(goods_introduction_html).text()
        else:
            goods_introduction = ''
        # print('goods_introduction:', goods_introduction)

        # 匹配工作人员信息
        staff_cast_html_pattern = re.compile(r'キャスト</div>.*?<div.*?>(.*?)</div',re.S)
        staff_cast_html_list = re.findall(staff_cast_html_pattern, unescapedHtmlStr)
        staff_cast_html = self.getFindedStr(staff_cast_html_list)
        # # print(staff_cast_html)
        if staff_cast_html:
            # print(staff_cast_html)
            staff_cast = pq(staff_cast_html).text()
        else:
            staff_cast = ''
        # print('staff_cast:', staff_cast)

        # 匹配国际标准书号，如果是书籍或者杂志会有这个属性
        ISBN13_pattern = re.compile(r'ISBN-13：.*?<td.*?>(.*?)</td', re.S)
        ISBN13_list = re.findall(ISBN13_pattern, soft_table_html)
        ISBN13 = self.getFindedStr(ISBN13_list)
        # print('ISBN13:', ISBN13)

        # 匹配 '原画／作家' 列表一些挂画会有这个属性
        painter_writer_html_pattern=re.compile(r'原画／作家：.*?<td.*?/td',re.S)
        painter_writer_html_list= re.findall(painter_writer_html_pattern,soft_table_html)
        painter_writer_list_html=self.getFindedStr(painter_writer_html_list)
        if painter_writer_list_html:
            painter_writer_list_pattern=re.compile(r'<a.*?>(.*?)</a',re.S)
            painter_writer_list=re.findall(painter_writer_list_pattern,painter_writer_list_html)
        else:
            painter_writer_list=[]

        # print('painter_writer_list:',painter_writer_list)

        # # 备份一下，免得有没匹配的信息,以后可以再筛选一下
        # table_backup=soft_table.text()
        # # print('table_backup:',table_backup)
        # # print()
        # 不备份了，会多占用很多空间

        return {
            'getchu_id':getchu_id,
            'title':title,
            'brand':brand,
            'brandsite':brandsite,
            'price':price,
            'midea':midea,
            'on_sale':on_sale,
            'genre':genre,
            'jan_code':jan_code,
            'painter_list':painter_list,
            'scenario_list':scenario_list,
            'specials':specials,
            'bikou':bikou,
            'system_requirements':system_requirements,
            'series_number':series_number,
            'category_list':category_list,
            'subgenre_list':subgenre_list,
            'introduction':introduction,
            'story':story,
            'chara_list':chara_list,
            'cover_url':cover_url,
            'sampleimg_list':sampleimg_list,
            'duration':duration,
            'goods_introduction':goods_introduction,
            'content_list':content_list,
            'staff_cast':staff_cast,
            'ISBN13':ISBN13,
            'painter_writer_list':painter_writer_list
        }

    def getHtmlFromPath(self):
        with open(self.file_path,'r',encoding='utf8')as f:
            htmlStr = f.read()
        f.close()
        return htmlStr

    def parse_one_path_page(self):
        filePath=self.file_path
        with open(filePath, 'r', encoding='utf8') as f:
            htmlStr = f.read()
            f.close()
        return self.parse_one_page(htmlStr)

    def get_save(self):
        htmlStr = self.get_one_page()
        self.save_page(htmlStr)

    def done(self):
        htmlStr=self.get_one_page()
        if htmlStr:
            self.save_page(htmlStr)
            product_info = self.parse_one_page(htmlStr)
            # insert_result = self.collection.insert_one(product_info)
            insert_result = self.collection.update_one({'getchu_id':int(self.getchu_id)},{'$set':product_info},upsert=True)

            print('insert complete:', insert_result.raw_result)
        else:
            print('not a correct page',self.getchu_url)
    def test(self):
        htmlStr=self.get_one_page()
        print(self.getchu_url)


def main(startNum,endNum):
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['getchu']
    collection = db['product']
    collection.save()
    for url_id in range(startNum,endNum):
        getchu_url=r'http://www.getchu.com/soft.phtml?id=' + str(url_id) + '&gc=gc'
        getchu=GetchuSpider(getchu_url,collection=collection)
        # getchu.get_save()
        try:
            getchu.done()
            # getchu.test()
        except Exception as e:
            print('done error',getchu.getchu_url,getchu.file_path,e)
            time.sleep(300)
    print('done')

def done(getchu_url):
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['getchu']
    collection = db['product']
    getchu = GetchuSpider(getchu_url, collection=collection)
    # getchu.get_save()
    try:
        getchu.done()
        # getchu.test()
    except Exception as e:
        print('done error', getchu.getchu_url, getchu.file_path,e)


def main2(startNum,endNum):
    getchu_url_list=[]
    for url_id in range(startNum,endNum):
        getchu_url=r'http://www.getchu.com/soft.phtml?id=' + str(url_id) + '&gc=gc'
        getchu_url_list.append(getchu_url)

    # for tmp_url in getchu_url_list:
    #     done(tmp_url)
    pool=Pool()
    pool.map(done,getchu_url_list)
    print('done')


if __name__ == '__main__':
    if len(sys.argv)==3:
        startNum = int(sys.argv[1])
        endNum = int(sys.argv[2])
    elif len(sys.argv)==2:
        startNum = int(sys.argv[1])
        endNum = startNum + 1
    else:
        print('请输入开始位置和结束位置，用空格隔开')
        sys.exit()
    main2(startNum,endNum)