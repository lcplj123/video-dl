#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor
from extractors import sohu

class WoLeExtractor(BasicExtractor):
	'''
	56视频下载器
	'''
	def __init__(self,c):
		super(WoLeExtractor,self).__init__(c, WOLE)

	def download(self):
		print('56:start downloading ...')
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

		#跳转到sohu下载
		sohu_url = ''
		r = re.search(r'url\s*\:\s*\'(http\://my\.tv\.sohu\.com/.*?\.shtml)\'',self.page)
		if r:
			#print(r.groups()[0])
			sohu_url = r.groups()[0]
		else:
			print('error: cannot download video.exut...')
			sys.exit(0)

		#metadata = ...
		#self.i.title = self.getTitle(...)
		#self.i.desc = self.getDesc()
		#self.i.keywords = self.getKeywords()
		#self.i.fname = self.getFname()
		#self.i.fsize = self.getFsize()
		#self.i.duration = self.getDuration()
		#self.i.category = self.getCategory()
		#self.i.uptime = self.getUptime()
		#self.i.m3u8 = self.query_m3u8()
		#self.flvlist = self.query_real()
		#self.realdown()
		self.c.url = sohu_url
		sohu.download(self.c)

	def query_m3u8(self,*args,**kwargs):
		pass

	def query_real(self,*args,**kwargs):
		pass

	def getVid(self,*args,**kwargs):
		return '000000'

	def getFsize(self,*args,**kwargs):
		pass

	def getTitle(self,*args,**kwargs):
		pass

	def getDesc(self,*args,**kwargs):
		pass

	def getKeywords(self,*args,**kwargs):
		pass

	def getCategory(self,*args,**kwargs):
		pass

	def getDuration(self,*args,**kwargs):
		pass

	def getUptime(self,*args,**kwargs):
		pass


def download(c):
	d = WoLeExtractor(c)
	return d.download()