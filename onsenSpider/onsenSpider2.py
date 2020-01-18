# -*- coding: utf-8 -*-
import requests
import chardet
# 音泉所有节目信息的xml接口，直接获得所有节目信息 http://www.onsen.ag/app/programs.xml

response = requests.get(r'http://www.onsen.ag/app/programs.xml')
print(response.headers)
print(response.encoding)
print(chardet.detect(response.content))
with open ('programs.xml','w',encoding='utf8') as f:
    f.write(response.content.decode('utf8'))
    f.close()


