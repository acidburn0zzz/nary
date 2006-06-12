#!/usr/bin/python
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author: Eray Ozkural

import sys
import os

import pisi
import pisi.context as ctx

usage = "Usage: pisimedia <pisi-index.xml>"

if len(sys.argv)!=2:
    print usage
    sys.exit(1)
    
#op = sys.argv[1]
#if not op in  ['install', 'upgrade']:
#    print usage
#    sys.exit(2)

idx = sys.argv[1]    
if not os.path.exists(idx):
    print "pisi index %s cannot be found" % idx
    
pisi.api.init()

try:
    tmpid = 0
    tmprepo = 'pisimedia%d' % tmpid
    while ctx.repodb.has_repo(tmprepo):
        tmpid += 1
        tmprepo = 'pisimedia%d' % tmpid
    pisi.api.add_repo(tmprepo, idx, at = 0)
    pisi.api.update_repo(tmprepo)
    packages = ctx.packagedb.list_packages(repo=tmprepo)
    pisi.api.install(packages, reinstall=True)
except Exception, e:
    ctx.ui.error(e)
    if ctx.repodb.has_repo(tmprepo):
        pisi.api.remove_repo(tmprepo)
pisi.api.finalize()
