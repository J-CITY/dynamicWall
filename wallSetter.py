import ctypes
import os
import random
from sys import platform
import datetime
from enum import Enum
import time

import ctypes
from typing import List

import pythoncom
import pywintypes
import win32gui
import argparse
from win32com.shell import shell, shellcon

user32 = ctypes.windll.user32

class Type(Enum):
	RANDOM = 1
	STEP_BY_STEP = 2
	TIME = 3

class DinamicWall:
	UPDATE_TIME_SEC = 60
	TYPE = Type.RANDOM
	DIR_PATH = "./image"
	IS_SMOOTH = True

	def __init__(self):
		self.images = []
		self.curImageId = 0

	def _setWallWindows(self, path):
		if not self.IS_SMOOTH:
			SPI_SETDESKWALLPAPER = 20 
			ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path , 0)
		else:
			self._setWallpaper(path)

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

	def _enableActivedesktop(self):
		try:
			progman = self._findWindowHandles(windowClass='Progman')[0]
			crypticParams = (0x52c, 0, 0, 0, 500, None)
			user32.SendMessageTimeoutW(progman, *crypticParams)
		except IndexError as e:
			raise WindowsError('Cannot enable Active Desktop') from e

	def _setWallpaper(self, imagePath: str, useActivedesktop: bool = True):
		if useActivedesktop:
			self._enableActivedesktop()
		pythoncom.CoInitialize()
		iad = pythoncom.CoCreateInstance(shell.CLSID_ActiveDesktop,
										 None,
										 pythoncom.CLSCTX_INPROC_SERVER,
										 shell.IID_IActiveDesktop)
		iad.SetWallpaper(str(imagePath), 0)
		iad.ApplyChanges(shellcon.AD_APPLY_ALL)
		
		user32.UpdatePerUserSystemParameters(1)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog="Wallpaper setter script", description='Set wallpaper.')
	parser.add_argument('-wallPath', type=str, help="Path to wallpaper folder")
	parser.add_argument('-updateTime', type=int, help="Update in seconds")
	parser.add_argument('-type', type=str, help="RANDOM, ONE_BY_ONE, TIME")
	parser.add_argument('-isNotSmooth', action="store_true", help="Smooth transition")
	parser.set_defaults(isNotSmooth=False)
	args = parser.parse_args()

	dw = DinamicWall()
	if args.isNotSmooth is not None and args.isNotSmooth:
		dw.IS_SMOOTH = False
	if args.updateTime is not None:
		dw.UPDATE_TIME_SEC = args.updateTime
	if args.wallPath is not None:
		dw.DIR_PATH = args.wallPath
	if args.type is not None:
		if args.type == "RANDOM":
			dw.TYPE = Type.RANDOM
		if args.type == "ONE_BY_ONE":
			dw.TYPE = Type.STEP_BY_STEP
		if args.type == "TIME":
			dw.TYPE = Type.TIME
	dw.loop()
