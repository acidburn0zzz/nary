#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import glob
import sys
import shutil
import fileinput
import re

import get
from pisitools_functions import *
from shelltools import *

def dobin(sourceFile, destinationDirectory = '/usr/bin'):
    '''insert a executable file into /bin or /usr/bin'''

    ''' example call: pisitools.dobin("bin/xloadimage", "/bin", "xload") '''
    executable_insinto(sourceFile, get.installDIR() + destinationDirectory)
 
def doconfd():
    #FIXME: AdditionalFiles
    pass

def dodir(destinationDirectory):
    '''creates a directory tree'''
    makedirs(get.installDIR() + destinationDirectory)

def dodoc(*sourceFiles):
    '''inserts the files in the list of files into /usr/share/doc/PACKAGE''' 
    readable_insinto(get.installDIR() + "/usr/share/doc/" + get.srcTAG(), *sourceFiles)

def doenvd():
    #FIXME: AdditionalFiles
    pass

def doexe(sourceFile, destinationDirectory):
    '''insert a executable file into destination directory'''
    
    ''' example call: pisitools.doexe("kde-3.4.sh", "/etc/X11/Sessions")'''
    executable_insinto(sourceFile, get.installDIR() + destinationDirectory)

def dohard(sourceFile, destinationFile):
    '''creates hard link between sourceFile and destinationFile'''
    #FIXME: How can i use hard-links in Python?
    pass

def dohtml(*sourceFiles):
    '''inserts the files in the list of files into /usr/share/doc/PACKAGE/html'''
 
    ''' example call: pisitools.dohtml("doc/doxygen/html/*")'''
    destionationDirectory = os.path.join(get.installDIR(), "usr/share/doc" ,get.srcTAG(), "html")

    if not can_access_directory(destionationDirectory):
        makedirs(os.getcwd() + destionationDirectory)

    allowed_extensions = ['.png', '.gif', '.html', '.htm', '.jpg', '.css', '.js']
    disallowed_directories = ['CVS']

    for sourceFile in sourceFiles:
        for source in glob.glob(sourceFile):
            if os.path.isfile(source) and os.path.splitext(source)[1] in allowed_extensions:
                os.system("install -m0644 %s %s" % (source, destionationDirectory))
            if os.path.isdir(source) and os.path.basename(source) not in disallowed_directories:
                for root, dirs, files in os.walk(source):
                    for source in files:
                        if os.path.splitext(source)[1] in allowed_extensions:
                            makedirs(destionationDirectory)
                            os.system("install -m0644 %s %s" % (os.path.join(root, source), destionationDirectory))
                            print "install -m0644 %s %s" % (os.path.join(root, source), destionationDirectory)

def doinfo(*sourceFiles):
    '''inserts the info files in the list of files into /usr/share/info'''
    readable_insinto(get.infoDIR(), *sourceFiles)

def doinitd():
    #FIXME: AdditionalFiles
    pass

def dojar():
    '''installs jar files into /usr/share/PACKAGE/lib, and adds to /usr/share/PACKAGE/classpath.env'''
    pass

def dolib(sourceFile, destinationDirectory = '/usr/lib'):
    '''insert the library info /usr/lib'''
    sourceFile = os.path.join(get.workDIR(), get.srcDIR(), sourceFile)
    destinationDirectory = get.installDIR() + destinationDirectory
    print destinationDirectory
    makedirs(destinationDirectory)
    os.system("install -m0644 %s %s" % (sourceFile, destinationDirectory))

def dolib_a():
    '''insert the static library info /usr/lib with permission 0644'''
    pass

def dolib_so():
    '''insert the static library info /usr/lib with permission 0755'''
    pass

def doman(*sourceFiles):
    '''inserts the man pages in the list of files into /usr/share/man/'''

    '''example call: pisitools.doman("man.1", "pardus.*")'''
    if not can_access_directory(get.manDIR()):
        makedirs(get.manDIR())

    #FIXME: splitext
    for sourceFile in sourceFiles:
        for source in glob.glob(sourceFile):
            try:
                pageName, pageDirectory = source.split('.')
            except ValueError:
                print "doman: Wrong man page file"
                sys.exit(1)
                
            makedirs(get.manDIR() + '/man%s' % pageDirectory) 
            os.system("install -m0644 %s %s" % (source, get.manDIR() + '/man%s' % pageDirectory))

def domo_(*sourceFiles):
    '''inserts the mo files in the list of files into /usr/share/locale/LOCALE/LC_MESSAGES'''
    pass

def domove(source, destination):
    '''moves sourceFile/Direcroty into destinationFile/Directory'''
    
    ''' example call: pisitools.domove("/usr/bin/bash", "/bin/bash")'''
    ''' example call: pisitools.domove("/usr/bin/", "/usr/sbin")'''
    makedirs(get.installDIR() + os.path.dirname(destination))
    shutil.move(get.installDIR() + source, get.installDIR() + destination)

def dopython():
    '''FIXME: What the hell is this?'''
    pass

def dosed(sourceFile, findPattern, replacePattern = ''):
    '''replaces patterns in sourceFile'''
    
    ''' example call: pisitools.dosed("/etc/passwd", "caglar", "cem")'''
    ''' example call: pisitools.dosym("/etc/passwd", "caglar")'''
    ''' example call: pisitools.dosym("Makefile", "(?m)^(HAVE_PAM=.*)no", r"\1yes")'''

    if can_access_file(sourceFile):
        for line in fileinput.input(sourceFile, inplace = 1):
            line = re.sub(findPattern, replacePattern, line)
            sys.stdout.write(line)
    else:
        raise FileError("File doesn't exists or permission denied...")

def dosbin(sourceFile, destinationDirectory = '/usr/sbin'):
    '''insert a executable file into /sbin or /usr/sbin'''
    
    ''' example call: pisitools.dobin("bin/xloadimage", "/sbin") '''
    executable_insinto(sourceFile, get.installDIR() + destinationDirectory)
        
def dosym(sourceFile, destinationFile):
    '''creates soft link between sourceFile and destinationFile'''

    ''' example call: pisitools.dosym("/usr/bin/bash", "/bin/bash")'''
    makedirs(get.installDIR() + os.path.dirname(destinationFile))

    try:
        os.symlink(sourceFile, get.installDIR() + destinationFile)
    except OSError:
        print "dosym: File exists..."

''' ************************************************************************** '''

def insinto(destinationDirectory, sourceFile,  destinationFile = ''):
    '''insert a sourceFile into destinationDirectory as a destinationFile with same uid/guid/permissions'''
    makedirs(get.installDIR() + destinationDirectory)

    for file in glob.glob(sourceFile):
        if can_access_file(file):
            shutil.copy(sourceFile, get.installDIR() + os.path.join(destinationDirectory, destinationFile))

''' ************************************************************************** '''

def newdoc(sourceFile, destinationFile):
    shutil.move(sourceFile, destinationFile)
    readable_insinto(get.installDIR() + "/usr/share/doc/" + get.srcTAG(), destinationFile)

def newman(sourceFile, destinationFile):
    shutil.move(sourceFile, destinationFile)
    doman(destinationFile)

''' ************************************************************************** '''

def remove(sourceFile):
    unlink(get.installDIR() + sourceFile)

def removeDir(destinationDirectory):
    unlinkDir(get.installDIR() + destinationDirectory)

''' ************************************************************************** '''

def preplib():
    '''prepare all library files for installation'''
    pass

def preplib_so():
    '''prepare dynamic library files for installation'''
    pass
