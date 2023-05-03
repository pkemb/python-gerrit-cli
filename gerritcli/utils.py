#!/usr/bin/python
# -*- coding:utf-8 -*-

from datetime import datetime
from prettytable import PrettyTable
import time
import json
import sys
import csv
from copy import deepcopy

now = time.time()
utc_offset = datetime.fromtimestamp(now) - datetime.utcfromtimestamp(now)

def utc2local(utc):
    # [0:-3] -> ns to us
    try:
        utc_datetime = datetime.strptime(utc[0:-3], "%Y-%m-%d %H:%M:%S.%f")
        local = utc_datetime + utc_offset
        return local.strftime("%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return utc

def show_json(data, header, file):
    print(json.dumps(data, indent=4), file=file)
    return

def show_table(data, header, file):
    if header is None:
        header = data[0].keys()

    table = PrettyTable(header)
    for d in data:
        table.add_row([d[key] for key in header])
    print(table, file=file)
    return

def show_csv(data, header, file):
    if header is None:
        header = data[0].keys()

    writer = csv.writer(file)
    writer.writerow(header)
    for d in data:
        writer.writerow([d[key] for key in header])
    return

show_handler = {
    "json": show_json,
    "csv": show_csv,
    "table": show_table
}
support_format = show_handler.keys()

def show(data, header = None, file = sys.stdout, format='table'):
    if format in show_handler:
        show_handler[format](data, header, file)

def check_format(format):
    if format not in support_format:
        print("format %s not support" % (format), file=sys.stderr)
        sys.exit(1)

def check_header(header, support_header):
    if header is None:
        return
    set_header  = set(header)
    set_support = set(support_header)
    if not set_header.issubset(set_support):
        print("header \"%s\" not support" % (','.join(set_header - set_support)), file=sys.stderr)
        sys.exit(1)

def show_info(infos, header = None , filename = None, format = 'table'):
    """
    :param infos: gerrit_info 类组成的列表
    :param header: 表头列表，可以为None
    :param filename: 重定向输出的文件
    :param format: 输出格式，支持 table / json / csv
    """
    check_format(format)
    check_header(header, infos[0].to_dict().keys())

    if filename:
        f = open(filename, 'w')
    else:
        f = sys.stdout

    show([i.to_dict() for i in infos], header = header, file = f, format=format)

    if filename:
        f.close()
    return

class gerrit_info():
    content = dict()
    def __init__(self, **kwargs):
        self.content.update(kwargs)
        self.content = deepcopy(self.content)
        for key, value in self.content.items():
            try:
                setattr(self, key, value)
            except AttributeError:
                pass

    def to_dict(self):
        return self.content

    def __getitem__(self, item):
        return self.content[item]


def add_commmon_argument(parse, arg, **kparam):
    param = { 'default': None, 'required': False }

    if 'output' == arg:
        param['dest'] = 'output_file'
        param['help'] = 'output to file, not stdout'
        param.update(kparam)
        parse.add_argument('--output', '-o', **param)
    elif 'header' == arg:
        param['dest'] = 'header'
        param['help'] = 'output header, when output format is csv / table'
        param.update(kparam)
        parse.add_argument('--header', **param)
    elif 'format' == arg:
        param['dest']    = 'format'
        param['help']    = 'output format, json / csv / table'
        param['default'] = 'table'
        param.update(kparam)
        parse.add_argument('--format', **param)
    elif 'limit' == arg:
        param['dest'] = 'limit'
        param['help'] = 'limit the search result'
        param['type'] = int
        param.update(kparam)
        parse.add_argument('--limit', **param)
    elif 'skip' in arg:
        param['dest'] = 'skip'
        param['help'] = 'skip the number of result'
        param['type'] = int
        param.update(kparam)
        parse.add_argument('--skip', **param)
