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

_WORKERW = None

class Main(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.initUI()
    def EnumWindowsProc(self, tophandle, topparamhandle):
        global _WORKERW
        defview = win32gui.FindWindowEx(tophandle, 0, "SHELLDLL_DefView", None)
        if (defview != None):
            _WORKERW = win32gui.FindWindowEx(0, tophandle, "WorkerW", None)
        return True

    def initUI(self):
        self.load(QUrl('https://www.google.com/'))
        #time.sleep(5)
        workerW = win32gui.FindWindow("Progman", None)
        print(workerW)
        win32gui.SendMessageTimeout(workerW, 0x052c, 0 ,0, win32con.SMTO_NORMAL, 0x3e8)
        win32gui.EnumWindows(self.EnumWindowsProc, None)
        win32gui.ShowWindow(_WORKERW, win32con.SW_HIDE)
        
        viewId = self.winId()

        win32gui.GetWindowLong(viewId, win32con.GWL_STYLE)
        win32gui.SetParent(viewId, workerW)
        win32gui.SetWindowPos(viewId, win32con.HWND_TOP, 0,0,0,0, \
            win32con.WS_EX_LEFT|win32con.WS_EX_LTRREADING|win32con.WS_EX_RIGHTSCROLLBAR)#|win32con.WS_EX_NOACTIVATE)
        
        self.show()
        
app = QApplication(sys.argv)
main = Main()
app.exec_()
