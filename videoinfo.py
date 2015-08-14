#!/usr/bin/env python3
import json
from define import INITIAL_UPTIME

class VideoInfo:
	def __init__(self,**kwargs):
		self.url = kwargs.get('url') #视频所在页面地址---
		self.source = kwargs.get('source') #(视频的源表明来自哪个网站)---
		self.path = kwargs.get('path') #视频下载的路径(不包括文件名)---
		self.server = kwargs.get('server') #下载视频的服务器ip或域名---
		self.vid = kwargs.get('vid') #视频的vid(显示在网页上的,一般都加密了)
		self.fname = kwargs.get('fname') #视频文件名字
		self.fsize = kwargs.get('fsize',0) #视频文件大小
		self.title = kwargs.get('title') #视频标题
		self.desc = kwargs.get('desc') #视频描述
		self.keywords = kwargs.get('keywords',[]) #视频标签,列表
		self.category = kwargs.get('category','未知') #视频类别(文字描述)
		self.duration = kwargs.get('duration',0) #视频时长
		self.m3u8 = kwargs.get('m3u8','') #视频的m3u8地址
		self.uptime = kwargs.get('uptime',INITIAL_UPTIME) #视频上传时间(整型，格式：20150101)

	def json(self):
		'''
		生成json
		'''
		js = json.dumps(self.__dict__)
		return js

	def jsonToFile(self,filename):
		'''
		将json字符串写入文件
		'''
		with open(filename,'w') as f:
			f.write(self.json())
			f.close()
		return True

#For test
#d= {'views':100}
#a = VideoInfo(**d)
#print(a.__dict__)
#print(a.json())
#a.jsonToFile('a.json')