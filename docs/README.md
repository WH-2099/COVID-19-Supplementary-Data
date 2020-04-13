# COVID-19-Supplementary-Data *COVID-19补充性数据*
[![LICENSE](https://img.shields.io/github/license/WH-2099/COVID-19-outbreak_area_data?style=for-the-badge)][LICENSE]


## 声明

**数据源均已标明，点击LOGO可导航至数据源页面**

==**以下声明均直接引自数据源**==
> - 为确保数据准确性和权威性，疫情场所数仅采用各地卫健委、政府等官方来源。
> - 官方目前未公布所有疫情场所，部分城市暂未收录。
> - 官方目前仅公布了部分确诊患者的活动场所，因此疫情场所数不等同于各地新冠肺炎确诊人数。
> - 确诊者信息持续收集中，仅收录官方公布的信息。


## 疫情区域 [![XinhuaAmap](XinhuaAmap.png)][amap]

> 行政区划下的疫情区域数量 [**City.csv**][City.csv]
>> 字段 | 含义
>> :---:|:---:
>> province_name  | 省份名
>> province_id    | 省份编号
>> province_total | 省份总计疫情区域数量
>> city_name   | 城市名
>> city_id     | 城市编号
>> city_lon    | 城市经度
>> city_lat    | 城市纬度
>> city_level  | 定位精度
>> city_count  | 城市疫情区域数量
>
> 具体疫情区域信息 [**Pois.csv**][Pois.csv]
>
>> 字段 | 含义
>> :---:|:---:
>> poi_name | 疫情地点名
>> lon     | 经度
>> lat     | 纬度
>> tag     | 地点类型
>> source  | 信息来源


## 患者轨迹 [![AliUC](docs/AliUC.png)][uc]

> 患者活动轨迹 [**Tracke.csv**][Tracke.csv]
>> 字段 | 含义
>> :---:|:---:
>> id              | 编号
>> province        | 省份名
>> city            | 城市名
>> base_info       | 患者基础信息
>> detail_info     | 详细活动轨迹信息
>> source          | 信息来源
>> is_from_outside | 是否为境外输入


## 名人感染 [![Hupu](docs/Hupu.png)][hupu]

> 公众人物感染情况 [**Popular.csv**][Popular.csv]
>> 字段 | 含义
>> :---:|:---:
>> title     | 标题
>> event     | 事件详情
>> date | 事件时间


[LICENSE]: https://github.com/WH-2099/COVID-19-outbreak_area_data/tree/master/LICENSE
[City.csv]: https://github.com/WH-2099/COVID-19-outbreak_area_data/tree/master/data/City.csv
[Pois.csv]: https://github.com/WH-2099/COVID-19-outbreak_area_data/tree/master/data/Pois.csv
[Tracke.csv]: https://github.com/WH-2099/COVID-19-outbreak_area_data/tree/master/data/Tracke.csv
[Popular.csv]: https://github.com/WH-2099/COVID-19-outbreak_area_data/tree/master/data/Popular.csv
[amap]: https://surl.amap.com/c3atQM1a2CT
[uc]: https://pages.uc.cn/r/feiyan-map/FyMapPageMap?app=alipay&init_tab=2&uc_biz_str=S:custom%7CC:titlebar_hover_2
[hupu]: http://movie.hupu.com/info#/moviePage?movieId=200021823&source=1

