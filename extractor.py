#!/usr/bin/env python3
import os
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
		'''
		raise NotImplementedError

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

	def getTags(self,*args,**kwargs):
		'''
		获取视频标签
		'''
		raise NotImplementedError

	def getUsername(self,*args,**kwargs):
		'''
		获取上传用户名
		'''
		raise NotImplementedError

	def getUserid(self,*args,**kwargs):
		'''
		获取上传用户id
		'''
		raise NotImplementedError

	def getViews(self,*args,**kwargs):
		'''
		获取视频的观看次数
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