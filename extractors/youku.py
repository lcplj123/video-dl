#!/usr/bin/env python3
import os
import re
import sys
import json
import time
from math import ceil
sys.path.append('..')
from define import *
from utils import *
from videoinfo import VideoInfo
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
		self.ext = c.format
		self.source = YOUKU
		self.server = getIP()
		self.stream_id = ''
		self.stream_size = 0
		self.stream_segs = []
		self.path = self._getDownloadDir()
		tmppath = os.path.join(self.path,'tmp')
		if not os.path.exists(tmppath):
			os.mkdir(tmppath)
		self.tmppath = tmppath

	def download(self):
		'''
		通过url下载的接口
		'''
		self.page = get_html(self.c.url)
		self.requestVideoInfo()
		ret = checkCondition(self,self.c)
		if ret == C_PASS: #可以下载
			#真正下载视频
			if not realDownload(self.flvlist,self.tmppath,self.c.verbose,self.c.debug):
				sys.exit(0)

			#合并视频
			if not mergeVideos(self.flvlist,self.tmppath,self.path,self.fname,self.c.verbose,self.c.debug):
				sys.exit(0)

			#删除临时文件
			for flvurl in self.flvlist:
				name = os.path.basename(flvurl)
				_name = os.path.join(tmppath,name)
				try:
					os.remove(_name)
				except Exception as e:
					continue
			if self.debug:
				print('dsuccess: merge success, download success!')
			if self.verbose:
				print('success: video download success. %s' % (self.fname,))

		else: #不能下载
			if self.c.debug:
				print('derror:video do not math conditions! code = %d' % (ret,))
			if self.c.verbose:
				print('error: video do not math conditions. code = %d' % (ret,))
			sys.exit(0)

	def requestVideoInfo(self):
		'''
		获取视频信息
		'''
		if self.c.verbose:
			print('start request video info...')

		self.evid = self._getEVid()
		if not self.evid: sys.exit()
		url = r'http://v.youku.com/player/getPlayList/VideoIDS/%s/Pf/4/ctype/12/ev/1' % (self.evid,)
		data = get_html(url)
		js = json.loads(data)
		if not js['data']:
			if self.c.verbose:
				print('error: input url has something error and cannot resolve! url = %s' % (self.c.url,))
			if self.c.debug:
				print('derror: returned bad data! url = %s' % (self.c.url,))
			sys.exit()

		metadata = js['data'][0]
		if self.c.debug:
			with open('test.json','w',encoding = 'utf8') as f:
				json.dump(metadata,f)

		self.vid = metadata.get('videoid')
		self.username = metadata.get('username')
		self.userid = metadata.get('userid')
		self.title = metadata.get('title')
		self.up = metadata.get('up')
		self.down = metadata.get('down')
		self.duration = ceil(float(metadata.get('seconds')))
		self.tags = metadata.get('tags')
		self.views = self._getViews(self.vid)
		self.desc = self._getDesc()
		self.category = self._getCategory()
		self.ip = metadata.get('ip')
		self.ep = metadata.get('ep')
		self.stream_id, self.stream_size, self.stream_segs = self._getStream(metadata)
		if self.stream_id == '' or self.stream_size == 0:
			if self.c.debug:
				print('derror: stream id not found!')
			if self.c.verbose:
				print('error: stream not found!')
			sys.exit(0)
		self.fsize = int(self.stream_size)
		if self.c.downloadname == 'title':
			self.fname = '%s.%s' % (self.title[:32],self.ext)
		else:
			self.fname = '%s.%s' % (self.evid,self.ext)

		m3u8_url,flvlist = self.m3u8_query()
		self.m3u8 = m3u8_url
		self.flvlist = flvlist

	def postProc(self,flvlist):
		'''
		合并视频到一个文件，并转成mp4 格式
		'''
		pass

	def _getDownloadDir(self):
		'''
		计算下载路径
		'''
		path = MAIN_DIR

		if self.c.downloaddir[0] == '.': #相对路径
			index = 0
			for ch in self.c.downloaddir:
				if ch != '/':
					break
				index += 1
			path = os.path.join(MAIN_DIR,self.c.downloaddir[index:])

		elif self.c.downloaddir[0] == '/': #绝对路径
			index = 0
			for ch in self.c.downloaddir:
				if ch != '/':
					break
				index += 1
			path = self.c.downloaddir[index-1:]
		else:
			if self.c.debug:
				print('derror: downloaddir error! dir = %s' % (self.c.downloaddir,))
			if self.c.verbose:
				print('error:downloaddir format error! it must be start with . or /')
			sys.exit()

		return path

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
		if self.c.debug:
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
		page = get_html(m3u8_url)
		if self.c.debug:
			with open('m3u8.json','w') as f:
				f.write(m3u8_url)
				f.write('\n')
				f.write(page)

		#从m3u8中解析视频地址
		flvlist = re.findall(r'(http://[^?]+)\?ts_start=0', page)
		if len(flvlist) == 0:
			if self.c.debug:
				print('derror:failed parse video download path from m3u8 file!')
			if self.c.verbose:
				print('error: failed parse m3u8 file! exit...')
			sys.exit(0)

		if len(flvlist) != len(self.stream_segs):
			if self.c.debug:
				print('视频段与码流段不匹配...')
				print(flvlist)

		return m3u8_url,flvlist

	def _getDesc(self):
		'''
		获取视频描述
		'''
		desc = self.title
		pattern = re.compile(r'\<meta\s+name=\"description\"\s+content=\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def _getEVid(self):
		'''
		获取编码之后的vid
		'''
		evid = ''
		pattern = re.compile(r'v\.youku\.com/v_show/id_([a-zA-Z0-9=]+)')
		r = pattern.search(self.c.url)
		if r:
			if self.c.debug:
				print('Evid ',r.groups()[0])
			evid = r.groups()[0]
		else:
			start = self.c.url.find('id_')
			end = self.c.url.find('.html')
			if start == -1 or end == -1:
				if self.c.debug:
					print('derror: get evid error!')
			else:
				evid = self.c.url[start+3,end]
				if self.c.debug:
					print('Evid ',evid)

		return evid

	def _getViews(self,vid):
		'''
		获取播放数 ajax请求
		'''
		views = 1
		if not vid: return views
		VIEW_URL = r'http://v.youku.com/QVideo/~ajax/getVideoPlayInfo?id=%s&type=vv' % (vid,)
		data = get_html(VIEW_URL)
		js = json.loads(data)
		views = js.get('vv',1)
		return views

	def _getCategory(self):
		'''
		获取类别
		'''
		cat = '未知'
		pattern = re.compile(r'\<meta\s+name=\"irCategory\"\s+content\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			cat = r.groups()[0]
		return cat

def download(c):
	d = YouKu_Extractor(c)
	return d.download()
