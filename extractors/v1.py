#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor

class V1Extractor(BasicExtractor):
	'''
	v1视频下载器
	'''
	def __init__(self,c):
		super(V1Extractor,self).__init__(c, V1)

	def download(self):
		print('v1:start downloading ...')
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
			print('error: not find vid! exit...')
			sys.exit(0)

		#metadata = ...
		self.i.title = self.getTitle(...)
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
		r = re.search(r'videoUrl=(.*\.(?:flv|f4v|mp4))',self.page)
		if r:
			urls.append(r.groups()[0])
		return urls

	def getVid(self,*args,**kwargs):
		vid = ''
		r = re.search(r'v1\.cn/video/v_(\d+)\.jhtml',self.c.url)
		if r:
			vid = r.groups()[0]
		else:
			r = re.search(r'v1\.cn/\d{4}-\d{2}-\d{2}/(\d+)\.shtml',self.c.url)
			if r:
				vid = r.groups()[0]
		return vid

	def getFsize(self,*args,**kwargs):
		return 1024*1024

	def getTitle(self,*args,**kwargs):
		title = ''
		r = re.search(r'\<meta\s+name=\"title\"\s+content=\"(.*?)\"',self.page)
		if r:
			title = r.groups()[0]
		return title

	def getDesc(self,*args,**kwargs):
		desc = self.i.title
		r = re.search(r'\<meta\s+name=\"description\"\s+content=\"(.*?)\"',self.page)
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
		t = ''
		r = re.search(r'v1\.cn/(\d{4}-\d{2}-d{2})/\d+\.shtml',self.c.url)
		if r:
			t = r.groups()[0]
			return t.replace('-','')

		return INITIAL_UPTIME


def download(c):
	d = V1Extractor(c)
	return d.download()