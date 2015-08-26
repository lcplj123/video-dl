#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor
import base64

class YinYueTaiExtractor(BasicExtractor):
	'''
	音悦台视频下载器
	'''
	def __init__(self,c):
		super(YinYueTaiExtractor,self).__init__(c, YINYUETAI)

	def download(self):
		print('yinyuetai:start downloading ...')
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

		self.i.title = self.getTitle()
		self.i.desc = self.getDesc()
		self.i.keywords = self.getKeywords()
		self.i.fname = self.getFname()
		self.i.fsize = self.getFsize()
		self.i.duration = self.getDuration()
		self.i.category = self.getCategory()
		self.i.uptime = self.getUptime()
		self.i.m3u8 = self.query_m3u8()
		self.flvlist = self.query_real()
		self.realdown()

	def query_m3u8(self,*args,**kwargs):
		return ''

	def query_real(self,*args,**kwargs):
		urls = []
		htm = get_html('http://www.yinyuetai.com/insite/get-video-info?flex=true&videoId=' + self.i.vid)
		#print(str(htm))
		for quality in ('he\w*', 'hd\w*', 'hc\w*', '\w+'):
			r = re.search(r'(http://' + quality + '\.yinyuetai\.com/uploads/videos/common/\w+\.(?:flv|mp4)\?(?:sc=[a-f0-9]{16}|v=\d{12}))', str(htm))
			if r:
				urls.append(r.groups()[0])
				break
		return urls

	def getVid(self,*args,**kwargs):
		vid = ''
		r = re.search(r'yinyuetai\.com/video/(\d+)\?',self.c.url)
		if r:
			vid = r.groups()[0]
		return vid

	def getFsize(self,*args,**kwargs):
		return 1024*1024

	def getTitle(self,*args,**kwargs):
		title = ''
		r = re.search(r'<meta property="og:title"\s+content="([^"]+)"/>',self.page)
		if r:
			title = r.groups()[0]
		return title

	def getDesc(self,*args,**kwargs):
		desc = self.i.title
		r = re.search(r'<meta property="og:description"\s+content="([^"]+)"/>',self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def getKeywords(self,*args,**kwargs):
		keywords = ''
		r = re.search(r'<meta property="og:keywords"\s+content="([^"]+)"/>',self.page)
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
	d = YinYueTaiExtractor(c)
	return d.download()