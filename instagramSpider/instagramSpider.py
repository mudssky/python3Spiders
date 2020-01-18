from pyquery import PyQuery as pq
import requests



def download_profile_page(url):
    profileHtml=requests.get(url).text
    print(profileHtml)





if __name__=='__main__':
    profile_url=r'https://www.instagram.com/minori_cat/'
    download_profile_page(profile_url)
