#!/usr/bin/env python
#-*- encoding: utf-8 -*-
__version__ = "0.1.2"
__date__    = "30-03-2013"
__author__  = "Ins_16 <ins16publick@gmail.com>"
__about__   = "Create thumbnails for all images in directory"
__license__ = "The MIT License (MIT) Copyright (c) 2013 ins_16"

import os, sys, re
import Image
import glob

def init_directory(directory):
	"""Find all images at directory"""
	imageslist = []
	fileslist = glob.glob("*.*")

	math_re = re.compile(r"#*.(jp?g)|(png)|(gif)$")
	for i in range(len(fileslist)):
		match = math_re.search(fileslist[i])
		if match:
			imageslist.append(fileslist[i])
	return imageslist

def create_thumbnails(infile):
	outfile = os.path.splitext(infile)[0] + ".thumbnail"
	if infile != outfile:
		try:
			im = Image.open(infile)
			im.thumbnail((128, 128))
			im.save(outfile, "JPEG")
		except IOError:
			print "Cannot create thumbnail for", infile

if __name__ == "__main__":
	imageslist = init_directory(directory = os.getcwd())
	for i in range(len(imageslist)):
		create_thumbnails(imageslist[i])
