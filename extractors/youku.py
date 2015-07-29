#!/usr/bin/env python3
import re
import sys
import json
import time
from math import ceil
sys.path.append('..')
from define import *
from utils import *
from videoinfo import VideoInfo
from errorcode import *
import base64
import urllib.parse

stream_types = [
{'id':'hd3','container':'flv','profile':'1080P'},
{'id':'hd2','container':'flv','profile':'超清'},
{'id':'mp4','container':'mp4','profile':'高清'},
{'id':'flvhd','container':'flv','profile':'高清'},
{'id':'flv','container':'flv','profile':'标清'},
{'id':'3gphd','container':'3gp','profile':'3GP高清'},
]

class YouKu_Extractor(VideoInfo):
	'''
	youku下载类
	'''
	def __init__(self,c):
		super(YouKu_Extractor,self).__init__()
		self.c = c
		self.url = c.url
		self.source = YOUKU
		self.server = getIP()
		self.stream_id = ''
		self.stream_size = 0
		self.stream_segs = []

	def download(self):
		'''
		通过url下载的接口
		'''
		self.page = get_html(self.c.url)
		self.requestVideoInfo()

		return E_DOWNLOAD_SUCCESS

	def beforeDownload():
		'''
		事前处理
		'''
		pass

	def afterDownload():
		'''
		事后处理
		'''
		pass

	def requestVideoInfo(self):
		'''
		获取视频信息
		'''
		self._getEVid()
		url = r'http://v.youku.com/player/getPlayList/VideoIDS/%s/Pf/4/ctype/12/ev/1' % (self.evid,)
		#url = r'http://v.youku.com/player/getPlayList/VideoIDS/%s' % (self.evid,)
		data = get_html(url)
		js = json.loads(data)
		metadata = js['data'][0]
		#print(metadata)
		with open('test.json','w',encoding = 'utf8') as f:
			json.dump(metadata,f)

		self.vid = metadata.get('videoid')
		self.username = metadata.get('username')
		self.userid = metadata.get('userid')
		self.title = metadata.get('title')
		self.up = metadata.get('up')
		self.down = metadata.get('down')
		self.duration = metadata.get('seconds')
		self.ip = metadata.get('ip')
		self.ep = metadata.get('ep')
		self.tags = metadata.get('tags')
		self._getViews(self.vid)
		self._getDesc()
		self._getStream(metadata)
		#------------------------------------------
		self.m3u8_query()

		#self.vid = self._getVid()
		#self.evid = self._getEVid()
		#self.title = self._getTitle()
		#self.tag = self._getTag()
		#self.desc = self._getDesc()
		#self.views = self._getViews(self.vid)
		#self.category = self._getCategory()
		#self.sever = getIP()
		#self._getPlaylist()

	def _getStream(self,metadata):
		'''
		获取视频有哪些版本，高清，超清，标清还是...
		清晰度由高到低排序
		'''
		for stream in stream_types:
			if stream['id'] in metadata['streamsizes']:
				self.stream_id = stream['id']
				self.stream_size = metadata['streamsizes'][self.stream_id]
				self.stream_segs = metadata['segs'][self.stream_id]
				break

		if not self.stream_id  or self.stream_segs:
			return E_STREAM_ERROR
		else:
			return SUCCESS

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

	def m3u8_query(self):
		'''
		查询m3u8
		'''
		new_ep,sid,token = self._generate(self.vid,self.ep)
		print('new_ep:',new_ep,'sid:',sid,'token:',token)
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
		print(m3u8_url)
		page = get_html(m3u8_url)
		#print('m3u8 page',page)
		with open('m3u8.json','w') as f:
			f.write(m3u8_url)
			f.write('\n')
			f.write(page)

		#从m3u8中解析视频地址
		flvlist = re.findall(r'(http://[^?]+)\?ts_start=0', page)
		if len(flvlist) != len(self.stream_segs):
			print('视频分段缺失...')
		print(flvlist)


	def _getTitle(self):
		'''
		获取视频标题
		'''
		pattern = re.compile(r'\<h1\s+cl ass=\"title\"\s+title=\"(.*?)\"\>')
		r = pattern.search(self.page)
		if r:
			print('title:',r.groups()[0])
			return r.groups()[0]
		else:
			pattern = re.compile(r'\<meta\s+name=\"irTitle\"\s+content=\"(.*?)\"')
			r = pattern.search(self.page)
			if r:
				print('Title:',r.groups()[0])
				return r.groups()[0]
			else:
				return ''

	def _getTag(self):
		'''
		获取标签
		'''
		pattern = re.compile(r'\<meta\s+name=\"keywords\"\s+content=\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			print("tag",r.groups()[0])
			return r.groups()[0]
		else:
			return ''

	def _getDesc(self):
		'''
		获取视频描述
		'''
		desc = self.title
		errcode = SUCCESS
		pattern = re.compile(r'\<meta\s+name=\"description\"\s+content=\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			print('desc',r.groups()[0])
			#return r.groups()[0]
			desc = r.groups()[0]

		self.desc = desc
		return errcode

	def _getVid(self):
		'''
		获取视频vid
		'''
		#pattern = re.compile(r'var\s+videoId\d?\s*\=\s*[\'|\"](.*?)[\'|\"]')
		pattern = re.compile(r'var\s+videoId\s*\=\s*[\'|\"](.*?)[\'|\"]')
		r = pattern.search(self.page)
		if r:
			print('vid ',r.groups()[0])
			return r.groups()[0]
		return ''

	def _getEVid(self):
		'''
		获取编码之后的vid
		'''
		errcode = SUCCESS
		evid = ''
		pattern = re.compile(r'v\.youku\.com/v_show/id_([a-zA-Z0-9=]+)')
		r = pattern.search(self.c.url)
		if r:
			print('Evid ',r.groups()[0])
			evid = r.groups()[0]
		else:
			start = self.c.url.find('id_')
			end = self.c.url.find('.html')
			if start == -1 or end == -1:
				errcode = E_URL_ERROR
			else:
				evid = self.c.url[start+3,end]
				print('Evid ',evid)
		self.evid = evid
		return errcode

	def _getViews(self,vid):
		'''
		获取播放数 ajax请求
		'''
		errcode = SUCCESS
		views = 0
		if not vid: return E_VV_FAILED
		VIEW_URL = r'http://v.youku.com/QVideo/~ajax/getVideoPlayInfo?id=%s&type=vv' % (vid,)
		js = get_html(VIEW_URL)
		if js == "null":
			return E_VV_FAILED
		d = json.loads(js)
		views = d.get('vv',0)
		self.views = views
		return errcode
		#return d.get('vv',0)

	def _getCategory(self):
		'''
		获取类别
		'''
		pattern = re.compile(r'\<meta\s+name=\"irCategory\"\s+content\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			print('category:',r.groups())
			return r.groups()[0]
		return '未知'

	def _getPlaylist(self):
		'''
		获取播放列表，返回的json
		'''
		url = r'http://v.youku.com/player/getPlayList/VideoIDS/%s/Pf/4/ctype/12/ev/1' % (self.evid,)
		print(url)
		data = get_html(url)
		with open('test.json','w',encoding = 'utf8') as f:
			f.write(data)
		js = json.loads(data)
		metadata = js['data'][0]
		self.ep = metadata['ep']
		self.ip = metadata['ip']



def download(c):
	d = YouKu_Extractor(c)
	return d.download()
