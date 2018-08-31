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
    print(url)
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
  f1 = open("/app/yxtk/script/data/pidesign.sql",'w',buffering=-1)
  headers = {
             'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
             'Accept-Encoding':'gzip, deflate, sdch',
             'Accept-Language':'zh-CN,zh;q=0.8',
             'Cache-Control':'max-age=0',
             'Connection':'keep-alive',
             'Host':'www.shejipi.com',
             'Upgrade-Insecure-Requests':'1',
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
            }
  while True:
      for j in range(1,2):
          time.sleep(1)
          url = 'http://www.shejipi.com/page/1?sort=date&days=all'
          print url;
          try:
              encoding_support = ContentEncodingProcessor
              doc = pq(url, headers)
              divs = doc('article.items')
              today  = datetime.datetime.today()
              for li in divs.items():
                  pi_url = li('a').attr('href')
                  m = re.findall(r'(\w*[0-9]+)\w*',str(pi_url))
                  if len(m) == 1:
                     pi_id = str(m[0])
                  else:
                     pi_id = '0000'
                  if li('img').attr('data-original') is None:
                     pi_pic = " "
                  else:
                     pi_pic = li('img').attr('data-original')
                  pi_title = li('h1.entry-title').text()
                  pi_title = "\" "+pi_title.replace('\"','\'')+" \""
                  pi_title = pi_title.replace("\n",'')
                  pi_title = pi_title.replace(",",'，')
                  pi_date = li('span.date').html()
                  if pi_date.find("分钟") > -1:
                     pi_date = today
                  elif pi_date.find("小时") > -1:
                     pi_date = today
                  elif pi_date.find("天前") > -1:
                     m = re.findall(r'(\w*[0-9]+)\w*',pi_date)
                     pi_date = today - datetime.timedelta(int(m[0]))
                  elif pi_date.find("周前") > -1:
                     m = re.findall(r'(\w*[0-9]+)\w*',pi_date)
                     pi_date = today - datetime.timedelta(days = int(m[0])*7)
                  elif pi_date.find("月前") > -1:
                     m = re.findall(r'(\w*[0-9]+)\w*',pi_date)
                     pi_date = today - datetime.timedelta(days = int(m[0])*30)
                  pi_date = str(pi_date.strftime("%Y-%m-%d"))
                  imageUrl=qiniuUpdate(pi_pic.strip())

                  req = urllib2.Request(pi_url)
                  res = urllib2.urlopen(req)
                  html1 = unicode(res.read(),'utf-8')
                  html1 = re.sub(r'<script>(.*?)</script>','',html1)
                  res.close()
                  doc1 = pq(html1)
                  con = doc1('div.entry-content')
                  con('img').removeAttr("style")
                  con('img').removeAttr("width")
                  con('img').removeAttr("height")
                  con('img').attr("style","width:100%")
                  p = con('div.entry-content').html()
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
                  p = re.sub(r'class=',' class=',p)

                  newqiniu = pq(p)
                  imgs = newqiniu('img')
                  for image in imgs.items():
                    imgurl = image('img').attr('src')
                    newimgurl = qiniuUpdate(imgurl.strip())
                    p = p.replace(str(imgurl),str(newimgurl))
                  sql = "INSERT INTO 3rd_design(id,creator,modifier,create_time,modify_time,is_deleted,design_id,title,third_date,img_url,sort,user_id,thumbnail_url,source,tag,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n','"+pi_id+"'," +pi_title.strip() + ",'" + pi_date.strip() +"','"+pi_pic.strip()+"','0','','"+imageUrl+"','设计癖','','"+p.strip()+"',0,NULL,0);"+'\n'
                  print sql
                  f1.writelines(sql)
                  file_name = urllib2.unquote(pi_pic.strip()).decode('utf8').split('/')[-1]
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
