#!/usr/bin/env python3
import re
import sys
import json
import time
import random
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor

_stream_ids = ('1300','1080p','1000','720p','350')

class LETVExtractor(BasicExtractor):
	'''
	乐视视频下载器
	'''
	def __init__(self,c):
		super(LETVExtractor,self).__init__(c, LETV)

	def download(self):
		print('letv:start downloading ...')
		retry = 3
		while retry > 0 :
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

		#metadata = ...
		url = r'http://api.letv.com/mms/out/video/playJson?id=%s&platid=1&splatid=101&format=1&tkey=%s&domain=www.letv.com&dvtype=1000&accessyx=1' % (self.i.vid,self.calcTimeKey(int(time.time())))
		info = json.loads(get_html(url))
		#print(info)

		self.i.title = self.getTitle(info = info)
		self.i.desc = self.getDesc()
		self.i.keywords = self.getKeywords()
		self.i.fname = self.getFname()
		self.i.fsize = self.getFsize()
		self.i.duration = self.getDuration(info = info)
		self.i.category = self.getCategory()
		self.i.uptime = self.getUptime()
		#self.i.m3u8 = self.query_m3u8()
		self.flvlist,self.m3u8  = self.query_real(info = info)
		self.realdown()

	def calcTimeKey(self,t):
		ror = lambda val, r_bits, : ((val & (2**32-1)) >> r_bits%32) |  (val << (32-(r_bits%32)) & (2**32-1))
		return ror(ror(t,773625421%13)^773625421,773625421%17)

	def query_m3u8(self,*args,**kwargs):
		return ''

	def query_real(self,*args,**kwargs):
		info = kwargs['info']
		support_stream_ids = info['playurl']['dispatch'].keys()
		#print(support_stream_ids)
		stream_id = '350'
		for _stream_id in _stream_ids:
			if _stream_id in support_stream_ids:
				stream_id = _stream_id
				break

		_url = info['playurl']['domain'][-1] + info['playurl']['dispatch'][stream_id][0]
		url = '%s&ctv=pc&m3v=1&termid=1&format=1&hwtype=un&ostype=Linux&tag=letv&sign=letv&expect=3&tn=%s&pay=0&iscpn=f9051&rateid=%s' % (_url,random.random(),stream_id)
		#print(url)
		info2 = json.loads(get_html(url))
		#print(info2)
		m3u8 = get_html(info2['location'])
		#print(m3u8)
		m3u8_list = self._decode(m3u8)

		urls = re.findall(r'^[^#][^\r]*',m3u8_list,re.MULTILINE)
		#print(len(urls))
		return urls,info2['location']

	def _decode(self,data):
		version = data[0:5]
		if version.lower() == b'vc_01':
			#get real m3u8
			loc2 = data[5:]
			length = len(loc2)
			loc4 = [0]*(2*length)
			for i in range(length):
				loc4[2*i] = loc2[i] >> 4
				loc4[2*i+1]= loc2[i] & 15;
			loc6 = loc4[len(loc4)-11:]+loc4[:len(loc4)-11]
			loc7 = [0]*length
			for i in range(length):
				loc7[i] = (loc6[2 * i] << 4) +loc6[2*i+1]
			return ''.join([chr(i) for i in loc7])
		else:
			# directly return
			return data

	def getVid(self,*args,**kwargs):
		vid = ''
		r = re.search(r'http://www\.letv\.com/ptv/vplay/(\d+)\.html',self.c.url)
		if r:
			vid = r.groups()[0]
		return vid

	def getFsize(self,*args,**kwargs):
		return 1024*1024

	def getTitle(self,*args,**kwargs):
		title = ''
		info = kwargs['info']
		title = info['playurl']['title']
		print(title)
		if not title:
			r = re.search(r'\<meta\s+name=\"irTitle\"\s+content=\"(.*?)\"',self.page)
			if r:
				title = r.groups()[0]
		return title

	def getDesc(self,*args,**kwargs):
		desc = self.i.title
		r = re.search(r'\<meta\s+name=\"description\"\s+content=\"(.*?)\"',self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def getKeywords(self,*args,**kwargs):
		keywords = ''
		r = re.search(r'\<meta\s+name=\"keywords\"\s+content=\"(.*?)\"',self.page)
		if r:
			keywords = r.groups()[0]
		return keywords.split(' ')

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		r = re.search(r'\<meta\s+name=\"irCategory\"\s+content=\"(.*?)\"',self.page)
		if r:
			cat = r.groups()[0]
		return cat

	def getDuration(self,*args,**kwargs):
		d = 0
		info = kwargs['info']
		d = info['playurl']['duration']
		return int(d.split('.')[0])

	def getUptime(self,*args,**kwargs):
		return INITIAL_UPTIME


def download(c):
	d = LETVExtractor(c)
	return d.download()