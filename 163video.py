#!/usr/bin/env  python
# This Python file uses the following encoding: utf-8
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config
import urllib2,httplib,json
import sys,socket,time,random
import os
import code
import re
import time
import uuid
import gzip
import requests
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
    print(url)
    with open(file_name, "wb") as code:
        code.write(f.read())
    time.sleep(1);
    #urllib.urlretrieve(url, file_name)
    print(url)
    #要上传文件的本地路径i
    localfile = '/app/yxtk/script/'+file_name
    if os.path.exists(localfile):
        ret, info = put_file(token, key, localfile)
        return 'http://7xpkhu.com2.z0.glb.qiniucdn.com/'+key
    else:
        return url
		
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
  uname = '/app/yxtk/script/useragent.txt'
  f1 = open("/app/yxtk/script/data/163video.sql",'w',buffering=-1)
  with open(uname) as f:
        useragents = f.readlines()  
  userAgent = random.choice(useragents) 
  headers = {
             'Accept':'application/json, text/javascript, */*; q=0.01',
             'Accept-Encoding':'gzip, deflate, sdch',
             'Accept-Language':'zh-CN,zh;q=0.8',
             'Cache-Control':'max-age=0',
             'Connection':'keep-alive',
             'Host':'http://bolo.163.com/',
             'Referer':'http://bolo.163.com/',
             'Upgrade-Insecure-Requests':'1',
             'X-Requested-With':'XMLHttpRequest',
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
            }
  while True:
      for j in range(1,4):
          time.sleep(1)
	  if j == 1:
            url = 'http://bolo.163.com/bolo/api/web/video/zoneVideoList.htm?zoneId=14679608401831&type=1&pageSize=9&pageNum=1&rendering=true'
	  if j == 2:
	    url = 'http://bolo.163.com/bolo/api/web/video/zoneVideoList.htm?zoneId=14679608401821&type=1&pageSize=9&pageNum=1&rendering=true'
 	  if j == 3:
            url = 'http://bolo.163.com/bolo/api/web/video/zoneVideoList.htm?zoneId=14836951235121&type=1&pageSize=9&pageNum=1&rendering=true'                                                   
          try:
              #encoding_support = ContentEncodingProcessor
              #data = None;
              #opener = urllib2.build_opener(encoding_support)
              #opener.addheaders = [('User-agent', userAgent[:-2]),('Accept-Encoding',"gzip, deflate")]
              #urllib2.install_opener(opener)
              req = urllib2.Request(url)
              con = urllib2.urlopen(req)
              result = json.load(con);
              result = json.dumps(result, sort_keys=True, indent=2)
              result = json.loads(result);
              if len(result) == 0:
                 break; 
              pageNo = len(result);
              print pageNo;
              for i in range(0,pageNo):
                img_url = result[i]['cover'];
                print img_url
                video_url = result[i]['link'];
                print video_url
                title = "\" "+result[i]['title']+" \""
                title = title.replace("\n",'')
                title = title.replace(",",'，')
                print title
                imageUrl=qiniuUpdate(img_url.strip())
                sql ="INSERT INTO 3rd_miaopai_video(creator,modifier,create_time,modify_time,is_deleted,title,username,user_url,img_url,wap_url,video_url,category,like_count,src_type,user_id,is_promotion,thumbnail_url,tag,push_flag,recommend_flag,view_status,source) VALUES('sys','sys',now(),now(),'n',"+title.strip()+",NULL,NULL,'" + img_url.strip() + "','"+video_url.strip()+"','" +video_url.strip() + "','joke','0','meipaijoke','10000'"+",'0','" + img_url.strip()+ "',' ',0,NULL,0,'网易菠萝');"+'\n'
                print sql
                f1.writelines(sql)
                file_name = urllib2.unquote(img_url.strip()).decode('utf8').split('/')[-1]
                os.remove('/app/yxtk/script/'+file_name)
                file1 = '/root/'+file_name
                if os.path.exists(file1):
                    os.remove(file1)
          except Exception as e:
            print e
      break
  f1.close()

if __name__ == '__main__': 
  reload(sys)
  sys.setdefaultencoding('utf8')
  fetchMiaopaiData()
exit()
