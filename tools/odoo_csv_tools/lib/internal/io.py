# -*- coding: utf-8 -*-
'''Created on 10 sept. 2016

@author: mythrys
'''


class ListWriter(object):

    def __init__(self):
        self.fails = []
        self.data = []
        self.header = []
        self.ids = []
        self.messages = []

    def writerow(self, header):
        self.header = list(header)

    def writefails(self, line):
        self.fails.extend(list(line))

    def writerows(self, line):
        self.data.extend(list(line))

    def writeids(self, line):
        self.ids.extend(list(line))

    def writemsg(self, line):
        self.messages.extend(list(line))
