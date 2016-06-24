#-*-coding:utf-8-*- 
import math
import json
import requests

class coordtrans:

       # 获取坐标
       def BDXY(self,address):
              "百度地图bd09 return (lng,lat)"
              """
              利用百度geocoding服务解析地址获取位置坐标
              :param address:需要解析的地址
              :return:
              """
              key = '2ae1130ce176b453fb29e59a69b18407'              
              geocoding = {'output': 'json',
                           'ak': key,
                           'address': address}
       
              res = requests.get("http://api.map.baidu.com/geocoder/v2/", params=geocoding)
              if res.status_code == 200:
                     json = res.json()
                     status = json.get('status')
                     #confidence = json.get('confidence')
                     if status == 0 :
                            geocodes = json.get('result')
                            location = geocodes.get('location')
                            lng = float(location.get('lng'))
                            lat = float(location.get('lat'))
                            return (lng, lat)
                     else:
                            return None
              else:
                     return None

       def GDXY(self,address):
              "高德地图gcj02 return (lng,lat)"
              """
              利用高德geocoding服务解析地址获取位置坐标
              :param address:需要解析的地址
              :return:
              """
              key = '7ba42b62224e28a20770deeb2a2ce246'
              geocoding = {'s': 'rsv3',
                           'key': key,
                           'city': '全国',
                           'address': address}
              res = requests.get(
                     "http://restapi.amap.com/v3/geocode/geo", params=geocoding)
              if res.status_code == 200:
                     json = res.json()
                     status = json.get('status')
                     count = json.get('count')
                     if status == '1' and int(count) >= 1:
                            geocodes = json.get('geocodes')[0]
                            lng = float(geocodes.get('location').split(',')[0])
                            lat = float(geocodes.get('location').split(',')[1])
                            return (lng, lat)
                     else:
                            return None
              else:
                     return None 
       
       def out_of_china(self,lng, lat):
              """
              判断是否在国内，不在国内不做偏移
              :param lng:
              :param lat:
              :return:
              """
              if lng < 72.004 or lng > 137.8347:
                     return True
              if lat < 0.8293 or lat > 55.8271:
                     return True
              return False

       def gcj02tobd09(self,lng, lat):
              "gcj02转bd09 return lng,lat"
              """
              火星坐标系(GCJ-02)转百度坐标系(BD-09)
              高德——>百度
              :param lng:火星坐标经度
              :param lat:火星坐标纬度
              :return:
              """
              x_pi = 3.14159265358979324 * 3000.0 / 180.0
              z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
              theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
              bd_lng = z * math.cos(theta) + 0.0065
              bd_lat = z * math.sin(theta) + 0.006
              return bd_lng, bd_lat


       def bd09togcj02(self,bd_lon, bd_lat):
              "bd09转gcj02 return lng,lat"
              """
              百度坐标系(BD-09)转火星坐标系(GCJ-02)
              百度——>高德
              :param bd_lat:百度坐标纬度
              :param bd_lon:百度坐标经度
              :return:转换后的坐标列表形式
              """
              x = bd_lon - 0.0065
              y = bd_lat - 0.006
              x_pi = 3.14159265358979324 * 3000.0 / 180.0
              z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
              theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
              gg_lng = z * math.cos(theta)
              gg_lat = z * math.sin(theta)
              return gg_lng, gg_lat
       
       def wgs84togcj02(self,lng, lat):
              "wgs84转gcj02 return lng,lat"
              """
              WGS84转GCJ02(火星坐标系)
              :param lng:WGS84坐标系的经度
              :param lat:WGS84坐标系的纬度
              :return:
              """
              pi = math.pi
              ee = 0.00669342162296594323  # 扁率
              a = 6378245.0  # 长半轴 
              if self.out_of_china(lng, lat):  # 判断是否在国内
                     return lng, lat
              dlat = self._transformlat(lng - 105.0, lat - 35.0)
              dlng = self._transformlng(lng - 105.0, lat - 35.0)
              radlat = lat / 180.0 * pi
              magic = math.sin(radlat)
              magic = 1 - ee * magic * magic
              sqrtmagic = math.sqrt(magic)
              dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
              dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
              mglat = lat + dlat
              mglng = lng + dlng
              return mglng,mglat
       
       def gcj02towgs84(self,lng,lat):
              "gcj02转wgs84 return lng,lat"
              """
              GCJ02(火星坐标系)转GPS84
              :param lng:火星坐标系的经度
              :param lat:火星坐标系纬度
              :return:
              """
              pi = math.pi
              ee = 0.00669342162296594323  # 扁率
              a = 6378245.0  # 长半轴 
              if self.out_of_china(lng, lat):
                     return lng, lat
              dlat = self._transformlat(lng - 105.0, lat - 35.0)
              dlng = self._transformlng(lng - 105.0, lat - 35.0)
              radlat = lat / 180.0 * pi
              magic = math.sin(radlat)
              magic = 1 - ee * magic * magic
              sqrtmagic = math.sqrt(magic)
              dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
              dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
              mglat = lat + dlat
              mglng = lng + dlng
              return lng * 2 - mglng, lat * 2 - mglat

       def bd09towgs84(self,lng,lat):
              "bd09转wgs84 return lng,lat"
              glng,glat = self.bd09togcj02(lng,lat)
              wlng,wlat = self.gcj02towgs84(glng,glat)
              return wlng,wlat

       def wgs84tobd09(self,lng,lat):
              "wgs84转bd09 return lng,lat"
              glng,glat = self.wgs84togcj02(lng,lat)
              blng,blat = self.gcj02tobd09(glng,glat)
              return blng,blat

       def _transformlat(self,lng, lat):
              pi = math.pi
              ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
                     0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
              ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                     math.sin(2.0 * lng * pi)) * 2.0 / 3.0
              ret += (20.0 * math.sin(lat * pi) + 40.0 *
                     math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
              ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
                     math.sin(lat * pi / 30.0)) * 2.0 / 3.0
              return ret

       def _transformlng(self,lng, lat):
              pi = math.pi
              ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
                     0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
              ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                     math.sin(2.0 * lng * pi)) * 2.0 / 3.0
              ret += (20.0 * math.sin(lng * pi) + 40.0 *
                     math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
              ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
                     math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
              return ret             
