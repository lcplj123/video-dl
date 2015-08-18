#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor
from xml.dom.minidom import parseString

class TangDouExtractor(BasicExtractor):
	'''
	糖豆广场舞视频下载器
	'''
	def __init__(self,c):
		super(TangDouExtractor,self).__init__(c, TANGDOU)

	def download(self):
		print('tangdou:start downloading ...')
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

		url = r'http://p.bokecc.com/servlet/playinfo?vid=%s&pm=spark&m=1&pp=false&d=%s&fv=%s&version=20140214' % (self.i.vid,'www%2Etangdou%2Ecom','WIN%2018%2C0%2C0%2C209')
		metaxml = get_html(url)
		#print(metaxml)
		dom = parseString(metaxml)
		root = dom.documentElement
		video = root.getElementsByTagName('video')[0]
		if not video:
			print('get videos info error! exit...')
			sys.exit(0)

		self.i.title = self.getTitle()
		self.i.desc = self.getDesc()
		self.i.keywords = self.getKeywords()
		self.i.fname = self.getFname()
		self.i.fsize = self.getFsize()
		self.i.duration = self.getDuration(video = video)
		self.i.category = self.getCategory()
		self.i.uptime = self.getUptime()
		self.i.m3u8 = self.query_m3u8()
		self.flvlist = self.query_real(video = video)
		self.realdown()

	def query_m3u8(self,*args,**kwargs):
		return ''

	def query_real(self,*args,**kwargs):
		video = kwargs['video']
		qlist = video.getElementsByTagName('quality')
		t = qlist[-1]
		value = int(t.getAttribute('value'))
		for q in qlist:
			if value < int(q.getAttribute('value')):
				value = int(q.getAttribute('value'))
				t = q
		if not t: t = qlist[-1]
		c = t.getElementsByTagName('copy')[0]
		url = c.getAttribute('playurl')
		return [url]

	def getVid(self,*args,**kwargs):
		vid = ''
		r = re.search(r'vid:\s*\"([A-Z0-9]+)\"',self.page)
		if r:
			vid = r.groups()[0]
		return vid

	def getFsize(self,*args,**kwargs):
		return 1024*1024

	def getTitle(self,*args,**kwargs):
		title = ''
		r = re.search(r'\<h1\>(.*?)\</h1\>',self.page)
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
		return '广场舞'

	def getDuration(self,*args,**kwargs):
		video = kwargs['video']
		t = video.getAttribute('duration')
		return int(t) if t else 60

	def getUptime(self,*args,**kwargs):
		return INITIAL_UPTIME


def download(c):
	d = TangDouExtractor(c)
	return d.download()