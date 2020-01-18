import pymongo
import requests
import html
import re

def get_page(url):
    '''
    获取一个指定url的页面并返回
    :param url:
    :return:
    '''
    try:
        res = requests.get(url)
    except Exception as e:
        print(e,'请求url出错，重试',url)
        get_page(url)
        return
    if(res.status_code==200):
        htmlStr = res.text
        print('200', url)
        # save_page(htmlStr,url)
        return htmlStr
    else:
        print(res.status_code, url)
        return ''
def getFindedStr(findedList):
    if len(findedList)==0:
        return ''
    else:
        return findedList[0]
def parse_a_page(htmlStr,rjid):
    # 先转换html的字符实体
    htmlStr = html.unescape(htmlStr)
    rjid=rjid
    print('rjid:',rjid)
    # 匹配标题
    title_pattern = re.compile('id="work_name">.*?<a.*?>(.*?)</a', re.S)
    title_list = re.findall(title_pattern, htmlStr)
    # 为了把标题中【】和其中中包含的内容替换成空，因为里面的内容大多是广告折扣之类
    # cleanTitle = re.sub('\u3010.*?\u3011','',rawTitle)

    # 上面的方案不是一个好方案，因为有些标题就是含有【】，和折扣这些无关也会被清除掉
    cleanTitle = getFindedStr(title_list)
    return cleanTitle


client=pymongo.MongoClient(host='localhost',port=27017)
db=client['dlsite']
collection=db['product']
res =collection.find({'title':None})
for info in res:
    try:
        rjid=info['RJID']
        rj_url= r'https://www.dlsite.com/maniax/work/=/product_id/'+rjid+'.html'
        htmlStr=get_page(rj_url)
        if not htmlStr:
            break
        title=parse_a_page(htmlStr,rjid)
        print(rj_url,title)
        print(info)
    except Exception as e:
        print(e)
        break
    condition = {"RJID": rjid}
    info['title']=title
    res = collection.update_one(condition,{"$set":info})
    print(res.raw_result,rjid)
    print()

