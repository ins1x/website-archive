import os, re, sys
# -*- coding: utf-8 -*-
# TEST MODULE

appdir = os.getcwd()

def framework_parsing(appdir):
	""" 
	Determines which framework is used.
	Return array [framework as str, filepath as path]
	"""
	patterns = {"Flask": "Flask", "Django": "Django", "CherryPy": "cherrypy", "KissPy": "kiss", "Tornado": "tornado", "Falcon": "falcon", "Bottle": "bottle"}

	def pywalker(path):
		""" Recursivelly search files at directory. Return Array of *.py files without current script. """
		os.chdir(path)
		fileslist = []
		for root, dirs, files in os.walk(path):
			for name in files:
				if name.lower().endswith(".py"):
					file = os.path.join(root, name)
					file = os.path.normpath(file)
					if file != sys.argv[0]:
						fileslist.append(file)
		return fileslist

	def sub_search(file, value):
		""" Search modules in files by pattern."""
		try:
			os.chdir(appdir)
			line_numb = 1
			with open(file, "r") as f:
				for line in f.readlines():
					line_numb += 1
					pattern = "".join(["import ", value])
					patterncmp = re.compile(pattern)
					match = patterncmp.search(line)
					if match:
						#debug print(" ".join([str(line_numb),str(line)]))
						return True
					if line_numb > 30:
						break
		except OSError:
			print("OS Error. Can not access to files")
	# Alternately processes the files from the list and searches for modules
	fileslist = pywalker(appdir)
	for file in fileslist:
		for key, value in patterns.items():
			data = sub_search(file, value)
			if data:
				return key, file

parsing_result = framework_parsing(appdir)
appfullpath = parsing_result[1]
appname = os.path.basename(appfullpath)
framework = parsing_result[0]
if framework == "Flask":
	devserverport = 5000
elif framework == "Django":
	devserverport = 8000
elif framework == "CherryPy":
	devserverport = 8080
elif framework == "KissPy":
	devserverport = 8080
elif framework == "Bottle":
	devserverport = 8080
elif framework == "Falcon":
	devserverport = 8000
elif framework == "Torando":
	devserverport = 8888
print(appfullpath, appname, framework, devserverport)