import jdCookie
import json
import requests
import time
import random
import re
import os,sys

headers = {
    'Host': 'lzkj-isv.isvjd.com',
    'Accept': '*/*',
    'Connection': 'close',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://lzkj-isv.isvjd.com/',
    'Accept-Encoding': 'gzip, deflate, br',
}

headers_api = {
    'Host': 'api.m.jd.com',
    'Accept': '*/*',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://lzkj-isv.isvjd.com/',
    'Accept-Encoding': 'gzip, deflate, br',
}

for cookies in jdCookie.get_cookies():
    print("##"*30)
    print("【开始获取活动信息】\n")
    today = jdCookie.get_time_now().strftime("%Y%m%d")
    errMsg = ""
    url = os.environ["JD_SIGN_GETTOKEN_URL"]
    params = {
        }
    data = os.environ["JD_SIGN_GETTOKEN_BODY"]
    tokenInfo = requests.post(url, headers=headers_api, data=data, params=params, cookies=cookies)
    token = tokenInfo.json()["token"]
    time.sleep(1)

    session = requests.session()
    url = os.environ["JD_SIGN_URL"]
    params = {        
    }
    session.get(url, headers=headers, params=params, cookies=cookies)
    time.sleep(1)

    data = {
        'userId': 599119,
        'token': token,
        'fromType': 'APP'
    }
    secretPinInfo = session.post('https://lzkj-isv.isvjd.com/customer/getMyPing', headers=headers, data=data, params=params)
    secretPin = secretPinInfo.json()["data"]["secretPin"]

    url = 'https://lzkj-isv.isvjcloud.com/wxAssemblePage/getTopAndNewActInfo'
    data = {
        'pin': secretPin,
        'aggrateActType': 3,
        'topNewType': 2,
        'pageNo': 1,
        'pageSize': 100
    }
    getTopAndNewActInfo = session.post(url, headers=headers, data=data, params=params)
    TopAndNewAct = getTopAndNewActInfo.json()["data"]["homeInfoResultVOList"]
    
    data = {
        'pin': secretPin,
        'aggrateActType': 3,
        'topNewType': 1,
        'pageNo': 1,
        'pageSize': 100
    }
    getTopAndNewActInfo = session.post(url, headers=headers, data=data, params=params)
    for newAct in getTopAndNewActInfo.json()["data"]["homeInfoResultVOList"]:
        TopAndNewAct.append(newAct)

    print("##"*30)
    print("【开始抽奖】\n")
    for lotteryActInfo in TopAndNewAct:
        skipStar = False
        data = {
            'pin': secretPin,
            'activityId': lotteryActInfo["activityId"]
        }
        response = session.post("https://lzkj-isv.isvjd.com/wxDrawActivity/activityContent", headers=headers, data=data, params=params)
        if response.text == '':
            errMsg = " 无效活动！"
            skipStar = True
        if skipStar == True:
            print(lotteryActInfo["shopName"], errMsg)
            time.sleep(random.randint(2, 3))
            continue
        if response.json()["result"] == True and response.json()["data"]["canDrawTimes"] > 0:
            for i in range(response.json()["data"]["canDrawTimes"]):
                response = session.post("https://lzkj-isv.isvjd.com/wxDrawActivity/start", headers=headers, data=data, params=params)
                if response.json()["data"]["drawOk"] == True:
                    errMsg = " 获得 " + response.json()["data"]["name"]
                else:
                    errMsg = " 未中奖！"
                print(lotteryActInfo["shopName"], errMsg)
                time.sleep(random.randint(3, 6))
        else:
            print(lotteryActInfo["shopName"], " 无抽奖次数！")
            time.sleep(random.randint(2, 5))
    print("\n")
    print("##"*30)
