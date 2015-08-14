#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor
import hashlib
from zlib import decompress
from math import floor
from uuid import uuid4
from random import randint,random
import time

# bid 代表着视频质量
# 0 none
# 1 standard
# 2 high
# 3 super
# 4 super-high
# 5 fullhd
# 10 4k
#96 top speed

class IQiYiExtractor(BasicExtractor):
	'''
	爱奇艺视频下载器
	'''
	def __init__(self,c):
		super(IQiYiExtractor,self).__init__(c, IQIYI)

	def download(self):
		print('iqiyi:start downloading ...')
		retry = 3
		while retry >=0 :
			self.page = get_html(self.c.url)
			if self.page: break
			retry -= 1
		if not self.page:
			print('error: request video info error,check url. %s' % (self.c.url,))
			sys.exit(0)

		self.i.vid,self.tvid = self.getVid()
		if not self.i.vid or not self.tvid:
			print('error: not find vid! exit...')
			sys.exit(0)

		gen_uid = uuid4().hex
		info = self._getVMS(self.tvid,self.i.vid,gen_uid)
		assert info['code'] == 'A000000'
		self.i.title = self.getTitle(info = info)
		self.i.desc = self.getDesc(info = info)
		self.i.fname = self.getFname()
		self.i.uptime = self.getUptime(info = info)
		self.i.keywords = self.getKeywords(info = info)

		if info['data']['vp']['tkl'] == '':
			print('sorry, do not support iqiyi vip videos!exit...')
			sys.exit(0)
		#print(info)
		bid = 0
		stream = {}
		vs = info['data']['vp']['tkl'][0]['vs']
		for i in vs:
			if int(i['bid']) <= 10 and int(i['bid']) >= bid:
				bid = int(i['bid'])
				stream = i

		#print(stream)
		self.i.duration = self.getDuration(stream = stream)
		self.i.m3u8 = self.query_m3u8(stream = stream,vs = vs)
		self.flvlist,self.i.fsize = self.query_real(stream = stream,du = info['data']['vp']['du'],gen_uid = gen_uid)
		self.realdown()


	def _getVMS(self,tvid,vid,gen_uid):
		#tm ->the flash run time for md5 usage
		#um -> vip 1 normal 0
		#authkey -> for password protected video ,replace '' with your password
		#puid user.passportid may empty?
		#TODO: support password protected video
		tm,sc,src = self._mix(tvid)
		vmsreq = 'http://cache.video.qiyi.com/vms?key=fvip&src=1702633101b340d8917a69cf8a4b8c7&tvId=%s&vid=%s&vinfo=1\
		&tm=%s&enc=%s&qyid=%s&tn=%s&um=0&authkey=%s' % (tvid,vid,tm,sc,gen_uid,str(random()),hashlib.new('md5',bytes(''+str(tm)+tvid,'utf-8')).hexdigest())
		return json.loads(get_html(vmsreq))

	def _mix(self,tvid):
		enc = []
		enc.append('65096542539c4e529c8ee97511cd979f')
		tm = str(randint(2000,4000))
		src = 'eknas'
		enc.append(str(tm))
		enc.append(tvid)
		sc = hashlib.new('md5',bytes("".join(enc),'utf-8')).hexdigest()
		return tm,sc,src

	def query_m3u8(self,*args,**kwargs):
		m3u8 = ''
		stream = kwargs['stream']
		m3u8 = stream['m3u8Url']
		if m3u8: return m3u8
		vs = kwargs['vs']
		bid = 0
		for i in vs:
			if int(i['bid']) <= 10 and int(i['bid']) >= bid and i['m3u8Url']:
				m3u8 = i['m3u8Url']

		return m3u8

	def query_real(self,*args,**kwargs):
		stream = kwargs['stream']
		du = kwargs['du']
		gen_uid = kwargs['gen_uid']
		video_links = stream['fs'] #now in i["flvs"] not in i["fs"]
		if not stream['fs'][0]['l'].startswith('/'):
			tmp = self._getVrsEncodeCode(stream['fs'][0]['l'])
			if tmp.endswith('mp4'):
				video_links = stream['flvs']
		urls = []
		size = 0
		for i in video_links:
			vlink = i['l']
			if not vlink.startswith("/"):
				#vlink is encode
				vlink=self._getVrsEncodeCode(vlink)
			key = self._getDispathKey(vlink.split("/")[-1].split(".")[0])
			size += i['b']
			baseurl=du.split("/")
			baseurl.insert(-1,key)
			url="/".join(baseurl)+vlink+'?su='+gen_uid+'&qyid='+uuid4().hex+'&client=&z=&bt=&ct=&tn='+str(randint(10000,20000))
			urls.append(json.loads(get_html(url))["l"])

		return urls,size


	def _getVrsEncodeCode(self,vlink):
		loc6=0
		loc2=''
		loc3=vlink.split("-")
		loc4=len(loc3)
		# loc5=loc4-1
		for i in range(loc4-1,-1,-1):
			loc6=self._getVRSXORCode(int(loc3[loc4-i-1],16),i)
			loc2+=chr(loc6)
		return loc2[::-1]

	def _getVRSXORCode(self,arg1,arg2):
		loc3=arg2 %3
		if loc3 == 1:
			return arg1^121
		if loc3 == 2:
			return arg1^72
		return arg1^103

	def _getDispathKey(self,rid):
		tp=")(*&^flash@#$%a"  #magic from swf
		time=json.loads(get_html("http://data.video.qiyi.com/t?tn="+str(random())))["t"]
		t=str(int(floor(int(time)/(10*60.0))))
		return hashlib.new("md5",bytes(t+tp+rid,"utf-8")).hexdigest()

	def getVid(self,*args,**kwargs):
		vid = ''
		tvid = ''
		r1 = re.search(r'data-player-tvid=\"([^"]+)\"',self.page)
		if r1:
			tvid = r1.groups()[0]
		r2 = re.search(r'data-player-videoid=\"([^"]+)\"',self.page)
		if r2:
			vid = r2.groups()[0]
		return vid,tvid

	def getFsize(self,*args,**kwargs):
		pass

	def getTitle(self,*args,**kwargs):
		info = kwargs['info']
		return info['data']['vi']['vn']

	def getDesc(self,*args,**kwargs):
		info = kwargs['info']
		desc = info['data']['vi']['info']
		return desc if desc else self.i.title

	def getKeywords(self,*args,**kwargs):
		info = kwargs['info']
		tag = info['data']['vi']['keyword']
		return tag.split(',')

	def getCategory(self,*args,**kwargs):
		info = kwargs['info']

	def getDuration(self,*args,**kwargs):
		stream = kwargs['stream']
		return stream['duration']

	def getUptime(self,*args,**kwargs):
		info = kwargs['info']
		t = info['data']['vi']['pubTime']
		if not t: return INITIAL_UPTIME
		ltime = time.localtime(int(t[:-3]))
		tstr = time.strftime('%Y%m%d',ltime)
		return int(tstr)


def download(c):
	d = IQiYiExtractor(c)
	return d.download()