#!/usr/bin/env python3
import json
import os

class VideoInfo:
	def __init__(self,**kwargs):
		self.url = kwargs.get('url') #视频所在页面地址-----------
		self.vid = kwargs.get('vid') #视频的vid--------------
		self.evid = kwargs.get('evid') #视频加密后的vid---------------
		self.source = kwargs.get('source') #视频的源(表明来自哪个网站)----------
		self.path = kwargs.get('path') #视频下载的路径(不包括文件名)----------
		self.server = kwargs.get('server') #下载视频的服务器ip或域名-----------
		self.fname = kwargs.get('fname') #视频文件名字--------------
		self.fsize = kwargs.get('fsize',0) #视频文件大小-------------
		self.ext = kwargs.get('ext') #视频扩展名-------------------------
		self.title = kwargs.get('title') #视频标题--------------------
		self.desc = kwargs.get('desc') #视频描述--------------------
		self.tags = kwargs.get('tags') #视频标签---------------
		self.uptime = kwargs.get('uptime') #视频上传时间
		self.username = kwargs.get('username') #上传视频的用户名-----------------
		self.userid = kwargs.get('userid') #上传视频的用户id--------------
		self.views = kwargs.get('views',0) #视频被观看次数--------------
		self.category = kwargs.get('category') #视频类别-----------------
		self.duration = kwargs.get('duration',0) #视频时长--------------
		self.vrate = kwargs.get('vrate') #视频码率
		self.arate = kwargs.get('arate') #音频码率
		self.height = kwargs.get('height',0) #视频高度
		self.width = kwargs.get('width',0) #视频宽度
		self.vcoding = kwargs.get('vcoding') #视频编码
		self.acoding = kwargs.get('acoding') #音频编码
		self.m3u8 = kwargs.get('m3u8') #视频的m3u8地址-----------
		self.up = kwargs.get('up',0) #视频被顶次数-----------------
		self.down = kwargs.get('down',0) #视频被踩次数------------------

	def json(self):
		'''
		生成json
		'''
		js = json.dumps(self.__dict__)
		return js

	def jsonToFile(self,filename,overwrite = True):
		'''
		将json字符串写入文件
		'''
		if os.path.exists(filename):
			if not overwrite:
				return True
			else:
				with open(filename,'w') as f:
					f.write(self.json())
					f.close()
					return True
		else:
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