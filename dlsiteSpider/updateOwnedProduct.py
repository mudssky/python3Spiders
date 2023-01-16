import pymongo
import dlsiteSpider3
import os
import re
import fire
# 递归获取当前目录下所有RJID并且去重
def getRjidList(path):
    '''
    os.walk(top, topdown=True, onerror=None, followlinks=False)
参数：
top 是你所要遍历的目录的地址
topdown 为真，则优先遍历top目录，否则优先遍历top的子目录 (默认为True)
onerror 需要一个 callable 对象，当walk需要异常时，会调用
followlinks 如果为真，则会遍历目录下的快捷方式
(linux 下是 symbolic link)实际所指的目录 (默认为False)
os.walk 的返回值是一个生成器(generator),也就是说我们需要不断的遍历它，来获得所有的内容。

每次遍历的对象都是返回的是一个三元组(root,dirs,files)

root 所指的是当前正在遍历的这个文件夹的本身的地址
dirs 是一个 list ，内容是该文件夹中所有的目录的名字(不包括子目录)
files 同样是 list , 内容是该文件夹中所有的文件(不包括子目录)
    '''
    rjidList=set()
    filename_list=[]
    for dirpath,dirnames,filenames in os.walk(path):
        # 他的原理是每次遍历一个目录，列出子目录和文件，然后子目录加入遍历的队列中，
        # 因此，我们匹配文件名只要每次root和 files中的文件名匹配以下就可以了。
        dirname = os.path.basename(dirpath)
        filename_list.append(dirname)
        filename_list.extend(filenames)
        # if re.findall(r'([Rr][Jj]\d{6})',dirname)
        # root.
    for filename in filename_list:
        upper_filename = filename.upper()
        # print(upper_filename)
        result=re.match('(RJ\d{6,8})',upper_filename)
        if result:
            rjidList.add(result.group())
    return sorted(rjidList)
    # print(rjidList)
        # for 
    # pass
    


def main(path):
    # fire.Fire()
    client=pymongo.MongoClient(host='localhost',port=27017)
    db=client['dlsite']
    collection=db['product']
    rjidList=getRjidList(path)
    print('需要更新的rjidList列表为：{0}'.format(rjidList))
    if rjidList:
        # 获取到rjid的列表之后，先查询数据库中最大的rjid，更新到现在添加的音声中最大值
        filter={}
        sort=list({
            'RJID': -1
        }.items())
        # limit=1
        newest_rjid=collection.find_one(filter=filter,sort=sort)['RJID']
        # newest_rjid=collection.find(filter=filter,sort=sort,limit=3)
        # print(newest_rjid)
        if newest_rjid<rjidList[-1]:
            startNum=int(newest_rjid[2:])+1
            endNum=int(rjidList[-1][2:])+1
            print('更新范围是RJ{0}～～RJ{1}'.format(startNum,endNum))
            dlsiteSpider3.main(startNum,endNum)
        
        # 更新数据库完毕后，修改新增产品的have属性
        for rjid in rjidList:
            # 首先查询rjid是否在数据库中
            condition={'RJID':rjid}
            result=collection.find_one(condition)
            if result:
                print('在数据库中查找到{0},直接进行更新'.format(rjid))
                result['have']=True
                # collection.update_one(condition,{'have':True})
                collection.replace_one(condition,result)
                print('update completed:{0}'.format(result)) 
            else:
                print('在数据库中没有找到{0},尝试从dlsite爬取并更新'.format(rjid))
                dlsiteSpider3.main(int(rjid[2:]),int(rjid[2:])+1) 
                result=collection.find_one(condition)
                if result:
                    print('爬取成功:{0}，更新数据'.format(result))
                    # result['have']=True
                    # collection.
                    result['have']=True
                    # collection.save(result)
                    collection.replace_one(condition,result)


        # rjidList[-1]













if __name__=="__main__":
    fire.Fire()


# with open('rjidList.txt','r',encoding='utf8')as f:
#     content=f.read().strip()
#     f.close()
# rjidList=content.split('\n')
# noneList=[]
# for rjid in rjidList:
#     condition={"RJID":rjid}
#     info=collection.find_one(condition)
#     if info:
#         info['have']=True
#         result=collection.update(condition,info)
#         print(result)
#     else:
#         print('none',rjid)
#         noneList.append(rjid)

# print(len(noneList))
# print(noneList)
# if len(noneList)>0:
#     for rjid in noneList:
#         try:
#             url=r'https://www.dlsite.com/maniax/work/=/product_id/'+rjid+'.html'
#             dlsiteSpider3.main2(url)
#         except Exception as e:
#             print('error',url,e)

#         print('add url:',url)
#
# for item in noneList:
#     propert_info = {
#         'RJID': item,
#         'title': '',
#         'circle': '',
#         'on_sale': '',
#         'series_name': '',
#         'writer': '',
#         'scenario': '',
#         'illustration': '',
#         'cv_list': [],
#         'age_judge': '',
#         'file_type': '',
#         'other_tips': [],
#         'genre': [],
#         'file_capcity': '',
#         'system_requirements': '',
#         'event': '',
#         'desp': '',
#         'img_list': [],
#         'have': True
#     }
#     result = collection.insert_one(propert_info)
#     print(rjid,result.inserted_id)
#
