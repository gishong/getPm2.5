__author__ = 'Lenovo'
# -*- coding: UTF-8 -*-
import urllib2
import pyodbc
import re
import time
import os
import sys
from coordtrans import coordtrans
class DB:
    def Select(self,sqlsel):
        self.cursor.execute(sqlsel)
        rows = self.cursor.fetchall()
        return rows
    def Update(self,sqlupd):
        self.cursor.execute(sqlupd)
        self.conn.commit()
    def Exitdb(self):
        self.cursor.close()
        self.conn.close()              
    def __init__(self,dbname):        
        self.conn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb)};DBQ='+dbname)
        self.cursor = self.conn.cursor()

#获取时间
def getTime(html):
    reg = r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}'
    data = re.compile(reg)
    pmlist = re.findall(data,html)
    return pmlist[0]

#获取系统时间
def getNowTime():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))

#写入日志
def writeLog(pathdir,strs):
    filepath = pathdir+'\\log'
    filename = filepath+'\\log.txt'
    if not os.path.exists(filepath):
        os.makedirs(filepath)
        log=open(filename,'w')
    else:
        log=open(filename,'a')
    log.write(strs)
    log.close()

#下载html
def getHtml(url):
    try:
        requ = urllib2.Request(url)
        res = urllib2.urlopen(requ,timeout=2)
        #html = res.read().decode('utf-8','ignore')
        html = res.read()
        return html
    except:        
        return 0      

def main():
    #起始url
    url = "http://www.pm25.in/rank"
    print u'开始下载数据……\n'
    html = getHtml(url)

    fails=0
    while(html == 0):
        html = getHtml(url)
        fails +=1
        time.sleep(2)
        if fails > 10:
            print u'无法下载'            
            return
    #获取html时间
    _time =str(getTime(html))
    #连接数据库
    pathdir = os.getcwd()
    databasename = pathdir+'\\database.mdb'
    # 实例化数据库处理类
    db = DB(databasename)
    #查询该时段数据是否存在
    sql = "select count(*) from data where [time] = '"+_time+"'"
    info = db.Select(sql)
    if info[0][0] >0:#该时间点数据已抓取
        print '----------------------------'
        return
    # 实例化坐标获取与转换类
    geocoord = coordtrans()
    # 解析html
    pat=re.compile('<td><a href=\"(.*?)\">')
    urlitems = re.findall(pat,html)
    del pat,html
    num = len(urlitems)
    count = 0
    fails = 0
    while(num>0):
        if fails > 20:
            print '\nerror'
            break        
        for urlitem in urlitems:
            #详情页
            urls=u"http://www.pm25.in"+urlitem    
            txt = getHtml(urls)
            if txt == 0:            
                continue
            #获取地名
            pat=re.compile('<h2>(.*?)</h2>')
            address_items = re.findall(pat,txt)
            address = str(address_items[0]).decode('utf8')
            del pat,address_items
            print address

            pattern = re.compile('<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>.*?<td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td class="O3_8h_dn">(.*?)</td>.*?<td>(.*?)</td>.*?</tr>',re.S)
            items = re.findall(pattern,txt)
            del txt
            for item in items:
                #print item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8] 
                name = str(item[0]).decode('utf8')       
                AQI = str(item[1]).decode('utf8')
                PM2_5 = str(item[2]).decode('utf8')
                PM10 = str(item[3]).decode('utf8')
                CO = str(item[4]).decode('utf8')
                NO2 = str(item[5]).decode('utf8')
                O3 = str(item[6]).decode('utf8')
                O3_8h = str(item[7]).decode('utf8')
                SO2 = str(item[8]).decode('utf8') 
                
                # 获取坐标
                geom = geocoord.GDXY(address+' '+name)
                if geom == None:
                    lng,lat='',''
                else:
                    lng,lat = geocoord.gcj02towgs84(geom[0],geom[1])                                       
                print _time,name,lng,lat
                sql_insert = "insert into data([time],[_name],aqi,pm2_5,pm10,co,no2,o3,o3_8h,so2,address,lng,lat) values ('"+_time+"','"+name+"','"+AQI+"','"+PM2_5+"','"+PM10+"','"+CO+"','"+NO2+"','"+O3+"','"+O3_8h+"','"+SO2+"','"+address+"','"+str(lng)+"','"+str(lat)+"');"
                db.Update(sql_insert)
                count += 1
            del items
            urlitems.remove(urlitem)
        num = len(urlitems)
        fails += 1
        
    strs = ""+getNowTime()+" 增加了"+str(count)+"条记录\n"
    writeLog(pathdir,strs)
    db.Exitdb()#关闭数据库
    print u"写入日志文件 \\log\\log.txt\n"    

if __name__=="__main__":
    '''
    @runcounts 采集次数
    @interval 时间间隔s
    '''
    #runcounts = 24 * 365
    #interval = 3600
    print u'键入采集次数：'
    runcounts = int(raw_input())
    print u'输入采集时间间隔：(单位s)'
    interval = int(raw_input())
    
    for runcount in range(runcounts):
        start_time = time.time()
        main()
        end_time = time.time()
        print u'本次采集已经结束，等待'
        time.sleep(int(interval+start_time-end_time))
    #提示按回车退出
    raw_input("Press <Enter> To Quit!")
