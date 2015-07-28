#!/usr/bin/env python3
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
		if c.debug or c.verbose:
			print('import error: %s' % (e,))
		return E_URL_NONE
	if not script:
		return E_URL_NONE
	executor = getattr(script,source)
	return executor.download(c)
