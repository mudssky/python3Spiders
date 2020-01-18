import requests
import os
import sys
def get_one_page(page_url):
    try:
        resText = requests.get(page_url).text
    except Exception as e:
        print('get url error',page_url,e)
        print('retry...')
        return get_one_page(page_url)
    cleanHtml=resText.encode('utf8')
    return resText
def save_page(htmlStr,page_url):
    if not os.path.exists('html'):
        os.mkdir('html')
    filename=page_url.split('=')[1][:-3]+'.html'
    print(filename)
    path=os.path.join('html',filename)
    with open(path,'w',encoding='utf8')as f:
        f.write(htmlStr)
    f.close()
    print('save completed',filename)
def main(url_id):
    page_url=r'http://www.getchu.com/soft.phtml?id='+url_id +'&gc=gc'
    htmlStr = get_one_page(page_url)
    save_page(htmlStr,page_url)

if __name__ == '__main__':
    url_id=sys.argv[1]
    main(url_id)