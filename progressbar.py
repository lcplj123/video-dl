#!/usr/bin/env python3
import sys

class ProgressBar:
	'''
	进度条类定义
	默认格式 [######         ] 43%
	'''
	def __init__(self,fill = '#',empty = ' ',width = 50):
		self.fill = fill
		self.empty = empty
		self.width = width

	def update(self,percent):
		'''
		更新
		'''
		length = int(percent*self.width)
		s = '[%s%s] %d%%\r' % (length*self.fill,(self.width-length)*self.empty,int(percent*100))
		sys.stdout.write(s)
		sys.stdout.flush()

	def done(self):
		'''
		完成时调用
		'''
		print()
#For test
#import time
#bar = ProgressBar()
#for i in range(101):
#	bar.update(i/100.0)
#	time.sleep(0.1)
#bar.done()
