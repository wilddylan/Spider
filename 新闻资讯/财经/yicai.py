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
  f1 = open("/app/yxtk/script/data/yicai.sql",'w',buffering=-1)
  headers = {
             'Accept':'*/*',
             'Accept-Encoding':'gzip, deflate, sdch',
             'Accept-Language':'zh-CN,zh;q=0.8',
             'Connection':'keep-alive',
             'Host':'www.yicai.com',
             'Referer':'http://www.yicai.com/news/business/',
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
             'X-Requested-With':'XMLHttpRequest'
            }
  data = None
  while True:
      for j in range(1,3):
          time.sleep(1)
          if j == 1:
            url = 'http://www.yicai.com/news/'
          if j == 2:
            url = 'http://www.yicai.com/data/'
          print url;
          try:
              encoding_support = ContentEncodingProcessor
              req = urllib2.Request(url)
              req.add_header('Referer', 'http://www.yicai.com/news/business/')
              res = urllib2.urlopen(req)
              html = res.read()
              res.close()
              if html.find("<!DOCTYPE") == -1:
                 html = "<!DOCTYPE html><base href=http://learning.sohu.com><script type='text/javascript'>var pvinsight_page_ancestors = '200312880;401049313';</script><html><head><meta http-equiv='content-type' content='text/html; charset=utf-8' /></head><body>" + html +"</body></html>"
              try:
                  html = html.replace('<meta charset="utf-8"/>','<meta http-equiv="content-type" content="text/html; charset=utf-8" /')
              except Exception as e:
                  print e
              doc = pq(html)
              dls = doc('dl.dl-item')
              for dl in dls.items():
                  dl = pq(dl)
                  dd = dl('dd')
                  yicai_url = dd('h3 > a').attr('href')
                  yicai_title = dd('h3 > a').html().encode('utf-8')
                  yicai_date = dd('h4 > span').html()
                  #now = datetime.datetime.now()
                  #otherStyleTime = now.strftime("%Y%m%d%H%M%S")
                  #rd = random.randint(10000,99999)
                  #yicai_id = otherStyleTime + str(rd)
                  dt = dl('dt')
                  if dt('a > img').attr('src') is None:
                     yicai_pic = " "
                  else:
                     yicai_pic = dt('a > img').attr('data-original')
                  yicai_title = "\" "+yicai_title.replace('\"','\'')+" \""
                  yicai_title = yicai_title.replace("\n",'')
                  yicai_title = yicai_title.replace(",",'，')
                  yicai_title = yicai_title.replace(" ",'')
                  yicai_title = yicai_title.replace("\"",'')
                  
                  imageUrl=qiniuUpdate(yicai_pic)

                  req = urllib2.Request(yicai_url)
                  req.add_header('Referer', yicai_url)
                  res = urllib2.urlopen(req)
                  html1 = unicode(res.read(),'utf-8')
                  res.close()
                  doc1 = pq(html1)
                  con = doc1('div.m-text')
                  con('img').removeAttr("style")
                  con('img').removeAttr("width")
                  con('img').removeAttr("height")
                  con('img').attr("style","width:100%")
                  p = con('div.m-text').html()
                  if p is None or p =='':
                    continue
                  p = re.sub(r'&#13;','',p)
                  p = re.sub(r'<style.*>([\S\s\t]*?)</style>','',p)
                  p = re.sub(r'<script.*>([\S\s\t]*?)</script>','',p)
                  p = re.sub(r'<p[^>]*>','<p>',p)
                  p = re.sub(r'<(?!img|br|p|/p).*?>','',p).encode('utf-8')
                  p = re.sub(r'\r','',p)
                  p = re.sub(r'\n','',p)
                  p = re.sub(r'\s','',p)
                  p = re.sub(r'src=',' src=',p)
                  p = re.sub(r'alt',' alt',p)

                  #newqiniu = pq(p)
                  #imgs = newqiniu('img')
                  #for image in imgs.items():
                    #imgurl = image('img').attr('src')
                    #newimgurl = qiniuUpdate(imgurl.strip())
                    #p = p.replace(str(imgurl),str(newimgurl))
                  sql ="INSERT INTO 3rd_tencent_news(id,creator,modifier,create_time,modify_time,is_deleted,title,time,img_url,thumbnail_url,source,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n',\"" +yicai_title.strip() + "\",'" + yicai_date.strip() +"','"+imageUrl+"','"+imageUrl+"','第一财经','"+p.strip()+"',0,NULL,0);"+'\n'
                  print sql
                  f1.writelines(sql)
                  file_name = urllib2.unquote(yicai_pic).decode('utf8').split('/')[-1]
                  os.remove('/app/yxtk/script/'+file_name)
          except Exception as e:
            print e
      break
  f1.close()

if __name__ == '__main__': 
  reload(sys)
  fetchMiaopaiData()
exit()
