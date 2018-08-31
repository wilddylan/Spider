#!/usr/bin/env  python
# This Python file uses the following encoding: utf-8
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config
import urllib2,httplib,json
import sys,socket,time,random
import os
import re
import codecs
import datetime
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

# deflate support
import zlib
def deflate(data):   # zlib only provides the zlib compress format, not the deflate format;
  try:               # so on top of all there's this workaround:
    return zlib.decompress(data, -zlib.MAX_WBITS)
  except zlib.error:
    return zlib.decompress(data)

list = [];
class MyHTMLParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.file = open("/app/yxtk/script/data/clothes.sql",'a',buffering=-1)
    self.links = []
    self.img_url = '';
    self.wap_url = '';
    self.title = '';
    self.id = '';
    self.date = '';
    self.title_judge = '';
    self.title_found = False
    self.time_found = False
    self.id_found = False
    self.flag = False;
    

  def handle_starttag(self, tag, attrs):
    if tag == "img":
      for name,val in attrs:
        if name == "class" and val == "hb_fl today_n_img":
           for name,val in attrs:
              if name == "data-lazy-src":
                 self.img_url =val;
              if name == "alt":
                 self.title = val;
                 self.title_judge = val;
                 self.title = "\" "+self.title.replace('\"','\'').encode('utf-8')+"\" "      
                 self.title = self.title.replace("\n",'')
                 self.title_found = True;
    if tag == "a":
        for name,val in attrs:
          if name == "title":
             title = str(val);
             if title.find(str(self.title_judge)) >-1:
                for name,val in attrs:
                  if name == "href":
                     self.wap_url = str(val);
                     if self.wap_url.find("article")>-1:
                         m = re.findall(r'(\w*[0-9]+)\w*',str(self.wap_url))
                         if len(m) ==1:
                           self.id = m[0];
                           self.id_found = True;
    if tag == "span":
         for name,val in attrs:
           if name == "class" and val == "date_item":
              self.time_found = True
  def handle_data(self,data):
        global list;
        if self.time_found:
             self.date = data.decode("utf-8")
             self.date = str(self.date)
             today  = datetime.datetime.today()
             if self.date.find("昨天") > -1:
                self.date = today - datetime.timedelta(days=1) 
                self.date =self.date.strftime("%Y-%m-%d %H:%M:%S")
                self.date = str(self.date)
        if self.id_found and self.title_found and self.time_found:
             self.time_found = False
             self.id_found = False
             self.title_found = False
             imageUrl=qiniuUpdate(self.img_url.strip())

             req = urllib2.Request(self.wap_url)
             res = urllib2.urlopen(req)
             html1 = unicode(res.read(),'utf-8')
             html1 = re.sub(r'<script>(.*?)</script>','',html1)
             res.close()
             doc1 = pq(html1)
             pages = doc1('a.next').attr('href')
             con = doc1('div.articledesc')
             con('img').removeAttr("style")
             con('img').removeAttr("width")
             con('img').removeAttr("height")
             con('img').attr("style","width:100%")
             p = con('div.articledesc').html()
             #if p is None or p =='':
               #bre
             p = re.sub(r'&#13;','',p)
             p = re.sub(r'<style.*>([\S\s\t]*?)</style>','',p)
             p = re.sub(r'<script.*>([\S\s\t]*?)</script>','',p)
             p = re.sub(r'<p[^>]*>','<p>',p)
             p = re.sub(r'<(?!img|br|p|/p).*?>','',p)
             p = re.sub(r'\r','',p)
             p = re.sub(r'\n','',p)
             p = re.sub(r'\s','',p)
             p = re.sub(r'src=',' src=',p)

             while pages is not None:
                url = 'http://star.haibao.com'+str(pages)
                print url
                req = urllib2.Request(url)
                res = urllib2.urlopen(req)
                html1 = unicode(res.read(),'utf-8')
                html1 = re.sub(r'<script>(.*?)</script>','',html1)
                res.close()
                doc1 = pq(html1)
                pages = doc1('a.next').attr('href')
                con = doc1('div.articledesc')
                con('img').removeAttr("style")
                con('img').removeAttr("width")
                con('img').removeAttr("height")
                con('img').attr("style","width:100%")
                p += con('div.articledesc').html()
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
             sql = "INSERT INTO 3rd_clothes(id,creator,modifier,create_time,modify_time,is_deleted,clothes_id,title,clothes_date,img_url,sort,user_id,thumbnail_url,source,tag,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n','"+self.id+"'," +self.title.strip() + ",'" + self.date.strip() +"','"+self.img_url.strip()+"','0','','"+imageUrl+"','HAIBAO网','','"+p.strip()+"',0,NULL,0);"+'\n'
             print sql;
             if str(self.id) not in list:
                print "self.id not in list"
                list.append(self.id);
                self.file.write(sql.encode('utf-8'));
                self.file.flush()
                file_name = urllib2.unquote(self.img_url.strip()).decode('utf8').split('/')[-1]
                os.remove('/app/yxtk/script/'+file_name)


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
    :type logger: logging.Logger instance
    """
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

        return f_retry  # true decorator

    return deco_retry

@retry(urllib2.URLError, tries=3, delay=5, backoff=2)
def fetchMiaopaiData():
  uname = '/app/yxtk/script/useragent.txt'
  with open(uname) as f:
    useragents = f.readlines()
  userAgent = random.choice(useragents)
  for i in range(1, 100):
    try:
      time.sleep(1)
      url = 'http://www.guoku.com/selected/'
      #print "##### Fetch miaopai video page: " + ", url=" + url
      encoding_support = ContentEncodingProcessor
      #proxy_handler = urllib2.ProxyHandler({"http" : r'' + proxy.strip() })
      opener = urllib2.build_opener(encoding_support)#, proxy_handler)
      opener.addheaders = [('User-agent', userAgent[:-2]),('Accept-Encoding',"gzip, deflate")]
      urllib2.install_opener(opener)
      req = urllib2.urlopen(url.strip(), timeout=5)
      result = req.read()
      parser = MyHTMLParser()
      parser.feed(result)
      parser.close()
    except urllib2.URLError, e:
      print "Time out error."
      pass
    except socket.error, e:
      print "Connection Refused:"
      pass
    except httplib.BadStatusLine:
      print "Bad status line:" 
      pass
    except httplib.IncompleteRead as e:
      print "IncompleteRead over long."
      pass

if __name__ == '__main__':  
  try:
     reload(sys)
     sys.setdefaultencoding('utf8')
     uname = '/app/yxtk/script/useragent.txt'
     with open(uname) as f:
        useragents = f.readlines()
     userAgent = random.choice(useragents)
     headers = {
                'Host': 'fashion.haibao.com',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Upgrade-Insecure-Requests':'1',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Cache-Control':'max-age=0',
                'Proxy-Connection':'keep-alive',
                'Cookie':'hbUnregUserId=FE519ED5-F429-4ECC-A7AF-87F652061BF0; mlti=@5~145679799275432918@; mlts=@5~5@; Hm_lvt_e42787babe2a01ee474c3f0133f0b9ac=1456797996; __captcha_comment=XH67MMq623D3JAczGEJE8MYveX0xrCkYc%2BkO%2F3anynw%3D; mltn=@5~6171424136073430911>1>1457662667954>1>1457662667954>6189423073026319539>1456797990813@; tmc=4.140919339.67248313.1457662053699.1457662512361.1457662986260; tma=140919339.88672223.1456797897541.1457603489659.1457662053702.3; tmd=12.140919339.88672223.1456797897541.; bfd_s=140919339.75312124.1457662053697; bfd_g=9de2782bcb754fd700004f6702618c9d556e9317; Hm_lvt_9448a813e61ee0a7a19c41713774f842=1456797965,1456798037,1457603489,1457662053; Hm_lpvt_9448a813e61ee0a7a19c41713774f842=1457662989; Hm_lvt_793a7d1dd685f0ec4bd2b50e47f13a15=1456797965,1456798037,1457603489,1457662053; Hm_lpvt_793a7d1dd685f0ec4bd2b50e47f13a15=1457662989; Hm_lvt_06ffaa048d29179add59c40fd5ca41f0=1456797965,1456798037,1457603489,1457662053; Hm_lpvt_06ffaa048d29179add59c40fd5ca41f0=1457662989',
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
                }
     for j in range(1,9):
         try:
             time.sleep(1)
             data = None;
             if j == 1:
                url = 'http://star.haibao.com/'
             if j == 2:
                url = 'http://fashion.haibao.com/'
	     if j == 3:
		url = 'http://beauty.haibao.com/'
	     if j == 4:
		url = 'http://brand.haibao.com/'
	     if j == 5:
		url = 'http://jewelrywatch.haibao.com/'
             if j == 6:
		url = 'http://accessory.haibao.com/'
	     if j == 7:
		url = 'http://wedding.haibao.com/'
	     if j == 8:
		url = 'http://life.haibao.com/'
             print url;
             encoding_support = ContentEncodingProcessor
             opener = urllib2.build_opener(encoding_support)
             opener.addheaders = []
             urllib2.install_opener(opener)
             req = urllib2.Request(url.strip(),data,headers)
             req = urllib2.urlopen(req)
             result = req.read()
             parser = MyHTMLParser()
             parser.feed(result)
             parser.close();
         except Exception as e:
             print e

  except Exception as e:
     print e
exit()

