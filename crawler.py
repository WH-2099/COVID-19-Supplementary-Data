#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'WH-2099'

import datetime
import logging
import logging.config
import json
import os
import random
import re

import psycopg2
import psycopg2.extras
import requests
import tablib
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
    def showJsonObject(data, pre=[]):
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


    def saveDB(self, conn):
        pass

                
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


    def saveFile(self, dir, format='csv', **kwargs):
        '''
        保存文件
        **kwargs传入open()
        '''
        for tableName, datas in self.datasDict.items():
            file = os.path.join(dir, str(tableName) + '.csv')
            self.logger.info(file + '输出开始')
            try:
                with open(file, 'wt', newline='', **kwargs) as f:
                #newline=''输出时不对\n进行转换
                    ds = tablib.Dataset()
                    ds.dict = datas
                    del ds['update_date']
                    f.write(ds.export(format))
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
        cityInfoList = self.__collectCityInfo(datas)
        poisInfoList = self.__collectPoisInfo(datas)
        self.datasDict['City'] = cityInfoList
        self.datasDict['Pois'] = poisInfoList


    def __collectCityInfo(self, datas):
        rawList = datas['citylist']
        cityInfoList = []
        cityInfo = {}
        for province in rawList:
            cityInfo['province_name'] = province.get('name')
            cityInfo['province_id'] = province.get('id')
            cityInfo['province_total'] = province.get('total')
            for city in province['list']:
                cityInfo['city_name'] = city.get('name')
                cityInfo['city_id'] = city.get('id')
                cityInfo['city_lon'] = city.get('lon')
                cityInfo['city_lat'] = city.get('lat')
                cityInfo['city_level'] = city.get('level')
                cityInfo['city_count'] = city.get('count')
                #内容无意义
                #cityInfo['textTitle'] = city.get('text_info',
                #None).get('title',None)
                #cityInfo['textContent'] =
                #city.get('text_info',None).get('content', None)
                cityInfo['update_date'] = datetime.date.today()
                cityInfoList.append(cityInfo.copy())
        return cityInfoList


    def __collectPoisInfo(self, datas):
        rawList = datas['pois']['one']['poilist'] + datas['pois']['seven']['poilist'] + datas['pois']['fourteen']['poilist'] + datas['pois']['other']['poilist']
        poisInfoList = []
        poisInfo = {}
        for poi in rawList:
            poisInfo['poi_name'] = poi.get('poiname')
            poisInfo['lat'] = poi.get('lat')
            poisInfo['lon'] = poi.get('lon')
            #内容无意义
            #poisInfo['number'] = poi.get('number')
            poisInfo['tag'] = poi.get('tag_display_std')
            poisInfo['source'] = poi.get('source')
            poisInfo['update_date'] = datetime.date.today()
            poisInfoList.append(poisInfo.copy())
        return poisInfoList

    
    def saveDB(self, conn):
        with conn:
            self.logger.info('更新city数据库')
            cc = conn.cursor()
            psycopg2.extras.execute_batch(cc, """INSERT INTO city(province_name, province_id, province_total, city_name, city_id, city_lon, city_lat, city_level, city_count, update_date)
                                                 VALUES (%(province_name)s, %(province_id)s, %(province_total)s, %(city_name)s, %(city_id)s, %(city_lon)s, %(city_lat)s, %(city_level)s, %(city_count)s, %(update_date)s)
                                                 ON CONFLICT DO NOTHING;"""
                                                 , self.datasDict['City'])
        with conn:
            self.logger.info('更新pois数据库')
            cc = conn.cursor()
            psycopg2.extras.execute_batch(cc, """INSERT INTO pois(poi_name, lat, lon, tag, source, update_date)
                                                 VALUES (%(poi_name)s, %(lat)s, %(lon)s, %(tag)s, %(source)s, %(update_date)s)
                                                 ON CONFLICT (poi_name, lat, lon) DO UPDATE SET update_date=%(update_date)s;"""
                                                 , self.datasDict['Pois'])


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
            TrackeInfo['is_from_outside'] = bool(Tracke.get('is_from_outside'))
            TrackeInfo['update_date'] = datetime.date.today()
            TrackeInfoList.append(TrackeInfo.copy())
        return TrackeInfoList


    def saveDB(self, conn):
        with conn:
            self.logger.info('更新tracke数据库')
            cc = conn.cursor()
            psycopg2.extras.execute_batch(cc, """INSERT INTO tracke(id, province, city, base_info, detail_info, source, is_from_outside, update_date)
                                                 VALUES (%(id)s, %(province)s, %(city)s, %(base_info)s, %(detail_info)s, %(source)s, %(is_from_outside)s, %(update_date)s)
                                                 ON CONFLICT (id) DO UPDATE SET update_date=%(update_date)s;"""
                                                 , self.datasDict['Tracke'])

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
            eventViewInfo['date']=eventView.get('eventTime').replace('年', '-').replace('月', '-').replace('日', '')
            eventViewInfo['update_date'] = datetime.date.today()
            eventViewInfoList.append(eventViewInfo.copy())
        return eventViewInfoList

    
    def saveDB(self, conn):
        with conn:
            self.logger.info('更新popular数据库')
            cc = conn.cursor()
            psycopg2.extras.execute_batch(cc, """INSERT INTO popular(title, event, date, update_date)
                                                 VALUES(%(title)s, %(event)s, %(date)s, %(update_date)s)
                                                 ON CONFLICT (title) DO UPDATE SET update_date=%(update_date)s;"""
                                                 , self.datasDict['Popular'])


if __name__ == '__main__':

    with open('../Tools/ConfigYaml/DatabaseConfigTemplate.yaml', 'rt', encoding='utf-8') as dbYAML:
        dbConfig = yaml.safe_load(dbYAML)['arch']
        dbConfig['dbname'] = 'covid'
    conn = psycopg2.connect(**dbConfig)


    with open('config/LogConfigNormal.yaml', 'rt', encoding='utf-8') as configYaml:
        configDict = yaml.safe_load(configYaml)
        logging.config.dictConfig(configDict)
    logger = logging.getLogger('root')

    session = requests.Session()
    with open('config/UserAgents.yaml', 'rt', encoding='utf-8') as uaYaml:
        uaDict = yaml.safe_load(uaYaml)['UserAgent']
        ua = random.choice(list(uaDict.values()))
        session.headers['user-agent'] = ua['String']

    amap = AmapCrawler(logger, session)
    amap.getJson(timeout=10)
    amap.parseRawData()
    amap.saveFile('data/', encoding='gb18030')
    amap.saveDB(conn)

    uc = UcCrawler(logger, session)
    uc.getJson(timeout=10)
    uc.parseRawData()
    uc.saveFile('data/', encoding='gb18030')
    uc.saveDB(conn)

    hupu = HupuCrawler(logger, session)
    hupu.getJson(timeout=10)
    hupu.parseRawData()
    hupu.saveFile('data/', encoding='gb18030')
    hupu.saveDB(conn)


    
