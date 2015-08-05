#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from random import random
import urllib.parse
from extractor import BasicExtractor

class SoHuExtractor(BasicExtractor):
	'''
	sohu 下载器
	'''
	def __init__(self,c):
		super(SoHuExtractor,self).__init__(c, SOHU)

	def download(self):
		print('sohu:start downloading ...')
		retry = 3
		while retry >=0 :
			self.page = get_html(self.c.url)
			if self.page: break
			retry -= 1
		if not self.page:
			print('error: request video info error,check url. %s' % (self.c.url,))
			sys.exit(0)

		self.i.vid = self.getVid()
		if not self.i.vid:
			#再一次检查，看url中是否含有vid
			r = re.search(r'vid=(\d+)&*',self.c.url)
			if r:
				self.i.vid = r.groups()[0]
			else:
				print('error: not find vid! exit...')
				sys.exit(0)

		if re.match(r'http://tv.sohu.com/', self.c.url):
			_url = r'http://hot.vrs.sohu.com/vrs_flash.action?vid=%s' % (self.i.vid,)
			jdata = get_html(_url)
			js = json.loads(jdata)
			#print(js)
			for streamtype in ('oriVid','superVid','highVid','norVid','relativeId'):
				svid = js['data'][streamtype] #获取最高清的视频
				if svid == self.i.vid: break
				if svid != 0 and svid != self.i.vid:
					reurl = r'http://hot.vrs.sohu.com/vrs_flash.action?vid=%s' % (svid,)
					js = json.loads(get_html(reurl))
					self.i.vid = svid
					break
		else:
			url = r'http://my.tv.sohu.com/play/videonew.do?vid=%s&referer=http://my.tv.sohu.com' % (self.i.vid,)
			jdata =get_html(url)
			js = json.loads(jdata)

			#print(js)

		self.i.title = self.getTitle(js = js)
		self.i.desc = self.getDesc()
		self.i.tags = self.getTags(js = js)
		self.i.duration = self.getDuration(js = js)
		self.i.category = self.getCategory(js = js)
		self.i.fsize = self.getFsize(js = js)
		self.i.fname = self.getFname()
		self.i.views = self.getViews()
		self.i.username,self.i.userid = self.getUser()
		self.flvlist = self.query_real(js = js)
		self.i.m3u8 = self.query_m3u8()

		ret = checkCondition(self.i,self.c)
		if ret == C_PASS:
			if not realDownload(self.flvlist,self.tmppath):
				sys.exit(0)
			#下载成功，合并视频，并删除临时文件
			if not mergeVideos(self.flvlist, self.tmppath, self.i.path, self.i.fname):
				sys.exit(0)

			self.jsonToFile()
		else:
			print('tips: video do not math conditions. code = %d' % (ret,))
			sys.exit(0)

	def _real_url(self,host,vid,tvid,new,clipURL,ck):
		url = 'http://'+host+'/?prot=9&prod=flash&pt=1&file='+clipURL+'&new='+new +'&key='+ ck+'&vid='+str(vid)+'&uid='+str(int(time.time()*1000))+'&t='+str(random())
		return json.loads(get_html(url))['url']

	def query_m3u8(self,*args,**kwargs):
		return ''

	def query_real(self,*args,**kwargs):
		js = kwargs['js']
		host = js['allot']
		prot = js['prot']
		tvid = js['tvid']
		flvlist = []
		if len(js['data']['clipsURL']) != len(js['data']['su']):
			print('error: internal error! exit...')
			sys.exit(0)
		for new,clip,ck in zip(js['data']['su'],js['data']['clipsURL'],js['data']['ck']):
			clipURL = urllib.parse.urlparse(clip).path
			flvlist.append(self._real_url(host,self.i.vid,tvid,new,clipURL,ck))

		return flvlist

	def getVid(self,*args,**kwargs):
		vid = ''
		pattern = re.compile(r'\Wvid\s*[\:=]\s*[\'"]?(\d+)[\'"]?')
		r = pattern.search(self.page)
		if r:
			vid = r.groups()[0]
		return vid

	def getFsize(self,*args,**kwargs):
		js = kwargs['js']
		return int(js['data']['totalBytes'])

	def getTitle(self,*args,**kwargs):
		js = kwargs['js']
		return js['data']['tvName']

	def getDesc(self,*args,**kwargs):
		desc = self.i.title
		pattern = re.compile(r'\<meta\s+name=\"description\"\s+content\s*=\s*\"(.*?)\"\s*/\>')
		r = pattern.search(self.page)
		if r:
			desc = r.groups()[0]
		return desc


	def getTags(self,*args,**kwargs):
		js = kwargs['js']
		kw = js['keyword']
		return kw.split(';')

	def getViews(self,*args,**kwargs):
		url = r'http://count.vrs.sohu.com/count/queryext.action?vids=%s' % (self.i.vid,)
		jdata = get_html(url)
		js = json.loads(jdata[6:-1])
		return js[str(self.i.vid)]['total'] + 1

	def getUser(self,*args,**kwargs):
		return '',''

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		js = kwargs['js']
		cat = js['caname']
		return cat

	def getDuration(self,*args,**kwargs):
		js = kwargs['js']
		return int(js['data']['totalDuration'])

	def getUptime(self,*args,**kwargs):
		pass

def download(c):
	d = SoHuExtractor(c)
	return d.download()