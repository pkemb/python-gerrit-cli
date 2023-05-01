#!/usr/bin/python
# -*- coding:utf-8 -*-
from gerritcli.utils import utc2local
import json
from gerritcli.command.account_command import account_command
import gerritcli
import sys
from copy import deepcopy


class gerrit_change_info():
    content = None

    def __init__(self, change):
        self.count = 0
        self.content = deepcopy(dict())
        # 无需转换的内容的key
        keylist = ['project', 'branch', 'change_id', 'subject', \
                   'status', 'topic', 'id', 'insertions', 'deletions' \
                   'meta_rev_id']
        for key in keylist:
            if key in change:
                self.content[key] = change[key]
            else:
                self.content[key] = None

        # 适当的转换
        self.content['number']   = change['_number']
        self.content['created']  = utc2local(change['created'])
        self.content['updated']  = utc2local(change['updated'])

        if 'submitted' in change:
            self.content['submitted'] = utc2local(change['submitted'])
        else:
            self.content['submitted'] = ""

        cmd = account_command.get()
        owner = cmd.get_account(change['owner']['_account_id'])

        self.content['owner_id']    = owner['id']
        self.content['owner_name']  = owner['username']
        self.content['owner_email'] = owner['email']
        if 'submitter' in change:
            submitter = cmd.get_account(change['submitter']['_account_id'])
            self.content['submitter_id']    = submitter['id']
            self.content['submitter_name']  = submitter['username']
            self.content['submitter_email'] = submitter['email']
        else:
            self.content['submitter_id']    = ""
            self.content['submitter_name']  = ""
            self.content['submitter_email'] = ""

        for key, value in self.content.items():
            try:
                setattr(self, key, value)
            except AttributeError:
                pass

    def to_dict(self):
        return self.content

class change_command(gerritcli.maincommand):
    """
    ...
    """
    command = "change"
    help = "change command help"
    search_default_header = \
        "number,owner_name,subject,status,submitter_name,created,submitted"

    def __init__(self, subparser):
        self.subcmd_info = {
            "search": {
                "handler": self.search_get_handler,
                "help": 'Queries changes visible to the caller.'
            },
            "get": {
                "handler": self.search_get_handler,
                "help": 'get change'
            },
            "create": {
                "handler": self.create_handler,
                "help": 'create change'
            },
            "delete": {
                "handler": self.delete_handler,
                "help": 'delete change'
            }
        }
        super().__init__(subparser)

    def init_argument(self):
        self.subcmd['search'].add_argument('query', help='set query condition', nargs='+')
        self.subcmd['get'].add_argument('id', help='change id or change number', nargs='+')
        for cmd in [self.subcmd['search'], self.subcmd['get']]:
            cmd.add_argument('--output', '-o',
                                    dest='output_file',
                                    help='output to file, not stdout',
                                    default=None, required=False)
            cmd.add_argument('--header',
                                    dest='header',
                                    help='output header, when output format is csv / table',
                                    default=self.search_default_header, required=False)
            cmd.add_argument('--format',
                                    dest='format',
                                    help='output format, json / csv / table',
                                    default='table', required=False)


        # subcmd create / delete no argument
        return

    def search_change(self, query):
        client = gerritcli.gerrit_server.get_client()
        changes = client.changes.search(query)
        changes_info = list()
        for change in changes:
            changes_info.append(gerrit_change_info(change))
        return changes_info

    def get_change(self, id):
        client = gerritcli.gerrit_server.get_client()
        change = client.changes.get(id).to_dict()
        return gerrit_change_info(change)

    def search_get_handler(self, args):
        header = args.header.split(",")
        if args.output_file:
            f = open(args.output_file, 'w')
        else:
            f = sys.stdout

        changes = list()
        if args.subcmd == 'search':
            for q in args.query:
                changes += self.search_change(q)
        elif args.subcmd == 'get':
            for i in args.id:
                changes.append(self.get_change(i))
        else:
            print("unknow subcmd %s!!!" % args.subcmd, file=sys.stderr)
            sys.exit(1)

        gerritcli.utils.show(
            [c.to_dict() for c in changes],
            header = header, format=args.format, file = f)

        if args.output_file:
            f.close()
        return

    def create_handler(self, args):
        print("TODO")

    def delete_handler(self, args):
        print("TODO")

