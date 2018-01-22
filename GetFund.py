#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################################################################
# 基金估值：http://fundgz.1234567.com.cn/js/160222.js?rt=1516587368315
# 基金详细信息：http://fund.eastmoney.com/pingzhongdata/160222.js?v=20180122095601
# 代码借鉴了以下文章：http://blog.csdn.net/yuzhucu/article/details/55261024
#######################################################################################################

__author__ = 'DouBa'

import requests  
from bs4 import BeautifulSoup  
import time  
import random  
import pymysql  
import os  
import pandas as pd  
import re

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
def getURL(url, tries_num=5, sleep_time=0, time_out=10,max_retry = 5):  
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
                res = requests.get(url, headers=header, timeout=time_out, proxies=proxy)  
            else:  
                res = requests.get(url, headers=header, timeout=time_out)  
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
    
def get_html_soup(url):#获取解编码后的HTML
    html = None
    try:        
        header = {'Host': 'fund.eastmoney.com',
          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
          'Connection': 'keep-alive'}
        req = request.Request(url,headers=header)
        response = request.urlopen(req, timeout = 100)
        html = response.read().decode(encoding = "utf-8", errors='ignore')
    except Exception as e:
        print(e, "please check your network situation")
        return None
    soup = BeautifulSoup(str(html), "lxml")    
    return soup

def page_url(url, page_num):#生成带页面的URL
    if page_num == 1:
        return url
    index = url.rfind(".")
    return url[0 : index] + "_" + str(page_num) + url[index : ]

def get_title_link(url, pattern):#获取新闻的标题和正文链接
    soup = get_html_soup(url)
    news_link = {}

    scroll_list1 = BeautifulSoup(str(soup.find("div", attrs = pattern)), "lxml")
    scroll_list = BeautifulSoup(str(scroll_list1.find_all("h2")), "lxml")
    for link in scroll_list.find_all("a"):    
        if len(link.get_text().strip()) > 0 and link.get("href").find("http") != -1:
            news_link[link.get_text().strip()] = link.get('href')
    return news_link

def get_intraday_valuation(url, pattern):#抓取盘中估值
    soup= get_html_soup(url)
    intraday_valuation = BeautifulSoup(str(soup.find("dl",attrs=pattern)),"lxml")    
    string = "估值:"+intraday_valuation.find(id="gz_gsz").getText().strip()
    string += ",涨跌:"+intraday_valuation.find(id="gz_gszze").getText().strip()
    string += ","+intraday_valuation.find(id="gz_gszzl").getText().strip()
    return string

def get_news_body(url):#抓取新闻主体内容
    first = True
    content_text = []
    page_num = 1
    article_div = ""

    #使用循环处理有分页的新闻
    while first == True or article_div.find("下一页</a>") != -1:
        soup = get_html_soup(page_url(url, page_num))
        if soup == None:
            return None

        #article_div = str(soup.find("div", attrs = {"class": "article"}))
        article_div = str(soup.find("div", attrs = {"class": "news_info"}))
        soup = BeautifulSoup(str(article_div), "lxml")
        for content in soup.find_all("p"):
            if len(content.get_text().strip()) > 0:
                content_text.append(" " + content.get_text().strip())
        page_num += 1
        first = False
    for x in content_text:
        if x == " None":
            return None
    return content_text

def clean_chinese_character(text):
    '''处理特殊的中文符号,将其全部替换为'-' 否则在保存时Windows无法将有的中文符号作为路径'''
    chars = chars = ["/", "\"", "'", "·", "。","？", "！", "，", "、", "；", "：", "‘", "’", "“", "”", "（", "）", "…", "–", "．", "《", "》"];
    new_text = ""
    for i in range(len(text)):
        if text[i] not in chars:
            new_text += text[i]
        else:
            new_text += "_"
    return new_text;

class FundSpiders():  
  
    def getCurrentTime(self):  
        # 获取当前时间  
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))  
  
    def getFundCodesFromCsv(self):  
        # 从csv文件中获取基金代码清单（可从wind或者其他财经网站导出）
        file_path=os.path.join(os.getcwd(),'fund.csv')  
        fund_code = pd.read_csv(filepath_or_buffer=file_path, encoding='utf-8')  
        Code=fund_code.trade_code  
        #print ( Code)  
        return Code  
    
    def getFundInfo(self,fund_code):  
        ''''' 
        获取基金概况基本信息 
        :param fund_code: 
        :return: 
        '''  
        fund_url='http://fund.eastmoney.com/f10/jbgk_'+fund_code +'.html'  
        res = getURL(fund_url)  
        soup = BeautifulSoup(res.text, 'html.parser')  
        result = {}  
        try:  
             result['fund_code']=fund_code  
             ''''' 
           之前用select、find 比较多，但是一些网页中经常出现部分字段不全导致内容和数据库不匹配的情况导致数据错位。这里改为用使用标题的next_element 来获取数据值来规避此问题 
           其中也有个别字段有问题的，特殊处理下即可 
           '''  
             result['fund_name']= soup.find_all(text=u"基金全称")[0].next_element.text.strip()  
             result['fund_abbr_name']= soup.find_all(text=u"基金简称")[0].next_element.text.strip()  
             #result['fund_code']= soup.find_all(text=u"基金代码")[0].next_element )  
             result['fund_type']= soup.find_all(text=u"基金类型")[0].next_element.text.strip()  
             result['issue_date']= soup.find_all(text=u"发行日期")[0].next_element.text.strip()  
             result['establish_date']= soup.find_all(text=u"成立日期/规模")[0].next_element.text.split(u'/')[0].strip()  
             result['establish_scale']= soup.find_all(text=u"成立日期/规模")[0].next_element.text.split(u'/')[-1].strip()  
             result['asset_value']= soup.find_all(text=u"资产规模")[0].next_element.text.split(u'（')[0].strip()  
             result['asset_value_date']= soup.find_all(text=u"资产规模")[0].next_element.text.split(u'（')[1].split(u'）')[0].strip(u'截止至：')  
             result['units']= soup.find_all(text=u"份额规模")[0].next_element.text.strip().split(u'（')[0].strip()  
             result['units_date']= soup.find_all(text=u"份额规模")[0].next_element.text.strip().split(u'（')[1].strip(u'（截止至：）')  
             result['fund_manager']= soup.find_all(text=u"基金管理人")[0].next_element.text.strip()  
             result['fund_trustee']= soup.find_all(text=u"基金托管人")[0].next_element.text.strip()  
             result['funder']= soup.find_all(text=u"基金经理人")[0].next_element.text.strip()  
             result['total_div']= soup.find_all(text=u"成立来分红")[0].next_element.text.strip()  
             result['mgt_fee']= soup.find_all(text=u"管理费率")[0].next_element.text.strip()  
             result['trust_fee']= soup.find_all(text=u"托管费率")[0].next_element.text.strip()  
             result['sale_fee']= soup.find_all(text=u"销售服务费率")[0].next_element.text.strip()  
             result['buy_fee']= soup.find_all(text=u"最高认购费率")[0].next_element.text.strip()  
             result['buy_fee2']= soup.find_all(text=u"最高申购费率")[0].next_element.text.strip()  
             result['benchmark']= soup.find_all(text=u"业绩比较基准")[0].next_element.text.strip(u'该基金暂未披露业绩比较基准')  
             result['underlying']= soup.find_all(text=u"跟踪标的")[0].next_element.text.strip(u'该基金无跟踪标的')  
        except  Exception as e:  
            print (self.getCurrentTime(), fund_code,fund_url,e )  
  
        try:  
            mySQL.insertData('fund_info', result)  
            #print (self.getCurrentTime(),'Fund Info Insert Sucess:', result['fund_code'],result['fund_name'],result['fund_abbr_name'],result['fund_manager'],result['funder'],result['establish_date'],result['establish_scale'],result['benchmark'] )  
        except  Exception as e:  
            print (self.getCurrentTime(), fund_code,fund_url,e )  
  
        try:  
            print (self.getCurrentTime(),'getFundInfo:', result['fund_code'],result['fund_name'],result['fund_abbr_name'],result['fund_manager'],result['funder'],result['establish_date'],result['establish_scale'],result['benchmark']  
             # ,result['issue_date'],result['asset_value'],result['asset_value_date'], result['unit'],result['unit_date'],result['fund_trustee']  
             # ,result['total_div'],result['mg_fee'],result['trust_fee'], result['sale_fee'], result['buy_fee'],result['buy_fee2'],result['underlying']  
               )  
        except  Exception as e:  
            print (self.getCurrentTime(), fund_code,fund_url,e )  
  
        return result  

code_url = "http://fund.eastmoney.com/160222.html"

#html = etree.HTML(data)
#td = html.xpath('//div[@class="feed-section"]/:text()')
#code_url_pattern = {"id": "main"}
code_url_pattern = {"class": "dataItem01"}

#获取盘中估值
new_str = get_intraday_valuation(code_url, code_url_pattern)
print(new_str)
