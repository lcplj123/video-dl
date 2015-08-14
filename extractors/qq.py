#!/usr/bin/env python3
import re
import sys
import json
import uuid
import random
import struct
sys.path.append('..')
from define import *
from utils import *
import base64
from extractor import BasicExtractor
import xml.etree.ElementTree as etree
import urllib.parse
import urllib.request

PLAYER_PLATFORM = 11 #pc平台
PLAYER_VERSION = '3.2.18.285'
ENCRYPTVER = '2.0'

User_Agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'
#swf地址
#http://cache.tv.qq.com/qqplayerout.swf?vid=...

class QQExtractor(BasicExtractor):
	'''
	腾讯视频下载器
	'''
	def __init__(self,c):
		super(QQExtractor,self).__init__(c, QQ)

	def download(self):
		print('qq:start downloading ...')
		retry = 3
		while retry >=0 :
			self.page = get_html(self.c.url)
			if self.page: break
			retry -= 1
		if not self.page:
			print('error: request video info error,check url. %s' % (self.c.url,))
			sys.exit(0)

		metadict = dict()
		r = re.search(r'var\s+VIDEO_INFO\s?=\s?({[^}]+})',self.page)
		if r:
			metadict = self._to_dict(r.groups()[0])
		self.i.vid = self.getVid(metadict = metadict)
		if not self.i.vid:
			print('error: not find vid! exit...')
			sys.exit(0)

		self.i.duration = self.getDuration(metadict = metadict)
		self.i.title = self.getTitle(metadict = metadict)
		self.i.fname = self.getFname()
		self.i.desc = self.getDesc()
		self.i.keywords = self.getKeywords()
		self.i.m3u8 = self.query_m3u8()
		self.i.category = self.getCategory()
		self.flvlist,self.i.fsize = self.query_real()
		self.realdown()


	def query_m3u8(self,*args,**kwargs):
		return ''

	def query_real(self,*args,**kwargs):
		url = r'http://vv.video.qq.com/geturl?vid=%s&otype=%s&platform=%d&ran=%s&defaultfmt=%s' % (self.i.vid,'json',11,str(random.random()),'fdh')
		jdata = get_html(url)
		start = jdata.find('=')
		js = json.loads(jdata[start+1:-1])
		#print(js)
		fsize = 0
		fsize = js['vd']['vi'][0]['fs']
		flvlist = []
		flvlist.append(js['vd']['vi'][0]['url'])
		return flvlist,fsize

	def getVid(self,*args,**kwargs):
		meta = kwargs['metadict']
		vid = ''
		vid = meta.get('vid')
		return vid

	def getFsize(self,*args,**kwargs):
		return 0

	def getTitle(self,*args,**kwargs):
		meta = kwargs['metadict']
		title = 'title'
		title = meta.get('title','title')
		return title

	def getDesc(self,*args,**kwargs):
		desc = self.i.title
		pattern = re.compile(r'\<meta\s+name=\"description\"\s+itemprop=\"description\"\s+content=\"(.*?)\"\s*/\>')
		r = pattern.search(self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def getKeywords(self,*args,**kwargs):
		tags = ''
		pattern = re.compile(r'\<meta\s+name=\"keywords\"\s+itemprop=\"keywords\"\s+content=\"(.*?)\"\s*/\>')
		r = pattern.search(self.page)
		if r:
			tags = r.groups()[0]
		return tags.split(',')

	def getCategory(self,*args,**kwargs):
		p1 = re.compile(r'target=\"_blanl\"\s+class=\"path_category\"\s+title=\"(.*?)\"')
		p2 = re.compile(r'class=\"breadcrumb_link\"\s+_hot=\"[a-zA-Z1-9.]+\"\s+title=\"(.*?)\"')
		r = p1.search(self.page)
		if r:
			return r.groups()[0]
		else:
			r2 = p2.search(self.page)
			if r2:
				return r2.groups()[0]
		return '未知'

	def getDuration(self,*args,**kwargs):
		meta = kwargs['metadict']
		t = 0
		t = meta.get('duration',0)
		return int(t)

	def getUptime(self,*args,**kwargs):
		return INITIAL_UPTIME

	def _to_dict(self,json_object):
		class global_dict(dict):
			def __getitem__(self, key):
				return key
		return eval(json_object, global_dict())

def download(c):
	d = QQExtractor(c)
	return d.download()