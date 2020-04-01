#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'WH-2099'

import csv
import datetime
import logging
import logging.config
import json
import os
import random

import requests
import yaml



class Crawler:
    '''
    Crawler(self, logger=None, session=None, encoding='ut-8')
    基本爬虫类
    '''
    def __init__(self, logger=None, session=None, encoding='ut-8'):
        if not logger:
            logger = logging.getLogger(__name__)
        if not session:
            session = requests.Session()

        self.logger = logger
        self.session = session
        self.encoding = encoding

        self.rawData = None
        self.datasDict = {}


    @staticmethod
    def showJson(data, pre=[]):
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (dict, list, tuple)):
                    for subData in showJson(v, pre + [k]):
                        yield subData
                else:
                    yield (pre + [k], v)
        elif isinstance(data, (list, tuple)):
            for item in data:
                if isinstance(item, (dict, list, tuple)):
                    for subData in showJson(item, pre):
                        yield subData
                else:
                    yield (pre, item)


    def getJson(self, url, **kargs):
        '''
        获取json文件并解析
        **kargs传入get()
        '''
        rawStr = ''
        self.logger.info('json爬取开始')
        with self.session.get(url, **kargs) as response:
            if response.status_code == requests.codes.ok:
                self.logger.info('json爬取成功')
                response.encoding = self.encoding
                rawStr = response.text
            else:
                self.logger.error('json爬取失败')
                raise RuntimeError('json爬取失败')

        begin = rawStr.find('{')
        end = rawStr.rfind('}') + 1
        jsonStr = rawStr[begin:end]
        self.logger.info('json解析开始')
        try:
            self.rawData = json.loads(jsonStr)
        except:
            self.logger.error('json解析失败')
            raise RuntimeError('json解析失败')
        else:
            self.logger.info('json解析成功')


    def parseRawData(self):
        '''
        解析数据
        '''
        pass

    
    def saveCsv(self, dir, **kargs):
        '''
        保存csv文件
        **kargs传入open()
        '''
        for tableName, datas in self.datasDict.items():
            file = os.path.join(dir, str(tableName) + '.csv')
            self.logger.info(file + '输出开始')
            try:
                with open(file, 'w', newline='', **kargs) as csvF:  
                #csv模块官方要求打开时设置参数 newline=''
                    heads = datas[0].keys()
                    writer = csv.DictWriter(csvF, heads)
                    writer.writeheader()
                    writer.writerows(datas)
            except:
                self.logger.error(file + '输出开始')
                raise RuntimeError(file + '输出开始')
            else:
                self.logger.info(file + '输出开始')


class AmapCrawler(Crawler):
    '''
    高德爬虫
    '''

    url = 'http://wb.amap.com/channel.php?aoscommon=1&callback=_aosJsonpRequest1&urlname=https%3A%2F%2Fm5.amap.com%2Fws%2Fshield%2Fsearch%2Fyiqing&param=%5B%7B%22user_loc%22%3A%22%22%2C%22sign%22%3A1%7D%2C%7B%22fromchannel%22%3A%22gaode%22%2C%22version%22%3A4%2C%22first_request%22%3A1%2C%22sign%22%3A0%7D%5D&method=get'

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def getJson(self):
        return super().getJson(self.url)

    def parseRawData(self):
        datas = self.rawData['data']
        date = self.__collectDate(datas)
        cityInfoList = self.__collectCityInfo(datas)
        poisInfoList = self.__collectPoisInfo(datas)
        self.datasDict['City'] = cityInfoList
        self.datasDict['Pois'] = poisInfoList
        



    def __collectCityInfo(self, data):
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
                #cityInfo['textTitle'] = city.get('text_info',
                #None).get('title',None)
                #cityInfo['textContent'] =
                #city.get('text_info',None).get('content', None)
                cityInfoList.append(cityInfo.copy())
        return cityInfoList



    def __collectDate(self, data):
        rawDate = data['date']
        splitIndex = rawDate.find('月')  
        year = 2020
        month = int(rawDate[0:splitIndex])
        day = int(rawDate[splitIndex + 1:-1])
        date = datetime.date(year, month, day)
        return date


    def __collectPoisInfo(self, data):
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




        


if __name__ == '__main__':
    
    with open('config/LogConfigNormal.yaml', 'r', encoding='utf-8') as configYaml:
        configDict = yaml.safe_load(configYaml)
        logging.config.dictConfig(configDict)
    logger = logging.getLogger('root')

    session = requests.Session()
    with open('config/UserAgents.yaml', 'r', encoding='utf-8') as uaYaml:
        uaDict = yaml.safe_load(uaYaml)['UserAgent']
        ua = random.choice(list(uaDict.values()))
        session.headers['user-agent'] = ua['String']

    amap = AmapCrawler(logger, session)
    amap.getJson()
    amap.parseRawData()
    amap.saveCsv('data/', encoding='gb18030')

    