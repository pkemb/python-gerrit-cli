#!/usr/bin/python
# -*- coding:utf-8 -*-
from gerritcli import gerrit_server
import gerritcli
import json
import urllib.parse
import sys

class gerrit_project_info(gerritcli.utils.gerrit_info):
    """
    Documentation/rest-api-projects.html#project-info
    """
    def __init__(self, project, host):
        self.content['name'] = urllib.parse.unquote(project['id'])
        self.content['state'] = project['state']
        if 'description' in project:
            self.content['description'] = project['description']
        else:
            self.content['description'] = ''

        web_links = list()
        for link in project['web_links']:
            prj_url = link['url']
            if prj_url.startswith('http'):
                web_links.append(prj_url)
            else:
                web_links.append(f"{host}{prj_url}")
        self.content['web_links'] = ','.join(web_links)

        super().__init__()

class project_command(gerritcli.maincommand):
    """
    list / search / create / delete project
    """
    command = "project"
    help = "project command"
    project_header = "name,state,web_links"

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
        self.subcmd['search'].add_argument('query', help='set query condition', nargs='+')
        for cmd in [self.subcmd['list'], self.subcmd['search']]:
            cmd.add_argument('--output', '-o',
                                dest='output_file',
                                help='output to file, not stdout',
                                default=None, required=False)
            cmd.add_argument('--header',
                                dest='header',
                                help='output header, when output format is csv / table',
                                default=self.project_header, required=False)
            cmd.add_argument('--format',
                                dest='format',
                                help='output format, json / csv / table',
                                default='table', required=False)
            cmd.add_argument('--limit',
                                dest = 'limit',
                                help = 'limit the search result',
                                type = int, default = None, required=False)
            cmd.add_argument('--skip',
                                dest = 'skip',
                                help = 'skip the number of result',
                                type = int, default = None, required=False)

        # subcmd create / delete no argument
        return

    def list_project(self, host, **kwargs):
        """
        列出gerrit服务器上所有的project
        待实现的选项：isall / limit / skip / project_type / description / branch / state
        """
        client = gerritcli.gerrit_server.get_client()
        projects = client.projects.list(**kwargs)
        prj_info = []
        for prj in projects:
            prj_info.append(gerrit_project_info(projects[prj], host))
        return prj_info

    def search_project(self, query, host, **kwargs):
        client = gerritcli.gerrit_server.get_client()
        projects = client.projects.search(query, **kwargs)
        prj_info = []
        for prj in projects:
            prj_info.append(gerrit_project_info(prj, host))
        return prj_info

    def list_handler(self, args):
        header = args.header.split(',')
        host = gerrit_server.get_host(args.server)
        projects = self.list_project(host, limit = args.limit, skip = args.skip)

        gerritcli.utils.show_info(
            projects,
            header   = header,
            filename = args.output_file,
            format   = args.format)
        return True

    def search_handler(self, args):
        header = args.header.split(',')
        host = gerrit_server.get_host(args.server)
        projects = list()
        for q in args.query:
            projects += self.search_project(q, host, limit=args.limit, skip=args.skip)

        gerritcli.utils.show_info(
            projects,
            header   = header,
            filename = args.output_file,
            format   = args.format)
        return True

    def create_handler(self, args):
        print("TODO")

    def delete_handler(self, args):
        print("TODO")

