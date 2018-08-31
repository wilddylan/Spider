#!/usr/bin/env  python
# This Python file uses the following encoding: utf-8
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config
import urllib2,httplib,json
import sys,socket,time,random
import os
import code
import re
import datetime
import uuid
from functools import wraps
from bs4 import BeautifulSoup
from gzip import GzipFile
from StringIO import StringIO   
from HTMLParser import HTMLParser
from pyquery import PyQuery as pq

def retry(ExceptionToCheck, tries=3, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance"""
    
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  

    return deco_retry

def qiniuUpdate(url):
    #需要填写你的 Access Key 和 Secret Key
    access_key = '8qXT7YOMZ-GtjM36rtkzKMEuZSaDrtbSPetdXYIf'
    secret_key = 'zbp-eUwRuMzucnYr37u_zXyNsiKkxBrTB84CmmSu'
    #构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = 'com-yixiantong-yxkj'
    #mutex = threading.Lock()
    #上传到七牛后保存的文件名
    keyVal = str(uuid.uuid1())
    keyTime = str(int(time.time()*1000))+'-'
    key = keyTime+keyVal[0:8]
    #mutex.acquire(3)
    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    file_name = urllib2.unquote(url).decode('utf8').split('/')[-1]
    #print(file_name)
    f = urllib2.urlopen(url)
    with open(file_name, "wb") as code:
        code.write(f.read())
    time.sleep(1);
    #urllib.urlretrieve(url, file_name)
    #print(url)
    #要上传文件的本地路径i
    localfile = '/app/yxtk/script/'+file_name
    if os.path.exists(localfile):
        ret, info = put_file(token, key, localfile)
        return 'http://7xpkhu.com2.z0.glb.qiniucdn.com/'+key
    else:
        return url


@retry(urllib2.URLError, tries=3, delay=5, backoff=2)
def fetchMiaopaiData():
  j = 1
  f1 = open("/app/yxtk/script/data/beibeiGoods.sql",'w',buffering=-1)
  f2 = open("/app/yxtk/script/data/beibeicategorty.txt",'a+',buffering=-1)
  sql = ''
  headers = {
             'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
             'Accept-Encoding':'gzip, deflate, sdch',
             'Accept-Language':'zh-CN,zh;q=0.8',
             'Cache-Control':'max-age=0',
             'Connection':'keep-alive',
             'Host':'www.beibei.com',
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
            }
  while True:
      line = f2.readline()
      line = line.replace('\n','')
      if len(line) > 0:
         if len(line.split("|")[0]) > 0:
            sub_url = line.split("|")[0];
         else:
            continue
         print "sub_url==================" + sub_url
         try:
             beibeicategorty = line.split("|")[1];
             req = urllib2.Request(sub_url)
             res = urllib2.urlopen(req)
             html = res.read()
             res.close()
             html = html.replace('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />','<meta http-equiv="content-type" content="text/html; charset=utf-8" /')
             doc = pq(html)
             divs = doc('li.view-ItemListItem')
             for li in divs.items():
                 beibei_id = li('li').attr('data-pid')
                 beibei_url = li('a').attr('href')
                 if li('a').children('img').attr('src') is None:
                      beibei_pic = li('a').children('img').attr('data-src')
                 else:
                      beibei_pic = li('a').children('img').attr('src')
                 if len(beibei_pic) == 0:
                     continue
                 beibei_title = li('div.title').attr('title')
                 beibei_title = "\" "+beibei_title.replace('\"','\'')+" \""
                 beibei_title = beibei_title.replace("\n",'')
                 beibei_title = beibei_title.replace(",",'，')
                 beibei_price = li('span.price-int').text()
                 if len(line.split("|")) == 4:
                     sub_begin = line.split("|")[2];
                     sub_end = line.split("|")[3];
                     print sub_begin + "++++" + sub_end
                     #imageUrl=qiniuUpdate(beibei_pic.strip())
                 sql ="INSERT INTO 3rd_smzdm(create_time,modify_time,is_deleted,channel,article_id,title,third_date,article_format_date,img_url,mall,wap_url,price,article_favorite,time_sort,user_smzdm_id,tag,content,sort,user_id,push_flag,recommend_flag,view_status,source)VALUES(now(),now(),'n','优惠','" +beibei_id.strip() + "'," + beibei_title.strip() + ",now(),now(),'" +beibei_pic.strip() +"','贝贝','"+beibei_url.strip() + "','"+beibei_price.strip() +"',null,null,null,null,null,0,null,0,null,0,'贝贝网');"+'\n'
                 print sql
                 f1.writelines(sql)
                 #file_name = urllib2.unquote(beibei_pic.strip()).decode('utf8').split('/')[-1]
                 #os.remove('/app/yxtk/script/'+file_name)
         except Exception as e:
             print e
             continue
      else:
         for i in range (1,3):
             if i == 1:
                 sub_url = r'http://d.beibei.com/search/item/-62---hot-'+str(j)+'.html'
                 beibeicategorty = 'driedmilk'
             else:
                 sub_url = r'http://www.beibei.com/diaper/0-0-0-'+str(j)+'.html?stock=1&oversea=0&sort=sale#diaper-con'
                 beibeicategorty = 'disaper'
             print "sub_url==================="
             print sub_url
             for j in range(1,8):
                 time.sleep(1)
                 try:
                     req = urllib2.Request(sub_url)
                     res = urllib2.urlopen(req)
                     html = res.read()
                     res.close()
                     html = html.replace('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />','<meta http-equiv="content-type" content="text/html; charset=utf-8" /')
                     doc = pq(html)
                     divs = doc('div.brand-detail').children('ul').children('li')
                     for li in divs.items():
                         beibei_url = li('a').attr('href')
                         m = re.findall(r'(\w*[0-9]+)\w*',str(beibei_url))
                         if len(m) == 2:
                              beibei_id = str(m[0])+str(m[1])
                         else:
                              beibei_id = '00000'
                         if li('a').children('img').attr('data-src') is None:
                             beibei_pic = li('a').children('img').attr('src')
                         else:
                             beibei_pic = li('a').children('img').attr('data-src')
                         beibei_title = li('div.title').attr('title')
                         beibei_title = "\" "+beibei_title.replace('\"','\'')+" \""
                         beibei_title = beibei_title.replace("\n",'')
                         beibei_title = beibei_title.replace(",",'，')
                         beibei_price = li('span.price-int').text()
                         #imageUrl=qiniuUpdate(beibei_pic.strip())
                         sql ="INSERT INTO 3rd_smzdm(create_time,modify_time,is_deleted,channel,article_id,title,third_date,article_format_date,img_url,mall,wap_url,price,article_favorite,time_sort,user_smzdm_id,tag,content,sort,user_id,push_flag,recommend_flag,view_status,source)VALUES(now(),now(),'n','优惠','" +beibei_id.strip() + "'," + beibei_title.strip() + ",now(),now(),'" +beibei_pic.strip() +"','贝贝','"+beibei_url.strip() + "','"+beibei_price.strip() +"',null,null,null,null,null,0,null,0,null,0,'贝贝网');"+'\n'
                         print sql
                         f1.writelines(sql)
                         #file_name = urllib2.unquote(beibei_pic.strip()).decode('utf8').split('/')[-1]
                         #os.remove('/app/yxtk/script/'+file_name)
                 except Exception as e:
                   print e
                   continue
         break
  f1.close()
  f2.close()

if __name__ == '__main__': 
  reload(sys)
  sys.setdefaultencoding('utf8')
  fetchMiaopaiData()
exit()
