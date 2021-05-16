import jdCookie
import json
import requests
import time
import random
import os

headers = {
    'Host': 'wq.jd.com',
    'Accept': '*/*',
    'Connection': 'close',
    'User-Agent': 'jdpingou',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://wqs.jd.com/fortune_island/index.html',
    'Accept-Encoding': 'gzip, deflate, br',
}

def requestsGet(cookies, url, paramsAdd, type):
    params = {
        'strZone': 'jxcfd',
        'bizCode': 'jxcfd',
        'source': 'jxcfd',
        'sceneval': '2',        
    }
    if type == 1:
        params.update(paramsAdd)    
    response = requests.get(url, headers=headers, params=params, cookies=cookies)
    return response.json()

shareList = []
if "JD_CFD_SHARECODE" in os.environ:
    cfdSharecode = os.environ["JD_CFD_SHARECODE"]
    for shareCode in cfdSharecode.split("@"):
        shareList.append(shareCode)


for cookies in jdCookie.get_cookies_all():
    # 助力ID
    print("##"*30)
    # myShareId = requestsGet(cookies, 'https://wq.jd.com/jxcfd/user/QueryUserInfo','', 0)
    # print("我的助力ID：",myShareId["strMyShareId"])
    # 开始助力
    print("##"*30)
    for shareId in shareList:
        params = {
            'strShareId': shareId,
            'dwSceneId': '1001'
            }
        joinScene = requestsGet(cookies, 'https://wq.jd.com/jxcfd/user/JoinScene', params, 1)
        # print(joinScene["sErrMsg"])
        time.sleep(random.randint(2,3))
    # 每天签到
    print("##"*30)
    daySignList = requestsGet(cookies, 'https://wq.jd.com/jxcfd/task/QuerySignListV2','', 0) 
    for signList in daySignList["sData"]["Sign"]:
        if signList["dwShowFlag"] == 1 and signList["dwStatus_x"] == 0:
            daySign = requestsGet(cookies, 'https://wq.jd.com/jxcfd/task/UserSignRewardV2',{'dwReqUserFlag': '1'}, 1)
            if daySign["sErrMsg"] == "success":
                print(f'每日签到：经验+{daySign["sData"]["ddwExperience"]}，金币+{daySign["sData"]["ddwMoney"]}')
            elif daySign["sErrMsg"] == "只有老用户能领取此奖励":
                daySign = requestsGet(cookies, 'https://wq.jd.com/jxcfd/task/UserSignReward',"", 0)
                print(f'每日签到：经验+{daySign["sData"]["ddwExperience"]}，金币+{daySign["sData"]["ddwMoney"]}')
            else:
                print(f'每日签到：{daySign["sErrMsg"]}')
        elif signList["dwShowFlag"] == 1 and signList["dwStatus_x"] == 1:
            print(f'每日签到：今日已签到!')
    time.sleep(random.randint(2,3))
    print("\n")
    print("##"*30)
