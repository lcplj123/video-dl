#!/usr/bin/env python3
import re
import sys
import json
import time
from math import ceil
sys.path.append('..')
from define import *
from utils import *
import base64
from extractor import BasicExtractor

stream_types = [
	{'id':'hd3','container':'flv','profile':'1080P'},
	{'id':'hd2','container':'flv','profile':'超清'},
	{'id':'mp4','container':'mp4','profile':'高清'},
	{'id':'flvhd','container':'flv','profile':'高清'},
	{'id':'flv','container':'flv','profile':'标清'},
	{'id':'3gphd','container':'3gp','profile':'3GP高清'},
]

class YouKuExtractor(BasicExtractor):
	'''
	优酷视频下载器
	'''
	def __init__(self,c):
		super(YouKuExtractor,self).__init__(c, YOUKU)

	def download(self):
		'''
		视频下载入口
		'''
		print('start downloading ...')
		retry = 3
		while retry >=0 :
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

		metadata = self._getVideoJson()
		if not metadata:
			print('error: request video json file error. exit...')
			sys.exit(0)

		self.vid = metadata.get('videoid')
		self.i.title = self.getTitle(metadata = metadata)
		self.i.username = self.getUsername(metadata = metadata)
		self.i.userid = self.getUserid(metadata = metadata)
		self.i.duration = self.getDuration(metadata = metadata)
		self.i.tags = self.getTags(metadata = metadata)
		self.i.views = self.getViews(vid = self.vid)
		self.i.desc = self.getDesc(title = self.i.title)
		self.i.category = self.getCategory()
		self.i.fname = self.getFname()
		self.ip = metadata.get('ip')
		self.ep = metadata.get('ep')
		self.stream_id, self.stream_size, self.stream_segs = self._getStream(metadata)
		self.i.fsize = int(self.stream_size)
		self.i.m3u8,self.flvlist = self.query_m3u8()

		ret = checkCondition(self.i,self.c)
		if ret == C_PASS:
			if not realDownload(self.flvlist,self.tmppath):
				sys.exit(0)
			#下载成功，合并视频，并删除临时文件
			if not mergeVideos(self.flvlist, self.tmppath, self.i.path, self.i.fname):
				sys.exit(0)

			self.jsonToFile()
		else:
			print('tips: video do not math conditions. code = %d' % (ret,))
			sys.exit(0)

	def _getVideoJson(self):
		url = r'http://v.youku.com/player/getPlayList/VideoIDS/%s/Pf/4/ctype/12/ev/1' % (self.i.vid,)
		data = get_html(url)
		js = json.loads(data)
		if not js['data']: return
		metadata = js['data'][0]
		#For test
		with open('test.json','w',encoding = 'utf8') as f:
			json.dump(metadata,f)
		return metadata

	def _generate(self,vid,ep):

		f_code_1 = 'becaf9be'
		f_code_2 = 'bf7e5f01'

		def trans_e(a, c):
			f = h = 0
			b = list(range(256))
			result = ''
			while h < 256:
				f = (f + b[h] + ord(a[h % len(a)])) % 256
				b[h], b[f] = b[f], b[h]
				h += 1
			q = f = h = 0
			while q < len(c):
				h = (h + 1) % 256
				f = (f + b[h]) % 256
				b[h], b[f] = b[f], b[h]
				if isinstance(c[q], int):
					result += chr(c[q] ^ b[(b[h] + b[f]) % 256])
				else:
					result += chr(ord(c[q]) ^ b[(b[h] + b[f]) % 256])
				q += 1
			return result

		e_code = trans_e(f_code_1, base64.b64decode(bytes(ep, 'ascii')))
		sid, token = e_code.split('_')
		new_ep = trans_e(f_code_2, '%s_%s_%s' % (sid, vid, token))
		return base64.b64encode(bytes(new_ep, 'latin')), sid, token

	def _getStream(self,metadata):
		'''
		获取视频有哪些版本，高清，超清，标清还是...
		清晰度由高到低排序
		'''
		stream_id = ''
		stream_size = 0
		stream_segs = []
		for stream in stream_types:
			if stream['id'] in metadata['streamtypes']:
				stream_id = stream['id']
				stream_size = metadata['streamsizes'][stream_id]
				stream_segs = metadata['segs'][stream_id]
				break
		return stream_id,stream_size,stream_segs

	def query_m3u8(self,*args,**kwargs):
		new_ep,sid,token = self._generate(self.vid,self.ep)
		querydict = dict(
			ctype = 12,
			ep = new_ep,
			ev = 1,
			keyframe = 1,
			oip = self.ip,
			sid = sid,
			token = token,
			ts = int(time.time()),
			type = self.stream_id,
			vid = self.vid,
		)
		m3u8_query = get_urlencode(querydict)
		m3u8_url = r'http://pl.youku.com/playlist/m3u8?%s' % (m3u8_query,)
		page = get_html(m3u8_url)
		#For test
		with open('m3u8.json','w') as f:
			f.write(m3u8_url)
			f.write('\n')
			f.write(page)

		#从m3u8中解析视频地址
		flvlist = re.findall(r'(http://[^?]+)\.ts\?ts_start=0', page)
		if len(flvlist) == 0:
			print('error: failed parse m3u8 file! exit...')
			sys.exit(0)

		return m3u8_url,flvlist

	def query_real(self,*args,**kwargs):
		'''
		获取真实下载地址
		'''
		pass

	def getVid(self,*args,**kwargs):
		evid = ''
		pattern = re.compile(r'v\.youku\.com/v_show/id_([a-zA-Z0-9=]+)')
		r = pattern.search(self.c.url)
		if r:
			evid = r.groups()[0]
		else:
			start = self.c.url.find('id_')
			end = self.c.url.find('.html')
			if start != -1 and end != -1:
				evid = self.c.url[start+3,end]
		return evid

	def getFname(self,*args,**kwargs):
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
		pass

	def getTitle(self,*args,**kwargs):
		metadata = kwargs['metadata']
		return metadata.get('title')

	def getDesc(self,*args,**kwargs):
		desc = kwargs['title']
		pattern = re.compile(r'\<meta\s+name=\"description\"\s+content=\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def getTags(self,*args,**kwargs):
		metadata = kwargs['metadata']
		return metadata.get('tags')

	def getUsername(self,*args,**kwargs):
		metadata = kwargs['metadata']
		return metadata.get('username')

	def getUserid(self,*args,**kwargs):
		metadata = kwargs['metadata']
		return int(metadata.get('userid'))

	def getViews(self,*args,**kwargs):
		views = 1
		vid = kwargs['vid']
		if not vid: return views
		VIEW_URL = r'http://v.youku.com/QVideo/~ajax/getVideoPlayInfo?id=%s&type=vv' % (vid,)
		data = get_html(VIEW_URL)
		js = json.loads(data)
		views = js.get('vv',1)
		return views

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		pattern = re.compile(r'\<meta\s+name=\"irCategory\"\s+content\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			cat = r.groups()[0]
		return cat

	def getDuration(self,*args,**kwargs):
		metadata = kwargs['metadata']
		return ceil(float(metadata.get('seconds')))

	def getUptime(self,*args,**kwargs):
		'''
		获取视频上传时间
		'''
		raise NotImplementedError

def download(c):
	d = YouKuExtractor(c)
	return d.download()
