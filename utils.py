#!/usr/bin/env python3
from define import *

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

#For test
#url = b'http://v.ku6.com'
#get_video_website(url)