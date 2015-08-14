#!/usr/bin/env python3
import os
#目录定义
MAIN_DIR = os.path.split(os.path.realpath(__file__))[0]
INITIAL_UPTIME = 10000101

#----------------------
#website define
UNSUPPORT = None
YOUKU = 'youku'
YOUTUBE = 'youtube'
TUDOU = 'tudou'
IQIYI = 'iqiyi'
SOHU = 'sohu'
QQ = 'qq'
PPTV = 'pptv'
SINA = 'sina'
CNTV = 'cntv'
KU6 = 'ku6'
WOLE = 'wole'
XUNLEI = 'xulei'
ACFUN = 'acfun'
FUN = 'fun'
BAOMIHUA = 'baomihua'
BILIBILI = 'bilibili'
BLIP = 'blip'
HUNANTV = 'hunantv'
IFENG = 'ifeng'
KUMI = 'kumi'
LETV = 'letv'
MIAOPAI = 'miaopai'
TANGDOU = 'tangdou'
V1 = 'v1'
WASU = 'wasu'
ZHANQI = 'zhanqi'


#------------------------
#条件检测结果表示
C_PASS = 0
C_SIZE_OVERFLOW = 1
C_SIZE_SMALL = 2
C_DATE_OVERFLOW = 3
C_DATE_SMALL = 4
C_DURATION_OVERFLOW = 5
C_DURATION_SMALL = 6
C_DUPLICATE_FORCE = 7