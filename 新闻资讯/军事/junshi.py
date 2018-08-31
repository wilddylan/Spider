#!/usr/bin/env  python
# This Python file uses the following encoding: utf-8
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config
import urllib2,httplib,json
import datetime
import sys,socket,time,random
import os
import code
import re
import time
import uuid
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
    elif os.path.exists('/root/'+file_name):
        localfile = '/root/'+file_name
        ret, info = put_file(token, key, localfile)
        return 'http://7xpkhu.com2.z0.glb.qiniucdn.com/'+key
    else :
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
  lasttime = None;
  dr = re.compile(r'<[^>]+>',re.S)
  uname = '/app/yxtk/script/useragent.txt'
  f1 = open("/app/yxtk/script/data/junshi.sql",'w',buffering=-1)
  with open(uname) as f:
        useragents = f.readlines()  
  userAgent = random.choice(useragents) 
  headers = {
            'Host': 'mobile.chinaiiss.com',
            'Connection': 'Keep-Alive',
            'User-Agent': 'android-async-http/1.4.4 (http://loopj.com/android-async-http)',
            'Accept-Encoding': 'gzip',
            }
  while True:
      for j in range(1,2):
          time.sleep(1)
          pageNo = 0;
          url=r'http://mobile.chinaiiss.com/strategy/v3/news/get_newslist?type=chinamil&lasttime=0';
          print url                                                     
          try:
              encoding_support = ContentEncodingProcessor
              opener = urllib2.build_opener(encoding_support)
              opener.addheaders = [('User-agent', userAgent[:-2]),('Accept-Encoding',"gzip, deflate")]
              urllib2.install_opener(opener)
              post_data = None;
              req = urllib2.Request(url.strip(),post_data,headers)
              con = urllib2.urlopen(req)
              result = json.load(con);
              result = json.dumps(result, sort_keys=True, indent=2)
              result = json.loads(result);
              result = result['data']['lists'];
              if len(result) == 0:
                 break; 
              pageNo = len(result);
              print pageNo;
              for i in range(0,pageNo):
                junshi_id  = result[i]['newsid'];
                lasttime = result[i]['lasttime'];
                if result[i].has_key('title'):
                    junshi_title = "\" "+result[i]['title'].replace('\"','\'').encode('utf-8')+" \""
                    junshi_title = dr.sub('',junshi_title)
                    junshi_title = junshi_title.replace("\n",'')
                    junshi_title = junshi_title.replace("\"","")
                else:
                    junshi_title = "";
                junshi_date = result[i]['gmdate'].encode('utf-8');
                if result[i].has_key('img_large'):
                    junshi_pic = result[i]['img_large'].encode('utf-8');
                    if len(junshi_pic) == 0:
                       continue;
                else :
                    continue;
                strDate = str(junshi_date)
                if strDate.find("小时") > -1 or strDate.find("分钟") > -1:
                    junshi_date = datetime.datetime.today().strftime("%Y-%m-%d")
                    junshi_date = str(junshi_date)
                elif strDate.find("月") > -1:
                    strDate =strDate.replace('月','-')
                    strDate =str(datetime.datetime.today().strftime("%Y"))+'-'+strDate.replace('日','')
                    junshi_date = datetime.datetime.strptime(strDate, "%Y-%m-%d").date()
                    junshi_date = str(junshi_date)
                junshi_url = 'http://wap.chinaiiss.com/touch/h5/'+junshi_id
                print junshi_url
                imageUrl=qiniuUpdate(junshi_pic.strip())

                req = urllib2.Request(junshi_url)
                res = urllib2.urlopen(req)
                html1 = unicode(res.read(),'utf-8')
                res.close()
                doc1 = pq(html1)
                con = doc1('div.black_top')
                con('img').removeAttr("style")
                con('img').removeAttr("width")
                con('img').removeAttr("height")
                con('img').attr("style","width:100%")
                p = con('div.black_top').html()
                if p is None or p =='':
                  continue
                p = re.sub(r'&#13;','',p)
                p = re.sub(r'<style.*>([\S\s\t]*?)</style>','',p)
                p = re.sub(r'<script.*>([\S\s\t]*?)</script>','',p)
                p = re.sub(r'<p[^>]*>','<p>',p)
                p = re.sub(r'<(?!img|br|p|/p).*?>','',p)
                p = re.sub(r'src','oooo',p)
                p = re.sub(r'data-original','src',p)
                p = re.sub(r'\r','',p)
                p = re.sub(r'\n','',p)
                p = re.sub(r'\s','',p)
                p = re.sub(r'src=',' src=',p)
                p = re.sub(r'img','img ',p)

                #newqiniu = pq(p)
                #imgs = newqiniu('img')
                #for image in imgs.items():
                  #imgurl = image('img').attr('src')
                  #newimgurl = qiniuUpdate(imgurl.strip())
                  #p = p.replace(str(imgurl),str(newimgurl))
                sql ="INSERT INTO 3rd_tencent_news(id,creator,modifier,create_time,modify_time,is_deleted,title,time,img_url,thumbnail_url,source,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n','" +junshi_title.strip() + "','" + junshi_date.strip() +"','"+imageUrl+"','"+imageUrl+"','战略军事网','"+p.strip()+"',0,NULL,0);"+'\n'
                print sql
                f1.writelines(sql)
                file_name = urllib2.unquote(junshi_pic.strip()).decode('utf8').split('/')[-1]
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
