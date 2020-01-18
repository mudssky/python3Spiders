# python3Spiders

## 1 qmkgSpider

通过全民k歌的个人页，下载全民k歌个人的所有歌曲

具体使用看程序注释



## 2 onsenSpider

下载onsen.ag的指定节目

具体使用看程序注释

* 1.0：增加下载进度显示，增加下载失败后的处理方案，失败后会把失败信息记录到json，再重新执行该程序，即可重新下载


## 3 dlsiteSpider
Get-rjids.ps1是一个powershell脚本，收集当前目录中的RJ编号，对目录递归查询，并且分行存到一个文件中，启动dlsiteSpider下载。
dlsiteSpider可以从页面中获取音声资源的相关信息，制作你的音声资源的目录，信息索引。

使用pyinstaller生成了exe文件，多进程模块调用会有问题，multi_process_support.py这个依赖解决多进程调用的问题。

程序使用说明看readme文件夹



dlsiteSpider2爬取整个站点，十几万个产品页面

dlsiteSpider3，爬取页面的同时，解析页面并入库

updateOwnedProduct作用是在数据库中把自己拥有的产品进行更新

## 4.eroCvRankSpider

爬取一个声优数据库，并且数据用sqlite存储

用flask框架，写了简单的查询api



## 5.getchuSpider

爬取getchu的产品信息页并入库



## 6.zxcsSpider

下载某小说网站的所有小说，提取所有下载链接存入mongodb，生成使用aria2c下载的powershell脚本