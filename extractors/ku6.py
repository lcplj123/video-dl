#!/usr/bin/env python3
import re
import sys
import json
import time
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor

RATE_LIST = (1500,799,450,299)

class Ku6Extractor(BasicExtractor):
	'''
	ku6下载器
	'''
	def __init__(self,c):
		super(Ku6Extractor,self).__init__(c, KU6)

	def download(self):
		print('youku:start downloading ...')
		retry = 3
		while retry >=0 :
			self.page = get_html(self.c.url)
			if self.page: break
			retry -= 1
		if not self.page:
			print('error: request video info error,check url. %s' % (self.c.url,))
			sys.exit(0)

		self.i.vid = self.getVid(url = self.c.url)
		if not self.i.vid:
			print('error: not find vid! exit...')
			sys.exit(0)

		#两个url均可以获取到视频信息
		url = r'http://v.ku6.com/fetchVideo4Player/%s.html' % (self.i.vid,)
		#url2 = r'http://v.ku6.com/fetch.htm?t=getVideo4Player&vid=%s' % (self.i.vid,)
		js = json.loads(get_html(url))
		if js.get('status') != 1:
			print('error: video maye be removed! exit...')
			sys.exit(0)

		self.flvlist = self.query_real(js = js)
		self.i.title = self.getTitle(js = js)
		self.i.keywords = self.getKeywords(js = js)
		self.i.desc = self.getDesc(js = js)
		self.i.fsize = self.getFsize(js = js)
		self.i.fname = self.getFname(js = js)
		self.i.duration = self.getDuration(js = js)
		self.i.uptime = self.getUptime(js = js)
		self.realdown()


	def query_m3u8(self,*args,**kwargs):
		pass

	def query_real(self,*args,**kwargs):
		js = kwargs['js']
		fstr = js['data']['f']
		flvlist = fstr.split(',')
		newlist = []
		for flv in flvlist:
			_flv = '%s?rate=%d' % (flv,RATE_LIST[0])
			newlist.append(_flv)
		return newlist

	def getVid(self,*args,**kwargs):
		url = kwargs['url']
		p1 = re.search(r'v\.ku6\.com/show/(.*?)\.html',url)
		if p1:
			return p1.groups()[0]
		else:
			p2 = re.search(r'v\.ku6\.com/special/show_\d+/(.*?)\.html')
			if p2:
				return p2.groups()[0]
			else:
				return ''
		return ''

	def getFsize(self,*args,**kwargs):
		size = 0
		js = kwargs['js']
		size = js['data']['videosize']
		index = size.find('@')
		if index != -1:
			return int(size[index+1:])
		return int(size)

	def getTitle(self,*args,**kwargs):
		js = kwargs['js']
		title = ''
		title = js['data']['t']
		return title

	def getDesc(self,*args,**kwargs):
		js = kwargs['js']
		desc = self.i.title
		desc = js['data']['desc']
		return desc

	def getKeywords(self,*args,**kwargs):
		tag = ''
		js = kwargs['js']
		tag =  js['data']['tag']
		return tag.split('/')

	def getCategory(self,*args,**kwargs):
		pass

	def getDuration(self,*args,**kwargs):
		t = 0
		js = kwargs['js']
		sizelist = str(js['data']['vtime']).split(',')
		for s in sizelist:
			t += int(s)
		return t

	def getUptime(self,*args,**kwargs):
		js = kwargs['js']
		t = int(js['data']['uploadtime'])
		localt = time.localtime(t)
		return int(time.strftime('%Y%m%d',localt))


def download(c):
	d = Ku6Extractor(c)
	return d.download()