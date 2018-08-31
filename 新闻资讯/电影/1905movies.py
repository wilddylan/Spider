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
    #time.sleep(1);
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
  lastid = None;
  dr = re.compile(r'<[^>]+>',re.S)
  uname = '/app/yxtk/script/useragent.txt'
  f1 = open("/app/yxtk/script/data/1905movienews.sql",'w',buffering=-1)
  with open(uname) as f:
        useragents = f.readlines()  
  userAgent = random.choice(useragents) 
  headers = {
             'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
             'Cache-Control':'max-age=0',
             'Accept-Encoding':'gzip, deflate, sdch',
             'Accept-Language':'zh-CN,zh;q=0.8', 
             'Cache-Control':'max-age=0',
             'Connection':'keep-alive',
             'Cookie':'__uv_=6606525396; SpMLdaPxuv=m4127234796; CNZZDATA1253604207=1123659875-1462410988-null%7C1462410988; C_P_i=1; GED_PLAYLIST_ACTIVITY=W3sidSI6IkxxMnIiLCJ0IjoxNDYyNDE1MjExLCJlZCI6eyJqIjp7IkEiOnsidHQiOjkzLCJwZCI6OTMsImJzIjoxMCwiZXMiOjB9fSwiZiI6MTQ2MjQxNTIxMSwiYSI6W3sia3YiOnsiYyI6MSwibSI6NzEwfX0seyJrdiI6eyJjIjo2LCJzIjoyNCwibSI6NTE5fX0seyJrdiI6eyJtIjoxMzk2LCJzIjoxNCwiYyI6M319LHsia3YiOnsibSI6MjU0OCwiYyI6MX19LHsia3YiOnsicyI6MiwibSI6MjY3fX0seyJrdiI6eyJjIjo0LCJtIjozODY4LCJzIjo2fX1dfSwibnYiOjEsInBsIjo5MywibHQiOjE0NjI0MTUyMTF9XQ..; WOlTvIlgRpuvid_=1138; pvid=1462419488231; bfd_s=68774865.12702418.1462415058975; tmc=2.68774865.79541045.1462419484753.1462419484753.1462419488287; tma=68774865.23748224.1462415058979.1462415058979.1462415058979.1; tmd=15.68774865.23748224.1462415058979.; Hm_lvt_49411f7bde52035653f2e2b70a0bb6a5=1462415059; Hm_lpvt_49411f7bde52035653f2e2b70a0bb6a5=1462419488; Hm_lvt_5a9573957327e40b58294447cd1d8ad2=1462415059; Hm_lpvt_5a9573957327e40b58294447cd1d8ad2=1462419488; bfd_g=9de2782bcb754fd700004f6702618c9d556e9317; Hm_lvt_bfe9961e25bf081711e59b3f78be82d4=1462415059; Hm_lpvt_bfe9961e25bf081711e59b3f78be82d4=1462419488; WOlTvIlgRptime_=1462419488231',
             'Host':'www.1905.com',
             'Upgrade-Insecure-Requests':'1',
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
            }
  while True:
      for j in range(1,3):
          time.sleep(1)
          pageNo = 0;
          if j==1:
            url = 'http://www.1905.com/list-p-catid-220.html'
          if j==2:
            url = 'http://www.1905.com/film/#fixedLeftMod'
          print url                                                     
          try:
              encoding_support = ContentEncodingProcessor
              opener = urllib2.build_opener(encoding_support)
              opener.addheaders = [('User-agent', userAgent[:-2]),('Accept-Encoding',"gzip, deflate")]
              urllib2.install_opener(opener)
              req = urllib2.urlopen(url.strip(), timeout=5)
              html = req.read()
              req.close()
              if html.find("<!DOCTYPE") == -1:
                 html = "<!DOCTYPE html><base href=http://learning.sohu.com><script type='text/javascript'>var pvinsight_page_ancestors = '200312880;401049313';</script><html><head><meta http-equiv='content-type' content='text/html; charset=utf-8' /></head><body>" + html +"</body></html>"
              try:
                  html = html.replace('<meta charset="utf-8">','<meta http-equiv="content-type" content="text/html; charset=utf-8" /')
              except Exception as e:
                  print e
              doc = pq(html)
              lis = doc('li.pic-pack-out')
              for li in lis.items():
                  movie_url = li('a.pic-url').attr('href')
                  m = re.findall(r'(\w*[0-9]+)\w*',str(movie_url))
                  if len(m) == 3:
                     movie_id = str(m[2])
                  else:
                     movie_id = '0000'
                  if li('a.pic-url').children('img').attr('src') is None:
                     movie_pic = " "
                     movie_id = '0000'
                  else:
                     movie_pic = li('a.pic-url').children('img').attr('src')
                  movie_title = "\" "+li('a.title').html().encode('utf8')+" \""
                  movie_title = movie_title.replace("\n",'')
                  movie_title = movie_title.replace(",",'，')
                  movie_date = li('span.timer').html()
                  imageUrl=qiniuUpdate(movie_pic.strip())

                  req = urllib2.Request(movie_url)
                  res = urllib2.urlopen(req)
                  html1 = unicode(res.read(),'utf-8')
                  html1 = re.sub(r'<script>(.*?)</script>','',html1)
                  res.close()
                  doc1 = pq(html1)
                  con = doc1('div.pic-content')
                  con('img').removeAttr("style")
                  con('img').removeAttr("width")
                  con('img').removeAttr("height")
                  con('img').attr("style","width:100%")
                  p = con('div.pic-content').html()
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

                  #newqiniu = pq(p)
                  #imgs = newqiniu('img')
                  #for image in imgs.items():
                    #imgurl = image('img').attr('src')
                    #newimgurl = qiniuUpdate(imgurl.strip())
                    #p = p.replace(str(imgurl),str(newimgurl))
                  sql ="INSERT INTO 3rd_tencent_news(id,creator,modifier,create_time,modify_time,is_deleted,title,time,img_url,thumbnail_url,source,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n'," + movie_title.strip() + ",now(),'" +imageUrl+ "','"+imageUrl+"','1905电影网','"+p.strip()+"',0,NULL,0);"+'\n'
                  print sql
                  f1.writelines(sql)
                  file_name = urllib2.unquote(movie_pic.strip()).decode('utf8').split('/')[-1]
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
