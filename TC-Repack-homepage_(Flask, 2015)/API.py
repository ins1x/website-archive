#!/usr/bin/env python
#-*- encoding: utf-8 -*-
__version__ = "0.1.2"
__date__    = "28-01-2015"
__about__   = "Flask singlepage site API to generates the home page and upload to hosting"
__author__  = "Ins_16 <ins16publick@gmail.com>"
__license__ = "Creative Commons Attribution 3.0 BY-NC (c) 2015 ins_16"


# Changelog:
# [-] - Deleted, [+] - Added, [!] - Fixed, [*] - Testing.
# --v--0.1.0
# The first terrible but working code release
# --v--0.1.1
# + Backup functions to API
# + Replacement links local css link on Dropbox
# + User's home directory is automatically determined
# --v--0.1.2
# ! Code to support autodetect dropbox folders on Win
# + Offline generation (without upload files to dropbox)
# + All variables are transferred in settings.yaml single file

import os.path
import sys
import urllib2
import string
import shutil
import tarfile
import time
import yaml

# config init from settings.yaml
cfg = yaml.load(open('settings.yaml','r'))
exclude = cfg['exclude']
folders = cfg['folders']
site_folder = folders.get('site_folder')
snaps_folder = folders.get('snaps_folder')
local_web_server_addr = cfg['local_web_server_addr']
main_page = cfg['main_page']
dropbox_user_url = cfg['dropbox_user_url']
main_css_file = cfg['main_css_file']
# < ---------- END config init ---------->

# Autodetect Dropbox folders on local computer
if sys.platform.startswith('linux'):
	User_homefolder = os.getenv("HOME")
	Dropbox_site_url = os.path.join(User_homefolder, "Dropbox/Public/site")
if sys.platform.startswith('win32'):
	User_homefolder = os.getenv("HOMEPATH")
	Dropbox_site_url = os.path.join(User_homefolder, "Dropbox/Public/site")
else:
	print "Autodetect folders failed"
		
def Release(Load_to_dropbox=True):
	"""Native script for the rapid publication of the page from the local server to the public website.
	Attention to the script in this configuration is designed for singlepage-site."""
	css_path = os.path.join(site_folder, main_css_file)
	f = urllib2.urlopen(local_web_server_addr)
	outfile = open(main_page, "w")
	page = f.read()
	#modifies a static reference to online version
	pagelink = dropbox_user_url + main_css_file
	new = string.replace(page, main_css_file, pagelink)
	outfile.write(new)
	outfile.close()
	#Put file to Dropbox
	if Load_to_dropbox == True:
		if os.path.exists(Dropbox_local_folder):
			shutil.move(main_page, os.path.join(Dropbox_local_folder, main_page))
			shutil.copy(css_path, os.path.join(Dropbox_local_folder,main_css_file))

def Create_snaps(snaps_directory = snaps_folder,site_directory = site_folder):
	"""Create tar.gz archive in snaps directory"""	
	excludelist = exclude
	try:
		dt_time = time.strftime("%A_%d.%m.%Y")
		outname = 'backup_' + dt_time + '.tar.gz'
		outfile = os.path.join(snaps_directory, outname)
		if os.path.exists(site_directory) and os.path.exists(snaps_directory):
			tar = tarfile.open(outfile, "w:gz")
			os.chdir(site_directory)
			fileslist = os.listdir('.')
			for file in excludelist:
				fileslist.remove(file)
			for file in fileslist:
				tar.add(file)
			for tarinfo in tar:
				print tarinfo.name, "is", tarinfo.size, "bytes is",
				if tarinfo.isreg():
					print "file."
				elif tarinfo.isdir():
					print "directory."
				else:
					print "something else."
			tar.close()
			statinfo = os.stat(outfile)
			b_size = statinfo.st_size
			k_size = statinfo.st_size / 1000
			print "Totally", b_size, "bytes", k_size, "kbytes"
		return outfile
	except ValueError:
		print "ValueError: Check, input and output backup folders, check exclude fileslist"
