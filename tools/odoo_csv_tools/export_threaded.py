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

from xmlrpc.client import Fault
from time import time
from itertools import islice, chain


import logging
import sys

from .lib.internal.rpc_thread import RpcThread
from .lib.internal.io import ListWriter

_logger = logging.getLogger('vxmigration')


def batch(iterable, size):
    sourceiter = iter(iterable)
    while True:
        batchiter = islice(sourceiter, size)
        yield chain([batchiter.__next__()], batchiter)


class RPCThreadExport(RpcThread):

    def __init__(self, max_connection, registry, model, header, writer,
                 batch_size=20, context=None):
        super(RPCThreadExport, self).__init__(max_connection)
        self.registry = registry
        self.model = model
        self.header = header
        self.batch_size = batch_size
        self.writer = writer
        self.context = context
        self.result = {}

    def launch_batch(self, data_ids, batch_number):
        def launch_batch_fun(data_ids, batch_number, check=False):
            st = time()
            try:
                self.result[batch_number] = self.registry.execute(
                    self.model, 'export_data', data_ids, self.header)['datas']
            except Fault as e:
                _logger.error("export %s failed" % batch_number)
                _logger.error(e.faultString)
            except Exception as e:
                _logger.info("Unknown Problem")
                exc_type, exc_value, _ = sys.exc_info()
                _logger.error(exc_type)
                _logger.error(exc_value)
            _logger.debug("export time for batch %s: %s" % (
                batch_number, time() - st))

        self.spawn_thread(launch_batch_fun, [data_ids, batch_number], {})

    def write_file(self, file_writer):
        file_writer.writerow(self.header)
        for key in self.result:
            file_writer.writerows(self.result[key])


def export_data(registry, model, ids, header,
                max_connection=1, batch_size=100):
    writer = ListWriter()
    rpc_thread = RPCThreadExport(
        int(max_connection), registry, model, header, writer, batch_size)
    st = time()
    i = 0
    for b in batch(ids, batch_size):
        batch_ids = [l for l in b]
        rpc_thread.launch_batch(batch_ids, i)
        i += 1

    rpc_thread.wait()
    _logger.debug("%s %s exported, total time %s second(s)" % (
        len(ids), model, (time() - st)))
    _logger.debug("Export Finished")
    rpc_thread.write_file(writer)
    return writer.data
