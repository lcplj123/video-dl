#!/usr/bin/env python3
import sys
from optparse import OptionParser
from condition import Condition
from dispatch import Dispatcher

if __name__ == '__main__':
	[...]
	parser = OptionParser()
	parser.add_option('-u','--url',action = 'store',type = 'string',dest = 'url',help = 'video url to download.')
	parser.add_option('-S','--maxsize',action = 'store',type = 'string',dest = 'maxsize',default = '8192M',help = 'max file size to download.default is 8192MB.')
	parser.add_option('-s','--minsize',action = 'store',type = 'string',dest = 'minsize',default = '0M',help = 'min file size to download.default is 0MB.')
	parser.add_option('-d','--datebefore',action = 'store',type = 'string',dest = 'datebefore',default = '29990101',help = 'video before this date will not be downloaded.default is 29990101')
	parser.add_option('-D','--dateafter',action = 'store',type = 'string',dest = 'dateafter',default = '20000101',help = 'video after this date will not be downloaded.default is 19990101')
	parser.add_option('-T','--maxduration',action = 'store',type = 'int',dest = 'maxduration',default = 86400,help = 'max duration to download.default is 86400.')
	parser.add_option('-t','--minduration',action = 'store',type = 'int',dest = 'minduration',default = 10,help = 'min duration to download.default is 10.')
	parser.add_option('-o','--sockettimeout',action = 'store',type = 'int',dest = 'sockettimeout',default = 15,help = 'socket time out in seconds. default is 15.')
	parser.add_option('-l','--downloaddir',action = 'store',type = 'string',dest = 'downloaddir',default = '.',help = 'directory to download video.if start with . ,means relative path else start with / ,means absolute path. default is . .')
	parser.add_option('-n','--nametype',action = 'store',type = 'string',dest = 'nametype',default = 'vid',help = 'how to name the video file. vid and title. default is vid. ')
	parser.add_option('-f',action = 'store_true',dest = 'force',default = False,help = 'overwrite the existing file.default is False.')
	parser.add_option('-m',action = 'store_true',dest = 'makejson',default = False,help = 'if create json file that describe the video. default is False.')
	parser.add_option('-e','--ext',action = 'store',type = 'string',dest = 'ext',default = 'mp4',help = 'output video extended name. default is mp4.')
	options,args = parser.parse_args()
	url = options.__dict__.get('url')
	c = Condition(**options.__dict__)
	if url is None or len(url) == 0:
		print('error: video url is None! exit...')
		sys.exit(0)

	Dispatcher(c)