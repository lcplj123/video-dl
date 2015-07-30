#!/usr/bin/env python3
import sys
from define import *
from utils import get_video_website

def Dispatcher(c):
	'''
	调度到实际下载模块
	'''
	source = get_video_website(c.url)
	_source = r"extractors.%s" % (source,)
	script = None
	try:
		script = __import__(_source, globals(), locals(), [], 0)
	except Exception as e:
		if c.debug:
			print('derror: import %s error! %s' % (_source,e))
		if c.verbose:
			print('error: import module %s error! %s' % (source,e))
		sys.exit()

	if not script:
		if c.debug:
			print('derror: import script is None!')
		if c.verbose:
			print('error! import script is None!')
		return
	executor = getattr(script,source)
	return executor.download(c)
