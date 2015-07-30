#!/usr/bin/env python3
import json

class Condition:
	'''
	下载视频对应的条件载体
	'''
	def __init__(self,url = None,maxsize='8192M',minsize='1M',datebefore='29990101',dateafter='20000101',maxviews = 9999999999999,minviews = 1,maxduration=86400,minduration=10,makejson=False,verbose=True,sockettimeout=15,downloaddir='.',downloadname='vid',debug=False,force = False,format = 'mp4'):
		self.url = url #视频下载地址
		self.source = ''
		self.maxsize = maxsize #最大尺寸 例如:10M
		self.minsize = minsize #视频最小尺寸 例如：1M
		self.datebefore = datebefore #
		self.dateafter = dateafter
		self.maxviews = maxviews
		self.minviews = minviews
		self.maxduration = maxduration #视频最大播放时长
		self.minduration = minduration #视频最小播放时长
		self.makejson = makejson #是否生成json文件
		self.verbose = verbose #下载过程中是否输出相关信息
		self.sockettimeout = sockettimeout #socket超时时间
		self.downloaddir = downloaddir #下载目录，可以是以 / 开始的绝对路径，也可以是以 . 开始的相对路径
		self.downloadname = downloadname #下载之后保存的文件名字 vid: 以视频的vid作为名字 title: 以视频的标题作为名字
		self.debug = debug #是否开启debug模式
		self.force = force #是否强制覆盖已存在的文件
		self.format = format

	def json(self):
		'''
		将下载条件转成json格式的，便于传输
		'''
		js = json.dumps(self.__dict__)
		return js

	def fromjson(self,js):
		'''
		从json字符串初始化对象
		'''
		if not js: return
		d = json.loads(js)
		self.__dict__.update(d)

	def string(self):
		'''
		获取string字符串
		'''
		pass
#For test
#a = Condition(url = "http://v.youku.com/watch/xxxxxxxx.html")
#print(a.json())

#js = '{"verbose":"ccccc","sockettimeout":100,"url":"http://v.youku.com","makejson":false}'
#a = Condition()
#a.fromjson(js)
#print(a.__dict__)
