#!/usr/bin/python
# -*- coding:utf-8 -*-
from gerritcli import subcommand
from gerritcli import gerrit_server
import gerritcli
import json

class project_command(subcommand):
    """
    list / search / create / delete project
    """
    command = "project"
    help = "project command"

    def init_argument(self):
        self.subcmd = self.cmd_parser.add_subparsers(
                                help='',
                                dest='project_command',
                                required=True)

        self.subcmd_list = self.subcmd.add_parser('list', help = 'list project info')
        self.subcmd_list.add_argument('--urltype',
                                        dest='urltype',
                                        help='project url type, can be \'clone\' \'gitiles\', default value is \'clone\'',
                                        default='clone',
                                        required=False)
        self.subcmd_list.set_defaults(project_handler=self.list)

        self.subcmd_search = self.subcmd.add_parser('search', help = 'search project')
        self.subcmd_search.set_defaults(project_handler=self.search)

        self.subcmd_create = self.subcmd.add_parser('create', help = 'create project')
        self.subcmd_create.set_defaults(project_handler=self.create)

        self.subcmd_delete = self.subcmd.add_parser('delete', help = 'delete project')
        self.subcmd_delete.set_defaults(project_handler=self.delete)
        return

    def get_project_url(self, server, web_links, urltype):
        host = gerrit_server.get_host(server)
        for link in web_links:
            prj_url = link['url']
            if prj_url.startswith('http'):
                continue
            if urltype == 'clone':
                prj_url = prj_url.replace('/plugins/gitiles', '')
                return f"{host}{prj_url}"
            elif urltype == 'gitiles':
                return f"{host}{prj_url}"
            else:
                return ""
        return None

    def list(self, args):
        """
        列出gerrit服务器上所有的project
        待实现的选项：isall / limit / skip / project_type / description / branch / state
        """
        client = gerritcli.gerrit_server.get_client()
        projects = client.projects.list()
        for prj in projects:
            web_links = projects[prj]['web_links']
            print(self.get_project_url(args.server, web_links, args.urltype))
        return True

    def search(self, args):
        print("TODO")

    def create(self, args):
        print("TODO")

    def delete(self, args):
        print("TODO")

    def handler(self, args):
        return args.project_handler(args)
