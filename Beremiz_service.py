#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Beremiz, a Integrated Development Environment for
# programming IEC 61131-3 automates supporting plcopen standard and CanFestival.
#
# Copyright (C) 2007: Edouard TISSERANT and Laurent BESSARD
# Copyright (C) 2017: Andrey Skvortsov
#
# See COPYING file for copyrights details.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import getopt
import threading
from threading import Thread, currentThread, Semaphore
import traceback
import __builtin__
import Pyro.core as pyro
import wx
# import wx.adv
from lxml import etree, objectify
import time

from runtime import PLCObject, ServicePublisher
import util.paths as paths

import logging
import wx.lib.agw.genericmessagedialog as GMD

scadaPath = 'c:\\OSSY-NG\\'
scadaVplc = scadaPath + 'Vplc\\'
scadaConfig = scadaPath + 'Runtime\\ASU.config.xml'
scada_vplc_config = scadaVplc + 'project.txt'

logs = logging.getLogger("Service")
logs.setLevel(logging.INFO)

# создаём logging файловый хендлер/форматер
log_fh = logging.FileHandler(scadaVplc + "PLCservice.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
log_fh.setFormatter(formatter)
logs.addHandler(log_fh)


# class ExceptionLogging(object):
#
#     def __init__(self, fn):
#         self.fn = fn
#
#         # создаём logging инстанцию
#         self.logs = logging.getLogger("wxErrors")
#         self.logs.setLevel(logging.INFO)
#
#         # создаём logging файловый хендлер/форматер
#         log_fh = logging.FileHandler("error.log")
#         formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
#         log_fh.setFormatter(formatter)
#         self.logs.addHandler(log_fh)
#
#     def __call__(self, evt):
#         try:
#             self.fn(self, evt)
#         except Exception, e:
#         #except Exception as e:
#             self.logs.exception("Exception")
#

def usage():
    print("""
Usage of Beremiz PLC execution service :\n
%s {[-n servicename] [-i IP] [-p port] [-x enabletaskbar] [-a autostart]|-h|--help} working_dir
           -n        - zeroconf service name (default:disabled)
           -i        - IP address of interface to bind to (default:localhost)
           -p        - port number default:3000
           -h        - print this help text and quit
           -a        - autostart PLC (0:disable 1:enable) (default:0)
           -x        - enable/disable wxTaskbarIcon (0:disable 1:enable) (default:1)
           -t        - enable/disable Twisted web interface (0:disable 1:enable) (default:1)
           -w        - web server port or "off" (default:8009)
           -c        - WAMP client config file or "off" (default:wampconf.json)
           -e        - python extension (absolute path .py)

           working_dir - directory where are stored PLC files
""" % sys.argv[0])


try:
    opts, argv = getopt.getopt(sys.argv[1:], "i:p:n:x:t:a:w:c:e:h")
except getopt.GetoptError, err:
    # print help information and exit:
    print(str(err))  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

# default values

given_ip = None
port = 3000
webport = 8009
wampconf = "wampconf.json"
servicename = None
autostart = False
enablewx = True
havewx = False
enabletwisted = True
havetwisted = False
WorkingDir = ""
extensions = []

for o, a in opts:
    if o == "-h":
        usage()
        sys.exit()
    elif o == "-i":
        if len(a.split(".")) == 4 or a == "localhost":
            given_ip = a
        else:
            usage()
            sys.exit()
    elif o == "-p":
        # port: port that the service runs on
        port = int(a)
    elif o == "-n":
        servicename = a
    elif o == "-x":
        enablewx = int(a)
    elif o == "-t":
        enabletwisted = int(a)
    # elif o == "-a":
    #     autostart = int(a)
    elif o == "-w":
        webport = None if a == "off" else int(a)
    elif o == "-c":
        wampconf = None if a == "off" else a
    elif o == "-e":
        extensions.append(a)
    else:
        usage()
        sys.exit()

beremiz_dir = paths.AbsDir(__file__)

if len(argv) > 1:
    usage()
    sys.exit()
elif len(argv) == 1:
    WorkingDir = argv[0]
    os.chdir(WorkingDir)
elif len(argv) == 0:
    WorkingDir = scadaVplc
    # WorkingDir = os.getcwd()
    argv = [WorkingDir]


def config_debug_mode():
    debug_p = ''
    with open(scadaConfig) as f:
        xml = f.read()

    tst = objectify.fromstring(xml).appSettings

    for appt in tst.getchildren():
        configItems = appt.attrib.items()
        for sss in appt.attrib.items():
            zxv = sss[1].lower()
            if zxv == 'debug':
                debug_p = configItems[1][1].lower()
                # print('Debug: ' + debug_p)
    return debug_p


if config_debug_mode() == 'true':
    autostart = False
else:
    autostart = True


class MyCustomTextCtrl(wx.TextCtrl):

    def __init__(self, *args, **kwargs):
        wx.TextCtrl.__init__(self, *args, **kwargs)

    def write(self, text):
        self.WriteText(text)

    def flush(self):
        self.WriteText('')


def Extract_info(msg):
    # self.log.AppendText("PLC stop.")
    print(_(msg))
    logs.info(msg)


import wx.lib.buttons as buts


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        self.dict = dict()
        # no_caption = wx.RESIZE_BORDER
        # wx.Frame.__init__(self, parent, title=title, style=no_caption)
        wx.Frame.__init__(self, parent, title=title, pos=(150, 150), size=(500, 450))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        # self.Bind(wx.EVT_CLOSE, taskbar_instance.OnTaskBarQuit )

        # self.control = wx.TextCtrl(self, pos=(300,20), size=(200,300), style=wx.TE_MULTILINE | wx.TE_READONLY) # wx.TextCtrl(self, style=wx.TE_MULTILINE)
        #   self.Show(True)

        # toolbar = self.CreateToolBar(style=wx.HORIZONTAL) # wx.TB_DOCKABLE
        # quittool1 = toolbar.AddLabelTool(wx.ID_ANY, 'Quit', wx.Bitmap(Bpath("images", "brz.png")))
        # self.Bind(wx.EVT_TOOL, self.OnClose, quittool1)
        # self.Show()

        menubar = wx.MenuBar()
        first = wx.Menu()
        second = wx.Menu()

        m_open = first.Append(1, "Hide")
        self.Bind(wx.EVT_MENU, self.OnHide, m_open)

        m_exit = first.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menubar.Append(first, "File")

        m_s_workdir = second.Append(wx.NewId(), "Change working directory")
        self.Bind(wx.EVT_MENU, self.OnTaskBarChangeWorkingDir, m_s_workdir)
        m_settings = second.Append(wx.NewId(), "Change Port Number")  #
        self.Bind(wx.EVT_MENU, self.OnTaskBarChangePort, m_settings)
        menubar.Append(second, "Settings")

        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menubar.Append(menu, "&Help")

        self.SetMenuBar(menubar)

        # self.m_statusBar1 = self.CreateStatusBar(1, wx.ID_ANY)
        bSizer1 = wx.BoxSizer(wx.VERTICAL)
        bSizer3 = wx.BoxSizer(wx.VERTICAL)
        bSizerLabels = wx.BoxSizer(wx.HORIZONTAL)
        bSizer4 = wx.BoxSizer(wx.HORIZONTAL)  # bSizerButtons

        self.config_load_result = self.get_config()
        if self.config_load_result == -1:
            self.projectName = 'not loaded'
            self.address = '-'
            self.port = '-'
        else:
            self.projectName = self.dict['project']
            self.address = self.dict['address']
            self.port = self.dict['port']

        # self.projectName = self.GetProjectFileName()
        self.m_staticText1 = wx.StaticText(self, wx.ID_ANY, u"Project: " + self.projectName, wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)
        bSizerLabels.Add(self.m_staticText1, 0, wx.ALL, 5)

        self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"Address: " + self.address, wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)
        bSizerLabels.Add(self.m_staticText2, 0, wx.ALL, 5)

        self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"Port: " + self.port, wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)
        bSizerLabels.Add(self.m_staticText2, 0, wx.ALL, 5)

        bSizer3.Add(bSizerLabels, 1, wx.EXPAND, 5)

        bSizerLabels2 = wx.BoxSizer(wx.HORIZONTAL)

        self.mode = config_debug_mode()
        # self.mode = 'false'

        self.m_staticText1 = wx.StaticText(self, wx.ID_ANY, u"Debug mode: " + self.mode, wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)
        bSizerLabels2.Add(self.m_staticText1, 0, wx.ALL, 5)
        # self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"true", wx.DefaultPosition, wx.DefaultSize, 0)
        # self.m_staticText2.Wrap(-1)

        # bSizerLabels2.Add(self.m_staticText2, 0, wx.ALL, 5)
        bSizer3.Add(bSizerLabels2, 1, wx.EXPAND, 5)

        self.defaulticon = wx.Image(Bpath("images", "brz.png")).ConvertToBitmap()  # .Scale(15, 15)
        self.starticon = wx.Image(Bpath("images", "icoplay24.png")).ConvertToBitmap()
        self.stopicon = wx.Image(Bpath("images", "icostop24.png")).ConvertToBitmap()

        self.ButtonStartStopCaptipn = u"Start"
        # self.m_button1 = buts.GenBitmapTextButton(self, -1, bitmap=self.defaulticon, label=self.ButtonStartStopCaptipn)
        self.m_button1 = wx.Button(self, wx.ID_ANY, self.ButtonStartStopCaptipn, wx.DefaultPosition, wx.DefaultSize, 0)

        self.m_button1.Bind(wx.EVT_BUTTON, self.OnButtonStartPLC)
        # self.m_button1.SetBitmap(defaulticon, wx.RIGHT)

        bSizer4.Add(self.m_button1, 0, wx.ALL, 5)
        #
        # self.m_button2 = wx.Button(self, wx.ID_ANY, u"Status", wx.DefaultPosition, wx.DefaultSize, 0)
        # self.m_button2.Bind(wx.EVT_BUTTON, self.onGetStatusPlc)
        # bSizerButtons.Add(self.m_button2, 0, wx.ALL, 5)
        self.m_bitmap1 = wx.StaticBitmap(self, wx.ID_ANY, self.defaulticon, wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer4.Add(self.m_bitmap1, 0, wx.ALL, 5)

        bSizer3.Add(bSizer4, 1, wx.EXPAND, 5)

        bSizer1.Add(bSizer3, 1, wx.EXPAND, 5)
        sbSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Log"), wx.VERTICAL)

        self.log = MyCustomTextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        sbSizer1.Add(self.log, 1, wx.EXPAND, 0)

        bSizer1.Add(sbSizer1, 2, wx.EXPAND, 0)
        self.SetSizer(bSizer1)
        self.Layout()
        self.Centre(wx.BOTH)

        # перенапраляем вывод лога
        sys.stdout = self.log
        sys.stderr = self.log

        if self.mode == 'false':
            self.m_button1.Disable()
            # self.OnButtonStartPLC(self) # !!! обьект еще не создан, поэтому не запустится
            menubar.Hide()
            Extract_info("Start programm in production mode")
        else:
            Extract_info("Start programm in debug mode")

        # Extract_info)

    def GetProjectFileName(self):
        file_name = 'no project files'
        for file in os.listdir(scadaVplc):
            if file.endswith(".dll"):
                # print(os.path.join(scadaVplc, file))
                file_name = file
                break

        return file_name

    def get_config(self):
        if not os.path.exists(scada_vplc_config):
            return -1

        with open(scada_vplc_config) as file:
            for item in file:
                key = item.split(":")[0]
                value = item.split(":")[1]
                self.dict[key] = value

            file.close()
        return 0

    def OnButtonStartPLC(self, evt):
        try:
            self.chage_server_state()

            #self.ChangeButtonIcon()

        except Exception, e:
            print(_("Exception - failed pyroserver.plcobj:"), e)

    def chage_server_state(self):
        if pyroserver.plcobj is not None:
            plcstatus = pyroserver.plcobj.GetPLCstatus()[0]
            if plcstatus is "Stopped":
                #Extract_info("PLC Start.")
                pyroserver.plcobj.StartPLC()
            else:
                #Extract_info("PLC is already started.") 
                if pyroserver.plcobj.GetPLCstatus()[0] == "Started":
                    #Extract_info("PLC stopping.")
                    Thread(target=pyroserver.plcobj.StopPLC).start()
                else:
                    Extract_info("PLC is empty.")

    def ChangeButtonIcon(self):
        if pyroserver.plcobj is not None and self is not None:
            plcstatus = pyroserver.plcobj.GetPLCstatus()[0]
            if plcstatus is "Stopped":
                #a=1
                Extract_info("PLC stopped.")
                self.m_button1.SetLabel("Start")
                self.m_bitmap1.SetBitmap(self.stopicon)
            else:
                if pyroserver.plcobj.GetPLCstatus()[0] == "Started":
                    #b=2
                    Extract_info("PLC started.")

                    self.m_button1.SetLabel("Stop")
                    self.m_bitmap1.SetBitmap(self.starticon)



    def onGetStatusPlc(self, event):
        status = ''
        if pyroserver.plcobj is not None:
            if pyroserver.plcobj.GetPLCstatus()[0] == "Started":
                status = 'Stop'
                # ttt = pyroserver.plcobj._GetLogMessage()[0]
                vvv = pyroserver.plcobj._GetLogCount()[0]

            else:
                status = 'Start'

    # return status

    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "Valcom Plc Service", "Valcom Plc Service", wx.OK)
        dlg.ShowModal()  # Show it
        dlg.Destroy()  # finally destroy it when finished.

    def OnTaskBarChangeWorkingDir(self, evt):
        dlg = wx.DirDialog(None)
        if dlg.ShowModal() == wx.ID_OK:
            pyroserver.Stop()
            # self.workdir = dlg.GetPath()
            # global WorkingDir
            pyroserver.workdir = dlg.GetPath()
            # pyroserver.evaluator
            # self.Extract_info("Изменена папка на ")
            # pyroserver.Stop()

            print("Изменена папка на")
            # self.pyroserver.plcobj.StartPLC()

    def OnTaskBarChangePort(self, evt):
        dlg = ParamsEntryDialog(None, _("Enter a port number "), defaultValue=str(pyroserver.port))
        dlg.SetTests([(UnicodeType.isdigit, _("Port number must be an integer!")),
                      (lambda port: 0 <= int(port) <= 65535, _("Port number must be 0 <= port <= 65535!"))])
        if dlg.ShowModal() == wx.ID_OK:
            pyroserver.port = int(dlg.GetValue())
            pyroserver.Stop()
            Extract_info("service change port to " + str(pyroserver.port))

    # @ExceptionLogging
    def OnClose(self, event):
        if self.mode == 'false':
            self.Hide()
        else:

            dlg = wx.MessageDialog(self,
                                   "Do you really want to close this application?",
                                   "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            # wx.CallAfter(taskbar_instance.TaskBarQuit())

            if result == wx.ID_OK:
                exitTskBar()

                # app.Destroy() # тут вызывает краш приложение, на 10-ке не видно, на семерке аварийно завершает

    def Exit(self):
        self.Destroy()
        Extract_info("PLC servise stop end exit.")
        os._exit(os.F_OK)

    def OnHide(self, event):
        self.Hide()


# class MyEvent(wx.PyCommandEvent):
#     def __init__(self, evtType, id):
#         wx.PyCommandEvent.__init__(self, evtType, id)
#         myVal = None
#
#     def SetMyVal(self, val):
#         self.myVal = val
#
#     def GetMyVal(self):
#         return self.myVal

class ToolbarFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Toolbars', size=(300, 200))
        panel = wx.Panel(self)
        panel.SetBackgroundColour('White')
        # (1) Creating the status bar
        statusBar = self.CreateStatusBar()
        # (2) Creating the toolbar
        toolbar = self.CreateToolBar()

        # (3) Adding a tool to the bar
        # toolbar.AddSimpleTool(wx.NewId(),  "New", "Long help for 'New'")

        # (4) Preparing the toolbar for display
        toolbar.Realize()
        # Creating a menubar
        menuBar = wx.MenuBar()
        # (5) Creating two individual menus
        menu1 = wx.Menu()
        menuBar.Append(menu1, "&File")
        menu2 = wx.Menu()
        # (6) Creating individual menu items
        menu2.Append(wx.NewId(), "&Copy", "Copy in status bar")
        menu2.Append(wx.NewId(), "C&ut", "")
        menu2.Append(wx.NewId(), "Paste", "")
        menu2.AppendSeparator()
        menu2.Append(wx.NewId(), "&Options...", "Display Options")
        # Attaching the menu to the menubar
        menuBar.Append(menu2, "&Edit")
        # Attaching the menubar to the frame
        self.SetMenuBar(menuBar)


def Bpath(*args):
    return os.path.join(beremiz_dir, *args)


def SetupI18n():
    # Get folder containing translation files
    localedir = os.path.join(beremiz_dir, "locale")
    # Get the default language
    langid = wx.LANGUAGE_DEFAULT
    # Define translation domain (name of translation files)
    domain = "Beremiz"

    # Define locale for wx
    loc = __builtin__.__dict__.get('loc', None)
    if loc is None:
        loc = wx.Locale(langid)
        __builtin__.__dict__['loc'] = loc
        # Define location for searching translation files
    loc.AddCatalogLookupPathPrefix(localedir)
    # Define locale domain
    loc.AddCatalog(domain)

    import locale
    global default_locale
    default_locale = locale.getdefaultlocale()[1]

    # sys.stdout.encoding = default_locale
    # if Beremiz_service is started from Beremiz IDE
    # sys.stdout.encoding is None (that means 'ascii' encoding').
    # And unicode string returned by wx.GetTranslation() are
    # automatically converted to 'ascii' string.
    def unicode_translation(message):
        return wx.GetTranslation(message).encode(default_locale)

    if __name__ == '__main__':
        __builtin__.__dict__['_'] = unicode_translation
        # __builtin__.__dict__['_'] = wx.GetTranslation


if enablewx:
    try:
        import wx

        havewx = True
    except ImportError:
        print("Wx unavailable !")
        havewx = False

    if havewx:
        import re
        from types import *

        if wx.VERSION >= (3, 0, 0):
            app = wx.App(redirect=True)
        else:
            app = wx.App(redirect=True)
        app.SetTopWindow(wx.Frame(None, -1))

        default_locale = None
        SetupI18n()

        defaulticon = wx.Image(Bpath("images", "brz.png"))
        starticon = wx.Image(Bpath("images", "icoplay24.png"))
        stopicon = wx.Image(Bpath("images", "icostop24.png"))


        class ParamsEntryDialog(wx.TextEntryDialog):
            if wx.VERSION < (2, 6, 0):
                def Bind(self, event, function, id=None):
                    if id is not None:
                        event(self, id, function)
                    else:
                        event(self, function)

            def __init__(self, parent, message, caption=_("Please enter text"), defaultValue="",
                         style=wx.OK | wx.CANCEL | wx.CENTRE, pos=wx.DefaultPosition):
                wx.TextEntryDialog.__init__(self, parent, message, caption, defaultValue, style, pos)

                self.Tests = []
                if wx.VERSION >= (2, 8, 0):
                    self.Bind(wx.EVT_BUTTON, self.OnOK, id=self.GetAffirmativeId())
                elif wx.VERSION >= (2, 6, 0):
                    self.Bind(wx.EVT_BUTTON, self.OnOK,
                              id=self.GetSizer().GetItem(3).GetSizer().GetAffirmativeButton().GetId())
                else:
                    self.Bind(wx.EVT_BUTTON, self.OnOK,
                              id=self.GetSizer().GetItem(3).GetSizer().GetChildren()[0].GetSizer().GetChildren()[
                                  0].GetWindow().GetId())

            def OnOK(self, event):
                value = self.GetValue()
                texts = {"value": value}
                for function, message in self.Tests:
                    if not function(value):
                        message = wx.MessageDialog(self, message % texts, _("Error"), wx.OK | wx.ICON_ERROR)
                        message.ShowModal()
                        message.Destroy()
                        return
                self.EndModal(wx.ID_OK)
                event.Skip()

            def GetValue(self):
                return self.GetSizer().GetItem(1).GetWindow().GetValue()

            def SetTests(self, tests):
                self.Tests = tests


        class BeremizTaskBarIcon(wx.TaskBarIcon):
            TBMENU_SHOW = wx.NewId()
            TBMENU_START = wx.NewId()
            TBMENU_STOP = wx.NewId()
            TBMENU_CHANGE_NAME = wx.NewId()
            TBMENU_CHANGE_PORT = wx.NewId()
            TBMENU_CHANGE_INTERFACE = wx.NewId()
            TBMENU_LIVE_SHELL = wx.NewId()
            TBMENU_WXINSPECTOR = wx.NewId()
            TBMENU_CHANGE_WD = wx.NewId()
            TBMENU_QUIT = wx.NewId()

            def __init__(self, pyroserver, level):
                wx.TaskBarIcon.__init__(self)
                self.pyroserver = pyroserver
                # Set the image
                self.UpdateIcon(None)
                self.level = level

                # bind some events
                self.Bind(wx.EVT_MENU, self.OnTaskBarShow, id=self.TBMENU_SHOW)
                self.Bind(wx.EVT_MENU, self.OnTaskBarStartPLC, id=self.TBMENU_START)
                self.Bind(wx.EVT_MENU, self.OnTaskBarStopPLC, id=self.TBMENU_STOP)
                self.Bind(wx.EVT_MENU, self.OnTaskBarChangeName, id=self.TBMENU_CHANGE_NAME)
                self.Bind(wx.EVT_MENU, self.OnTaskBarChangeInterface, id=self.TBMENU_CHANGE_INTERFACE)
                self.Bind(wx.EVT_MENU, self.OnTaskBarLiveShell, id=self.TBMENU_LIVE_SHELL)
                self.Bind(wx.EVT_MENU, self.OnTaskBarWXInspector, id=self.TBMENU_WXINSPECTOR)
                self.Bind(wx.EVT_MENU, self.OnTaskBarChangePort, id=self.TBMENU_CHANGE_PORT)
                self.Bind(wx.EVT_MENU, self.OnTaskBarChangeWorkingDir, id=self.TBMENU_CHANGE_WD)
                self.Bind(wx.EVT_MENU, self.OnTaskBarQuit, id=self.TBMENU_QUIT)

            def CreatePopupMenu(self):
                """
                This method is called by the base class when it needs to popup
                the menu for the default EVT_RIGHT_DOWN event.  Just create
                the menu how you want it and return it from this function,
                the base class takes care of the rest.
                """
                menu = wx.Menu()
                menu.Append(self.TBMENU_SHOW, _("Show"))
                # menu.Append(self.TBMENU_START, _("Start PLC"))
                # menu.Append(self.TBMENU_STOP, _("Stop PLC"))
                if self.level == 1:
                    menu.AppendSeparator()
                # menu.Append(self.TBMENU_CHANGE_NAME, _("Change Name"))
                # menu.Append(self.TBMENU_CHANGE_INTERFACE, _("Change IP of interface to bind"))
                # menu.Append(self.TBMENU_CHANGE_PORT, _("Change Port Number"))
                # menu.Append(self.TBMENU_CHANGE_WD, _("Change working directory"))
                # menu.AppendSeparator()
                #  menu.Append(self.TBMENU_LIVE_SHELL, _("Launch a live Python shell"))
                # menu.Append(self.TBMENU_WXINSPECTOR, _("Launch WX GUI inspector"))
                # menu.AppendSeparator()
                menu.Append(self.TBMENU_QUIT, _("Quit"))
                return menu

            def MakeIcon(self, img):
                """
                The various platforms have different requirements for the
                icon size...
                """
                icon = None
                try:

                    if "wxMSW" in wx.PlatformInfo:
                        img = img.Scale(16, 16)
                    elif "wxGTK" in wx.PlatformInfo:
                        img = img.Scale(22, 22)
                    # wxMac can be any size upto 128x128, so leave the source img alone....
                    icon = wx.IconFromBitmap(img.ConvertToBitmap())  # wx.Icon(img.ConvertToBitmap())
                except Exception:
                    print("exeption")
                return icon

            def OnTaskBarShow(self, evt):
                frame.Show()

            def OnTaskBarStartPLC(self, evt):
                if self.pyroserver.plcobj is not None:
                    plcstatus = self.pyroserver.plceobj.GetPLCstatus()[0]
                    if plcstatus is "Stopped":
                        self.pyroserver.plcobj.StartPLC()
                    else:
                        print(_("PLC is empty or already started."))

            def OnTaskBarStopPLC(self, evt):
                if self.pyroserver.plcobj is not None:
                    if self.pyroserver.plcobj.GetPLCstatus()[0] == "Started":
                        Thread(target=self.pyroserver.plcobj.StopPLC).start()
                    else:
                        print(_("PLC is not started."))

            def OnTaskBarChangeInterface(self, evt):
                ip_addr = self.pyroserver.ip_addr
                ip_addr = '' if ip_addr is None else ip_addr
                dlg = ParamsEntryDialog(None, _("Enter the IP of the interface to bind"), defaultValue=ip_addr)
                dlg.SetTests([(re.compile('\d{1,3}(?:\.\d{1,3}){3}$').match, _("IP is not valid!")),
                              (lambda x: len([x for x in x.split(".") if 0 <= int(x) <= 255]) == 4,
                               _("IP is not valid!"))])
                if dlg.ShowModal() == wx.ID_OK:
                    self.pyroserver.ip_addr = dlg.GetValue()
                    self.pyroserver.Stop()

            def OnTaskBarChangePort(self, evt):
                dlg = ParamsEntryDialog(None, _("Enter a port number "), defaultValue=str(self.pyroserver.port))
                dlg.SetTests([(UnicodeType.isdigit, _("Port number must be an integer!")),
                              (lambda port: 0 <= int(port) <= 65535, _("Port number must be 0 <= port <= 65535!"))])
                if dlg.ShowModal() == wx.ID_OK:
                    self.pyroserver.port = int(dlg.GetValue())
                    self.pyroserver.Stop()

            def OnTaskBarChangeWorkingDir(self, evt):
                dlg = wx.DirDialog(None, _("Choose a working directory "), self.pyroserver.workdir,
                                   wx.DD_NEW_DIR_BUTTON)
                if dlg.ShowModal() == wx.ID_OK:
                    self.pyroserver.workdir = dlg.GetPath()
                    self.pyroserver.Stop()
                    # self.pyroserver.plcobj.StartPLC()

            def OnTaskBarChangeName(self, evt):
                servicename = self.pyroserver.servicename
                servicename = '' if servicename is None else servicename
                dlg = ParamsEntryDialog(None, _("Enter a name "), defaultValue=servicename)
                dlg.SetTests([(lambda name: len(name) is not 0, _("Name must not be null!"))])
                if dlg.ShowModal() == wx.ID_OK:
                    self.pyroserver.servicename = dlg.GetValue()
                    self.pyroserver.Restart()

            def _LiveShellLocals(self):
                if self.pyroserver.plcobj is not None:
                    return {"locals": self.pyroserver.plcobj.python_runtime_vars}
                else:
                    return {}

            def OnTaskBarLiveShell(self, evt):
                from wx import py
                frame = py.crust.CrustFrame(**self._LiveShellLocals())
                frame.Show()

            def OnTaskBarWXInspector(self, evt):
                # Activate the widget inspection tool
                from wx.lib.inspection import InspectionTool
                if not InspectionTool().initialized:
                    InspectionTool().Init(**self._LiveShellLocals())

                wnd = wx.GetApp()
                InspectionTool().Show(wnd, True)

            def OnTaskBarQuit(self, evt):
                if wx.Platform == '__WXMSW__':
                    Thread(target=self.pyroserver.Stop).start()
                    Thread(target=self.pyroserver.Quit).start()
                self.RemoveIcon()
                wx.CallAfter(wx.GetApp().ExitMainLoop)
                wx.CallAfter(frame.Exit)

            def UpdateIcon(self, plcstatus):
                if plcstatus is "Started":
                    currenticon = self.MakeIcon(starticon)
                elif plcstatus is "Stopped":
                    currenticon = self.MakeIcon(stopicon)
                else:
                    currenticon = self.MakeIcon(defaulticon)
                self.SetIcon(currenticon, "PLC Service")

            def TaskBarQuit(self):
                pyroserver.Stop()
                if wx.Platform == '__WXMSW__':
                    Thread(target=self.pyroserver.Stop).start()
                    Thread(target=self.pyroserver.Quit).start()
                self.RemoveIcon()
                wx.CallAfter(wx.GetApp().ExitMainLoop)
                wx.CallAfter(frame.Exit)

if not os.path.isdir(WorkingDir):
    os.mkdir(WorkingDir)

if not os.path.isdir(scadaVplc):
    os.mkdir(scadaVplc)


# TODO разобрать что это
def default_evaluator(tocall, *args, **kwargs):
    try:
        res = (tocall(*args, **kwargs), None)
    except Exception:
        res = (None, sys.exc_info())
    return res


class Server(object):
    def __init__(self, servicename, ip_addr, port,
                 workdir, argv, autostart=False,
                 statuschange=None, evaluator=default_evaluator,
                 pyruntimevars=None):
        self.continueloop = True
        self.daemon = None
        self.servicename = servicename
        self.ip_addr = ip_addr
        self.port = port
        self.workdir = workdir
        self.argv = argv
        self.plcobj = None
        self.servicepublisher = None
        self.autostart = autostart
        self.statuschange = statuschange
        self.evaluator = evaluator
        self.pyruntimevars = pyruntimevars

    def Loop(self):
        while self.continueloop:
            self.Start()

    def Restart(self):
        self.Stop()
        self.Start()

    def Quit(self):
        self.continueloop = False
        if self.plcobj is not None:
            self.plcobj.StopPLC()
            self.plcobj.UnLoadPLC()
        self.Stop()

    def Start(self):
        pyro.initServer()
        self.daemon = pyro.Daemon(host=self.ip_addr, port=self.port)
        self.plcobj = PLCObject(self.workdir, self.daemon, self.argv,
                                self.statuschange, self.evaluator,
                                self.pyruntimevars)
        uri = self.daemon.connect(self.plcobj, "PLCObject")

        print(_("PLC service port :"), self.port)
        print(_("PLC service object's uri :"), uri)

        # Beremiz IDE detects daemon start by looking
        # for self.workdir in the daemon's stdout.
        # Therefore don't delete the following line
        print(_("Current working directory :"), self.workdir)

        # Configure and publish service
        # Not publish service if localhost in address params
        if self.servicename is not None and \
                self.ip_addr is not None and \
                self.ip_addr != "localhost" and \
                self.ip_addr != "127.0.0.1":
            print(_("Publishing service on local network"))
            self.servicepublisher = ServicePublisher.ServicePublisher()
            self.servicepublisher.RegisterService(self.servicename, self.ip_addr, self.port)

        self.plcobj.AutoLoad()
        if self.plcobj.GetPLCstatus()[0] != "Empty":
            if self.autostart:
                self.plcobj.StartPLC()
        self.plcobj.StatusChange()

        sys.stdout.flush()

        self.daemon.requestLoop()
        self.daemon.sock.close()

    def Stop(self):
        if self.plcobj is not None:
            self.plcobj.StopPLC()
        if self.servicepublisher is not None:
            self.servicepublisher.UnRegisterService()
            self.servicepublisher = None
        self.daemon.shutdown(True)


if enabletwisted:
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            if havewx:
                from twisted.internet import wxreactor

                wxreactor.install()
            from twisted.internet import reactor

            havetwisted = True
        except ImportError:
            print(_("Twisted unavailable."))
            havetwisted = False

pyruntimevars = {}
statuschange = []

if havetwisted:

    if havewx:
        reactor.registerWxApp(app)

if havewx:
    wx_eval_lock = Semaphore(0)
    main_thread = currentThread()


    def statuschangeTskBar(status):
        wx.CallAfter(taskbar_instance.UpdateIcon, status)
        frame.ChangeButtonIcon()
        #wx.CallAfter(frame.ChangeButtonIcon())


    def exitTskBar():
        wx.CallAfter(taskbar_instance.TaskBarQuit())


    statuschange.append(statuschangeTskBar)


    def wx_evaluator(obj, *args, **kwargs):
        tocall, args, kwargs = obj.call
        obj.res = default_evaluator(tocall, *args, **kwargs)
        wx_eval_lock.release()


    def evaluator(tocall, *args, **kwargs):
        if main_thread == currentThread():
            # avoid dead lock if called from the wx mainloop
            return default_evaluator(tocall, *args, **kwargs)
        else:
            o = type('', (object,), dict(call=(tocall, args, kwargs), res=None))
            wx.CallAfter(wx_evaluator, o)
            wx_eval_lock.acquire()
            return o.res


    pyroserver = Server(servicename, given_ip, port,
                        WorkingDir, argv, autostart,
                        statuschange, evaluator, pyruntimevars)

    taskbar_instance = BeremizTaskBarIcon(pyroserver, enablewx)
else:
    pyroserver = Server(servicename, given_ip, port,
                        WorkingDir, argv, autostart,
                        statuschange, pyruntimevars=pyruntimevars)


# Exception hooks s


def LogException(*exp):
    if pyroserver.plcobj is not None:
        pyroserver.plcobj.LogMessage(0, '\n'.join(traceback.format_exception(*exp)))
    else:
        traceback.print_exception(*exp)
    Extract_info('\n'.join(traceback.format_exception(*exp)))


sys.excepthook = LogException


def installThreadExcepthook():
    init_old = threading.Thread.__init__

    def init(self, *args, **kwargs):
        init_old(self, *args, **kwargs)
        run_old = self.run

        def run_with_except_hook(*args, **kw):
            try:
                run_old(*args, **kw)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                sys.excepthook(*sys.exc_info())

        self.run = run_with_except_hook

    threading.Thread.__init__ = init


installThreadExcepthook()

# запуск WEB-сервиса
# ВЫКЛЮчАЕМ
# if havetwisted:
#     if webport is not None:
#         try:
#             import runtime.NevowServer as NS  # pylint: disable=ungrouped-imports
#         except Exception, e:
#             print(_("Nevow/Athena import failed :"), e)
#             webport = None
#         NS.WorkingDir = WorkingDir
#
#         # if wampconf is not None:
#         #     try:
#         #         import runtime.WampClient as WC  # pylint: disable=ungrouped-imports
#         #     except Exception, e:
#         #         print(_("WAMP import failed :"), e)
#         wampconf = None

# Load extensions
for extfilename in extensions:
    extension_folder = os.path.split(os.path.realpath(extfilename))[0]
    sys.path.append(extension_folder)
    execfile(extfilename, locals())

# if havetwisted:
#     if webport is not None:
#         try:
#             website = NS.RegisterWebsite(webport)
#             pyruntimevars["website"] = website
#             statuschange.append(NS.website_statuslistener_factory(website))
#         except Exception, e:
#             print(_("Nevow Web service failed. "), e)

# if wampconf is not None:
#     try:
#         WC.RegisterWampClient(wampconf)
#         pyruntimevars["wampsession"] = WC.GetSession
#         WC.SetServer(pyroserver)
#     except Exception, e:
#         print(_("WAMP client startup failed. "), e)

if __name__ == '__main__':
    # app = wx.App(redirect=True)
    frame = MyFrame(None, 'PLC service')  # ToolbarFrame(parent=None, id=-1)
    if config_debug_mode() == 'true':
        frame.Show()

    __builtin__.__dict__['_'] = lambda x: x
    if havetwisted or havewx:
        pyro_thread = Thread(target=pyroserver.Loop)
        pyro_thread.start()

        if havetwisted:
            reactor.run()
        elif havewx:
            app.MainLoop()
    else:
        try:
            pyroserver.Loop()
        except KeyboardInterrupt, e:
            pass

    app.MainLoop()

# if havetwisted or havewx:
#     pyro_thread = Thread(target=pyroserver.Loop)
#     pyro_thread.start()
#
#     if havetwisted:
#         reactor.run()
#     elif havewx:
#         app.MainLoop()
# else:
#     try:
#         pyroserver.Loop()
#     except KeyboardInterrupt, e:
#         pass
pyroserver.Quit()
sys.exit(0)
