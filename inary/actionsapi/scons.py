# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.


# Inary Modules
import inary.context as ctx

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

# ActionsAPI Modules
import inary.actionsapi
import inary.actionsapi.get as get
from inary.actionsapi.shelltools import system

class MakeError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

class InstallError(inary.actionsapi.Error):
    def __init__(self, value=''):
        inary.actionsapi.Error.__init__(self, value)
        self.value = value
        ctx.ui.error(value)

def make(parameters = ''):
    if system('scons %s %s' % (get.makeJOBS(), parameters)):
        raise MakeError(_('Make failed.'))

def install(parameters = 'install', prefix = get.installDIR(), argument='prefix'):
    if system('scons %s=%s %s' % (argument, prefix, parameters)):
        raise InstallError(_('Install failed.'))
