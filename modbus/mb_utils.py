#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Beremiz, a Integrated Development Environment for
# programming IEC 61131-3 automates supporting plcopen standard and CanFestival.
#
# Copyright (c) 2016 Mario de Sousa (msousa@fe.up.pt)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This code is made available on the understanding that it will not be
# used in safety-critical situations without a full and competent review.

from __future__ import absolute_import
from __future__ import division
from six.moves import xrange
from collections import OrderedDict
import sqlite3

# dictionary implementing:
# key   - string with the description we want in the request plugin GUI
# tuple - (modbus function number, request type, max count value,
# data_type, bit_size)
modbus_function_dict = {
    "00 - Read Coils":                  ('1',   'req_input', 2000, "BOOL", 1, "Q", "X", "Coil"),
    "01 - Read sig":                    ('4',   'req_input', 1, "BOOL", 1, "Q", "X", "Read Signal"),
    "02 - Write Sig":                   ('6',   'req_output', 1, "BOOL", 1, "Q", "X", "Write Signal"),
   #"02 - Read Input Discretes":        ('2',   'req_input', 2000, "BOOL",  1, "I", "X", "Input Discrete"),
    "03 - Read Holding Registers":      ('3',   'req_input',  125, "REAL", 16, "Q", "D", "Holding Register"),
   #"03 - Read Holding Registers":      ('3',   'req_input',  125, "REAL", 16, "Q", "D", "Holding Register"),
   # "04 - Read Input Registers":        ('4',   'req_input',  125, "REAL", 16, "I", "W", "Input Register"),
    "04 - Read Input Registers":        ('4',    'req_input', 125, "REAL", 16, "Q", "D", "Input Register"),
    #"05 - Write Single coil":          ('5',   'req_output',    1, "BOOL",  1, "Q", "X", "Coil"),
    "06 - Write Single Register":       ('6',   'req_output',    1, "REAL", 16, "Q", "D", "Holding Register"),
    #"15 - Write Multiple Coils":       ('15',  'req_output', 1968, "BOOL",  1, "Q", "X", "Coil"),
    "16 - Write Multiple Registers":    ('16',  'req_output',  123, "REAL", 16, "Q", "D", "Holding Register")}


#lacalDir = 'd:\\Valcom\\GITrep\\APS\\APS\\bin\\Debug\\Schema\\'
lacalDir = 'c:\\OSSY-NG\\Schema\\'
dbFile = '718W.db3'
try:

    conn = sqlite3.connect(lacalDir + dbFile)
    c = conn.cursor()
    #c.execute("select   GroupName   from tblGroupSignals")
    #print(c.fetchone())

    lstMBServSignals = []
    # for row in c.execute('select  *   from tblMBServSignals'):
    #    lstMBServSignals.append(row)

    # lstOs = []
    # for row in c.execute('select  *   from tblOs'):
    #    lstOs.append(row)

    lstMBServ = []
    # for row in c.execute('select  *   from tblMBServer'):
    #    lstMBServ.append(row)

    # lstDataType = []
    # for row in c.execute('select  *   from dirMbValueType'):
    #    lstDataType.append(row)

    lstOs = []
    cursor = c.execute('select rowid, *   from tblOs')
    columnList = list(map(lambda x: x[0], cursor.description))
    dicData = OrderedDict((k,'') for k in list(map(lambda x: x[0], cursor.description)))
    for row in cursor:
        lstOs.append(dict(zip(columnList, row)))

    cursor = c.execute('select  rowid,*   from tblMBServSignals')
    columnList = list(map(lambda x: x[0], cursor.description))
    dicData = dict((k, '') for k in list(map(lambda x: x[0], cursor.description)))
    for row in cursor:
        lstMBServSignals.append(dict(zip(columnList, row)))

    cursor = c.execute('select  rowid,*   from tblMBServer')
    columnList = list(map(lambda x: x[0], cursor.description))
    dicData = dict((k, '') for k in list(map(lambda x: x[0], cursor.description)))
    for row in cursor:
        lstMBServ.append(dict(zip(columnList, row)))

    ipLstBv = []
    for x in lstOs:
        if (x['Location'] == u'Вычислитель'):
            ipLstBv.append(x["IP1"])

except Exception :
    pass



signallist = []
vraiableTree = []
# Configuration tree value acces helper
def GetCTVal(child, index):
    return child.GetParamsAttributes()[0]["children"][index]["value"]


# Configuration tree value acces helper, for multiple values
def GetCTVals(child, indexes):
    return map(lambda index: GetCTVal(child, index), indexes)


def GetTCPClientNodePrinted(self, child):
    """
    Outputs a string to be used on C files
    params: child - the correspondent subplugin in Beremiz
    """
    node_init_template = '''/*node %(locnodestr)s*/
{"%(locnodestr)s", {naf_tcp, {.tcp = {"%(host)s", "%(port)s", DEF_CLOSE_ON_SILENCE}}}, -1 /* mb_nd */, 0 /* init_state */, %(coms_period)s /* communication period */, 0 /* prev_error */}'''

    location = ".".join(map(str, child.GetCurrentLocation()))
    host, port, coms_period = GetCTVals(child, range(3))

    node_dict = {"locnodestr": location,
                 "host": host,
                 "port": port,
                 "coms_period": coms_period}
    return node_init_template % node_dict


def GetClientRequestPrinted(self, child, nodeid):
    """
    Outputs a string to be used on C files
    params: child - the correspondent subplugin in Beremiz
            nodeid - on C code, each request has it's own parent node (sequential, 0..NUMBER_OF_NODES)
                     It's this parameter.
    return: None - if any definition error found
            The string that should be added on C code - if everything goes allright
    """

    req_init_template = '''/*request %(locreqstr)s*/
{"%(locreqstr)s", %(nodeid)s, %(slaveid)s, %(iotype)s, %(func_nr)s, %(address)s , %(count)s,
DEF_REQ_SEND_RETRIES, 0 /* error_code */, 0 /* prev_code */, {%(timeout_s)d, %(timeout_ns)d} /* timeout */,
{%(buffer)s}, {%(buffer)s} , {%(abuffer)s} }'''

    timeout = int(GetCTVal(child, 4))
    timeout_s = timeout // 1000
    timeout_ms = timeout - (timeout_s * 1000)
    timeout_ns = timeout_ms * 1000000

    request_dict = {
        "locreqstr": "_".join(map(str, child.GetCurrentLocation())),
        "nodeid": str(nodeid),
        "slaveid": GetCTVal(child, 1),
        "address": GetCTVal(child, 3),
        "count": GetCTVal(child, 2),
        "timeout": timeout,
        "timeout_s": timeout_s,
        "timeout_ns": timeout_ns,
        "buffer": ",".join(['0'] * int(GetCTVal(child, 2))),
        "abuffer": ",".join(['0'] * int(GetCTVal(child, 2))),
        "func_nr": modbus_function_dict[GetCTVal(child, 0)][0],
        "iotype": modbus_function_dict[GetCTVal(child, 0)][1],
        "maxcount": modbus_function_dict[GetCTVal(child, 0)][2]
        # ,
        # "offset": GetCTVal(child, 5),
        # "scale": GetCTVal(child, 6)
    }

    if int(request_dict["slaveid"]) not in xrange(256):
        self.GetCTRoot().logger.write_error(
            "Modbus plugin: Invalid slaveID in TCP client request node %(locreqstr)s (Must be in the range [0..255])\nModbus plugin: Aborting C code generation for this node\n" % request_dict)
        return None
    if int(request_dict["address"]) not in xrange(65536):
        self.GetCTRoot().logger.write_error(
            "Modbus plugin: Invalid Start Address in TCP client request node %(locreqstr)s (Must be in the range [0..65535])\nModbus plugin: Aborting C code generation for this node\n" % request_dict)
        return None
    if int(request_dict["count"]) not in xrange(1, 1 + int(request_dict["maxcount"])):
        self.GetCTRoot().logger.write_error(
            "Modbus plugin: Invalid number of channels in TCP client request node %(locreqstr)s (Must be in the range [1..%(maxcount)s])\nModbus plugin: Aborting C code generation for this node\n" % request_dict)
        return None
    if (int(request_dict["address"]) + int(request_dict["count"])) not in xrange(1, 65537):
        self.GetCTRoot().logger.write_error(
            "Modbus plugin: Invalid number of channels in TCP client request node %(locreqstr)s (start_address + nr_channels must be less than 65536)\nModbus plugin: Aborting C code generation for this node\n" % request_dict)
        return None

    return req_init_template % request_dict



def GetClientRequestRegisters(self, child, nodeid):

    req_init_template = '''{ %(address)s ,  {%(num_bit)s}}'''

    request_dict = {
        "address": GetCTVal(child, 3),
        "num_bit": 0 # GetCTVal(child, 2),# nodeid,
        }

    return req_init_template % request_dict