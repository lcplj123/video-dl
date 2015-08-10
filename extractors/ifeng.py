#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor
from xml.dom import minidom

class IFengExtractor(BasicExtractor):
	'''
	凤凰视频下载器
	'''
	def __init__(self,c):
		super(IFengExtractor,self).__init__(c, IFENG)

	def download(self):
		print('ifeng:start downloading ...')
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

		self.flvlist = self.query_real()
		self.i.title = self.getTitle()
		self.i.fname = self.getFname()
		self.i.fsize = self.getFsize()
		self.i.tags = self.getTags()
		self.i.desc = self.getDesc()
		self.i.duration = self.getDuration()
		self.i.views = self.getViews()
		self.i.uptime = self.getUptime()
		self.i.m3u8 = self.query_m3u8()

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
		return ''

	def query_real(self,*args,**kwargs):
		flvlist = []
		ids = self.i.vid
		url = 'http://v.ifeng.com/video_info_new/%s/%s/%s.xml' % (ids[-2], ids[-2:], ids)
		xml = get_html(url)
		self.xml = xml
		node = minidom.parseString(self.xml)
		print(xml)
		item = node.getElementsByTagName('item')[0]
		playurl = item.attributes['VideoPlayUrl'].value
		if playurl:
			flvlist.append(playurl)
		else:
			nodelist = node.getElementsByTagName('partsH')
			if not nodelist:
				nodelist = node.getElementsByTagName('parts')
			for node in nodelist:
				t = node.attributes['playurl']
				flvlist.append(t.value)
		return [flv.replace(' ','') for flv in flvlist]

	def getVid(self,*args,**kwargs):
		vid = ''
		r = re.search(r'/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.shtml$',self.c.url)
		if r:
			vid = r.groups()[0]
		else:
			r2 = re.search(r'\"id\"\s*:\s*\"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\"',self.page)
			if r2:
				vid = r2.groups()[0]
		return vid

	def getFname(self,*args,**kwargs):
		fname = ''
		if self.c.nametype == 'title':
			fname = '%s.%s' % (self.i.title[:32],self.c.ext)
		else:
			fname = '%s.%s' % (self.i.vid,self.c.ext)
		return fname

	def getFsize(self,*args,**kwargs):
		return 2048*1024

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		r = re.search(r'\<meta\s+name=\"irCategory\"\s+content=\"(.*?)\"',self.page)
		if r:
			cat = r.groups()[0]
		else:
			node = minidom.parseString(self.xml)
			item = node.getElementsByTagName('item')[0]
			cat = item.attributes['CategoryName'].value
		return cat

	def getDesc(self,*args,**kwargs):
		desc = self.i.title
		r = re.search(r'\<meta\s+name=\"description\"\s+content=\"(.*?)\"',self.page)
		if r:
			desc = r.groups()[0]
		if not desc:
			desc = self.i.title
		return desc

	def getTags(self,*args,**kwargs):
		tags = ''
		r = re.search(r'\<meta\s+name=\"keywords\"\s+content=\"(.*?)\"',self.page)
		if r:
			tags = r.groups()[0]
		else:
			node = minidom.parseString(self.xml)
			item = node.getElementsByTagName('item')[0]
			tags = item.attributes['Keyword'].value
		return tags.split(',')

	def getViews(self,*args,**kwargs):
		view = 1
		return view

	def getTitle(self,*args,**kwargs):
		title = ''
		r = re.search(r'\<meta\s+name=\"irTitle\"\s+content=\"(.*?)\"',self.page)
		if r:
			title = r.groups()[0]
		else:
			node = minidom.parseString(self.xml)
			item = node.getElementsByTagName('item')[0]
			title = item.attributes['Name'].value
		return title

	def getDuration(self,*args,**kwargs):
		t = 0
		r = re.search(r'\"duration\"\s*:\s*\"([0-9.]+)\"',self.page)
		if r:
			t = r.groups()[0]
		if int(t) == 0:
			node = minidom.parseString(self.xml)
			item = node.getElementsByTagName('item')[0]
			t = item.attributes['Duration'].value
		return int(t)

	def getUptime(self,*args,**kwargs):
		node = minidom.parseString(self.xml)
		item = node.getElementsByTagName('item')[0]
		t = item.attributes['CreateDate'].value
		x,_ = t.split(' ')
		a,b,c = x.split('-')
		return '%s%s%s' % (a,b,c)



def download(c):
	d = IFengExtractor(c)
	return d.download()