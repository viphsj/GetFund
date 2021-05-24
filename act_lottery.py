import jdCookie
import json
import requests
import time
import random
import re
import os,sys
import jdSendNotify

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
    giftMsg = ""
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
    """
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
    """
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
        if response.text.find('"result":true,"') > -1:
            if response.json()["data"]["canDrawTimes"] > 0:
                canDrawTimes = response.json()["data"]["canDrawTimes"]
                for i in range(canDrawTimes):
                    getGift = session.post("https://lzkj-isv.isvjd.com/wxDrawActivity/start", headers=headers, data=data, params=params)
                    if getGift.text.find('"drawOk":true,"') > -1:
                        errMsg = " 获得：" + str(getGift.json()["data"]["name"])
                        giftMsg += lotteryActInfo["shopName"] + " " + errMsg + "\n"
                    elif getGift.text.find('errorMessage') > -1:
                        errMsg = getGift.json()["errorMessage"]
                    else:
                        errMsg = getGift.text
                    # print(lotteryActInfo["shopName"], errMsg, "\n")
                    time.sleep(random.randint(3, 6))
            else:
                print(lotteryActInfo["shopName"], " 无抽奖次数！\n")
                time.sleep(random.randint(2, 5))
        else:
            print(lotteryActInfo["shopName"], " 无效活动！\n")
            time.sleep(random.randint(2, 5))
    if giftMsg != "":
        jdSendNotify.sendNotify("小活动-抽奖2\n" + cookies["pt_pin"] + "\n", giftMsg)
    print("\n")
    print("##"*30)
