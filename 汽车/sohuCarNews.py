#!/usr/bin/env  python
# This Python file uses the following encoding: utf-8

import urllib2,httplib,json
import sys,socket,time,random
import os
import code
import re
import time
from functools import wraps
from bs4 import BeautifulSoup
from gzip import GzipFile
from StringIO import StringIO   
from HTMLParser import HTMLParser
from pyquery import PyQuery as pq


class ContentEncodingProcessor(urllib2.BaseHandler):  
  """A handler to add gzip capabilities to urllib2 requests """
 
  # add headers to requests
  def http_request(self, req):
    req.add_header("Accept-Encoding", "gzip, deflate")
    return req
 
  # decode
  def http_response(self, req, resp): 
    old_resp = resp
    # gzip
    if resp.headers.get("content-encoding") == "gzip":
        gz = GzipFile(
                    fileobj=StringIO(resp.read()),
                    mode="r"
                  )
        resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
        resp.msg = old_resp.msg
    # deflate
    if resp.headers.get("content-encoding") == "deflate":
        gz = StringIO( deflate(resp.read()) )
        resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)  # 'class to add info() and
        resp.msg = old_resp.msg
    return resp
 
    
		
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


@retry(urllib2.URLError, tries=3, delay=5, backoff=2)
def fetchMiaopaiData():
  lastid = None;
  dr = re.compile(r'<[^>]+>',re.S)
  uname = '/app/yxtk/script/useragent.txt'
  f1 = open("/app/yxtk/script/data/souhucarnews.sql",'w',buffering=-1)
  with open(uname) as f:
        useragents = f.readlines()  
  userAgent = random.choice(useragents) 
  headers = {
             'Accept':'*/*',
             'Accept-Encoding':'gzip, deflate, sdch',
             'Accept-Language':'zh-CN,zh;q=0.8',
             'Cache-Control':'max-age=0',
             'Connection':'keep-alive',
             'Cookie':'vjuids=a86860a33.14ec8fa5b18.0.d31cc95f; gn12=w:1; _smuid=XPhJA6lboSHN9HJ2Wwd8J; ent12=w:1; sci12=w:1; IPLOC=CN3301; SUV=1601171016461697; shenhui12=w:1; sohutag=8HsmeSc5Njwmcyc5NCwmYjc5NSwmYSc5MSwmZjc5NCwmZyc5NCwmbjc5NjwmaSc5Njwmdyc5NCwmaCc5NCwmYyc5NSwmZSc5MCwmbSc5NywmdCc5NH0; sohu_user_ip=218.108.65.210; vjlast=1455603022.1461746534.11; ipcncode=CN330100; __utmt=1; __utma=32066017.1607301432.1461746541.1461746541.1461746541.1; __utmb=32066017.1.10.1461746541; __utmc=32066017; __utmz=32066017.1461746541.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
             'Host':'api.db.auto.sohu.com',
             'Referer':'http://auto.sohu.com/qichexinwen.shtml',
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
            }
  while True:
      for j in range(1,21):
          time.sleep(1)
          pageNo = 0;
          url=r'http://api.db.auto.sohu.com/restful/news/list/news/'+str(j)+'/20.json';
          print url                                                     
          try:
              encoding_support = ContentEncodingProcessor
              data = None;
              opener = urllib2.build_opener(encoding_support)
              opener.addheaders = [('User-agent', userAgent[:-2]),('Accept-Encoding',"gzip, deflate")]
              urllib2.install_opener(opener)
              req = urllib2.Request(url.strip(),data,headers)
              con = urllib2.urlopen(req)
              result = json.load(con);
              result = json.dumps(result, sort_keys=True, indent=2)
              result = json.loads(result);
              result = result['result'];
              if len(result) == 0:
                 break; 
              pageNo = len(result);
              print pageNo;
              for i in range(0,pageNo):
                car_id  = str(result[i]['id']).encode('utf-8');
                if result[i].has_key('title'):
                    car_title = "\" "+result[i]['title'].replace('\"','\'').encode('utf-8')+" \""
                    car_title = dr.sub('',car_title)
                    car_title = car_title.replace("\n",'')
                    car_title = car_title.replace(",",'，')
                else:
                    car_title = "";
                timestamp=time.localtime(result[i]['pbdate']/1000)
                car_date=time.strftime("%Y-%m-%d %H:%M:%S", timestamp)
                if result[i].has_key('picurl'):
                    car_pic = result[i]['picurl'].encode('utf-8');
                else:
                    continue
		if car_pic is None:
		    continue
                car_url = result[i]['url'].encode('utf-8');

                req = urllib2.Request(car_url)
                res = urllib2.urlopen(req)
                html1 = unicode(res.read(),'GBK')
                html1 = re.sub(r'<script>(.*?)</script>','',html1)
                res.close()
                doc1 = pq(html1)
                con = doc1('#contentText')
                con('img').removeAttr("style")
                con('img').removeAttr("width")
                con('img').removeAttr("height")
                con('img').attr("style","width:100%")
                p = con('#contentText').html()
                if p is None or p =='':
                  continue
                p = re.sub(r'&#13;','',p)
                p = re.sub(r'<style.*>([\S\s\t]*?)</style>','',p)
                p = re.sub(r'<script.*>([\S\s\t]*?)</script>','',p)
                p = re.sub(r'<p[^>]*>','<p>',p)
                p = re.sub(r'<(?!img|br|p|/p).*?>','',p)
                p = re.sub(r'\r','',p)
                p = re.sub(r'\n','',p)
                p = re.sub(r'\s','',p)
                p = re.sub(r'src=',' src=',p)

                newqiniu = pq(p)
                imgs = newqiniu('img')
                for image in imgs.items():
                  imgurl = image('img').attr('src')
                  newimgurl = qiniuUpdate(imgurl.strip())
                  p = p.replace(str(imgurl),str(newimgurl))
                sql ="INSERT INTO 3rd_carnews(id,creator,modifier,create_time,modify_time,is_deleted,type_name,content_id,title,third_date,img_url,comment_count,user_id,thumbnail_url,sort,source,tag,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n','产业','" +car_id.strip() + "'," + car_title.strip() + ",'" +car_date.strip() + "','" +car_pic.strip()+ "','0','','','0','搜狐汽车','','"+p.strip()+"',0,NULL,0);"+'\n'
                print sql
                f1.writelines(sql)
                file_name = urllib2.unquote(article_pic.strip()).decode('utf8').split('/')[-1]
                os.remove('/app/yxtk/script/'+file_name)
          except Exception as e:
            print e
      break
  f1.close()

if __name__ == '__main__': 
  reload(sys)
  sys.setdefaultencoding('utf8')
  fetchMiaopaiData()
exit()
