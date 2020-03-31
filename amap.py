#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'WH-2099'

import os
import urllib.request
import json
import csv
import datetime
from shellColor import printColorStr



def showJson(data, pre=[]):
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict,list)):
                for subData in parsingGenerator(v, pre + [k]):
                    yield subData
            else:
                yield (pre + [k], v)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict,list)):
                for subData in parsingGenerator(item, pre):
                    yield subData
            else:
                yield (pre, item)



def getJson():
    printColorStr('开始爬取\n', displayType='highlight')
    url = 'http://wb.amap.com/channel.php?aoscommon=1&callback=_aosJsonpRequest1&urlname=https%3A%2F%2Fm5.amap.com%2Fws%2Fshield%2Fsearch%2Fyiqing&param=%5B%7B%22user_loc%22%3A%22%22%2C%22sign%22%3A1%7D%2C%7B%22fromchannel%22%3A%22gaode%22%2C%22version%22%3A4%2C%22first_request%22%3A1%2C%22sign%22%3A0%7D%5D&method=get'
    flag = True
    rawStr = None
    while flag:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                flag = False
                printColorStr('json文件获取中\n', foreColor='yellow', displayType='twinkle')
                rawStr = response.read().decode()
                printColorStr('json文件解码完成\n', foreColor='yellow', displayType='highlight')
            else:
                printColorStr('json文件获取失败，重试中\n', foreColor='red')
    return rawStr



def collectCityInfo(data):
    rawList = data['citylist']
    cityInfoList = []
    cityInfo = {}
    for province in rawList:
        cityInfo['provinceName'] = province.get('name', None)
        cityInfo['provinceId'] = province.get('id', None)
        cityInfo['provinceTotal'] = province.get('total', None)
        for city in province['list']:
            cityInfo['cityName'] = city.get('name', None)
            cityInfo['cityId'] = city.get('id', None)
            cityInfo['cityLon'] = city.get('lon', None)
            cityInfo['cityLat'] = city.get('lat', None)
            cityInfo['cityLevel'] = city.get('level', None)
            cityInfo['cityCount'] = city.get('count', None)
            #内容无意义
            #cityInfo['textTitle'] = city.get('text_info', None).get('title',None)
            #cityInfo['textContent'] = city.get('text_info',None).get('content', None)
            cityInfoList.append(cityInfo.copy())
    return cityInfoList



def collectDate(data):
    rawDate = data['date']
    splitIndex = rawDate.find('月')  
    year = 2020
    month = int(rawDate[0:splitIndex])
    day = int(rawDate[splitIndex + 1:-1])
    date = datetime.date(year, month, day)
    return date


def collectPoisInfo(data):
    rawList = data['pois']['one']['poilist'] + \
              data['pois']['seven']['poilist'] + \
              data['pois']['fourteen']['poilist'] + \
              data['pois']['other']['poilist']
    poisInfoList = []
    poisInfo = {}
    for poi in rawList:
        poisInfo['poiname'] = poi.get('poiname', None)
        poisInfo['lat'] = poi.get('lat', None)
        poisInfo['lon'] = poi.get('lon', None)
        #内容无意义
        #poisInfo['number'] = poi.get('number', None)
        poisInfo['tag'] = poi.get('tag_display_std', None)
        poisInfo['source'] = poi.get('source', None)
        poisInfoList.append(poisInfo.copy())
    return poisInfoList



def readJson(rawStr):
    begin = rawStr.find('{')
    end = rawStr.rfind('}') + 1
    jsonStr = rawStr[begin:end]
    rawData = json.loads(jsonStr)
    data = rawData['data']
    date = collectDate(data)
    cityInfoList = collectCityInfo(data)
    poisInfoList = collectPoisInfo(data)
    return (date, cityInfoList, poisInfoList)



def saveCsv(dataList, file):
    with open(file, 'w', encoding='gb18030', newline='') as csvF:  
        #使用csv模块读写文件，打开时需要设置参数 newline=''
        #gb18030保证excel直接读取
        heads = dataList[0].keys()
        writer = csv.DictWriter(csvF,heads)
        writer.writeheader()
        writer.writerows(dataList)
    


if __name__ == '__main__':
    jsonStr = getJson()
    date, cityInfoList, poisInfoList = readJson(jsonStr)
    printColorStr(f'{date!s}数据读取成功\n', foreColor='green')    
    saveCsv(cityInfoList, 'data/City.csv')
    saveCsv(poisInfoList, 'data/Pois.csv')
    printColorStr('!!!导出csv成功!!!\n\n\n', foreColor='green', displayType='highlight')
