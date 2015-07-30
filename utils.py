#!/usr/bin/env python3
import gzip
import zlib
from define import *
import urllib.request
import urllib.parse
import platform
import time
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
	elif url.find('acfun.tv') != -1:
		return ACFUN
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
	将传入的参数编码
	'''
	t = urllib.parse.urlencode(kwargs)
	return t

basic_header = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Encoding':'gzip,deflate',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
	'Accept-Charset':'UTF-8,*;q=0.5',
	'Connection':'keep-alive',
	'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
}

def get_html(url):
	'''
	GET方式获取html,可以添加header，也可以不添加
	'''
	resp = None
	try:
		req = urllib.request.Request(url,data = None,headers = basic_header)
		resp = urllib.request.urlopen(req,timeout = 15)
	except Exception as e:
		print('error: get html error! url = %s' % (url,))
		return ''
	if resp is None or resp.getcode() != 200:
		print('error: get html error! errorcode = %d,url = %s' % (resp.getcode(),url,))
		return ''

	content = resp.read()
	coding = resp.getheader('Content-Encoding')
	charset = resp.getheader('Content-Type')
	#print(coding,charset)
	if coding == 'gzip':
		content = gzip.decompress(content)
	elif coding == 'deflate':
		content = zlib.decompress(content)
	else:
		pass
	if charset.find('UTF8') != -1  or charset.find('UTF-8') != -1:
		content = content.decode('utf-8')
	elif charset.find('GB2312') != -1 or charset.find('GBK') != -1:
		content = content.decode('gbk')
	elif charset.find('javascript') != -1:
		content = content.decode('utf-8')
	else: #默认也是用utf-8解码
		print('xxxxxxxxxxxxxxxxx 未知编码',charset)
		content = content.decode('utf-8')


	return content

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

def checkCondition(cls,c):
	'''
	检查是否符合下载条件
	'''
	if c.minsize[-1] == 'M' or c.minsize[-1] == 'm':
		cminsize = int(c.minsize[:-1])
	if c.maxsize[-1] == 'M' or c.maxsize[-1] == 'm':
		cmaxsize = int(c.maxsize[:-1])
	fsize = cls.fsize/(1024*1024)
	if fsize > cmaxsize:
		return C_SIZE_OVERFLOW
	if fsize < cminsize:
		return C_SIZE_SMALL

	if cls.views > c.maxviews:
		return C_VIEW_OVERFLOW
	if cls.views < c.minviews:
		return C_VIEW_SMALL

	if cls.duration > c.maxduration:
		return C_DURATION_OVERFLOW
	if cls.duration < c.minduration:
		return C_DURATION_SMALL

	path = os.path.join(cls.path,cls.fname)
	if os.path.exists(path):
		if c.force is True:
			os.remove(path)
		else:
			return C_DUPLICATE_FORCE

	if not cls.uptime:
		pass
	if cls.uptime:
		t = time.strptime(cls.uptime,'%Y%m%d')
		b = time.strptime(c.datebefore,'%Y%m%d')
		a = time.strptime(c.dateafter,'%Y%m%d')
		if t < b:
			return C_DATE_SMALL
		if t > a:
			return C_DATE_OVERFLOW

	return C_PASS


def realDownload(flvlist,tmppath,verbose,debug):
	'''
	实际的下载行为
	'''
	if debug:
		print('dsuccess:start downloading videos...segs = %d' % (len(flvlist),))
		#print('dsuccess:flvlist ',flvlist)
	if verbose:
		print('success:start downloading videos, please wait. segs = %d' % (len(flvlist),))
	finishlist = []
	for flvurl in flvlist:
		retry = 3 #最多重试3次
		if not __realDownload(flvurl,tmppath,verbose,debug):
			if debug:
				print('derror: flv file download error!')
			if verbose:
				print('error: flv file download error!')
			return False
	return True


def __realDownload(flvurl,tmppath,verbose,debug):
	'''
	逐条下载，默认每条最多重试3次
	'''
	bar = ProgressBar()
	name = os.path.basename(flvurl)
	_name = os.path.join(tmppath,name)
	resp = None
	try:
		resp = urllib.request.urlopen(flvurl,data = None,timeout = 15)
	except Exception as e:
		if debug:
			print('derror:request stream error! error = %s,url = %s' % (e,flvurl))
		if verbose:
			print('error:request stream error! retry...')
		return False
	if resp is None or resp.getcode() != 200:
		if debug:
			print('derror:request stream error! error = %s,url = %s' % (e,flvurl))
		if verbose:
			print('error:request stream error! retry...')
		return False
	length = 0
	content_length = int(resp.getheader('Content-Length'))*1.0
	with open(_name,'wb') as f:
		while True:
			data = resp.read(1024*1024)
			if len(data) == 0:
				bar.done()
				break
			f.write(data)
			length += len(data)
			bar.update(length/content_length)
		f.close()
	return True

def mergeVideos(flvlist,tmppath,path,fname,verbose,debug):
	'''
	合并视频
	'''
	if debug:
		print('success: all videos download success! start merge videos...')
	if verbose:
		print('success: all videos download success! start merge videos...')

	nameList = []
	for flvurl in flvlist:
		name = os.path.basename(flvurl)
		_name = os.path.join(tmppath,name)
		nameList.append(_name)
	outputname = os.path.join(path,fname)
	ext = getExt(flvlist[0])
	import megre_mp4
	megre_mp4.concat_mp4(nameList,outputname)

	#if ext == 'mp4': #需要合并的文件是MP4格式
	#	pass
	#elif ext in ('flv','f4v'): #需要合并的文件是FLV格式
	#	pass
	#elif ext == 'ts': #需要合并的文件是TS格式 也只能合并成ts格式，否则只能转换
	#	pass

	return True


def getExt(path):
	(filepath,filename) = os.path.split(path)
	(shortname,extname) = os.path.splitext(filename)
	return extname




#For test
#url = b'http://v.ku6.com'
#get_video_website(url)
#get_html('http://v.youku.com/v_show/id_XMTI5MzYyOTAyMA==.html')
#getIP()