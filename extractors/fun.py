#!/usr/bin/env python3
import re
import sys
import json
import time
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor

class FunExtractor(BasicExtractor):
	'''
	风行视频下载器
	'''
	def __init__(self,c):
		super(FunExtractor,self).__init__(c, FUN)

	def download(self):
		print('fun:start downloading ...')
		retry = 3
		while retry > 0 :
			self.page = get_html(self.c.url)
			if self.page: break
			retry -= 1
		if not self.page:
			print('error: request video info error,check url. %s' % (self.c.url,))
			sys.exit(0)

		self.i.vid = self.getVid()
		if not self.i.vid:
			print('error: not find vid! exit...')
			sys.exit(0)

		#metadata = ...
		url = r'http://api1.fun.tv/ajax/playinfo/video/%s/' % (self.i.vid,)
		info = json.loads(get_html(url))
		#print(info)
		if info['status'] != 200:
			print('error; get video info error! %s' % (info,))
			sys.exit(0)

		files = info['data']['files']
		sortedf =sorted(files,key = lambda item: item['filesize'],reverse = True)
		#print(sortedf)
		exctF = sortedf[0]

		name = exctF.get('filename')
		hashid = exctF.get('hashid')

		self.i.title = self.getTitle(sortedf = exctF)
		self.i.desc = self.getDesc()
		self.i.keywords = self.getKeywords()
		self.i.fname = self.getFname()
		self.i.fsize = self.getFsize(sortedf = exctF)
		self.i.duration = self.getDuration()
		self.i.category = self.getCategory()
		self.i.uptime = self.getUptime()
		self.i.m3u8 = self.query_m3u8()
		self.flvlist = self.query_real(sortedf = exctF)
		self.realdown()

	def query_m3u8(self,*args,**kwargs):
		return ''

	def query_real(self,*args,**kwargs):
		sf = kwargs['sortedf']
		hashid = sf.get('hashid')
		t = int(time.time())
		fname = sf.get('filename')
		url = r'http://jobsfe.funshion.com/query/v1/mp4/%s.json?file=%s&clifz=fun&mac=&tm=%d' % (hashid,fname,t)
		#print(url)
		info = json.loads(get_html(url))
		#print(info)
		if info['return'] != 'succ':
			return []
		return info['playlist'][0]['urls']

	def getVid(self,*args,**kwargs):
		vid = ''
		r = re.search(r'fun\.tv/vplay/[a-z]{1}-(\d+)/',self.c.url)
		if r:
			vid = r.groups()[0]
		else:
			r2 = re.search(r'fun\.tv/vplay/[a-z]{1}-[1-9.a-z]{1,}-[1-9.a-z]{1,}-[1-9.a-z]{1,}-(\d+)/',self.c.url)
			if r2:
				vid = r2.groups()[0]
		print(vid)
		return vid

	def getFsize(self,*args,**kwargs):
		sf = kwargs['sortedf']
		return sf.get('filesize',1024*1024)

	def getTitle(self,*args,**kwargs):
		sf = kwargs['sortedf']
		title = sf.get('name_cn')
		if not title:
			r = re.search(r'\<title\>(.*?)\<title\>',self.page)
			if r:
				title = r.groups()[0][:-4]
		return title

	def getDesc(self,*args,**kwargs):
		desc = self.i.title
		r = re.search(r'\<meta\s+name=\"Description\"\s+content=\"(.*?)\"',self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def getKeywords(self,*args,**kwargs):
		keywords = ''
		r = re.search(r'\<meta\s+name=\"keywords\"\s+content=\"(.*?)\"',self.page)
		if r:
			keywords = r.groups()[0]
		return keywords.split(',')

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		return cat

	def getDuration(self,*args,**kwargs):
		return 60

	def getUptime(self,*args,**kwargs):
		return INITIAL_UPTIME


def download(c):
	d = FunExtractor(c)
	return d.download()