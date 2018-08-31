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
    else:
        return url

    
def fetchMiaopaiData():
  lastid = None;
  dr = re.compile(r'<[^>]+>',re.S)
  f1 = open("/app/yxtk/script/data/tgbusonly.sql",'w',buffering=-1)
  data = None
  while True:
      for j in range(1,7):
          time.sleep(1)
          if j ==1:
            url = 'http://ps4.tgbus.com/news/'
          if j ==2:
            url = 'http://ps4.tgbus.com/pingce/'
          if j ==3:
            url = 'http://ps4.tgbus.com/gonglue/'
          if j ==4:
            url = 'http://ps4.tgbus.com/gonglue/jiangbei/'
          if j ==5:
            url = 'http://ps4.tgbus.com/previews/'
          if j ==6:
            url = 'http://ps4.tgbus.com/guohang/'
          try:
              encoding_support = ContentEncodingProcessor
              req = urllib2.Request(url)
              res = urllib2.urlopen(req)
              html = unicode(res.read(),'gbk')
              res.close()
              doc = pq(html)
              dls = doc('div#body > dl')
              for dl in dls.items():
                  dl = pq(dl)
                  dt = dl('dt')
                  dd = dl('dd')
                  tg_url = dt('a').attr('href')
                  print tg_url
                  tg_title = dd('a').html().encode('utf-8')
                  tg_date = dd('span').html()
                  #m = re.findall(r'(\w*[0-9]+)\w*',str(tg_url))
                  #now = datetime.datetime.now()
                  #otherStyleTime = now.strftime("%Y%m%d%H%M%S")
                  #rd = random.randint(10000,99999)
                  #tg_id=str(url.split("/")[-1])
                  #print(url.rindex("/"))
                  s=tg_url.split('/')
                  tg_id=s[len(s)-1].split(".")[0]
                  #print(tg_id)
                  #if len(m) == 3:
                  #   tg_id = str(m[2])
                  #else:
                  #   tg_id = otherStyleTime + str(rd)
                  dt = dl('dt')
                  if dt('a > img').attr('src') is None:
                     tg_pic = " "
                  else:
                     tg_pic = dt('a > img').attr('src')
                  tg_title = "\" "+tg_title.replace('\"','\'')+" \""
                  tg_title = tg_title.replace("\n",'')
                  tg_title = tg_title.replace(",",'，')                  
                  imageUrl=qiniuUpdate(tg_pic)

                  req = urllib2.Request(tg_url)
                  res = urllib2.urlopen(req)
                  html1 = unicode(res.read(),'gbk')
                  res.close()
                  doc1 = pq(html1)
                  con = doc1('div.article')
                  con('img').removeAttr("style")
                  con('img').removeAttr("width")
                  con('img').removeAttr("height")
                  con('img').attr("style","width:100%")
                  p = con('div.article').html().encode('utf-8')
                  p = re.sub(r'<span class="ptag">(.*?)</span>','',p)
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
                  sql ="INSERT INTO 3rd_zhongguangame(id,creator,modifier,create_time,modify_time,is_deleted,gamenews_id,title,third_date,img_url,sort,user_id,thumbnail_url,source,tag,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n','" + tg_id +"'," +tg_title.strip() + ",'" + tg_date.strip() +"','"+tg_pic+"','0','','"+imageUrl+"','电玩bus','','"+p.strip()+"',0,NULL,0);"+'\n'
                  print sql
                  f1.writelines(sql)
                  file_name = urllib2.unquote(tg_pic).decode('utf8').split('/')[-1]
                  os.remove('/app/yxtk/script/'+file_name)
          except Exception as e:
            print e
      break
  f1.close()

if __name__ == '__main__': 
  reload(sys)
  fetchMiaopaiData()
exit()
