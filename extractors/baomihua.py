#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor
import urllib.parse

class BaoMiHuaExtractor(BasicExtractor):
	'''
	爆米花视频下载器
	'''
	def __init__(self,c):
		super(BaoMiHuaExtractor,self).__init__(c, BAOMIHUA)

	def download(self):
		print('baomihua:start downloading ...')
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

		url = r'http://play.baomihua.com/getvideourl.aspx?flvid=%s' % (self.i.vid,)
		html = get_html(url)
		info = '&%s&' % (urllib.parse.unquote_plus(html),)
		self.i.title = self.getTitle(info = info)
		self.i.desc = self.getDesc(info = info)
		self.i.keywords = self.getKeywords(info = info)
		self.i.m3u8 = self.query_m3u8(info = info)
		self.i.fsize = self.getFsize(info = info)
		self.i.fname = self.getFname()
		self.flvlist = self.query_real(info = info)
		self.i.uptime = self.getUptime(info = info)
		self.i.category = self.getCategory(info = info)
		self.i.duration = self.getDuration(info = info)
		self.realdown()

	def query_m3u8(self,*args,**kwargs):
		m3u8 = ''
		info = kwargs['info']
		r = re.search(r'&hlshost=(.*?)&',info)
		if r:
			m3u8 = r.groups()[0]
		return m3u8

	def query_real(self,*args,**kwargs):
		urls = []
		info = kwargs['info']
		host = ''
		stream_name = ''
		stream_type = ''
		r = re.search('&host=(.*?)&',info)
		if r:
			host = r.groups()[0]
		r2 = re.search('&stream_name=(.*?)&',info)
		if r2:
			stream_name = r2.groups()[0]
		r3 = re.search('&videofiletype=(.*?)&',info)
		if r3:
			stream_type = r3.groups()[0]

		url = r'http://%s/pomoho_video/%s.%s' % (host,stream_name,stream_type)
		return [url]

	def getVid(self,*args,**kwargs):
		vid = ''
		r = re.search(r'var\s+flvid\s*=\s*(\d+)',self.page)
		if r:
			vid = r.groups()[0]
		else:
			r2 = re.search(r'flvid=(\d+)',self.page)
			if r2:
				vid = r2.groups()[0]
		return vid

	def getFsize(self,*args,**kwargs):
		size = 1024*1024
		info = kwargs['info']
		r = re.search(r'&videofilesize=(\d+)&',info)
		if r:
			size = r.groups()[0]
		return int(size)

	def getTitle(self,*args,**kwargs):
		title = ''
		info = kwargs['info']
		r = re.search(r'&title=(.*?)&',info)
		if r:
			title = r.groups()[0]
		return title

	def getDesc(self,*args,**kwargs):
		desc = self.i.title
		r = re.search(r'\<meta\s+content=\"(.*?)\"\s+name=\"description\"',self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def getKeywords(self,*args,**kwargs):
		tag = ''
		r = re.search(r'\<meta\s+content=\"(.*?)\"\s+name=\"keywords\"',self.page)
		if r:
			tag = r.groups()[0]
		return tag.split(',')

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		return cat

	def getDuration(self,*args,**kwargs):
		duration = 0
		info = kwargs['info']
		r = re.search(r'&totaltime=(\d+)&',info)
		if r:
			duration = r.groups()[0]
		return int(duration)

	def getUptime(self,*args,**kwargs):
		return INITIAL_UPTIME


def download(c):
	d = BaoMiHuaExtractor(c)
	return d.download()