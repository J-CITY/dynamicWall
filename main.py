#pip install pywin32
#pip install PyQtWebEngine
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView, QWebEnginePage
import PyQt5
import sys
import win32gui
import win32con
import time

import ctypes
from typing import List
from ctypes.wintypes import HWND

user32 = ctypes.windll.user32

_WORKERW = None

def EnumWindowsProc():
    def cb(tophandle: int, topparamhandle: list):
        global _WORKERW
        defview = win32gui.FindWindowEx(tophandle, 0, "SHELLDLL_DefView", None)
        if (defview != None):
            _WORKERW = win32gui.FindWindowEx(0, tophandle, "WorkerW", None)
        return True
    return cb

class Main(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def _makeFilter(self, className: str, title: str):
        def enumWindows(handle: int, h_list: list):
            if not (className or title):
                h_list.append(handle)
            if className and className not in win32gui.GetClassName(handle):
                return True  # continue enumeration
            if title and title not in win32gui.GetWindowText(handle):
                return True  # continue enumeration
            h_list.append(handle)
        return enumWindows
        
    def _findWindowHandles(self, parent: int = None, windowClass: str = None, title: str = None) -> List[int]:
        cb = self._makeFilter(windowClass, title)
        try:
            handle_list = []
            if parent:
                win32gui.EnumChildWindows(parent, cb, handle_list)
            else:
                win32gui.EnumWindows(cb, handle_list)
            return handle_list
        except pywintypes.error:
            return []

    def initUI(self):
        workerW = self._findWindowHandles(windowClass='Progman')[0]
        crypticParams = (0x52c, 0, 0, win32con.SMTO_NORMAL, 0x3e8, None)
        user32.SendMessageTimeoutW(workerW, *crypticParams)
        win32gui.EnumWindows(EnumWindowsProc(), None)
        win32gui.ShowWindow(_WORKERW, win32con.SW_HIDE)
        
        viewId = self.winId()

        win32gui.GetWindowLong(viewId, win32con.GWL_STYLE)
        win32gui.SetParent(viewId, workerW)
        win32gui.SetWindowPos(viewId, win32con.HWND_TOP, 0,0,0,0, \
            win32con.WS_EX_LEFT|win32con.WS_EX_LTRREADING|win32con.WS_EX_RIGHTSCROLLBAR|win32con.SWP_NOACTIVATE)
        
        self.load(QUrl('https://www.google.com/'))
        self.showFullScreen()
        self.show()
        
app = QApplication(sys.argv)
main = Main()
app.exec_()
