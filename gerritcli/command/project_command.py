#!/usr/bin/python
# -*- coding:utf-8 -*-
from gerritcli import gerrit_server
import gerritcli
import json

class project_command(gerritcli.maincommand):
    """
    list / search / create / delete project
    """
    command = "project"
    help = "project command"

    def __init__(self, subparser):
        self.subcmd_info = {
            "list": {
                "handler": self.list_handler,
                "help": 'list project info'
            },
            "search": {
                "handler": self.search_handler,
                "help": 'search project'
            },
            "create": {
                "handler": self.create_handler,
                "help": 'create project'
            },
            "delete": {
                "handler": self.delete_handler,
                "help": 'delete project'
            }
        }
        super().__init__(subparser)

    def init_argument(self):
        self.subcmd['list'].add_argument('--urltype',
                                        dest='urltype',
                                        help='project url type, can be \'clone\' \'gitiles\', default value is \'clone\'',
                                        default='clone',
                                        required=False)

        # subcmd search / create / delete no argument
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

    def list_handler(self, args):
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

    def search_handler(self, args):
        print("TODO")

    def create_handler(self, args):
        print("TODO")

    def delete_handler(self, args):
        print("TODO")

