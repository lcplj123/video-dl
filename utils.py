#!/usr/bin/env python3
import uuid
import gzip
import zlib
from define import *
import urllib.request
import urllib.parse
import platform
import time
from copy import deepcopy
from progressbar import ProgressBar

def get_video_website(url):
	'''
	根据视频地址，获取视频来自哪个网站
	'''
	if url is None or len(url) == 0:
		return UNSUPPORT
	if type(url) is not str:
		return UNSUPPORT
	if url.find('v.youku.com') != -1:
		return YOUKU
	elif url.find('tudou.com') != -1:
		return TUDOU
	elif url.find('tv.sohu.com') != -1:
		return SOHU
	elif url.find('iqiyi.com') != -1:
		return IQIYI
	elif url.find('video.sina.com.cn') != -1:
		return SINA
	elif url.find('v.qq.com') != -1:
		return QQ
	elif url.find('letv.com') != -1:
		return LETV
	elif url.find('v.pptv.com') != -1:
		return PPTV
	elif url.find('youtube.com') != -1:
		return YOUTUBE
	elif url.find('v.ku6.com') != -1:
		return KU6
	elif url.find('hunantv.com') != -1:
		return HUNANTV
	elif url.find('56.com') != -1:
		return WOLE
	elif url.find('acfun.tv') != -1:
		return ACFUN
	elif url.find('fun.tv') != -1:
		return FUN
	elif url.find('kankan.com') != -1:
		return XUNLEI
	elif url.find('v.ifeng.com') != -1:
		return IFENG
	elif url.find('miaopai.com') != -1:
		return MIAOPAI
	elif url.find('video.baomihua.com') != -1:
		return BAOMIHUA
	elif url.find('wasu.cn') != -1:
		return WASU
	elif url.find('bilibili.com') != -1:
		return BILIBILI
	elif url.find('tangdou.com') != -1:
		return TANGDOU
	elif url.find('v1.cn') != -1:
		return V1
	elif url.find('zhanqi.tv') != -1:
		return ZHANQI
	elif url.find('kumi.cn') != -1:
		return KUMI
	elif url.find('cntv.cn') != -1:
		return CNTV
	elif url.find('blip.tv') != -1:
		return BLIP
	else:
		return UNSUPPORT

def get_urlencode(kwargs):
	'''
	对传入的参数进行url编码
	'''
	t = urllib.parse.urlencode(kwargs)
	return t

basic_header = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Encoding':'gzip,deflate',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
	'Accept-Charset':'UTF-8,*;q=0.5',
	'Connection':'keep-alive',
	#'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
}

def get_header(header):
	if header:
		_header = deepcopy(basic_header)
		_header.update(header)
	else:
		_header = basic_header
	return _header

def get_html(url,header = None,data = None):
	'''
	GET方式获取html, 默认添加 basic_header
	'''
	resp = None
	_header = get_header(header)
	try:
		req = urllib.request.Request(url,data = data,headers = _header)
		resp = urllib.request.urlopen(req,timeout = 15)
	except Exception as e:
		print('error: get html error! url = %s, error = %s' % (url,e))
		return ''
	if resp is None or resp.getcode() != 200:
		print('error: get html error! errorcode = %d,url = %s' % (resp.getcode(),url,))
		return ''

	content = resp.read()
	coding = resp.getheader('Content-Encoding','')
	charset = resp.getheader('Content-Type','')

	if coding == 'gzip':
		content = gzip.decompress(content)
	elif coding == 'deflate':
		content = zlib.decompress(content)

	if charset.find('GB2312') != -1 or charset.find('GBK') != -1:
		content = content.decode('gbk')
	else:  #默认先尝试用utf8，不行再用gbk
		try:
			content = content.decode('utf-8')
		except Exception as e:
			try:
				content = content.decode('GBK')
			except Exception as e:
				pass
	return content

	#以下是resp的一些使用方法,酌情参考！
	#print('code ',resp.code)
	#print('getcode ',resp.getcode())
	#print('geturl ',resp.geturl())
	#print('url ',resp.url)
	#print('length ',resp.length)
	#print('msg ',resp.msg)
	#print('version ',resp.version)
	#print('status ',resp.status)
	#print('reason ',resp.reason)
	#print('headers ',resp.headers)
	#print('Server ',resp.getheader('Server'))
	#print('Content-Encoding ',resp.getheader('Content-Encoding'))
	#print('Content-Type ',resp.getheader('Content-Type'))
	#print('Content-Length ',resp.getheader('Content-Length'))
	#print('Connection ',resp.getheader('Connection'))
	#print('X-Cache ',resp.getheader('X-Cache'))
	#print('Age ',resp.getheader('Age'))
	#print('Date ',resp.getheader('Date'))
	#print('Accept-Ranges ',resp.getheader('Accept-Ranges'))
	#print('Cache-Control ',resp.getheader('Cache-Control'))
	#print('Set-Cookie ',resp.getheader('Set-Cookie'))
	#print('Pragma ',resp.getheader('Pragma'))

def getIP(ifname = 'eth0'):
	if platform.system() == 'Linux':
		pass
	#	import socket
	#	import fcntl
	#	import struct
	#	def get_ip_addr(ifname = 'eth0'):
	#	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	#	pktString = fcntl.ioctl(sock.fileno(), 0x8915, struct.pack(b'256s', ifname[:15].encode('utf-8')))
	#	ipString  = socket.inet_ntoa(pktString[20:24])
	#	return ipString
	elif platform.system() == 'Windows':
		return '0.0.0.0'
	elif platform.system() == 'Darwin':
		return '0.0.0.0'

def checkCondition(i,c):
	'''
	检查是否符合下载条件
	'''
	if c.minsize[-1] == 'M' or c.minsize[-1] == 'm':
		cminsize = int(c.minsize[:-1])
	if c.maxsize[-1] == 'M' or c.maxsize[-1] == 'm':
		cmaxsize = int(c.maxsize[:-1])
	fsize = i.fsize/(1024*1024)
	if fsize > cmaxsize:
		return C_SIZE_OVERFLOW
	if fsize < cminsize:
		return C_SIZE_SMALL

	if i.duration > c.maxduration:
		return C_DURATION_OVERFLOW
	if i.duration < c.minduration:
		return C_DURATION_SMALL

	path = os.path.join(i.path,i.fname)
	if os.path.exists(path):
		if c.force is True:
			os.remove(path)
		else:
			return C_DUPLICATE_FORCE

	if i.uptime != INITIAL_UPTIME: #(uptime 整型 格式 20150102)
		t = time.strptime(str(i.uptime),'%Y%m%d')
		b = time.strptime(c.datebefore,'%Y%m%d')
		a = time.strptime(c.dateafter,'%Y%m%d')
		if t > b:
			return C_DATE_SMALL
		if t < a:
			return C_DATE_OVERFLOW

	return C_PASS


def realDownload(flvlist,tmppath,header = None):
	'''
	实际的下载行为
	'''
	print('start downloading videos, please wait. segs = %d' % (len(flvlist),))
	finishlist = []
	for flvurl in flvlist:
		retry = 3 #最多重试3次
		while retry > 0:
			if __realDownload(flvurl,tmppath,header):
				break
			retry -= 1
			if retry == 0:
				print('error: flv file download error!')
				return False
	return True


def __realDownload(flvurl,tmppath,header):
	'''
	逐条下载，默认每条最多重试3次
	'''
	bar = ProgressBar()
	name = os.path.basename(flvurl)
	index = name.find('?')
	if index != -1:
		name = name[:index]
	_name = os.path.join(tmppath,name)
	resp = None
	_header = get_header(header)
	try:
		req = urllib.request.Request(flvurl,data = None,headers = _header)
		resp = urllib.request.urlopen(req,timeout = 15)
	except Exception as e:
		print('error: request stream error! retrying...')
		return False
	if resp is None or resp.getcode() != 200:
		print('error: request stream error! retry....')
		return False
	length = 0
	content_length = int(resp.getheader('Content-Length'))*1.0
	with open(_name,'wb') as f:
		while True:
			try:
				data = resp.read(1024*1024)
			except Exception as e:
				bar.done()
				return False
			if len(data) == 0:
				bar.done()
				break
			f.write(data)
			length += len(data)
			bar.update(length/content_length)
		f.close()
	return True

def getExt(path):
	index = path.find('?')
	if index != -1:
		path = path[:index]
	(filepath,filename) = os.path.split(path)
	(shortname,extname) = os.path.splitext(filename)
	return extname


def mergeVideos(flvlist,tmppath,path,fname):
	'''
	合并视频，转成相应的容器类型
	'''
	print('start merge videos...')
	nameList = []
	for flvurl in flvlist:
		name = os.path.basename(flvurl)
		index = name.find('?')
		if index != -1:
			name = name[:index]
		_name = os.path.join(tmppath,name)
		nameList.append(_name)
	outputname = os.path.join(path,fname)
	realext = getExt(outputname)
	tmpext = getExt(flvlist[0])  #形式：'.mp4  or .flv'
	tmpoutputname = os.path.join(tmppath,uuid.uuid1().hex  + tmpext)

	#合并视频 & 视频转换
	if tmpext in ('.flv','.f4v','.hlv'):
		try:
			from postproc.ffmpeg import has_ffmpeg_installed
			if has_ffmpeg_installed():
				from postproc.ffmpeg import ffmpeg_concat_flv_to_mp4
				ffmpeg_concat_flv_to_mp4(nameList, outputname)
			else:
				from postproc.join_flv import concat_flv
				concat_flv(nameList,outputname + '.flv')
		except Exception as e:
			print('merge videos error! %s' % (e,))
			return False

	elif tmpext in ('.ts',):
		try:
			from postproc.ffmpeg import has_ffmpeg_installed
			if has_ffmpeg_installed():
				from postproc.ffmpeg import ffmpeg_concat_ts_to_mp4
				ffmpeg_concat_ts_to_mp4(nameList,outputname)
			else:
				from postproc.join_ts import concat_ts
				concat_ts(nameList,outputname+'.ts')
		except Exception as e:
			print('merge videos error! %s' % (e,))
			return False

	elif tmpext in ('.mp4',):
		try:
			from postproc.ffmpeg import has_ffmpeg_installed
			if has_ffmpeg_installed():
				from postproc.ffmpeg import ffmpeg_concat_mp4_to_mp4
				ffmpeg_concat_mp4_to_mp4(nameList,outputname)
			else:
				from postproc.join_mp4 import concat_mp4
				concat_mp4(nameList,outputname)
		except Exception as e:
			print('merge videos error! %s' % (e,))
			return False
	else:
		print('unsupport %s merge videos!' % (tmpext,))
		return False

	#删除无用文件
	for x in nameList:
		if os.path.exists(x):
			os.remove(x)

	if os.path.exists(tmpoutputname):
		os.remove(tmpoutputname)

	print('*****merge videos success!*****')

	return True


def getDownloadDir(downloaddir):
	'''
	计算下载路径
	'''
	path = MAIN_DIR

	if downloaddir[0] == '.': #相对路径
		index = 0
		for ch in downloaddir:
			if ch != '.':
				break
			index += 1
		path = os.path.join(MAIN_DIR,downloaddir[index:])

	elif downloaddir[0] == '/': #绝对路径
		index = 0
		for ch in downloaddir:
			if ch != '/':
				break
			index += 1
		path = downloaddir[index:]
	else:
		print('error:downloaddir format error! it must be start with "." or "/" ,exit...')
		sys.exit(0)

	return path

#For test
#url = b'http://v.ku6.com'
#get_video_website(url)
#get_html('http://v.youku.com/v_show/id_XMTI5MzYyOTAyMA==.html')
#getIP()