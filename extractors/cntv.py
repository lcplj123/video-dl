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
	ku6下载器
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
		if js.get('ack','no') == 'no':
			print('cntv: error vid %s,exit...' % (self.i.vid,))
			sys.exit(0)

		xiyou_js = dict()
		if self.branch == 'xiyou':
			xiyou_url = r'http://xiyou.cntv.cn/interface/index?videoId=%s'
			xiyou_js = json.loads(get_html(xiyou_url % (self.i.vid,)))

		self.i.title = self.getTitle(js = js,xiyou_js = xiyou_js)
		self.i.m3u8 = self.query_m3u8(js = js,xiyou_js = xiyou_js)
		self.i.duration = self.getDuration(js = js,xiyou_js = xiyou_js)
		self.i.fsize = self.getFsize(js = js,xiyou_js = xiyou_js)
		self.i.fname = self.getFname(js = js,xiyou_js = xiyou_js)
		self.i.desc = self.getDesc(js = js,xiyou_js = xiyou_js)
		self.i.tags = self.getTags(js = js,xiyou_js = xiyou_js)
		self.i.views = self.getViews(js = js,xiyou_js = xiyou_js)
		self.i.category = self.getCategory(js = js,xiyou_js = xiyou_js)
		self.i.uptime = self.getUptime(js = js, xiyou_js = xiyou_js)
		self.flvlist = self.query_real(js = js)

		ret = checkCondition(self.i,self.c)
		if ret == C_PASS:
			if not realDownload(self.flvlist,self.tmppath):
				sys.exit(0)
			#下载成功，合并视频，并删除临时文件
			if not mergeVideos(self.flvlist, self.tmppath, self.i.path, self.i.fname):
				sys.exit(0)

			self.jsonToFile()
		else:
			print('tips: video do not math conditions. code = %d' % (ret,))
			sys.exit(0)


	def query_m3u8(self,*args,**kwargs):
		m3u8 = ''
		js = kwargs['js']
		m3u8 = js.get('hls_url','')
		return m3u8

	def query_real(self,*args,**kwargs):
		urls = []
		js = kwargs['js']
		video  = js['video']
		ch = 'chapters'
		for i in ('5','4','3','2',''):
			ch = 'chapters%s' % (i,)
			if ch in video: break
		chapterlist = video[ch]
		for d in chapterlist:
			urls.append(d['url'])
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
			title = xiyou_js['data']['title']
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
			desc = xiyou_js['data']['videoDetailInfo']
			return desc
		else:
			pass

		r = re.search(r'\<meta\s+name=\"description\"\s+content=\"(.*?)\"',self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def getTags(self,*args,**kwargs):
		tags = ''
		js = kwargs['js']
		xiyou_js = kwargs['xiyou_js']
		if self.branch == 'xiyou':
			tags = xiyou_js['data']['videoTags']
			return tags.split(',')
		else:
			pass
		r = re.search(r'\<meta\s+name=\"keywords\"\s+content=\"(.*?)\"',self.page)
		if r:
			tags = r.groups()[0]
		return tags.split(',')

	def getViews(self,*args,**kwargs):
		views = 1
		js = kwargs['js']
		xiyou_js = kwargs['xiyou_js']
		if self.branch == 'xiyou':
			views = xiyou_js['data']['playCount']
			return int(views)
		else:
			pass
		r = re.search(r'',self.page)

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		js = kwargs['js']
		xiyou_js = kwargs['xiyou_js']
		if self.branch == 'xiyou':
			cat = xiyou_js['data']['categoryName']
			return cat
		else:
			pass
		return cat

	def getDuration(self,*args,**kwargs):
		duration = 0
		js = kwargs['js']
		xiyou_js = kwargs['xiyou_js']
		if self.branch == 'xiyou':
			duration = xiyou_js['data']['timeSpan']
			x,y = duration.split('.')
			return int(x)+1 if y != '00' else int(x)
		else:
			t = js['video']['totalLength']
			x,y = t.split('.')
			return int(x)+1 if y != '00' else int(x)

	def getUptime(self,*args,**kwargs):
		t = ''
		js = kwargs['js']
		xiyou_js = kwargs['xiyou_js']
		if self.branch == 'xiyou':
			t = xiyou_js['data']['uploadTime']
		else:
			t = js['f_pgmtime'].split(' ')[0]
		return t.replace('-','')


def download(c):
	d = CNTVExtractor(c)
	return d.download()