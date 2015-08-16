#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor

class AcFunExtractor(BasicExtractor):
	'''
	acfun视频下载器
	'''
	def __init__(self,c):
		super(AcFunExtractor,self).__init__(c, ACFUN)

	def download(self):
		print('acfun:start downloading ...')
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

		self.i.title = self.getTitle()
		self.i.desc = self.getDesc()
		self.i.keywords = self.getKeywords()
		self.i.username,self.i.userid = self.getUser()
		self.i.uptime = self.getUptime()
		self.i.fname = self.getFname()

		sUrl = r'http://www.acfun.tv/video/getVideo.aspx?id=%s' % (self.i.vid,)
		js = json.loads(get_html(sUrl))
		sourcetype = js['sourceType']
		sourceid = js['sourceId']

		if sourcetype == 'letv':
			k = '2d8c027396'
		elif sourcetype == 'youku':
			pass
		elif sourcetype == 'sina':
			pass
		elif sourcetype == 'tudou':
			pass
		elif sourcetype == 'qq':
			pass
			print(js['sourceType'])

	def query_m3u8(self,*args,**kwargs):
		pass

	def query_real(self,*args,**kwargs):
		pass

	def getVid(self,*args,**kwargs):
		vid = ''
		pattern = re.compile(r'data-vid=\"(\d+)\"')
		r = pattern.search(self.page)
		if r:
			vid = r.groups()[0]
		print(vid)
		return vid

	def getFsize(self,*args,**kwargs):
		pass

	def getTitle(self,*args,**kwargs):
		title = ''
		pattern = re.compile(r'data-title\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			title = r.groups()[0]
		return title

	def getDesc(self,*args,**kwargs):
		desc = self.i.title
		r = re.search(r'\<meta\s+name=\"description\"\s+content=\"([\s\S]+?)\"\>',self.page)
		if r:
			desc = r.groups()[0]
			desc = desc.replace('<br/>',' ')
		return desc

	def getKeywords(self,*args,**kwargs):
		tags = ''
		pattern = re.compile(r'data-tags\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			tags = r.groups()[0]

		return tags.split(',')

	def getUser(self,*args,**kwargs):
		uid = ''
		name = ''
		r1 = re.search(r'data-uid\s*=\s*\"(.*?)\"',self.page)
		if r1:
			uid = r1.groups()[0]
		r2 = re.search(r'data-name\s*=\s*\"(.*?)\"',self.page)
		if r2:
			name = r2.groups()[0]
		return name,uid

	def getCategory(self,*args,**kwargs):
		pass

	def getDuration(self,*args,**kwargs):
		pass

	def getUptime(self,*args,**kwargs):
		t = ''
		pattern = re.compile(r'data-date\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			x = r.groups()[0][:10]
			t = x.replace('-','')
		return t


def download(c):
	d = AcFunExtractor(c)
	return d.download()