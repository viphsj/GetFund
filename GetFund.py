#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################################################################
# 基金估值1：https://fundgz.1234567.com.cn/js/160222.js?rt=1516587368315
# 基金估值2：https://fundmobapi.eastmoney.com/FundMApi/FundValuationDetail.ashx?FCODE=161725&deviceid=Wap&plat=Wap&product=EFund&version=2.0.0&Uid=1996055101399758&_=1516629470384
# 基金详细信息：http://fund.eastmoney.com/pingzhongdata/160222.js?v=20180122095601
# 
# 代码借鉴了以下文章：http://blog.csdn.net/yuzhucu/article/details/55261024
#######################################################################################################

__author__ = 'DouBa'

import requests  
from bs4 import BeautifulSoup  
import time  
import random
import os
import pandas as pd  
import re
import json
import PyRSS2Gen

def randHeader():  
    # 随机生成User-Agent     
    head_connection = ['Keep-Alive', 'close']  
    head_accept = ['text/html, application/xhtml+xml,application/xml, */*']  
    head_accept_language = ['zh-CN,fr-FR;q=0.5', 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3']  
    head_user_agent = ['Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',  
                       'Opera/9.27 (Windows NT 5.2; U; zh-cn)',  
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',  
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',  
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',  
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',  
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',  
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',  
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',  
                       'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',  
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',  
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',  
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',  
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',  
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000 Chrome/26.0.1410.43 Safari/537.1 ',  
                      'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER',  
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',  
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/3.0 Safari/536.11',  
                       'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',  
                       'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0'  
                       ]  
    result = {  
        'Connection': head_connection[0],  
        'Accept': head_accept[0],  
        'Accept-Language': head_accept_language[1],  
        'User-Agent': head_user_agent[random.randrange(0, len(head_user_agent))]  
    }  
    return result  

def getCurrentTime():  
        # 获取当前时间  
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
    
def getURL(url, tries_num=5, sleep_time=0, time_out=10,max_retry = 5,isproxy = 0):  
        ''''' 
           这里重写get函数，主要是为了实现网络中断后自动重连，同时为了兼容各种网站不同的反爬策略及，通过sleep时间和timeout动态调整来测试合适的网络连接参数； 
           通过isproxy 来控制是否使用代理，以支持一些在内网办公的同学 
        :param url: 
        :param tries_num:  重试次数 
        :param sleep_time: 休眠时间 
        :param time_out: 连接超时参数 
        :param max_retry: 最大重试次数，仅仅是为了递归使用 
        :return: response 
        '''  
        sleep_time_p = sleep_time  
        time_out_p = time_out  
        tries_num_p = tries_num  
        try:  
            res = requests.Session()  
            if isproxy == 1:  
                res = requests.get(url, headers=randHeader(), timeout=time_out, proxies=proxy)  
            else:  
                res = requests.get(url, headers=randHeader(), timeout=time_out)  
            res.raise_for_status()  # 如果响应状态码不是 200，就主动抛出异常  
        except requests.RequestException as e:  
            sleep_time_p = sleep_time_p + 10  
            time_out_p = time_out_p + 10  
            tries_num_p = tries_num_p - 1  
            # 设置重试次数，最大timeout 时间和 最长休眠时间  
            if tries_num_p > 0:  
                time.sleep(sleep_time_p)  
                print (getCurrentTime(), url, 'URL Connection Error: 第', max_retry - tries_num_p, u'次 Retry Connection', e)  
                return getURL(url, tries_num_p, sleep_time_p, time_out_p,max_retry)  
        return res     

class FundSpiders():  
  
    def __init__(self):
        self.myrss = PyRSS2Gen.RSS2(title = 'Get fund gz from 1234567.com',
                                link = 'http://my.com',
                                docs = 'Test',
                                description = "仅供本人自用测试 _ DouBa",
                                pubDate = getCurrentTime(),
                                lastBuildDate = getCurrentTime(),
                                items=[]
                                )
        #xmlpath = r'fund.xml'
        #baseurl = "http://my.com"
        #if os.path.isfile(self.xmlpath):
          #os.remove(self.xmlpath)

    def getCurrentTime(self):  
        # 获取当前时间  
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))  
    
    def getRfc822Time(self):
        # 获取 RFC822 日期格式，以便 RSS 使用
        # Here is an example, a format for dates compatible with that specified in the RFC 2822 Internet email standard. 
        # from time import gmtime, strftime
        # strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        # 'Thu, 28 Jun 2001 14:17:15 +0000'
        return time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())  
  
    def getFundCodesFromCsv(self):  
        # 从csv文件中获取基金代码清单（可从wind或者其他财经网站导出）
        file_path=os.path.join(os.getcwd(),'fund.csv')  
        fund_code = pd.read_csv(filepath_or_buffer=file_path, encoding='utf-8', dtype='str')  
        Code = fund_code["Code"]
        #print ( Code)  
        return Code  

    def getFundGZ(self,fund_code):
        #获取基金估值
        fund_url='https://fundgz.1234567.com.cn/js/'+fund_code +'.js?rt=1516587368315'  
        fund_json = getURL(fund_url).text
        fund_json = fund_json.replace("jsonpgz(","").replace(");","")
        fund_gz = json.loads(fund_json)
        fund_gszzl = str(round((float(fund_gz["gsz"]) * float(fund_gz["gszzl"]) / 100),4))
        fund_gz_str = fund_gz["gztime"] + " " + fund_code + " 估值：" + fund_gz["gsz"] + " 涨幅：" + fund_gz["gszzl"] + "% ( " + fund_gszzl +" ) " + fund_gz["name"]
        # print (fund_gz_str)
        rss = PyRSS2Gen.RSSItem(
            title = fund_gz_str,
            link = fund_url,
            description = fund_gz["gztime"],
            pubDate = getCurrentTime()
            )
        self.myrss.items.append(rss)
        return fund_gz

def main():
    fundSpiders=FundSpiders()   
    isproxy = 0  # 如需要使用代理，改为1，并设置代理IP参数 proxy  
    proxy = {"http": "http://110.37.84.147:8080", "https": "http://110.37.84.147:8080"}#这里需要替换成可用的代理IP  
    header = randHeader()  
    sleep_time = 0.1
    funds = fundSpiders.getFundCodesFromCsv()  

    for fund in funds:  
         try:  
             fund_json = fundSpiders.getFundGZ(fund)
         except Exception as e:  
            print (getCurrentTime(),'main', fund,e )
    fundSpiders.myrss.write_xml(open("fundrss.xml", "w",encoding='utf-8'),encoding='utf-8')
    print("Write Done!")
  
if __name__ == "__main__":  
    main()  
