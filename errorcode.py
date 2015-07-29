#!/usr/bin/env python3
SUCCESS = 0
E_URL_NONE = 1
E_URL_ERROR = 2
E_IMPORT = 3
E_VIDEO_NOTFOUND = 4
E_VV_FAILED = 5
E_STREAM_ERROR = 6

ERROR_DICT = {
	E_URL_NONE:'arg error: url is None! exit...',
	E_IMPORT:'import error: cannot import! exit...',
	E_VIDEO_NOTFOUND:'video error: video not found...',
}
