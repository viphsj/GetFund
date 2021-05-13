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
        'aggrateActType': 7,
        'topNewType': 2,
        'pageNo': 1,
        'pageSize': 100
    }
    getTopAndNewActInfo = session.post(url, headers=headers, data=data, params=params)
    TopAndNewAct = getTopAndNewActInfo.json()["data"]["homeInfoResultVOList"]
    """
    data = {
        'pin': secretPin,
        'aggrateActType': 7,
        'topNewType': 1,
        'pageNo': 1,
        'pageSize': 100
    }
    getTopAndNewActInfo = session.post(url, headers=headers, data=data, params=params)
    for newAct in getTopAndNewActInfo.json()["data"]["homeInfoResultVOList"]:
        TopAndNewAct.append(newAct)
    """
    print("##"*30)
    print("【开始加购】\n")
    for addCartActInfo in TopAndNewAct:
        skipAdd = False
        url = "https://lzkj-isv.isvjd.com/wxCollectionActivity/activity2/"+addCartActInfo["activityId"]+"?activityId="+addCartActInfo["activityId"]
        response = session.get(url, headers=headers, cookies=cookies)
        # print(response.text)
        if response.text.find("活动已经结束了") > -1:
            errMsg = " 活动已经结束1!"
            skipAdd = True
        data = {
            'pin': secretPin,
            'activityId': addCartActInfo["activityId"]
        }
        response = session.post("https://lzkj-isv.isvjd.com/wxCollectionActivity/activityContent", headers=headers, data=data, params=params)
        if response.text == '':
            errMsg = " 活动已经结束2!"
            skipAdd = True
        elif response.text.find('"result":false,') > -1:
            errMsg = response.json()["errorMessage"]
            skipAdd = True
        if skipAdd == True:
            print(f'{addCartActInfo["shopName"]} {errMsg}\n')
            time.sleep(random.randint(2, 3))
            continue
        activityType = response.json()["data"]["type"]
        cpvosList = response.json()["data"]["cpvos"]
        hasCollectionSize = response.json()["data"]["hasCollectionSize"]
        needCollectionSize = response.json()["data"]["needCollectionSize"]
        needAddCartSize = needCollectionSize - hasCollectionSize
        needFollow = response.json()["data"]["needFollow"]
        hasFollow = response.json()["data"]["hasFollow"]
        userId = response.json()["data"]["userId"]
        print(f'{addCartActInfo["shopName"]} 开始加购')
        if needAddCartSize > 0:
            if needFollow == True and hasFollow == False:
                data = {
                    'userId': userId,
                    'buyerNick': secretPin,
                    'activityId': addCartActInfo["activityId"],
                    'activityType': str(activityType)
                }
                followShop = session.post("https://lzkj-isv.isvjd.com/wxActionCommon/followShop", headers=headers, data=data, params=params)
                if followShop.json()["result"] == True:
                    print(f'关注店铺 成功')
                else:
                    print(f'关注店铺 失败  {followShop.json()["errorMessage"]}')
                time.sleep(random.randint(2, 3))
            for cpvosInfo in cpvosList:
                hasAddCartSize = 0
                if cpvosInfo["collection"] == False:
                    data = {
                        'productId': cpvosInfo["productId"],
                        'pin': secretPin,
                        'activityId': addCartActInfo["activityId"]
                    }
                    addCart = session.post("https://lzkj-isv.isvjd.com/wxCollectionActivity/addCart", headers=headers, data=data, params=params)
                    if addCart.json()["result"] == False:
                        continue
                    hasAddCartSize = addCart.json()["data"]["hasAddCartSize"]
                    time.sleep(random.randint(1, 3))
                    print(f'加购数量 {str(addCart.json()["data"]["hasAddCartSize"])}/{str(needCollectionSize)}')
                if hasAddCartSize == needCollectionSize:
                    print("加购完成，开始抽奖")
                    break
        else:
            print(f'已做过活动 跳过 \n')
            time.sleep(random.randint(3, 6))
            continue
        time.sleep(random.randint(1, 3))
        data = {
            'pin': secretPin,
            'activityId': addCartActInfo["activityId"]
        }
        getPrize = session.post("https://lzkj-isv.isvjd.com/wxCollectionActivity/getPrize", headers=headers, data=data, params=params)        
        if getPrize.text.find('"result":true,') > -1:
            print(f'获得：{getPrize.json()["data"]["name"]}\n')
            giftMsg = addCartActInfo["shopName"] + " 获得：" + getPrize.json()["data"]["name"] + "\n"
        elif getPrize.text.find('"result":false,') > -1:
            print(f'错误：{getPrize.json()["errorMessage"]}\n')
        else:
            print(f'错误：{getPrize.text}\n')
        time.sleep(random.randint(3, 6))
    if giftMsg != "":
        jdSendNotify.sendNotify("小活动-加购有礼\n" + cookies["pt_pin"] + "\n", giftMsg)
    print("\n")
    print("##"*30)
