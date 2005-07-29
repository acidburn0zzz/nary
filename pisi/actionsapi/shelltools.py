#!/usr/bin/python
#-*- coding: utf-8 -*-

# Standart Python Modules
import os
import glob
import shutil

# ActionsAPI Modules
import get

def can_access_file(sourceFile):
    '''test the existence of file'''
    return os.access(sourceFile, os.F_OK)

def can_access_directory(destinationDirectory):
    '''test readability, writability and executablility of directory'''
    return os.access(destinationDirectory, os.R_OK | os.W_OK | os.X_OK)

def makedirs(destinationDirectory):
    try:
        os.makedirs(destinationDirectory)
    except OSError:
        pass

def chmod(sourceFile, mode = 0755):
    for file in glob.glob(sourceFile):
        os.chmod(file, mode)
            
def unlink(sourceFile):
    os.unlink(sourceFile)

def unlinkDir(sourceDirectory):
    if can_access_directory(sourceDirectory):
        shutil.rmtree(sourceDirectory)
    else:
        print "unlinkDir: remove failed..."

def move(sourceFile, destinationFile):
    shutil.move(sourceFile, destinationFile)

def touch(sourceFile):
    for file in glob.glob(sourceFile):
        os.utime(file, None)

def cd(directoryName = ''):
    current = os.getcwd()
    if directoryName:
        os.chdir(directoryName)
    else:
        os.chdir(os.path.dirname(current))

def ls(sourceDirectory):
    return os.listdir(sourceDirectory)

def export(key, value):
    os.environ[key] = value
        
