# -*- coding:utf-8 -*-
#
#
# Old author: Copyright (C) 2005 - 2011, Tubitak/UEKAE 
#
# Copyright (C) 2017 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import optparse

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.cli.command as command
import inary.context as ctx
import inary.api

class UpdateRepo(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Update repository databases

Usage: update-repo [<repo1> <repo2> ... <repon>]

<repoi>: repository name

Synchronizes the INARY databases with the current repository.
If no repository is given, all repositories are updated.
""")

    def __init__(self,args):
        super(UpdateRepo, self).__init__(args)

    name = ("update-repo", "ur")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("update-repo options"))

        group.add_option("-f", "--force", action="store_true",
                               default=False,
                               help=_("Update database in any case"))

        self.parser.add_option_group(group)

    def run(self):
        self.init(database = True)

        if self.args:
            repos = self.args
        else:
            repos = inary.api.list_repos()

        inary.api.update_repos(repos, ctx.get_option('force'))
