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
    else:
        return url

    
def fetchMiaopaiData():
  uname = '/app/yxtk/script/useragent.txt'
  with open(uname) as f:
        useragents = f.readlines()  
  userAgent = random.choice(useragents) 
  f1 = open("/app/yxtk/script/data/jikebusiness.sql",'w',buffering=-1)
  headers = {
             'Accept':'*/*',
             'Accept-Encoding':'gzip, deflate, sdch',
             'Accept-Language':'zh-CN,zh;q=0.8',
             'Cache-Control':'max-age=0',
             'Connection':'keep-alive',
             'Host':'www.geekpark.net',
             'Referer':'http://www.geekpark.net/',
             'Upgrade-Insecure-Requests':'1',
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
            }
  while True:
      for j in range(1,2):
          time.sleep(1)
          url = 'http://www.geekpark.net/articles_list?page=1'
          print url
          try:
              encoding_support = ContentEncodingProcessor
              opener = urllib2.build_opener(encoding_support)
              opener.addheaders = [('User-agent', userAgent[:-2]),('Accept-Encoding',"gzip, deflate")]
              urllib2.install_opener(opener)
              req = urllib2.urlopen(url.strip(), timeout=5)
              html = req.read()
              req.close()
              if html.find("<!DOCTYPE") == -1:
                 html = "<!DOCTYPE html><html lang=\"zh-CN\"><head><meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\" /><meta content=\"initial-scale=1.0, width=device-width\" name=\"viewport\" /><meta content=\"webkit\" name=\"renderer\" /></head><body>" + html +"</body></html>"
              try:
                  html = html.replace('<meta charset="utf-8" />','<meta http-equiv="content-type" content="text/html; charset=utf-8" />')
              except Exception as e:
                  print e
              doc = pq(html)
              divs = doc('article.article-item')
              for li in divs.items():
                  print "li============"
                  print li
                  bu_url = li('a.dib-top').attr('href')
                  bu_url ='http://www.geekpark.net'+bu_url
                  m = re.findall(r'(\w*[0-9]+)\w*',str(bu_url))
                  if len(m) == 1:
                     bu_id = str(m[0])
                  else:
                     bu_id = '0000'
                  if li('div.responsive-img').children('img').attr('data-src') is None:
                     bu_pic = " "
                     bu_id = '0000'
                  else:
                     bu_pic = li('div.responsive-img').children('img').attr('data-src')+'?imageView2/1/w/272/h/168'
                  bu_title = li('div.responsive-img').children('img').attr('alt')
                  bu_title = "\" "+bu_title.replace('\"','\'')+" \""
                  bu_title = bu_title.replace("\n",'')
                  bu_title = bu_title.replace(",",'，')
                  bu_date = li('a.article-time').attr('title')
                  imageUrl=qiniuUpdate(bu_pic.strip())

                  req = urllib2.Request(bu_url)
                  res = urllib2.urlopen(req)
                  html1 = unicode(res.read(),'utf-8')
                  res.close()
                  html1 = re.sub(r'<\s*script[^>]*>[^<]*<\s*/\s*script\s*>','',html1)
                  doc1 = pq(html1)
                  con = doc1('div.article-content')
                  con('img').removeAttr("style")
                  con('img').removeAttr("width")
                  con('img').removeAttr("height")
                  con('img').attr("style","width:100%")
                  p = con('div.article-content').html()
                  if p is None or p =='':
                    continue
                  p = re.sub(r'<(?!img).*?>','',p)
                  p = re.sub(r'\r','',p)
                  p = re.sub(r'\n','',p)
                  p = re.sub(r'\s','',p)
                  p = re.sub(r'src=',' src=',p)
                  p = re.sub(r'alt',' alt',p)

                  newqiniu = pq(p)
                  imgs = newqiniu('img')
                  for image in imgs.items():
                    imgurl = image('img').attr('src')
                    newimgurl = qiniuUpdate(imgurl.strip())
                    p = p.replace(str(imgurl),str(newimgurl))
                  sql = "INSERT INTO 3rd_business(id,creator,modifier,create_time,modify_time,is_deleted,business_id,title,third_date,img_url,sort,user_id,thumbnail_url,source,tag,content,push_flag,recommend_flag,view_status) VALUES(NULL,'sys','sys',now(),now(),'n','"+bu_id+"'," +bu_title.strip() + ",'" + bu_date.strip() +"','"+bu_pic.strip()+"','0','','"+imageUrl+"','极客公园','','"+p.strip()+"',0,NULL,0);"+'\n'
                  print sql
                  f1.writelines(sql)
                  file_name = urllib2.unquote(bu_pic.strip()).decode('utf8').split('/')[-1]
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
