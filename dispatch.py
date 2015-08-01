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
		print('error: import module %s error! %s' % (source,e))
		sys.exit(0)

	if not script:
		print('error: imported script is None! exit...')
		sys.exit(0)

	executor = getattr(script,source)
	if not executor:
		print('error: not find script entrance! exit...')
		sys.exit(0)

	return executor.download(c)
