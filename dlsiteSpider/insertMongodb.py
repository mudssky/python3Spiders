import  re
import os
from pyquery import PyQuery as pq
import html
import  pymongo
import logging
import sys
import datetime
def getFindedStr(findedList):
    if len(findedList)==0:
        return ''
    else:
        return findedList[0]

def parse_a_page(htmlStr,path):
    # 先转换html的字符实体
    htmlStr = html.unescape(htmlStr)
    rjid=path[5:-5]
    print('rjid:',rjid)
    # 匹配标题
    title_pattern = re.compile('id="work_name">.*?<a.*?>(.*?)</a', re.S)
    rawTitle = re.findall(title_pattern, htmlStr)[0]
    # 为了把标题中【】和其中中包含的内容替换成空，因为里面的内容大多是广告折扣之类
    cleanTitle = re.sub('\u3010.*\u3011','',rawTitle)
    # print('title:',cleanTitle)

    # 匹配右侧信息列表
    work_right_inner_pattern= re.compile('id="work_right_inner">(.*?)</ul',re.S)
    work_right_inner_list=re.findall(work_right_inner_pattern, htmlStr)
    work_right_inner=getFindedStr(work_right_inner_list)
    # 接下来把右侧信息列表逐项匹配

    # 匹配社团名
    circle_pattern=re.compile(r'サークル名.*?<a.*?>(.*?)</a',re.S)
    circle_list = re.findall(circle_pattern,work_right_inner)
    circle=getFindedStr(circle_list)
    # print('circle:',circle)

    # 匹配贩売日
    on_sale_pattern = re.compile(r'販売日.*?<a.*?>(.*?)<', re.S)
    # print(work_right_inner)
    on_sale_list = re.findall(on_sale_pattern, work_right_inner)
    on_sale = getFindedStr(on_sale_list)
    # print('on_sale:',on_sale)

    # 匹配系列名
    series_name_pattern=re.compile(r'シリーズ名.*?<a.*?>(.*?)<', re.S)
    series_name_list=re.findall(series_name_pattern,work_right_inner)
    series_name=getFindedStr(series_name_list)
    # print('series_name:',series_name)

    # 匹配作家
    writer_pattern=re.compile(r'作家.*?<a.*?>(.*?)<', re.S)
    writer_list=re.findall(writer_pattern,work_right_inner)
    writer=getFindedStr(writer_list)
    # print('writer:',writer)

    # 匹配shinario脚本
    scenario_pattern=re.compile(r'シナリオ.*?<a.*?>(.*?)<', re.S)
    scenario_list=re.findall(scenario_pattern,work_right_inner)
    scenario=getFindedStr(scenario_list)
    # print('scenario:',scenario)

    # 匹配插画illustration
    illustration_pattern = re.compile(r'イラスト.*?<a.*?>(.*?)<', re.S)
    illustration_list=re.findall(illustration_pattern,work_right_inner)
    illustration=getFindedStr(illustration_list)
    # print('illustrationl:',illustration)

    # 匹配声优列表cv
    # cv_pattern=re.compile(r'声優.*?<a.*?>(.*?)<', re.S)
    # cv_list=re.findall(cv_pattern,work_right_inner)
    # cv=getFindedStr(cv_list)
    cvs_pattern = re.compile(r'声優.*?td>(.*?)</td', re.S)
    cvs_list=re.findall(cvs_pattern,work_right_inner)
    # print('cvs_list',cvs_list)
    cvHtmlStr=getFindedStr(cvs_list)
    # print('cvhtmlstr',cvHtmlStr)
    if cvHtmlStr:
        cv_list_pattern=re.compile('<a.*?>(.*?)</a',re.S)
        cv_list=re.findall(cv_list_pattern,cvHtmlStr)
    else:
        cv_list=[]
    # print('cv_list:',cv_list)

    # 匹配 年龄指定
    age_judge_pattern=re.compile(r'年齢指定.*?<span.*?>(.*?)</span',re.S)
    age_judge_list=re.findall(age_judge_pattern,work_right_inner)
    age_judge=getFindedStr(age_judge_list)
    # print('age_judge:',age_judge)

    # 匹配 作品形式
    category_pattern=re.compile(r'作品形式.*?<span.*?>(.*?)</span',re.S)
    category_list=re.findall(category_pattern,work_right_inner)
    category=getFindedStr(category_list)
    # print('category:',category)

    # 匹配文件形式
    file_type_pattern=re.compile(r'ファイル形式.*?<span.*?>(.*?)</span',re.S)
    file_type_list=re.findall(file_type_pattern,work_right_inner)
    file_type=getFindedStr(file_type_list)
    # print('file_type:',file_type)

    # 匹配备注列表
    other_tips_str_pattern=re.compile(r'その他.*?td>(.*?)</td',re.S)
    other_tips_str_list=re.findall(other_tips_str_pattern,work_right_inner)
    other_tips_str=getFindedStr(other_tips_str_list)
    if other_tips_str:
        other_tips_list_pattern=re.compile('<span.*?>(.*?)</span',re.S)
        other_tips_list=re.findall(other_tips_list_pattern,other_tips_str)
    else:
        other_tips_list=[]
    # print('other_tips_list:',other_tips_list)

    # 匹配作品分类列表genre
    genre_str_pattern=re.compile(r'ジャンル.*?<div.*?>(.*?)</div',re.S)
    genre_str_list=re.findall(genre_str_pattern,work_right_inner)
    genre_str=getFindedStr(genre_str_list)
    if genre_str:
        genre_list_pattern=re.compile(r'<a.*?>(.*?)</a',re.S)
        genre_list=re.findall(genre_list_pattern,genre_str)
    else:
        genre_list=[]
    # print('genre_list:',genre_list)

    # 匹配文件大小
    file_capcity_pattern=re.compile(r'ファイル容量.*?div.*?>(.*?)</div',re.S)
    file_capcity_list=re.findall(file_capcity_pattern,work_right_inner)
    # print(file_capcity_list)
    file_capcity=getFindedStr(file_capcity_list)
    # print('file_capcity:',file_capcity)

    # 匹配运行环境
    system_requirements_pattern=re.compile(r'動作環境.*?div.*?>(.*?)</div',re.S)
    system_requirements_list=re.findall(system_requirements_pattern,work_right_inner)
    system_requirements=getFindedStr(system_requirements_list)
    # print('system_requirements:',system_requirements)

    # 匹配event信息
    event_pattern=re.compile(r'イベント.*?span.*?title="(.*?)">',re.S)
    event_list=re.findall(event_pattern,work_right_inner)
    event=getFindedStr(event_list)
    # print('event:',event)


    # 匹配作品详细说明，用pyquery
    doc = pq(htmlStr)
    desp = doc('.work_article.work_story').text()
    # print('desp:',desp)

    # 匹配作品所有图片地址
    # 因为图片地址不是后端渲染，而是vue渲染的，所以从下载的html文档中只能截取一个图片地址
    try:
        ul=doc('.slider_items.trans')
        imgUrlList=ul('img').attr('src')
    except Exception as e:
        imgUrlList=''
    # print('imgUrlList:',imgUrlList)
    # print('')
    return {
        'RJID':rjid,
        'title':cleanTitle,
        'circle':circle,
        'on_sale':on_sale,
        'series_name':series_name,
        'writer':writer,
        'scenario':scenario,
        'illustration':illustration,
        'cv_list':cv_list,
        'age_judge':age_judge,
        'file_type':file_type,
        'other_tips':other_tips_list,
        'genre':genre_list,
        'file_capcity':file_capcity,
        'system_requirements':system_requirements,
        'event':event,
        'desp':desp,
        'img_list':imgUrlList
    }







def main():
    # 记录日志
    logger = logging.getLogger('dlsiteSpiderLogger')
    logger.setLevel(logging.ERROR)
    screenError_handler=logging.StreamHandler(sys.stderr)
    screenError_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(message)s"))

    fileError_handler=logging.FileHandler('error.log')
    fileError_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))
    logger.addHandler(screenError_handler)
    logger.addHandler(fileError_handler)
    client=pymongo.MongoClient(host='localhost',port=27017)
    db=client['dlsite']
    collection=db['product']
    htmlPathList = []
    for filename in os.listdir('html'):
        htmlPathList.append(os.path.join('html',filename))
        print(filename)
    for path in htmlPathList:
        # print(path)
        try:
            with open(path, 'r', encoding='utf8') as f:
                htmlStr = f.read()
                product_info=parse_a_page(htmlStr, path)
                result=collection.insert_one(product_info)
                print(result.inserted_id)
        except Exception as e:
            print(e)
            # print("读取文件出错",path,"将继续读取下一个文件")
            logger.error("读取文件出错",path,"将继续读取下一个文件")
            continue
        finally:
            f.close()


if __name__=="__main__":
    main()