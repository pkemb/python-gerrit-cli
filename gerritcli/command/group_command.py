#!/usr/bin/python
# -*- coding:utf-8 -*-
import gerritcli
import json
import sys
import gerrit.utils.exceptions
from gerrit.groups.groups import GerritGroups
from gerritcli.utils import utc2local
from gerritcli.utils import add_commmon_argument

empty_group = {
    'name': '',
    'url': '',
    'description': '',
    'group_id': None,
    'owner': '',
    'owner_id': '',
    'id': '',
    'created_on': '',
    'members': ''
}

class gerrit_group_info(gerritcli.utils.gerrit_info):
    """
    Documentation/rest-api-groups.html#group-info
    """
    def __init__(self, group, **kwargs):
        copy_key = ['name', 'url', 'description', 'group_id',
                    'owner', 'owner_id', 'id']
        for key in copy_key:
            self.content[key] = group.get(key, empty_group[key])

        self.content['created_on'] = utc2local(group['created_on'])
        members = list()
        if group['members'] == empty_group['members']:
            self.content['members'] = empty_group['members']
        else:
            for m in group['members']:
                members.append(m['username'])
            self.content['members'] = ';'.join(members)
        super().__init__(**kwargs)

class group_command(gerritcli.maincommand):
    """
    list / search / get / create group
    """
    command = "group"
    help = "group command"
    group_header = "group_id,name,owner,members,description"

    def __init__(self, subparser):
        self.subcmd_info = {
            "list": {
                "handler": self.list_handler,
                "help": 'list group info'
            },
            "search": {
                "handler": self.search_handler,
                "help": 'search group'
            },
            "create": {
                "handler": self.create_handler,
                "help": 'create group'
            },
            "get": {
                "handler": self.get_handler,
                "help": 'get group'
            }
        }
        super().__init__(subparser)

    def init_argument(self):
        self.subcmd['search'].add_argument('query', help='set query condition', nargs='+')
        self.subcmd['get'].add_argument('groupid',
                                        help='group id or name', nargs='+', default=['self'])
        for cmd in [self.subcmd['list'], self.subcmd['search']]:
            add_commmon_argument(cmd, 'output')
            add_commmon_argument(cmd, 'header', default = self.group_header)
            add_commmon_argument(cmd, 'format')
            add_commmon_argument(cmd, 'limit')
            add_commmon_argument(cmd, 'skip')

        add_commmon_argument(self.subcmd['get'], 'header', default = self.group_header)
        add_commmon_argument(self.subcmd['get'], 'output')
        add_commmon_argument(self.subcmd['get'], 'format')

        # subcmd create no argument
        return

    def list_group(self, **kwargs):
        """
        列出gerrit服务器上所有的group
        """
        client = gerritcli.gerrit_server.get_client()
        # fix 404 issue
        client_groups = GerritGroups(gerrit=client)
        client_groups.endpoint += '/'
        groups = client_groups.list(options=['MEMBERS'], **kwargs)

        grp_info = []
        for name in groups:
            grp_info.append(gerrit_group_info(groups[name], name=name))
        return grp_info

    def search_group(self, query, **kwargs):
        """
        Documentation/user-search-groups.html#_search_operators
        """
        try:
            client = gerritcli.gerrit_server.get_client()
            groups = client.groups.search(query, options=['MEMBERS'], **kwargs)
            grp_info = []
            for grp in groups:
                grp_info.append(gerrit_group_info(grp))
            return grp_info
        except gerrit.utils.exceptions.ValidationError:
            print("query \"%s\" is invalid!!!" % query)
            sys.exit(1)

    def get_group(self, groupid):
        try:
            client = gerritcli.gerrit_server.get_client()
            group = client.groups.get(groupid, detailed=True)
            return gerrit_group_info(group.to_dict())
        except gerrit.utils.exceptions.NotFoundError:
            return gerrit_group_info(empty_group,
                    description="notfound",
                    owner='notfound',
                    members='notfound',
                    group_id=groupid, owner_id=groupid)

    def list_handler(self, args):
        header = args.header.split(',')
        groups = self.list_group(limit = args.limit, skip = args.skip)

        gerritcli.utils.show_info(
            groups,
            header   = header,
            filename = args.output_file,
            format   = args.format)
        return True

    def search_handler(self, args):
        header = args.header.split(',')
        groups = list()
        for q in args.query:
            groups += self.search_group(q, limit=args.limit, skip=args.skip)

        gerritcli.utils.show_info(
            groups,
            header   = header,
            filename = args.output_file,
            format   = args.format)
        return True

    def create_handler(self, args):
        print("TODO")

    def get_handler(self, args):
        header = args.header.split(',')
        groups = list()
        for id in args.groupid:
            groups.append(self.get_group(id))
        gerritcli.utils.show_info(
            groups,
            header   = header,
            filename = args.output_file,
            format   = args.format)
        return

