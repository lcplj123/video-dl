#!/usr/bin/env python3
import json
import os

class VideoInfo:
	def __init__(self,**kwargs):
		self.url = kwargs.get('url')
		self.vid = kwargs.get('vid')
		self.source = kwargs.get('source')
		self.path = kwargs.get('path')
		self.server = kwargs.get('server')
		self.fname = kwargs.get('fname')
		self.fsize = kwargs.get('fsize')
		self.ext = kwargs.get('ext')
		self.title = kwargs.get('title')
		self.desc = kwargs.get('desc')
		self.tag = kwargs.get('tag')
		self.uptime = kwargs.get('uptime')
		self.upuser = kwargs.get('upuser')
		self.views = kwargs.get('views')
		self.category = kwargs.get('category')
		self.duration = kwargs.get('duration')
		self.vrate = kwargs.get('vrate')
		self.arate = kwargs.get('arate')
		self.height = kwargs.get('height')
		self.width = kwargs.get('width')
		self.vcoding = kwargs.get('vcoding')
		self.acoding = kwargs.get('acoding')

	def json(self):
		'''
		生成json
		'''
		js = json.dumps(self.__dict__)
		return js

	def jsonToFile(self,filename,overwrite = False):
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
			with open(filename,'wa') as f:
				f.write(self.json())
				f.close()
				return True

#For test
#d= {'views':100}
#a = VideoInfo(**d)
#print(a.__dict__)
#print(a.json())