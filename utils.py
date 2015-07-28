#!/usr/bin/env python3
import gzip
import zlib
from define import *
import urllib.request
import platform

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

basic_header = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Encoding':'gzip,deflate',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
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
		return ''
	if resp is None or resp.getcode() != 200:
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
	else:
		print('xxxxxxxxxxxxxxxxx 未知编码',charset)

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
		import socket
		import fcntl
		import struct
		def get_ip_addr(ifname = 'eth0'):
		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		pktString = fcntl.ioctl(sock.fileno(), 0x8915, struct.pack(b'256s', ifname[:15].encode('utf-8')))
		ipString  = socket.inet_ntoa(pktString[20:24])
		return ipString
	elif platform.system() == 'Windows':
		return '0.0.0.0'
	elif platform.system() == 'Darwin':
		return '0.0.0.0'


#For test
#url = b'http://v.ku6.com'
#get_video_website(url)
#get_html('http://v.youku.com/v_show/id_XMTI5MzYyOTAyMA==.html')
getIP()