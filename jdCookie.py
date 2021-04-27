import requests
import json
import time
import os
import re
from datetime import datetime
from datetime import timedelta
from datetime import timezone

if "JD_COOKIE" in os.environ:
    print("执行自GitHub action")
    secret = os.environ["JD_COOKIE"]
    cookieLists_all = []
    cookieLists = []
    cookieId = 0
    for line in secret.split('&'):
        pt_key = re.findall(r'pt_key=(.*?);', line)[0]
        pt_pin = re.findall(r'pt_pin=(.*?)$', line)[0]
        if cookieId <= 2:
            cookieLists.append({"pt_key": pt_key, "pt_pin": pt_pin})
        cookieLists_all.append({"pt_key": pt_key, "pt_pin": pt_pin})
        cookieId += 1

def valid(cookies):
    headers = {
        'Host': 'api.m.jd.com',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'User-Agent': 'jdapp;iPhone;8.5.5;13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1',
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    params = (
        ('functionId', 'plantBeanIndex'),
        ('body', json.dumps(
            {"monitor_source": "plant_m_plant_index", "version": "8.4.0.0"})),
        ('appid', 'ld'),
    )
    response = requests.get('https://api.m.jd.com/client.action',
                            headers=headers, params=params, cookies=cookies)
    if response.json()["code"] == "3":
        print(f"cookie过期")
        return False
    return True

def get_cookies():
    return [i for i in cookieLists if valid(i)]
    
def get_cookies_all():
    return [i for i in cookieLists_all if valid(i)]

def get_time_now():
    SHA_TZ = timezone(timedelta(hours=8),name = 'Asia/Shanghai')
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    time_now = utc_now.astimezone(SHA_TZ)
    return time_now

def get_time_unix():
	return round(get_time_now().timestamp()*1000)

print("***"*20)
print("***"*20)
print(get_time_now().strftime("%Y-%m-%d %H:%M:%S"))
