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
  f1 = open("/app/yxtk/script/data/wulinjunshi.sql",'w',buffering=-1)
  data = None
  while True:
      for j in range(1,9):
          time.sleep(1)
          if j == 1:
             url = 'http://www.5011.net/junshi/guonei'
          if j == 2:
             url = 'http://www.5011.net/junshi/guoji/'
	  if j == 3:
	     url = 'http://www.5011.net/shehui/wanxiang/'
	  if j == 4:
	     url = 'http://www.5011.net/shehui/lieqi/'
	  if j == 5:
	     url = 'http://www.5011.net/lishizatan/'
	  if j == 6:
 	     url = 'http://www.5011.net/junshi/guancha/'
 	  if j == 7:
 	     url = 'http://www.5011.net/lishi/junshi/'
 	  if j == 8:
 	     url = 'http://www.5011.net/lishi/miwen/'
          print url;
          try:
              encoding_support = ContentEncodingProcessor
              req = urllib2.Request(url)
              res = urllib2.urlopen(req)
              html = res.read()
              res.close()
              html = html.replace('<meta charset="utf-8">','<meta http-equiv="content-type" content="text/html; charset=utf-8" /')
              doc = pq(html)
              lis = doc('div.colunmcont > ul > li')
              for li in lis.items():
                  li = pq(li)
                  wap_url = li('a:eq(0)').attr('href');
                  wulin_title = li('a:eq(0)').attr('title');
                  wulin_date = li('h3 > span').html();
                  now = datetime.datetime.now()
                  otherStyleTime = now.strftime("%Y%m%d%H%M%S")
                  rd = random.randint(10000,99999)
                  wulin_id = otherStyleTime + str(rd)
                  if li('a:eq(0) > img').attr('src') is None:
                     wulin_pic = " "
                  else:
                     wulin_pic = li('a:eq(0) > img').attr('src')
                  if wulin_pic.find(',') != -1:
                     wulin_pic = " "
                  wulin_title = "\" "+wulin_title.replace('\"','\'')+" \""
                  wulin_title = wulin_title.replace("\n",'')
                  wulin_title = wulin_title.replace(",",'，')
                  wulin_title = wulin_title.replace("\"",'')
                  imageUrl=qiniuUpdate(wulin_pic)                  

                  req = urllib2.Request(wap_url)
                  res = urllib2.urlopen(req)
                  html1 = unicode(res.read(),'utf-8')
                  res.close()
                  html1 = re.sub(r'<script>(.*?)</script>','',html1)
                  doc1 = pq(html1)
                  con = doc1('div.topmain')
                  con('img').removeAttr("style")
                  con('img').removeAttr("width")
                  con('img').removeAttr("height")
                  con('img').attr("style","width:100%")
                  p = con('div.topmain').html()
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
                  p = re.sub(r'img','img ',p)
                  p = re.sub(r'img tu','imgtu',p)

                  #newqiniu = pq(p)
                  #imgs = newqiniu('img')
                  #for image in imgs.items():
                    #imgurl = image('img').attr('src')
                    #newimgurl = qiniuUpdate(imgurl.strip())
                  sql ="INSERT INTO 3rd_tencent_news(id,creator,modifier,create_time,modify_time,is_deleted,title,time,img_url,thumbnail_url,source,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n','" +wulin_title.strip() + "','" + wulin_date.strip() +"','"+imageUrl+"','"+imageUrl+"','武林网','"+p.strip()+"',0,NULL,0);"+'\n'
                  print sql
                  f1.writelines(sql)
                  file_name = urllib2.unquote(wulin_pic).decode('utf8').split('/')[-1]
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
