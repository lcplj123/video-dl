#!/usr/bin/env python3
import os
import sys
from optparse import OptionParser
from condition import Condition
from dispatch import Dispatcher

if __name__ == '__main__':
	[...]
	parser = OptionParser()
	parser.add_option('-u','--url',action = 'store',type = 'string',dest = 'url',help = 'video url to download.')
	parser.add_option('-s','--maxsize',action = 'store',type = 'string',dest = 'maxsize',default = '8192M',help = 'max file size to download.default is 1MB.')
	parser.add_option('-p','--minsize',action = 'store',type = 'string',dest = 'minsize',default = '1M',help = 'min file size to download.default is 8192MB.')
	parser.add_option('-c','--datebefore',action = 'store',type = 'string',dest = 'datebefore',default = '29990101',help = 'video before this date will not be downloaded.default is 29990101')
	parser.add_option('-e','--dateafter',action = 'store',type = 'string',dest = 'dateafter',default = '20000101',help = 'video after this date will not be downloaded.default is 19990101')
	parser.add_option('-w','--maxviews',action = 'store',type = 'int', dest = 'maxviews',default = 9999999999999,help = 'max views to download. default is 9999999999999')
	parser.add_option('-x','--minviews',action = 'store',type = 'int', dest = 'minviews',default = 1,help = 'min views to download. default is 1')
	parser.add_option('-i','--maxduration',action = 'store',type = 'int',dest = 'maxduration',default = 86400,help = 'max duration to download.default is 86400.')
	parser.add_option('-g','--minduration',action = 'store',type = 'int',dest = 'minduration',default = 10,help = 'min duration to download.default is 10.')
	parser.add_option('-j',action = 'store_true',dest = 'makejson',default = False,help = 'if create json file that describe the video. default is False.')
	parser.add_option('-v',action = 'store_true',dest = 'verbose',default = False, help = 'output detailed message during downlaod. default is True.')
	parser.add_option('-t','--sockettimeout',action = 'store',type = 'int',dest = 'sockettimeout',default = 15,help = 'socket time out in seconds. default is 15.')
	parser.add_option('-l','--downloaddir',action = 'store',type = 'string',dest = 'downloaddir',default = '.',help = 'directory to download video.if start with . ,means relative path else start with / ,means absolute path. default is . .')
	parser.add_option('-f','--downloadname',action = 'store',type = 'string',dest = 'downloadname',default = 'vid',help = 'how to name the video file. vid and title. default is vid. ')
	parser.add_option('-d',action = 'store_true',dest = 'debug',default = True,help = 'open debug mode.')
	parser.add_option('-o',action = 'store_true',dest = 'force',default = False,help = 'overwrite the existing file.default is False.')
	parser.add_option('-m','--format',action = 'store',type = 'string',dest = 'format',default ='mp4',help = 'output video format.default is mp4,others mkv/flv.')
	options,args = parser.parse_args()
	url = options.__dict__.get('url')
	c = Condition(**options.__dict__)
	if url is None or len(url) == 0:
		if c.debug or c.verbose:
			print('error: video url is None! exit...')
		sys.exit(0)
	if c.format not in ('mp4',):
		if c.debug or c.verbose:
			print('derror: format arg error! exit...')
		sys.exit(0)
	Dispatcher(c)