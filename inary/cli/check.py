# -*- coding:utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE (Licensed with GPLv2)
# More details about GPLv2, please read the COPYING.OLD file.
#
# Copyright (C) 2016 - 2019, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# Please read the COPYING file.
#

import optparse

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.operations.check as check
import inary.cli.command as command
import inary.context as ctx
import inary.util as util
import inary.db


class Check(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Verify installation

    Usage: check [<package1> <package2> ... <packagen>]
           check -c <component>

    <packagei>: package name

    A cryptographic checksum is stored for each installed
    file. Check command uses the checksums to verify a package.
    Just give the names of packages.

    If no packages are given, checks all installed packages.
    """)

    def __init__(self, args):
        super(Check, self).__init__(args)
        self.installdb = inary.db.installdb.InstallDB()
        self.componentdb = inary.db.componentdb.ComponentDB()

    name = ("check", None)

    def options(self):
        group = optparse.OptionGroup(self.parser, _("check options"))

        group.add_option("-c", "--component",
                         action="store",
                         default=None,
                         help=_("Check installed packages under "
                                "given component."))

        group.add_option("--config",
                         action="store_true",
                         default=False,
                         help=_("Checks only changed config files of "
                                "the packages."))

        self.parser.add_option_group(group)

    def run(self):
        self.init(database=True, write=False)

        component = ctx.get_option('component')
        if component:
            installed = inary.db.installdb.InstallDB().list_installed()
            component_pkgs = self.componentdb.get_union_packages(component,
                                                                 walk=True)
            pkgs = list(set(installed) & set(component_pkgs))
        elif self.args:
            pkgs = self.args
        else:
            ctx.ui.info(_('Checking all installed packages.') + '\n')
            pkgs = inary.db.installdb.InstallDB().list_installed()

        necessary_permissions = True

        # True if we should also check the configuration files
        check_config = ctx.get_option('config')

        # Line prefix
        prefix = _('Checking integrity of \"{}\".')

        # Determine maximum length of messages for proper formatting
        maxpkglen = max([len(_p) for _p in pkgs])

        for pkg in pkgs:
            if self.installdb.has_package(pkg):
                check_results = check.check(pkg, check_config)
                ctx.ui.info("{0}    {1}".format(prefix.format(pkg), (' ' * (maxpkglen - len(pkg)))), noln=True)

                if check_results['missing'] or check_results['corrupted'] \
                        or check_results['config']:
                    ctx.ui.info(_("Broken"), color='brightred')
                elif check_results['denied']:
                    # We can't deduce a result when some files
                    # can't be accessed
                    necessary_permissions = False
                    ctx.ui.info(_("Unknown"), color='yellow')
                else:
                    ctx.ui.info(_("OK"), color='green')
                    continue

                # Dump per file stuff
                for fpath in check_results['missing']:
                    ctx.ui.info(_("Missing file: \"/{}\"").format(fpath), color='brightred')

                for fpath in check_results['denied']:
                    ctx.ui.info(_("Access denied: \"/{}\"").format(fpath), color='yellow')

                for fpath in check_results['corrupted']:
                    ctx.ui.info(_("Corrupted file: \"/{}\"").format(fpath), color='brightyellow')

                for fpath in check_results['config']:
                    ctx.ui.info(_("Modified configuration file: \"/{}\"").format(fpath),
                                color='brightyellow')

            else:
                # Package is not installed
                ctx.ui.info(_('Package \"{}\" not installed.').format(pkg))

        if not necessary_permissions:
            ctx.ui.info("")
            ctx.ui.warning(_("Inary was unable to check the integrity of "
                             "packages which contain files that you don't "
                             "have read access.\n"
                             "Running the check under a privileged user "
                             "may help fixing this problem."))
