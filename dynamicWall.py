import ctypes
import os
import random
from sys import platform
import datetime
from enum import Enum
import time

class Type(Enum):
    RANDOM = 1
    STEP_BY_STEP = 2
    TIME = 3

class DinamicWall:
    UPDATE_TIME_SEC = 10
    TYPE = Type.TIME
    DIR_PATH = "C:/Users/Daniil (WORK)/Desktop/dynamicWall/wall/1"

    def __init__(self):
        self.images = []
        self.curImageId = 0

    def _setWallWindows(self, path):
        SPI_SETDESKWALLPAPER = 20 
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path , 0)

    def _setWallLinux(self, path):
        os.system("feh --bg-scale " + path)

    def getImagesPaths(self):
        images = []
        for filename in os.listdir(self.DIR_PATH):
            img = os.path.join(self.DIR_PATH, filename)
            if img is not None:
                images.append(img)
        self.images = images

    def randomWall(self):
        self.getImagesPaths()
        if len(self.images) == 0:
            print("Error:randomWall: images size is 0")
            return
        choice = random.randint(0, len(self.images)-1)
        if platform == "linux" or platform == "linux2":
            self._setWallLinux(self.images[choice])
        elif platform == "win32":
            self._setWallWindows(self.images[choice])

    def stepByStepWall(self):
        self.getImagesPaths()
        if len(self.images) == 0:
            print("Error:stepByStepWall: images size is 0")
            return
        if platform == "linux" or platform == "linux2":
            self._setWallLinux(self.images[self.curImageId])
        elif platform == "win32":
            self._setWallWindows(self.images[self.curImageId])
        self.curImageId+=1
        if (self.curImageId == len(self.images)):
            self.curImageId = 0

    def timeWall(self):
        self.getImagesPaths()
        if len(self.images) == 0:
            print("Error:timeWall: images size is 0")
            return

        cur = datetime.datetime.now()
        curSec = cur.hour*3600 + cur.minute*60 + cur.second
        secondInDay = 86400
        curImageId = int(curSec / (secondInDay / len(self.images)))
        if self.curImageId == curImageId:
            return
        self.curImageId = curImageId
        if platform == "linux" or platform == "linux2":
            self._setWallLinux(self.images[self.curImageId])
        elif platform == "win32":
            self._setWallWindows(self.images[self.curImageId])

    def loop(self):
        while (True):
            self.step()

    def step(self):
        if (self.TYPE == Type.RANDOM):
            self.randomWall()
        elif (self.TYPE == Type.TIME):
            self.timeWall()
        else:
            self.stepByStepWall()
        time.sleep(self.UPDATE_TIME_SEC)



dw = DinamicWall()
dw.loop()
