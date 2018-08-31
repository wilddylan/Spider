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

class MyHTMLParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.file = open("/app/yxtk/script/data/yuedu.sql",'a',buffering=-1)
    self.links = []
    self.img_url = '';
    self.wap_url = '';
    self.title = '';
    self.id = '';
    self.date = '';
    self.title_found = False
    self.mont_found = False
    self.id_found = False
    self.flag = False;
    

  def handle_starttag(self, tag, attrs):
    if tag == "img":
      for name,val in attrs:
        if name == "class" and val == "attachment-archive-small wp-post-image":
           for name,val in attrs:
              if name == "src":
                 self.img_url =val;
    if tag == "a":
        for name,val in attrs:
            if name == "title":
                if str(val).find("Permanent Link to ")>-1:
                     self.title =str(val)[18:];
                     self.title = "\" "+self.title.replace('\"','\'').encode('utf-8')+" \""      
                     self.title = self.title.replace("\n",'')
                     self.title_found = True;
                for name,val in attrs:
                    if name == "href":
                       self.wap_url = val; 
  def handle_data(self,data):
        m = re.findall(r'(\w*[0-9]+)\w*',str(self.wap_url))
        if len(m) == 4:
           self.id =str(m[3])
           self.date = str(m[0])+'-'+str(m[1])+'-'+str(m[2])
           self.id_found = True
        #self.date = datetime.datetime.now().strftime("%Y-%m-%d")
        if self.id_found and self.title_found:
             self.id_found = False
             self.title_found = False
             imageUrl=qiniuUpdate(self.img_url.strip())

             req = urllib2.Request(self.wap_url)
             res = urllib2.urlopen(req)
             html1 = unicode(res.read(),'utf-8')
             res.close()
             doc1 = pq(html1)
             con = doc1('article.entry')
             con('img').removeAttr("style")
             con('img').removeAttr("width")
             con('img').removeAttr("height")
             con('img').attr("style","width:100%")
             p = con('article.entry').html()
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
             sql = "INSERT INTO 3rd_yuedubook(id,creator,modifier,create_time,modify_time,is_deleted,yuedu_id,title,third_date,img_url,sort,user_id,thumbnail_url,source,tag,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n','"+self.id+ "'," +self.title.strip() + ",'" + self.date.strip() +"','"+self.img_url.strip()+"','0','','"+imageUrl+"','佳人网','','"+p.strip()+"',0,NULL,0);"+'\n'
             print sql;
             self.file.write(sql.encode('utf-8'));
             self.file.flush();
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
                'Host': 'jiaren.org',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Upgrade-Insecure-Requests':'1',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Cache-Control':'max-age=0',
                'Proxy-Connection':'keep-alive',
                'Cookie':'lzstat_uv=27928647343830578883|4386; _gat=1; lzstat_ss=3647636641_5_1457540284_4386; _ga=GA1.2.1910162478.1457407085',
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
                }
     for j in range(1,9):
         try:
             time.sleep(1)
             data = None;
             if j == 1:
               url = 'http://jiaren.org/category/f_yuedu/'
             if j == 2:
               url = 'http://jiaren.org/category/d_human/'
             if j == 3:
               url = 'http://jiaren.org/category/a_xiuxian/'
             if j == 4:
               url = 'http://jiaren.org/category/c_learn/'
             if j == 5:
               url = 'http://jiaren.org/category/e_hot/'
             if j == 6:
               url = 'http://jiaren.org/category/b_lifetips/'
             if j == 7:
               url = 'http://jiaren.org/category/g_fun/'
             if j == 8:
               url = 'http://jiaren.org/category/z/'
             encoding_support = ContentEncodingProcessor
             opener = urllib2.build_opener(encoding_support)
             opener.addheaders = [('User-agent', userAgent[:-2]),('Accept-Encoding',"gzip, deflate")]
             urllib2.install_opener(opener)
             req = urllib2.Request(url.strip(),data,headers)
             req = urllib2.urlopen(req)
             result = req.read()
             parser = MyHTMLParser()
             parser.feed(result)
             parser.close();
         except Exception as e:
             print e;
             continue
  except Exception as e:
     print e
exit()

