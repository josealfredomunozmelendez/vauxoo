# !/usr/bin/env python
# -*- coding: utf-8 -*-
'''Copyright (C) Thibault Francois

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Lesser Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''


import logging
import sys

from time import time
from itertools import islice, chain
from xmlrpc.client import Fault

from .lib.internal.rpc_thread import RpcThread
from .lib.internal.io import ListWriter

_logger = logging.getLogger('vxmigration')


def batch(iterable, size):
    sourceiter = iter(iterable)
    while True:
        batchiter = islice(sourceiter, size)
        yield chain([batchiter.__next__()], batchiter)


class RPCThreadImport(RpcThread):

    def __init__(self, max_connection, registry, model, header, writer,
                 batch_size=20, context=None):
        super(RPCThreadImport, self).__init__(max_connection)
        self.registry = registry
        self.model = model
        self.header = header
        self.batch_size = batch_size
        self.writer = writer
        self.context = context

    def launch_batch(self, data_lines, batch_number, check=False):
        def launch_batch_fun(lines, batch_number, check=False):
            i = 0
            for lines_batch in batch(lines, self.batch_size):
                lines_batch = [l for l in lines_batch]
                self.sub_batch_run(
                    lines_batch, batch_number, i, len(lines), check=check)
                i += 1
        self.spawn_thread(
            launch_batch_fun, [data_lines, batch_number], {'check': check})

    def sub_batch_run(self, lines, batch_number, sub_batch_number,
                      total_line_nb, check=False):
        success = False
        res = {'fails': [], 'messages': [], 'ids': []}
        st = time()
        fails = []
        try:
            res = self._send_rpc(
                lines, batch_number, sub_batch_number, check=check)
            success = True
        except Fault as e:
            message = "Line %s %s failed" % (batch_number, sub_batch_number)
            _logger.error(message)
            _logger.error(e.faultString)
            res['messages'] = [e.faultString]
        except ValueError as e:
            message = "Line %s %s failed value error" % (
                batch_number, sub_batch_number)
            _logger.error(message)
            res['messages'] = [e]
        except BaseException as e:
            message = "Import Problem %s" % (e)
            _logger.error(message)
            exc_type, exc_value, _ = sys.exc_info()
            _logger.error(exc_type)
            _logger.error(exc_value)
            res['messages'] = [e]
        if not success:
            fails = lines
        self.writer.writefails(fails)
        self.writer.writeids(res.get('ids') or [])
        self.writer.writemsg(res.get('messages') or [])
        message = "import time for batch %s - %s of %s : %s" % (
            batch_number, (sub_batch_number + 1) * self.batch_size,
            total_line_nb, time() - st)
        _logger.debug(message)

    def _send_rpc(self, lines, batch_number, sub_batch_number, check=False):
        res = self.registry.execute(self.model, 'load', self.header, lines)
        if res['messages']:
            for msg in res['messages']:
                _logger.error('batch %s, %s', batch_number, sub_batch_number)
                _logger.error(msg)
                _logger.error(lines[msg['record']])
            return res
        if len(res['ids']) != len(lines) and check:
            _logger.error(
                "number of record import is different from the "
                "record to import, probably duplicate xml_id")
            return res

        return res


def do_not_split(split, previous_split_value, split_index, line):
    if not split:  # If no split no need to continue
        return False

    split_value = line[split_index]
    # Different Value no need to not split
    if split_value != previous_split_value:
        return False

    return True


def filter_line_ignore(ignore, header, line):
    new_line = []
    for k, val in zip(header, line):
        if k not in ignore:
            new_line.append(val)
    return new_line


def filter_header_ignore(ignore, header):
    new_header = []
    for val in header:
        if val not in ignore:
            new_header.append(val)
    return new_header


def split_sort(split, header, data):
    split_index = 0
    if split:
        try:
            split_index = header.index(split)
        except ValueError as ve:
            _logger.error("column %s not defined\n %s" % (split, ve))
            raise ValueError
        data = sorted(data, key=lambda d: d[split_index])
    return data, split_index


def import_data(registry, model, header=None, data=None,
                ignore=False, split=False, check=True,
                max_connection=1, batch_size=10, skip=0):
    ignore = ignore or []
    if not header or data is None:
        raise ValueError(
            "Please provide either a data file or a header and data")

    writer = ListWriter()
    writer.writerow(filter_header_ignore(ignore, header))
    rpc_thread = RPCThreadImport(
        int(max_connection), registry, model,
        filter_header_ignore(ignore, header), writer, batch_size)
    st = time()
    data, split_index = split_sort(split, header, data)
    i = 0
    previous_split_value = False
    while i < len(data):
        lines = []
        j = 0
        while i < len(data) and (
            j < batch_size or do_not_split(
                split, previous_split_value, split_index, data[i])):
            line = data[i][:len(header)]
            lines.append(filter_line_ignore(ignore, header, line))
            previous_split_value = line[split_index]
            j += 1
            i += 1
        batch_number = (
            split and "[%s] - [%s]" % (
                rpc_thread.thread_number(), previous_split_value) or
            "[%s]" % rpc_thread.thread_number())
        rpc_thread.launch_batch(lines, batch_number, check)

    rpc_thread.wait()
    _logger.debug("%s %s imported, total time %s second(s)" % (
        len(data), model, (time() - st)))
    _logger.debug("Import Finished")
    return writer.messages, writer.fails, writer.ids
