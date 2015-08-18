#!/usr/bin/env python3
import re
import sys
import json
import time
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor

class MiaoPaiExtractor(BasicExtractor):
	'''
	秒拍视频下载器
	'''
	def __init__(self,c):
		super(MiaoPaiExtractor,self).__init__(c, MIAOPAI)

	def download(self):
		print('miaopai:start downloading ...')
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

		url = r'http://api.miaopai.com/m/v2_channel.json?scid=%s&vend=miaopai&fillType=259' % (self.i.vid,)
		info = json.loads(get_html(url))
		if info['status'] != 200:
			print('error: request info wrong.exit...')
			sys.exit(0)

		self.i.title = self.getTitle(info = info)
		self.i.desc = self.getDesc(info = info)
		self.i.keywords = self.getKeywords(info = info)
		self.i.duration = self.getDuration(info = info)
		self.i.category = self.getCategory(info = info)
		self.i.fname = self.getFname()
		self.i.fsize = self.getFsize(info = info)
		self.flvlist = self.query_real(info = info)
		self.i.m3u8 = self.query_m3u8(info = info)
		self.i.uptime = self.getUptime(info = info)
		self.realdown()


	def query_m3u8(self,*args,**kwargs):
		m3u8 = ''
		return m3u8

	def query_real(self,*args,**kwargs):
		info = kwargs['info']
		base = info['result']['stream']['base']
		return [base]

	def getVid(self,*args,**kwargs):
		vid = ''
		r = re.search(r'/show/(.*?)\.htm',self.c.url)
		if r:
			vid = r.groups()[0]
		return vid

	def getFsize(self,*args,**kwargs):
		return 1024*1024

	def getTitle(self,*args,**kwargs):
		info = kwargs['info']
		return info['result']['ext']['t']

	def getDesc(self,*args,**kwargs):
		desc = self.i.title
		r = re.search(r'\<meta\s+name=\"description\"\s+content=\"(.*?)\"',self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def getKeywords(self,*args,**kwargs):
		tag = []
		info = kwargs['info']
		tag = info['result']['topicinfo']
		if not tag:
			r = re.search(r'\<meta\s+name=\"keywords\"\s+content=\"(.*?)\"',self.page)
			if r:
				g = r.groups()[0]
				tag = g.split(',')
		return tag

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		return cat

	def getDuration(self,*args,**kwargs):
		info = kwargs['info']
		return info['result']['ext']['length']

	def getUptime(self,*args,**kwargs):
		info = kwargs['info']
		t = info['result']['ext']['finishTime']
		lt = time.localtime(int(t/1000))
		return int(time.strftime('%Y%m%d',lt))


def download(c):
	d = MiaoPaiExtractor(c)
	return d.download()