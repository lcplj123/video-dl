#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *

class YouKu_Extractor():
	'''
	youku下载类
	'''
	def __init__(self,c):
		self.c = c

	def download(self):
		'''
		通过url下载的接口
		'''
		self.page = get_html(self.c.url)
		#with open('test.html','w',encoding = 'utf8') as f:
		#	f.write(self.page)
		self.requestVideoInfo()

		return E_DOWNLOAD_SUCCESS

	def beforeDownload():
		'''
		事前处理
		'''
		pass

	def afterDownload():
		'''
		事后处理
		'''
		pass

	def requestVideoInfo(self):
		'''
		获取视频信息
		'''
		vid = self._getVids()
		title = self._getTitle()
		tag = self._getTag()
		desc = self._getDesc()
		views = self._getViews(vid)
		category = self._getCategory()
		sever = getIP()


	def _getTitle(self):
		'''
		获取视频标题
		'''
		pattern = re.compile(r'\<h1\s+cl ass=\"title\"\s+title=\"(.*?)\"\>')
		r = pattern.search(self.page)
		if r:
			print('title:',r.groups()[0])
			return r.groups()[0]
		else:
			pattern = re.compile(r'\<meta\s+name=\"irTitle\"\s+content=\"(.*?)\"')
			r = pattern.search(self.page)
			if r:
				print('Title:',r.groups()[0])
				return r.groups()[0]
			else:
				return ''

	def _getTag(self):
		'''
		获取标签
		'''
		pattern = re.compile(r'\<meta\s+name=\"keywords\"\s+content=\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			print("tag",r.groups()[0])
			return r.groups()[0]
		else:
			return ''

	def _getDesc(self):
		'''
		获取视频描述
		'''
		pattern = re.compile(r'\<meta\s+name=\"description\"\s+content=\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			print('desc',r.groups()[0])
			return r.groups()[0]
		else:
			return ''

	def _getVids(self):
		'''
		获取视频vid
		'''
		#pattern = re.compile(r'var\s+videoId\d?\s*\=\s*[\'|\"](.*?)[\'|\"]')
		pattern = re.compile(r'var\s+videoId\s*\=\s*[\'|\"](.*?)[\'|\"]')
		r = pattern.search(self.page)
		if r:
			return r.groups()[0]
		return ''


	def _getViews(self,vid):
		'''
		获取播放数 ajax请求
		'''
		if not vid: return 0
		VIEW_URL = r'http://v.youku.com/QVideo/~ajax/getVideoPlayInfo?id=%s&type=vv' % (vid,)
		js = get_html(VIEW_URL)
		if js == "null":
			return 0
		d = json.loads(js)
		return d.get('vv',0)

	def _getCategory(self):
		'''
		获取类别
		'''
		pattern = re.compile(r'\<meta\s+name=\"irCategory\"\s+content\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			print('category:',r.groups())
			return r.groups()[0]
		return '未知'

def download(c):
	d = YouKu_Extractor(c)
	return d.download()
