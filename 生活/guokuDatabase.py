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
for i in range(0,7):
   if i ==0:
       f =open("/app/yxtk/script/data/haibaolife.sql",'r',buffering=-1)
       flag = True;
   if i ==1:
       f =open("/app/yxtk/script/data/lohaslife.sql",'r',buffering=-1)
       flag = True;
   if i ==2:
       f =open("/app/yxtk/script/data/raylilife.sql",'r',buffering=-1)
       flag = True;
   if i ==3:
       f =open("/app/yxtk/script/data/juzilife.sql",'r',buffering=-1)
       flag = True;
   if i ==4:
       f =open("/app/yxtk/script/data/stylemodelife.sql",'r',buffering=-1)
       flag = True;
   if i ==5:
       f =open("/app/yxtk/script/data/onlyladylife.sql",'r',buffering=-1)
       flag = True;
   if i ==6:
       f =open("/app/yxtk/script/data/meishichina.sql",'r',buffering=-1)
       flag = True;
   while True:
      line = f.readline()
      print line
      if len(line)==0:
        break;
      if line[-2:-1] != ";":
        continue;

      insert_sql =line.encode('utf-8')
      try:
         print insert_sql
         cursor.execute(insert_sql) 
         count = count +1 
         print "insert success"
         db.commit()
      except Exception as e:
         continue;
      #except ProgrammingError as e:
         #continue;

   if i==0:
       log_sql = "INSERT INTO python_crawl_log VALUES ( NULL, 'sys', NOW(), 'n', '"+str(count)+"', '3rd_guokulife', '海报生活' )"
   if i==1:
       log_sql = "INSERT INTO python_crawl_log VALUES ( NULL, 'sys', NOW(), 'n', '"+str(count)+"', '3rd_guokulife', '乐活生活' )"
   if i==2:
       log_sql = "INSERT INTO python_crawl_log VALUES ( NULL, 'sys', NOW(), 'n', '"+str(count)+"', '3rd_guokulife', '瑞丽生活' )"
   if i==3:
       log_sql = "INSERT INTO python_crawl_log VALUES ( NULL, 'sys', NOW(), 'n', '"+str(count)+"', '3rd_guokulife', '橘子生活' )"
   if i==4:
       log_sql = "INSERT INTO python_crawl_log VALUES ( NULL, 'sys', NOW(), 'n', '"+str(count)+"', '3rd_guokulife', '风尚网' )"
   if i==5:
       log_sql = "INSERT INTO python_crawl_log VALUES ( NULL, 'sys', NOW(), 'n', '"+str(count)+"', '3rd_guokulife', 'onlylady' )"
   if i==6:
       log_sql = "INSERT INTO python_crawl_log VALUES ( NULL, 'sys', NOW(), 'n', '"+str(count)+"', '3rd_guokulife', '美食天下' )"
   try:
      print log_sql
      cursor.execute(log_sql)
      print "log insert success"
      db.commit()
   except Exception as e:
      continue;
   #except ProgrammingError as e:
      #continue;
   count = 0
   flag = False;
   f.close()
db.close()
exit()
