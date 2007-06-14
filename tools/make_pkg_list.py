#!/usr/bin/python

import sys
import os

def usage():
	print '''Usage:
	$0 <dir>
	Where <dir> is the path to the metas.'''

if len(sys.argv) < 2:
	usage()
	sys.exit()
	
dir = sys.argv[1]
	
if not os.path.exists(dir):
	print dir, "doesn't exist."
	usage()
	sys.exit()
	
dst = file(dir+"/packages_list.db", "w")
	
for i in os.listdir(dir):
	if not os.path.isfile(dir+"/"+i):
		print "Is a directory", i
		continue
	
	if not i.startswith('meta-'):
		print "Is no meta file", i
		continue
	
	src = file(dir+"/"+i)
	for i in src.readlines():
		i = i.rstrip("\n")
		if i.startswith("Name:"):
			trash,name = i.split(": ")
		elif i.startswith("Version:"):
			trash,ver = i.split(": ")
		elif i.startswith("Release:"):
			trash,rel = i.split(": ")
		elif i.startswith("Size:"):
			trash,size = i.split(": ")
		
	src.close()
	
	dst.write(name+";"+ ver +";"+ rel +";"+ size +";\n")

dst.close()
