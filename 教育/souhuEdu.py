#!/usr/bin/env  python
# -*- coding: utf-8 -*-
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config
import urllib2,httplib,json
import sys,socket,time,random
import os
import codecs
import re
import datetime
import random
import uuid
from functools import wraps
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
    print(url)
    #要上传文件的本地路径i
    localfile = '/app/yxtk/script/'+file_name
    if os.path.exists(localfile):
        ret, info = put_file(token, key, localfile)
        return 'http://7xpkhu.com2.z0.glb.qiniucdn.com/'+key
    else:
        return url

    
def fetchMiaopaiData():
  lastid = None;
  dr = re.compile(r'<[^>]+>',re.S)
  f1 = open("/app/yxtk/script/data/souhuedu.sql",'w',buffering=-1)
  headers = {
             'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
             'Accept-Encoding':'gzip, deflate, sdch',
             'Accept-Language':'zh-CN,zh;q=0.8',
             'Cache-Control':'max-age=0',
             'Connection':'keep-alive',
             'Host':'learning.sohu.com',
             'If-Modified-Since':'Wed, 27 Apr 2016 08:58:33 GMT',
             'Upgrade-Insecure-Requests':'1',
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
            }
  while True:
      for j in range(0,1):
          time.sleep(1)         
          url = 'http://learning.sohu.com/xinwen/index.shtml'
          print url;
          try:
              encoding_support = ContentEncodingProcessor
              req = urllib2.Request(url)
              res = urllib2.urlopen(req)
              html = unicode(res.read(),'GBK')
              res.close()
              doc = pq(html)
              divs = doc('div.published')
              for div in divs.items():
                  div = pq(div)
                  edu_url = div('.content-title > a').attr('href')
		  if edu_url is None:
		      continue
                  edu_title = div('.content-title > a').html()
                  keyVal = str(uuid.uuid1())
                  keyTime = str(int(time.time()*1000))
                  edu_id=keyTime
                  if div('.content-pic > a > img').attr('src') is None:
                     continue
                  else:
                     edu_pic = div('.content-pic > a > img').attr('src')
                  edu_title = "\" "+edu_title.replace('\"','\'')+" \""
                  edu_title = edu_title.replace("\n",'')
                  edu_title = edu_title.replace(",",'，')
                  edu_date = div('.time').html()                  
                  imageUrl=qiniuUpdate(edu_pic)
                  
                  req = urllib2.Request(edu_url)
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
                  p = re.sub(r'width',' width',p)
                  
                  newqiniu = pq(p)
                  imgs = newqiniu('img')
                  for image in imgs.items():
                    imgurl = image('img').attr('src')
                    newimgurl = qiniuUpdate(imgurl.strip())
                    p = p.replace(str(imgurl),str(newimgurl))
                  sql ="INSERT INTO 3rd_souhuedu(id,creator,modifier,create_time,modify_time,is_deleted,edu_id,title,third_date,img_url,sort,user_id,thumbnail_url,source,tag,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n','" + edu_id +"'," +edu_title.strip() + ",now(),'"+edu_pic+"','0','','"+imageUrl+"','搜狐教育','','"+p.strip()+"',0,NULL,0);"+'\n'
                  print sql
                  f1.writelines(sql)
                  file_name = urllib2.unquote(edu_pic).decode('utf8').split('/')[-1]
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
