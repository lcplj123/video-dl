#!/usr/bin/env python3

def Dispatcher(c):
	'''
	调度到实际下载模块
	'''
	source = get_video_website(c.url)
	_source = "extractors.%s" % (source,)
	try:
		script = __import__(_source,globals(),locals(),[],0)
	except Exception as e:
		print('import error: %s' % (e,))
		return
	if not script:
