#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor
from random import randint
from hashlib import md5
from time import time

class SinaExtractor(BasicExtractor):
	'''
	新浪视频下载器
	'''
	def __init__(self,c):
		super(SinaExtractor,self).__init__(c, SINA)

	def download(self):
		print('sina:start downloading ...')
		retry = 3
		while retry >=0 :
			self.page = get_html(self.c.url)
			if self.page: break
			retry -= 1
		if not self.page:
			print('error: request video info error,check url. %s' % (self.c.url,))
			sys.exit(0)

		self.i.vid,self.vtype = self.getVid()
		if not self.i.vid:
			print('error: not find vid! exit...')
			sys.exit(0)

		#metadata = ...
		xml = dict()
		if self.vtype == 'vid':
			xml = self.getXml(self.i.vid)

		self.i.title = self.getTitle()
		self.i.desc = self.getDesc()
		self.i.keywords = self.getKeywords()
		self.i.fname = self.getFname()
		self.i.fsize = self.getFsize()
		self.i.duration = self.getDuration()
		self.i.category = self.getCategory()
		self.i.uptime = self.getUptime()
		self.i.m3u8 = self.query_m3u8()
		self.flvlist = self.query_real(xml = xml)
		self.realdown()

	def getXml(self,vid):
		rand = "0.{0}{1}".format(randint(10000, 10000000), randint(10000, 10000000))
		url = 'http://v.iask.com/v_play.php?vid={0}&ran={1}&p=i&k={2}'.format(vid,rand,self._get_k(vid,rand))
		xml = get_html(url)
		return xml

	def _get_k(self,vid, rand):
		t = str(int('{0:b}'.format(int(time()))[:-6], 2))
		return md5((vid + 'Z6prk18aWxP278cVAH' + t + rand).encode('utf-8')).hexdigest()[:16] + t

	def query_m3u8(self,*args,**kwargs):
		return ''

	def query_real(self,*args,**kwargs):
		xml = kwargs['xml']
		urls = []
		if self.vtype == 'vid':
			urls = re.findall(r'<url>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</url>',xml)
			#print(urls)
			return urls
		else:
			url = r'http://video.sina.com/v/flvideo/%s_0.flv' % (self.i.vid,)
			return [url]

	def getVid(self,*args,**kwargs):
		vid = ''
		r = re.search(r'hd_vid\s*\:\s*\'(\d+)\'',self.page)
		if r:
			vid = r.groups()[0]
		if vid == '0':
			r2 = re.search(r'vid\s*\:\s*\'(\d+)\'',self.page)
			if r2:
				vid = r2.groups()[0]
		if vid:
			return vid, 'vid'
		r3 = re.search(r'vkey\s*:\s*"([^"]+)"',self.page)
		if r3:
			vid = r3.groups()[0]
		return vid,'vkey'

	def getFsize(self,*args,**kwargs):
		return 1024*1024

	def getTitle(self,*args,**kwargs):
		title = ''
		r = re.search(r'title\s*:\s*\'([^\']+)\'',self.page)
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
		r = re.search(r'categoryID\s*\:\s*\'(\d+)\'',self.page)
		if r:
			cat = r.groups()[0]
		return cat

	def getDuration(self,*args,**kwargs):
		return 60

	def getUptime(self,*args,**kwargs):
		return INITIAL_UPTIME


def download(c):
	d = SinaExtractor(c)
	return d.download()