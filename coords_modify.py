# -*- coding: utf-8 -*-
# Lolonger's

import math
import pandas as pd


##################################################################################################################
# 谷歌瓦片坐标 转 经纬度
##################################################################################################################
def tilexy2LngLat_Marcator(tilex, tiley, zoom):
    num = 2**zoom * 1.0
    lng = tilex / num * 360.0 - 180.0
    lat = math.atan(math.sinh(math.pi * (1 - 2.0 * tiley / num)))
    lat = math.degrees(lat)
    return lng, lat


def LngLat2tilexyt_Marcator(lng, lat, zoom):
    num = 2**zoom * 1.0
    tilex = ((lng + 180.0) / 360.0) * num
    tiley = (1.0 - (math.log(
        math.tan(math.radians(lat)) +
        (1.0 / math.cos(math.radians(lat)))) / math.pi)) / 2.0 * num
    return int(tilex), int(tiley)


def tilexy2LngLat_GoogleEarth(tilex, tiley, zoom):
    num = 2**zoom * 1.0
    lng = tilex / num * 360.0 - 180.0
    lat = 180 - tiley / num * 360.0
    return lng, lat


##################################################################################################################
# web墨卡托坐标 转 经纬度
##################################################################################################################
def LngLat2WebMercator(lng, lat):
    earthRad = 6378137.0
    x = lng * math.pi / 180.0 * earthRad
    a = lat * math.pi / 180.0
    y = earthRad / 2 * math.log((1.0 + math.sin(a)) / (1.0 - math.sin(a)))
    return x, y


def WebMercator2LngLat(x, y):
    lng = x / 20037508.34 * 180
    lat = y / 20037508.34 * 180
    lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180)) -
                           math.pi / 2)
    return lng, lat


##################################################################################################################
# 国内坐标系纠偏
##################################################################################################################
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率


def gcj02tobd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd09togcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


def wgs84togcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]


def gcj02towgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    #if out_of_china(lng, lat):
    #    return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]


def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(
        math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) +
            20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) +
            40.0 * math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) +
            320 * math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(
        math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) +
            20.0 * math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) +
            40.0 * math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) +
            300.0 * math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:·
    """
    if lng < 72.004 or lng > 137.8347:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False


########################################################
########################################################
########################################################

df = pd.read_csv(r"F:\Research\全国房价\SH_housepoi_19.csv")
df[['gcjLON', 'gcjLAT']] = df.apply(
    lambda row: pd.Series(bd09togcj02(row['longitude'], row['latitude'])),
    axis=1)
df[['wgs_lon', 'wgs_lat']] = df.apply(
    lambda row: pd.Series(gcj02towgs84(row['gcjLON'], row['gcjLAT'])), axis=1)
del df['longitude'], df['latitude']
del df['gcjLON'], df['gcjLAT']
df.to_csv(r"F:\Research\全国房价\SH_wgs19.csv", index=False)
