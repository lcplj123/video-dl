#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor
from xml.dom.minidom import parseString
import time
from random import random

class PPTVExtractor(BasicExtractor):
	'''
	PPTV视频下载器
	'''
	def __init__(self,c):
		super(PPTVExtractor,self).__init__(c, PPTV)

	def download(self):
		print('pptv:start downloading ...')
		retry = 3
		while retry >=0 :
			self.page = get_html(self.c.url)
			if self.page: break
			retry -= 1
		if not self.page:
			print('error: request video info error,check url. %s' % (self.c.url,))
			sys.exit(0)

		self.i.vid,self.evid = self.getVid()
		if not self.i.vid :
			print('error: not find vid! exit...')
			sys.exit(0)

		xml = get_html(r'http://web-play.pptv.com/webplay3-0-%s.xml?type=web.fpp' % self.i.vid)
		print(xml)
		#metadata = ...
		self.i.title = self.getTitle(xml = xml)
		self.i.desc = self.getDesc()
		self.i.keywords = self.getKeywords()
		self.i.fname = self.getFname()
		self.i.fsize = self.getFsize(xml =xml)
		self.i.duration = self.getDuration()
		self.i.category = self.getCategory()
		self.i.uptime = self.getUptime()
		self.i.m3u8 = self.query_m3u8()
		self.flvlist = self.query_real(xml = xml)
		print(self.flvlist)
		self.realdown()

	def query_m3u8(self,*args,**kwargs):
		pass

	def query_real(self,*args,**kwargs):
		xml = kwargs['xml']
		root = parseString(xml).documentElement
		host = root.getElementsByTagName('sh')[0].firstChild.data
		k = root.getElementsByTagName('key')[0].firstChild.data
		files = root.getElementsByTagName('file')[0]
		item = files.getElementsByTagName('item')[-1]
		rid = item.getAttribute('rid')
		st = root.getElementsByTagName('st')[0].firstChild.data[:-4]
		st = time.mktime(time.strptime(st))*1000-60*1000-time.time()*1000
		st += time.time()*1000
		st = st/1000
		key = self._constructKey(st)
		pieces = re.findall(r'<sgm no="(\d+)"[^<>]+fs="(\d+)"', xml)
		numbers, fs = zip(*pieces)
		urls=[ "http://ccf.pptv.com/{}/{}?key={}&fpp.ver=1.3.0.4&k={}&type=web.fpp".format(i,rid,key,k)  for i in range(max(map(int,numbers))+1)]
		assert rid.endswith('.mp4')
		return urls

	def _constructKey(self,arg):
		def str2hex(s):
			r=""
			for i in s[:8]:
				t=hex(ord(i))[2:]
				if len(t)==1:
					t="0"+t
				r+=t
			for i in range(16):
				r+=hex(int(15*random()))[2:]
			return r

		#ABANDONED  Because SERVER_KEY is static
		def getkey(s):
			#returns 1896220160
			l2=[i for i in s]
			l4=0
			l3=0
			while l4<len(l2):
				l5=l2[l4]
				l6=ord(l5)
				l7=l6<<((l4%4)*8)
				l3=l3^l7
				l4+=1
			return l3
			pass

		def rot(k,b): ##>>> in as3
			if k>=0:
				return k>>b
			elif k<0:
				return (2**32+k)>>b
			pass

		def lot(k,b):
			return (k<<b)%(2**32)

		#WTF?
		def encrypt(arg1,arg2):
			delta=2654435769
			l3=16;
			l4=getkey(arg2)  #1896220160
			l8=[i for i in arg1]
			l10=l4;
			l9=[i for i in arg2]
			l5=lot(l10,8)|rot(l10,24)#101056625
			# assert l5==101056625
			l6=lot(l10,16)|rot(l10,16)#100692230
			# assert 100692230==l6
			l7=lot(l10,24)|rot(l10,8)
			# assert 7407110==l7
			l11=""
			l12=0
			l13=ord(l8[l12])<<0
			l14=ord(l8[l12+1])<<8
			l15=ord(l8[l12+2])<<16
			l16=ord(l8[l12+3])<<24
			l17=ord(l8[l12+4])<<0
			l18=ord(l8[l12+5])<<8
			l19=ord(l8[l12+6])<<16
			l20=ord(l8[l12+7])<<24
			l21=(((0|l13)|l14)|l15)|l16
			l22=(((0|l17)|l18)|l19)|l20
			l23=0
			l24=0
			while l24<32:
				l23=(l23+delta)%(2**32)
				l33=(lot(l22,4)+l4)%(2**32)
				l34=(l22+l23)%(2**32)
				l35=(rot(l22,5)+l5)%(2**32)
				l36=(l33^l34)^l35
				l21=(l21+l36)%(2**32)
				l37=(lot(l21,4)+l6)%(2**32)
				l38=(l21+l23)%(2**32)
				l39=(rot(l21,5))%(2**32)
				l40=(l39+l7)%(2**32)
				l41=((l37^l38)%(2**32)^l40)%(2**32)
				l22=(l22+l41)%(2**32)
				l24+=1
			l11+=chr(rot(l21,0)&0xff)
			l11+=chr(rot(l21,8)&0xff)
			l11+=chr(rot(l21,16)&0xff)
			l11+=chr(rot(l21,24)&0xff)
			l11+=chr(rot(l22,0)&0xff)
			l11+=chr(rot(l22,8)&0xff)
			l11+=chr(rot(l22,16)&0xff)
			l11+=chr(rot(l22,24)&0xff)
			return l11

		loc1=hex(int(arg))[2:]+(16-len(hex(int(arg))[2:]))*"\x00"
		SERVER_KEY="qqqqqww"+"\x00"*9
		res=encrypt(loc1,SERVER_KEY)
		return str2hex(res)


	def getVid(self,*args,**kwargs):
		vid = ''
		evid = ''
		r1 = re.search(r'pptv\.com/show/(.*?)\.html',self.c.url)
		if r1:
			evid = r1.groups()[0]
		r2 = re.search(r'webcfg\s*=\s*{\"id\":\s*(\d+)',self.page)
		if r2:
			vid = r2.groups()[0]
		return vid,evid

	def getFsize(self,*args,**kwargs):
		s = 0
		xml = kwargs['xml']
		r = re.findall(r'filesize=\"(\d+)\"',xml)
		for t in r:
			if s < int(t):
				s = int(t)
		return s

	def getTitle(self,*args,**kwargs):
		title = ''
		xml = kwargs['xml']
		r = re.search(r'nm=\"(.*?)\"',xml)
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
		return keywords.split(';')

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		return cat

	def getDuration(self,*args,**kwargs):
		d = 60
		r = re.search(r"\"duration\"\s*:\s*(\d+)",self.page)
		if r:
			d = r.groups()[0]
		return int(d)

	def getUptime(self,*args,**kwargs):
		return INITIAL_UPTIME


def download(c):
	d = PPTVExtractor(c)
	return d.download()