# -*- coding:utf-8 -*-
#
#
# Old author: Copyright (C) 2005 - 2011, Tubitak/UEKAE 
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
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

import inary
import inary.api
import inary.cli.command as command
import inary.context as ctx

class AddRepo(command.Command, metaclass=command.autocommand):
    __doc__ = _("""Add a repository

Usage: add-repo <repo> <indexuri>

<repo>: name of repository to add
<indexuri>: URI of index file

NB: We support only local files (e.g., /a/b/c) and http:// URIs at the moment
""")

    def __init__(self, args):
        super(AddRepo, self).__init__(args)
        self.repodb = inary.db.repodb.RepoDB()

    name = ("add-repo", "ar")

    def options(self):

        group = optparse.OptionGroup(self.parser, _("add-repo options"))
        group.add_option("--ignore-check", action="store_true", default=False, help=_("Ignore repository distribution check"))
        group.add_option("--no-fetch", action="store_true", default=False, help=_("Does not fetch repository index and does not check distribution match"))
        group.add_option("--at", action="store",
                               type="int", default=None,
                               help=_("Add repository at given position (0 is first)"))
        self.parser.add_option_group(group)

    def warn_and_remove(self, message, repo):
        ctx.ui.warning(message)
        inary.api.remove_repo(repo)

    def run(self):

        if len(self.args) == 2:
            self.init()
            name, indexuri = self.args

            if ctx.get_option('no_fetch'):
                if not ctx.ui.confirm(_('Add {} repository without updating the database?\nBy confirming '
                                        'this you are also adding the repository to your system without '
                                        'checking the distribution of the repository.\n'
                                        'Do you want to continue?').format(name)):
                    return

            inary.api.add_repo(name, indexuri, ctx.get_option('at'))

            if not ctx.get_option('no_fetch'):
                try:
                    inary.api.update_repo(name)
                except (inary.Error, IOError):
                    warning = _("{0} repository could not be reached. Removing {0} from system.").format(name)
                    self.warn_and_remove(warning, name)
        else:
            self.help()
            return
