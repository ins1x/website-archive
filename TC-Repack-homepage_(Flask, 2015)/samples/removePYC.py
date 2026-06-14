#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,glob

def main():
	fileslist = glob.glob("*.pyc")
	for file in fileslist:
		os.remove(file)
		print file,"-was deleted"

main()