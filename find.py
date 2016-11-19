#!/usr/bin/env python2.7
import os
import sys
import stat
import fnmatch
import re

#variables
PROGRAM_NAME = os.path.basename(sys.argv[0])
TYPE=''
X= False
R= False
W= False
E= False
NAME=''
PATH=''
REGEX=''
PERM=''
NEWER=''
UID=''
GID=''
input = sys.argv[1]
index=1

#functions
def error(message, exit_code=1):
    print >>sys.stderr, message
    sys.exit(exit_code)
def inode_info(path):
    try:
	return os.stat(path)
    except OSError as e:
	#error('Could not open link {}: {}' .format(path, e))
	brokenSL= True	
	return os.lstat(path)
def DirCheck(path):
    try:
	if os.listdir(path): #os.listdir(path) lists the full path of... of path
		return False # directory is not empty
	else:
		return True #directory is empty
    except: 
	return False #cannot access directory; treat it like it's empty
def modTime(new, old): #checks if path was modified more recently than NEWER (inputted file). True if new is newer than old!
	try:
		if os.path.getmtime(new)<=os.path.getmtime(old):
			return True
		else:
			return False
	except OSError as e:
		return True # treat it as if old is older than new

def usage(exit_code=0):
    error('''Usage: find.py directory [options]...
	Options:

	    -type [f|d]     File is of type f for regular file or d for directory

	    -executable     File is executable and directories are searchable to user
	    -readable       File readable to user
	    -writable       File is writable to user

	    -empty          File or directory is empty

	    -name  pattern  Base of file name matches shell pattern
	    -path  pattern  Path of file matches shell pattern
	    -regex pattern  Path of file matches regular expression

	    -perm  mode     File's permission bits are exactly mode (octal)
	    -newer file     File was modified more recently than file

	    -uid   n        File's numeric user ID is n
	    -gid   n        File's numeric group ID is n
	'''
	.format(PROGRAM_NAME), exit_code)
def include(path): #returns true if item should be included in output, otherwise false
	brokenSL= False
	emptyDir= DirCheck(path) #emptyDir= True if the directory is empty
	s= inode_info(path)

	if (TYPE.strip()=="d" and not stat.S_ISDIR(s.st_mode)): # if type d incated it wants a file, but it's not a file... then return false
		return False
	if (TYPE.strip()=="f" and not stat.S_ISREG(s.st_mode)):
		return False
	if (X and not os.access(path, os.X_OK)):
		return False
	if (R and not os.access(path, os.R_OK)):
		return False
	if (W and not os.access(path, os.W_OK)):
		return False
	## is there a file? better be empty. a directory? better have no folders. 
	# a link? better be broken
	if (E and not ((stat.S_ISREG(s.st_mode) and os.path.getsize(path)==0) or (stat.S_ISDIR(s.st_mode) and emptyDir) or (stat.S_ISLNK(s.st_mode) and brokenSL))): 
		return False
	if not (NAME=='' or fnmatch.fnmatch(os.path.basename(path), NAME)):
		return False
	if not (PATH=='' or fnmatch.fnmatch(path, PATH)): #(name, pattern)
		return False
	if not (REGEX=='' or re.search(REGEX, path)): #(pattern, name) 
		return False
	if not (PERM=='' or int(PERM)==int(oct(stat.S_IMODE(s.st_mode)))): 
		return False
	if not (NEWER=='' or not modTime(path, NEWER)): #path should be more recent than NEWER
		return False
	if not (GID=='' or int(GID)==s.st_gid):
		return False
	if not (UID=='' or int(UID)==s.st_uid):
		return False
	return True

#Parse Command line arguments flags
while index < len(sys.argv):
	#if (sys.argv[1]=="-h"): #check for -h flag
	#	usage(0)
        if (sys.argv[index]=="-type"):
                TYPE= sys.argv[index+1]
        if (sys.argv[index]=="-executable"):
                X= True
        if (sys.argv[index]=="-readable"):
                R= True
        if (sys.argv[index]=="-writable"):
                W= True
        if (sys.argv[index]=="-empty"):
                E= True
        if (sys.argv[index]=="-name"):
                NAME= sys.argv[index+1]
        if (sys.argv[index]=="-path"):
                PATH= sys.argv[index+1]
        if (sys.argv[index]=="-regex"):
                REGEX= sys.argv[index+1]
        if (sys.argv[index]=="-perm"):
                PERM= sys.argv[index+1]
        if (sys.argv[index]=="-newer"):
                NEWER= sys.argv[index+1]
        if (sys.argv[index]=="-uid"):
                UID= int(sys.argv[index+1])
        if (sys.argv[index]=="-gid"):
                GID= int(sys.argv[index+1])
        index+=1

# Main Execution

if include(input): # check the input directory as well as it's subdirectories
	print input
for root, dirs, files in os.walk(input, followlinks=True):
	for name in files+dirs:
		path= os.path.join(root, name)
		if (include(path)):
			print os.path.join(root, name)






