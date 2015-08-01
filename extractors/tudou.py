#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor


class TuDouExtractor(BasicExtractor):
	'''
	土豆视频下载器
	'''
	def __init__(self,c):
		super(TuDouExtractor,self).__init__(c,TUDOU)

	def download(self):
		'''
		下载入口
		'''
		print('start downloading ...')
		retry = 3
		while retry >=0 :
			self.page = get_html(self.c.url)
			if self.page: break
			retry -= 1
		if not self.page:
			print('error: request video info error,check url. %s' % (self.c.url,))
			sys.exit(0)

		pattern = re.compile(r'vcode\s*[:=]\s*\'([^\']+)\'')
		r = pattern.search(self.page)
		if r:
			vcode = r.groups()[0]
			youku_url = r'http://v.youku.com/v_show/id_%s.html' % (vcode,)
			self.c.url = youku_url
			from extractors.youku import download
			download(self.c)
		else:
			self._download()

	def _download(self):

		js = None
		pattern = re.compile(r'segs:\s*\'(\{.*?\})\'')
		r = pattern.search(self.page)
		if r:
			js = json.loads(r.groups()[0])
		else:
			url = r'http://www.tudou.com/outplay/goto/getItemSegs.action?iid=%'
			data = get_html(url)

		if not js:
			print('regret: unsupported url. %s' % (self.c.url,))
			sys.exit(0)

	def _getIID(self):
		iid = ''
		pattern = re.compile(r'iid\s*[:=]\s*(\S+)')
		r = pattern.search(self.page)
		if r:
			print(r)
			iid = r.groups()[0]
		return iid


	def query_m3u8(self,*args,**kwargs):
		js = kwargs['js']


	def query_real(self,*args,**kwargs):
		pass

	def getVid(self,*args,**kwargs):
		pass

	def getFsize(self,*args,**kwargs):
		pass

	def getFname(self,*args,**kwargs):
		pass

	def getTitle(self,*args,**kwargs):
		title = ''
		pattern = re.compile(r'\<meta\s+name\s*=\s*\"irTitle\"\s+content\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			title = r.groups()[0]
		if not title:
			pattern = re.compile(r'kw\s*[:=]\s*[\'\"]([^\n]+?)\'\s*\n')
			r = pattern.search(self.page)
			if r:
				title = r.groups()[0]
		return title

	def getDesc(self,*args,**kwargs):
		desc = ''
		pattern = re.compile(r'\<meta\s+name\s*=\s*\"description\"\s+content\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def getTags(self,*args,**kwargs):
		tags = ''
		pattern = re.compile(r'\<meta\s+name\s*=\s*\"keywords\"\s+content\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			tags = r.groups()[0]
		return tags.split(' ')

	def getUsername(self,*args,**kwargs):
		pass

	def getUserid(self,*args,**kwargs):
		pass

	def getViews(self,*args,**kwargs):
		pass

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		pattern = re.compile(r'\<meta\s+name\s*=\s*\"irCategory\"\s+content\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			cat = r.groups()[0]
		return cat

	def getDuration(self,*args,**kwargs):
		pass

	def getUptime(self,*args,**kwargs):
		pass


def download(c):
	d = TuDouExtractor(c)
	return d.download()



class TuDou_Extractor():
	'''
	土豆下载类
	'''
	def __init__(self,c):
		self.i = VideoInfo() # i 表示videoinfo
		self.c = c # c 表示condition
		self.i.url = c.url
		self.i.ext = c.format
		self.i.source = TUDOU
		self.i.server = getIP()
		self.i.path = getDownloadDir(self.c.downloaddir, self.c.verbose, self.c.debug)
		tmppath = os.path.join(self.i.path,'tmp')
		if not os.path.exists(tmppath):
			os.mkdir(tmppath)
		self.tmppath = tmppath

	def download(self):
		'''
		下载
		'''
		self.page = get_html(self.c.url)
		if not self.page: sys.exit(0)
		pattern = re.compile(r'vcode\s*[:=]\s*\'([^\']+)\'')
		r = pattern.search(self.page)
		if r:
			print(r)
			vcode = r.groups()[0]
			youku_url = r'http://v.youku.com/v_show/id_%s.html' % (vcode,)
			self.c.url = youku_url
			from youku import download
			download(self.c)
		else:
			pattern = re.compile(r'segs:\s*\'(\{.*?\})\'')
			r = pattern.search(self.page)
			if r:
				#print(r.groups()[0])
				js = json.loads(r.groups()[0])
				self.m3u8 = self.query_m3u8(js)
			else:
				if self.c.debug or self.c.verbose:
					print('sorry: cannot resolve the url... url = %s' % (self.c.url,))

	def query_m3u8(self,segs):
		'''
		查询m3u8
		'''
		pass

	def download_by_iid(self):
		pass

	def download_by_listplay(self):
		pass

	def download_by_programs(self):
		pass

	def download_by_albumplay(self):
		pass


