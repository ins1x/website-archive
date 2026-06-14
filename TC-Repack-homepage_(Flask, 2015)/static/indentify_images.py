#!/usr/bin/env python
#-*- encoding: utf-8 -*-

#Script to identify image files.Use PIL module
import os
import sys
import Image

search_dir = os.path.join(os.getcwd(),'images')

def file_founder(dir):
	"""Recursivelly walk,return fileslist"""
	try:
		dirs = []
		files = []
		for dirname, dirnames, filenames in os.walk(dir):
			dirs.append(dirname.decode('utf-8'))
			for subdirname in dirnames:
				dirs.append(os.path.join(dirname.decode('utf-8'), subdirname.decode('utf-8')))
			for filename in filenames:
				files.append(os.path.join(dirname.decode('utf-8'), filename.decode('utf-8')))
	except IOError:
		print "cant found dir"
	return files


files = file_founder(search_dir)
for file in files:
	im = Image.open(file)
	print file, im.format, "%dx%d" % im.size, im.mode
