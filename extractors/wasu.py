#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor
from xml.dom.minidom import parseString

class WasuExtractor(BasicExtractor):
	'''
	华数视频下载器
	'''
	def __init__(self,c):
		super(WasuExtractor,self).__init__(c, WASU)

	def download(self):
		print('wasu:start downloading ...')
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
		#self.realdown()

	def query_m3u8(self,*args,**kwargs):
		return ''

	def query_real(self,*args,**kwargs):
		xml_url = r'http://www.wasu.cn/Api/getPlayInfoById/id/%s/datatype/xml' % (self.i.vid,)
		dom = parseString(get_html(xml_url))
		root = dom.documentElement
		mp4tab = root.getElementsByTagName('mp4')[0]
		_url = ''
		for i in (5,4,3,2,1):
			_name = 'hd%d' % (i,)
			hdx = mp4tab.getElementsByTagName(_name)
			if hdx and hdx[0]:
				_url = hdx[0].firstChild.data

		_key = ''
		r = re.search(r'_playKey\s*=\s*\'(.*?)\'',self.page)
		if r:
			_key = r.groups()[0]

		urls = self.getDecodeUrl(_url,_key)
		return []

	def getDecodeUrl(self,_url,_key):
		pass

	def getVid(self,*args,**kwargs):
		vid = ''
		r = re.search(r'wasu\.cn/Play/show/id/(\d+)',self.c.url)
		if r:
			vid = r.groups()[0]
		else:
			r2 = re.search(r'_playId\s*=\s*\'(\d+)\'',self.page)
			if r2:
				vid = r2.groups()[0]
		return vid

	def getFsize(self,*args,**kwargs):
		return 1024*1024

	def getTitle(self,*args,**kwargs):
		title = ''
		r = re.search(r'_playTitle\s*=\s*\'(.*?)\'',self.page)
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
		return keywords.split(' ')

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		r = re.search(r'playCatName\s*=\s*\'(.*?)\'',self.page)
		if r:
			cat = r.groups()[0]
		return cat

	def getDuration(self,*args,**kwargs):
		t = '60'
		r = re.search(r'_playDuration\s*=\s*\'(\d+)\'',self.page)
		if r:
			r.groups()[0]
		return int(t)

	def getUptime(self,*args,**kwargs):
		return INITIAL_UPTIME


def download(c):
	d = WasuExtractor(c)
	return d.download()