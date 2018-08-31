#!/usr/bin/env  python
# This Python file uses the following encoding: utf-8
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config
import urllib,urllib2,httplib,json
import sys,socket,time,random
import os
import codecs
import re
import uuid
import threading
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

class Num:
    def __init__(self):
        self.num = 0
        self.lock = threading.Lock()
    def add(self):
        self.lock.acquire()#加锁，锁住相应的资源
        key=qiniuUpdate(self.url)
        self.lock.release()#解锁，离开该资源
        return key

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

    
def fetchMiaopaiData():
  lastid = None;
  dr = re.compile(r'<[^>]+>',re.S)
  uname = '/app/yxtk/script/useragent.txt'
  f1 = open("/app/yxtk/script/data/178Game.sql",'w',buffering=-1)
  with open(uname) as f:
      useragents = f.readlines()
  userAgent = random.choice(useragents)
  headers = {
             'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
             'Accept-Encoding':'gzip, deflate, sdch',
             'Accept-Language':'zh-CN,zh;q=0.8',
             'Cache-Control':'max-age=0',
             'Connection':'keep-alive',
             'Cookie':'__wmbgid=9d9firpt3uk8ur5yowzivx51fdakxy4s; GlobalAD=1; Hm_lvt_efa0bf813242f01d2e1c0da09e3526bd=1460541391,1461722866; Hm_lpvt_efa0bf813242f01d2e1c0da09e3526bd=1461724499; CNZZDATA30068957=cnzz_eid%3D1168315897-1452054394-http%253A%252F%252Fdota2.178.com%252F%26ntime%3D1461720045; CNZZDATA30098334=cnzz_eid%3D1655623630-1460537173-%26ntime%3D1461723804; CNZZDATA30039253=cnzz_eid%3D329365541-1460538613-%26ntime%3D1461723723; __wmbsid=nzhmpjpcp7jrcjxi',
             'Host':'news.178.com',
             'Upgrade-Insecure-Requests':'1',
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
            }
  while True:
      for j in range(1,8):
          time.sleep(1)
          pageNo = 0;
          if j == 1:
              url = 'http://news.178.com/list/242375821947.html'
          if j == 2:
              url = 'http://news.178.com/list/233371578701.html'
          if j == 3:
              url = 'http://news.178.com/list/chanye.html'
          if j == 4:
              url = 'http://news.178.com/list/242362785857.html'
          if j == 5:
              url = 'http://news.178.com/list/242362762215.html'
          if j == 6:
              url = 'http://news.178.com/list/242362769466.html'
          if j == 7:
              url = 'http://news.178.com/list/242362780275.html'
          print url;
          try:
              encoding_support = ContentEncodingProcessor
              doc = pq(url, headers)
              lis = doc('li.list-content-item')
              for li in lis.items():
                  li = pq(li)
                  Game_url = li('a').attr('href')
                  m = re.findall(r'(\w*[0-9]+)\w*',str(Game_url))
                  if len(m) == 3:
                     Game_id = str(m[2])
                  else:
                     Game_id = '178'
                  if li('img').attr('src') is None:
                     Game_pic = " "
                  else:
                     Game_pic = li('img').attr('src')
                  Game_title = li('.list-content-item-title').html()
                  Game_title = "\" "+Game_title.replace('\"','\'')+" \""
                  Game_title = Game_title.replace("\n",'')
                  Game_title = Game_title.replace(",",'，')
                  Game_date = li('p.list-content-item-posttime').html()
                  file_name = urllib2.unquote(Game_pic).decode('utf8').split('/')[-1]
                  imageUrl=qiniuUpdate(Game_pic)

                  req = urllib2.Request(Game_url)
                  res = urllib2.urlopen(req)
                  html1 = unicode(res.read(),'utf-8')
                  res.close()
                  doc1 = pq(html1)
                  con = doc1('div#main-content')
                  con('img').removeAttr("style")
                  con('img').removeAttr("width")
                  con('img').removeAttr("height")
                  con('img').attr("style","width:100%")
                  p = con('div#main-content').html()
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
                  sql ="INSERT INTO 3rd_zhongguangame(id,creator,modifier,create_time,modify_time,is_deleted,gamenews_id,title,third_date,img_url,sort,user_id,thumbnail_url,source,tag,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n','" + Game_id +"'," +Game_title.strip() + ",'" + Game_date.strip() +"','"+Game_pic+"','0','','"+imageUrl+"','178游戏','','"+p.strip()+"',0,NULL,0);"+'\n'
                  print sql
                  f1.writelines(sql)
                  file_name = urllib2.unquote(Game_pic).decode('utf8').split('/')[-1]
                  if os.path.exists(file_name):
                      message = 'OK, the "%s" file exists.'
                      os.remove('/app/yxtk/script/'+file_name)
                  else:
                      message='fault'
          except Exception as e:
            print e
      break
  f1.close()

if __name__ == '__main__': 
  reload(sys)
  sys.setdefaultencoding('utf8')
  fetchMiaopaiData()
exit()
