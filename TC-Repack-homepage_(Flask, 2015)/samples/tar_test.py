#!/usr/bin/env python
#-*- encoding: utf-8 -*-
__about__   = """Test script"""

import tarfile
import os
import yaml
import re

cfg = yaml.load(open('settings.yaml','r'))
folders = cfg['folders']
snaps_folder = folders.get('snaps_folder')

dir = snaps_folder
fileslist = os.listdir(dir)
targz_ext = re.compile(r".*[\.tar.gz]$")
for i in range(len(fileslist)):
	if targz_ext.match(fileslist[i]):
		print fileslist[i]
		tar = tarfile.open(fileslist[i], "r:*")
		for tarinfo in tar:
			print tarinfo.name, "is", tarinfo.size, "bytes in size and is"