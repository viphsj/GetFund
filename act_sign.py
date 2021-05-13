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
        'aggrateActType': 5,
        'topNewType': 2,
        'pageNo': 1,
        'pageSize': 100
    }
    getTopAndNewActInfo = session.post(url, headers=headers, data=data, params=params)
    TopAndNewAct = getTopAndNewActInfo.json()["data"]["homeInfoResultVOList"]
    
    if int(jdCookie.get_time_now().strftime("%H%M%S")) < 60000:
        data = {
            'pin': secretPin,
            'aggrateActType': 5,
            'topNewType': 1,
            'pageNo': 1,
            'pageSize': 100
        }
        getTopAndNewActInfo = session.post(url, headers=headers, data=data, params=params)
        for newAct in getTopAndNewActInfo.json()["data"]["homeInfoResultVOList"]:
            TopAndNewAct.append(newAct)

    print("##"*30)
    print("【开始签到】\n")
    for activityInfo in TopAndNewAct:
        skipSign = False
        signURL = 'https://lzkj-isv.isvjd.com/sign/wx/signUp'
        SignInfoURL = 'https://lzkj-isv.isvjd.com/sign/wx/getSignInfo'
        activityURL = 'https://lzkj-isv.isvjd.com/sign/wx/getActivity'
        if activityInfo["activityUrl"].find("sevenDay") > -1:
            signURL = 'https://lzkj-isv.isvjd.com/sign/sevenDay/wx/signUp'
            SignInfoURL = 'https://lzkj-isv.isvjd.com/sign/sevenDay/wx/getSignInfo'
            activityURL = ''
        if activityURL != '':
            data = {
                'venderId': activityInfo["venderId"],
                'actId': activityInfo["activityId"]
            }
            getActivityInfo = session.post(activityURL, headers=headers, data=data, params=params)
            if getActivityInfo.text == '':
                errMsg = " 无效活动1！"
                skipSign = True
            elif getActivityInfo.json()["isOk"] == False:
                errMsg = " 无效活动2！"
                skipSign = True
            elif getActivityInfo.json()["act"]["actRange"] != "all":
                errMsg = " 只有会员才能签到！"
                skipSign = True
        if SignInfoURL != '':
            data = {
                'venderId': activityInfo["venderId"],
                'pin': secretPin,
                'actId': activityInfo["activityId"]
            }
            getSignInfo = session.post(SignInfoURL, headers=headers, data=data, params=params)
            if getSignInfo.text == '':
                errMsg = " 无效活动1！"
                skipSign = True
            elif getSignInfo.json()["isOk"] == False:
                errMsg = " 无效活动2！"
                skipSign = True
            elif "signRecord" in getSignInfo.json():
                if getSignInfo.json()["signRecord"]["lastSignDate"] != None:
                    if str(getSignInfo.json()["signRecord"]["lastSignDate"]) == today:
                        errMsg = " 今天已签到！"
                        skipSign = True     
        if skipSign == True:
            print(activityInfo["shopName"], errMsg)
            time.sleep(random.randint(3, 6))
            continue
        data = {
            'actId': activityInfo["activityId"],
            'pin': secretPin
        }
        response = session.post(signURL, headers=headers, data=data, params=params)
        time.sleep(random.randint(3, 6))
        if response.status_code == 200:
            pattern = re.compile(r'(?<="giftName":").+?(?=",")')                
            giftName = pattern.search(response.text)
            if giftName == None:
                print(activityInfo["shopName"], " ", response.json()["msg"])
            else:
                print(activityInfo["shopName"], " ", giftName.group())
                giftMsg = activityInfo["shopName"] + " 获得：" + giftName.group() + "\n"
    if giftMsg != "":
        jdSendNotify.sendNotify("小活动-签到\n" + cookies["pt_pin"] + "\n", giftMsg)
    print("\n")
    print("##"*30)
