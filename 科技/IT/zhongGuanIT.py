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
  f1 = open("/app/yxtk/script/data/itnews.sql",'w',buffering=-1)
  with open(uname) as f:
        useragents = f.readlines()  
  userAgent = random.choice(useragents) 
  headers = {
            'Connection': 'Keep-Alive',
            'Host': 'lib.wap.zol.com.cn',
            'Accept-Encoding': 'gzip',
            }
  while True:
      for j in range(1,2):
          time.sleep(1)
          pageNo = 0;
          url=r'http://lib.wap.zol.com.cn/ipj/docList/?v=7.0&class_id=0&page=1&vs=and420&retina=1 ';
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
              result = result['list'];
              if len(result) == 0:
                 break; 
              pageNo = len(result);
              for i in range(1,pageNo):
                itNews_id  = result[i]['id'];
                if itNews_id is None:
                  continue
                if result[i].has_key('stitle'):
                    itNews_title = "\" "+result[i]['stitle'].replace('\"','\'').encode('utf-8')+" \""
                    itNews_title = dr.sub('',itNews_title)
                    itNews_title = itNews_title.replace("\n",'')
                else:
                    continue
                itNews_date = result[i]['sdate'].encode('utf-8');
                
                if result[i].has_key('imgsrc'):
                    itNews_pic = result[i]['imgsrc'].encode('utf-8');
                elif result[i].has_key('pics'):
                    itNews_pic = result[i]['pics'][0];
                else :
                    continue;
                if result[i]['url'].find('/0/') > -1:
                    continue;
                itNews_url = result[i]['url'];
                print itNews_url
                imageUrl=qiniuUpdate(itNews_pic.strip())

                req = urllib2.Request(itNews_url)
                res = urllib2.urlopen(req)
                html1 = unicode(res.read(),'GBK')
                res.close()
                #res = requests.get(itNews_url)
                #html1 = res.content.encode('utf-8')
                doc1 = pq(html1)
                con = doc1('div.article-cont')
                con('img').removeAttr("style")
                con('img').removeAttr("width")
                con('img').removeAttr("height")
                con('img').attr("style","width:100%")
                p = con('div.article-cont').html()
                if p is None or p =='':
                  continue
                p = re.sub(r'&#13;','',p)
                p = re.sub(r'<style.*>([\S\s\t]*?)</style>','',p)
                p = re.sub(r'<script.*>([\S\s\t]*?)</script>','',p)
                p = re.sub(r'<p[^>]*>','<p>',p)
                p = re.sub(r'<div style="display:none;">([\S\s\t]*?)</div>','',p)
                p = re.sub(r'<(?!img|br|p|/p).*?>','',p)
                p = re.sub(r'onclick=".*?"','',p)
                newqiniu = pq(p)
                imgs = newqiniu('img')
                for image in imgs.items():
                  imgurl = image('img').attr('src')
                  newimgurl = qiniuUpdate(imgurl.strip())
                  p = p.replace(str(imgurl),str(newimgurl))
                sql ="INSERT INTO 3rd_technology(id,creator,modifier,create_time,modify_time,is_deleted,technology_id,title,technology_date,img_url,sort,user_id,thumbnail_url,source,tag,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n','"+str(itNews_id)+ "'," +itNews_title.strip() + ",'" + itNews_date.strip() +"','"+itNews_pic.strip()+"','0','','"+imageUrl+"','中关村在线','', '"+p.strip()+"',0,NULL,0);"+'\n'
                print sql
                f1.writelines(sql)
                file_name = urllib2.unquote(itNews_pic.strip()).decode('utf8').split('/')[-1]
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
