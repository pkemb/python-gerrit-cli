#!/usr/bin/python
# -*- coding:utf-8 -*-
from gerritcli.utils import utc2local
import json
from gerritcli.command.account_command import account_command
import gerritcli
import sys
from copy import deepcopy
import gerrit.utils.exceptions

empty_change = {
    "project": "",
    "branch": "",
    "change_id": "",
    "subject": "",
    "status": "",
    "topic": "",
    "id": None,
    "insertions": None,
    "deletionsmeta_rev_id": None,
    "number": None,
    "created": "",
    "updated": "",
    "submitted": "",
    "registered_on": "",
    "username": "",
    "name": "",
    "email": "",
    "tags": "",
    "display_name": "",
    "active": "",
    "owner_id": None,
    "owner_name": "",
    "owner_email": "",
    "submitter_id": None,
    "submitter_name": "",
    "submitter_email": ""
}

class gerrit_change_info(gerritcli.utils.gerrit_info):
    """
    Documentation/rest-api-changes.html#change-info
    """
    def __init__(self, change, **kwargs):
        self.content = deepcopy(self.content)
        # 无需转换的内容的key
        keylist = ['project', 'branch', 'change_id', 'subject', \
                   'status', 'topic', 'id', 'insertions', 'deletions' \
                   'meta_rev_id']
        for key in keylist:
            self.content[key] = change.get(key, empty_change[key])

        # 适当的转换
        self.content['number']   = change.get('_number', empty_change['number'])
        self.content['created']  = utc2local(change['created'])
        self.content['updated']  = utc2local(change['updated'])
        self.content['submitted'] = utc2local(change.get('submitted', empty_change['submitted']))

        cmd = account_command.get()
        for key in ['owner', 'submitter']:
            if key in change:
                account = cmd.get_account(change[key]['_account_id'])
                self.content['%s_id' % key]    = account['id']
                self.content['%s_name' % key]  = account['username']
                self.content['%s_email' % key] = account['email']
            else:
                self.content['%s_id' % key]    = empty_change['%s_id' % key]
                self.content['%s_name' % key]  = empty_change['%s_name' % key]
                self.content['%s_email' % key] = empty_change['%s_email' % key]

        super().__init__(**kwargs)

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
                "handler": self.search_handler,
                "help": 'Queries changes visible to the caller.'
            },
            "get": {
                "handler": self.get_handler,
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
            gerritcli.utils.add_commmon_argument(cmd, 'output')
            gerritcli.utils.add_commmon_argument(cmd, 'header', default = self.search_default_header)
            gerritcli.utils.add_commmon_argument(cmd, 'format')

        gerritcli.utils.add_commmon_argument(self.subcmd['search'], 'limit', default=0)
        gerritcli.utils.add_commmon_argument(self.subcmd['search'], 'skip')

        # subcmd create / delete no argument
        return

    def search_change(self, query, options=None, limit=0, skip=0):
        try:
            client = gerritcli.gerrit_server.get_client()
            params = {
                'o': options,
                'S': skip,
            }
            # limit 为 0 表示没有限制
            if limit == 0:
                params['no-limit'] = ''
            else:
                params['n'] = limit

            # client.changes.search() 不支持 'no-limit' 参数，所以直接使用client.get()
            changes = client.get(f'/changes/?q={query}', params=params)
            changes_info = list()
            for change in changes:
                changes_info.append(gerrit_change_info(change))
            return changes_info
        except gerrit.utils.exceptions.ValidationError:
            print("query \"%s\" is invalid!!!" % query)
            sys.exit(1)

    def get_change(self, id):
        try:
            client = gerritcli.gerrit_server.get_client()
            change = client.changes.get(id).to_dict()
            return gerrit_change_info(change)
        except gerrit.utils.exceptions.NotFoundError:
            return gerrit_change_info(empty_change,
                    id=id, change_id=id, number=id,
                    subject='notfound', status='notfound', tags='notfound')

    def search_handler(self, args):
        header = args.header.split(",")
        changes = list()
        for q in args.query:
            changes += self.search_change(q, limit=args.limit, skip=args.skip)

        gerritcli.utils.show_info(
            changes,
            header = header,
            filename = args.output_file,
            format = args.format
        )
        return

    def get_handler(self, args):
        header = args.header.split(",")
        changes = list()
        for i in args.id:
            changes.append(self.get_change(i))

        gerritcli.utils.show_info(
            changes,
            header = header,
            filename = args.output_file,
            format = args.format
        )
        return

    def create_handler(self, args):
        print("TODO")

    def delete_handler(self, args):
        print("TODO")

