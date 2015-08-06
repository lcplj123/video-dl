#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor

class Ku6Extractor(BasicExtractor):
	'''
	ku6下载器
	'''
	def __init__(self,c):
		super(Ku6Extractor,self).__init__(c, KU6)

	def download(self):
		print('ku6:start downloading ...')
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


	def query_m3u8(self,*args,**kwargs):
		pass

	def query_real(self,*args,**kwargs):
		pass

	def getVid(self,*args,**kwargs):
		pass

	def getFname(self,*args,**kwargs):
		fname = ''
		if self.c.nametype == 'title':
			fname = '%s.%s' % (self.i.title[:32],self.c.ext)
		else:
			fname = '%s.%s' % (self.i.vid,self.c.ext)
		return fname

	def getFsize(self,*args,**kwargs):
		pass

	def getTitle(self,*args,**kwargs):
		pass

	def getDesc(self,*args,**kwargs):
		pass

	def getTags(self,*args,**kwargs):
		pass

	def getViews(self,*args,**kwargs):
		pass

	def getCategory(self,*args,**kwargs):
		pass

	def getDuration(self,*args,**kwargs):
		pass

	def getUptime(self,*args,**kwargs):
		pass


def download(c):
	d = Ku6Extractor(c)
	return d.download()