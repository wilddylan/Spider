#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import urllib2,httplib,json
import sys,socket,time,random
import os
import codecs
import time
import types 
import re
from functools import wraps
from gzip import GzipFile
from StringIO import StringIO  

reload(sys)
sys.setdefaultencoding('utf-8')
db = MySQLdb.connect(host="yxtkmysqldb.mysql.rds.aliyuncs.com",user="resource",passwd="resource@1234",db="yxtk-resource",charset="utf8")
#db = MySQLdb.connect(host="yxtkmysqldb.mysql.rds.aliyuncs.com",user="yxtk",passwd="readyidu",db="yxtk-yun",charset="utf8")
#db = MySQLdb.connect(host="192.168.4.180",user="yxtk",passwd="readyidu",db="yxtk-test",charset="utf8")
#db = MySQLdb.connect(host="192.168.4.181",user="resource",passwd="readyidu@2015",db="yxtk_resource",charset="utf8")
cursor = db.cursor()
count = 0
flag = False;
query_sql = '';
for i in range(0,4):
  if i==0:
    f = open("/app/yxtk/script/data/tentnews.sql",'r',buffering=-1)
    flag = True;
  if i==1:
    f = open("/app/yxtk/script/data/1905movienews.sql",'r',buffering=-1)
    flag = True;
  if i==2:
    f = open("/app/yxtk/script/data/mtimemovienews.sql",'r',buffering=-1)
    flag = True;
  if i==3:
    f = open("/app/yxtk/script/data/baijiayule.sql",'r',buffering=-1)
    flag = True;
  while True:
    line = f.readline()
    if len(line)==0:
      break;
    if line[-2:-1] != ";":
       continue;
    if len(line.split(",")) < 11:
       continue;
    title = line.split(",")[20].encode('utf-8')
    if len(title) >0:
        query_sql = "SELECT id FROM 3rd_tencent_news WHERE title = " + title
        print query_sql
        cursor.execute(query_sql)
        query_results = cursor.fetchall()
        if len(query_results)==0:
            insert_sql =line.encode('utf-8')
            try:
               print insert_sql
               cursor.execute(insert_sql)
               count = count +1
               print "insert success"
               db.commit()
            except Exception as e:
               continue;
            except ProgrammingError as e:
               continue;
        else:
            print "already exit"
            continue

    else:
      continue

'''
  if i==0:
      log_sql = "INSERT INTO python_crawl_log VALUES ( NULL, 'sys', NOW(), 'n', '"+str(count)+"', '3rd_miaopai_video', '美拍网' )"
  try:
    print log_sql
    cursor.execute(log_sql)
    print "log insert success"
    db.commit()
  except Exception as e:
     continue;
  except ProgrammingError as e:
     continue;
  count = 0
  flag = False;
'''
f.close()
db.close()
exit()
