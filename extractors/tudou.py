#!/usr/bin/env python3
import re
import sys
import json
sys.path.append('..')
from define import *
from utils import *
from extractor import BasicExtractor
from xml.dom.minidom import parseString

class TuDouExtractor(BasicExtractor):
	'''
	土豆视频下载器
	'''
	def __init__(self,c):
		super(TuDouExtractor,self).__init__(c,TUDOU)

	def download(self):
		'''
		下载入口
		'''
		print('tudou:start downloading ...')
		retry = 3
		while retry >=0 :
			self.page = get_html(self.c.url)
			if self.page: break
			retry -= 1
		if not self.page:
			print('error: request video info error,check url. %s' % (self.c.url,))
			sys.exit(0)

		#For test
		with open('test.html','w') as f:
			f.write(self.page)

		pattern = re.compile(r'vcode\s*[:=]\s*\'([^\']+)\'')
		r = pattern.search(self.page)
		if r:
			vcode = r.groups()[0]
			youku_url = r'http://v.youku.com/v_show/id_%s.html' % (vcode,)
			self.c.url = youku_url
			from extractors.youku import download
			download(self.c)
		else:
			self._download()

	def _download(self):
		self.iid = self._getIID()
		self.i.vid = self.iid
		self.i.title = self.getTitle()
		self.i.desc = self.getDesc()
		self.i.tags = self.getTags()
		self.i.category = self.getCategory()
		self.i.views = self.getViews()
		self.i.username,self.i.userid = self.getUser()

		js = None

		url = r'http://www.tudou.com/outplay/goto/getItemSegs.action?iid=%s' % (self.iid,)
		data = get_html(url)
		js = json.loads(data)
		if js and 'status' not in js:
			pass
		else:
			js = None
			pattern = re.compile(r'segs:\s*\'(\{.*?\})\'')
			r = pattern.search(self.page)
			if r:
				js = json.loads(r.groups()[0])

		if not js:
			print('regret: unsupported url. %s' % (self.c.url,))
			sys.exit(0)

		maxkey = max(js.keys())
		print(js[maxkey])
		self.flvlist = self.query_real(js = js[maxkey])
		self.i.fsize = self.getFsize(js = js[maxkey])
		self.i.duration = int(self.getDuration(js = js[maxkey]) / 1000)
		self.i.m3u8 = self.query_m3u8(iid = self.iid,st = maxkey)
		self.i.fname = self.getFname()

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

	def _getIID(self):
		iid = ''
		pattern = re.compile(r'iid\s*[:=]\s*(\S+)')
		r = pattern.search(self.page)
		if r:
			iid = r.groups()[0]
		return iid

	def query_m3u8(self,*args,**kwargs):
		iid = kwargs['iid']
		st = kwargs['st']
		m3u8_url = r'http://vr.tudou.com/v2proxy/v2.m3u8?it=%s&st=%s&pw=' % (iid,st)
		return m3u8_url

	def query_real(self,*args,**kwargs):
		jdata = kwargs['js']
		vids = [d['k'] for d in jdata]
		url = r'http://ct.v2.tudou.com/f?id=%s'
		realurls = [
		[n.firstChild.nodeValue.strip()
		for n in parseString(get_html(url%(vid,))).getElementsByTagName('f')
		][0]
		for vid in vids
		]
		return realurls

	def getVid(self,*args,**kwargs):
		pass

	def getFsize(self,*args,**kwargs):
		size = 0
		jdata = kwargs['js']
		size = sum(d['size'] for d in jdata)
		return size

	def getTitle(self,*args,**kwargs):
		title = ''
		pattern = re.compile(r'\<meta\s+name\s*=\s*\"irTitle\"\s+content\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			title = r.groups()[0]
		if not title:
			pattern = re.compile(r'kw\s*[:=]\s*[\'\"]([^\n]+?)\'\s*\n')
			r = pattern.search(self.page)
			if r:
				title = r.groups()[0]
		return title

	def getDesc(self,*args,**kwargs):
		desc = ''
		pattern = re.compile(r'\<meta\s+name\s*=\s*\"description\"\s+content\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			desc = r.groups()[0]
		return desc

	def getTags(self,*args,**kwargs):
		tags = ''
		pattern = re.compile(r'\<meta\s+name\s*=\s*\"keywords\"\s+content\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			tags = r.groups()[0]
		return tags.split(' ')

	def getUser(self,*args,**kwargs):
		name = ''
		uid = ''
		pattern = re.compile(r'onic\:\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			name = r.groups()[0]
		pr = re.compile(r'oname\:\s*\"(.*?)\"')
		m = pr.search(self.page)
		if m:
			uid = m.groups()[0]
		return name,uid

	def getViews(self,*args,**kwargs):
		views = 1
		url = r'http://index.youku.com/dataapi/getData?num=100011&icode=%s'
		pattern = re.compile(r'icode\:\s*[\'|\"](.*?)[\'|\"]')
		r = pattern.search(self.page)
		if r:
			icode = r.groups()[0]
		else:
			icode = 'xx'
		jdata = get_html(url%(icode,))
		js = json.loads(jdata)
		result = js['result']
		if result:
			views = result.get('totalVv')

		return views + 1

	def getCategory(self,*args,**kwargs):
		cat = '未知'
		pattern = re.compile(r'\<meta\s+name\s*=\s*\"irCategory\"\s+content\s*=\s*\"(.*?)\"')
		r = pattern.search(self.page)
		if r:
			cat = r.groups()[0]
		return cat

	def getDuration(self,*args,**kwargs):
		duration = 0
		jdata = kwargs['js']
		duration = sum(d['seconds'] for d in jdata)
		return duration

	def getUptime(self,*args,**kwargs):
		pass


def download(c):
	d = TuDouExtractor(c)
	return d.download()