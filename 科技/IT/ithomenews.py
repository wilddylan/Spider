#!/usr/bin/env  python
# This Python file uses the following encoding: utf-8
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config
import urllib2,httplib,json
import sys,socket,time,random
import os
import codecs
import re
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

    
def fetchMiaopaiData():
  f1 = open("/app/yxtk/script/data/IThomenews.sql",'w',buffering=-1)
  headers = {
             'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
             'Accept-Encoding':'gzip, deflate, sdch',
             'Accept-Language':'zh-CN,zh;q=0.8',
             'Cache-Control':'max-age=0',
             'Connection':'keep-alive',
             'Host':'it.ithome.com',
             'Upgrade-Insecure-Requests':'1',
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
            }
  while True:
      for j in range(1,11):
          time.sleep(1)
          if j == 1:
            url = 'http://it.ithome.com/ityejie/'
          if j == 2:
            url = 'http://it.ithome.com/internet/'
          if j == 3:
            url = 'http://it.ithome.com/pinglun/'
          if j == 4:
            url = 'http://it.ithome.com/people/'
          if j == 5:
            url = 'http://it.ithome.com/fun/'
          if j == 6:
            url = 'http://it.ithome.com/chuangye/'
          if j == 7:
            url = 'http://it.ithome.com/tele/'
          if j == 8:
            url = 'http://it.ithome.com/ec/'
          if j == 9:
            url = 'http://it.ithome.com/apple/'
          if j == 10:
            url = 'http://it.ithome.com/microsoft/'
          print url;
          #i = 0;
          try:
              encoding_support = ContentEncodingProcessor
              req = urllib2.Request(url)
              res = urllib2.urlopen(req)
              html = unicode(res.read(),"utf8")
              res.close()
              doc = pq(html)
              divs = doc('ul.ulcl')
              divs = divs('li')
              for li in divs.items():
                  IThome_url = li('a').attr('href')
                  m = re.findall(r'(\w*[0-9]+)\w*',str(IThome_url))
                  if len(m) == 1:
                     IThome_id = m[0]
                  else:
                     IThome_id = '0000'
                  if li('img.lazy').attr('data-original') is None:
                     continue
                  else:
                     IThome_pic = li('img.lazy').attr('data-original')
                  imageUrl = qiniuUpdate(IThome_pic)
                  IThome_title = li('h2').children('a').text()
                  IThome_title = "\" "+IThome_title.replace('\"','\'')+" \""
                  IThome_title = IThome_title.replace("\n",'')
                  IThome_title = IThome_title.replace(",",'，')

                  req = urllib2.Request(IThome_url)
                  res = urllib2.urlopen(req)
                  html1 = unicode(res.read(),'utf-8')
                  html1 = re.sub(r'<script>(.*?)</script>','',html1)
                  res.close()
                  doc1 = pq(html1)
                  con = doc1('div.post_content')
                  con('img').removeAttr("style")
                  con('img').removeAttr("width")
                  con('img').removeAttr("height")
                  con('img').attr("style","width:100%")
                  p = con('div.post_content').html()
                  if p is None or p =='':
                    continue
                  p = re.sub(r'&#13;','',p)
                  p = re.sub(r'<style.*>([\S\s\t]*?)</style>','',p)
                  p = re.sub(r'<script.*>([\S\s\t]*?)</script>','',p)
                  p = re.sub(r'<p[^>]*>','<p>',p)
                  p = re.sub(r'<(?!img|br|p|/p).*?>','',p)
                  p = re.sub(r'src','oooo',p)
                  p = re.sub(r'data-original','src',p)
                  
                  #newqiniu = pq(p)
                  #imgs = newqiniu('img')
                  #for image in imgs.items():
                    #imgurl = image('img').attr('src')
                    #newimgurl = qiniuUpdate(imgurl.strip())
                    #p = p.replace(str(imgurl),str(newimgurl))
                  sql ="INSERT INTO 3rd_technology(id,creator,modifier,create_time,modify_time,is_deleted,technology_id,title,technology_date,img_url,sort,user_id,thumbnail_url,source,tag,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n','" + IThome_id +"'," +IThome_title.strip() + ",now(),'"+imageUrl+"','0','','','IT之家','','"+p.strip()+"',0,NULL,0);"+'\n'
                  print sql
                  f1.writelines(sql)
                  #i = i+1
		  #file_name = urllib2.unquote(IThome_pic.strip()).decode('utf8').split('/')[-1]
		  #os.remove('/app/yxtk/script/'+file_name)
          except Exception as e:
            print e
      break
  f1.close()

if __name__ == '__main__': 
  reload(sys)
  sys.setdefaultencoding('utf8')
  fetchMiaopaiData()
  sys.exit()
