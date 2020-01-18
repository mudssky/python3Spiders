import  pymongo






client=pymongo.MongoClient(host='localhost',port=27017)
db=client['dlsite']
collection=db['product']
with open('allrjid.txt','r',encoding='utf8')as f:
    content=f.read().strip()
    f.close()
rjidList=content.split('\n')
noneList=[]
for rjid in rjidList:
    condition={"RJID":rjid}
    info=collection.find_one(condition)
    if info:
        info['have']=True
        result=collection.update(condition,info)
        print(result)
    else:
        print('none',rjid)
        noneList.append(rjid)

print(len(noneList))
print(noneList)
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
