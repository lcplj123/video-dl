#!/usr/bin/env python3
import os
import sys
from utils import *
from videoinfo import VideoInfo

class BasicExtractor:
	'''
	视频下载类的基类
	'''
	def __init__(self,c,source):
		self.i = VideoInfo() # i 表示 videoinfo
		self.c = c # c 表示条件
		self.i.url = c.url
		self.i.source = source
		self.i.path = getDownloadDir(c.downloaddir)
		self.i.server = getIP()
		self.tmppath = self.mktmp()
		self.flvlist = [] #视频真实下载地址列表

	def mktmp(self):
		'''
		生成tmp路径
		'''
		tmppath = os.path.join(self.i.path,'tmp')
		if not os.path.exists(tmppath):
			os.mkdir(tmppath)
		return tmppath

	def download(self):
		'''
		视频下载入口
		'''
		raise NotImplementedError

	def realdown(self,header = None):
		'''
		实际的下载行为
		'''
		ret = checkCondition(self.i,self.c)
		if ret == C_PASS:
			if not realDownload(self.flvlist,self.tmppath,header):
				sys.exit(0)
			#下载成功，合并视频，并删除临时文件
			if not mergeVideos(self.flvlist, self.tmppath, self.i.path, self.i.fname):
				sys.exit(0)

			self.jsonToFile()
		else:
			print('tips: video do not math conditions. code = %d,exit...' % (ret,))
			sys.exit(0)

	def query_m3u8(self,*args,**kwargs):
		'''
		获取视频的m3u8地址
		'''
		raise NotImplementedError

	def query_real(self,*args,**kwargs):
		'''
		获取真实下载地址
		'''
		raise NotImplementedError

	def getVid(self,*args,**kwargs):
		'''
		获取视频vid
		'''
		raise NotImplementedError

	def getFname(self,*args,**kwargs):
		'''
		获取视频文件的名字
		此函数调用的前提是title不为空
		'''
		fname = ''
		if self.c.nametype == 'title':
			fname = '%s.%s' % (self.i.title[:32],self.c.ext)
		else:
			fname = '%s.%s' % (self.i.vid,self.c.ext)
		return fname

	def getFsize(self,*args,**kwargs):
		'''
		获取视频文件的大小
		'''
		raise NotImplementedError

	def getTitle(self,*args,**kwargs):
		'''
		获取视频标题
		'''
		raise NotImplementedError

	def getDesc(self,*args,**kwargs):
		'''
		获取视频描述
		'''
		raise NotImplementedError

	def getKeywords(self,*args,**kwargs):
		'''
		获取视频标签
		'''
		raise NotImplementedError

	def getCategory(self,*args,**kwargs):
		'''
		获取视频类别
		'''
		raise NotImplementedError

	def getDuration(self,*args,**kwargs):
		'''
		获取视频播放时长(秒)
		'''
		raise NotImplementedError

	def getUptime(self,*args,**kwargs):
		'''
		获取视频上传时间
		'''
		raise NotImplementedError

	def jsonToFile(self):
		'''
		生成json文件
		'''
		if not self.c.makejson: return
		jsonFile = os.path.join(self.i.path,self.i.fname+'.json')
		self.i.jsonToFile(jsonFile)