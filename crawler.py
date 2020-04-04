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
import re

import requests
import requests_html
import yaml



class Crawler:
    '''基本爬虫类
    Args:
        logger: 日志记录器
        session: request.Session
    '''
    def __init__(self, logger=None, session=None):
        if not logger:
            logger = logging.getLogger(__name__)
        if not session:
            session = requests.Session()

        self.logger = logger
        self.session = session

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
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list, tuple)):
                    for subData in showJson(item, pre):
                        yield subData
                else:
                    yield (pre + ['[,]'], item)
        elif isinstance(data, tuple):
            for item in data:
                if isinstance(item, (dict, list, tuple)):
                    for subData in showJson(item, pre):
                        yield subData
                else:
                    yield (pre + ['(,)'], item)


    def getJson(self, url, **kwargs):
        '''获取json文件并解析
        **kwargs传入get()
        '''
        rawStr = ''
        self.logger.info('json爬取开始')
        with self.session.get(url, **kwargs) as response:
            if response.status_code == requests.codes.ok:
                self.logger.info('json爬取成功')
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
            raise
        else:
            self.logger.info('json解析成功')


    def parseRawData(self):
        '''
        解析数据
        '''
        pass


    def saveCsv(self, dir, **kwargs):
        '''
        保存csv文件
        **kwargs传入open()
        '''
        for tableName, datas in self.datasDict.items():
            file = os.path.join(dir, str(tableName) + '.csv')
            self.logger.info(file + '输出开始')
            try:
                with open(file, 'w', newline='', **kwargs) as csvF:
                #csv模块官方要求打开时设置参数 newline=''
                    heads = datas[0].keys()
                    writer = csv.DictWriter(csvF, heads)
                    writer.writeheader()
                    writer.writerows(datas)
            except:
                self.logger.error(file + '输出失败')
                raise
            else:
                self.logger.info(file + '输出成功')


class AmapCrawler(Crawler):
    '''高德爬虫
    '''

    url = 'http://wb.amap.com/channel.php?aoscommon=1&callback=_aosJsonpRequest1&urlname=https%3A%2F%2Fm5.amap.com%2Fws%2Fshield%2Fsearch%2Fyiqing&param=%5B%7B%22user_loc%22%3A%22%22%2C%22sign%22%3A1%7D%2C%7B%22fromchannel%22%3A%22gaode%22%2C%22version%22%3A4%2C%22first_request%22%3A1%2C%22sign%22%3A0%7D%5D&method=get'


    def getJson(self, **kwargs):
        super().getJson(self.url, **kwargs)


    def parseRawData(self):
        datas = self.rawData['data']
        date = self.__collectDate(datas)
        cityInfoList = self.__collectCityInfo(datas)
        poisInfoList = self.__collectPoisInfo(datas)
        self.datasDict['City'] = cityInfoList
        self.datasDict['Pois'] = poisInfoList


    def __collectCityInfo(self, datas):
        rawList = datas['citylist']
        cityInfoList = []
        cityInfo = {}
        for province in rawList:
            cityInfo['provinceName'] = province.get('name')
            cityInfo['provinceId'] = province.get('id')
            cityInfo['provinceTotal'] = province.get('total')
            for city in province['list']:
                cityInfo['cityName'] = city.get('name')
                cityInfo['cityId'] = city.get('id')
                cityInfo['cityLon'] = city.get('lon')
                cityInfo['cityLat'] = city.get('lat')
                cityInfo['cityLevel'] = city.get('level')
                cityInfo['cityCount'] = city.get('count')
                #内容无意义
                #cityInfo['textTitle'] = city.get('text_info',
                #None).get('title',None)
                #cityInfo['textContent'] =
                #city.get('text_info',None).get('content', None)
                cityInfoList.append(cityInfo.copy())
        return cityInfoList


    def __collectDate(self, datas):
        rawDate = datas['date']
        splitIndex = rawDate.find('月')
        year = 2020
        month = int(rawDate[0:splitIndex])
        day = int(rawDate[splitIndex + 1:-1])
        date = datetime.date(year, month, day)
        return date


    def __collectPoisInfo(self, datas):
        rawList = datas['pois']['one']['poilist'] + datas['pois']['seven']['poilist'] + datas['pois']['fourteen']['poilist'] + datas['pois']['other']['poilist']
        poisInfoList = []
        poisInfo = {}
        for poi in rawList:
            poisInfo['poiname'] = poi.get('poiname')
            poisInfo['lat'] = poi.get('lat')
            poisInfo['lon'] = poi.get('lon')
            #内容无意义
            #poisInfo['number'] = poi.get('number')
            poisInfo['tag'] = poi.get('tag_display_std')
            poisInfo['source'] = poi.get('source')
            poisInfoList.append(poisInfo.copy())
        return poisInfoList



class UcCrawler(Crawler):
    '''UC爬虫
    '''

    url = 'https://iflow-api.uc.cn/feiyan/track?page=0&size=100000&fallback=1&loc=%E5%85%A8%E9%83%A8%2C%E5%85%A8%E9%83%A8'


    def getJson(self, **kwargs):
        super().getJson(self.url, **kwargs)


    def parseRawData(self):
        datas = self.rawData['data']
        TrackeInfoList = self.__collectTrackeInfo(datas)
        self.datasDict['Tracke'] = TrackeInfoList


    def __collectTrackeInfo(self, datas):
        trackes = datas['trackes']
        TrackeInfoList = []
        TrackeInfo = {}
        for Tracke in trackes:
            TrackeInfo['id'] = Tracke.get('id')
            TrackeInfo['province'] = Tracke.get('province')
            TrackeInfo['city'] = Tracke.get('city')
            TrackeInfo['base_info'] = Tracke.get('base_info')
            TrackeInfo['detail_info'] = Tracke.get('detail_info')
            #内容无意义
            #TrackeInfo['index']=Tracke.get('index')
            TrackeInfo['source'] = Tracke.get('source')
            TrackeInfo['is_from_outside'] = Tracke.get('is_from_outside')
            TrackeInfoList.append(TrackeInfo.copy())
        return TrackeInfoList

class HupuCrawler(Crawler):
    '''虎扑爬虫
    '''
    
    url = 'http://movie.hupu.com/movieapi/movieView/movieAggView?movieId=200021823'


    def getJson(self, **kwargs):
        return super().getJson(self.url, **kwargs)

    
    def parseRawData(self):
        datas = self.rawData['data']
        eventViewInfoList = self.__collectEventViewInfo(datas)
        self.datasDict['Popular'] = eventViewInfoList


    def __collectEventViewInfo(self, datas):
        eventViews = datas['eventViews']
        eventViewInfo = {}
        eventViewInfoList = []
        htmlPattern = re.compile(r'<.+?>')
        for eventView in eventViews:
            eventViewInfo['title']=eventView.get('title')

            #除去html标记
            eventViewInfo['event']=htmlPattern.sub('', eventView.get('event'))

            #数据无意义
            #eventViewInfo['eventUrl']=eventView.get('eventUrl')
            #eventViewInfo['postId']=eventView.get('postId')
            
            #格式化字符为ISO-8601标准
            eventViewInfo['eventTime']=eventView.get('eventTime').replace('年', '-').replace('月', '-').replace('日', '')
            eventViewInfoList.append(eventViewInfo.copy())
        return eventViewInfoList


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
    amap.getJson(timeout=10)
    amap.parseRawData()
    amap.saveCsv('data/', encoding='gb18030')

    uc = UcCrawler(logger, session)
    uc.getJson(timeout=10)
    uc.parseRawData()
    uc.saveCsv('data/', encoding='gb18030')

    hupu = HupuCrawler(logger, session)
    hupu.getJson(timeout=10)
    hupu.parseRawData()
    hupu.saveCsv('data/', encoding='gb18030')

