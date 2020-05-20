import sys
import datetime
import os
from pathlib import Path
import traceback
import pandas as pd
import numpy as np
import calendar
from statistics import mean
from scipy.interpolate import interp1d as interp
import sqlite3
#%%######################################################################################################
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Qt5Agg")
#%%######################################################################################################
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5 import QtTest
from PyQt5.QtCore import Qt, QThread, pyqtSignal
# from PyQt5.QtCore.QElapsedTimer import timer
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QAction, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import time
import copy
import xlsxwriter
import xlrd
from scipy import integrate
from operator import itemgetter
from itertools import groupby, chain
from PIL import Image as ImageTk
from matplotlib.ticker import MaxNLocator
from matplotlib.transforms import Bbox
import pickle
import six
from functools import partial
import darktolight as DtoL
import os.path
import shutil
from dateutil import parser
from scipy import stats
from statistics import mean
from scipy.interpolate import interp1d

from PyQt5.uic import loadUiType
Ui_MainWindow, QMainWindow = loadUiType('spectrogui.ui')


class Spectroapp(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.fig = Figure()
        self.Spectrograph = self.fig.add_subplot(111)
        self.addmpl(self.fig,self.ui.verticalLayout_mplwidget, self.ui.mplwidget)

    def addmpl(self, fig, whereLayout, whereWidget):
        self.canvas = FigureCanvas(fig)
        whereLayout.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, 
                whereWidget, coordinates=True)
        whereLayout.addWidget(self.toolbar)
        
#%%#############
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Spectroapp()
    window.show()
    sys.exit(app.exec())

