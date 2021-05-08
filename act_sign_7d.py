import jdCookie
import json
import requests
import time
import random
import GetSignToken

headers = {
    'Host': 'api.m.jd.com',
    'Accept': '*/*',
    'Connection': 'close',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'zh-CN,zh;q=0.9',    
    'Referer': 'https://h5.m.jd.com/',
    'Accept-Encoding': 'gzip, deflate, br',
}

def requestsGet(cookies, functionId, body):
    params = {
        'appid': 'interCenter_shopSign',
        'loginType': '2',
        'functionId': functionId,
        'body': body
    }    
    response = requests.get('https://api.m.jd.com/api', headers=headers, params=params, cookies=cookies)
    return response

signTokenList = GetSignToken.main()

for cookies in jdCookie.get_cookies():
    invalidToken = []
    validToken = []
    for signToken in signTokenList:
        body = '{"token":"' + signToken + '","venderId":""}'
        getActivityInfo = requestsGet(cookies, 'interact_center_shopSign_getActivityInfo', body)
        if getActivityInfo.text.find('"code":200') > -1:
            activityName = getActivityInfo.json()["data"]["activityName"]
            venderId = getActivityInfo.json()["data"]["venderId"]
            activityId = getActivityInfo.json()["data"]["id"]
            giftName = "未中奖"
            canSign = 0
            for continuePrizeRuleList in getActivityInfo.json()["data"]["continuePrizeRuleList"]:
                if continuePrizeRuleList["userPrizeRuleStatus"] == 1:
                    canSign = 1
            if canSign == 0:
                continue
            body = '{"token":"' + signToken + '","venderId":' + str(venderId) + ', "activityId": '+ str(activityId) +',"type":56}'
            getSignRecord = requestsGet(cookies, 'interact_center_shopSign_getSignRecord', body)
            if getSignRecord.text.find("signRecords") > -1:
                for signRecords in getSignRecord.json()["data"]["signRecords"]:
                    if signRecords["currentDay"] == 1 and signRecords["signed"] == 2:
                        canSign = 0
                        validToken.append(signToken)
                        print(f"{activityName} 今天已签到！\n")
                        break
            if canSign == 0:
                continue
            body = '{"token":"' + signToken + '","venderId":' + str(venderId) + ', "activityId": '+ str(activityId) +',"type":56,"actionType":7}'
            doSign = requestsGet(cookies, 'interact_center_shopSign_signCollectGift', body)
            if doSign.text.find('"code":404130026') > -1:
                print("达到当天签到个数限制\n")
                break
            elif doSign.text.find("prizeList") > -1 and doSign.text.find('"type":4') > -1:
                giftName = str(int(doSign.json()["data"][0]["prizeList"][0]["discount"])) + "京豆"
            validToken.append(signToken)
            print(f"{activityName} {giftName}\n")
            time.sleep(random.randint(1, 3))
        elif getActivityInfo.text.find('"code":402') > -1:
            invalidToken.append(signToken)
        time.sleep(random.randint(3, 6))
    print("\n")
    print("##"*30)
