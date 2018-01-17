# -*- coding:utf-8 -*-
#
# Copyright (C)  2017,  Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import optparse

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.cli.command as command
import inary.context as ctx
import inary.reactor as Reactor
import inary

class Fetch(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Fetch a package

Usage: fetch [<package1> <package2> ... <packagen>]

<packagei>: package name

Downloads the given inary packages to working directory
""")

    def __init__(self,args):
        super(Fetch, self).__init__(args)

    name = ("fetch", "fc")

    def options(self):
        group = optparse.OptionGroup(self.parser, _("fetch options"))
        self.add_options(group)
        self.parser.add_option_group(group)

    def add_options(self, group):
        group.add_option("-o", "--output-dir", action="store", default=os.path.curdir,
                               help=_("Output directory for the fetched packages"))
        group.add_option("--runtime-deps", action="store_true", default=None,
                               help=_("Bağımlılıkları ile indirme açıklaması."))

    def run(self):
        packages = inary.db.packagedb.PackageDB()
        self.init(database = False, write = False)

        if not self.args:
            self.help()
            return
        
        full_packages = []
        
        for inary_package in self.args:
            package = packages.get_package(inary_package)
            full_packages.append(inary_package)
            if ctx.config.options.runtime_deps:
                for dep in package.runtimeDependencies():
                    full_packages.append(dep.name())

        Reactor.fetch(full_packages, ctx.config.options.output_dir)
