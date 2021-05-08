import jdCookie
import json
import requests
import time
import random
import os,re

headers = {
    'Host': 'api.m.jd.com',
    'Accept': '*/*',
    'Connection': 'keep-alive',
    'User-Agent': 'jdapp;iPhone;9.0.4;13.5.1;;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://h5.m.jd.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'content-type': 'application/x-www-form-urlencoded'
}

def requestsPost(cookies, functionId, body):    
    params = {
        #'functionId': functionId
        }    
    data = {
       'functionId': functionId,
       'body': body,
       'client': 'wh5',
       'clientVersion': '1.0.0'
    }      
    response = requests.post("https://api.m.jd.com/client.action",headers=headers, params=params, cookies=cookies, data=data)
    return response

def toDo(cookies, apiId, taskToken, waitDuration):
    collectScore = requestsPost(cookies, "harmony_collectScore", r'{"appId":"' + apiId + '","taskToken":"' + taskToken + '","taskId":' + taskId + ',"actionType":1}')    
    # print(collectScore)
    time.sleep(waitDuration)
    collectScore = requestsPost(cookies, "harmony_collectScore", r'{"appId":"' + apiId + '","taskToken":"' + taskToken + '","taskId":' + taskId + ',"actionType":0}')
    # print(collectScore, "\n")
    return collectScore.json()["data"]["bizMsg"]

for cookies in jdCookie.get_cookies():
    #获取任务列表
    rawData = requests.get(os.environ["JD_LOTTERYLIST_URL"]).json()
    appIdList = rawData["idList"]
    for apiId in appIdList:
        # print(apiId)
        getTaskDetail = requestsPost(cookies, 'healthyDay_getHomeData', r'{"appId":"'+apiId+'","taskToken":"","channelId":1}')
        if getTaskDetail.text.find('"bizMsg":"success"') > -1:
            print("【开始做任务】")
            for taskVos in getTaskDetail.json()["data"]["result"]["taskVos"]:
                for taskType in [0, 1, 2, 3, 7, 8, 9, 26, 14, 15]:
                    if taskVos["taskType"] == taskType and taskVos["status"] == 1:
                        taskId = str(taskVos["taskId"])
                        taskTimes = taskVos["times"]
                        taskMaxTimes = taskVos["maxTimes"]
                        taskName = taskVos["taskName"]
                        if taskVos["waitDuration"] == 0:
                            waitDuration = 1
                        else:
                            waitDuration = taskVos["waitDuration"]
                        doNum = taskMaxTimes - taskTimes
                        i = 0
                        if taskType in [3, 9, 26]:
                            for taskInfo in taskVos["shoppingActivityVos"]:
                                if taskInfo["status"] == 1:
                                    if i == doNum:
                                        break
                                    resultMsg = toDo(cookies, apiId, taskInfo["taskToken"], waitDuration)
                                    print(taskName, str(i+1), "/", str(doNum), " ", resultMsg)
                                    i = i + 1                            
                        elif taskType == 0:
                            if i == doNum:
                                break
                            collectScore = requestsPost(cookies, "harmony_collectScore", r'{"appId":"'+apiId+'","taskToken":"' + taskVos["simpleRecordInfoVo"]["taskToken"]  + '"}')
                            break
                        elif taskType == 7:
                            for taskInfo in taskVos["browseShopVo"]:
                                if taskInfo["status"] == 1:
                                    if i == doNum:
                                        break
                                    resultMsg = toDo(cookies, apiId, taskInfo["taskToken"], waitDuration)
                                    print(taskName, str(i+1), "/", str(doNum), " ", resultMsg)
                                    i = i + 1
                        elif taskType == 1:
                            for taskInfo in taskVos["followShopVo"]:
                                if taskInfo["status"] == 1:
                                    if i == doNum:
                                        break
                                    collectScore = requestsPost(cookies, "harmony_collectScore", r'{"appId":"'+apiId+'","taskToken":"' + taskInfo["taskToken"] + '","taskId":' + taskId + ',"actionType":0}')                                
                                    resultMsg = collectScore.json()["data"]["bizMsg"]
                                    print(taskName, str(i+1), "/", str(doNum), " ", resultMsg, "\n")
                                    time.sleep(waitDuration)
                                    i = i + 1
                        elif taskType in [2, 8, 15]:
                            for taskInfo in taskVos["productInfoVos"]:
                                if taskInfo["status"] == 1:
                                    if i == doNum:
                                        break
                                    resultMsg = toDo(cookies, apiId, taskInfo["taskToken"], waitDuration)
                                    print(taskName, str(i+1), "/", str(doNum), " ", resultMsg)
                                    i = i + 1
                        elif taskType == 14:
                            for cookiesSupport in jdCookie.get_cookies_all():
                                collectScore = requestsPost(cookiesSupport, "harmony_collectScore", r'{"appId":"'+apiId+'","taskToken":"' + taskVos["assistTaskDetailVo"]["taskToken"]  + '","taskId":' + taskId + ',"actionType":0}')                            
                                print(f"{taskName} {collectScore.json()['data']['bizMsg']}\n")
                                time.sleep(waitDuration)
                                if collectScore.json()["data"]["bizMsg"] == "助力已满员！谢谢你哦~":
                                    break
            getHomeData = requestsPost(cookies, 'healthyDay_getHomeData', r'{"appId":"'+apiId+'","taskToken":"","channelId":1}')
            if getHomeData.text.find("lotteryNum") > -1:
                userScore = int(getHomeData.json()['data']['result']['userInfo']['lotteryNum'])
            else:
                userScore = int(getHomeData.json()["data"]["result"]["userInfo"]["userScore"])
            scorePerLottery = int(getHomeData.json()["data"]["result"]["userInfo"]["scorePerLottery"])
            lotteryNum = userScore//scorePerLottery
            if lotteryNum > 0:
                print("【开始抽奖】")
                for i in range(lotteryNum):                    
                    getLotteryResult = requestsPost(cookies, 'interact_template_getLotteryResult', r'{"appId":"'+apiId+'"}')
                    if getLotteryResult.json()["data"]["bizCode"] == 112:
                        break
                    pattern = re.compile(r'(?<="prizeName":").+?(?=",)')
                    giftName = pattern.search(getLotteryResult.text)
                    if giftName != None:
                        print(giftName.group())
                    time.sleep(1)
        else:
            print(getTaskDetail.text)
    time.sleep(random.randint(1, 2))
    print("\n")
    print("##"*30)
