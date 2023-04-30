#!/usr/bin/python
# -*- coding:utf-8 -*-

from datetime import datetime
from prettytable import PrettyTable
import time
import json
import sys
import csv

now = time.time()
utc_offset = datetime.fromtimestamp(now) - datetime.utcfromtimestamp(now)

def utc2local(utc):
    # [0:-3] -> ns to us
    utc_datetime = datetime.strptime(utc[0:-3], "%Y-%m-%d %H:%M:%S.%f")
    local = utc_datetime + utc_offset
    return local.strftime("%Y-%m-%d %H:%M:%S.%f")

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
