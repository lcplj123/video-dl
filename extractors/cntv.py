#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor

class CNTVExtractor(BasicExtractor):
	'''
	CNTV视频下载器
	'''
	def __init__(self,c):
		super(CNTVExtractor,self).__init__(c, CNTV)

	def download(self):
		print('cntv:start downloading ...')
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

		url = r'http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid=%s'
		jdata = get_html(url % (self.i.vid,))
		js = json.loads(jdata)
		#print(js)
		if js.get('ack','no') == 'no' and self.branch != 'xiyou':
			print('cntv: error vid %s,exit...' % (self.i.vid,))
			sys.exit(0)

		xiyou_js = dict()
		if self.branch == 'xiyou':
			xiyou_url = r'http://xiyou.cntv.cn/interface/index?videoId=%s'
			xiyou_js = json.loads(get_html(xiyou_url % (self.i.vid,)))
		#print(xiyou_js)
		self.i.title = self.getTitle(js = js,xiyou_js = xiyou_js)
		self.i.m3u8 = self.query_m3u8(js = js,xiyou_js = xiyou_js)
		self.i.duration = self.getDuration(js = js,xiyou_js = xiyou_js)
		self.i.fsize = self.getFsize(js = js,xiyou_js = xiyou_js)
		self.i.fname = self.getFname(js = js,xiyou_js = xiyou_js)
		self.i.desc = self.getDesc(js = js,xiyou_js = xiyou_js)
		self.i.keywords = self.getKeywords(js = js,xiyou_js = xiyou_js)
		self.i.category = self.getCategory(js = js,xiyou_js = xiyou_js)
		self.i.uptime = self.getUptime(js = js, xiyou_js = xiyou_js)
		self.flvlist = self.query_real(js = js,xiyou_js = xiyou_js)
		self.realdown()


	def query_m3u8(self,*args,**kwargs):
		m3u8 = ''
		js = kwargs['js']
		xiyou_js = kwargs['xiyou_js']
		if self.branch == 'xiyou':
			pass
		else:
			m3u8 = js.get('hls_url','')
		return m3u8

	def query_real(self,*args,**kwargs):
		urls = []
		js = kwargs['js']
		xiyou_js = kwargs['xiyou_js']
		if self.branch == 'xiyou':
			hdx = ('videoFilePathSHD','videoFilePathHD','videoFilePath')
			videopath = xiyou_js['data'][0]['videoList'][0]
			for hd in hdx:
				if hd in videopath:
					path = videopath[hd]
					x,y = path.split('#')
					zlist = y.split('_')
					for i in range(1,len(zlist)+1):
						url = '%s_%03d.mp4' % (x,i)
						urls.append(url)
					break
		else:
			video  = js['video']
			ch = 'chapters'
			for i in ('5','4','3','2',''):
				ch = 'chapters%s' % (i,)
				if ch in video: break
			chapterlist = video.get(ch,[])
			if not chapterlist:
				chapterlist = video.get('lowChapters',[])
			for d in chapterlist:
				urls.append(d['url'])
		#print(urls)
		return urls

	def getVid(self,*args,**kwargs):
		vid = ''
		if self.c.url.find('xiyou.cntv.cn') != -1:
			self.branch = 'xiyou'
			r = re.search(r'xiyou\.cntv\.cn/\w-([\w-]+)\.html',self.c.url)
			if r:
				vid = r.groups()[0]
		else:
			self.branch = 'other'
			r = re.search(r'\<!--repaste\.video\.code\.begin--\>(\w+)\<!--repaste\.video\.code\.end--\>',self.page)
			if r:
				vid = r.groups()[0]
			else:
				r2 = re.search(r'videoCenterId\s*:\s+[\'\"](.*?)[\'\"]',self.page)
				if r2:
					vid = r2.groups()[0]
		return vid

	def getFsize(self,*args,**kwargs):
		js = kwargs['js']
		xiyou_js = kwargs['xiyou_js']
		size = 1024*1024
		if self.branch == 'xiyou':
			pass
		else:
			pass
		return size

	def getTitle(self,*args,**kwargs):
		xiyou_js = kwargs['xiyou_js']
		js = kwargs['js']
		title = ''
		if self.branch == 'xiyou':
			title = xiyou_js['data'][0]['title']
		else:
			title = js['title']
		if title: return title

		r = re.search('\<em\s+class=\"htt\"\s+id=\"videotitle\"\s+title=\"(.*?)\"',self.page)
		if r:
			title = r.groups()[0]
		return title

	def getDesc(self,*args,**kwargs):
		desc = self.i.title
		xiyou_js = kwargs['xiyou_js']
		js = kwargs['js']
		if self.branch == 'xiyou':
			desc = xiyou_js['data'][0]['videoDetailInfo']
			return desc
		else:
			pass

		r = re.search(r'\<meta\s+name=\"description\"\s+content=\"(.*?)\"',self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def getKeywords(self,*args,**kwargs):
		tags = ''
		js = kwargs['js']
		xiyou_js = kwargs['xiyou_js']
		if self.branch == 'xiyou':
			tags = xiyou_js['data'][0]['videoTags']
			return tags.split(',')
		else:
			pass
		r = re.search(r'\<meta\s+name=\"keywords\"\s+content=\"(.*?)\"',self.page)
		if r:
			tags = r.groups()[0]
		return tags.split(',')

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		js = kwargs['js']
		xiyou_js = kwargs['xiyou_js']
		if self.branch == 'xiyou':
			cat = xiyou_js['data'][0]['categoryName']
			return cat
		else:
			pass
		return cat

	def getDuration(self,*args,**kwargs):
		duration = 0
		js = kwargs['js']
		xiyou_js = kwargs['xiyou_js']
		if self.branch == 'xiyou':
			duration = xiyou_js['data'][0]['timeSpan']
			x = duration.split('.')
			return int(x[0])
		else:
			t = js['video']['totalLength']
			x = t.split('.')
			return int(x[0])

	def getUptime(self,*args,**kwargs):
		t = INITIAL_UPTIME
		js = kwargs['js']
		xiyou_js = kwargs['xiyou_js']
		if self.branch == 'xiyou':
			t = xiyou_js['data'][0]['uploadTime']
		else:
			t = js['f_pgmtime'].split(' ')[0]
		return int(t.replace('-',''))


def download(c):
	d = CNTVExtractor(c)
	return d.download()