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
import os
from six.moves import xrange

from modbus.mb_utils import *
from ConfigTreeNode import ConfigTreeNode
from PLCControler import LOCATION_CONFNODE, LOCATION_VAR_MEMORY, LOCATION_GROUP


base_folder = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
base_folder = os.path.join(base_folder, "..")
ModbusPath = os.path.join(base_folder, "Modbus")


def savelog(projects):
    try:
        path = 'log.txt'
        with open(path, "w+" ) as log_file:
            # csv.list_dialects()
            # writer = csv.writer(csv_file, delimiter=';')
            #writer.writerow(('Цена', 'Проект;', 'Инфо;'))

            for project in projects:
                log_file.writelines(str(project))
                #writer.writerow((project))
    except Exception:
        print('ошибка записи в файл')
    # else:
    #     print('csv сохранен')


#
#
#
# C L I E N T    R E Q U E S T            #
#
#
#
class _RequestSignal(object):


    XSD = """<?xml version="1.0" encoding="ISO-8859-1" ?>
    <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
     <xsd:element name="MBsignal">
       <xsd:complexType>
          <xsd:attribute name="Signal_name" type="xsd:string" use="optional" default="signal00"/>

          <xsd:attribute name="Bit" use="optional" default="0">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">
                    <xsd:minInclusive value="0"/>
                    <xsd:maxInclusive value="16"/>
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>

        </xsd:complexType>
      </xsd:element>
    </xsd:schema>
    """


    def GetParamsAttributes(self, path=None):
        infos = ConfigTreeNode.GetParamsAttributes(self, path=path)
        # for element in infos:
        #     if element["name"] == "ModbusRequestSignal":
        #         for child in element["children"]:
        #             if child["name"] == "Bit_in_word":
        #                 list = modbus_function_dict.keys()
        #                 list.sort()
        #                 child["type"] = int
        return infos

    def GetVariableLocationTree(self):
        current_location = self.GetCurrentLocation() # tuple objects
        name = self.BaseParams.getName()

        signame = self.GetParamsAttributes()[0]["children"][0]["value"]

        bit = self.GetParamsAttributes()[0]["children"][1]["value"]

        dataname = vraiableTree[0]['name']
        address = vraiableTree[0]['address']
        datatacc = vraiableTree[0]['datatacc']

        entries = []

        #for offset in range(0,  15):
        entries.append({
            "name": dataname + "_" + str(address) +"." + str(bit), #+ "_" + str(address)
            "type": LOCATION_VAR_MEMORY,
            "size": 1,
            "IEC_type": "BOOL",
            "var_name": "MB_" + "".join([w[0] for w in dataname.split()]) + "_" + str(address) + "." + str(bit), # добавляет список в ветку дерева
            #для нас x.x.                                           0 . skip one simbol   [:3:]        8000      .       our bit
            "location": datatacc + ".".join([str(i) for i in current_location]) + "." + str(address) + "." + str(bit), # add a variable in addres list
            "description": "description",
            "children": []})

        return {"name": name,
                "type": LOCATION_CONFNODE,
                "location": "." .join([str(i) for i in current_location]) + ".x",              # "." .join([str(i) for i in current_location])
                "children": entries}



    def CTNGenerate_C(self, buildpath, locations):
        """
        Generate C code
        @param current_location: Tupple containing plugin IEC location : %I0.0.4.5 => (0,0,4,5)
        @param locations: List of complete variables locations \
            [{"IEC_TYPE" : the IEC type (i.e. "INT", "STRING", ...)
            "NAME" : name of the variable (generally "__IW0_1_2" style)
            "DIR" : direction "Q","I" or "M"
            "SIZE" : size "X", "B", "W", "D", "L"
            "LOC" : tuple of interger for IEC location (0,1,2,...)
            }, ...]
        @return: [(C_file_name, CFLAGS),...] , LDFLAGS_TO_APPEND
        """
        return [], "", False



class _RequestSignalWrite(object):


    XSD = """<?xml version="1.0" encoding="ISO-8859-1" ?>
    <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
     <xsd:element name="MBSigWrite">
       <xsd:complexType>
          <xsd:attribute name="Signal_name" type="xsd:string" use="optional" default="signal00"/>

          <xsd:attribute name="Bit" use="optional" default="0">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">
                    <xsd:minInclusive value="0"/>
                    <xsd:maxInclusive value="16"/>
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>
          
          <xsd:attribute name="Offset" use="optional" default="0">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">                    
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>
          
          <xsd:attribute name="Scale" use="optional" default="0">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">                   
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>

        </xsd:complexType>
      </xsd:element>
    </xsd:schema>
    """


    def GetParamsAttributes(self, path=None):
        infos = ConfigTreeNode.GetParamsAttributes(self, path=path)
        # for element in infos:
        #     if element["name"] == "ModbusRequestSignal":
        #         for child in element["children"]:
        #             if child["name"] == "Bit_in_word":
        #                 list = modbus_function_dict.keys()
        #                 list.sort()
        #                 child["type"] = int
        return infos

    def GetVariableLocationTree(self):
        current_location = self.GetCurrentLocation() # tuple objects
        name = self.BaseParams.getName()

        signame = self.GetParamsAttributes()[0]["children"][0]["value"]

        bit = self.GetParamsAttributes()[0]["children"][1]["value"]
        offset = self.GetParamsAttributes()[0]["children"][2]["value"]
        scale = self.GetParamsAttributes()[0]["children"][3]["value"]

        dataname = vraiableTree[0]['name']
        address = vraiableTree[0]['address']
        datatacc = vraiableTree[0]['datatacc']

        entries = []

        if (bit == 16):
            entries.append({
                "name": dataname + "_" + str(address) + "." + str(bit),  # + "_" + str(address)
                "type": LOCATION_VAR_MEMORY,
                "size": 16,
                "IEC_type": "WORD",
                "var_name": "MB_" + "".join([w[0] for w in dataname.split()]) + "_" + str(address) + "." + str(bit),
                # добавляет список в ветку дерева
                # для нас x.x.                                           0 . skip one simbol   [:3:]        8000
                "location": datatacc + ".".join([str(i) for i in current_location]) + "." + str(address) + "." + str(
                    bit),  # add a variable in addres list
                "description": "description",
                "offset": offset,
                "scale": scale,
                "children": []})
        else:
            #for offset in range(0,  15):
            entries.append({
                "name": dataname + "_" + str(address) +"." + str(bit), #+ "_" + str(address)
                "type": LOCATION_VAR_MEMORY,
                "size": 1,
                "IEC_type": "BOOL",
                "var_name": "MB_" + "".join([w[0] for w in dataname.split()]) + "_" + str(address) + "." + str(bit), # добавляет список в ветку дерева
                #для нас x.x.                                           0 . skip one simbol   [:3:]        8000      .       our bit
                "location": datatacc + ".".join([str(i) for i in current_location]) + "." + str(address) + "." + str(bit), # add a variable in addres list
                "description": "description",
                "offset": 0,
                "scale": 0,
                "children": []})

        return {"name": name,
                "type": LOCATION_CONFNODE,
                "location": "." .join([str(i) for i in current_location]) + ".x",              # "." .join([str(i) for i in current_location])
                "children": entries}



    def CTNGenerate_C(self, buildpath, locations):
        """
        Generate C code
        @param current_location: Tupple containing plugin IEC location : %I0.0.4.5 => (0,0,4,5)
        @param locations: List of complete variables locations \
            [{"IEC_TYPE" : the IEC type (i.e. "INT", "STRING", ...)
            "NAME" : name of the variable (generally "__IW0_1_2" style)
            "DIR" : direction "Q","I" or "M"
            "SIZE" : size "X", "B", "W", "D", "L"
            "LOC" : tuple of interger for IEC location (0,1,2,...)
            }, ...]
        @return: [(C_file_name, CFLAGS),...] , LDFLAGS_TO_APPEND
        """
        return [], "", False


class _RequestSignalRead(object):


    XSD = """<?xml version="1.0" encoding="ISO-8859-1" ?>
    <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
     <xsd:element name="MBSigRead">
       <xsd:complexType>
          <xsd:attribute name="Signal_name" type="xsd:string" use="optional" default="signal00"/>

          <xsd:attribute name="Bit" use="optional" default="0">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">
                    <xsd:minInclusive value="0"/>
                    <xsd:maxInclusive value="16"/>
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>
          
            <xsd:attribute name="Offset" use="optional" default="0">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">                    
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>
          
          <xsd:attribute name="Scale" use="optional" default="0">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">                   
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>

        </xsd:complexType>
      </xsd:element>
    </xsd:schema>
    """


    def GetParamsAttributes(self, path=None):
        infos = ConfigTreeNode.GetParamsAttributes(self, path=path)
        # for element in infos:
        #     if element["name"] == "ModbusRequestSignal":
        #         for child in element["children"]:
        #             if child["name"] == "Bit_in_word":
        #                 list = modbus_function_dict.keys()
        #                 list.sort()
        #                 child["type"] = int
        return infos

    def GetVariableLocationTree(self):
        current_location = self.GetCurrentLocation() # tuple objects
        name = self.BaseParams.getName()

        signame = self.GetParamsAttributes()[0]["children"][0]["value"]
        #count = self.GetParamsAttributes()[0]["children"][2]["value"]

        bit = self.GetParamsAttributes()[0]["children"][1]["value"]
        offset = self.GetParamsAttributes()[0]["children"][2]["value"]
        scale = self.GetParamsAttributes()[0]["children"][3]["value"]

        dataname = vraiableTree[0]['name']
        address = vraiableTree[0]['address']
        datatacc = vraiableTree[0]['datatacc']

        entries = []

        if(bit == 16):
            entries.append({
                "name": dataname + "_" + str(address) + "." + str(bit),  # + "_" + str(address)
                "type": LOCATION_VAR_MEMORY,
                "size": 16,
                "IEC_type": "WORD",
                "var_name": "MB_" + "".join([w[0] for w in dataname.split()]) + "_" + str(address) + "." + str(bit),
                # добавляет список в ветку дерева
                # для нас x.x.                                           0 . skip one simbol   [:3:]        8000
                "location": datatacc + ".".join([str(i) for i in current_location]) + "." + str(address) + "." + str(bit), # add a variable in addres list
                "description": "description",
                "offset": offset,
                "scale": scale,
                "children": []})
        else:
            #for offset in range(0,  15):
            entries.append({
                "name": dataname + "_" + str(address) +"." + str(bit), #+ "_" + str(address)
                "type": LOCATION_VAR_MEMORY,
                "size": 1,
                "IEC_type": "BOOL",
                "var_name": "MB_" + "".join([w[0] for w in dataname.split()]) + "_" + str(address) + "." + str(bit), # добавляет список в ветку дерева
                #для нас x.x.                                           0 . skip one simbol   [:3:]        8000      .       our bit
                "location": datatacc + ".".join([str(i) for i in current_location]) + "." + str(address) + "." + str(bit), # add a variable in addres list
                "description": "description",
                "offset": 0,
                "scale": 0,
                "children": []})

        return {"name": name,
                "type": LOCATION_CONFNODE,
                "location": "." .join([str(i) for i in current_location]) + ".x",              # "." .join([str(i) for i in current_location])
                "children": entries}



    def CTNGenerate_C(self, buildpath, locations):
        """
        Generate C code
        @param current_location: Tupple containing plugin IEC location : %I0.0.4.5 => (0,0,4,5)
        @param locations: List of complete variables locations \
            [{"IEC_TYPE" : the IEC type (i.e. "INT", "STRING", ...)
            "NAME" : name of the variable (generally "__IW0_1_2" style)
            "DIR" : direction "Q","I" or "M"
            "SIZE" : size "X", "B", "W", "D", "L"
            "LOC" : tuple of interger for IEC location (0,1,2,...)
            }, ...]
        @return: [(C_file_name, CFLAGS),...] , LDFLAGS_TO_APPEND
        """
        return [], "", False



XSDread = """<?xml version="1.0" encoding="ISO-8859-1" ?>
       <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
         <xsd:element name="Read">
           <xsd:complexType>
             <xsd:attribute name="Function" type="xsd:string" use="optional" default="01 - Read sig"/>

             <xsd:attribute name="SlaveID" use="optional" default="1">
               <xsd:simpleType>
                   <xsd:restriction base="xsd:integer">
                       <xsd:minInclusive value="0"/>
                       <xsd:maxInclusive value="255"/>
                   </xsd:restriction>
               </xsd:simpleType>
             </xsd:attribute>

             <xsd:attribute name="Nr_of_Channels" use="optional" default="1">
               <xsd:simpleType>
                   <xsd:restriction base="xsd:integer">
                       <xsd:minInclusive value="1"/>
                       <xsd:maxInclusive value="2000"/>
                   </xsd:restriction>
               </xsd:simpleType>
             </xsd:attribute>

             <xsd:attribute name="Start_Address" use="optional" default="0">
               <xsd:simpleType>
                   <xsd:restriction base="xsd:integer">
                       <xsd:minInclusive value="0"/>
                       <xsd:maxInclusive value="65535"/>
                   </xsd:restriction>
               </xsd:simpleType>
             </xsd:attribute>

             <xsd:attribute name="Timeout_in_ms" use="optional" default="10">
               <xsd:simpleType>
                   <xsd:restriction base="xsd:integer">
                       <xsd:minInclusive value="1"/>
                       <xsd:maxInclusive value="100000"/>
                   </xsd:restriction>
               </xsd:simpleType>
             </xsd:attribute>
             
             <xsd:attribute name="Offset" use="optional" default="0">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">                    
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>
          
          <xsd:attribute name="Scale" use="optional" default="0">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">                   
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>
          
           </xsd:complexType>
         </xsd:element>
       </xsd:schema>
       """

XSDwrite = """<?xml version="1.0" encoding="ISO-8859-1" ?>
       <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
         <xsd:element name="Write">
           <xsd:complexType>
             <xsd:attribute name="Function" type="xsd:string" use="optional" default="02 - Write Sig"/>

                <xsd:attribute name="SlaveID" use="optional" default="1">
               <xsd:simpleType>
                   <xsd:restriction base="xsd:integer">
                       <xsd:minInclusive value="0"/>
                       <xsd:maxInclusive value="255"/>
                   </xsd:restriction>
               </xsd:simpleType>
             </xsd:attribute>

             <xsd:attribute name="Nr_of_Channels" use="optional" default="1">
               <xsd:simpleType>
                   <xsd:restriction base="xsd:integer">
                       <xsd:minInclusive value="1"/>
                       <xsd:maxInclusive value="2000"/>
                   </xsd:restriction>
               </xsd:simpleType>
             </xsd:attribute>

             <xsd:attribute name="Start_Address" use="optional" default="0">
               <xsd:simpleType>
                   <xsd:restriction base="xsd:integer">
                       <xsd:minInclusive value="0"/>
                       <xsd:maxInclusive value="65535"/>
                   </xsd:restriction>
               </xsd:simpleType>
             </xsd:attribute>

             <xsd:attribute name="Timeout_in_ms" use="optional" default="10">
               <xsd:simpleType>
                   <xsd:restriction base="xsd:integer">
                       <xsd:minInclusive value="1"/>
                       <xsd:maxInclusive value="100000"/>
                   </xsd:restriction>
               </xsd:simpleType>
             </xsd:attribute>               
              
          <xsd:attribute name="Offset" use="optional" default="0">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">                    
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>
          
          <xsd:attribute name="Scale" use="optional" default="0">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">                   
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>

           </xsd:complexType>
         </xsd:element>
       </xsd:schema>
       """

class _ModbusRead(object):
    def __init__(self):
         self.countSignals = 0
         vraiableTree = self.GetVariable()
         global vraiableTree, ReadRegistr

        #vraiableTree = self.GetVariableLocationTree()


    XSD = XSDread

    CTNChildrenTypes = [("MBSigRead", _RequestSignalRead, "Request")]

    def GetParamsAttributes(self, path=None):
        infos = ConfigTreeNode.GetParamsAttributes(self, path=path)
        for element in infos:
            if element["name"] == "Read":
                for child in element["children"]:
                    if child["name"] == "Function":
                        list = modbus_function_dict.keys()
                        list.sort()
                        child["type"] = list

        # for element in infos:
        #     if element["name"] == "ModbusFunctionLoad":
        #         for child in element["children"]:
        #             # TODO запрещаем выбор, хардокдим функцию!
        #             # if child["name"] == "Function":
        #             #     list = modbus_function_dict.keys()
        #             #     list.sort()
        #             #     child["type"] = list
        #             if ReadRegistr != 0:
        #                 if child["name"] == "Start_Address":
        #                     child["value"] = ReadRegistr
        #
        #             if child["name"][0:11:] == "Signal_name":
        #                 if(ReadRegistr in allReg):
        #                     sigInfo = allReg[ReadRegistr]
        #                     index = 0
        #                     self.countSignals = len(sigInfo)
        #                     while index < self.countSignals:
        #                         if child["name"] == "Signal_name"+str(index):
        #                             child["value"] = sigInfo[index][0]
        #                         index +=1

        return infos



    def GetVariable(self):
        current_location = self.GetCurrentLocation()
        name = self.BaseParams.getName()
        address = self.GetParamsAttributes()[0]["children"][3]["value"]
        count = self.GetParamsAttributes()[0]["children"][2]["value"]
        function = self.GetParamsAttributes()[0]["children"][0]["value"]
        # 'BOOL' or 'WORD'
        datatype = modbus_function_dict[function][3]
        # 1 or 16
        datasize = modbus_function_dict[function][4]
        # 'Q' for coils and holding registers, 'I' for input discretes and input registers
        # datazone = modbus_function_dict[function][5]

        # 'X' for bits, 'W' for words
        datatacc = modbus_function_dict[function][6]
        # 'Coil', 'Holding Register', 'Input Discrete' or 'Input Register'
        dataname = modbus_function_dict[function][7]
        entries = []

        for offset in range(address, address + count):
            entries.append({
                "name": dataname,
                "address": address,
                "datatacc": datatacc,
                "type": LOCATION_VAR_MEMORY,
                "size": datasize,
                "IEC_type": datatype,
                "var_name": "MB_" + "".join([w[0] for w in dataname.split()]) + "_" + str(offset),
                "location": datatacc + ".".join([str(i) for i in current_location]) + "." + str(offset),
                "description": "description",
                "children": []})
        return entries

    # def GetNodeCount(self):
    #     return (0, 1, 0 )

    def CTNGenerate_C(self, buildpath, locations):
        """
        Generate C code
        @param current_location: Tupple containing plugin IEC location : %I0.0.4.5 => (0,0,4,5)
        @param locations: List of complete variables locations \
            [{"IEC_TYPE" : the IEC type (i.e. "INT", "STRING", ...)
            "NAME" : name of the variable (generally "__IW0_1_2" style)
            "DIR" : direction "Q","I" or "M"
            "SIZE" : size "X", "B", "W", "D", "L"
            "LOC" : tuple of interger for IEC location (0,1,2,...)
            }, ...]
        @return: [(C_file_name, CFLAGS),...] , LDFLAGS_TO_APPEND
        """
        return [], "", False

    # def GetVariable(self):
    #     GetVariableLocationTree(self)


#class _ModbusWrite(PythonFileCTNMixin):
class _ModbusWrite(object):
    def __init__(self):
        self.countSignals = 0
        vraiableTree = self.GetVariable()
    #     global vraiableTree
    #     vraiableTree = self.GetVariableLocationTree()


    CTNChildrenTypes = [("MBSigWrite", _RequestSignalWrite, "Request")]

    XSD = XSDwrite

    def GetParamsAttributes(self, path=None):
        infos = ConfigTreeNode.GetParamsAttributes(self, path=path)
        for element in infos:
            if element["name"] == "Write":
                for child in element["children"]:
                    if child["name"] == "Function":
                        list = modbus_function_dict.keys()
                        list.sort()
                        child["type"] = list
        # for element in infos:
        #     if element["name"] == "ModbusFunctionLoad":
        #         for child in element["children"]:
        #             # TODO запрещаем выбор, хардокдим функцию!
        #             # if child["name"] == "Function":
        #             #     list = modbus_function_dict.keys()
        #             #     list.sort()
        #             #     child["type"] = list
        #             if child["name"] == "Start_Address":
        #                 child["value"] = WriteRegistr
        #
        #             if child["name"][0:11:] == "Signal_name":
        #                 if (WriteRegistr in allReg):
        #                     sigInfo = allReg[WriteRegistr]
        #                     index = 0
        #                     self.countSignals = len(sigInfo)
        #                     while index < self.countSignals:
        #                         if child["name"] == "Signal_name" + str(index):
        #                             child["value"] = sigInfo[index][0]
        #                         index += 1

                    # if child["name"][0:11:] == "Description":
                    #     if (WriteRegistr in allReg):
                    #         sigInfo = allReg[WriteRegistr]
                    #         index = 0
                    #         self.countSignals = len(sigInfo)
                            # while index < self.countSignals:
                            #     if child["name"] == "Description" + str(index):
                            #         child["value"] = sigInfo[index][1]
                            #     index += 1

        return infos

    def GetVariable(self):
        current_location = self.GetCurrentLocation()
        # name = self.BaseParams.getName()
        #
        # function = self.GetParamsAttributes()[0]["children"][0]["value"]
        # address = self.GetParamsAttributes()[0]["children"][1]["value"]
        # count = self.countSignals
        #
        # # 'BOOL' or 'WORD'
        # datatype = modbus_function_dict[function][3]
        # # 1 or 16
        # datasize = modbus_function_dict[function][4]
        # # 'Q' for coils and holding registers, 'I' for input discretes and input registers
        # # datazone = modbus_function_dict[function][5]
        #
        # # 'X' for bits, 'W' for words
        # datatacc = modbus_function_dict[function][6]
        # # 'Coil', 'Holding Register', 'Input Discrete' or 'Input Register'
        # dataname = modbus_function_dict[function][7]
        #
        # entries = []
        #
        # for offset in range(address, address + count):
        #     entries.append({
        #         "name": dataname,
        #         "address": address,
        #         "datatacc": datatacc,
        #         "type": LOCATION_VAR_MEMORY,
        #         "size": datasize,
        #         "IEC_type": datatype,
        #         "var_name": "MB_" + "".join([w[0] for w in dataname.split()]) + "_" + str(offset),
        #         "location": datatacc + ".".join([str(i) for i in current_location]) + "." + str(offset),
        #         "description": "description",
        #         "children": []})
        #
        # return {"name": name,
        #         "type": LOCATION_CONFNODE,
        #         "location": ".".join([str(i) for i in current_location]) + ".x",
        #         "children": entries}

    # def GetNodeCount(self):
    #     return (0, 1, 0 )

    def CTNGenerate_C(self, buildpath, locations):
        """
        Generate C code
        @param current_location: Tupple containing plugin IEC location : %I0.0.4.5 => (0,0,4,5)
        @param locations: List of complete variables locations \
            [{"IEC_TYPE" : the IEC type (i.e. "INT", "STRING", ...)
            "NAME" : name of the variable (generally "__IW0_1_2" style)
            "DIR" : direction "Q","I" or "M"
            "SIZE" : size "X", "B", "W", "D", "L"
            "LOC" : tuple of interger for IEC location (0,1,2,...)
            }, ...]
        @return: [(C_file_name, CFLAGS),...] , LDFLAGS_TO_APPEND
        """
        return [], "", False

    # def GetVariable(self):
    #     GetVariableLocationTree(self)













class _ModbusFunctionLoad(object):
    def __init__(self):
        # Create BaseParam
        global vraiableTree
        vraiableTree = self.GetVariable()
        # savelog(vraiableTree)

    XSD = """<?xml version="1.0" encoding="ISO-8859-1" ?>
       <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
         <xsd:element name="ModbusFunctionLoad">
           <xsd:complexType>
             <xsd:attribute name="Function" type="xsd:string" use="optional" default="00 - Read Coils"/>

             <xsd:attribute name="SlaveID" use="optional" default="1">
               <xsd:simpleType>
                   <xsd:restriction base="xsd:integer">
                       <xsd:minInclusive value="0"/>
                       <xsd:maxInclusive value="255"/>
                   </xsd:restriction>
               </xsd:simpleType>
             </xsd:attribute>

             <xsd:attribute name="Nr_of_Channels" use="optional" default="1">
               <xsd:simpleType>
                   <xsd:restriction base="xsd:integer">
                       <xsd:minInclusive value="1"/>
                       <xsd:maxInclusive value="2000"/>
                   </xsd:restriction>
               </xsd:simpleType>
             </xsd:attribute>

             <xsd:attribute name="Start_Address" use="optional" default="0">
               <xsd:simpleType>
                   <xsd:restriction base="xsd:integer">
                       <xsd:minInclusive value="0"/>
                       <xsd:maxInclusive value="65535"/>
                   </xsd:restriction>
               </xsd:simpleType>
             </xsd:attribute>

             <xsd:attribute name="Timeout_in_ms" use="optional" default="10">
               <xsd:simpleType>
                   <xsd:restriction base="xsd:integer">
                       <xsd:minInclusive value="1"/>
                       <xsd:maxInclusive value="100000"/>
                   </xsd:restriction>
               </xsd:simpleType>
             </xsd:attribute>

           </xsd:complexType>
         </xsd:element>
       </xsd:schema>
       """
    CTNChildrenTypes = [("ModbusRequestSignal", _RequestSignal, "Request")]

    def GetVariable(self):
        current_location = self.GetCurrentLocation()
        name = self.BaseParams.getName()
        address = self.GetParamsAttributes()[0]["children"][3]["value"]
        count = self.GetParamsAttributes()[0]["children"][2]["value"]
        function = self.GetParamsAttributes()[0]["children"][0]["value"]
        # 'BOOL' or 'WORD'
        datatype = modbus_function_dict[function][3]
        # 1 or 16
        datasize = modbus_function_dict[function][4]
        # 'Q' for coils and holding registers, 'I' for input discretes and input registers
        # datazone = modbus_function_dict[function][5]

        # 'X' for bits, 'W' for words
        datatacc = modbus_function_dict[function][6]
        # 'Coil', 'Holding Register', 'Input Discrete' or 'Input Register'
        dataname = modbus_function_dict[function][7]
        entries = []

        for offset in range(address, address + count):
            entries.append({
                "name": dataname,
                "address": address,
                "datatacc": datatacc,
                "type": LOCATION_VAR_MEMORY,
                "size": datasize,
                "IEC_type": datatype,
                "var_name": "MB_" + "".join([w[0] for w in dataname.split()]) + "_" + str(offset),
                "location": datatacc + ".".join([str(i) for i in current_location]) + "." + str(offset),
                "description": "description",
                "children": []})
        return entries

    # def GetNodeCount(self):
    #     return (0, 1, 0 )

    def CTNGenerate_C(self, buildpath, locations):
        """
        Generate C code
        @param current_location: Tupple containing plugin IEC location : %I0.0.4.5 => (0,0,4,5)
        @param locations: List of complete variables locations \
            [{"IEC_TYPE" : the IEC type (i.e. "INT", "STRING", ...)
            "NAME" : name of the variable (generally "__IW0_1_2" style)
            "DIR" : direction "Q","I" or "M"
            "SIZE" : size "X", "B", "W", "D", "L"
            "LOC" : tuple of interger for IEC location (0,1,2,...)
            }, ...]
        @return: [(C_file_name, CFLAGS),...] , LDFLAGS_TO_APPEND
        """
        return [], "", False

    def GetParamsAttributes(self, path=None):
        infos = ConfigTreeNode.GetParamsAttributes(self, path=path)
        for element in infos:
            if element["name"] == "ModbusFunction":
                for child in element["children"]:
                    if child["name"] == "Function":
                        list = modbus_function_dict.keys()
                        list.sort()
                        child["type"] = list
        return infos



class _RequestPlug(object):
    XSD = """<?xml version="1.0" encoding="ISO-8859-1" ?>
    <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <xsd:element name="ModbusRequest">
        <xsd:complexType>
          <xsd:attribute name="Function" type="xsd:string" use="optional" default="00 - Read Coils"/>

          <xsd:attribute name="SlaveID" use="optional" default="1">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">
                    <xsd:minInclusive value="0"/>
                    <xsd:maxInclusive value="255"/>
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>

          <xsd:attribute name="Nr_of_Channels" use="optional" default="1">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">
                    <xsd:minInclusive value="1"/>
                    <xsd:maxInclusive value="2000"/>
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>

          <xsd:attribute name="Start_Address" use="optional" default="0">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">
                    <xsd:minInclusive value="0"/>
                    <xsd:maxInclusive value="65535"/>
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>

          <xsd:attribute name="Timeout_in_ms" use="optional" default="10">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">
                    <xsd:minInclusive value="1"/>
                    <xsd:maxInclusive value="100000"/>
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>
        </xsd:complexType>
      </xsd:element>
    </xsd:schema>
    """

    def GetParamsAttributes(self, path=None):
        infos = ConfigTreeNode.GetParamsAttributes(self, path=path)
        for element in infos:
            if element["name"] == "ModbusRequest":
                for child in element["children"]:
                    if child["name"] == "Function":
                        list = modbus_function_dict.keys()
                        list.sort()
                        child["type"] = list
        return infos

    def GetVariableLocationTree(self):
        current_location = self.GetCurrentLocation()
        name = self.BaseParams.getName()
        address = self.GetParamsAttributes()[0]["children"][3]["value"] # 3 атрибут в XML схеме
        count = self.GetParamsAttributes()[0]["children"][2]["value"] # 2 атрибут в XML схеме
        function = self.GetParamsAttributes()[0]["children"][0]["value"] # нулевой атрибут в XML схеме
        # 'BOOL' or 'WORD'
        datatype = modbus_function_dict[function][3]
        # 1 or 16
        datasize = modbus_function_dict[function][4]
        # 'Q' for coils and holding registers, 'I' for input discretes and input registers
        # datazone = modbus_function_dict[function][5]
        # 'X' for bits, 'W' for words
        datatacc = modbus_function_dict[function][6]
        # 'Coil', 'Holding Register', 'Input Discrete' or 'Input Register'
        dataname = modbus_function_dict[function][7]
        entries = []

        for offset in range(address, address + count):
            entries.append({
                "name": dataname + " " + str(offset),
                "type": LOCATION_VAR_MEMORY,
                "size": datasize,
                "IEC_type": datatype,
                "var_name": "MB_" + "".join([w[0] for w in dataname.split()]) + "_" + str(offset),
                "location": datatacc + ".".join([str(i) for i in current_location]) + "." + str(offset),
                "description": "description",
                "children": []})

        return {"name": name,
                "type": LOCATION_CONFNODE,
                "location": ".".join([str(i) for i in current_location]) + ".x",
                "children": entries}

    def CTNGenerate_C(self, buildpath, locations):
        """
        Generate C code
        @param current_location: Tupple containing plugin IEC location : %I0.0.4.5 => (0,0,4,5)
        @param locations: List of complete variables locations \
            [{"IEC_TYPE" : the IEC type (i.e. "INT", "STRING", ...)
            "NAME" : name of the variable (generally "__IW0_1_2" style)
            "DIR" : direction "Q","I" or "M"
            "SIZE" : size "X", "B", "W", "D", "L"
            "LOC" : tuple of interger for IEC location (0,1,2,...)
            }, ...]
        @return: [(C_file_name, CFLAGS),...] , LDFLAGS_TO_APPEND
        """
        return [], "", False


#
#
#
# T C P    C L I E N T                 #
#
#
#

class _ModbusTCPclientPlug(object):

    XSD = """<?xml version="1.0" encoding="ISO-8859-1" ?>
    <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <xsd:element name="ModbusTCPclient">
        <xsd:complexType>

          <xsd:attribute name="Remote_IP_Address" type="xsd:string" use="optional" default="localhost"/>
          <xsd:attribute name="Remote_Port_Number" type="xsd:string" use="optional" default="502"/>
          <xsd:attribute name="Invocation_Rate_in_ms" use="optional" default="100">

            <xsd:simpleType>
                <xsd:restriction base="xsd:unsignedLong">
                    <xsd:minInclusive value="1"/>
                    <xsd:maxInclusive value="2147483647"/>
                </xsd:restriction>
            </xsd:simpleType>

          </xsd:attribute>
        </xsd:complexType>
      </xsd:element>
    </xsd:schema>
    """
    # NOTE: Max value of 2147483647 (i32_max) for Invocation_Rate_in_ms
    # corresponds to aprox 25 days.
    CTNChildrenTypes = [("ModbusRequest", _RequestPlug, "Request")]
    # TODO: Replace with CTNType !!!
    PlugType = "ModbusTCPclient"

    # Return the number of (modbus library) nodes this specific TCP client will need
    #   return type: (tcp nodes, rtu nodes, ascii nodes)
    def GetNodeCount(self):
        return (1, 0, 0)

    def CTNGenerate_C(self, buildpath, locations):
        """
        Generate C code
        @param current_location: Tupple containing plugin IEC location : %I0.0.4.5 => (0,0,4,5)
        @param locations: List of complete variables locations \
            [{"IEC_TYPE" : the IEC type (i.e. "INT", "STRING", ...)
            "NAME" : name of the variable (generally "__IW0_1_2" style)
            "DIR" : direction "Q","I" or "M"
            "SIZE" : size "X", "B", "W", "D", "L"
            "LOC" : tuple of interger for IEC location (0,1,2,...)
            }, ...]
        @return: [(C_file_name, CFLAGS),...] , LDFLAGS_TO_APPEND
        """
        return [], "", False





def _lt_to_str(loctuple):
    return '.'.join(map(str, loctuple))




class _ModbusTCPNode(object):
    XSD = """<?xml version="1.0" encoding="ISO-8859-1" ?>
    <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <xsd:element name="ModbusTCPNode">
        <xsd:complexType>
          <xsd:attribute name="Remote_IP_Address" type="xsd:string" use="optional" default="localhost"/>
          <xsd:attribute name="Remote_Port_Number" type="xsd:string" use="optional" default="502"/>
          <xsd:attribute name="Invocation_Rate_in_ms" use="optional" default="100">
            <xsd:simpleType>
                <xsd:restriction base="xsd:unsignedLong">
                    <xsd:minInclusive value="1"/>
                    <xsd:maxInclusive value="2147483647"/>
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>
        </xsd:complexType>
      </xsd:element>
    </xsd:schema>
    """
    # NOTE: Max value of 2147483647 (i32_max) for Invocation_Rate_in_ms
    # corresponds to aprox 25 days.
    CTNChildrenTypes = [
       # ("ModbusFunctionLoad", _ModbusFunctionLoad, "Request"),
        ("Read", _ModbusRead, "Request"),
        ("Write", _ModbusWrite, "Request")]


    # TODO: Replace with CTNType !!!
    PlugType = "ModbusTCPNode"

    # Return the number of (modbus library) nodes this specific TCP client will need
    #   return type: (tcp nodes, rtu nodes, ascii nodes)
    def GetNodeCount(self):
        return (1, 0,  0 , 0)

    def CTNGenerate_C(self, buildpath, locations):
        """
        Generate C code
        @param current_location: Tupple containing plugin IEC location : %I0.0.4.5 => (0,0,4,5)
        @param locations: List of complete variables locations \
            [{"IEC_TYPE" : the IEC type (i.e. "INT", "STRING", ...)
            "NAME" : name of the variable (generally "__IW0_1_2" style)
            "DIR" : direction "Q","I" or "M"
            "SIZE" : size "X", "B", "W", "D", "L"
            "LOC" : tuple of interger for IEC location (0,1,2,...)
            }, ...]
        @return: [(C_file_name, CFLAGS),...] , LDFLAGS_TO_APPEND
        """
        return [], "", False


#
#
#
# R O O T    C L A S S                #
#
#
#
class RootClass(object):
    XSD = """<?xml version="1.0" encoding="ISO-8859-1" ?>
    <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <xsd:element name="ModbusRoot">
        <xsd:complexType>
          <xsd:attribute name="MaxRemoteTCPclients" use="optional" default="10">
            <xsd:simpleType>
                <xsd:restriction base="xsd:integer">
                    <xsd:minInclusive value="0"/>
                    <xsd:maxInclusive value="65535"/>
                </xsd:restriction>
            </xsd:simpleType>
          </xsd:attribute>
        </xsd:complexType>
      </xsd:element>
    </xsd:schema>
    """
    CTNChildrenTypes = [
                        ("ModbusTCPclient", _ModbusTCPclientPlug, "Modbus TCP Client"),
                       # ("ModbusTCPserver", _ModbusTCPserverPlug, "Modbus TCP Server") ,
                        ("ModbusTCPNode",    _ModbusTCPNode, "Modbus Client")


                       # ("ModbusRTUclient", _ModbusRTUclientPlug, "Modbus RTU Client"),
                       # ("ModbusRTUslave", _ModbusRTUslavePlug,  "Modbus RTU Slave")
                        ]

    # Return the number of (modbus library) nodes this specific instance of the modbus plugin will need
    #   return type: (tcp nodes, rtu nodes, ascii nodes)
    def GetNodeCount(self):
        max_remote_tcpclient = self.GetParamsAttributes()[0]["children"][0]["value"]
        total_node_count = (max_remote_tcpclient, 0, 0)
        for child in self.IECSortedChildren():
            # ask each child how many nodes it needs, and add them all up.
            total_node_count = tuple(x1 + x2 for x1, x2 in zip(total_node_count, child.GetNodeCount()))
        return total_node_count

    # Return a list with tuples of the (location, port numbers) used by all
    # the Modbus/IP servers
    def GetIPServerPortNumbers(self):
        IPServer_port_numbers = []
        for child in self.IECSortedChildren():
            if child.CTNType == "ModbusTCPserver":
                IPServer_port_numbers.extend(child.GetIPServerPortNumbers())
        return IPServer_port_numbers

    def CTNGenerate_C(self, buildpath, locations):
        # print "#############"
        # print self.__class__
        # print type(self)
        # print "self.CTNType >>>"
        # print self.CTNType
        # print "type(self.CTNType) >>>"
        # print type(self.CTNType)
        # print "#############"

        loc_dict = {"locstr": "_".join(map(str, self.GetCurrentLocation()))}

        # Determine the number of (modbus library) nodes ALL instances of the modbus plugin will need
        #   total_node_count: (tcp nodes, rtu nodes, ascii nodes)
        # Also get a list with tuples of (location, IP port numbers) used by all the Modbus/IP server nodes
        #   This list is later used to search for duplicates in port numbers!
        #   IPServer_port_numbers = [(location ,IPserver_port_number), ...]
        #       location: tuple similar to (0, 3, 1) representing the location in the configuration tree "0.3.1.x"
        # IPserver_port_number: a number (i.e. port number used by the Modbus/IP server)
        total_node_count = (0, 0, 0)
        IPServer_port_numbers = []
        for CTNInstance in self.GetCTRoot().IterChildren():
            if CTNInstance.CTNType == "modbus":
                # ask each modbus plugin instance how many nodes it needs, and add them all up.

                total_node_count = tuple(x1 + x2 for x1, x2 in zip(total_node_count, CTNInstance.GetNodeCount()))
                IPServer_port_numbers.extend(CTNInstance.GetIPServerPortNumbers())

        # Search for use of duplicate port numbers by Modbus/IP servers print IPServer_port_numbers
        # ..but first define a lambda function to convert a tuple with the config tree location to a nice looking string
        #   for e.g., convert the tuple (0, 3, 4) to "0.3.4"

        for i in range(0, len(IPServer_port_numbers) - 1):
            for j in range(i + 1, len(IPServer_port_numbers)):
                if IPServer_port_numbers[i][1] == IPServer_port_numbers[j][1]:
                    self.GetCTRoot().logger.write_warning( _("Error: Modbus/IP Servers %{a1}.x and %{a2}.x use the same port number {a3}.\n").
                        format(
                            a1=_lt_to_str(IPServer_port_numbers[i][0]),
                            a2=_lt_to_str(IPServer_port_numbers[j][0]),
                            a3=IPServer_port_numbers[j][1]))
                    raise Exception
                    # TODO: return an error code instead of raising an
                    # exception

        # Determine the current location in Beremiz's project configuration
        # tree
        current_location = self.GetCurrentLocation()

        # define a unique name for the generated C and h files
        prefix = "_".join(map(str, current_location))
        Gen_MB_c_path = os.path.join(buildpath, "MB_%s.c" % prefix)
        Gen_MB_h_path = os.path.join(buildpath, "MB_%s.h" % prefix)
        c_filename = os.path.join(os.path.split(__file__)[0], "mb_runtime.c")
        h_filename = os.path.join(os.path.split(__file__)[0], "mb_runtime.h")

        tcpclient_reqs_count = 0

        tcpclient_node_count = 0

        nodeid = 0
        client_nodeid = 0
        client_requestid = 0
        server_id = 0

        server_node_list = []
        client_node_list = []
        client_request_list = []
        server_memarea_list = []
        loc_vars = []
        loc_vars_list = []  # list of variables already declared in C code!

        registers_params = []


        client_signal_list = []

        for child in self.IECSortedChildren():
            # print "<<<<<<<<<<<<<"
            # print "child (self.IECSortedChildren())----->"
            # print child.__class__
            # print ">>>>>>>>>>>>>"
            #

            if child.PlugType == "ModbusTCPclient":
                tcpclient_reqs_count += len(child.IECSortedChildren())
                new_node = GetTCPClientNodePrinted(self, child)
                if new_node is None:
                    return [], "", False
                client_node_list.append(new_node)
                for subchild in child.IECSortedChildren():
                    new_req = GetClientRequestPrinted(
                        self, subchild, client_nodeid)
                    if new_req is None:
                        return [], "", False
                    client_request_list.append(new_req)
                    for iecvar in subchild.GetLocations():
                        # absloute address - start address
                        relative_addr = iecvar["LOC"][3] - int(GetCTVal(subchild, 3))
                        # test if relative address in request specified range
                        if relative_addr in xrange(int(GetCTVal(subchild, 2))):
                            if str(iecvar["NAME"]) not in loc_vars_list:
                                loc_vars.append(
                                    "u16 *" + str(iecvar["NAME"]) + " = &client_requests[%d].plcv_buffer[%d];" % (
                                    client_requestid, relative_addr))
                                loc_vars_list.append(str(iecvar["NAME"]))
                    client_requestid += 1
                tcpclient_node_count += 1
                client_nodeid += 1
            #
            #
            #

            if child.PlugType == "ModbusTCPNode":
                #print "ModbusTCPNode----->"

                tcpclient_reqs_count += len(child.IECSortedChildren())
                new_node = GetTCPClientNodePrinted(self, child)

                if new_node is None:
                    return [], "", False

                client_node_list.append(new_node)
                for subchild in child.IECSortedChildren():

                    new_req = GetClientRequestPrinted(self, subchild, client_nodeid)
                    if new_req is None:
                        return [], "", False

                    new_node_registr = GetClientRequestRegisters(self, subchild, client_requestid)
                    if new_node_registr is None:
                        return [], "", False
                    notSig = ''
                    client_request_list.append(new_req)
                    for iecvar in subchild.GetLocations():

                        # absloute address - start address --(Я) absloute address [4] in dictionary
                        relative_addr = iecvar["LOC"][4] - int(GetCTVal(subchild, 3))
                        # test if relative address in request specified range
                        if relative_addr in range(16):  # xrange(int(GetCTVal(subchild, 2))):
                            iecvarname = iecvar["NAME"]
                            notSig = iecvarname[-2:]
                            bit_num = int(iecvarname[-1])
                       #обработка регистра
                            if(notSig == '16'):
                                if str(iecvar["NAME"]) not in loc_vars_list:
                                    loc_vars.append(
                                        "float *" + str(iecvar["NAME"]) + " = &client_requests[%d].analog_buffer[%d];" % (
                                            client_requestid, relative_addr))
                                    loc_vars_list.append(str(iecvar["NAME"]))
                        # обработка сигналов
                            else:
                                if str(iecvarname) not in loc_vars_list:
                                    loc_vars.append(
                                        "u16 *" + str(iecvar["NAME"]) + " = &request_registers[%d].num_bit[%d];" % (
                                        client_requestid, bit_num))

                                    loc_vars_list.append(str(iecvar["NAME"]))

                    if notSig != '16':
                        registers_params.append(new_node_registr)


                    client_requestid += 1
                tcpclient_node_count += 1
                client_nodeid += 1
                #
                #
            nodeid += 1

            # if child.PlugType == "ModbusTCPLoadNode":
            #     # print "ModbusTCPLoadNode----->"
            #
            #     tcpclient_reqs_count += len(child.IECSortedChildren())
            #     new_node = GetTCPClientNodePrinted(self, child)
            #
            #     new_node_registr = GetClientRequestRegisters(self, child)
            #
            #     if new_node is None:
            #         return [], "", False
            #
            #     if new_node_registr is None:
            #         return [], "", False
            #
            #     client_node_list.append(new_node)
            #     registers_params.append(new_node_registr)
            #     for subchild in child.IECSortedChildren():
            #
            #         new_req = GetClientRequestPrinted(self, subchild, client_nodeid)
            #         if new_req is None:
            #             return [], "", False
            #
            #         client_request_list.append(new_req)
            #         for iecvar in subchild.GetLocations():
            #
            #             # absloute address - start address --(Я) absloute address [4] in dictionary
            #             relative_addr = iecvar["LOC"][4] - int(GetCTVal(subchild, 3))
            #             # test if relative address in request specified range
            #             if relative_addr in xrange(int(GetCTVal(subchild, 2))):
            #                 iecvarname = iecvar["NAME"]
            #                 if str(iecvarname) not in loc_vars_list:
            #                     loc_vars.append(
            #                         "u16 *" + str(iecvarname) + " = &client_requests[%d].plcv_buffer[%d]  ;" % (client_requestid, relative_addr ))  # подставляем наши значение в индексы массива client_requests
            #                     loc_vars_list.append(str(iecvarname))
            #         client_requestid += 1
            #     tcpclient_node_count += 1
            #     client_nodeid += 1
            #     #
            #     #
            # nodeid += 1

        loc_dict["loc_vars"] = "\n".join(loc_vars)
        loc_dict["client_nodes_params"] = ",\n\n".join(client_node_list)
        loc_dict["client_req_params"] = ",\n\n".join(client_request_list)

        loc_dict["registers_params"] = ",\n\n".join(registers_params)
        loc_dict["registers_count"] = str(tcpclient_reqs_count)

        loc_dict["tcpclient_reqs_count"] = str(tcpclient_reqs_count)

        loc_dict["tcpclient_node_count"] = str(tcpclient_node_count)

        loc_dict["total_tcpnode_count"] = str(total_node_count[0])
        loc_dict["max_remote_tcpclient"] = int(self.GetParamsAttributes()[0]["children"][0]["value"])


        # get template file content into a string, format it with dict
        # and write it to proper .h file
        mb_main = open(h_filename).read() % loc_dict
        f = open(Gen_MB_h_path, 'w')
        f.write(mb_main)
        f.close()
        # same thing as above, but now to .c file
        mb_main = open(c_filename).read() % loc_dict
        f = open(Gen_MB_c_path, 'w')
        f.write(mb_main)
        f.close()

        LDFLAGS = []
        LDFLAGS.append(" \"-L" + ModbusPath + "\"")
        #LDFLAGS.append(" \"" + os.path.join(ModbusPath, "MbBeremiz.lib") + "\"")
        LDFLAGS.append(" \"" + os.path.join(ModbusPath, "libmb.a") + "\"")
        LDFLAGS.append(" \"-Wl,-rpath," + ModbusPath + "\"")
        # LDFLAGS.append("\"" + os.path.join(ModbusPath, "mb_slave_and_master.o") + "\"")
        # LDFLAGS.append("\"" + os.path.join(ModbusPath, "mb_slave.o") + "\"")
        # LDFLAGS.append("\"" + os.path.join(ModbusPath, "mb_master.o") + "\"")
        # LDFLAGS.append("\"" + os.path.join(ModbusPath, "mb_tcp.o")    + "\"")
        # LDFLAGS.append("\"" + os.path.join(ModbusPath, "mb_rtu.o")    + "\"")
        # LDFLAGS.append("\"" + os.path.join(ModbusPath, "mb_ascii.o")    + "\"")
        # LDFLAGS.append("\"" + os.path.join(ModbusPath, "sin_util.o")  + "\"")
        # Target is ARM with linux and not win on x86 so winsock2 (ws2_32) library is useless !!!
        # if os.name == 'nt':   # other possible values: 'posix' 'os2' 'ce' 'java' 'riscos'
        # LDFLAGS.append(" -lws2_32 ")  # on windows we need to load winsock
        # library!

        return [(Gen_MB_c_path, ' -I"' + ModbusPath + '"')], LDFLAGS, True

