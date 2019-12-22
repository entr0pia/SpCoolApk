#!/usr/bin/env python3

import requests
import random
from bs4 import BeautifulSoup

def GetProxy():
    '''获取代理'''
    r=requests.get('https://www.freeip.top/?page=1&protocol=http&country=%E4%B8%AD%E5%9B%BD')
    soup=BeautifulSoup(r.text,'lxml')
    trs=soup.find_all('tr')
    try:
        tr=trs[random.randint(1,10)]
    except BaseException:
        l =len(trs)
        if l < 1:
            return None
        else:
            tr=trs[l]
    tds=tr.find_all('td')
    proxy=tds[3].text.lower()+'://'+tds[0].text+':'+tds[1].text
    return proxy

if __name__ == "__main__":
    print(GetProxy())