import os
import re
import json
import requests

# 设置变量 telegram 机器人
# 机器人 telegram bot 的 Token
TG_BOT_TOKEN = ""
TG_USER_ID = ""

# 读取环境变量
if "TG_BOT_TOKEN" in os.environ:
    TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]

if "TG_USER_ID" in os.environ:
    TG_USER_ID = os.environ["TG_USER_ID"]

def requestsPost(url, body):    
    params = {
        }    
    data = body
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
        }
    response = requests.post(url, headers = headers, params = params, data = data)
    return response.json()

# 发送通知
def sendNotify(text, desp):
    desp += "\n Power By GITHUB"
    pattern = re.compile(r'.*?(?=\\s?-)')
    tempText = pattern.search(text)
    if tempText is not None:
        titleText = tempText.group(0)
    else:
        titleText = text
    # 通过 telegram 机器人发送通知
    tgBotNotify(titleText, desp)

def tgBotNotify(titleText, desp):
    if TG_BOT_TOKEN != "" and TG_USER_ID != "":
        body = f"chat_id={TG_USER_ID}&text={titleText}\n\n{desp}&disable_web_page_preview=true"
        urlApi = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        doPost = requestsPost(urlApi, body)
        print(doPost)
    else:
        print("未提供 telegram 机器人推送所需的 TG_BOT_TOKEN 和 TG_USER_ID，取消 telegram 推送消息通知\n")
