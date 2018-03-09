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
#

import re
import time
import gzip
import gettext
import datetime
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import xml.dom.minidom as minidom
from xml.parsers.expat import ExpatError

import inary.db
import inary.data.metadata as Metadata
import inary.analyzer.dependency
import inary.db.itembyrepo
import inary.db.lazydb as lazydb

class PackageDB(lazydb.LazyDB):

    def __init__(self):
        lazydb.LazyDB.__init__(self, cacheable=True)
        self.init()

    def init(self):
        self.__package_nodes = {} # Packages
        self.__revdeps = {}       # Reverse dependencies
        self.__obsoletes = {}     # Obsoletes
        self.__replaces = {}      # Replaces

        repodb = inary.db.repodb.RepoDB()

        for repo in repodb.list_repos():
            doc = repodb.get_repo_doc(repo)
            self.__package_nodes[repo] = self.__generate_packages(doc)
            self.__revdeps[repo] = self.__generate_revdeps(doc)
            self.__obsoletes[repo] = self.__generate_obsoletes(doc)
            self.__replaces[repo] = self.__generate_replaces(doc)

        self.pdb = inary.db.itembyrepo.ItemByRepo(self.__package_nodes, compressed=True)
        self.rvdb = inary.db.itembyrepo.ItemByRepo(self.__revdeps)
        self.odb = inary.db.itembyrepo.ItemByRepo(self.__obsoletes)
        self.rpdb = inary.db.itembyrepo.ItemByRepo(self.__replaces)

    def __generate_replaces(self, doc):
        for x in doc.getElementsByTagName("Package"):
            if x.getElementsByTagName("Replaces")[0]:
                return x.getElementsByTagName("Name")[0].firstChild.data

    def __generate_obsoletes(self, doc):
        distribution = doc.getElementsByTagName("Distribution")[0]
        obsoletes = distribution and distribution.getElementsByTagName("Obsoletes")[0].firstChild.data
        src_repo = doc.getElementsByTagName("SpecFile")[0].firstChild.data is not None

        if not obsoletes or src_repo:
            return []

        return [x.childNodes[0].data for x in obsoletes.getElementsByTagName("Package")]

    def __generate_packages(self, doc):
        pdict={}
        for x in doc.getElementsByTagName("Package"):
            pdict[x.getElementsByTagName("Name")[0].firstChild.data]= gzip.zlib.compress(x.toxml('utf-8'))
        return pdict

    def __generate_revdeps(self, doc):
        revdeps = {}
        for node in doc.childNodes:
            if node.nodeType == node.ELEMENT_NODE and node.tagName == "Package":
                name = node.getElementsByTagName('Name')[0].firstChild.data
                deps = node.getElementsByTagName('RuntimeDependencies')
                if deps:
                    for dep in deps.getElementsByTagName("Dependency"):
                        revdeps.setdefault(dep.childNodes[0].data, set()).add((name, dep.toString()))

        return revdeps

    def has_package(self, name, repo=None):
        return self.pdb.has_item(name, repo)

    def get_package(self, name, repo=None):
        pkg, repo = self.get_package_repo(name, repo)
        return pkg

    def search_in_packages(self, packages, terms, lang=None):
        resum = '<Summary xml:lang=.({0}|en).>.*?{1}.*?</Summary>'
        redesc = '<Description xml:lang=.({0}|en).>.*?{1}.*?</Description>'
        if not lang:
            lang = inary.sxml.autoxml.LocalText.get_lang()
        found = []
        for name in packages:
            xml = self.pdb.get_item(name)
            if terms == [term for term in terms if re.compile(term, re.I).search(name) or \
                                            re.compile(resum.format(lang, term), re.I).search(xml) or \
                                            re.compile(redesc.format(lang, term), re.I).search(xml)]:
                found.append(name)
        return found

    def search_package(self, terms, lang=None, repo=None, fields=None, cs=False):
        """
        fields (dict) : looks for terms in the fields which are marked as True
        If the fields is equal to None the method will search on all fields

        example :
        if fields is equal to : {'name': True, 'summary': True, 'desc': False}
        This method will return only package that contents terms in the package
        name or summary
        """
        resum = '<Summary xml:lang=.({0}|en).>.*?{1}.*?</Summary>'
        redesc = '<Description xml:lang=.({0}|en).>.*?{1}.*?</Description>'
        if not lang:
            lang = inary.sxml.autoxml.LocalText.get_lang()
        if not fields:
            fields = {'name': True, 'summary': True, 'desc': True}
        found = []
        for name, xml in self.pdb.get_items_iter(repo):
            if terms == [term for term in terms if (fields['name'] and \
                    re.compile(term, re.I).search(name)) or \
                    (fields['summary'] and \
                    re.compile(resum.format(lang, term), 0 if cs else re.I).search(xml)) or \
                    (fields['desc'] and \
                    re.compile(redesc.format(lang, term), 0 if cs else re.I).search(xml))]:
                found.append(name)
        return found

    def __get_version(self, meta_doc):
        history = meta_doc.getElementsByTagName("History")[0]
        version = history.getElementsByTagName("Update")[0].getElementsByTagName("Version")[0].firstChild.data
        release = history.getElementsByTagName("Update")[0].getAttribute["release"]

        # TODO Remove None
        return version, release, None

    def __get_distro_release(self, meta_doc):
        distro = meta_doc.getElementsByTagName("Distribution")[0].firstChild.data
        release = meta_doc.getElementsByTagName("DistributionRelease")[0].firstChild.data

        return distro, release

    def get_version_and_distro_release(self, name, repo):
        if not self.has_package(name, repo):
            raise Exception(_('Package {} not found.').format(name))

        pkg_doc = minidom.parseString(self.pdb.get_item(name, repo))
        return self.__get_version(pkg_doc) + self.__get_distro_release(pkg_doc)

    def get_version(self, name, repo):
        if not self.has_package(name, repo):
            raise Exception(_('Package {} not found.').format(name))

        pkg_doc = minidom.parseString(self.pdb.get_item(name, repo)).documentElement
        return self.__get_version(pkg_doc)

    def get_package_repo(self, name, repo=None):
        pkg, repo = self.pdb.get_item_repo(name, repo)
        package = Metadata.Package()
        package.parse(pkg)
        return package, repo

    def which_repo(self, name):
        return self.pdb.which_repo(name)

    def get_obsoletes(self, repo=None):
        return self.odb.get_list_item(repo)

    def get_isa_packages(self, isa):
        repodb = inary.db.repodb.RepoDB()

        packages = set()
        for repo in repodb.list_repos():
            doc = repodb.get_repo_doc(repo)
            for package in doc.getElementsByTagName("Package"):
                if package.getElementsByTagName("IsA"):
                    for node in package.getElementsByTagName("IsA"):
                        if node.childNodes[0].data == isa:
                            packages.add(package.getElementsByTagName("Name")[0].firstChild.data)
        return list(packages)

    def get_rev_deps(self, name, repo=None):
        try:
            rvdb = self.rvdb.get_item(name, repo)
        except Exception: #FIXME: what exception could we catch here, replace with that.
            return []

        rev_deps = []
        for pkg, dep in rvdb:
            node = minidom.parseString(dep).documentElement
            dependency = inary.analyzer.dependency.Dependency()
            dependency.package = node.firstChild.data
            #FIXME
            if node.attributes():
                attr = node.attributes()[0]
                dependency.__dict__[attr] = node.getAttribute(attr)
            rev_deps.append((pkg, dependency))
        return rev_deps

    # replacesdb holds the info about the replaced packages (ex. gaim -> pidgin)
    def get_replaces(self, repo=None):
        pairs = {}

        for pkg_name in self.rpdb.get_list_item():
            xml = self.pdb.get_item(pkg_name, repo)
            package = minidom.parseString(xml).documentElement
            replaces_tag = package.getElementsByTagName("Replaces")
            if replaces_tag:
                for node in replaces_tag.getElementsByTagName("Package"):
                    r = inary.relation.Relation()
                    # XXX Is there a better way to do this?
                    r.decode(node, [])
                    if inary.replace.installed_package_replaced(r):
                        pairs.setdefault(r.package, []).append(pkg_name)

        return pairs

    def list_packages(self, repo):
        return self.pdb.get_item_keys(repo)

    def list_newest(self, repo, since=None):
        packages = []
        historydb = inary.db.historydb.HistoryDB()
        if since:
            since_date = datetime.datetime(*time.strptime(since, "%Y-%m-%d")[0:6])
        else:
            since_date = datetime.datetime(*time.strptime(historydb.get_last_repo_update(), "%Y-%m-%d")[0:6])

        for pkg in self.list_packages(repo):
            enter_date = datetime.datetime(*time.strptime(self.get_package(pkg).history[-1].date, "%Y-%m-%d")[0:6])
            if enter_date >= since_date:
                packages.append(pkg)
        return packages
