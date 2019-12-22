#!/usr/bin/env python3
'''
@作者:  风沐白
@文件:  SpCoolApk.py
@描述:  爬取酷安网的apk文件
@代理:  git@github.com:jhao104/proxy_pool.git
'''

import csv
import os
import random
import re
import time
import threading

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

import libProxy

page_num=302        #页数
home_dir=r'D:\Apks\App' #主存储目录

website='https://coolapk.com'
url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

user_agent_list=['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4000.3 Safari/537.36',
                'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',
                'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931',
                'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.9200',
                'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
                'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16']



def ApkListPage():
    '''应用首页'''
    # 使用代理
    proxy = libProxy.GetProxy()
    for i in range(38,page_num):
        print('Starting page %d' % i)
        CatLog('Starting page {}'.format(i))
        ua={'user-agent':user_agent_list[random.randint(0,10)]}
        # 请求APP列表
        try:
            if proxy:
                page=requests.get(website+'/apk?p='+str(i),headers=ua,proxies={'http':proxy})
            else:
                page=requests.get(website+'/apk?p='+str(i),headers=ua)

        except BaseException as e:
            print(e)
            CatLog(e.__str__)
            continue
        # 查找列表元素
        soup=BeautifulSoup(page.text,'lxml')
        item=soup.find_all('div',attrs={'class':'app_left_list'})[0]
        try:
            hrefs=item.find_all('a')[0:10] # 除最后一页, 每页10个
        except BaseException as e:
            print(e)
            CatLog(e.__str__)
            continue
        # 处理每个APP条目
        randsleep()
        for href in hrefs:
            if 'href' in href.attrs:
                ApkPage(href.attrs['href'])


def ApkPage(path:str):
    '''处理APP页面'''
    proxy = libProxy.GetProxy()
    url=website+path
    packageName=path.split('/')[-1]
    ua={'User-Agent':user_agent_list[random.randint(0,10)]}
    # 创建会话
    ss=requests.session()
    # 解析APP页面
    try:
        if proxy:
            page=ss.get(url,headers=ua,proxies={'http':proxy})
        else:
            page=ss.get(url,headers=ua)

        # 获取APP信息
        soup=BeautifulSoup(page.text,'lxml')
        mss=soup.find_all('div',attrs={'class':'apk_topbar_mss'})[0]
        # 获取下载直连
        jsFun=soup.find_all('script',attrs={'type':'text/javascript'})[0]
        dl=re.findall(url_pattern,jsFun.text)
        randsleep()
        rep=ss.get(dl[0],allow_redirects=False)
        dl_url=rep.headers['Location']
    except BaseException as e:
        print(e)
        CatLog(e.__str__)
        return
    Download(packageName,dl_url,mss)

def Download(packageName:str,url:str,mss:Tag):
    '''处理下载事件'''
    # 按域名划分目录
    ua={'User-Agent':user_agent_list[random.randint(0,7)]}
    s=packageName.split('.')
    d = home_dir + '\\' + (packageName if len(s)<3 else s[0]+'.'+s[1])
    if not os.path.exists(d):
        #print('mkdir %s with domain' % d)
        CatLog('mkdir '+d+' with domain')
        os.mkdir(d)
    # 分块下载
    try:
        randsleep()
        dltmp=requests.get(url,headers=ua,stream=True)
    except BaseException as e:
        print(e)
        CatLog(e.__str__)
        return
    print('Downloading %s.apk ...' % packageName)
    Statics(packageName,mss)
    t=threading.Thread(target=Write,args=(packageName,d,dltmp))
    t.start()
    return

def Write(packageName,d,dltmp:requests.Response):
    '''写入apk文件'''
    file=d+'\\'+packageName+'.apk'
    if os.path.exists(file):
        print('Apk %s has existed, skip' % packageName)
        CatLog('Apk '+packageName+' has existed, skip')
        return
    try:
        with open(file,'wb') as f:
            for chunk in dltmp.iter_content(0x4096):
                if chunk:
                    f.write(chunk)
    except BaseException as e:
        print(e)
        CatLog(e.__str__)


def CatLog(s:str):
    '''日志记录'''
    t=time.localtime()
    ltime='{}年{}月{}日{}时{}分{}秒 >>> '.format(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min,t.tm_sec)
    with open(home_dir+'\\log.txt','a') as f:
        try:
            f.write(ltime+s+'\n')
        except BaseException:
            f.close()

def Statics(packageName:str,mss:Tag):
    '''统计APP信息'''
    ps=mss.findAll('p')
    appName=ps[0].contents[0]                    #应用名
    column=ps[1].contents[0].split('/')
    res = re.findall(r'[\d\w.]+',column[0])
    apkSize='0' if not res else res[0]           #应用大小
    num=column[1].replace('下载','').strip()     #下载数
    staticFile=home_dir+'\\statics.csv'
    with open(staticFile,'a',newline='',encoding='utf-8') as f:
        writer=csv.writer(f)
        writer.writerow([appName,packageName,num,apkSize])
    return

def run():
    if not os.path.exists(home_dir):
        os.mkdir(home_dir)
    ApkListPage()

def randsleep():
    time.sleep(random.random()*10)


if __name__ == "__main__":
    print('Start')
    run()
    print('End')