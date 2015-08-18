#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor

ha = {'Host':'pcfastvideo.imgo.tv','Referer':'http://i1.hunantv.com/ui/swf/player/v0813/main.swf','User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'}

class HunanExtractor(BasicExtractor):
	'''
	芒果TV视频下载器
	'''
	def __init__(self,c):
		super(HunanExtractor,self).__init__(c, HUNANTV)

	def download(self):
		print('mango:start downloading ...')
		retry = 3
		while retry >=0 :
			self.page = get_html(self.c.url,header = {'Referer':'http://www.hunantv.com/'})
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
		url = r'http://v.api.hunantv.com/player/video?video_id=%s' % (self.i.vid,)
		jdata = json.loads(get_html(url))
		if jdata['status'] != 200:
			print('request video info error! exit...')
			sys.exit(0)


		self.i.title = self.getTitle(jdata = jdata['data'])
		self.i.desc = self.getDesc(jdata = jdata['data'])
		self.i.keywords = self.getKeywords()
		self.i.fname = self.getFname()
		self.i.fsize = self.getFsize()
		self.i.duration = self.getDuration()
		self.i.category = self.getCategory(jdata = jdata['data'])
		self.i.uptime = self.getUptime()
		self.i.m3u8 = self.query_m3u8()
		self.flvlist = self.query_real(jdata = jdata['data'])
		self.realdown(header = ha)

	def query_m3u8(self,*args,**kwargs):
		return ''

	def query_real(self,*args,**kwargs):
		jdata = kwargs['jdata']
		stream = jdata['stream'][-1]
		url = stream['url']
		js = json.loads(get_html(url))
		if js['status'] != 'ok':
			print('request video info error. exit...')
			sys.exit(0)
		info_url = js['info']
		return [info_url]

	def getVid(self,*args,**kwargs):
		vid = ''
		r = re.search(r'vid\s*\:\s*(\d+)',self.page)
		if r:
			vid = r.groups()[0]
		return vid

	def getFsize(self,*args,**kwargs):
		return 1024*1024

	def getTitle(self,*args,**kwargs):
		title = ''
		jdata = kwargs['jdata']
		title = jdata['info']['title']
		if title: return title

		r = re.search(r'title\s*\:\s*\"(.*?)\"',self.page)
		if r:
			title = r.groups()[0]
		else:
			r2 = re.search(r'\<title\>(.*?)\</title\>',self.page)
			if r2:
				title = r2.groups()[0]
		return title

	def getDesc(self,*args,**kwargs):
		desc = self.i.title
		jdata = kwargs['jdata']
		desc = jdata['info']['desc']
		if desc: return desc
		r = re.search(r'\<meta\s+name=\"description\"\s+content=\"(.*?)\"',self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def getKeywords(self,*args,**kwargs):
		keywords = ''
		r = re.search(r'keywords\s*\:\s*\"(.*?)\"',self.page)
		if r:
			keywords = r.groups()[0]
		return keywords.split(',')

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		jdata = kwargs['jdata']
		cat = jdata['info']['root_name']
		if cat: return cat
		r = re.search(r'type\s*\:\s*\"(.*?)\"',self.page)
		if r:
			cat = r.groups()[0]
		return cat

	def getDuration(self,*args,**kwargs):
		jdata = kwargs['jdata']
		t = jdata['info']['duration']
		return int(t)

	def getUptime(self,*args,**kwargs):
		t = ''
		r = re.search(r'release_date\s*\:\s*\"(.*?)\"',self.page)
		if r:
			t = r.groups()[0]
		return t.replace('-','')


def download(c):
	d = HunanExtractor(c)
	return d.download()