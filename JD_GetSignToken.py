import re
import json
import requests
import time
import random
import os

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'zh-CN,zh;q=0.9', 
    'Accept-Encoding': 'gzip, deflate, br',
}

def getCurrentTime():
    return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))

def requestsGet(url):
    params = {
    }    
    response = requests.get(url, headers=headers)
    return response

def main():
    tokenList =[]
    tokenListSort = []
    urlList = []
    try:
        getJdUrl = requestsGet(os.environ["JD_SIGN_7D_URL"])
        pattern = re.compile(os.environ["JD_SIGN_7D_C1"])
        urlList = re.findall(pattern, getJdUrl.text)
        if len(urlList) > 0:
            for urlTmp in urlList:
                getUJDUrl = requestsGet(urlTmp)
                getTempTxt = requestsGet(getUJDUrl.url)
                pattern = re.compile(r'(?<=var hrl=\').+?(?=\')')                
                getTokenUrl = pattern.search(getTempTxt.text)
                if getTokenUrl is None:
                    continue
                getTokenTxt= requestsGet(getTokenUrl.group(0)).url
                tokenTxt = re.search(r'(?<=token=).+?(?=&)',getTokenTxt)
                if tokenTxt is None:
                    print(urlTmp)
                    print("无数据！") 
                    continue
                else:
                    # print(tokenTxt.group(0))
                    tokenList.append(tokenTxt.group(0))                    
                    time.sleep(2)
        print("Token 数量：" + str(len(tokenList)))
        tokenListSort = list(set(tokenList))
        tokenListSort.sort(key=tokenList.index)
        print("Token 去重后数量：" + str(len(tokenListSort)))
        # print(tokenListSort)
    except Exception as e:  
        print (getCurrentTime(),'main', e )
    if len(tokenListSort) < 1:
        tokenListSort = ['35ADF3ABFAAA8E91AF97336AA0A46929']
    return tokenListSort
