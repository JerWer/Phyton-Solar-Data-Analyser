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
# from IVpyqt5gui import Ui_MainWindow
from PyQt5.uic import loadUiType


#%%############# Global variable definition
file_path=[]
testdata = []
DATA = {} #{sampleID: {"SampleName":, "CellNumber": , "MeasDayTime":, "CellSurface":, "Voc":, "Jsc":, "FF":, "Eff":, "Pmpp":, "Vmpp":, "Jmpp":, "Roc":, "Rsc":, "VocFF":, "RscJsc":, "NbPoints":, "Delay":, "IntegTime":, "Vstart":, "Vend":, "Illumination":, "ScanDirection":, "ImaxComp":, "Isenserange":,"AreaJV":, "Operator":, "MeasComment":, "IVData":}]
DATAJVforexport=[]
DATAJVtabforexport=[]
DATAmppforexport=[]
DATAgroupforexport=[]
DATAHistforexport=[]
DATAcompforexport=[]
DATAtimeevolforexport={}#key: [[realtimeF, relativetimeF, valueF, normalizedvaluetot0F, realtimeR, relativetimeR, valueR, normalizedvaluetot0R]]
takenforplot=[]
takenforplotmpp=[]
takenforplotTime=[]

DATAMPP = {}
DATAdark = []
DATAFV=[]

numbLightfiles=0
numbDarkfiles=0

IVlegendMod = []
IVlinestyle = []
colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']
colormapname="jet"

MPPlegendMod = []
MPPlinestyle = []

titIV =0
titmpp=0
titStat=0
samplesgroups=["Default group"]
groupstoplot=["Default group"]
groupstoplotcomp=["Default group"]

listofanswer=[]
listoflinestyle=[]
listofcolorstyle=[]
listoflinewidthstyle=[]

#%%#############
def modification_date(path_to_file):
    return datetime.datetime.fromtimestamp(os.path.getmtime(path_to_file)).strftime("%Y-%m-%d %H:%M:%S")


Ui_MainWindow, QMainWindow = loadUiType('IVpyqt5gui.ui')


#%%#############

class IVapp(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.fig1 = Figure()
        self.JVgraph = self.fig1.add_subplot(111)
        self.JVgraph.set_xlabel('Voltage (mV)')
        self.JVgraph.set_ylabel('Current density (mA/cm'+'\xb2'+')')
        self.JVgraph.axhline(y=0, color='k')
        self.JVgraph.axvline(x=0, color='k')
        self.addmpl(self.fig1,self.ui.gridLayout_5, self.ui.widget_JVGraph)

        self.fig2 = Figure()
        self.MPPgraph = self.fig2.add_subplot(111)
        self.MPPgraph.set_ylabel('Power (mW/cm'+'\xb2'+')')
        self.MPPgraph.set_xlabel('Time (s)')
        self.addmpl(self.fig2,self.ui.gridLayout_2, self.ui.widget_Mpp)
        
        self.fig3 = Figure()
        self.Boxgraph = self.fig3.add_subplot(111)
        self.addmpl(self.fig3,self.ui.gridLayout_7, self.ui.widget_BoxPlot)
        
        self.fig4 = Figure()
        self.TimeEvolraph = self.fig4.add_subplot(111)
        self.addmpl(self.fig4,self.ui.gridLayout_10, self.ui.widget_PVPTime)
        
        self.fig5 = Figure()
        self.ParamParamgraph = self.fig5.add_subplot(111)
        self.addmpl(self.fig5,self.ui.gridLayout_11, self.ui.widget_PVPGraph)
        
        self.fig6 = Figure()
        self.Histgraph = self.fig6.add_subplot(111)
        self.addmpl(self.fig6,self.ui.gridLayout_13, self.ui.widget_HistoGraph)
        
        finish = QAction("Quit", self)
        finish.triggered.connect(lambda: self.closeEvent(1))
        
        self.ui.actionLoad.triggered.connect(self.LoadSession)
        self.ui.actionSave.triggered.connect(self.SaveSession)
        self.ui.actionLoad_2.triggered.connect(lambda: self.loadconfigsgui(''))
        self.ui.actionSave_2.triggered.connect(lambda: self.saveconfigsgui(''))
        self.ui.actionSave_to_DB.triggered.connect(self.SaveToDB)
        
        self.ui.pushButton_ImportData.clicked.connect(self.startimporting)
        self.ui.pushButton_DeleteRows.clicked.connect(self.DeleteRows)
        self.ui.pushButton_DefineGroup.clicked.connect(self.Confirmgroupnamechanges)
        
        self.ui.radioButton_JVtopleft.toggled.connect(self.PlotIV)
        self.ui.radioButton_JVtopright.toggled.connect(self.PlotIV)
        self.ui.radioButton_JVbottomleft.toggled.connect(self.PlotIV)
        self.ui.radioButton_JVbottomright.toggled.connect(self.PlotIV)
        self.ui.radioButton_JVoutside.toggled.connect(self.PlotIV)
        self.ui.radioButton_JVBest.toggled.connect(self.PlotIV)
        self.ui.checkBox_JVLegend.toggled.connect(self.PlotIV)
        self.ui.pushButton_PlotJV.clicked.connect(self.PlotIV)
        self.ui.pushButton_SaveJV.clicked.connect(self.GraphJVsave_as)
        self.ui.spinBox_JVfontsize.valueChanged.connect(self.PlotIV)
        
        self.ui.radioButton_MppTopleft.toggled.connect(self.PlotMPP)
        self.ui.radioButton_MppTopright.toggled.connect(self.PlotMPP)
        self.ui.radioButton_MppBottomleft.toggled.connect(self.PlotMPP)
        self.ui.radioButton_MppBottomright.toggled.connect(self.PlotMPP)
        self.ui.radioButton_MppOutside.toggled.connect(self.PlotMPP)
        self.ui.radioButton_MppBest.toggled.connect(self.PlotMPP)
        self.ui.checkBox_MppLegend.toggled.connect(self.PlotMPP)
        self.ui.listWidget_MppSamples.itemClicked.connect(self.PlotMPP)
        self.ui.pushButton_SaveMpp.clicked.connect(self.GraphMPPsave_as)
        self.ui.listWidget_MppSamples.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ui.spinBox_MppFontsize.valueChanged.connect(self.PlotMPP)
        
        self.ui.listWidget_HistoGroups.itemClicked.connect(self.UpdateHistGraph)
        self.ui.comboBox_HistoParam.currentTextChanged.connect(self.UpdateHistGraph)
        self.ui.comboBox_HistoScanDirect.currentTextChanged.connect(self.UpdateHistGraph)
        self.ui.comboBox_HistoType.currentTextChanged.connect(self.UpdateHistGraph)
        self.ui.checkBox_Histxscale.toggled.connect(self.UpdateHistGraph)
        self.ui.spinBox_HistoBins.valueChanged.connect(self.UpdateHistGraph)
        self.ui.spinBox_HistxscaleMin.valueChanged.connect(self.UpdateHistGraph)
        self.ui.spinBox_HistxscaleMax.valueChanged.connect(self.UpdateHistGraph)
        self.ui.pushButton_SaveHistoGraph.clicked.connect(self.GraphHistsave_as)
        self.ui.listWidget_HistoGroups.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.ui.listWidget_BoxPlotGroup.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ui.listWidget_BoxPlotGroup.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.ui.listWidget_BoxPlotGroup.itemClicked.connect(self.UpdateBoxGraph)
        self.ui.comboBox_BoxPlotParam.currentTextChanged.connect(self.UpdateBoxGraph)
        self.ui.checkBox_BoxPlotAftermpp.toggled.connect(self.UpdateBoxGraph)
        self.ui.checkBox_BoxPlotBkg.toggled.connect(self.UpdateBoxGraph)
        self.ui.spinBox_BoxPlotRotation.valueChanged.connect(self.UpdateBoxGraph)
        self.ui.spinBox_BoxPlotFontsize.valueChanged.connect(self.UpdateBoxGraph)
        self.ui.checkBox_BoxPlotBoxPlot.toggled.connect(self.UpdateBoxGraph)
        self.ui.checkBox_BoxPlotRevForw.toggled.connect(self.UpdateBoxGraph)
        self.ui.pushButton_SaveBoxPlot.clicked.connect(self.GraphBoxsave_as)
        
        self.ui.pushButton_SavePVPTime.clicked.connect(self.GraphTimesave_as)
        self.ui.pushButton_PVPTimePlot.clicked.connect(self.plottingTimefromTable)
        self.ui.checkBox_PVPTimeBig4.toggled.connect(self.UpdateTimeGraph)
        self.ui.checkBox_PVPTimeLine.toggled.connect(self.UpdateTimeGraph)
        self.ui.checkBox_PVPTimeRelativeTime.toggled.connect(self.UpdateTimeGraph)
        self.ui.checkBox_PVPTimeNormal.toggled.connect(self.UpdateTimeGraph)
        self.ui.checkBox_bestofRevFor.toggled.connect(self.UpdateTimeGraph)
        self.ui.checkBox_BestEffPixDay.toggled.connect(self.UpdateTimeGraph)
        self.ui.spinBox_PVPTimeNormalPoint.valueChanged.connect(self.UpdateTimeGraph)
        self.ui.comboBox_PVPTimeParam.currentTextChanged.connect(self.UpdateTimeGraph)
        
        self.ui.pushButton_SavePVPGraph.clicked.connect(self.GraphCompsave_as)
        self.ui.comboBox_PVPx.currentTextChanged.connect(self.UpdateCompGraph)
        self.ui.comboBox_PVPy.currentTextChanged.connect(self.UpdateCompGraph)
        self.ui.listWidget_ParamComp.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ui.listWidget_ParamComp.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.ui.listWidget_ParamComp.itemClicked.connect(self.UpdateCompGraph)
        
        self.ui.pushButton_AutoAnalysis.clicked.connect(self.ExportAutoAnalysis)
    
    def addmpl(self, fig, whereLayout, whereWidget):
        self.canvas = FigureCanvas(fig)
        whereLayout.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, 
                whereWidget, coordinates=True)
        whereLayout.addWidget(self.toolbar)
        
    def closeEvent(self, event):
        """ what happens when close the program"""
        global testdata, DATA, DATAJVforexport, DATAJVtabforexport
        global DATAmppforexport, DATAgroupforexport, takenforplot
        global takenforplotmpp, DATAMPP, DATAdark, DATAFV, IVlegendMod,groupstoplot
        global IVlinestyle, colorstylelist, MPPlegendMod, MPPlinestyle
        global titIV, titmpp, titStat, samplesgroups, listofanswer, listoflinestyle, listofcolorstyle,listoflinewidthstyle
        
        close = QMessageBox.question(self,
                                     "QUIT",
                                     "Are you sure?",
                                      QMessageBox.Yes | QMessageBox.No)
        if close == QMessageBox.Yes:
            testdata = []
            DATA = [] #[{"SampleName":, "CellNumber": , "MeasDayTime":, "CellSurface":, "Voc":, "Jsc":, "FF":, "Eff":, "Pmpp":, "Vmpp":, "Jmpp":, "Roc":, "Rsc":, "VocFF":, "RscJsc":, "NbPoints":, "Delay":, "IntegTime":, "Vstart":, "Vend":, "Illumination":, "ScanDirection":, "ImaxComp":, "Isenserange":,"AreaJV":, "Operator":, "MeasComment":, "IVData":}]
            DATAJVforexport=[]
            DATAJVtabforexport=[]
            DATAmppforexport=[]
            DATAgroupforexport=[]
            takenforplot=[]
            takenforplotmpp=[]
            plt.close()
            DATAMPP = []
            DATAdark = []
            DATAFV=[]
            
            IVlegendMod = []
            IVlinestyle = []
            colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']
            
            MPPlegendMod = []
            MPPlinestyle = []
            
            titIV =0
            titmpp=0
            titStat=0
            samplesgroups=["Default group"]
            groupstoplot=["Default group"]
            
            listofanswer=[]
            listoflinestyle=[]
            listofcolorstyle=[]   
            listoflinewidthstyle=[]

            event.accept()
        else:
            event.ignore()

    def darktolightchange(self):
        DtoL.DarkToLight()
        
    def startimporting(self):
        global DATA 
        global DATAFV
        global DATAMPP
        global DATAdark, numbLightfiles, numbDarkfiles, file_path

        finished=0
        j=0
        while j<2:
            file_pathnew=[]
            file_path = QFileDialog.getOpenFileNames(caption = 'Please select the JV files')[0]
            if file_path!='':
                filetypes=[os.path.splitext(item)[1] for item in file_path]
#                print(list(set(filetypes)))
                if len(list(set(filetypes)))==1 or (''in list(set(filetypes)) and '.txt'in list(set(filetypes))) or (".itx" in list(set(filetypes)) and '.txt'in list(set(filetypes))):
                    directory = os.path.join(str(Path(file_path[0]).parent.parent),'resultFilesIV')
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                        os.chdir(directory)
                    else :
                        os.chdir(directory)
                    filetype=list(set(filetypes))[0]
                    if filetype==".iv":
                        print("these are rawdata files")
                        # self.getdatalistsfromIVTFfiles(file_path)
                        finished=1
                        break
                    elif filetype==".itx" or (".itx" in list(set(filetypes)) and '.txt'in list(set(filetypes))):
                        print("cigs igor text data")
                        # self.getdatalistsfromNRELcigssetup(file_path)
                        finished=1
                        break
                    elif filetype==".txt" or filetype=='':
                        filetoread = open(file_path[0],"r", encoding='ISO-8859-1')
                        filerawdata = filetoread.readlines()
                        # print(filerawdata[0])
                        if '***' in filerawdata[0]:
                            print("NREL files")
                            self.thread = Thread_getdatalistsfromNRELfiles(file_path)
                            self.thread.change_value.connect(self.setProgressVal)
                            self.thread.finished.connect(self.ImportFinished)
                            self.thread.start()
                            finished=1
                        elif '#Boulder Solar Simulator, Python'in filerawdata[0]:
                            print("CUBpython files")
                            self.thread = Thread_getdatalistsfromCUBpyfiles(file_path)
                            self.thread.change_value.connect(self.setProgressVal)
                            self.thread.finished.connect(self.ImportFinished)
                            self.thread.start()
                            finished=1
                        elif 'Notes' in filerawdata[1]:
                            print("CUB files")
                            self.thread = Thread_getdatalistsfromCUBfiles(file_path)
                            self.thread.change_value.connect(self.setProgressVal)
                            self.thread.finished.connect(self.ImportFinished)
                            self.thread.start()
                            finished=1
                        else:
                            print("NREL files")
                            self.thread = Thread_getdatalistsfromCUBfiles(file_path)
                            self.thread.change_value.connect(self.setProgressVal)
                            self.thread.finished.connect(self.ImportFinished)
                            self.thread.start()
                            finished=1
                        break
                    elif filetype==".xls":
                        celltest=[]
                        for k in range(len(file_path)):
                            wb = xlrd.open_workbook(file_path[k])
                            xlsheet = wb.sheet_by_index(0)
                            celltest.append(str(xlsheet.cell(3,0).value))
                        if len(list(set(celltest)))==1:
                            if celltest[0]=="User name:             ":#HIT excel files
                                print("HITfiles")
                                # self.getdatalistsfromIVHITfiles(file_path)
                                finished=1
                                break
                            elif str(xlsheet.cell(3,1).value)=="Cell number":
                                print("thin film files")
                                for k in range(len(file_path)):
                                    wb = xlrd.open_workbook(file_path[k])
                                    sheet_names = wb.sheet_names()
                                    for j in range(len(sheet_names)):
                                        if 'Sheet' not in sheet_names[j]:
                                            xlsheet = wb.sheet_by_index(j)
                                            #print(sheet_names[j])
                                            item=0
                                            while(True):
                                                try:
                                                    #print(item)
                                                    cell1 = xlsheet.cell(68+item,17).value 
                                                    #print(cell1)
                                                    if cell1!="":
                                                        file_pathnew.append(cell1)
                                                        item+=1
                                                    else:
                                                        break
                                                except:
                                                    print("except")
                                                    break
                                # self.getdatalistsfromIVTFfiles(file_pathnew)
                                finished=1
                                break
                            else:
                                QMessageBox.information(self,'Information', 'these are not IV related .xls files... try again')         
                                j+=1
                        else:
                            QMessageBox.information(self,'Information', "several types of .xls files... try again")
                            j+=1
                    else:
                        QMessageBox.information(self,'Information', "neither .iv or .xls IV files... try again")
                        j+=1
                else:
                    QMessageBox.information(self,'Information', "Multiple types of files... please choose one!")
                    j+=1
            else:
                QMessageBox.information(self,'Information', "Please select IV files")
                j+=1

    def ImportFinished(self):
        global file_path
        global DATA, DATAdark
        global DATAMPP, numbLightfiles, numbDarkfiles
        
        print(len(DATA))
        print(len(DATAMPP.keys()))
        
        if DATAMPP!={}:
            self.ui.listWidget_MppSamples.clear()
            self.ui.listWidget_MppSamples.addItems(DATAMPP.keys())

        self.updateTable(DATA)
        
        # self.updategrouptoplotdropbutton()
        # self.updateCompgrouptoplotdropbutton()
        # self.updateHistgrouptoplotdropbutton()
        # self.UpdateGroupGraph(1)
        # self.UpdateCompGraph(1)
        
    def setProgressVal(self, val):
        global DATA
        
        self.ui.progressBar_ImportData.setValue(val)
        
        # self.updateTable(DATA) #fills the table live as data comes. problem is that if the user messes around with the table while it's loading the data gets messed up. 

        
    def updateTable(self, dictdata):
        try:
            self.ui.tableWidget.setRowCount(len(dictdata.keys()))
            self.ui.tableWidget.setHorizontalHeaderLabels(
                ['Group','SampleName','DateTime','Eff. (%)','FF (%)', 'Voc (mV)', 'Jsc (mA/cm2)','Isc (A)', 
                 'Roc (ohm/cm2)', 'Rsc (ohm/cm2)', 'Pmpp (W/m2)', 'Vmpp (mV)', 'Jmpp (mA/cm2)','Area','ScanDirect.','SunInten.'])
            i=0
            for key in dictdata.keys():
                self.ui.tableWidget.setItem(i,0,QTableWidgetItem(dictdata[key]['Group']))
                self.ui.tableWidget.setItem(i,1,QTableWidgetItem(dictdata[key]['SampleName']))
                self.ui.tableWidget.setItem(i,2,QTableWidgetItem(str(dictdata[key]['MeasDayTime2'])))
                self.ui.tableWidget.setItem(i,3,QTableWidgetItem('%.2f' % dictdata[key]['Eff']))
                self.ui.tableWidget.setItem(i,4,QTableWidgetItem('%.2f' % dictdata[key]['FF']))
                self.ui.tableWidget.setItem(i,5,QTableWidgetItem('%.2f' % dictdata[key]['Voc']))
                self.ui.tableWidget.setItem(i,6,QTableWidgetItem('%.2f' % dictdata[key]['Jsc']))
                self.ui.tableWidget.setItem(i,7,QTableWidgetItem('%.2f' % dictdata[key]['Isc']))
                self.ui.tableWidget.setItem(i,8,QTableWidgetItem('%.2f' % dictdata[key]['Roc']))
                self.ui.tableWidget.setItem(i,9,QTableWidgetItem('%.2f' % dictdata[key]['Rsc']))
                self.ui.tableWidget.setItem(i,10,QTableWidgetItem('%.2f' % dictdata[key]['Pmpp']))
                self.ui.tableWidget.setItem(i,11,QTableWidgetItem('%.2f' % dictdata[key]['Vmpp']))
                self.ui.tableWidget.setItem(i,12,QTableWidgetItem('%.2f' % dictdata[key]['Jmpp']))
                self.ui.tableWidget.setItem(i,13,QTableWidgetItem('%.2f' % dictdata[key]['CellSurface']))
                self.ui.tableWidget.setItem(i,14,QTableWidgetItem(dictdata[key]['ScanDirection']))
                self.ui.tableWidget.setItem(i,15,QTableWidgetItem('%.2f' % dictdata[key]['sunintensity']))
                i+=1
        except RuntimeError:
            pass
        
            
    def ClearTable(self):
        self.ui.tableWidget.setRowCount(0)
    
    def DeleteRows(self):
        global DATA
        
        rows=list(set(index.row() for index in self.ui.tableWidget.selectedIndexes()))
        sampleselected=[self.ui.tableWidget.item(row,1).text()+'_'+str(self.ui.tableWidget.item(row,2).text()).replace(' ','_').replace(':','-')+'_'+'%.2f'%float(self.ui.tableWidget.item(row,3).text()) for row in rows]
        
        for item in sampleselected:
            del(DATA[item])
        
        self.updateTable(DATA)
        
    def Confirmgroupnamechanges(self):
        global DATA
        self.ui.listWidget_BoxPlotGroup.clear()
        self.ui.listWidget_HistoGroups.clear()
        self.ui.listWidget_ParamComp.clear()
        
        groupnames=[]
        for i in range(self.ui.tableWidget.rowCount()):
            sn=self.ui.tableWidget.item(i,1).text()+'_'+str(self.ui.tableWidget.item(i,2).text()).replace(' ','_').replace(':','-')+'_'+'%.2f'%float(self.ui.tableWidget.item(i,3).text())
            DATA[sn]['Group']=self.ui.tableWidget.item(i,0).text()
            groupnames.append(self.ui.tableWidget.item(i,0).text())
            
        groupnames=set(groupnames)
        self.ui.listWidget_BoxPlotGroup.addItems(groupnames)
        self.ui.listWidget_HistoGroups.addItems(groupnames)
        self.ui.listWidget_ParamComp.addItems(groupnames)
        
#%%#############
    def PlotMPP(self):
        global DATAMPP, MPPlegendMod, MPPlinestyle
        global DATAmppforexport
        DATAmppforexport=[]
        items = self.ui.listWidget_MppSamples.selectedItems()
        selectedmpptraces = []
        for i in range(len(items)):
            selectedmpptraces.append(str(self.ui.listWidget_MppSamples.selectedItems()[i].text()))
        
        self.MPPgraph.clear()
        for item in selectedmpptraces:
            x = DATAMPP[item]["MppData"][2]
            y = DATAMPP[item]["MppData"][3]
            
            colx=["Time","s",""]+x
            coly=["Power","mW/cm2",DATAMPP[item]["SampleName"]]+y
            DATAmppforexport.append(colx)
            DATAmppforexport.append(coly)
            
            if self.ui.checkBox_MppLegend.isChecked():
                self.MPPgraph.plot(x,y,label=DATAMPP[item]["MPPlinestyle"][0],linestyle=DATAMPP[item]["MPPlinestyle"][1],color=DATAMPP[item]["MPPlinestyle"][2],linewidth=DATAMPP[item]["MPPlinestyle"][3])
            else:
                self.MPPgraph.plot(x,y,linestyle=DATAMPP[item]["MPPlinestyle"][1],color=DATAMPP[item]["MPPlinestyle"][2],linewidth=DATAMPP[item]["MPPlinestyle"][3])
                
        self.MPPgraph.set_ylabel('Power (mW/cm'+'\xb2'+')')
        self.MPPgraph.set_xlabel('Time (s)')
        
        for item in ([self.MPPgraph.title, self.MPPgraph.xaxis.label, self.MPPgraph.yaxis.label] +
                             self.MPPgraph.get_xticklabels() + self.MPPgraph.get_yticklabels()):
            item.set_fontsize(self.ui.spinBox_MppFontsize.value())
        
        if self.ui.checkBox_MppLegend.isChecked():
            if self.ui.radioButton_MppTopleft.isChecked():
                self.leg=self.MPPgraph.legend(loc=2, fontsize = self.ui.spinBox_MppFontsize.value())
            elif self.ui.radioButton_MppTopright.isChecked():
                self.leg=self.MPPgraph.legend(loc=1, fontsize = self.ui.spinBox_MppFontsize.value())
            elif self.ui.radioButton_MppBottomleft.isChecked():
                self.leg=self.MPPgraph.legend(loc=3, fontsize = self.ui.spinBox_MppFontsize.value())
            elif self.ui.radioButton_MppBottomright.isChecked():
                self.leg=self.MPPgraph.legend(loc=4, fontsize = self.ui.spinBox_MppFontsize.value())
            elif self.ui.radioButton_MppOutside.isChecked():
                self.leg=self.MPPgraph.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1, fontsize = self.ui.spinBox_MppFontsize.value())
            elif self.ui.radioButton_MppBest.isChecked():
                self.leg=self.MPPgraph.legend(loc=0, fontsize = self.ui.spinBox_MppFontsize.value())
        
        DATAmppforexport=map(list, six.moves.zip_longest(*DATAmppforexport, fillvalue=' '))

        self.fig2.canvas.draw_idle()
        self.fig2.canvas.flush_events()        
        
    def GraphMPPsave_as(self):
        global DATAmppforexport
        path = QFileDialog.getSaveFileName(self, 'Save graph and data', ".png", "graph file (*.png);; All Files (*)")[0]

        if self.ui.checkBox_MppLegend.isChecked():
            self.fig2.savefig(path, dpi=300, bbox_extra_artists=(self.leg,))#, transparent=True)
        else:
            self.fig2.savefig(path, dpi=300)#, transparent=True)
            
        DATAmppforexport1=[]            
        for item in DATAmppforexport:
            line=""
            for item1 in item:
                line=line+str(item1)+"\t"
            line=line[:-1]+"\n"
            DATAmppforexport1.append(line)
            
        file = open(str(path[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
        file.writelines("%s" % item for item in DATAmppforexport1)
        file.close()

#%%#############
        
    def PlotIV(self):
        global DATA, DATAJVforexport, DATAJVtabforexport
        
        # print(DATA.keys())
        
        DATAJVforexport=[]
        DATAJVtabforexport=[]
        
        rows=list(set(index.row() for index in self.ui.tableWidget.selectedIndexes()))
        sampleselected=[self.ui.tableWidget.item(row,1).text()+'_'+str(self.ui.tableWidget.item(row,2).text()).replace(' ','_').replace(':','-')+'_'+'%.2f'%float(self.ui.tableWidget.item(row,3).text()) for row in rows]
        # print(sampleselected)
        self.JVgraph.clear()
        for item in sampleselected:
            x = DATA[item]["IVData"][0]
            y = DATA[item]["IVData"][1]
            
            colx=["Voltage","mV",""]+x
            coly=["Current density","ma/cm2",DATA[item]["SampleName"]]+y
            DATAJVforexport.append(colx)
            DATAJVforexport.append(coly)
            DATAJVtabforexport.append([DATA[item]["SampleName"],str(DATA[item]["MeasDayTime2"]),'%.f' % float(DATA[item]["Voc"]),'%.2f' % float(DATA[item]["Jsc"]),'%.2f' % float(DATA[item]["FF"]),'%.2f' % float(DATA[item]["Eff"]),'%.2f' % float(DATA[item]["Roc"]),'%.2f' % float(DATA[item]["Rsc"]),'%.2f' % float(DATA[item]["Vstart"]),'%.2f' % float(DATA[item]["Vend"]),'%.2f' % float(DATA[item]["CellSurface"])])

            if self.ui.checkBox_JVLegend.isChecked():
                self.JVgraph.plot(x,y,label=DATA[item]["IVlinestyle"][0],linestyle=DATA[item]["IVlinestyle"][1],color=DATA[item]["IVlinestyle"][2],linewidth=DATA[item]["IVlinestyle"][3])
            else:
                self.JVgraph.plot(x,y,linestyle=DATA[item]["IVlinestyle"][1],color=DATA[item]["IVlinestyle"][2],linewidth=DATA[item]["IVlinestyle"][3])
        self.JVgraph.set_xlabel('Voltage (V)')#,**csfont)
        self.JVgraph.set_ylabel('Current density (mA/cm'+'\xb2'+')')#,**csfont)
        self.JVgraph.axhline(y=0, color='k')
        self.JVgraph.axvline(x=0, color='k')
        for item in ([self.JVgraph.title, self.JVgraph.xaxis.label, self.JVgraph.yaxis.label] +
                             self.JVgraph.get_xticklabels() + self.JVgraph.get_yticklabels()):
            item.set_fontsize(self.ui.spinBox_JVfontsize.value())
        
        DATAJVforexport=map(list, six.moves.zip_longest(*DATAJVforexport, fillvalue=' '))
        DATAJVtabforexport.insert(0,[" ","DateTime","Voc", "Jsc", "FF","Eff","Roc","Rsc","Vstart","Vend","Cellsurface"])
        
        if self.ui.checkBox_JVLegend.isChecked():
            if self.ui.radioButton_JVtopleft.isChecked():
                self.leg=self.JVgraph.legend(loc=2, fontsize = self.ui.spinBox_JVfontsize.value())
            elif self.ui.radioButton_JVtopright.isChecked():
                self.leg=self.JVgraph.legend(loc=1, fontsize = self.ui.spinBox_JVfontsize.value())
            elif self.ui.radioButton_JVbottomleft.isChecked():
                self.leg=self.JVgraph.legend(loc=3, fontsize = self.ui.spinBox_JVfontsize.value())
            elif self.ui.radioButton_JVbottomright.isChecked():
                self.leg=self.JVgraph.legend(loc=4, fontsize = self.ui.spinBox_JVfontsize.value())
            elif self.ui.radioButton_JVoutside.isChecked():
                self.leg=self.JVgraph.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1, fontsize = self.ui.spinBox_JVfontsize.value())
            elif self.ui.radioButton_JVBest.isChecked():
                self.leg=self.JVgraph.legend(loc=0, fontsize = self.ui.spinBox_JVfontsize.value())

        self.fig1.canvas.draw_idle()
        self.fig1.canvas.flush_events()

    def GraphJVsave_as(self):
        global DATA, DATAJVforexport, DATAJVtabforexport
        
        f = QFileDialog.getSaveFileName(self, 'Save graph and data', ".png", "graph file (*.png);; All Files (*)")[0]

        if self.ui.checkBox_MppLegend.isChecked():
            self.fig1.savefig(f, dpi=300, bbox_extra_artists=(self.leg,))#, transparent=True)
        else:
            self.fig1.savefig(f, dpi=300)#, transparent=True)
        
        DATAJVforexport1=[]
        for item in DATAJVforexport:
            line=""
            for item1 in item:
                line=line+str(item1)+"\t"
            line=line[:-1]+"\n"
            DATAJVforexport1.append(line)
            
        file = open(str(f[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
        file.writelines("%s" % item for item in DATAJVforexport1)
        file.close()   
        
        DATAJVforexport1=[]
        for item in DATAJVtabforexport:
            line=""
            for item1 in item:
                line=line+str(item1)+"\t"
            line=line[:-1]+"\n"
            DATAJVforexport1.append(line)
        file = open(str(f[:-4]+"_tab.txt"),'w', encoding='ISO-8859-1')
        file.writelines("%s" % item for item in DATAJVforexport1)
        file.close()
        
        
#%%#############
        
    def UpdateHistGraph(self):
        global DATA        
        global DATAHistforexport, groupstoplot
        
        DATAHistforexport=[]
        numbbins=int(self.ui.spinBox_HistoBins.value())
        DATAx=copy.deepcopy(DATA)
        
        samplesgroups = self.ui.listWidget_HistoGroups.selectedItems()
        samplesgroups=[item.text() for item in samplesgroups]
        # print(samplesgroups)
        groupnames=[]
        #sorting data
        if samplesgroups==[]:
            self.Histgraph.clear()
        else:
            grouplistdict=[]
            if self.ui.comboBox_HistoScanDirect.currentText()=="Allmeas":    #select all data points
                for item in range(len(samplesgroups)):
                    listdata=[]
                    for item1 in DATAx.keys():
                        if DATAx[item1]["Group"]==samplesgroups[item] and DATAx[item1]["Illumination"]=='Light':
                            listdata.append(DATAx[item1][self.ui.comboBox_HistoParam.currentText()])
                    groupnames.append(samplesgroups[item])
                    grouplistdict.append(listdata)
            elif self.ui.comboBox_HistoScanDirect.currentText()=="OnlyRev":
                for item in range(len(samplesgroups)):
                    listdata=[]
                    for item1 in DATAx.keys():
                        if DATAx[item1]["Group"]==samplesgroups[item] and DATAx[item1]["Illumination"]=='Light' and DATAx[item1]["ScanDirection"]=="Reverse":
                            listdata.append(DATAx[item1][self.ui.comboBox_HistoParam.currentText()])
                    groupnames.append(samplesgroups[item])        
                    grouplistdict.append(listdata)
                    
            elif self.ui.comboBox_HistoScanDirect.currentText()=="OnlyForw":
                for item in range(len(samplesgroups)):
                    listdata=[]
                    for item1 in DATAx.keys():
                        if DATAx[item1]["Group"]==samplesgroups[item] and DATAx[item1]["Illumination"]=='Light' and DATAx[item1]["ScanDirection"]=="Forward":
                            listdata.append(DATAx[item1][self.ui.comboBox_HistoParam.currentText()])
                    groupnames.append(samplesgroups[item])        
                    grouplistdict.append(listdata)
                    
            elif self.ui.comboBox_HistoScanDirect.currentText()=="Bestof/pix":  
                for item in range(len(samplesgroups)):
                    listofthegroup=[]
                    for item1 in DATAx.keys():
                        if DATAx[item1]["Group"]==samplesgroups[item] and DATAx[item1]["Illumination"]=='Light':
                            listofthegroup.append(DATAx[item1])
                    if len(listofthegroup)!=0:
                        
                        grouper = itemgetter("DepID", "Cellletter")
                        result = []
                        keylist=[]
                        for key, grp in groupby(sorted(listofthegroup, key = grouper), grouper):
                            result.append(list(grp))
                            keylist.append(key)
                        # print(result)
                        # print(keylist)
                        listdata=[]
                        for item1 in range(len(keylist)):
                            listdata1=[]
                            for item2 in range(len(result[item1])):
                                listdata1.append(result[item1][item2][self.ui.comboBox_HistoParam.currentText()])
                            listdata.append(max(listdata1))
                            
                        groupnames.append(samplesgroups[item])        
                        grouplistdict.append(listdata)
            elif self.ui.comboBox_HistoScanDirect.currentText()=="Bestof/subst":  
                for item in range(len(samplesgroups)):
                    listofthegroup=[]
                    for item1 in DATAx.keys():
                        if DATAx[item1]["Group"]==samplesgroups[item] and DATAx[item1]["Illumination"]=='Light':
                            listofthegroup.append(DATAx[item1])
                    if len(listofthegroup)!=0:
                        grouper = itemgetter("DepID")
                        result = []
                        keylist=[]
                        for key, grp in groupby(sorted(listofthegroup, key = grouper), grouper):
                            result.append(list(grp))
#                            print(len(result))
                            keylist.append(key)
                        
                        listdata=[]
                        for item1 in range(len(keylist)):
                            listdata1=[]
                            for item2 in range(len(result[item1])):
                                listdata1.append(result[item1][item2][self.ui.comboBox_HistoParam.currentText()])
                            listdata.append(max(listdata1))
                            
                        groupnames.append(samplesgroups[item])        
                        grouplistdict.append(listdata)


            self.Histgraph.clear()
            if self.ui.checkBox_Histxscale.isChecked():
                self.Histgraph.hist(grouplistdict,bins=numbbins,range=[self.ui.spinBox_HistxscaleMin.value(), self.ui.spinBox_HistxscaleMax.value()],histtype= self.ui.comboBox_HistoType.currentText(), density=False, cumulative=False, alpha=0.6, edgecolor='black', linewidth=1.2, label=groupnames)
            else:
                self.Histgraph.hist(grouplistdict,bins=numbbins,histtype= self.ui.comboBox_HistoType.currentText(), density=False, cumulative=False, alpha=0.6, edgecolor='black', linewidth=1.2, label=groupnames)
                
            self.Histgraph.set_xlabel(self.ui.comboBox_HistoParam.currentText())
            self.Histgraph.set_ylabel('counts')
            self.Histgraph.legend()
        
            DATAHistforexport=list(map(list, six.moves.zip_longest(*grouplistdict, fillvalue=' ')))
            DATAHistforexport=[groupnames]+DATAHistforexport

        
        self.fig6.canvas.draw_idle()
        self.fig6.canvas.flush_events()

    def GraphHistsave_as(self):
        global DATA, DATAHistforexport
        
        f = QFileDialog.getSaveFileName(self, 'Save graph and data', ".png", "graph file (*.png);; All Files (*)")[0]
        self.fig6.savefig(f, dpi=300)#, transparent=True)
                       
        DATAHistforexport1=[]            
        for item in DATAHistforexport:
            line=""
            for item1 in item:
                line=line+str(item1)+"\t"
            line=line[:-1]+"\n"
            DATAHistforexport1.append(line)
            
        file = open(str(f[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
        file.writelines("%s" % item for item in DATAHistforexport1)
        file.close()
        
#%%#############

    def UpdateBoxGraph(self):
        global DATA
        global groupstoplot
        global DATAgroupforexport
        
        DATAgroupforexport=[]
        fontsizegroup=self.ui.spinBox_BoxPlotFontsize.value()
        DATAx=copy.deepcopy(DATA)
        
        samplesgroups = self.ui.listWidget_BoxPlotGroup.selectedItems()
        samplesgroups=[item.text() for item in samplesgroups]
        # print(samplesgroups)
        
        if len(samplesgroups)>0:    #if user defined group names different than "Default group"        
            grouplistdict=[]
            if not self.ui.checkBox_BoxPlotRevForw.isChecked():    #select all data points
                if not self.ui.checkBox_BoxPlotAftermpp.isChecked():#all points without separation
                    for sample in samplesgroups:
#                        print(samplesgroups[item])
                        groupdict={}
                        groupdict["Group"]=sample
                        listofthegroup=[]
                        for item1 in DATAx.keys():
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light':
                                listofthegroup.append(DATAx[item1])
                        if len(listofthegroup)!=0:
                            listofthegroupRev=[]
                            listofthegroupFor=[]
                            for item1 in range(len(listofthegroup)):
#                                print(listofthegroup[item1]["ScanDirection"])
                                if listofthegroup[item1]["ScanDirection"]=="Reverse":
                                    listofthegroupRev.append(listofthegroup[item1])
                                else:
                                    listofthegroupFor.append(listofthegroup[item1])
                            
                            groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                            groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                            groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                            groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                            groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                            groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                            groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                            groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                            groupdict["RevRoc"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                            groupdict["ForRoc"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                            groupdict["RevRsc"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                            groupdict["ForRsc"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                            groupdict["RevVmpp"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                            groupdict["ForVmpp"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                            groupdict["RevJmpp"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                            groupdict["ForJmpp"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                            
                            grouplistdict.append(groupdict)
                
                else:#for separation before/after mpp
                    for sample in samplesgroups:
                        groupdict={}
                        groupdict["Group"]=sample
                        listofthegroup=[]
                        for item1 in DATAx.keys():
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light' and DATAx[item1]["aftermpp"]==0:
                                listofthegroup.append(DATAx[item1])
                        if len(listofthegroup)!=0:
                            listofthegroupRev=[]
                            listofthegroupFor=[]
                            for item1 in range(len(listofthegroup)):
                                if listofthegroup[item1]["ScanDirection"]=="Reverse":
                                    listofthegroupRev.append(listofthegroup[item1])
                                else:
                                    listofthegroupFor.append(listofthegroup[item1])
                            
                            groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                            groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                            groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                            groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                            groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                            groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                            groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                            groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                            groupdict["RevRoc"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                            groupdict["ForRoc"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                            groupdict["RevRsc"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                            groupdict["ForRsc"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                            groupdict["RevVmpp"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                            groupdict["ForVmpp"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                            groupdict["RevJmpp"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                            groupdict["ForJmpp"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                            
#                            grouplistdict.append(groupdict)
                        listofthegroup2=[]
                        for item1 in DATAx.keys():
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light' and DATAx[item1]["aftermpp"]==1:
                                listofthegroup2.append(DATAx[item1])
                        if len(listofthegroup2)!=0:
                            listofthegroupRev=[]
                            listofthegroupFor=[]
                            for item1 in range(len(listofthegroup2)):
                                if listofthegroup2[item1]["ScanDirection"]=="Reverse":
                                    listofthegroupRev.append(listofthegroup2[item1])
                                else:
                                    listofthegroupFor.append(listofthegroup2[item1])
                            
                            groupdict["RevVocAMPP"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                            groupdict["ForVocAMPP"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                            groupdict["RevJscAMPP"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                            groupdict["ForJscAMPP"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                            groupdict["RevFFAMPP"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                            groupdict["ForFFAMPP"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                            groupdict["RevEffAMPP"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                            groupdict["ForEffAMPP"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                            groupdict["RevRocAMPP"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                            groupdict["ForRocAMPP"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                            groupdict["RevRscAMPP"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                            groupdict["ForRscAMPP"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                            groupdict["RevVmppAMPP"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                            groupdict["ForVmppAMPP"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                            groupdict["RevJmppAMPP"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                            groupdict["ForJmppAMPP"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                        else:
                            groupdict["RevVocAMPP"]=[]
                            groupdict["ForVocAMPP"]=[]
                            groupdict["RevJscAMPP"]=[]
                            groupdict["ForJscAMPP"]=[]
                            groupdict["RevFFAMPP"]=[]
                            groupdict["ForFFAMPP"]=[]
                            groupdict["RevEffAMPP"]=[]
                            groupdict["ForEffAMPP"]=[]
                            groupdict["RevRocAMPP"]=[]
                            groupdict["ForRocAMPP"]=[]
                            groupdict["RevRscAMPP"]=[]
                            groupdict["ForRscAMPP"]=[]
                            groupdict["RevVmppAMPP"]=[]
                            groupdict["ForVmppAMPP"]=[]
                            groupdict["RevJmppAMPP"]=[]
                            groupdict["ForJmppAMPP"]=[]                            
                        grouplistdict.append(groupdict)
                    
                    
            elif self.ui.checkBox_BoxPlotRevForw.isChecked():      #select only the best RevFor of each cell
                if not self.ui.checkBox_BoxPlotAftermpp.isChecked():
                    for sample in samplesgroups:
                        groupdict={}
                        groupdict["Group"]=sample
                        listofthegroup=[]
                        for item1 in DATAx.keys():
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light':
                                listofthegroup.append(DATAx[item1])
                        if len(listofthegroup)!=0:
                            grouper = itemgetter("DepID", "Cellletter",'ScanDirection')
                            result = []
                            for key, grp in groupby(sorted(listofthegroup, key = grouper), grouper):
                                result.append(list(grp))
                            
                            result1=[]
                            
                            for item in result:
                                result1.append(sorted(item,key=itemgetter('Eff'),reverse=True)[0])
                            
                            grouper = itemgetter('ScanDirection')
                            result2 = []
                            for key, grp in groupby(sorted(result1, key = grouper), grouper):
                                result2.append(list(grp))
                            
                            listofthegroupRev=[]
                            listofthegroupFor=[]
                            
                            if result2[0][0]['ScanDirection']=='Forward':
                                listofthegroupFor=result2[0]
                                if len(result2)>1:
                                    listofthegroupRev=result2[1]
                            else:
                                listofthegroupRev=result2[0]
                                if len(result2)>1:
                                    listofthegroupFor=result2[1]
        
                            groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                            groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                            groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                            groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                            groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                            groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                            groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                            groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                            groupdict["RevRoc"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                            groupdict["ForRoc"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                            groupdict["RevRsc"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                            groupdict["ForRsc"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                            groupdict["RevVmpp"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                            groupdict["ForVmpp"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                            groupdict["RevJmpp"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                            groupdict["ForJmpp"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                            
                            grouplistdict.append(groupdict)
                else: #if aftermppchecked
#                    print("aftermpp is checked")
#                    print(samplesgroups)
                    for sample in samplesgroups:
                        groupdict={}
                        groupdict["Group"]=sample
                        listofthegroup=[]
                        for item1 in DATAx.keys():
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light' and DATAx[item1]["aftermpp"]==0:
                                listofthegroup.append(DATAx[item1])
                        if len(listofthegroup)!=0:
#                            print("listofthegroup1nonzero")
                            grouper = itemgetter("DepID", "Cellletter",'ScanDirection')
                            result = []
                            for key, grp in groupby(sorted(listofthegroup, key = grouper), grouper):
                                result.append(list(grp))
                            
                            result1=[]
                            
                            for item in result:
                                result1.append(sorted(item,key=itemgetter('Eff'),reverse=True)[0])
                            
                            grouper = itemgetter('ScanDirection')
                            result2 = []
                            for key, grp in groupby(sorted(result1, key = grouper), grouper):
                                result2.append(list(grp))
                            
                            listofthegroupRev=[]
                            listofthegroupFor=[]
                            
                            if result2[0][0]['ScanDirection']=='Forward':
                                listofthegroupFor=result2[0]
                                if len(result2)>1:
                                    listofthegroupRev=result2[1]
                            else:
                                listofthegroupRev=result2[0]
                                if len(result2)>1:
                                    listofthegroupFor=result2[1]
        
                            groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                            groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                            groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                            groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                            groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                            groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                            groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                            groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                            groupdict["RevRoc"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                            groupdict["ForRoc"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                            groupdict["RevRsc"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                            groupdict["ForRsc"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                            groupdict["RevVmpp"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                            groupdict["ForVmpp"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                            groupdict["RevJmpp"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                            groupdict["ForJmpp"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                            
#                            grouplistdict.append(groupdict)
                        listofthegroup2=[]
                        for item1 in DATAx.keys():
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light' and DATAx[item1]["aftermpp"]==1:
                                listofthegroup2.append(DATAx[item1])
                        if len(listofthegroup2)!=0:
#                            print("listofthegroup2nonzero")
                            grouper = itemgetter("DepID", "Cellletter",'ScanDirection')
                            result = []
                            for key, grp in groupby(sorted(listofthegroup2, key = grouper), grouper):
                                result.append(list(grp))
                            
                            result1=[]
                            
                            for item in result:
                                result1.append(sorted(item,key=itemgetter('Eff'),reverse=True)[0])
                            
                            grouper = itemgetter('ScanDirection')
                            result2 = []
                            for key, grp in groupby(sorted(result1, key = grouper), grouper):
                                result2.append(list(grp))
                            
                            listofthegroupRev=[]
                            listofthegroupFor=[]
                            
                            if result2[0][0]['ScanDirection']=='Forward':
                                listofthegroupFor=result2[0]
                                if len(result2)>1:
                                    listofthegroupRev=result2[1]
                            else:
                                listofthegroupRev=result2[0]
                                if len(result2)>1:
                                    listofthegroupFor=result2[1]
        
                            groupdict["RevVocAMPP"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                            groupdict["ForVocAMPP"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                            groupdict["RevJscAMPP"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                            groupdict["ForJscAMPP"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                            groupdict["RevFFAMPP"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                            groupdict["ForFFAMPP"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                            groupdict["RevEffAMPP"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                            groupdict["ForEffAMPP"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                            groupdict["RevRocAMPP"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                            groupdict["ForRocAMPP"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                            groupdict["RevRscAMPP"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                            groupdict["ForRscAMPP"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                            groupdict["RevVmppAMPP"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                            groupdict["ForVmppAMPP"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                            groupdict["RevJmppAMPP"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                            groupdict["ForJmppAMPP"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                        else:
                            groupdict["RevVocAMPP"]=[]
                            groupdict["ForVocAMPP"]=[]
                            groupdict["RevJscAMPP"]=[]
                            groupdict["ForJscAMPP"]=[]
                            groupdict["RevFFAMPP"]=[]
                            groupdict["ForFFAMPP"]=[]
                            groupdict["RevEffAMPP"]=[]
                            groupdict["ForEffAMPP"]=[]
                            groupdict["RevRocAMPP"]=[]
                            groupdict["ForRocAMPP"]=[]
                            groupdict["RevRscAMPP"]=[]
                            groupdict["ForRscAMPP"]=[]
                            groupdict["RevVmppAMPP"]=[]
                            groupdict["ForVmppAMPP"]=[]
                            groupdict["RevJmppAMPP"]=[]
                            groupdict["ForJmppAMPP"]=[]    
                        grouplistdict.append(groupdict)
                            
            self.Boxgraph.clear()
            names=samplesgroups
            #                print("aftermpp1")
            # if self.GroupChoice.get()=="Eff":
            groupchoice=self.ui.comboBox_BoxPlotParam.currentText()
            # print(groupchoice)

            if not self.ui.checkBox_BoxPlotAftermpp.isChecked():#aftermpp checkbox is not checked
                Effsubfig = self.Boxgraph 
                #names=samplesgroups
                valsRev=[]
                for item in names:
                    valsRev.append([i["Rev"+groupchoice] for i in grouplistdict if i["Group"]==item and "Rev"+groupchoice in i])
                valsFor=[]
                for item in names:
                    valsFor.append([i["For"+groupchoice] for i in grouplistdict if i["Group"]==item and "For"+groupchoice in i])
                valstot=[]
                
                for item in names:
                    d=[item,"Rev"+groupchoice]
                    for i in grouplistdict: 
                        if i["Group"]==item and "Rev"+groupchoice in i:
                            d+=i["Rev"+groupchoice]
                    if d!=[]:
                        DATAgroupforexport.append(d)
                    d=[item,"For"+groupchoice]
                    for i in grouplistdict: 
                        if i["Group"]==item and "For"+groupchoice in i:
                            d+=i["For"+groupchoice]
                    if d!=[]:
                        DATAgroupforexport.append(d)
                # print(DATAgroupforexport)
                DATAgroupforexport=list(map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' ')))
                # print(DATAgroupforexport)
                Rev=[]
                Forw=[]
                namelist=[]
#                        print(names)
                for i in range(len(names)):
                     if valsRev!=[]:
                         if valsRev[i]!=[]:
                             if valsRev[i][0]!=[]:
                                 Rev.append(valsRev[i][0])
                             else:
                                 Rev.append([])
                     if valsFor!=[]:
                         if valsFor[i]!=[]:
                             if valsFor[i][0]!=[]:
                                 Forw.append(valsFor[i][0])
                             else:
                                 Forw.append([])
                     if valsRev!=[] or valsFor!=[]: 
                         if valsRev[i]!=[] or valsFor[i]!=[]: 
                             if valsRev[i][0]!=[] or valsFor[i][0]!=[]:
                                 valstot.append(valsRev[i][0]+valsFor[i][0])
                                 namelist.append(names[i])
#                        print(namelist)  
                
                if self.ui.checkBox_BoxPlotBoxPlot.isChecked():
                    # print('box')
                    Effsubfig.boxplot(valstot,0,'',labels=namelist)
                # print(valstot)
                # print(Rev)
                # print(Forw)
                for i in range(len(namelist)):
                    y=Rev[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        Effsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                    y=Forw[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        Effsubfig.scatter(x,y,s=15,color='blue', alpha=0.5) 
                    
            else:
#                        print("aftermpp")
                Effsubfig = self.Boxgraph 
                #names=samplesgroups
                valsRev=[]
                for item in names:
                    valsRev.append([i["Rev"+groupchoice] for i in grouplistdict if i["Group"]==item and "Rev"+groupchoice in i])
                valsFor=[]
                for item in names:
                    valsFor.append([i["For"+groupchoice] for i in grouplistdict if i["Group"]==item and "For"+groupchoice in i])
                valsRevAMPP=[]
                for item in names:
#                            v=[i["RevEffAMPP"] for i in grouplistdict if i["Group"]==item and "RevEffAMPP" in i]
                    valsRevAMPP.append([i["Rev"+groupchoice+"AMPP"] for i in grouplistdict if i["Group"]==item and "Rev"+groupchoice+"AMPP" in i])
#                        print(len(valsRevAMPP))
                valsForAMPP=[]
                for item in names:
                    valsForAMPP.append([i["For"+groupchoice+"AMPP"] for i in grouplistdict if i["Group"]==item and "For"+groupchoice+"AMPP" in i])
#                        print(len(valsForAMPP))
                
                
                
                for item in names:
                    try:
                        DATAgroupforexport.append([item,"Rev"+groupchoice]+[i["Rev"+groupchoice] for i in grouplistdict if i["Group"]==item and "Rev"+groupchoice in i][0])
                    except IndexError:
#                                print("indexError1")
                        DATAgroupforexport.append([item,"Rev"+groupchoice]+[])
                    try:
                        DATAgroupforexport.append([item,"For"+groupchoice]+[i["For"+groupchoice] for i in grouplistdict if i["Group"]==item and "For"+groupchoice in i][0])
                    except IndexError:
#                                print("indexError1")
                        DATAgroupforexport.append([item,"For"+groupchoice]+[])
                    try:
                        DATAgroupforexport.append([item,"Rev"+groupchoice+"AMPP"]+[i["Rev"+groupchoice+"AMPP"] for i in grouplistdict if i["Group"]==item and "Rev"+groupchoice+"AMPP" in i][0])
                    except IndexError:
#                                print("indexError1")
                        DATAgroupforexport.append([item,"Rev"+groupchoice+"AMPP"]+[])
                    try:
                        DATAgroupforexport.append([item,"For"+groupchoice+"AMPP"]+[i["For"+groupchoice+"AMPP"] for i in grouplistdict if i["Group"]==item and "For"+groupchoice+"AMPP" in i][0])
                    except IndexError:
#                                print("indexError2")
                        DATAgroupforexport.append([item,"For"+groupchoice+"AMPP"]+[])
                # print(DATAgroupforexport)
                DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                
                valstot=[]
                Rev=[]
                Forw=[]
                RevAMPP=[]
                ForwAMPP=[]
                namelist=[]
                for i in range(len(names)):
                    if valsRev[i]!=[]:
                        if valsRev[i][0]!=[]:
                             Rev.append(valsRev[i][0])
                        else:
                             Rev.append([])
                    else:
                        Rev.append([])
                    if valsFor[i]!=[]:
                        if valsFor[i][0]!=[]:
                             Forw.append(valsFor[i][0])
                        else:
                             Forw.append([])
                    else:
                        Forw.append([])
                    if valsRevAMPP[i]!=[]:
                        if valsRevAMPP[i][0]!=[]:
                             RevAMPP.append(valsRevAMPP[i][0])
                        else:
                             RevAMPP.append([])
                    else:
                        RevAMPP.append([])
                    if valsForAMPP[i]!=[]:    
                        if valsForAMPP[i][0]!=[]:
                             ForwAMPP.append(valsForAMPP[i][0])
                        else:
                             ForwAMPP.append([])  
                    else:
                        ForwAMPP.append([])
                    try:    
                        if valsRev[i][0]!=[] or valsFor[i][0]!=[] or valsRevAMPP[i][0]!=[] or valsForAMPP[i][0]!=[]:
                             valstot.append(valsRev[i][0]+valsFor[i][0]+valsRevAMPP[i][0]+valsForAMPP[i][0])
                             namelist.append(names[i])
                    except IndexError:
                        toaddtovalstot=[]
                        try:
                            toaddtovalstot+=valsRev[i][0]
                        except:
                            pass
                        try:
                            toaddtovalstot+=valsFor[i][0]
                        except:
                            pass
                        try:
                            toaddtovalstot+=valsRevAMPP[i][0]
                        except:
                            pass
                        try:
                            toaddtovalstot+=valsForAMPP[i][0]
                        except:
                            pass
                            
                if namelist!=[]:            
                    if self.ui.checkBox_BoxPlotBoxPlot.isChecked():
                        Effsubfig.boxplot(valstot,0,'',labels=namelist)
                
                    for i in range(len(namelist)):
#                            if len(listofthegroup)!=0:
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+0.9,0.04,size=len(y))
                            Effsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                        y=Forw[i]
                        if len(y)>0:
                            x=np.random.normal(i+0.9,0.04,size=len(y))
                            Effsubfig.scatter(x,y,s=15,color='blue', alpha=0.5) 
#                            if len(listofthegroup2)!=0:   
                            y=RevAMPP[i]
                        if len(y)>0:
                            x=np.random.normal(i+1.1,0.04,size=len(y))
                            Effsubfig.scatter(x,y,s=15,color='orange', alpha=0.5)
                        y=ForwAMPP[i]
                        if len(y)>0:
                            x=np.random.normal(i+1.1,0.04,size=len(y))
                            Effsubfig.scatter(x,y,s=15,color='lightblue', alpha=0.5) 
                        
            if not self.ui.checkBox_BoxPlotBoxPlot.isChecked():
                if namelist!=[]:
                    span=range(1,len(namelist)+1)
#                            print(namelist)
#                            print(span)
#                        plt.xticks(span,namelist)
                    Effsubfig.set_xticks(span)
                    Effsubfig.set_xticklabels(namelist)
                    Effsubfig.set_xlim([0.5,span[-1]+0.5])
            
            # if self.minmaxgroupgraphcheck.get()==1:
            #     Effsubfig.set_ylim([self.minYgroupgraph.get(),self.maxYgroupgraph.get()])
                
            Effsubfig.set_ylabel(groupchoice)
            for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                         Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                item.set_fontsize(fontsizegroup)
            
            for tick in Effsubfig.get_xticklabels():
                tick.set_rotation(self.ui.spinBox_BoxPlotRotation.value())
        
        self.fig3.canvas.draw_idle()
        
    def GraphBoxsave_as(self):
        global DATA
        global DATAgroupforexport
        
        try:
            if not self.ui.checkBox_BoxPlotBig4.isChecked():
                f = QFileDialog.getSaveFileName(self, 'Save graph and data', ".png", "graph file (*.png);; All Files (*)")[0]
                if self.ui.checkBox_BoxPlotBkg.isChecked():
                    self.fig3.savefig(f, dpi=300, transparent=True)
                else:
                    self.fig3.savefig(f,dpi=300, transparent=False)
                print(DATAgroupforexport)
                DATAgroupforexport1=[]            
                for item in DATAgroupforexport:
                    line=""
                    for item1 in item:
                        line=line+str(item1)+"\t"
                    line=line[:-1]+"\n"
                    DATAgroupforexport1.append(line)
                
                file = open(str(f[:-4]+"_"+self.ui.comboBox_BoxPlotParam.currentText()+"dat.txt"),'w', encoding='ISO-8859-1')
                file.writelines("%s" % item for item in DATAgroupforexport1)
                file.close()
            elif self.ui.checkBox_BoxPlotBig4.isChecked():
                
                f = QFileDialog.getSaveFileName(self, 'Save graph and data', ".png", "graph file (*.png);; All Files (*)")[0]
                
                for param in ["Eff","Voc","Jsc","FF"]:
                    self.ui.comboBox_BoxPlotParam.setCurrentIndex(self.ui.comboBox_BoxPlotParam.findText(param, QtCore.Qt.MatchFixedString))
                    self.UpdateBoxGraph()
                    if self.ui.checkBox_BoxPlotBkg.isChecked():
                        self.fig3.savefig(f[:-4]+"_"+self.ui.comboBox_BoxPlotParam.currentText()+f[-4:], dpi=300, transparent=True)
                    else:
                        self.fig3.savefig(f[:-4]+"_"+self.ui.comboBox_BoxPlotParam.currentText()+f[-4:],dpi=300, transparent=False)
                        
                    DATAgroupforexport1=[]            
                    for item in DATAgroupforexport:
                        line=""
                        for item1 in item:
                            line=line+str(item1)+"\t"
                        line=line[:-1]+"\n"
                        DATAgroupforexport1.append(line)
                    
                    file = open(str(f[:-4]+"_"+self.ui.comboBox_BoxPlotParam.currentText()+"dat.txt"),'w', encoding='ISO-8859-1')
                    file.writelines("%s" % item for item in DATAgroupforexport1)
                    file.close()
        except:
            print("there is an exception with save groupboxgraph")  

#%%#############
    def plottingTimefromTable(self):
        global takenforplotTime
        rows=list(set(index.row() for index in self.ui.tableWidget.selectedIndexes()))
        takenforplotTime=[self.ui.tableWidget.item(row,1).text()+'_'+str(self.ui.tableWidget.item(row,2).text()).replace(' ','_').replace(':','-')+'_'+'%.2f'%float(self.ui.tableWidget.item(row,3).text()) for row in rows]
        self.UpdateTimeGraph()

    def UpdateTimeGraph(self):
        global DATA, takenforplotTime, colorstylelist, DATAtimeevolforexport
#        print("")
#        print(takenforplotTime)
        #"MeasDayTime2"
        DATAtimeevolforexport={}
        
        if takenforplotTime!=[]:
            if self.ui.checkBox_BestEffPixDay.isChecked()==False and self.ui.checkBox_bestofRevFor.isChecked()==False:
                TimeDatDict={}
                self.TimeEvolraph.clear()
                for item in takenforplotTime:
                    newkey=item.split('_')[0]+'_'+item.split('_')[1]+'_'+item.split('_')[2]
                    if newkey not in TimeDatDict.keys():
                        TimeDatDict[newkey]={'reverse':{'Voc':[[],[]],'Jsc':[[],[]],'FF':[[],[]],'Eff':[[],[]]},'forward':{'Voc':[[],[]],'Jsc':[[],[]],'FF':[[],[]],'Eff':[[],[]]}}
                    for item11 in DATA.keys():
                        item1=DATA[item11]
                        if item1["SampleNameID"]==item:
                            if item1["ScanDirection"]=="Reverse" and item1["Illumination"]=="Light":
                                TimeDatDict[newkey]['reverse']['Voc'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['reverse']['Voc'][1].append(item1["Voc"])
                                TimeDatDict[newkey]['reverse']['Jsc'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['reverse']['Jsc'][1].append(item1["Jsc"])
                                TimeDatDict[newkey]['reverse']['FF'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['reverse']['FF'][1].append(item1["FF"])
                                TimeDatDict[newkey]['reverse']['Eff'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['reverse']['Eff'][1].append(item1["Eff"])
                            elif item1["ScanDirection"]=="Forward" and item1["Illumination"]=="Light":
                                TimeDatDict[newkey]['forward']['Voc'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['forward']['Voc'][1].append(item1["Voc"])
                                TimeDatDict[newkey]['forward']['Jsc'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['forward']['Jsc'][1].append(item1["Jsc"])
                                TimeDatDict[newkey]['forward']['FF'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['forward']['FF'][1].append(item1["FF"])
                                TimeDatDict[newkey]['forward']['Eff'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['forward']['Eff'][1].append(item1["Eff"])
        #        num_plots = len(TimeDatDict.keys())          
        #        plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.Spectral(np.linspace(0, 1, num_plots))))
                   
        #        print(list(TimeDatDict.keys())) 
                # minx=min(TimeDatDict[newkey]['forward'][self.TimeChoice.get()][0]+TimeDatDict[newkey]['reverse'][self.TimeChoice.get()][0])
                # maxx=max(TimeDatDict[newkey]['forward'][self.TimeChoice.get()][0]+TimeDatDict[newkey]['reverse'][self.TimeChoice.get()][0])
                # print(TimeDatDict)
                for key in list(TimeDatDict.keys()):
                    partdatatime=[[],[],[],[],[],[],[],[]]
                    # if minx>min(TimeDatDict[key]['forward'][self.TimeChoice.get()][0]+TimeDatDict[key]['reverse'][self.TimeChoice.get()][0]):
                    #     minx=min(TimeDatDict[key]['forward'][self.TimeChoice.get()][0]+TimeDatDict[key]['reverse'][self.TimeChoice.get()][0])
                    # if maxx<max(TimeDatDict[key]['forward'][self.TimeChoice.get()][0]+TimeDatDict[key]['reverse'][self.TimeChoice.get()][0]):
                    #     maxx=max(TimeDatDict[key]['forward'][self.TimeChoice.get()][0]+TimeDatDict[key]['reverse'][self.TimeChoice.get()][0])
                    try:
                        xfor, yfor=zip(*sorted(zip(TimeDatDict[key]['forward'][self.ui.comboBox_PVPTimeParam.currentText()][0],TimeDatDict[key]['forward'][self.ui.comboBox_PVPTimeParam.currentText()][1]), key = lambda x: x[1]))
                        xfor=list(xfor)
                        yfor=list(yfor)
                        yfor.sort(key=dict(zip(yfor, xfor)).get)
                        xfor=sorted(xfor)
                        partdatatime[0]=xfor
                        partdatatime[1]=[(m-xfor[0]).total_seconds()/3600 for m in xfor]
                        partdatatime[2]=yfor
                        if self.ui.spinBox_PVPTimeNormalPoint.value()==-1:
                            partdatatime[3]=[(m)/(yfor[0]) for m in yfor]
                        else:
                            foundnormalsetpt=0
                            for item in range(len(partdatatime[1])):
                                if partdatatime[1][item]>=self.ui.spinBox_PVPTimeNormalPoint.value():
                                    partdatatime[3]=[(m)/(partdatatime[2][item]) for m in yfor]
                                    foundnormalsetpt=1
                                    break
                            if foundnormalsetpt==0:
                                partdatatime[3]=[(m)/(yfor[0]) for m in yfor]
                    except ValueError:
                        pass
                    try:
                        xrev, yrev=zip(*sorted(zip(TimeDatDict[key]['reverse'][self.ui.comboBox_PVPTimeParam.currentText()][0],TimeDatDict[key]['reverse'][self.ui.comboBox_PVPTimeParam.currentText()][1]), key = lambda x: x[1]))                
                        xrev=list(xrev)
                        yrev=list(yrev)
                        yrev.sort(key=dict(zip(yrev, xrev)).get)
                        xrev=sorted(xrev)
                        partdatatime[4]=xrev
                        partdatatime[5]=[(m-xrev[0]).total_seconds()/3600 for m in xrev]
                        partdatatime[6]=yrev
                        
                        if self.ui.spinBox_PVPTimeNormalPoint.value()==-1:
                            partdatatime[7]=[(m)/(yrev[0]) for m in yrev]
                        else:
                            foundnormalsetpt=0
                            for item in range(len(partdatatime[5])):
                                if partdatatime[5][item]>=self.ui.spinBox_PVPTimeNormalPoint.value():
                                    partdatatime[7]=[(m)/(partdatatime[6][item]) for m in yrev]
                                    foundnormalsetpt=1
                                    break
                            if foundnormalsetpt==0:
                                partdatatime[7]=[(m)/(yrev[0]) for m in yrev]
                        
                    except ValueError:
                        pass
                    DATAtimeevolforexport[key]=partdatatime
                 
                color1=0 
                for key in list(DATAtimeevolforexport.keys()):
                    xfor=DATAtimeevolforexport[key][0]
                    yfor=DATAtimeevolforexport[key][2]
                    xrev=DATAtimeevolforexport[key][4]
                    yrev=DATAtimeevolforexport[key][6]
                    if self.ui.checkBox_PVPTimeRelativeTime.isChecked():
                        xfor=DATAtimeevolforexport[key][1]
                        xrev=DATAtimeevolforexport[key][5]
                    if self.ui.checkBox_PVPTimeNormal.isChecked():
                        yfor=DATAtimeevolforexport[key][3]
                        yrev=DATAtimeevolforexport[key][7]
                
                    if self.ui.checkBox_PVPTimeLine.isChecked():
                        self.TimeEvolraph.plot(xfor, yfor, linestyle='--', marker='o',color=colorstylelist[color1],label=key+'_For')
                        self.TimeEvolraph.plot(xrev, yrev, linestyle='-', marker='o', color=colorstylelist[color1], alpha=0.5,label=key+'_Rev')
                    else:
                        self.TimeEvolraph.plot(xfor, yfor, linestyle='', marker='o',color=colorstylelist[color1],label=key+'_For')
                        self.TimeEvolraph.plot(xrev, yrev, linestyle='', marker='o', color=colorstylelist[color1], alpha=0.5,label=key+'_Rev')  
                    color1=color1+1
                    
                
                if self.ui.checkBox_PVPTimeRelativeTime.isChecked():
                    self.TimeEvolraph.set_xlabel('Time (hours)')
                else:
                    # self.TimeEvolfig.set_xlim(minx-0.05*(maxx-minx),maxx+0.05*(maxx-minx))    
                    self.TimeEvolraph.set_xlabel('Time')
                
                # if self.minmaxtimegraphcheck.get():
                #     self.TimeEvolfig.set_ylim(self.minYtimegraph.get(),self.maxYtimegraph.get())
                
                self.TimeEvolraph.set_ylabel(self.ui.comboBox_PVPTimeParam.currentText())
                for tick in self.TimeEvolraph.get_xticklabels():
                    tick.set_rotation(20)
                self.TimeEvolraphleg=self.TimeEvolraph.legend(loc='lower left', bbox_to_anchor=(1, 0))
                self.fig4.canvas.draw_idle()
                
            elif self.ui.checkBox_bestofRevFor.isChecked() and not self.ui.checkBox_BestEffPixDay.isChecked():
                print("bestrevfor")
                
                
            elif not self.ui.checkBox_bestofRevFor.isChecked() and self.ui.checkBox_BestEffPixDay.isChecked():   
#                print("bestoftheday")
                TimeDatDict={}
                self.TimeEvolraph.clear()
                for item in takenforplotTime:
                    newkey=item.split('_')[0]+'_'+item.split('_')[1]#per substrate e.g. 41_10
                    if newkey not in TimeDatDict.keys():
                        TimeDatDict[newkey]={}
                    for item11 in DATA.keys():
                        item1=DATA[item11]
                        if item1["SampleNameID"]==item:
                            newdatekey=str(item1["MeasDayTime2"].date())
                            if newdatekey not in TimeDatDict[newkey].keys():
                                TimeDatDict[newkey][newdatekey]={'Voc':[[],[]],'Jsc':[[],[]],'FF':[[],[]],'Eff':[[],[]]}
                            
                            TimeDatDict[newkey][newdatekey]['Voc'][0].append(item1["MeasDayTime2"])
                            TimeDatDict[newkey][newdatekey]['Voc'][1].append(item1["Voc"])
                            TimeDatDict[newkey][newdatekey]['Jsc'][0].append(item1["MeasDayTime2"])
                            TimeDatDict[newkey][newdatekey]['Jsc'][1].append(item1["Jsc"])
                            TimeDatDict[newkey][newdatekey]['FF'][0].append(item1["MeasDayTime2"])
                            TimeDatDict[newkey][newdatekey]['FF'][1].append(item1["FF"])
                            TimeDatDict[newkey][newdatekey]['Eff'][0].append(item1["MeasDayTime2"])
                            TimeDatDict[newkey][newdatekey]['Eff'][1].append(item1["Eff"])
                
                for key0 in list(TimeDatDict.keys()):
#                    print(key0)
                    TimeDatDict[key0]['bestEffofday']={'Voc':[[],[]],'Jsc':[[],[]],'FF':[[],[]],'Eff':[[],[]]}
                    for key in list(TimeDatDict[key0].keys()):
#                        print(key)
#                        print(max(TimeDatDict[key0][key]['Eff'][1]))
                        
                        ind=TimeDatDict[key0][key]['Eff'][1].index(max(TimeDatDict[key0][key]['Eff'][1]))
                        
                        TimeDatDict[key0]['bestEffofday']['Voc'][0].append(TimeDatDict[key0][key]['Voc'][0][ind])
                        TimeDatDict[key0]['bestEffofday']['Voc'][1].append(TimeDatDict[key0][key]['Voc'][1][ind])
                        TimeDatDict[key0]['bestEffofday']['Jsc'][0].append(TimeDatDict[key0][key]['Jsc'][0][ind])
                        TimeDatDict[key0]['bestEffofday']['Jsc'][1].append(TimeDatDict[key0][key]['Jsc'][1][ind])
                        TimeDatDict[key0]['bestEffofday']['FF'][0].append(TimeDatDict[key0][key]['FF'][0][ind])
                        TimeDatDict[key0]['bestEffofday']['FF'][1].append(TimeDatDict[key0][key]['FF'][1][ind])
                        TimeDatDict[key0]['bestEffofday']['Eff'][0].append(TimeDatDict[key0][key]['Eff'][0][ind])
                        TimeDatDict[key0]['bestEffofday']['Eff'][1].append(TimeDatDict[key0][key]['Eff'][1][ind])
                
                # minx=min(TimeDatDict[newkey]['bestEffofday'][self.ui.comboBox_PVPTimeParam.currentText()][0])
                # maxx=max(TimeDatDict[newkey]['bestEffofday'][self.ui.comboBox_PVPTimeParam.currentText()][0])
                
                for key in list(TimeDatDict.keys()):
                    partdatatime=[[],[],[],[]]
                    # if minx>min(TimeDatDict[key]['bestEffofday'][self.ui.comboBox_PVPTimeParam.currentText()][0]):
                    #     minx=min(TimeDatDict[key]['bestEffofday'][self.ui.comboBox_PVPTimeParam.currentText()][0])
                    # if maxx<max(TimeDatDict[key]['bestEffofday'][self.ui.comboBox_PVPTimeParam.currentText()][0]):
                    #     maxx=max(TimeDatDict[key]['bestEffofday'][self.ui.comboBox_PVPTimeParam.currentText()][0])
                    try:
                        xfor, yfor=zip(*sorted(zip(TimeDatDict[key]['bestEffofday'][self.ui.comboBox_PVPTimeParam.currentText()][0],TimeDatDict[key]['bestEffofday'][self.ui.comboBox_PVPTimeParam.currentText()][1]), key = lambda x: x[1]))
                        xfor=list(xfor)
                        yfor=list(yfor)
                        yfor.sort(key=dict(zip(yfor, xfor)).get)
                        xfor=sorted(xfor)
                        partdatatime[0]=xfor
                        partdatatime[1]=[(m-xfor[0]).total_seconds()/3600 for m in xfor]
                        partdatatime[2]=yfor
                        if self.ui.spinBox_PVPTimeNormalPoint.value()==-1:
                            partdatatime[3]=[(m)/(yfor[0]) for m in yfor]
                        else:
                            foundnormalsetpt=0
                            for item in range(len(partdatatime[1])):
                                if partdatatime[1][item]>=self.ui.spinBox_PVPTimeNormalPoint.value():
                                    partdatatime[3]=[(m)/(partdatatime[2][item]) for m in yfor]
                                    foundnormalsetpt=1
                                    break
                            if foundnormalsetpt==0:
                                partdatatime[3]=[(m)/(yfor[0]) for m in yfor]
                    except ValueError:
                        pass
                    
                    DATAtimeevolforexport[key]=partdatatime
                 
                color1=0 
                for key in list(DATAtimeevolforexport.keys()):
                    xfor=DATAtimeevolforexport[key][0]
                    yfor=DATAtimeevolforexport[key][2]
                    
                    if self.ui.checkBox_PVPTimeRelativeTime.isChecked():
                        xfor=DATAtimeevolforexport[key][1]
                    if self.ui.checkBox_PVPTimeNormal.isChecked():
                        yfor=DATAtimeevolforexport[key][3]
                
                    if self.ui.checkBox_PVPTimeLine.isChecked():
                        self.TimeEvolraph.plot(xfor, yfor, linestyle='-', marker='o',color=colorstylelist[color1],label=key+'_Best')
                    else:
                        self.TimeEvolraph.plot(xfor, yfor, linestyle='', marker='o',color=colorstylelist[color1],label=key+'_Best')
                    color1=color1+1
                    
                
                if self.ui.checkBox_PVPTimeRelativeTime.isChecked():
                    self.TimeEvolraph.set_xlabel('Time (hours)')
                else:
                    # self.TimeEvolraph.set_xlim(minx-0.05*(maxx-minx),maxx+0.05*(maxx-minx))    
                    self.TimeEvolraph.set_xlabel('Time')
                
                # if self.minmaxtimegraphcheck.get():
                #     self.TimeEvolraph.set_ylim(self.minYtimegraph.get(),self.maxYtimegraph.get())
                
                self.TimeEvolraph.set_ylabel(self.ui.comboBox_PVPTimeParam.currentText())
                for tick in self.TimeEvolraph.get_xticklabels():
                    tick.set_rotation(20)
                self.TimeEvolraphleg=self.TimeEvolraph.legend(loc='lower left', bbox_to_anchor=(1, 0))
                
                self.fig4.canvas.draw_idle()
        
    def GraphTimesave_as(self):
        global DATAtimeevolforexport
        if not self.ui.checkBox_PVPTimeBig4.isChecked():
            f = QFileDialog.getSaveFileName(self, 'Save graph and data', ".png", "graph file (*.png);; All Files (*)")[0]
            
            self.fig4.savefig(f, dpi=300, transparent=False)
            
                            
            for key in list(DATAtimeevolforexport.keys()):
                DATAgroupforexport1=["realtimeF\trelativetimeF\tvalueF\tnormalizedvaluetot0F\trealtimeR\trelativetimeR\tvalueR\tnormalizedvaluetot0R\n"] 
                templist=map(list, six.moves.zip_longest(*DATAtimeevolforexport[key], fillvalue=' '))
                for item in templist:
                    line=""
                    for item1 in item:
                        line=line+str(item1)+"\t"
                    line=line[:-1]+"\n"
                    DATAgroupforexport1.append(line)
                file = open(str(f[:-4]+"_"+self.ui.comboBox_PVPTimeParam.currentText()+'_'+str(key)+"_dat.txt"),'w', encoding='ISO-8859-1')
                file.writelines("%s" % item for item in DATAgroupforexport1)
                file.close()
            
        elif self.ui.checkBox_PVPTimeBig4.isChecked():
            
            f = QFileDialog.getSaveFileName(self, 'Save graph and data', ".png", "graph file (*.png);; All Files (*)")[0]                
            for param in ["Eff","Voc","Jsc","FF"]:
                self.ui.comboBox_PVPTimeParam.setCurrentIndex(self.ui.comboBox_PVPTimeParam.findText(param, QtCore.Qt.MatchFixedString))
                self.UpdateTimeGraph()
                self.fig4.savefig(f[:-4]+"_"+self.ui.comboBox_PVPTimeParam.currentText()+f[-4:], dpi=300, transparent=False)
                
                for key in list(DATAtimeevolforexport.keys()):
                    DATAgroupforexport1=["realtimeF\trelativetimeF\tvalueF\tnormalizedvaluetot0F\trealtimeR\trelativetimeR\tvalueR\tnormalizedvaluetot0R\n"] 
                    templist=map(list, six.moves.zip_longest(*DATAtimeevolforexport[key], fillvalue=' '))
                    for item in templist:
                        line=""
                        for item1 in item:
                            line=line+str(item1)+"\t"
                        line=line[:-1]+"\n"
                        DATAgroupforexport1.append(line)
                    file = open(str(f[:-4]+"_"+self.ui.comboBox_PVPTimeParam.currentText()+'_'+str(key)+"_dat.txt"),'w', encoding='ISO-8859-1')
                    file.writelines("%s" % item for item in DATAgroupforexport1)
                    file.close()

#%%#############
    def UpdateCompGraph(self):
        global DATA
        global groupstoplot
        global DATAcompforexport
        
        DATAcompforexport=[]
        DATAx=copy.deepcopy(DATA)
        
        samplesgroups = self.ui.listWidget_ParamComp.selectedItems()
        samplesgroups=[item.text() for item in samplesgroups]
        
#        print(samplesgroups)
        
        if samplesgroups==[]:
            self.ParamParamgraph.clear()
        else:
            grouplistdict={}
            for item in range(len(samplesgroups)):
                groupdict={}
                groupdict["Group"]=samplesgroups[item]
                listofthegroup=[]
                for item1 in DATAx.keys():
                    if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light':
                        listofthegroup.append(DATAx[item1])
               
                if len(listofthegroup)!=0:
                    listofthegroupRev=[]
                    listofthegroupFor=[]
                    for item1 in range(len(listofthegroup)):
                        if listofthegroup[item1]["ScanDirection"]=="Reverse":
                            listofthegroupRev.append(listofthegroup[item1])
                        else:
                            listofthegroupFor.append(listofthegroup[item1])
                    
                    groupdict["Voc"]={}
                    groupdict["Jsc"]={}
                    groupdict["FF"]={}
                    groupdict["Eff"]={}
                    groupdict["Roc"]={}
                    groupdict["Rsc"]={}
                    groupdict["Vmpp"]={}
                    groupdict["Jmpp"]={}
                    
                    
                    groupdict["Voc"]["Rev"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                    groupdict["Voc"]["For"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                    groupdict["Jsc"]["Rev"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                    groupdict["Jsc"]["For"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                    groupdict["FF"]["Rev"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                    groupdict["FF"]["For"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                    groupdict["Eff"]["Rev"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                    groupdict["Eff"]["For"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                    groupdict["Roc"]["Rev"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                    groupdict["Roc"]["For"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                    groupdict["Rsc"]["Rev"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                    groupdict["Rsc"]["For"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                    groupdict["Vmpp"]["Rev"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                    groupdict["Vmpp"]["For"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                    groupdict["Jmpp"]["Rev"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                    groupdict["Jmpp"]["For"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                    
#                    grouplistdict.append(groupdict)
                    grouplistdict[samplesgroups[item]]=groupdict
            colormapname="jet"
            cmap = plt.get_cmap(colormapname)
            colors = cmap(np.linspace(0, 1.0, len(list(grouplistdict.keys()))))
            colors=[tuple(item) for item in colors]  
             
            self.ParamParamgraph.clear()
            indexcolor=0
            for group in list(grouplistdict.keys()):
                DATAcompforexport.append([self.ui.comboBox_PVPx.currentText(),'']+grouplistdict[group][self.ui.comboBox_PVPx.currentText()]['Rev'])
                DATAcompforexport.append([self.ui.comboBox_PVPy.currentText(),group+'_Rev']+grouplistdict[group][self.ui.comboBox_PVPy.currentText()]['Rev'])
                self.ParamParamgraph.scatter(grouplistdict[group][self.ui.comboBox_PVPx.currentText()]['Rev'],grouplistdict[group][self.ui.comboBox_PVPy.currentText()]['Rev']
                                            ,label=group+'_Rev',color=colors[indexcolor],marker="o")
                DATAcompforexport.append([self.ui.comboBox_PVPx.currentText(),'']+grouplistdict[group][self.ui.comboBox_PVPx.currentText()]['For'])
                DATAcompforexport.append([self.ui.comboBox_PVPy.currentText(),group+'For']+grouplistdict[group][self.ui.comboBox_PVPy.currentText()]['For'])
                self.ParamParamgraph.scatter(grouplistdict[group][self.ui.comboBox_PVPx.currentText()]['For'],grouplistdict[group][self.ui.comboBox_PVPy.currentText()]['For']
                                            ,label=group+'_For',color=colors[indexcolor],marker="s")
                indexcolor+=1
            
            DATAcompforexport=map(list, six.moves.zip_longest(*DATAcompforexport, fillvalue=' '))
            
            self.ParamParamgraph.set_ylabel(self.ui.comboBox_PVPy.currentText())    
            self.ParamParamgraph.set_xlabel(self.ui.comboBox_PVPx.currentText()) 
#            self.CompParamGroupfig.legend()
            self.leg=self.ParamParamgraph.legend(loc='lower left', bbox_to_anchor=(1, 0))
            
        self.fig5.canvas.draw_idle()
    
    def GraphCompsave_as(self):
        global DATAcompforexport
        
        try:
            f = QFileDialog.getSaveFileName(self, 'Save graph and data', ".png", "graph file (*.png);; All Files (*)")[0]
            self.fig5.savefig(f, dpi=300, bbox_extra_artists=(self.leg,))#, transparent=True)
                           
            DATAcompforexport1=[]            
            for item in DATAcompforexport:
                line=""
                for item1 in item:
                    line=line+str(item1)+"\t"
                line=line[:-1]+"\n"
                DATAcompforexport1.append(line)
                
            file = open(str(f[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in DATAcompforexport1)
            file.close()
        
        except:
            print("there is an exception") 

#%%#############
    def SaveSession(self):
        global DATA, DATAMPP, DATAdark, DATAFV, IVlegendMod, MPPlegendMod
        global testdata, DATAJVforexport, DATAJVtabforexport, DATAmppforexport, DATAgroupforexport
        global takenforplot, takenforplotmpp, IVlinestyle, MPPlinestyle, samplesgroups
        global listofanswer, listoflinestyle, listofcolorstyle
        global numbLightfiles, numbDarkfiles, groupstoplot
        global titIV, titmpp, titStat
        
        current_path = os.getcwd()
        directory=QFileDialog.getExistingDirectory(self, 'Select directory')
        os.chdir(directory)
        
        pickle.dump(DATA,open('DATA.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAdark,open('DATAdark.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAMPP,open('DATAMPP.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAMPP,open('DATAFV.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)        
        pickle.dump(IVlegendMod,open('IVlegendMod.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(MPPlegendMod,open('MPPlegendMod.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)

        pickle.dump(testdata,open('testdata.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAJVforexport,open('DATAJVforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAJVtabforexport,open('DATAJVtabforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAmppforexport,open('DATAmppforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)        
        pickle.dump(DATAgroupforexport,open('DATAgroupforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAHistforexport,open('DATAHistforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAcompforexport,open('DATAcompforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAtimeevolforexport,open('DATAtimeevolforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)

        pickle.dump(takenforplot,open('takenforplot.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(takenforplotmpp,open('takenforplotmpp.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(IVlinestyle,open('IVlinestyle.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(MPPlinestyle,open('MPPlinestyle.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(samplesgroups,open('samplesgroups.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL) 
        
#        pickle.dump(listofanswer,open('listofanswer.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
#        pickle.dump(listoflinestyle,open('listoflinestyle.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
#        pickle.dump(listofcolorstyle,open('listofcolorstyle.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL) 
        pickle.dump(numbLightfiles,open('numbLightfiles.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL) 
        pickle.dump(numbDarkfiles,open('numbDarkfiles.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL) 
        pickle.dump(groupstoplot,open('groupstoplot.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL) 
        
        
        self.saveconfigsgui(directory)
        
        print("dumped")
        """
        try:
            self.dumpfilename = filedialog.asksaveasfilename(defaultextension=".pkl")
            dill.dump_session(self.dumpfilename)
        except:
            print("there is an exception")
        """
        
    def LoadSession(self):
        global DATA, DATAMPP, DATAdark, DATAFV, IVlegendMod, MPPlegendMod
        global testdata, DATAJVforexport, DATAJVtabforexport, DATAmppforexport, DATAgroupforexport
        global takenforplot, takenforplotmpp, IVlinestyle, MPPlinestyle, samplesgroups
        global listofanswer, listoflinestyle, listofcolorstyle

        global numbLightfiles, numbDarkfiles, groupstoplot
        global titIV, titmpp, titStat


        current_path = os.getcwd()
        path=QFileDialog.getExistingDirectory(self, 'Select directory')
        os.chdir(path)
        
        DATA = pickle.load(open('DATA.pkl','rb'))
        DATAdark = pickle.load(open('DATAdark.pkl','rb'))
        DATAMPP = pickle.load(open('DATAMPP.pkl','rb'))
        DATAFV = pickle.load(open('DATAFV.pkl','rb'))
        IVlegendMod = pickle.load(open('IVlegendMod.pkl','rb'))
        MPPlegendMod = pickle.load(open('MPPlegendMod.pkl','rb'))
        testdata = pickle.load(open('testdata.pkl','rb'))
        DATAJVforexport = pickle.load(open('DATAJVforexport.pkl','rb'))
        DATAJVtabforexport = pickle.load(open('DATAJVtabforexport.pkl','rb'))
        DATAmppforexport = pickle.load(open('DATAmppforexport.pkl','rb'))
        DATAgroupforexport = pickle.load(open('DATAgroupforexport.pkl','rb'))
        takenforplot = pickle.load(open('takenforplot.pkl','rb'))
        takenforplotmpp = pickle.load(open('takenforplotmpp.pkl','rb'))
        IVlinestyle = pickle.load(open('IVlinestyle.pkl','rb'))
        MPPlinestyle = pickle.load(open('MPPlinestyle.pkl','rb'))
        samplesgroups = pickle.load(open('samplesgroups.pkl','rb'))
#        listofanswer = pickle.load(open('listofanswer.pkl','rb'))
#        listoflinestyle = pickle.load(open('listoflinestyle.pkl','rb'))
#        listofcolorstyle = pickle.load(open('listofcolorstyle.pkl','rb'))
        groupstoplot = pickle.load(open('groupstoplot.pkl','rb'))
        numbDarkfiles = pickle.load(open('numbDarkfiles.pkl','rb'))
        numbLightfiles = pickle.load(open('numbLightfiles.pkl','rb'))
        
        self.loadconfigsgui(path)
        """
        try:
            self.dumpfilename = filedialog.asksaveasfilename(defaultextension=".pkl")
            dill.load_session(self.dumpfilename)
        except:
            print("there is an exception")
        """
        print("loaded")
        
            
        if DATAMPP!=[]:
            self.ui.listWidget_MppSamples.clear()
            self.ui.listWidget_MppSamples.addItems(DATAMPP.keys())
            
        if DATA!=[]:
            titIV =0
            titmpp=0
            titStat=0
            self.updateTable(DATA)
            self.Confirmgroupnamechanges()
            
    def loadconfigsgui(self,directory):
        
        if directory=='':
            current_path = os.getcwd()
            fname = QFileDialog.getSaveFileName(self, 'load file', current_path,"Text files (*.txt)")[0]
        else:
            fname=os.path.join(directory,'guiconfigs.txt')
        
        
        with open(fname,'r') as file:
            for line in file:
                if 'checkBox_JVLegend' in line:
                    self.ui.checkBox_JVLegend.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_MppLegend' in line:
                    self.ui.checkBox_MppLegend.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_BoxPlotBig4' in line:
                    self.ui.checkBox_BoxPlotBig4.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_BoxPlotRevForw' in line:
                    self.ui.checkBox_BoxPlotRevForw.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_BoxPlotBoxPlot' in line:
                    self.ui.checkBox_BoxPlotBoxPlot.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_BoxPlotAftermpp' in line:
                    self.ui.checkBox_BoxPlotAftermpp.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_BoxPlotBkg' in line:
                    self.ui.checkBox_BoxPlotBkg.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_PVPTimeBig4' in line:
                    self.ui.checkBox_PVPTimeBig4.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_PVPTimeLine' in line:
                    self.ui.checkBox_PVPTimeLine.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_PVPTimeRelativeTime' in line:
                    self.ui.checkBox_PVPTimeRelativeTime.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_PVPTimeNormal' in line:
                    self.ui.checkBox_PVPTimeNormal.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_bestofRevFor' in line:
                    self.ui.checkBox_bestofRevFor.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_BestEffPixDay' in line:
                    self.ui.checkBox_BestEffPixDay.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_Histxscale' in line:
                    self.ui.checkBox_Histxscale.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_AAxlsxsummary' in line:
                    self.ui.checkBox_AAxlsxsummary.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_AAstatgraphs' in line:
                    self.ui.checkBox_AAstatgraphs.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_AAivgraphs' in line:
                    self.ui.checkBox_AAivgraphs.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_AAmppgraphs' in line:
                    self.ui.checkBox_AAmppgraphs.setChecked(eval(line.split('\t')[1]))
                elif 'checkBox_AAtxtfiles' in line:
                    self.ui.checkBox_AAtxtfiles.setChecked(eval(line.split('\t')[1]))
                elif 'spinBox_JVfontsize' in line:
                    self.ui.spinBox_JVfontsize.setValue(float(line.split('\t')[1]))
                elif 'spinBox_MppFontsize' in line:
                    self.ui.spinBox_MppFontsize.setValue(float(line.split('\t')[1]))
                elif 'spinBox_BoxPlotFontsize' in line:
                    self.ui.spinBox_BoxPlotFontsize.setValue(float(line.split('\t')[1]))
                elif 'spinBox_BoxPlotRotation' in line:
                    self.ui.spinBox_BoxPlotRotation.setValue(float(line.split('\t')[1]))
                elif 'spinBox_PVPTimeNormalPoint' in line:
                    self.ui.spinBox_PVPTimeNormalPoint.setValue(float(line.split('\t')[1]))
                elif 'spinBox_HistoBins' in line:
                    self.ui.spinBox_HistoBins.setValue(float(line.split('\t')[1]))
                elif 'spinBox_HistxscaleMin' in line:
                    self.ui.spinBox_HistxscaleMin.setValue(float(line.split('\t')[1]))
                elif 'spinBox_HistxscaleMax' in line:
                    self.ui.spinBox_HistxscaleMax.setValue(float(line.split('\t')[1]))
                elif 'comboBox_BoxPlotParam' in line:
                    index = self.ui.comboBox_BoxPlotParam.findText(line.split('\t')[1][:-1], QtCore.Qt.MatchFixedString)
                    if index >= 0:
                         self.ui.comboBox_BoxPlotParam.setCurrentIndex(index)
                elif 'comboBox_PVPTimeParam' in line:
                    index = self.ui.comboBox_PVPTimeParam.findText(line.split('\t')[1][:-1], QtCore.Qt.MatchFixedString)
                    if index >= 0:
                         self.ui.comboBox_PVPTimeParam.setCurrentIndex(index)
                elif 'comboBox_PVPx' in line:
                    index = self.ui.comboBox_PVPx.findText(line.split('\t')[1][:-1], QtCore.Qt.MatchFixedString)
                    if index >= 0:
                         self.ui.comboBox_PVPx.setCurrentIndex(index)
                elif 'comboBox_PVPy' in line:
                    index = self.ui.comboBox_PVPy.findText(line.split('\t')[1][:-1], QtCore.Qt.MatchFixedString)
                    if index >= 0:
                         self.ui.comboBox_PVPy.setCurrentIndex(index)
                elif 'comboBox_HistoType' in line:
                    index = self.ui.comboBox_HistoType.findText(line.split('\t')[1][:-1], QtCore.Qt.MatchFixedString)
                    if index >= 0:
                         self.ui.comboBox_HistoType.setCurrentIndex(index)
                elif 'comboBox_HistoScanDirect' in line:
                    index = self.ui.comboBox_HistoScanDirect.findText(line.split('\t')[1][:-1], QtCore.Qt.MatchFixedString)
                    if index >= 0:
                         self.ui.comboBox_HistoScanDirect.setCurrentIndex(index)
                elif 'comboBox_HistoParam' in line:
                    index = self.ui.comboBox_HistoParam.findText(line.split('\t')[1][:-1], QtCore.Qt.MatchFixedString)
                    if index >= 0:
                         self.ui.comboBox_HistoParam.setCurrentIndex(index)
                     
        
    def saveconfigsgui(self,directory):
        
        if directory=='':
            current_path = os.getcwd()
            fname = QFileDialog.getSaveFileName(self, 'Save file', current_path,"Text files (*.txt)")[0]
        else:
            fname=os.path.join(directory,'guiconfigs.txt')
            # print(fname)
        
        with open(fname,'w') as file:
            text='checkBox_JVLegend\t'+ str(self.ui.checkBox_JVLegend.isChecked())+'\n'+\
                'checkBox_MppLegend\t'+ str(self.ui.checkBox_MppLegend.isChecked())+'\n'+\
                'checkBox_BoxPlotBig4\t'+ str(self.ui.checkBox_BoxPlotBig4.isChecked())+'\n'+\
                'checkBox_BoxPlotRevForw\t'+ str(self.ui.checkBox_BoxPlotRevForw.isChecked())+'\n'+\
                'checkBox_BoxPlotBoxPlot\t'+ str(self.ui.checkBox_BoxPlotBoxPlot.isChecked())+'\n'+\
                'checkBox_BoxPlotAftermpp\t'+ str(self.ui.checkBox_BoxPlotAftermpp.isChecked())+'\n'+\
                'checkBox_BoxPlotBkg\t'+ str(self.ui.checkBox_BoxPlotBkg.isChecked())+'\n'+\
                'checkBox_PVPTimeBig4\t'+ str(self.ui.checkBox_PVPTimeBig4.isChecked())+'\n'+\
                'checkBox_PVPTimeLine\t'+ str(self.ui.checkBox_PVPTimeLine.isChecked())+'\n'+\
                'checkBox_PVPTimeRelativeTime\t'+ str(self.ui.checkBox_PVPTimeRelativeTime.isChecked())+'\n'+\
                'checkBox_PVPTimeNormal\t'+ str(self.ui.checkBox_PVPTimeNormal.isChecked())+'\n'+\
                'checkBox_bestofRevFor\t'+ str(self.ui.checkBox_bestofRevFor.isChecked())+'\n'+\
                'checkBox_BestEffPixDay\t'+ str(self.ui.checkBox_BestEffPixDay.isChecked())+'\n'+\
                'checkBox_Histxscale\t'+ str(self.ui.checkBox_Histxscale.isChecked())+'\n'+\
                'checkBox_AAxlsxsummary\t'+ str(self.ui.checkBox_AAxlsxsummary.isChecked())+'\n'+\
                'checkBox_AAstatgraphs\t'+ str(self.ui.checkBox_AAstatgraphs.isChecked())+'\n'+\
                'checkBox_AAivgraphs\t'+ str(self.ui.checkBox_AAivgraphs.isChecked())+'\n'+\
                'checkBox_AAmppgraphs\t'+ str(self.ui.checkBox_AAmppgraphs.isChecked())+'\n'+\
                'checkBox_AAtxtfiles\t'+ str(self.ui.checkBox_AAtxtfiles.isChecked())+'\n'+\
                'spinBox_JVfontsize\t'+ str(self.ui.spinBox_JVfontsize.value())+'\n'+\
                'spinBox_MppFontsize\t'+ str(self.ui.spinBox_MppFontsize.value())+'\n'+\
                'spinBox_BoxPlotFontsize\t'+ str(self.ui.spinBox_BoxPlotFontsize.value())+'\n'+\
                'spinBox_BoxPlotRotation\t'+ str(self.ui.spinBox_BoxPlotRotation.value())+'\n'+\
                'spinBox_PVPTimeNormalPoint\t'+ str(self.ui.spinBox_PVPTimeNormalPoint.value())+'\n'+\
                'spinBox_HistoBins\t'+ str(self.ui.spinBox_HistoBins.value())+'\n'+\
                'spinBox_HistxscaleMin\t'+ str(self.ui.spinBox_HistxscaleMin.value())+'\n'+\
                'spinBox_HistxscaleMax\t'+ str(self.ui.spinBox_HistxscaleMax.value())+'\n'+\
                'comboBox_BoxPlotParam\t'+ str(self.ui.comboBox_BoxPlotParam.currentText())+'\n'+\
                'comboBox_PVPTimeParam\t'+ str(self.ui.comboBox_PVPTimeParam.currentText())+'\n'+\
                'comboBox_PVPx\t'+ str(self.ui.comboBox_PVPx.currentText())+'\n'+\
                'comboBox_PVPy\t'+ str(self.ui.comboBox_PVPy.currentText())+'\n'+\
                'comboBox_HistoType\t'+ str(self.ui.comboBox_HistoType.currentText())+'\n'+\
                'comboBox_HistoScanDirect\t'+ str(self.ui.comboBox_HistoScanDirect.currentText())+'\n'+\
                'comboBox_HistoParam\t'+ str(self.ui.comboBox_HistoParam.currentText())
            file.write(text)
        
        

            
    def SaveToDB(self):
        global DATA
        
        
#%%#############
            
    def ExportAutoAnalysis(self):
        global DATA
        global DATAdark
        global DATAFV
        global DATAMPP
        global samplesgroups

        current_path = os.getcwd()
        folderName=QFileDialog.getExistingDirectory(self, 'Select directory')
        # folderName = filedialog.askdirectory(title = "choose a folder to export the auto-analysis results", initialdir=os.path.dirname(current_path))
        os.chdir(folderName)
        
        DATAx=[DATA[key] for key in DATA.keys()]
        DATAMPPx=[DATAMPP[key] for key in DATAMPP.keys()]
        # DATAdarkx=[DATAdark[key] for key in DATAdark.keys()]
        sorted_datajv = sorted(DATAx, key=itemgetter('DepID')) 
        sorted_datampp = sorted(DATAMPPx, key=itemgetter('DepID')) 
        sorted_datadark = sorted(DATAdark, key=itemgetter('DepID'))

        
        Thread_AA(DATAx,DATAMPPx,DATAdark,sorted_datajv,sorted_datampp,sorted_datadark)


# class Thread_AA(QThread):
    
#     finished = pyqtSignal()
#     change_value = pyqtSignal(int)
#     def __init__(self, DATAx,DATAMPPx,DATAdarkx,sorted_datajv,sorted_datampp,sorted_datadark, parent=None):
#         QThread.__init__(self, parent)
#         self.DATAx=DATAx
#         self.DATAMPPx=DATAMPPx
#         self.DATAdarkx=DATAdarkx
#         self.sorted_datajv=sorted_datajv
#         self.sorted_datampp=sorted_datampp
#         self.sorted_datadark=sorted_datadark
        
#     def run(self):
#         # global DATA, DATAdark, colorstylelist
#         # global DATAMPP, numbLightfiles, numbDarkfiles, colormapname
#         print('threadstart')
#         DATAx=self.DATAx
#         DATAMPP=self.DATAMPPx
#         DATAdark=self.DATAdarkx
#         sorted_datajv=self.sorted_datajv
#         sorted_datampp=self.sorted_datampp
#         sorted_datadark=self.sorted_datadark
#         DATAbysubstrate=[] 
#         DATAmppbysubstrate=[]
#         DATAdarkbysubstrate=[] 
#         bestEff=[]
#         bestvocff =[]

def Thread_AA(DATAx,DATAMPPx,DATAdarkx,sorted_datajv,sorted_datampp,sorted_datadark):
    
    DATAx=copy.deepcopy(DATAx)
    DATAMPP=DATAMPPx
    DATAdark=DATAdarkx
    sorted_datajv=sorted_datajv
    sorted_datampp=sorted_datampp
    sorted_datadark=sorted_datadark
    DATAbysubstrate=[] 
    DATAmppbysubstrate=[]
    DATAdarkbysubstrate=[] 
    bestEff=[]
    bestvocff =[]
    
    batchname=DATAx[0]["batchname"]
    
    # plt.show(block=False)
    
    for key, group in groupby(sorted_datadark, key=lambda x:x['DepID']):
        substratpartdat=[key,list(group)]
        DATAdarkbysubstrate.append(copy.deepcopy(substratpartdat))
        try:
            if window.ui.checkBox_AAtxtfiles.isChecked():
                contenttxtfile=["","",""]
                for item in range(len(substratpartdat[1])):
                    contenttxtfile[0] += "Voltage\t" + "Current density\t" 
                    contenttxtfile[1] += "mV\t" + "mA/cm2\t"
                    contenttxtfile[2] += " \t" + substratpartdat[1][item]["SampleName"] + '\t'
                contenttxtfile[0]=contenttxtfile[0][:-1]+'\n'
                contenttxtfile[1]=contenttxtfile[1][:-1]+'\n'
                contenttxtfile[2]=contenttxtfile[2][:-1]+'\n'
                #find max length of subjv lists => fill the others with blancks
                lengthmax=max([len(substratpartdat[1][x]["IVData"][0]) for x in range(len(substratpartdat[1]))])
                for item in range(len(substratpartdat[1])):
                    while (len(substratpartdat[1][item]["IVData"][0])<lengthmax):
                        substratpartdat[1][item]["IVData"][0].append('')   
                        substratpartdat[1][item]["IVData"][1].append('') 
                #append them all in the content list
                for item0 in range(lengthmax):
                    ligne=""
                    for item in range(len(substratpartdat[1])):
                        ligne += str(substratpartdat[1][item]["IVData"][0][item0]) +'\t' + str(substratpartdat[1][item]["IVData"][1][item0]) +'\t'   
                    ligne=ligne[:-1]+'\n'    
                    contenttxtfile.append(ligne)
                #export it to txt files
                file = open(str(substratpartdat[0]) + '_lowIllum.txt','w', encoding='ISO-8859-1')
                file.writelines("%s" % item for item in contenttxtfile)
                file.close()
        except:
            print("there's an issue with creating JVdark txt files")
        try:
            if window.ui.checkBox_AAivgraphs.isChecked():
                plt.clf()
                plt.close("all")
                fig, axs =plt.subplots(1,2)
                x1=min(DATAdarkbysubstrate[-1][1][0]["IVData"][0])
                x2=max(DATAdarkbysubstrate[-1][1][0]["IVData"][0])
                y1=min(DATAdarkbysubstrate[-1][1][0]["IVData"][1])
                if max(DATAdarkbysubstrate[-1][1][0]["IVData"][1])<10:
                    y2=max(DATAdarkbysubstrate[-1][1][0]["IVData"][1])
                else:
                    y2=10
                for item in range(len(substratpartdat[1])):
                    axs[0].plot(DATAdarkbysubstrate[-1][1][item]["IVData"][0],DATAdarkbysubstrate[-1][1][item]["IVData"][1], label=DATAdarkbysubstrate[-1][1][item]["SampleName"])
                    if min(DATAdarkbysubstrate[-1][1][item]["IVData"][0])<x1:
                        x1=copy.deepcopy(min(DATAdarkbysubstrate[-1][1][item]["IVData"][0]))
                    if max(DATAdarkbysubstrate[-1][1][item]["IVData"][0])>x2:
                        x2=copy.deepcopy(max(DATAdarkbysubstrate[-1][1][item]["IVData"][0]))
                    if min(DATAdarkbysubstrate[-1][1][item]["IVData"][1])<y1:
                        y1=copy.deepcopy(min(DATAdarkbysubstrate[-1][1][item]["IVData"][1]))
                    if max(DATAdarkbysubstrate[-1][1][item]["IVData"][1])>y2 and max(DATAdarkbysubstrate[-1][1][item]["IVData"][1])<10:
                        y2=copy.deepcopy(max(DATAdarkbysubstrate[-1][1][item]["IVData"][1]))
                    slist=DATAdarkbysubstrate[-1][1][item]
                axs[0].set_title("Low Illumination: "+str(substratpartdat[0]))
                axs[0].set_xlabel('Voltage (mV)')
                axs[0].set_ylabel('Current density (mA/cm'+'\xb2'+')')
                axs[0].axhline(y=0, color='k')
                axs[0].axvline(x=0, color='k')
                axs[0].axis([x1,x2,y1,y2])
                for item in range(len(substratpartdat[1])):
                    axs[1].semilogy(DATAdarkbysubstrate[-1][1][item]["IVData"][0],list(map(abs, DATAdarkbysubstrate[-1][1][item]["IVData"][1])), label=DATAdarkbysubstrate[-1][1][item]["SampleName"])
                axs[1].set_title("logscale")
                axs[1].set_xlabel('Voltage (mV)')
                axs[1].axhline(y=0, color='k')
                axs[1].axvline(x=0, color='k')
                box = axs[0].get_position()
                axs[0].set_position([box.x0, box.y0, box.width, box.height])
                box = axs[1].get_position()
                axs[1].set_position([box.x0, box.y0, box.width, box.height])
                lgd=axs[1].legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1)
                #axs[1].legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.2)
                plt.savefig(str(substratpartdat[0])+'_lowIllum.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
                plt.close(fig) 
                plt.close('all')
                plt.clf()
        except:
            print("there's an issue with creating JV lowillum graphs")
    plt.clf()
    try:
        for key, group in groupby(sorted_datampp, key=lambda x:x['DepID']):
            substratpartdat=[key,list(group)]
            DATAmppbysubstrate.append(copy.deepcopy(substratpartdat))
            for item0 in range(len(substratpartdat[1])):
                if window.ui.checkBox_AAtxtfiles.isChecked():
                    contenttxtfile=["Voltage\tCurrent density\tTime\tPmpp\tTime\tVstep\n","V\tmA/cm2\ts\tW/m2\ts\tV\n"]
                    for item in range(len(substratpartdat[1][item0]["MppData"][0])):
                        contenttxtfile.append(str(substratpartdat[1][item0]["MppData"][0][item])+"\t"+str(substratpartdat[1][item0]["MppData"][1][item])+"\t"+str(substratpartdat[1][item0]["MppData"][2][item])+"\t"+str(substratpartdat[1][item0]["MppData"][3][item])+"\t"+str(substratpartdat[1][item0]["MppData"][2][item])+"\t"+str(substratpartdat[1][item0]["MppData"][4][item])+"\n")
                    #export to txt files
                    file = open(str(substratpartdat[1][item0]["SampleName"]) + '_Pmpp.txt','w', encoding='ISO-8859-1')
                    file.writelines("%s" % item for item in contenttxtfile)
                    file.close()
                #export figures
                if window.ui.checkBox_AAmppgraphs.isChecked():
                    plt.plot(substratpartdat[1][item0]["MppData"][2],substratpartdat[1][item0]["MppData"][3])
                    plt.xlabel('Time (s)')
                    plt.ylabel('Power (mW/cm'+'\xb2'+')')        
                    plt.savefig(str(substratpartdat[1][item0]["SampleName"]) + '_Pmpp.png',dpi=300)
                plt.close('all')
                plt.clf()
    except:
        print("there's an issue with creating pmpp txt files")
    
    print('start substrate graph')
    for key, group in groupby(sorted_datajv, key=lambda x:x['DepID']):
        substratpartdat=[key,list(group)]
        DATAbysubstrate.append(copy.deepcopy(substratpartdat))
        if window.ui.checkBox_AAtxtfiles.isChecked():
            contenttxtfile=["","",""]
            for item in range(len(substratpartdat[1])):
                contenttxtfile[0] += "Voltage\t" + "Current density\t" 
                contenttxtfile[1] += "mV\t" + "mA/cm2\t"
                contenttxtfile[2] += " \t" + substratpartdat[1][item]["SampleName"] + '\t'
            contenttxtfile[0]=contenttxtfile[0][:-1]+'\n'
            contenttxtfile[1]=contenttxtfile[1][:-1]+'\n'
            contenttxtfile[2]=contenttxtfile[2][:-1]+'\n'
            #print(contenttxtfile)  
            #find max length of subjv lists => fill the others with blancks
            lengthmax=max([len(substratpartdat[1][x]["IVData"][0]) for x in range(len(substratpartdat[1]))])
            for item in range(len(substratpartdat[1])):
                while (len(substratpartdat[1][item]["IVData"][0])<lengthmax):
                    substratpartdat[1][item]["IVData"][0].append('')   
                    substratpartdat[1][item]["IVData"][1].append('') 
            #append them all in the content list
            for item0 in range(lengthmax):
                ligne=""
                for item in range(len(substratpartdat[1])):
                    ligne += str(substratpartdat[1][item]["IVData"][0][item0]) +'\t' + str(substratpartdat[1][item]["IVData"][1][item0]) +'\t'   
                ligne=ligne[:-1]+'\n'    
                contenttxtfile.append(ligne)
            #export it to txt files
            file = open(str(substratpartdat[0]) + '.txt','w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in contenttxtfile)
            file.close()
        #graphs by substrate with JV table, separate graph and table production, then reassemble to export...
        plt.clf()
        if window.ui.checkBox_AAivgraphs.isChecked() or window.ui.checkBox_AAstatgraphs.isChecked() or window.ui.checkBox_AAmppgraphs.isChecked():
            collabel=("Voc","Jsc","FF","Eff","Roc","Rsc","Vstart","Vend","CellSurface")
            nrows, ncols = len(substratpartdat[1])+1, len(collabel)
            hcell, wcell = 0.3, 1.
            hpad, wpad = 0, 0 
            fig2=plt.figure(figsize=(ncols*wcell+wpad, nrows*hcell+hpad))
            ax2 = fig2.add_subplot(111)
            
            fig1=plt.figure()
            ax3 = fig1.add_subplot(111)
            
            item=0
            while item < len(DATAbysubstrate[-1][1]):
                try:
                    x1=min(DATAbysubstrate[-1][1][item]["IVData"][0])
                    # print(x1)
                    x2=max(DATAbysubstrate[-1][1][item]["IVData"][0])
                    y1=min(DATAbysubstrate[-1][1][item]["IVData"][1])
                    if max(DATAbysubstrate[-1][1][item]["IVData"][1])<10:
                        y2=max(DATAbysubstrate[-1][1][item]["IVData"][1])
                    else:
                        y2=10
                    break
                except TypeError:
                    item+=1
                    
            tabledata=[]
            rowlabel=[]
            for item in range(len(substratpartdat[1])):
                # print(item)
                # print(DATAbysubstrate[-1][1][item]["IVData"][0])
                try:
                    if min(DATAbysubstrate[-1][1][item]["IVData"][0])<x1:
                        # x1=copy.deepcopy(min(DATAbysubstrate[-1][1][item]["IVData"][0]))
                        x1=min(DATAbysubstrate[-1][1][item]["IVData"][0])
                    if max(DATAbysubstrate[-1][1][item]["IVData"][0])>x2:
                        x2=copy.deepcopy(max(DATAbysubstrate[-1][1][item]["IVData"][0]))
                    if min(DATAbysubstrate[-1][1][item]["IVData"][1])<y1:
                        y1=copy.deepcopy(min(DATAbysubstrate[-1][1][item]["IVData"][1]))
                    if max(DATAbysubstrate[-1][1][item]["IVData"][1])>y2 and max(DATAbysubstrate[-1][1][item]["IVData"][1])<10:
                        y2=copy.deepcopy(max(DATAbysubstrate[-1][1][item]["IVData"][1]))
                    ax3.plot(DATAbysubstrate[-1][1][item]["IVData"][0],DATAbysubstrate[-1][1][item]["IVData"][1], label=DATAbysubstrate[-1][1][item]["SampleName"])
                    slist=DATAbysubstrate[-1][1][item]
                    rowlabel.append(slist["SampleName"])
                    tabledata.append(['%.f' % float(slist["Voc"]),'%.2f' % float(slist["Jsc"]),'%.2f' % float(slist["FF"]),'%.2f' % float(slist["Eff"]),'%.2f' % float(slist["Roc"]),'%.2f' % float(slist["Rsc"]),'%.2f' % float(slist["Vstart"]),'%.2f' % float(slist["Vend"]),'%.2f' % float(slist["CellSurface"])])
                except:
                    print('exception <, ',DATAbysubstrate[-1][1][item]["SampleName"])
                    pass
                
            ax3.set_title(str(substratpartdat[0]))
            ax3.set_xlabel('Voltage (mV)')
            ax3.set_ylabel('Current density (mA/cm'+'\xb2'+')')
            ax3.axhline(y=0, color='k')
            ax3.axvline(x=0, color='k')
            ax3.axis([x1,x2,y1,y2])
            
            if window.ui.checkBox_AAivgraphs.isChecked():
                rowlabel=tuple(rowlabel)
                the_table = ax2.table(cellText=tabledata,colLabels=collabel,rowLabels=rowlabel,loc='center')
                the_table.set_fontsize(18)
                ax2.axis('off')
                fig2.savefig(str(substratpartdat[0])+'_table.png',dpi=200,bbox_inches="tight")
                handles, labels = ax3.get_legend_handles_labels()
                lgd = ax3.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
                fig1.savefig(str(substratpartdat[0])+'.png',dpi=200, bbox_extra_artists=(lgd,),bbox_inches="tight")
            
                images = list(map(ImageTk.open, [str(substratpartdat[0])+'.png',str(substratpartdat[0])+'_table.png']))
                widths, heights = zip(*(i.size for i in images))
                total_width = max(widths)
                max_height = sum(heights)
                new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
                new_im.paste(im=images[0],box=(0,0))
                new_im.paste(im=images[1],box=(0,heights[0]))
                new_im.save(str(substratpartdat[0])+'.png')
                
                os.remove(str(substratpartdat[0])+'_table.png')
            plt.close(fig2)
            plt.close(fig1)
            plt.close('all')
            plt.clf()
            print('starting best FR')
            if DATAx[0]["Setup"]=="TFIV"  or DATAx[0]["Setup"]=="SSIgorC215":
                #graph best FR of this substrate
                best = sorted(DATAbysubstrate[-1][1], key=itemgetter('VocFF'), reverse=True)
                item=0
                while item<len(best):
                    if float(best[item]["FF"])>10 and float(best[item]["Jsc"])<40:
                        bestvocff.append(copy.deepcopy(best[item]))
                        break
                    else:
                        item+=1
                best = sorted(DATAbysubstrate[-1][1], key=itemgetter('Eff'), reverse=True)
                item=0
                while item<len(best):
                    if float(best[item]["FF"])>10 and float(best[item]["Jsc"])<40:
                        fig=plt.figure()
                        ax=fig.add_subplot(111)
                        bestEff.append(copy.deepcopy(best[item]))
                        if best[item]["ScanDirection"]=="Reverse":
                            ax.plot(best[item]["IVData"][0],best[item]["IVData"][1],"r", label=best[item]["SampleName"])
                            text = best[item]["ScanDirection"]+"; "+"Voc: " + '%.f' % float(best[item]["Voc"]) +" mV; " + "Jsc: " + '%.2f' % float(best[item]["Jsc"]) +" mA/cm2; " +"FF: " + '%.2f' % float(best[item]["FF"]) +" %; " +"Eff: " + '%.2f' % float(best[item]["Eff"]) +" %"
                            ax.set_title('Best:'+ best[item]["SampleName"]+"\n"+text, fontsize = 10, color="r")
                        elif best[item]["ScanDirection"]=="Forward":
                            ax.plot(best[item]["IVData"][0],best[item]["IVData"][1],"k", label=best[item]["SampleName"]) 
                            text = best[item]["ScanDirection"]+"; "+"Voc: " + '%.f' % float(best[item]["Voc"]) +" mV; " + "Jsc: " + '%.2f' % float(best[item]["Jsc"]) +" mA/cm2; " +"FF: " + '%.2f' % float(best[item]["FF"]) +" %; " +"Eff: " + '%.2f' % float(best[item]["Eff"]) +" %"
                            ax.set_title('Best:'+ best[item]["SampleName"]+"\n"+text, fontsize = 10, color="k")
                        pos=0
                        if best[item]["ScanDirection"]=="Reverse":
                            for item0 in range(item+1,len(best),1):
                                if best[item0]["ScanDirection"]=="Forward" and best[item]["Cellletter"]==best[item0]["Cellletter"]:
                                    #other=best[item0]
                                    pos=item0
                                    ax.plot(best[pos]["IVData"][0],best[pos]["IVData"][1],"k", label=best[pos]["SampleName"])
                                    ax.set_title('Best:'+ best[item]["SampleName"]+"-"+best[pos]["SampleName"]+"\n"+text, fontsize = 10, color="r")
                                    break
                            
                        elif best[item]["ScanDirection"]=="Forward":
                            for item0 in range(item+1,len(best),1):
                                if best[item0]["ScanDirection"]=="Reverse" and best[item]["Cellletter"]==best[item0]["Cellletter"]:
                                    #other=best[item0]
                                    pos=item0
                                    ax.plot(best[pos]["IVData"][0],best[pos]["IVData"][1],"r", label=best[pos]["SampleName"])
                                    ax.set_title('Best:'+ best[item]["SampleName"]+"-"+best[pos]["SampleName"]+"\n"+text, fontsize = 10, color="k")
                                    break
                        for item0 in range(len(DATAx)):
                            if DATAx[item0]["DepID"]==best[item]["DepID"] and DATAx[item0]["Cellletter"]==best[item]["Cellletter"] and DATAx[item0]["Illumination"]=="Dark":
                                ax.plot(DATAx[item0]["IVData"][0],DATAx[item0]["IVData"][1],color='gray',linestyle='dashed', label=DATAx[item0]["SampleName"])
                                break
                        
                        ax.set_xlabel('Voltage (mV)')
                        ax.set_ylabel('Current density (mA/cm'+'\xb2'+')')
                        ax.axhline(y=0, color='k')
                        ax.axvline(x=0, color='k')
                        
                        x1=min(best[item]["IVData"][0][0],best[pos]["IVData"][0][0])
                        x2=max(best[item]["IVData"][0][-1],best[pos]["IVData"][0][-1])
                        y1=1.1*min(best[item]["IVData"][1]+best[pos]["IVData"][1])
                        if max(best[item]["IVData"][1]+best[pos]["IVData"][1])>10:
                            y2=10
                        else:
                            y2=max(best[item]["IVData"][1]+best[pos]["IVData"][1])
                        ax.axis([x1,x2,y1,y2])
                        if window.ui.checkBox_AAivgraphs.isChecked():
                            handles, labels = ax.get_legend_handles_labels()
                            lgd = ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
                            fig.savefig(str(substratpartdat[0])+'_BestRevForw.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
                        plt.close('all')
                        plt.clf()
                        break
                    else:
                        item+=1 
            plt.close('all')
            plt.clf()
            #specific power graph
            if window.ui.checkBox_AAmppgraphs.isChecked(): 
                for item in range(len(DATAmppbysubstrate)):
                    if substratpartdat[0]==DATAmppbysubstrate[item][0]:
                        for item0 in range(len(DATAmppbysubstrate[item][1])):
                            fig=plt.figure()
                            ax=fig.add_subplot(111)
                            ax.plot([],[],label="Initial scans",color="White") 
                            checkaftermpp=1
                            for item1 in range(len(DATAbysubstrate[-1][1])):
                                if DATAmppbysubstrate[item][1][item0]["Cellletter"]==DATAbysubstrate[-1][1][item1]["Cellletter"] and DATAbysubstrate[-1][1][item1]["Illumination"]=="Light":
                                    if DATAbysubstrate[-1][1][item1]["aftermpp"] and checkaftermpp:
                                        ax.plot([],[],label="After mpp",color="White") 
                                        checkaftermpp=0
                                        ax.plot(DATAbysubstrate[-1][1][item1]["IVData"][0],[-a*b for a,b in zip(DATAbysubstrate[-1][1][item1]["IVData"][0],DATAbysubstrate[-1][1][item1]["IVData"][1])],label=DATAbysubstrate[-1][1][item1]["SampleName"])   
                                    else:
                                        ax.plot(DATAbysubstrate[-1][1][item1]["IVData"][0],[-a*b for a,b in zip(DATAbysubstrate[-1][1][item1]["IVData"][0],DATAbysubstrate[-1][1][item1]["IVData"][1])],label=DATAbysubstrate[-1][1][item1]["SampleName"])
                            ax.plot([abs(a) for a in DATAmppbysubstrate[item][1][item0]["MppData"][0]],DATAmppbysubstrate[item][1][item0]["MppData"][3])
                            ax.set_xlabel('Voltage (mV)')
                            ax.set_ylabel('Specific power (mW/cm$^2$)')
                            ax.axhline(y=0, color='k')
                            ax.axvline(x=0, color='k')
                            ax.set_xlim(left=0)
                            ax.set_ylim(bottom=0)
                            ax.legend()
                            fig.savefig(DATAmppbysubstrate[item][1][item0]["SampleName"]+'_specpower.png',dpi=300,bbox_inches="tight")
                            plt.close("all")
                            plt.clf()
                        break
    plt.close("all")
    plt.clf()
    print('start besteff stat graph')
    if DATAx[0]["Setup"]=="TFIV" or DATAx[0]["Setup"]=="SSIgorC215":
#            try:        
        if window.ui.checkBox_AAstatgraphs.isChecked():
            #graph with all best efficient cells from all substrates
            fig=plt.figure()
            ax=fig.add_subplot(111)
            bestEff2=[item for item in bestEff if item["Illumination"]=="Light"]
            bestEffsorted = sorted(bestEff2, key=itemgetter('Eff'), reverse=True) 
            tabledata=[]
            rowlabel=[]
            minJscfind=[]
            maxcurrentfind=[]
            minVfind=[]
            maxVfind=[]
            for item in range(len(bestEffsorted)):
                ax.plot(bestEffsorted[item]["IVData"][0],bestEffsorted[item]["IVData"][1], label=bestEffsorted[item]["SampleName"]) 
                rowlabel.append(bestEffsorted[item]["SampleName"])
                tabledata.append(['%.f' % float(bestEffsorted[item]["Voc"]),'%.2f' % float(bestEffsorted[item]["Jsc"]),'%.2f' % float(bestEffsorted[item]["FF"]),'%.2f' % float(bestEffsorted[item]["Eff"]),'%.2f' % float(bestEffsorted[item]["Roc"]),'%.2f' % float(bestEffsorted[item]["Rsc"]),'%.2f' % float(bestEffsorted[item]["Vstart"]),'%.2f' % float(bestEffsorted[item]["Vend"]),'%.2f' % float(bestEffsorted[item]["CellSurface"])])
                minJscfind.append(min(bestEffsorted[item]["IVData"][1]))
                maxcurrentfind.append(max(bestEffsorted[item]["IVData"][1]))
                minVfind.append(min(bestEffsorted[item]["IVData"][0]))
                maxVfind.append(max(bestEffsorted[item]["IVData"][0]))
            ax.set_xlabel('Voltage (mV)')
            ax.set_ylabel('Current density (mA/cm'+'\xb2'+')')
            ax.axhline(y=0, color='k')
            ax.axvline(x=0, color='k')
            x1=min(minVfind)
            x2=max(maxVfind)
            y1=1.1*min(minJscfind)
            if max(maxcurrentfind)>10:
                y2=10
            else:
                y2=max(maxcurrentfind)
            ax.axis([x1,x2,y1,y2])
            handles, labels = ax.get_legend_handles_labels()
            lgd = ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
            fig.savefig(batchname+'_MostEfficientCells.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
            plt.close()
            collabel=("Voc","Jsc","FF","Eff","Roc","Rsc","Vstart","Vend","CellSurface")
            nrows, ncols = len(bestEffsorted)+1, len(collabel)
            hcell, wcell = 0.3, 1.
            hpad, wpad = 0, 0 
            fig=plt.figure(figsize=(ncols*wcell+wpad, nrows*hcell+hpad))
            ax = fig.add_subplot(111)
            rowlabel=tuple(rowlabel)
            the_table = ax.table(cellText=tabledata,colLabels=collabel,rowLabels=rowlabel,loc='center')
            the_table.set_fontsize(18)
            ax.axis('off')
            fig.savefig('MostEfficientCellstable.png',dpi=300,bbox_inches="tight")
            plt.close("all")
            images = list(map(ImageTk.open, [batchname+'_MostEfficientCells.png','MostEfficientCellstable.png']))
            widths, heights = zip(*(i.size for i in images))
            total_width = max(widths)
            max_height = sum(heights)
            new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
            new_im.paste(im=images[0],box=(0,0))
            new_im.paste(im=images[1],box=(0,heights[0]))
            new_im.save(batchname+'_MostEfficientCells.png')
            os.remove('MostEfficientCellstable.png')
            plt.close()
            plt.clf()
            #graph with all best voc*FF cells from all substrates  
            fig=plt.figure()
            ax=fig.add_subplot(111)
            bestvocff2=[item for item in bestvocff if item["Illumination"]=="Light"]
            bestvocffsorted = sorted(bestvocff2, key=itemgetter('VocFF'), reverse=True) 
            tabledata=[]
            rowlabel=[]
            minJscfind=[]
            maxcurrentfind=[]
            minVfind=[]
            maxVfind=[]
            for item in range(len(bestvocffsorted)):
                x=bestvocffsorted[item]["IVData"][0]
                y=bestvocffsorted[item]["IVData"][1]
                ax.plot(x,y, label=bestvocffsorted[item]["SampleName"]) 
                rowlabel.append(bestvocffsorted[item]["SampleName"])
                tabledata.append(['%.f' % float(bestvocffsorted[item]["Voc"]),'%.2f' % float(bestvocffsorted[item]["Jsc"]),'%.2f' % float(bestvocffsorted[item]["FF"]),'%.2f' % float(bestvocffsorted[item]["Eff"]),'%.2f' % float(bestvocffsorted[item]["Roc"]),'%.2f' % float(bestvocffsorted[item]["Rsc"]),'%.2f' % float(bestvocffsorted[item]["Vstart"]),'%.2f' % float(bestvocffsorted[item]["Vend"]),'%.2f' % float(bestvocffsorted[item]["CellSurface"])])
                minJscfind.append(min(bestvocffsorted[item]["IVData"][1]))
                maxcurrentfind.append(max(bestvocffsorted[item]["IVData"][1]))
                minVfind.append(min(bestvocffsorted[item]["IVData"][0]))
                maxVfind.append(max(bestvocffsorted[item]["IVData"][0]))
            ax.set_xlabel('Voltage (mV)')
            ax.set_ylabel('Current density (mA/cm'+'\xb2'+')')
            ax.axhline(y=0, color='k')
            ax.axvline(x=0, color='k')
            x1=min(minVfind)
            x2=max(maxVfind)
            y1=1.1*min(minJscfind)
            if max(maxcurrentfind)>10:
                y2=10
            else:
                y2=max(maxcurrentfind)
            ax.axis([x1,x2,y1,y2])
            handles, labels = ax.get_legend_handles_labels()
            lgd = ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
            fig.savefig(batchname+'_bestvocff.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
            plt.close(fig)
            plt.clf()
            collabel=("Voc","Jsc","FF","Eff","Roc","Rsc","Vstart","Vend","CellSurface")
            nrows, ncols = len(bestvocffsorted)+1, len(collabel)
            hcell, wcell = 0.3, 1.
            hpad, wpad = 0, 0 
            fig=plt.figure(figsize=(ncols*wcell+wpad, nrows*hcell+hpad))
            ax = fig.add_subplot(111)
            rowlabel=tuple(rowlabel)
            the_table = ax.table(cellText=tabledata,colLabels=collabel,rowLabels=rowlabel,loc='center')
            the_table.set_fontsize(18)
            ax.axis('off')
            fig.savefig('bestvocfftable.png',dpi=300,bbox_inches="tight")
            plt.close(fig)
            plt.clf()
            images = list(map(ImageTk.open, [batchname+'_bestvocff.png','bestvocfftable.png']))
            widths, heights = zip(*(i.size for i in images))
            total_width = max(widths)
            max_height = sum(heights)
            new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
            new_im.paste(im=images[0],box=(0,0))
            new_im.paste(im=images[1],box=(0,heights[0]))
            new_im.save(batchname+'_bestvocff.png')
            os.remove('bestvocfftable.png')
            plt.close("all")
            plt.clf()
#            except:
#                print("there's an issue with creating Bestof graphs")

    plt.clf()    
    plt.close("all")    
    if len(samplesgroups)>1:            
        grouplistdict=[]
        for item in range(len(samplesgroups)):
            groupdict={}
            groupdict["Group"]=samplesgroups[item]
            listofthegroup=[]
            listofthegroupNames=[]
            for item1 in range(len(DATAx)):
                if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=="Light":
                    listofthegroup.append(DATAx[item1])
                    listofthegroupNames.append(DATAx[item1]['DepID']+'_'+DATAx[item1]['Cellletter'])
            groupdict["numbCell"]=len(list(set(listofthegroupNames)))
            listofthegroupRev=[]
            listofthegroupFor=[]
            for item1 in range(len(listofthegroup)):
                if listofthegroup[item1]["ScanDirection"]=="Reverse":
                    listofthegroupRev.append(listofthegroup[item1])
                else:
                    listofthegroupFor.append(listofthegroup[item1])
           
            groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
            groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
            groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
            groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
            groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
            groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
            groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
            groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
            
            grouplistdict.append(groupdict)
    plt.close("all")  
    plt.clf()
    if window.ui.checkBox_AAxlsxsummary.isChecked():   
        workbook = xlsxwriter.Workbook(batchname+'_Summary.xlsx')
        
        LandD=DATAx + DATAdark
        timeLandD =sorted(LandD, key=itemgetter('MeasDayTime')) 
        
        if len(samplesgroups)>1:
#                try:
            worksheet = workbook.add_worksheet("GroupStat")
            summary=[]
            for item in range(len(samplesgroups)):
                ncell=1
                if grouplistdict[item]["ForVoc"]!=[]:
                    lengthofgroup=len(grouplistdict[item]["ForVoc"])
                    summary.append([grouplistdict[item]["Group"],grouplistdict[item]["numbCell"],"Forward",lengthofgroup,sum(grouplistdict[item]["ForVoc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["ForVoc"]),sum(grouplistdict[item]["ForJsc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["ForJsc"]),sum(grouplistdict[item]["ForFF"],0.0)/lengthofgroup,np.std(grouplistdict[item]["ForFF"]),sum(grouplistdict[item]["ForEff"],0.0)/lengthofgroup,np.std(grouplistdict[item]["ForEff"])])
                    ncell=0
                if grouplistdict[item]["RevVoc"]!=[]:  
                    if ncell==0:
                        lengthofgroup=len(grouplistdict[item]["RevVoc"])
                        summary.append([grouplistdict[item]["Group"]," ","Reverse",lengthofgroup,sum(grouplistdict[item]["RevVoc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevVoc"]),sum(grouplistdict[item]["RevJsc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevJsc"]),sum(grouplistdict[item]["RevFF"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevFF"]),sum(grouplistdict[item]["RevEff"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevEff"])])
                    else:
                        lengthofgroup=len(grouplistdict[item]["RevVoc"])
                        summary.append([grouplistdict[item]["Group"],grouplistdict[item]["numbCell"],"Reverse",lengthofgroup,sum(grouplistdict[item]["RevVoc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevVoc"]),sum(grouplistdict[item]["RevJsc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevJsc"]),sum(grouplistdict[item]["RevFF"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevFF"]),sum(grouplistdict[item]["RevEff"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevEff"])])

            summary.insert(0, [" ", " "," ", "-", "mV","-","mA/cm2","-","%","-","%","-"])
            summary.insert(0, ["Group","#Cells","Scan Dir.","#ofmeas", "Voc"," ","Jsc"," ","FF"," ","Eff"," "])
            summary.insert(0, [" "," "," "," ", "Avg","StdDev","Avg","StdDev","Avg","StdDev","Avg","StdDev"])
            for item in range(len(summary)):
                for item0 in range(len(summary[item])):
                    worksheet.write(item,item0, str(summary[item][item0]))
            # except:
            #     print("exception: excel summary - groupstat")
    
        if timeLandD!=[]:
            try:
                worksheet = workbook.add_worksheet("AllJVrawdata")
                summary=[]
                for item in range(len(timeLandD)):
                    summary.append([timeLandD[item]["Group"],timeLandD[item]["SampleName"],timeLandD[item]["Cellletter"],timeLandD[item]["MeasDayTime"],timeLandD[item]["CellSurface"],str(timeLandD[item]["Voc"]),str(timeLandD[item]["Jsc"]),str(timeLandD[item]["FF"]),str(timeLandD[item]["Eff"]),str(timeLandD[item]["Pmpp"]),str(timeLandD[item]["Vmpp"]),str(timeLandD[item]["Jmpp"]),str(timeLandD[item]["Roc"]),str(timeLandD[item]["Rsc"]),str(timeLandD[item]["VocFF"]),str(timeLandD[item]["RscJsc"]),str(timeLandD[item]["NbPoints"]),timeLandD[item]["Delay"],timeLandD[item]["IntegTime"],timeLandD[item]["Vstart"],timeLandD[item]["Vend"],timeLandD[item]["Illumination"],timeLandD[item]["ScanDirection"],str('%.2f' % float(timeLandD[item]["ImaxComp"])),timeLandD[item]["Isenserange"],str(timeLandD[item]["AreaJV"]),timeLandD[item]["Operator"],timeLandD[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                for item in range(len(summary)):
                    for item0 in range(len(summary[item])):
                        worksheet.write(item,item0,summary[item][item0])
            except:
                print("exception: excel summary - AllJVrawdata")
        
        if DATAx!=[]:
            try:
                worksheet = workbook.add_worksheet("rawdataLight")
                summary=[]
                for item in range(len(DATAx)):
                    if DATAx[item]["Illumination"]=='Light':
                        summary.append([DATAx[item]["Group"],DATAx[item]["SampleName"],DATAx[item]["Cellletter"],DATAx[item]["MeasDayTime"],DATAx[item]["CellSurface"],str(DATAx[item]["Voc"]),str(DATAx[item]["Jsc"]),str(DATAx[item]["FF"]),str(DATAx[item]["Eff"]),str(DATAx[item]["Pmpp"]),str(DATAx[item]["Vmpp"]),str(DATAx[item]["Jmpp"]),str(DATAx[item]["Roc"]),str(DATAx[item]["Rsc"]),str(DATAx[item]["VocFF"]),str(DATAx[item]["RscJsc"]),str(DATAx[item]["NbPoints"]),str(DATAx[item]["Delay"]),str(DATAx[item]["IntegTime"]),str(DATAx[item]["Vstart"]),str(DATAx[item]["Vend"]),str(DATAx[item]["Illumination"]),str(DATAx[item]["ScanDirection"]),str('%.2f' % float(DATAx[item]["ImaxComp"])),str(DATAx[item]["Isenserange"]),str(DATAx[item]["AreaJV"]),DATAx[item]["Operator"],DATAx[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                for item in range(len(summary)):
                    for item0 in range(len(summary[item])):
                        worksheet.write(item,item0,summary[item][item0])
                worksheet = workbook.add_worksheet("rawdatadark")
                summary=[]
                for item in range(len(DATAx)):
                    if DATAx[item]["Illumination"]=='Dark':
                        summary.append([DATAx[item]["Group"],DATAx[item]["SampleName"],DATAx[item]["Cellletter"],DATAx[item]["MeasDayTime"],DATAx[item]["CellSurface"],str(DATAx[item]["Voc"]),str(DATAx[item]["Jsc"]),str(DATAx[item]["FF"]),str(DATAx[item]["Eff"]),str(DATAx[item]["Pmpp"]),str(DATAx[item]["Vmpp"]),str(DATAx[item]["Jmpp"]),str(DATAx[item]["Roc"]),str(DATAx[item]["Rsc"]),str(DATAx[item]["VocFF"]),str(DATAx[item]["RscJsc"]),str(DATAx[item]["NbPoints"]),str(DATAx[item]["Delay"]),str(DATAx[item]["IntegTime"]),str(DATAx[item]["Vstart"]),str(DATAx[item]["Vend"]),str(DATAx[item]["Illumination"]),str(DATAx[item]["ScanDirection"]),str('%.2f' % float(DATAx[item]["ImaxComp"])),str(DATAx[item]["Isenserange"]),str(DATAx[item]["AreaJV"]),DATAx[item]["Operator"],DATAx[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                for item in range(len(summary)):
                    for item0 in range(len(summary[item])):
                        worksheet.write(item,item0,summary[item][item0])
            except:
                print("exception: excel summary - rawdataLight")
#                if DATAdark!=[]:
#                    worksheet = workbook.add_worksheet("rawdatadark")
#                    summary=[]
#                    for item in range(len(DATAdark)):
#                        summary.append([DATAdark[item]["Group"],DATAdark[item]["SampleName"],DATAdark[item]["Cellletter"],DATAdark[item]["MeasDayTime"],DATAdark[item]["CellSurface"],str(DATAdark[item]["Voc"]),str(DATAdark[item]["Jsc"]),str(DATAdark[item]["FF"]),str(DATAdark[item]["Eff"]),str(DATAdark[item]["Pmpp"]),str(DATAdark[item]["Vmpp"]),str(DATAdark[item]["Jmpp"]),str(DATAdark[item]["Roc"]),str(DATAdark[item]["Rsc"]),str(DATAdark[item]["VocFF"]),str(DATAdark[item]["RscJsc"]),str(DATAdark[item]["NbPoints"]),DATAdark[item]["Delay"],DATAdark[item]["IntegTime"],DATAdark[item]["Vstart"],DATAdark[item]["Vend"],DATAdark[item]["Illumination"],DATAdark[item]["ScanDirection"],str('%.2f' % float(DATAdark[item]["ImaxComp"])),DATAdark[item]["Isenserange"],str(DATAdark[item]["AreaJV"]),DATAdark[item]["Operator"],DATAdark[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
#                    summary.insert(0, ["-", "-", "-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
#                    summary.insert(0, ["Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
#                    for item in range(len(summary)):
#                        for item0 in range(len(summary[item])):
#                            worksheet.write(item,item0,summary[item][item0])
                    
        sorted_bestEff= sorted(bestEff, key=itemgetter('Eff'), reverse=True) 
        if sorted_bestEff!=[]:  
            try:
                worksheet = workbook.add_worksheet("besteff")
                summary=[]
                for item in range(len(sorted_bestEff)):
                    summary.append([sorted_bestEff[item]["Group"],sorted_bestEff[item]["SampleName"],sorted_bestEff[item]["Cellletter"],sorted_bestEff[item]["MeasDayTime"],sorted_bestEff[item]["CellSurface"],str(sorted_bestEff[item]["Voc"]),str(sorted_bestEff[item]["Jsc"]),str(sorted_bestEff[item]["FF"]),str(sorted_bestEff[item]["Eff"]),str(sorted_bestEff[item]["Pmpp"]),str(sorted_bestEff[item]["Vmpp"]),str(sorted_bestEff[item]["Jmpp"]),str(sorted_bestEff[item]["Roc"]),str(sorted_bestEff[item]["Rsc"]),str(sorted_bestEff[item]["VocFF"]),str(sorted_bestEff[item]["RscJsc"]),str(sorted_bestEff[item]["NbPoints"]),sorted_bestEff[item]["Delay"],sorted_bestEff[item]["IntegTime"],sorted_bestEff[item]["Vstart"],sorted_bestEff[item]["Vend"],sorted_bestEff[item]["Illumination"],sorted_bestEff[item]["ScanDirection"],str('%.2f' % float(sorted_bestEff[item]["ImaxComp"])),sorted_bestEff[item]["Isenserange"],str(sorted_bestEff[item]["AreaJV"]),sorted_bestEff[item]["Operator"],sorted_bestEff[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                summary.insert(0, ["-", "-", "-", "-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                for item in range(len(summary)):
                    for item0 in range(len(summary[item])):
                        worksheet.write(item,item0,summary[item][item0])
            except:
                print("exception: excel summary - besteff")
        sorted_bestvocff= sorted(bestvocff, key=itemgetter('VocFF'), reverse=True) 
        if sorted_bestvocff!=[]: 
            try:
                worksheet = workbook.add_worksheet("bestvocff")
                summary=[]
                for item in range(len(sorted_bestvocff)):
                    summary.append([sorted_bestvocff[item]["Group"], sorted_bestvocff[item]["SampleName"],sorted_bestvocff[item]["Cellletter"],sorted_bestvocff[item]["MeasDayTime"],sorted_bestvocff[item]["CellSurface"],str(sorted_bestvocff[item]["Voc"]),str(sorted_bestvocff[item]["Jsc"]),str(sorted_bestvocff[item]["FF"]),str(sorted_bestvocff[item]["Eff"]),str(sorted_bestvocff[item]["Pmpp"]),str(sorted_bestvocff[item]["Vmpp"]),str(sorted_bestvocff[item]["Jmpp"]),str(sorted_bestvocff[item]["Roc"]),str(sorted_bestvocff[item]["Rsc"]),str(sorted_bestvocff[item]["VocFF"]),str(sorted_bestvocff[item]["RscJsc"]),str(sorted_bestvocff[item]["NbPoints"]),sorted_bestvocff[item]["Delay"],sorted_bestvocff[item]["IntegTime"],sorted_bestvocff[item]["Vstart"],sorted_bestvocff[item]["Vend"],sorted_bestvocff[item]["Illumination"],sorted_bestvocff[item]["ScanDirection"],str('%.2f' % float(sorted_bestvocff[item]["ImaxComp"])),sorted_bestvocff[item]["Isenserange"],str(sorted_bestvocff[item]["AreaJV"]),sorted_bestvocff[item]["Operator"],sorted_bestvocff[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                for item in range(len(summary)):
                    for item0 in range(len(summary[item])):
                        worksheet.write(item,item0,summary[item][item0])
            except:
                print("exception: excel summary - bestvocff")
        
        if DATAMPP!=[]: 
            try:
                worksheet = workbook.add_worksheet("Pmpp")
                summary=[]
                for item in range(len(DATAMPP)):
                    summary.append([DATAMPP[item]["Group"],DATAMPP[item]["SampleName"],DATAMPP[item]["Cellletter"],DATAMPP[item]["MeasDayTime"],float('%.2f' % float(DATAMPP[item]["CellSurface"])),DATAMPP[item]["Delay"],DATAMPP[item]["IntegTime"],float(DATAMPP[item]["Vstep"]),float(DATAMPP[item]["Vstart"]),float('%.1f' % float(DATAMPP[item]["MppData"][2][-1])),DATAMPP[item]["Operator"],DATAMPP[item]["MeasComment"]])
                summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Delay","IntegTime","Vstep","Vstart","ExecTime","Operator","MeasComment"])
                for item in range(len(summary)):
                    for item0 in range(len(summary[item])):
                        worksheet.write(item,item0,summary[item][item0])
            except:
                print("exception: excel summary - Pmpp")
        
        if DATAFV!=[]: 
            try:
                worksheet = workbook.add_worksheet("fixedvoltage")
                summary=[]
                for item in range(len(DATAFV)):
                    summary.append([DATAFV[item]["Group"],DATAFV[item]["SampleName"],DATAFV[item]["Cellletter"],DATAFV[item]["MeasDayTime"],float('%.2f' % float(DATAFV[item]["CellSurface"])),DATAFV[item]["Delay"],DATAFV[item]["IntegTime"],DATAFV[item]["NbCycle"],float(DATAFV[item]["Vstep"]),float(DATAFV[item]["ExecTime"]),float(DATAFV[item]["TimeatZero"]),DATAFV[item]["Operator"],DATAFV[item]["MeasComment"]])
                summary.insert(0, ["Group", "Sample Name", "Cell","MeasDayTime","Cell Surface","Delay","IntegTime","NbCycle","Initial voltage step", "Time at voltage bias", "Time at zero", "Operator","MeasComment"])
                for item in range(len(summary)):
                    for item0 in range(len(summary[item])):
                        worksheet.write(item,item0,summary[item][item0])
            except:
                print("exception: excel summary - fixedvoltage")
                
        if LandD!=[]:   
            try:
                sorted_dataall = sorted(LandD, key=itemgetter('DepID')) 
                for key, group in groupby(sorted_dataall, key=lambda x:x['DepID']):
                    partdat=list(group)
                    worksheet = workbook.add_worksheet(key)
                    summary=[]
                    for item in range(len(partdat)):
                        summary.append([partdat[item]["Group"],partdat[item]["SampleName"],partdat[item]["Cellletter"],partdat[item]["MeasDayTime"],partdat[item]["CellSurface"],str(partdat[item]["Voc"]),str(partdat[item]["Jsc"]),str(partdat[item]["FF"]),str(partdat[item]["Eff"]),str(partdat[item]["Pmpp"]),str(partdat[item]["Vmpp"]),str(partdat[item]["Jmpp"]),str(partdat[item]["Roc"]),str(partdat[item]["Rsc"]),str(partdat[item]["VocFF"]),str(partdat[item]["RscJsc"]),str(partdat[item]["NbPoints"]),partdat[item]["Delay"],partdat[item]["IntegTime"],partdat[item]["Vstart"],partdat[item]["Vend"],partdat[item]["Illumination"],partdat[item]["ScanDirection"],str('%.2f' % float(partdat[item]["ImaxComp"])),partdat[item]["Isenserange"],str(partdat[item]["AreaJV"]),partdat[item]["Operator"],partdat[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                    summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                    summary.insert(0, ["Group", "Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
            except:
                print("exception: excel summary - LandD")
                        
        workbook.close()
    
    plt.close("all")
    plt.clf()
            
    if DATAx[0]["Setup"]=="SSIgorC215":
        if window.ui.checkBox_AAstatgraphs.isChecked():
            fig = plt.figure()
            Effsubfig = fig.add_subplot(224)
            Vocsubfig = fig.add_subplot(221)
            Jscsubfig = fig.add_subplot(222)
            FFsubfig = fig.add_subplot(223)
            
            
            eff=[[],[],[],[],[],[]]
            for item in DATAx:
                if item["Illumination"]=='Light':
                    if item["Cellletter"]=="A":
                        eff[0].append(item["Eff"])
                    elif item["Cellletter"]=="B":
                        eff[1].append(item["Eff"]) 
                    elif item["Cellletter"]=="C":
                        eff[2].append(item["Eff"]) 
                    elif item["Cellletter"]=="D":
                        eff[3].append(item["Eff"]) 
                    elif item["Cellletter"]=="E":
                        eff[4].append(item["Eff"]) 
                    elif item["Cellletter"]=="F":
                        eff[5].append(item["Eff"]) 
            names=["A","B","C","D","E","F"]
            for i in range(len(names)):
                y=eff[i]
                if len(y)>0:
                    x=np.random.normal(i+1,0.04,size=len(y))
                    Effsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
            span=range(1,len(names)+1)
            Effsubfig.set_xticks(span)
            Effsubfig.set_xticklabels(names)
            Effsubfig.set_xlim([0.5,span[-1]+0.5])
            Effsubfig.set_ylim([min([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])-1,max([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])+1])
            Effsubfig.set_ylabel('Efficiency (%)')
            
            eff=[[],[],[],[],[],[]]
            for item in DATAx:
                if item["Illumination"]=='Light':
                    if item["Cellletter"]=="A":
                        eff[0].append(item["Voc"])
                    elif item["Cellletter"]=="B":
                        eff[1].append(item["Voc"]) 
                    elif item["Cellletter"]=="C":
                        eff[2].append(item["Voc"]) 
                    elif item["Cellletter"]=="D":
                        eff[3].append(item["Voc"]) 
                    elif item["Cellletter"]=="E":
                        eff[4].append(item["Voc"]) 
                    elif item["Cellletter"]=="F":
                        eff[5].append(item["Voc"]) 
#            names=["A","B","C","D","E","F"]
            for i in range(len(names)):
                y=eff[i]
                if len(y)>0:
                    x=np.random.normal(i+1,0.04,size=len(y))
                    Vocsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
            span=range(1,len(names)+1)
            Vocsubfig.set_xticks(span)
            Vocsubfig.set_xticklabels(names)
            Vocsubfig.set_xlim([0.5,span[-1]+0.5])
            Vocsubfig.set_ylim([min([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])-5,max([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])+5])
            Vocsubfig.set_ylabel('Voc (mV)')
            
            eff=[[],[],[],[],[],[]]
            for item in DATAx:
                if item["Illumination"]=='Light':
                    if item["Cellletter"]=="A":
                        eff[0].append(item["Jsc"])
                    elif item["Cellletter"]=="B":
                        eff[1].append(item["Jsc"]) 
                    elif item["Cellletter"]=="C":
                        eff[2].append(item["Jsc"]) 
                    elif item["Cellletter"]=="D":
                        eff[3].append(item["Jsc"]) 
                    elif item["Cellletter"]=="E":
                        eff[4].append(item["Jsc"]) 
                    elif item["Cellletter"]=="F":
                        eff[5].append(item["Jsc"]) 
#            names=["A","B","C","D","E","F"]
            for i in range(len(names)):
                y=eff[i]
                if len(y)>0:
                    x=np.random.normal(i+1,0.04,size=len(y))
                    Jscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
            span=range(1,len(names)+1)
            Jscsubfig.set_xticks(span)
            Jscsubfig.set_xticklabels(names)
            Jscsubfig.set_xlim([0.5,span[-1]+0.5])
            Jscsubfig.set_ylim([min([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])-5,max([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])+5])
            Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
            
            eff=[[],[],[],[],[],[]]
            for item in DATAx:
                if item["Illumination"]=='Light':
                    if item["Cellletter"]=="A":
                        eff[0].append(item["FF"])
                    elif item["Cellletter"]=="B":
                        eff[1].append(item["FF"]) 
                    elif item["Cellletter"]=="C":
                        eff[2].append(item["FF"]) 
                    elif item["Cellletter"]=="D":
                        eff[3].append(item["FF"]) 
                    elif item["Cellletter"]=="E":
                        eff[4].append(item["FF"]) 
                    elif item["Cellletter"]=="F":
                        eff[5].append(item["FF"]) 
#            names=["A","B","C","D","E","F"]
            for i in range(len(names)):
                y=eff[i]
                if len(y)>0:
                    x=np.random.normal(i+1,0.04,size=len(y))
                    FFsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
            span=range(1,len(names)+1)
            FFsubfig.set_xticks(span)
            FFsubfig.set_xticklabels(names)
            FFsubfig.set_xlim([0.5,span[-1]+0.5])
            FFsubfig.set_ylim([min([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])-5,max([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])+5])
            FFsubfig.set_ylabel('FF (%)')
            
            
            fig.subplots_adjust(wspace=.25)
            fig.savefig(batchname+'_StatCells.png',dpi=300,bbox_inches="tight")
            
            plt.close("all")
            plt.clf()
        
    #stat graphs
    if window.ui.checkBox_AAstatgraphs.isChecked():
        #group
#            try:
        plt.close("all")
        plt.clf()
        if len(samplesgroups)>1:
            fig = plt.figure()
            Effsubfig = fig.add_subplot(224) 
            names=samplesgroups
            valsRev=[]
            for item in names:
                valsRev.append([i["RevEff"] for i in grouplistdict if i["Group"]==item and "RevEff" in i])
            valsFor=[]
            for item in names:
                valsFor.append([i["ForEff"] for i in grouplistdict if i["Group"]==item and "ForEff" in i])
                
            valstot=[]
            Rev=[]
            Forw=[]
            namelist=[]
            for i in range(len(names)):
                if valsRev[i][0]==[] and valsFor[i][0]==[]:
                    print(" ")
                else:
                    Rev.append(valsRev[i][0])
                    Forw.append(valsFor[i][0])
                    valstot.append(valsRev[i][0]+valsFor[i][0])
                    namelist.append(names[i])
            
            Effsubfig.boxplot(valstot,0,'',labels=namelist)
            
            for i in range(len(namelist)):
                y=Rev[i]
                if len(y)>0:
                    x=np.random.normal(i+1,0.04,size=len(y))
                    Effsubfig.scatter(x,y,s=5,color='red', alpha=0.5)
                y=Forw[i]
                if len(y)>0:
                    x=np.random.normal(i+1,0.04,size=len(y))
                    Effsubfig.scatter(x,y,s=5,color='blue', alpha=0.5)  
            
            #Effsubfig.set_xlabel('Red=reverse; Blue=forward')
            
            Effsubfig.set_ylabel('Efficiency (%)')
            for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                          Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                item.set_fontsize(4)
            
            Vocsubfig = fig.add_subplot(221) 
            names=samplesgroups
            valsRev=[]
            for item in names:
                valsRev.append([i["RevVoc"] for i in grouplistdict if i["Group"]==item and "RevVoc" in i])
            valsFor=[]
            for item in names:
                valsFor.append([i["ForVoc"] for i in grouplistdict if i["Group"]==item and "ForVoc" in i])
                
            valstot=[]
            Rev=[]
            Forw=[]
            namelist=[]
            for i in range(len(names)):
                if valsRev[i][0]==[] and valsFor[i][0]==[]:
                    print(" ")
                else:
                    Rev.append(valsRev[i][0])
                    Forw.append(valsFor[i][0])
                    valstot.append(valsRev[i][0]+valsFor[i][0])
                    namelist.append(names[i])
            
            Vocsubfig.boxplot(valstot,0,'',labels=namelist)
            
            for i in range(len(namelist)):
                y=Rev[i]
                if len(y)>0:
                    x=np.random.normal(i+1,0.04,size=len(y))
                    Vocsubfig.scatter(x,y,s=5,color='red', alpha=0.5)
                y=Forw[i]
                if len(y)>0:
                    x=np.random.normal(i+1,0.04,size=len(y))
                    Vocsubfig.scatter(x,y,s=5,color='blue', alpha=0.5)  
            
            #Vocsubfig.set_xlabel('Red=reverse; Blue=forward')
            
            Vocsubfig.set_ylabel('Voc (mV)')
            for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                          Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                item.set_fontsize(4)
                
            Jscsubfig = fig.add_subplot(222) 
            names=samplesgroups
            valsRev=[]
            for item in names:
                valsRev.append([i["RevJsc"] for i in grouplistdict if i["Group"]==item and "RevJsc" in i])
            valsFor=[]
            for item in names:
                valsFor.append([i["ForJsc"] for i in grouplistdict if i["Group"]==item and "ForJsc" in i])
                
            valstot=[]
            Rev=[]
            Forw=[]
            namelist=[]
            for i in range(len(names)):
                if valsRev[i][0]==[] and valsFor[i][0]==[]:
                    print(" ")
                else:
                    Rev.append(valsRev[i][0])
                    Forw.append(valsFor[i][0])
                    valstot.append(valsRev[i][0]+valsFor[i][0])
                    namelist.append(names[i])
            
            Jscsubfig.boxplot(valstot,0,'',labels=namelist)
            
            for i in range(len(namelist)):
                y=Rev[i]
                if len(y)>0:
                    x=np.random.normal(i+1,0.04,size=len(y))
                    Jscsubfig.scatter(x,y,s=5,color='red', alpha=0.5)
                y=Forw[i]
                if len(y)>0:
                    x=np.random.normal(i+1,0.04,size=len(y))
                    Jscsubfig.scatter(x,y,s=5,color='blue', alpha=0.5)  
            
            #Jscsubfig.set_xlabel('Red=reverse; Blue=forward')
            
            Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
            for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                          Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                item.set_fontsize(4)
            
            FFsubfig = fig.add_subplot(223) 
            names=samplesgroups
            valsRev=[]
            for item in names:
                valsRev.append([i["RevFF"] for i in grouplistdict if i["Group"]==item and "RevFF" in i])
            valsFor=[]
            for item in names:
                valsFor.append([i["ForFF"] for i in grouplistdict if i["Group"]==item and "ForFF" in i])
                
            valstot=[]
            Rev=[]
            Forw=[]
            namelist=[]
            for i in range(len(names)):
                if valsRev[i][0]==[] and valsFor[i][0]==[]:
                    print(" ")
                else:
                    Rev.append(valsRev[i][0])
                    Forw.append(valsFor[i][0])
                    valstot.append(valsRev[i][0]+valsFor[i][0])
                    namelist.append(names[i])
            
            FFsubfig.boxplot(valstot,0,'',labels=namelist)
            
            for i in range(len(namelist)):
                y=Rev[i]
                if len(y)>0:
                    x=np.random.normal(i+1,0.04,size=len(y))
                    FFsubfig.scatter(x,y,s=5,color='red', alpha=0.5)
                y=Forw[i]
                if len(y)>0:
                    x=np.random.normal(i+1,0.04,size=len(y))
                    FFsubfig.scatter(x,y,s=5,color='blue', alpha=0.5)  
            
            #FFsubfig.set_xlabel('Red=reverse; Blue=forward')
            
            FFsubfig.set_ylabel('FF (%)')
            for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                          FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                item.set_fontsize(4)
                
            FFsubfig.annotate('Red=reverse; Blue=forward', xy=(1.3,-0.2), xycoords='axes fraction', fontsize=4,
                        horizontalalignment='right', verticalalignment='bottom')
            annotation="#ofCells: "
            for item in range(len(samplesgroups)):
                if samplesgroups[item] in namelist:
                    annotation+=samplesgroups[item]+"=>"+str(grouplistdict[item]["numbCell"])+"; "
            FFsubfig.annotate(annotation, xy=(0,-0.3), xycoords='axes fraction', fontsize=4,
                        horizontalalignment='left', verticalalignment='bottom')
            
            fig.subplots_adjust(wspace=.25)
            fig.savefig(batchname+'_StatGroupgraph.png',dpi=300,bbox_inches="tight")
            
            
            
            plt.close("all")
        plt.clf()
#            except:
#                print("Exception: statgraphs - group")
        
        #time
        if DATAx[0]["Setup"]=="TFIV" or DATAx[0]["Setup"]=='SSIgorC215':
            try: 
                if DATAx[0]["Setup"]=="TFIV":
                    time=[float(i["MeasDayTime"].split()[1].split(':')[0])+ float(i["MeasDayTime"].split()[1].split(':')[1])/60 + float(i["MeasDayTime"].split()[1].split(':')[2])/3600 for i in DATAx if i["Illumination"]=="Light"]
                elif DATAx[0]["Setup"]=='SSIgorC215':
                    time=[]
                    for i in DATAx:
                        if i["Illumination"]=="Light":
                            if i["MeasDayTime"].split(' ')[-1]=='PM' and float(i["MeasDayTime"].split(' ')[-2].split(':')[0])!=12: 
                                time.append(float(i["MeasDayTime"].split(' ')[-2].split(':')[0])+12+ float(i["MeasDayTime"].split(' ')[-2].split(':')[1])/60 + float(i["MeasDayTime"].split(' ')[-2].split(':')[2])/3600)
                            else:
                                time.append(float(i["MeasDayTime"].split(' ')[-2].split(':')[0])+ float(i["MeasDayTime"].split(' ')[-2].split(':')[1])/60 + float(i["MeasDayTime"].split(' ')[-2].split(':')[2])/3600)
                                       
                Voct=[i["Voc"] for i in DATAx if i["Illumination"]=="Light"]
                Jsct=[i["Jsc"] for i in DATAx if i["Illumination"]=="Light"]
                FFt=[i["FF"] for i in DATAx if i["Illumination"]=="Light"]
                Efft=[i["Eff"] for i in DATAx if i["Illumination"]=="Light"]
                
                fig = plt.figure()
                Vocsubfig = fig.add_subplot(221) 
                Vocsubfig.scatter(time, Voct, s=5, c='k', alpha=0.5)
                Vocsubfig.set_ylabel('Voc (mV)')
                for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                              Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Vocsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                Jscsubfig = fig.add_subplot(222) 
                Jscsubfig.scatter(time, Jsct, s=5, c='k', alpha=0.5)
                Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                              Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Jscsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                FFsubfig = fig.add_subplot(223) 
                FFsubfig.scatter(time, FFt, s=5, c='k', alpha=0.5)
                FFsubfig.set_xlabel('Time')
                FFsubfig.set_ylabel('FF (%)')
                for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                              FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                FFsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                Effsubfig = fig.add_subplot(224) 
                Effsubfig.scatter(time, Efft, s=5, c='k', alpha=0.5)
                Effsubfig.set_xlabel('Time')
                Effsubfig.set_ylabel('Eff (%)')
                for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                              Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Effsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                fig.subplots_adjust(wspace=.25)
                fig.savefig(batchname+'_StatTimegraph.png',dpi=300,bbox_inches="tight")
                plt.close("all")
            except:
                print("Exception: statgraph - time")
        plt.clf()
        
        #Resistances
        try:
            Rsclist=[float(i["Rsc"]) for i in DATAx]
            Roclist=[float(i["Roc"]) for i in DATAx]
            Voct=[i["Voc"] for i in DATAx]
            Jsct=[i["Jsc"] for i in DATAx]
            FFt=[i["FF"] for i in DATAx]
            Efft=[i["Eff"] for i in DATAx]
            
            
            fig = plt.figure()
            Vocsubfig = fig.add_subplot(221) 
            Vocsubfig.scatter(Rsclist, Voct, s=5, c='k', alpha=0.5)
            Vocsubfig.set_ylabel('Voc (mV)')
            for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                          Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                item.set_fontsize(8)
            #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
            Vocsubfig.set_xlim(left=0)
            Vocsubfig.set_ylim(bottom=0)
            Vocsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
            
            
            Jscsubfig = fig.add_subplot(222) 
            Jscsubfig.scatter(Rsclist, Jsct, s=5, c='k', alpha=0.5)
            Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
            for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                          Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                item.set_fontsize(8)
            #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
            Jscsubfig.set_xlim(left=0)
            Jscsubfig.set_ylim(bottom=0)
            Jscsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
            
            FFsubfig = fig.add_subplot(223) 
            FFsubfig.scatter(Rsclist, FFt, s=5, c='k', alpha=0.5)
            FFsubfig.set_xlabel('Rsc')
            FFsubfig.set_ylabel('FF (%)')
            for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                          FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                item.set_fontsize(8)
            #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
            FFsubfig.set_xlim(left=0)
            FFsubfig.set_ylim(bottom=0)
            FFsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
            
            Effsubfig = fig.add_subplot(224) 
            Effsubfig.scatter(Rsclist, Efft, s=5, c='k', alpha=0.5)
            Effsubfig.set_xlabel('Rsc')
            Effsubfig.set_ylabel('Eff (%)')
            for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                          Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                item.set_fontsize(8)
            #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
            Effsubfig.set_xlim(left=0)
            Effsubfig.set_ylim(bottom=0)
            Effsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
            
            fig.subplots_adjust(wspace=.3)
            fig.savefig(batchname+'_StatRscgraph.png',dpi=300,bbox_inches="tight")
            plt.close("all")
            
            
            fig = plt.figure()
            Vocsubfig = fig.add_subplot(221) 
            Vocsubfig.scatter(Roclist, Voct, s=5, c='k', alpha=0.5)
            Vocsubfig.set_ylabel('Voc (mV)')
            for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                          Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                item.set_fontsize(8)
            #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
            Vocsubfig.set_xlim(left=0)
            Vocsubfig.set_ylim(bottom=0)
            Vocsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
            
            Jscsubfig = fig.add_subplot(222) 
            Jscsubfig.scatter(Roclist, Jsct, s=5, c='k', alpha=0.5)
            Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
            for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                          Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                item.set_fontsize(8)
            #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
            Jscsubfig.set_xlim(left=0)
            Jscsubfig.set_ylim(bottom=0)
            Jscsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
            
            FFsubfig = fig.add_subplot(223) 
            FFsubfig.scatter(Roclist, FFt, s=5, c='k', alpha=0.5)
            FFsubfig.set_xlabel('Roc')
            FFsubfig.set_ylabel('FF (%)')
            for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                          FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                item.set_fontsize(8)
            #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
            FFsubfig.set_xlim(left=0)
            FFsubfig.set_ylim(bottom=0)
            FFsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
            
            Effsubfig = fig.add_subplot(224) 
            Effsubfig.scatter(Roclist, Efft, s=5, c='k', alpha=0.5)
            Effsubfig.set_xlabel('Roc')
            Effsubfig.set_ylabel('Eff (%)')
            for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                          Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                item.set_fontsize(8)
            #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
            Effsubfig.set_xlim(left=0)
            Effsubfig.set_ylim(bottom=0)
            Effsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
            
            fig.subplots_adjust(wspace=.3)
            fig.savefig(batchname+'_StatRocgraph.png',dpi=300,bbox_inches="tight")
            plt.close("all")
            plt.clf()
        except:
            print("Exception: statgraph - resistance")
        
        #stat graph with diff colors for ABC and Forw Rev, by substrate
        #get substrate number without run number
        if DATAx[0]["Setup"]=="TFIV" or DATAx[0]["Setup"]=='SSIgorC215':
            try:
                fig = plt.figure()
                
                VocAFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                VocAFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                VocBFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                VocBFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                VocCFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                VocCFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                VocDFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                VocDFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                VocEFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                VocEFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                VocFFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                VocFFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                VocARy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                VocARx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                VocBRy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                VocBRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                VocCRy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                VocCRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                VocDRy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                VocDRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                VocERy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                VocERx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                VocFRy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                VocFRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                Vocsubfig = fig.add_subplot(221) 
                Vocsubfig.scatter(VocAFx, VocAFy, s=5, facecolors='none', edgecolors='r', lw=0.5)
                Vocsubfig.scatter(VocBFx, VocBFy, s=5, facecolors='none', edgecolors='g', lw=0.5)
                Vocsubfig.scatter(VocCFx, VocCFy, s=5, facecolors='none', edgecolors='b', lw=0.5)
                Vocsubfig.scatter(VocARx, VocARy, s=5, facecolors='r', edgecolors='r', lw=0.5)
                Vocsubfig.scatter(VocBRx, VocBRy, s=5, facecolors='g', edgecolors='g', lw=0.5)
                Vocsubfig.scatter(VocCRx, VocCRy, s=5, facecolors='b', edgecolors='b', lw=0.5)
                Vocsubfig.scatter(VocDFx, VocDFy, s=5, facecolors='none', edgecolors='c', lw=0.5)
                Vocsubfig.scatter(VocEFx, VocEFy, s=5, facecolors='none', edgecolors='m', lw=0.5)
                Vocsubfig.scatter(VocFFx, VocFFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
                Vocsubfig.scatter(VocDRx, VocDRy, s=5, facecolors='c', edgecolors='c', lw=0.5)
                Vocsubfig.scatter(VocERx, VocERy, s=5, facecolors='m', edgecolors='m', lw=0.5)
                Vocsubfig.scatter(VocFRx, VocFRy, s=5, facecolors='k', edgecolors='k', lw=0.5)
                
#                    Vocsubfig.scatter(VocSFx, VocSFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
#                    Vocsubfig.scatter(VocSRx, VocSRy, s=5, edgecolors='k', lw=0.5)
                Vocsubfig.set_ylabel('Voc (mV)')
                Vocsubfig.set_xlabel("Sample #")
                for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] + Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                    item.set_fontsize(4)
                Vocsubfig.set_ylim(bottom=0)
                Vocsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                Vocsubfig.set_xticks(np.arange(float(min(VocAFx+VocBFx+VocCFx+VocARx+VocBRx+VocCRx+VocDFx+VocEFx+VocFFx+VocDRx+VocERx+VocFRx))-0.5,float(max(VocAFx+VocBFx+VocCFx+VocARx+VocBRx+VocCRx+VocDFx+VocEFx+VocFFx+VocDRx+VocERx+VocFRx))+0.5,1), minor=True)
                #Vocsubfig.set_xticks(np.arange(float(min(VocAFx))-0.5,float(max(VocAFx))+0.5,1), minor=True)
                Vocsubfig.xaxis.grid(False, which='major')
                Vocsubfig.xaxis.grid(True, which='minor', color='k', linestyle='-', alpha=0.2)
                
                Vocsubfig.axis([float(min(VocAFx+VocBFx+VocCFx+VocARx+VocBRx+VocCRx+VocDFx+VocEFx+VocFFx+VocDRx+VocERx+VocFRx))-0.5,float(max(VocAFx+VocBFx+VocCFx+VocARx+VocBRx+VocCRx+VocDFx+VocEFx+VocFFx+VocDRx+VocERx+VocFRx))+0.5,0.5*float(min(VocAFy+VocBFy+VocCFy+VocARy+VocBRy+VocCRy+VocDFy+VocEFy+VocFFy+VocDRy+VocERy+VocFRy)),1.1*float(max(VocAFy+VocBFy+VocCFy+VocARy+VocBRy+VocCRy+VocDFy+VocEFy+VocFFy+VocDRy+VocERy+VocFRy))])
                for axis in ['top','bottom','left','right']:
                  Vocsubfig.spines[axis].set_linewidth(0.5)
                Vocsubfig.tick_params(axis='x', which='both',bottom='off', top='off')
                
                
                
                JscAFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                JscAFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                JscBFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                JscBFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                JscCFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                JscCFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                JscARy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                JscARx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                JscBRy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                JscBRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                JscCRy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                JscCRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]

                JscDFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                JscDFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                JscEFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                JscEFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                JscFFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                JscFFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                JscDRy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                JscDRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                JscERy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                JscERx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                JscFRy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                JscFRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]                    
                
                Jscsubfig = fig.add_subplot(222) 
                Jscsubfig.scatter(JscAFx, JscAFy, s=5, facecolors='none', edgecolors='r', lw=0.5)
                Jscsubfig.scatter(JscBFx, JscBFy, s=5, facecolors='none', edgecolors='g', lw=0.5)
                Jscsubfig.scatter(JscCFx, JscCFy, s=5, facecolors='none', edgecolors='b', lw=0.5)
                Jscsubfig.scatter(JscARx, JscARy, s=5, facecolors='r', edgecolors='r', lw=0.5)
                Jscsubfig.scatter(JscBRx, JscBRy, s=5, facecolors='g', edgecolors='g', lw=0.5)
                Jscsubfig.scatter(JscCRx, JscCRy, s=5, facecolors='b', edgecolors='b', lw=0.5)
                Jscsubfig.scatter(JscDFx, JscDFy, s=5, facecolors='none', edgecolors='c', lw=0.5)
                Jscsubfig.scatter(JscEFx, JscEFy, s=5, facecolors='none', edgecolors='m', lw=0.5)
                Jscsubfig.scatter(JscFFx, JscFFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
                Jscsubfig.scatter(JscDRx, JscDRy, s=5, facecolors='c', edgecolors='c', lw=0.5)
                Jscsubfig.scatter(JscERx, JscERy, s=5, facecolors='m', edgecolors='m', lw=0.5)
                Jscsubfig.scatter(JscFRx, JscFRy, s=5, facecolors='k', edgecolors='k', lw=0.5)
                
                Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                Jscsubfig.set_xlabel("Sample #")
                for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                              Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                    item.set_fontsize(4)
                Jscsubfig.set_ylim(bottom=0)
                Jscsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                Jscsubfig.set_xticks(np.arange(float(min(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))-0.5,float(max(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))+0.5,1), minor=True)
                #Jscsubfig.set_xticks(np.arange(float(min(JscAFx))-0.5,float(max(JscAFx))+0.5,1), minor=True)
                Jscsubfig.xaxis.grid(False, which='major')
                Jscsubfig.xaxis.grid(True, which='minor', color='k', linestyle='-', alpha=0.2)
                
                Jscsubfig.axis([float(min(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))-0.5,float(max(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))+0.5,0.5*float(min(JscAFy+JscBFy+JscCFy+JscARy+JscBRy+JscCRy+JscDFy+JscEFy+JscFFy+JscDRy+JscERy+JscFRy)),1.1*float(max(JscAFy+JscBFy+JscCFy+JscARy+JscBRy+JscCRy+JscDFy+JscEFy+JscFFy+JscDRy+JscERy+JscFRy))])
#                    print([float(min(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))-0.5,float(max(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))+0.5,0.5*float(min(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx)),1.1*float(max(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))])
                for axis in ['top','bottom','left','right']:
                  Jscsubfig.spines[axis].set_linewidth(0.5)
                Jscsubfig.tick_params(axis='x', which='both',bottom='off', top='off')
                
                
                FFAFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                FFAFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                FFBFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                FFBFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                FFCFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                FFCFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                FFARy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                FFARx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                FFBRy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                FFBRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                FFCRy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                FFCRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]

                FFDFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                FFDFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                FFEFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                FFEFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                FFFFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                FFFFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                FFDRy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                FFDRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                FFERy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                FFERx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                FFFRy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                FFFRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]                    
                
                FFsubfig = fig.add_subplot(223) 
                FFsubfig.scatter(FFAFx, FFAFy, s=5, facecolors='none', edgecolors='r', lw=0.5)
                FFsubfig.scatter(FFBFx, FFBFy, s=5, facecolors='none', edgecolors='g', lw=0.5)
                FFsubfig.scatter(FFCFx, FFCFy, s=5, facecolors='none', edgecolors='b', lw=0.5)
                FFsubfig.scatter(FFARx, FFARy, s=5, facecolors='r', edgecolors='r', lw=0.5)
                FFsubfig.scatter(FFBRx, FFBRy, s=5, facecolors='g', edgecolors='g', lw=0.5)
                FFsubfig.scatter(FFCRx, FFCRy, s=5, facecolors='b', edgecolors='b', lw=0.5)
                FFsubfig.scatter(FFDFx, FFDFy, s=5, facecolors='none', edgecolors='c', lw=0.5)
                FFsubfig.scatter(FFEFx, FFEFy, s=5, facecolors='none', edgecolors='m', lw=0.5)
                FFsubfig.scatter(FFFFx, FFFFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
                FFsubfig.scatter(FFDRx, FFDRy, s=5, facecolors='c', edgecolors='c', lw=0.5)
                FFsubfig.scatter(FFERx, FFERy, s=5, facecolors='m', edgecolors='m', lw=0.5)
                FFsubfig.scatter(FFFRx, FFFRy, s=5, facecolors='k', edgecolors='k', lw=0.5)
                
                FFsubfig.set_ylabel('FF (%)')
                FFsubfig.set_xlabel("Sample #")
                for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                              FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                    item.set_fontsize(4)
                FFsubfig.set_ylim(bottom=0)
                FFsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                FFsubfig.set_xticks(np.arange(float(min(FFAFx+FFBFx+FFCFx+FFARx+FFBRx+FFCRx+FFDFx+FFEFx+FFFFx+FFDRx+FFERx+FFFRx))-0.5,float(max(FFAFx+FFBFx+FFCFx+FFARx+FFBRx+FFCRx+FFDFx+FFEFx+FFFFx+FFDRx+FFERx+FFFRx))+0.5,1), minor=True)
                #FFsubfig.set_xticks(np.arange(float(min(FFAFx))-0.5,float(max(FFAFx))+0.5,1), minor=True)
                FFsubfig.xaxis.grid(False, which='major')
                FFsubfig.xaxis.grid(True, which='minor', color='k', linestyle='-', alpha=0.2)
                
                FFsubfig.axis([float(min(FFAFx+FFBFx+FFCFx+FFARx+FFBRx+FFCRx+FFDFx+FFEFx+FFFFx+FFDRx+FFERx+FFFRx))-0.5,float(max(FFAFx+FFBFx+FFCFx+FFARx+FFBRx+FFCRx+FFDFx+FFEFx+FFFFx+FFDRx+FFERx+FFFRx))+0.5,0.5*float(min(FFAFy+FFBFy+FFCFy+FFARy+FFBRy+FFCRy+FFDFy+FFEFy+FFFFy+FFDRy+FFERy+FFFRy)),1.1*float(max(FFAFy+FFBFy+FFCFy+FFARy+FFBRy+FFCRy+FFDFy+FFEFy+FFFFy+FFDRy+FFERy+FFFRy))])
                for axis in ['top','bottom','left','right']:
                  FFsubfig.spines[axis].set_linewidth(0.5)
                FFsubfig.tick_params(axis='x', which='both',bottom='off', top='off')
                
                
                EffAFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                EffAFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                EffBFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                EffBFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                EffCFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                EffCFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                EffARy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                EffARx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                EffBRy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                EffBRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                EffCRy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                EffCRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                EffDFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                EffDFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                EffEFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                EffEFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                EffFFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                EffFFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                
                EffDRy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                EffDRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                EffERy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                EffERx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                EffFRy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                EffFRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                
                Effsubfig = fig.add_subplot(224) 
                Effsubfig.scatter(EffAFx, EffAFy, s=5, facecolors='none', edgecolors='r', lw=0.5)
                Effsubfig.scatter(EffBFx, EffBFy, s=5, facecolors='none', edgecolors='g', lw=0.5)
                Effsubfig.scatter(EffCFx, EffCFy, s=5, facecolors='none', edgecolors='b', lw=0.5)
                Effsubfig.scatter(EffARx, EffARy, s=5, facecolors='r', edgecolors='r', lw=0.5)
                Effsubfig.scatter(EffBRx, EffBRy, s=5, facecolors='g', edgecolors='g', lw=0.5)
                Effsubfig.scatter(EffCRx, EffCRy, s=5, facecolors='b', edgecolors='b', lw=0.5)
                Effsubfig.scatter(EffDFx, EffDFy, s=5, facecolors='none', edgecolors='c', lw=0.5)
                Effsubfig.scatter(EffEFx, EffEFy, s=5, facecolors='none', edgecolors='m', lw=0.5)
                Effsubfig.scatter(EffFFx, EffFFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
                Effsubfig.scatter(EffDRx, EffDRy, s=5, facecolors='c', edgecolors='c', lw=0.5)
                Effsubfig.scatter(EffERx, EffERy, s=5, facecolors='m', edgecolors='m', lw=0.5)
                Effsubfig.scatter(EffFRx, EffFRy, s=5, facecolors='k', edgecolors='k', lw=0.5)
                Effsubfig.set_ylabel('Eff (%)')
                Effsubfig.set_xlabel("Sample #")
                for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                              Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                    item.set_fontsize(4)
                Effsubfig.set_ylim(bottom=0)
                Effsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                Effsubfig.set_xticks(np.arange(float(min(EffAFx+EffBFx+EffCFx+EffARx+EffBRx+EffCRx+EffDFx+EffEFx+EffFFx+EffDRx+EffERx+EffFRx))-0.5,float(max(EffAFx+EffBFx+EffCFx+EffARx+EffBRx+EffCRx+EffDFx+EffEFx+EffFFx+EffDRx+EffERx+EffFRx))+0.5,1), minor=True)
                Effsubfig.xaxis.grid(False, which='major')
                Effsubfig.xaxis.grid(True, which='minor', color='k', linestyle='-', alpha=0.2)
                
                Effsubfig.axis([float(min(EffAFx+EffBFx+EffCFx+EffARx+EffBRx+EffCRx+EffDFx+EffEFx+EffFFx+EffDRx+EffERx+EffFRx))-0.5,float(max(EffAFx+EffBFx+EffCFx+EffARx+EffBRx+EffCRx+EffDFx+EffEFx+EffFFx+EffDRx+EffERx+EffFRx))+0.5,0.5*float(min(EffAFy+EffBFy+EffCFy+EffARy+EffBRy+EffCRy+EffDFy+EffEFy+EffFFy+EffDRy+EffERy+EffFRy)),1.1*float(max(EffAFy+EffBFy+EffCFy+EffARy+EffBRy+EffCRy+EffDFy+EffEFy+EffFFy+EffDRy+EffERy+EffFRy))])
                for axis in ['top','bottom','left','right']:
                  Effsubfig.spines[axis].set_linewidth(0.5)
                Effsubfig.tick_params(axis='x', which='both',bottom='off', top='off')
                
                
                FFsubfig.annotate('Red=A; Green=B; Blue=C; Cyan=D; Magenta=E; Black=F; empty=Forward; full=Reverse;', xy=(1.55,-0.3), xycoords='axes fraction', fontsize=4,
                                horizontalalignment='right', verticalalignment='bottom')
                
                fig.savefig(batchname+'_StatJVgraph.png',dpi=300,bbox_inches="tight")
                plt.close("all")
                plt.clf()
            except:
                print("Exception: statgraph - bysubstrate")
                
    plt.close("all")
    plt.close(fig)
    plt.close(fig1) 
    
    if window.ui.checkBox_AAstatgraphs.isChecked():
        try:
            images = list(map(ImageTk.open, [batchname+'_StatCells.png',batchname+'_StatTimegraph.png',batchname+'_StatJVgraph.png',batchname+'_StatGroupgraph.png']))
            widths, heights = zip(*(i.size for i in images))
            total_width = max(widths[0]+widths[2],widths[1]+widths[3])
            max_height = max(heights[0]+heights[1],heights[2]+heights[3])
            new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
            new_im.paste(im=images[0],box=(0,0))
            new_im.paste(im=images[1],box=(0,max(heights[0],heights[2])))
            new_im.paste(im=images[2],box=(max(widths[0],widths[1]),0))
            new_im.paste(im=images[3],box=(max(widths[0],widths[1]),max(heights[0],heights[2])))
            new_im.save(batchname+'_controls.png')
        except:
            images = list(map(ImageTk.open, [batchname+'_StatCells.png',batchname+'_StatTimegraph.png',batchname+'_StatJVgraph.png']))
            widths, heights = zip(*(i.size for i in images))
            total_width = max(widths[0]+widths[2],2*widths[1])
            max_height = max(heights[0]+heights[1],2*heights[2])
            new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
            new_im.paste(im=images[0],box=(0,0))
            new_im.paste(im=images[1],box=(0,max(heights[0],heights[2])))
            new_im.paste(im=images[2],box=(max(widths[0],widths[1]),0))
            new_im.save(batchname+'_controls.png')
                
    QMessageBox.information('Information', 'autoanalysis is finished')

#%%#############
# self.getdatalistsfromIVTFfiles(file_pathnew)
# self.getdatalistsfromIVHITfiles(file_path)

# self.getdatalistsfromNRELcigssetup(file_path)


class Thread_getdatalistsfromCUBpyfiles(QThread):
    finished = pyqtSignal()
    change_value = pyqtSignal(int)
    def __init__(self, file_path, parent=None):
        QThread.__init__(self, parent)
        self.file_path=file_path
        
    def run(self):
        global DATA, DATAdark, colorstylelist
        global DATAMPP, numbLightfiles, numbDarkfiles, colormapname
        print('threadstart')
        
        for i in range(len(self.file_path)):
            filetoread = open(self.file_path[i],"r", encoding='ISO-8859-1')
            filerawdata = filetoread.readlines()
            # print(i)
            filetype = 0
            partdict = {}
            partdict["filepath"]=self.file_path[i]
            filename=os.path.splitext(os.path.basename(partdict["filepath"]))[0]
            
            if "MPPT" in filename:
                filetype = 2
                num_plots=len(DATAMPP.keys())+len(file_path)
                cmap = plt.get_cmap(colormapname)
                colors = cmap(np.linspace(0, 1.0, num_plots))
                colors=[tuple(item) for item in colors]
            else:
                filetype = 1 
                num_plots=len(DATA.keys())+len(file_path)
                cmap = plt.get_cmap(colormapname)
                colors = cmap(np.linspace(0, 1.0, num_plots))
                colors=[tuple(item) for item in colors]
            
            if filetype ==1 : #J-V files from CUBoulder python software
                partdict["DepID"]=filename[:filename.index('pX')-1]
                aftername=filename[filename.index('pX'):]
                
                partdict["Cellletter"]=aftername.split('_')[0][2:]
                partdict["batchname"]=partdict["DepID"].split('_')[0]
                partdict["SampleName"]=partdict["DepID"]+"_"+partdict["Cellletter"]+"_"+aftername.split('_')[4]
                # print(partdict["SampleName"])
                if "_lt_" in aftername:
                    partdict["Illumination"]="Light"
                else:
                    partdict["Illumination"]="Dark"
                    
                if "_rev_" in aftername:
                    partdict["ScanDirection"]="Reverse"
                else:
                    partdict["ScanDirection"]="Forward" 
                
                for item in range(len(filerawdata)):
                    if "DateTime:" in filerawdata[item]:
                        partdict["MeasDayTime2"]=parser.parse(filerawdata[item][10:-1])
                        partdict["MeasDayTime"]=filerawdata[item][10:-1]
                        # print(partdict["MeasDayTime2"])
#                        print(partdict["MeasDayTime"].split(' ')[-2])
                        break
                for item in range(len(filerawdata)):
                    if "#sun:" in filerawdata[item]:
                        partdict["sunintensity"]=float(filerawdata[item][6:-1])
                        break
                partdict["MeasComment"]="-"
                for item in range(len(filerawdata)):
                    if "Comment: " in filerawdata[item]:
                        partdict["MeasComment"]=filerawdata[item][9:-1]
                        break
                if "aftermpp" in partdict["MeasComment"]:
                    partdict["aftermpp"]=1
                else:
                    partdict["aftermpp"]=0
                for item in range(len(filerawdata)):
                    if "minvoltage:" in filerawdata[item]:
                        partdict["Vstart"]=float(filerawdata[item][12:-1])
                        break
                for item in range(len(filerawdata)):
                    if "maxvoltage:" in filerawdata[item]:
                        partdict["Vend"]=float(filerawdata[item][12:-1])
                        break
                if partdict["ScanDirection"]=="Reverse":
                    if partdict["Vstart"]<partdict["Vend"]:
                        vend=partdict["Vend"]
                        partdict["Vend"]=partdict["Vstart"]
                        partdict["Vstart"]=vend
                else:
                    if partdict["Vstart"]>partdict["Vend"]:
                        vend=partdict["Vend"]
                        partdict["Vend"]=partdict["Vstart"]
                        partdict["Vstart"]=vend 
                for item in range(len(filerawdata)):
                    if "JVstepsize:" in filerawdata[item]:
                        partdict["NbPoints"]=abs(partdict["Vend"]-partdict["Vstart"])/float(filerawdata[item][12:-1])
                        break    
                for item in range(len(filerawdata)):
                    if "PixArea:" in filerawdata[item]:
                        partdict["CellSurface"]=float(filerawdata[item][9:-1])
                        #print(partdict["CellSurface"])
                        break
                for item in range(len(filerawdata)):
                    if "delaypoints:" in filerawdata[item]:
                        partdict["Delay"]=float(filerawdata[item][13:-1])
                        break
                for item in range(len(filerawdata)):
                    if "integtime:" in filerawdata[item]:
                        partdict["IntegTime"]=float(filerawdata[item][11:-1])
                        break
                for item in range(len(filerawdata)):
                    if "#IV data" in filerawdata[item]:
                            pos=item+2
                            break
                        
                ivpartdat = [[],[]]#[voltage,current]
                for item in range(pos,len(filerawdata),1):
                    try:
                        ivpartdat[0].append(float(filerawdata[item].split("\t")[0]))
                        ivpartdat[1].append(float(filerawdata[item].split("\t")[1]))
                    except:
                        break
                partdict["IVData"]=ivpartdat
                # params=extract_jv_params(partdict["IVData"])
                for item in range(len(filerawdata)):
                    if "#IV results" in filerawdata[item]:
                        partdict["Voc"]=float(filerawdata[item+2][4:-1]) #mV
                        partdict["Jsc"]=float(filerawdata[item+4][4:-1]) #mA/cm2
                        partdict["Isc"]=float(filerawdata[item+5][4:-1])
                        partdict["FF"]=float(filerawdata[item+3][3:-1]) #%
                        partdict["Eff"]=float(filerawdata[item+1][4:-1])#%
                        partdict["Pmpp"]=float(filerawdata[item+6][5:-1]) #W/cm2
                        partdict["VocFF"]=partdict["Voc"]*partdict["FF"]
                        partdict["Roc"]=float(filerawdata[item+9][4:-1])
                        partdict["Rsc"]=float(filerawdata[item+10][4:-1])
                        partdict["RscJsc"]=partdict["Rsc"]*partdict["Jsc"]
                        partdict["Vmpp"]=float(filerawdata[item+7][5:-1])
                        partdict["Jmpp"]=float(filerawdata[item+8][5:-1])
                        break
                
                partdict["ImaxComp"]=-1
                partdict["Isenserange"]=-1
                
                for item in range(len(filerawdata)):
                    if "UserName:" in filerawdata[item]:
                        partdict["Operator"]=str(filerawdata[item][10:-1])
                        break
                
                try:
                    if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                        f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                        x2 = lambda x: f(x)
                        partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                    else:
                        partdict["AreaJV"] =""
                except ValueError:
                    print("there is a ValueError on sample ",i)
                
                
                partdict["Group"]="Default group"
                partdict["Setup"]="CUBpythonIV"              
                for item in range(len(filerawdata)):
                    if "Diode nominal current:" in filerawdata[item]:
                        partdict["RefNomCurr"]=float(filerawdata[item][23:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Diode measured current:" in filerawdata[item]:
                        partdict["RefMeasCurr"]=float(filerawdata[item][24:-1])
                        break
                for item in range(len(filerawdata)):
                    if "temperature:" in filerawdata[item]:
                        partdict["AirTemp"]=float(filerawdata[item][13:-1])
                        break
                partdict["ChuckTemp"]=999
                partdict["IVlinestyle"]=[partdict["SampleName"],"-",colors[len(DATA.keys())],2]
#                DATA.append(partdict)

                if partdict["Illumination"]=="Light":
                    # DATA.append(partdict)
                    partdict["SampleNameID"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime2"]).replace(' ','_').replace(':','-')+'_'+'%.2f'%float(partdict["Eff"])

                    DATA[partdict["SampleNameID"]]=partdict
                    numbLightfiles+=1
                else:
                    partdict["SampleName"]=partdict["SampleName"]+'_D'
                    partdict["SampleNameID"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime2"]).replace(' ','_').replace(':','-')+'_'+'%.2f'%float(partdict["Eff"])
                    DATA[partdict["SampleNameID"]]=partdict
                    DATAdark.append(partdict)
                    numbDarkfiles+=1
                
            elif filetype ==2 : #mpp files of SERF C215 labview program
                #assumes file name: batch_samplenumber_cellLetter_mpp
                partdict = {}
                partdict["filepath"]=self.file_path[i]
                filename=os.path.splitext(os.path.basename(partdict["filepath"]))[0]
                partdict["DepID"]=filename.split('_')[0]+'_'+filename.split('_')[1]
                partdict["SampleName"]=filename.split('_')[0]+'_'+filename.split('_')[1]+'_'+filename.split('_')[2][2:]
                partdict["Cellletter"]=filename.split('_')[2][2:]
                partdict["batchname"]=filename.split('_')[0]
                
                for item in range(len(filerawdata)):
                    if "Comment: " in filerawdata[item]:
                        partdict["MeasComment"]=filerawdata[item][9:-1]
                        break
                for item in range(len(filerawdata)):
                    if "PixArea:" in filerawdata[item]:
                        partdict["CellSurface"]=float(filerawdata[item][9:-1])
                        break
                for item in range(len(filerawdata)):
                    if "DateTime:" in filerawdata[item]:
                        partdict["MeasDayTime2"]=parser.parse(filerawdata[item][10:-1])
                        partdict["MeasDayTime"]=filerawdata[item][10:-1]
                        # print(partdict["MeasDayTime2"])
#                        print(partdict["MeasDayTime"].split(' ')[-2])
                        break
                # partdict["MeasDayTime"]=modification_date(self.file_path[i])
                for item in range(len(filerawdata)):
                    if "PixArea:" in filerawdata[item]:
                        partdict["CellSurface"]=float(filerawdata[item][9:-1])
                        break
                for item in range(len(filerawdata)):
                    if "initialdelay:" in filerawdata[item]:
                        partdict["Delay"]=float(filerawdata[item][14:-1])
                        break
                partdict["IntegTime"]=0
                for item in range(len(filerawdata)):
                    if "initialstep:" in filerawdata[item]:
                        partdict["Vstep"]=float(filerawdata[item][13:-1])
                        break
                for item in range(len(filerawdata)):
                    if "InitialVoltage:" in filerawdata[item]:
                        partdict["Vstart"]=float(filerawdata[item][16:-1])
                        break
                partdict["Vend"]=0
                partdict["ExecTime"]=0
                for item in range(len(filerawdata)):
                    if "UserName:" in filerawdata[item]:
                        partdict["Operator"]=str(filerawdata[item][10:-1])
                        break
                partdict["Group"]="Default group"
                for item in range(len(filerawdata)):
                    if "#sun:" in filerawdata[item]:
                        partdict["sunintensity"]=float(filerawdata[item][6:-1])
                        break
                
                for item in range(len(filerawdata)):
                    if "#MPPT data" in filerawdata[item]:
                            pos=item+2
                            break
                        
                mpppartdat = [[],[],[],[],[]]#[voltage,current,time,power,vstep]
                for item in range(pos,len(filerawdata),1):
                    mpppartdat[0].append(float(filerawdata[item].split("\t")[2]))
                    mpppartdat[1].append(float(filerawdata[item].split("\t")[3]))
                    mpppartdat[2].append(float(filerawdata[item].split("\t")[0]))
                    mpppartdat[3].append(float(filerawdata[item].split("\t")[1]))
                    mpppartdat[4].append(float(filerawdata[item].split("\t")[5]))
                partdict["PowerEnd"]=mpppartdat[3][-1]
                partdict["PowerAvg"]=sum(mpppartdat[3])/float(len(mpppartdat[3]))
                partdict["trackingduration"]=mpppartdat[2][-1]
                partdict["SampleNameID"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime2"]).replace(' ','_').replace(':','-')+'_'+str(partdict["PowerEnd"])

                partdict["MppData"]=mpppartdat
                partdict["SampleName"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime2"]).replace(':','').replace(' ','-')
                partdict["MPPlinestyle"]=[partdict["SampleName"],"-",colors[len(DATAMPP.keys())],2]
                
                DATAMPP[partdict["SampleNameID"]]=partdict
                
            self.change_value.emit(100*(i+1)/len(self.file_path))
        self.finished.emit()
        
        
class Thread_getdatalistsfromCUBfiles(QThread):
    finished = pyqtSignal()
    change_value = pyqtSignal(int)
    def __init__(self, file_path, parent=None):
        QThread.__init__(self, parent)
        self.file_path=file_path
        
    def run(self):
        global DATA, DATAdark, colorstylelist
        global DATAMPP, numbLightfiles, numbDarkfiles, colormapname
        print('threadstart')
        
        num_plots=len(DATA.keys())+len(file_path)
        cmap = plt.get_cmap(colormapname)
        colors = cmap(np.linspace(0, 1.0, num_plots))
        colors=[tuple(item) for item in colors]
        
        for i in range(len(self.file_path)):
            filetoread = open(self.file_path[i],"r", encoding='ISO-8859-1')
            filerawdata = filetoread.readlines()
                              
            partdict = {}
            partdict["filepath"]=self.file_path[i]
            
            filename=os.path.splitext(os.path.basename(partdict["filepath"]))[0]                
            
            partdict["Cellletter"]=filename.split('_')[2][2:]
            partdict["batchname"]=filename.split('_')[0]
            partdict["DepID"]=partdict["batchname"]+"_"+filename.split('_')[1]
            partdict["SampleName"]=partdict["DepID"]+"_"+partdict["Cellletter"] #+"_"+aftername.split('_')[4]
            
            if "light" in filename:
                partdict["Illumination"]="Light"
            else:
                partdict["Illumination"]="Dark"
                
            if "rev" in filename:
                partdict["ScanDirection"]="Reverse"
            else:
                partdict["ScanDirection"]="Forward" 
            
            
            partdict["MeasDayTime2"]=parser.parse(filerawdata[0])
            partdict["MeasDayTime"]=filerawdata[0]
#                print(partdict["MeasDayTime2"])
#                print(partdict["MeasDayTime"])
                    
            partdict["MeasComment"]="-"
            for item in range(len(filerawdata)):
                if "Notes = " in filerawdata[item]:
                    partdict["MeasComment"]=filerawdata[item][8:-1]
                    break
            if "aftermpp" in partdict["MeasComment"]:
                partdict["aftermpp"]=1
            else:
                partdict["aftermpp"]=0
                
            for item in range(len(filerawdata)):
                if "Device Area = " in filerawdata[item]:
                    partdict["CellSurface"]=float(filerawdata[item][14:-5])
#                        print(partdict["CellSurface"])
                    break
            for item in range(len(filerawdata)):
                if "Delay = " in filerawdata[item]:
                    partdict["Delay"]=float(filerawdata[item][8:-3])
#                        print(partdict["Delay"])
                    break
            for item in range(len(filerawdata)):
                if "NPLC = " in filerawdata[item]:
                    partdict["IntegTime"]=float(filerawdata[item][7:-1])
                    break     
            
            for item in range(len(filerawdata)):
                if "Voltage" in filerawdata[item]:
                        pos=item+1
                        break
                    
            ivpartdat = [[],[]]#[voltage,current]
            for item in range(pos,len(filerawdata),1):
                try:
                    ivpartdat[0].append(float(filerawdata[item].split("\t")[0]))
                    ivpartdat[1].append(float(filerawdata[item].split("\t")[1]))
                except:
                    break
            partdict["IVData"]=ivpartdat
            partdict["NbPoints"]=len(ivpartdat[0])
            partdict["Vstart"]=ivpartdat[0][-1]
            partdict["Vend"]=ivpartdat[0][0]
                    
            params=self.extract_jv_params(partdict["IVData"])
            partdict["Voc"]=params['Voc']*1000 #mV
            partdict["Jsc"]=params['Jsc'] #mA/cm2
            partdict["FF"]=params['FF'] #%
            partdict["Eff"]=params['Pmax'] #%
            partdict["Pmpp"]=partdict["Eff"]*10 #W/cm2
            partdict["VocFF"]=partdict["Voc"]*partdict["FF"]
            partdict["Roc"]=params['Roc'] 
            partdict["Rsc"]=params['Rsc'] 
            partdict["RscJsc"]=partdict["Rsc"]*partdict["Jsc"]
            
            partdict["Vmpp"]=params['Vmpp']
            partdict["Jmpp"]=params['Jmpp']
            partdict["ImaxComp"]=-1
            partdict["Isenserange"]=-1
            
            partdict["Operator"]=-1
                          
            try:
                if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                    f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                    x2 = lambda x: f(x)
                    partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                else:
                    partdict["AreaJV"] =""
            except ValueError:
                print("there is a ValueError on sample ",i)
            
            
            partdict["Group"]="Default group"
            partdict["Setup"]="CUBoulder"              
            partdict["RefNomCurr"]=999
            partdict["RefMeasCurr"]=999
            partdict["AirTemp"]=999
            partdict["ChuckTemp"]=999
            partdict["IVlinestyle"]=[partdict["SampleName"],"-",colors[len(DATA.keys())],2]
            
            if partdict["Illumination"]=="Light":
                # DATA.append(partdict)
                partdict["SampleNameID"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime2"]).replace(' ','_').replace(':','-')+'_'+'%.2f'%float(partdict["Eff"])
                DATA[partdict["SampleNameID"]]=partdict
                numbLightfiles+=1
            else:
                partdict["SampleName"]=partdict["SampleName"]+'_D'
                partdict["SampleNameID"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime2"]).replace(' ','_').replace(':','-')+'_'+'%.2f'%float(partdict["Eff"])
                DATA[partdict["SampleNameID"]]=partdict
                DATAdark.append(partdict)
                numbDarkfiles+=1
                
            self.change_value.emit(100*(i+1)/len(self.file_path))
            
        self.finished.emit()
        
        
        

class Thread_getdatalistsfromNRELfiles(QThread):
    finished = pyqtSignal()
    change_value = pyqtSignal(int)
    def __init__(self, file_path, parent=None):
        QThread.__init__(self, parent)
        self.file_path=file_path
        
    def run(self):
        global DATA, DATAdark, colorstylelist
        global DATAMPP, numbLightfiles, numbDarkfiles, colormapname
        print('threadstart')
        
        for i in range(len(self.file_path)):
            filetoread = open(self.file_path[i],"r", encoding='ISO-8859-1')
            filerawdata = filetoread.readlines()
            # print(i)
            filetype = 0
            if "HEADER START" in filerawdata[0]:
                filetype = 1 #JV file from solar simulator in SERF C215
                num_plots=len(DATA.keys())+len(file_path)
                cmap = plt.get_cmap(colormapname)
                colors = cmap(np.linspace(0, 1.0, num_plots))
                colors=[tuple(item) for item in colors]
                # print('jv')
            elif "Power (mW/cm2)" in filerawdata[0]:
                filetype = 2
                num_plots=len(DATAMPP.keys())+len(file_path)
                cmap = plt.get_cmap(colormapname)
                colors = cmap(np.linspace(0, 1.0, num_plots))
                colors=[tuple(item) for item in colors]
                # print('mpp')
            elif "V\tI" in filerawdata[0]:
                filetype = 3
                num_plots=len(DATA.keys())+len(file_path)
                cmap = plt.get_cmap(colormapname)
                colors = cmap(np.linspace(0, 1.0, num_plots))
                colors=[tuple(item) for item in colors]
                # print("JVT")
            
            
            if filetype ==1 : #J-V files of SERF C215
                              
                partdict = {}
                partdict["filepath"]=self.file_path[i]
                
                filename=os.path.splitext(os.path.basename(partdict["filepath"]))[0]
#                print(filename)
                if 'rev' in filename:
                    partdict["DepID"]=filename[:filename.index('rev')-1]
                    aftername=filename[filename.index('rev'):]
                elif 'fwd' in filename:
                    partdict["DepID"]=filename[:filename.index('fwd')-1]
                    aftername=filename[filename.index('fwd'):]
                
                partdict["Cellletter"]=aftername.split('_')[3][2:]
                partdict["batchname"]=partdict["DepID"].split('_')[0]
                partdict["SampleName"]=partdict["DepID"]+"_"+partdict["Cellletter"]+"_"+aftername.split('_')[4]
                
                if aftername.split('_')[1]=="lt":
                    partdict["Illumination"]="Light"
                else:
                    partdict["Illumination"]="Dark"
                    
                if aftername.split('_')[0]=="rev":
                    partdict["ScanDirection"]="Reverse"
                else:
                    partdict["ScanDirection"]="Forward" 
                
                for item in range(len(filerawdata)):
                    if "Date/Time:" in filerawdata[item]:
                        partdict["MeasDayTime2"]=parser.parse(filerawdata[item][11:-1])
                        partdict["MeasDayTime"]=filerawdata[item][11:-1]
                        # print(partdict["MeasDayTime2"])
#                        print(partdict["MeasDayTime"].split(' ')[-2])
                        break
                for item in range(len(filerawdata)):
                    if "Intensity:" in filerawdata[item]:
                        partdict["sunintensity"]=float(filerawdata[item][11:-1])
                        break
                partdict["MeasComment"]="-"
                for item in range(len(filerawdata)):
                    if "Comments: " in filerawdata[item]:
                        partdict["MeasComment"]=filerawdata[item][10:-1]
                        break
                if "aftermpp" in partdict["MeasComment"]:
                    partdict["aftermpp"]=1
                else:
                    partdict["aftermpp"]=0
                for item in range(len(filerawdata)):
                    if "Start V:" in filerawdata[item]:
                        partdict["Vstart"]=float(filerawdata[item][9:-1])
                        break
                for item in range(len(filerawdata)):
                    if "End V:" in filerawdata[item]:
                        partdict["Vend"]=float(filerawdata[item][7:-1])
                        break
                if partdict["ScanDirection"]=="Reverse":
                    if partdict["Vstart"]<partdict["Vend"]:
                        vend=partdict["Vend"]
                        partdict["Vend"]=partdict["Vstart"]
                        partdict["Vstart"]=vend
                else:
                    if partdict["Vstart"]>partdict["Vend"]:
                        vend=partdict["Vend"]
                        partdict["Vend"]=partdict["Vstart"]
                        partdict["Vstart"]=vend 
                for item in range(len(filerawdata)):
                    if "Number Points:" in filerawdata[item]:
                        partdict["NbPoints"]=float(filerawdata[item][15:-1])
                        break    
                for item in range(len(filerawdata)):
                    if "Pixel Size:" in filerawdata[item]:
                        partdict["CellSurface"]=float(filerawdata[item][12:-5])
                        #print(partdict["CellSurface"])
                        break
                for item in range(len(filerawdata)):
                    if "Source Delay:" in filerawdata[item]:
                        partdict["Delay"]=float(filerawdata[item][14:-1])
                        break
                for item in range(len(filerawdata)):
                    if "NPLC:" in filerawdata[item]:
                        partdict["IntegTime"]=float(filerawdata[item][6:-1])
                        break
                for item in range(len(filerawdata)):
                    if "HEADER END" in filerawdata[item]:
                            pos=item+3
                            break
                        
                ivpartdat = [[],[]]#[voltage,current]
                for item in range(pos,len(filerawdata),1):
                    try:
                        ivpartdat[0].append(float(filerawdata[item].split("\t")[0]))
                        ivpartdat[1].append(-float(filerawdata[item].split("\t")[1]))
                    except:
                        break
                partdict["IVData"]=ivpartdat
                params=extract_jv_params(partdict["IVData"])
                partdict["Voc"]=params['Voc']*1000 #mV
                partdict["Jsc"]=params['Jsc'] #mA/cm2
                partdict["Isc"]=params['Jsc']*partdict["CellSurface"]
                partdict["FF"]=params['FF'] #%
                partdict["Eff"]=params['Pmax'] #%
                partdict["Pmpp"]=partdict["Eff"]*10 #W/cm2
                partdict["VocFF"]=partdict["Voc"]*partdict["FF"]
                partdict["Roc"]=params['Roc'] 
                partdict["Rsc"]=params['Rsc'] 
                partdict["RscJsc"]=partdict["Rsc"]*partdict["Jsc"]
                
                partdict["Vmpp"]=params['Vmpp']
                partdict["Jmpp"]=params['Jmpp']
                partdict["ImaxComp"]=-1
                partdict["Isenserange"]=-1
                
                partdict["Operator"]=-1
                
                
                
                try:
                    if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                        f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                        x2 = lambda x: f(x)
                        partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                    else:
                        partdict["AreaJV"] =""
                except ValueError:
                    print("there is a ValueError on sample ",i)
                
                
                partdict["Group"]="Default group"
                partdict["Setup"]="SSIgorC215"              
                partdict["RefNomCurr"]=999
                partdict["RefMeasCurr"]=999
                partdict["AirTemp"]=999
                partdict["ChuckTemp"]=999
                partdict["IVlinestyle"]=[partdict["SampleName"],"-",colors[len(DATA.keys())],2]
#                DATA.append(partdict)

                if partdict["Illumination"]=="Light":
                    # DATA.append(partdict)
                    partdict["SampleNameID"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime2"]).replace(' ','_').replace(':','-')+'_'+'%.2f'%float(partdict["Eff"])

                    DATA[partdict["SampleNameID"]]=partdict
                    numbLightfiles+=1
                else:
                    partdict["SampleName"]=partdict["SampleName"]+'_D'
                    partdict["SampleNameID"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime2"]).replace(' ','_').replace(':','-')+'_'+'%.2f'%float(partdict["Eff"])
                    DATA[partdict["SampleNameID"]]=partdict
                    DATAdark.append(partdict)
                    numbDarkfiles+=1
            elif filetype ==3 : #JVT files from Taylor
                partdict = {}
                partdict["filepath"]=self.file_path[i]
                
                filename=os.path.splitext(os.path.basename(partdict["filepath"]))[0]
#                print(filename)
                
                partdict["DepID"]=filename
                aftername=filename
    
                
                partdict["Cellletter"]='A'
                partdict["batchname"]='batch'
                partdict["SampleName"]=partdict["DepID"]
                
                partdict["Illumination"]="Light"
                    
                partdict["ScanDirection"]="Reverse"
                
                
                partdict["MeasDayTime2"]=modification_date(self.file_path[i])#'2020-01-29 12:55:00'
                partdict["MeasDayTime"]='Wed, Jan 29, 2020 0:00:00'
                partdict["MeasComment"]="-"
                partdict["aftermpp"]=1
                partdict["Vstart"]=0
                partdict["Vend"]=0
                partdict["NbPoints"]=0      
                partdict["CellSurface"]=0.1  
                partdict["Delay"]=0    
                partdict["IntegTime"]=0
                partdict["sunintensity"]=1
                        
                ivpartdat = [[],[]]#[voltage,current]
                for item in range(1,len(filerawdata),1):
                    try:
                        ivpartdat[0].append(float(filerawdata[item].split("\t")[0]))
                        ivpartdat[1].append(1000*float(filerawdata[item].split("\t")[1])/partdict["CellSurface"])
                    except:
                        break
                partdict["IVData"]=ivpartdat
                params=extract_jv_params(partdict["IVData"])
                partdict["Voc"]=params['Voc']*1000 #mV
                partdict["Jsc"]=params['Jsc'] #mA/cm2
                partdict["Isc"]=params['Jsc']*partdict["CellSurface"]
                partdict["FF"]=params['FF'] #%
                partdict["Eff"]=params['Pmax'] #%
                partdict["Pmpp"]=partdict["Eff"]*10 #W/cm2
                partdict["VocFF"]=partdict["Voc"]*partdict["FF"]
                partdict["Roc"]=params['Roc'] 
                partdict["Rsc"]=params['Rsc'] 
                partdict["RscJsc"]=partdict["Rsc"]*partdict["Jsc"]
                
                partdict["Vmpp"]=params['Vmpp']
                partdict["Jmpp"]=params['Jmpp']
                partdict["ImaxComp"]=-1
                partdict["Isenserange"]=-1
                
                partdict["Operator"]=-1
                partdict["SampleNameID"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime2"]).replace(' ','_').replace(':','-')+'_'+'%.2f'%float(partdict["Eff"])

                try:
                    if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                        f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                        x2 = lambda x: f(x)
                        partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                    else:
                        partdict["AreaJV"] =""
                except ValueError:
                    print("there is a ValueError on sample ",i)
                
                partdict["IVlinestyle"]=[partdict["SampleName"],"-",colors[len(DATA.keys())],2]

                partdict["Group"]="Default group"
                partdict["Setup"]="JVT"              
                partdict["RefNomCurr"]=999
                partdict["RefMeasCurr"]=999
                partdict["AirTemp"]=999
                partdict["ChuckTemp"]=999
                    
#                DATA.append(partdict)
                DATA[partdict["SampleNameID"]]=partdict
                numbLightfiles+=1
                
            elif filetype ==2 : #mpp files of SERF C215 labview program
                #assumes file name: batch_samplenumber_cellLetter_mpp
                partdict = {}
                partdict["filepath"]=self.file_path[i]
                filename=os.path.splitext(os.path.basename(partdict["filepath"]))[0]
                partdict["DepID"]=filename.split('_')[0]+'_'+filename.split('_')[1]
                partdict["SampleName"]=filename.split('_')[0]+'_'+filename.split('_')[1]+'_'+filename.split('_')[2]
                partdict["Cellletter"]=filename.split('_')[2]
                partdict["batchname"]=filename.split('_')[0]
                partdict["MeasComment"]=filename[filename.index('_')+1:]
                
                partdict["MeasDayTime"]=modification_date(self.file_path[i])
                # print(partdict["MeasDayTime"])
                partdict["CellSurface"]= float(filerawdata[0].split('\t')[-1])

                partdict["Delay"]=0
                partdict["IntegTime"]=0
                partdict["Vstep"]=0
                partdict["Vstart"]=0
                partdict["Vend"]=0
                partdict["ExecTime"]=0
                partdict["Operator"]='unknown'
                partdict["Group"]="Default group"
                partdict["sunintensity"]=1
                
                mpppartdat = [[],[],[],[],[]]#[voltage,current,time,power,vstep]
                for item in range(1,len(filerawdata),1):
                    mpppartdat[0].append(float(filerawdata[item].split("\t")[2]))
                    mpppartdat[1].append(float(filerawdata[item].split("\t")[3]))
                    mpppartdat[2].append(float(filerawdata[item].split("\t")[0]))
                    mpppartdat[3].append(float(filerawdata[item].split("\t")[1]))
                    mpppartdat[4].append(-1)
                partdict["PowerEnd"]=mpppartdat[3][-1]
                partdict["PowerAvg"]=sum(mpppartdat[3])/float(len(mpppartdat[3]))
                partdict["trackingduration"]=mpppartdat[2][-1]
                partdict["SampleNameID"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime"]).replace(' ','_').replace(':','-')+'_'+str(partdict["PowerEnd"])

                partdict["MppData"]=mpppartdat
                partdict["SampleName"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime"]).replace(':','').replace(' ','-')
                partdict["MPPlinestyle"]=[partdict["SampleName"],"-",colors[len(DATAMPP.keys())],2]
                
                DATAMPP[partdict["SampleNameID"]]=partdict                
                
            self.change_value.emit(100*(i+1)/len(self.file_path))
        
#         DATA = sorted(DATA, key=itemgetter('SampleName')) 
#         names=[d["SampleName"] for d in DATA if "SampleName" in d]
#         groupednames=[list(j) for i, j in groupby(names)]
#         # print(groupednames)
#         for item in range(len(groupednames)):
#             if len(groupednames[item])>1 and groupednames[item][0][-1]!='D':
#                 positions=[]
#                 effrev=0
#                 efffor=0
#                 for item2 in range(len(DATA)):
#                     if DATA[item2]['SampleName']==groupednames[item][0]:
#                         positions.append(item2)
#                         if DATA[item2]["ScanDirection"]=="Reverse":
#                             effrev=DATA[item2]['Eff']
#                         else:
#                             efffor=DATA[item2]['Eff']
#                     if len(positions)==len(groupednames[item]):
#                         break
#                 try:
#                     hyste=100*(effrev-efffor)/effrev
#                     for item2 in range(len(positions)):
#                         DATA[positions[item2]]['HI']=hyste
# #                        print(hyste)
#                 except:
#                     print("except HI")
        
#         for item in range(len(groupednames)):
#             if len(groupednames[item])!=1:
#                 k=1
#                 for item0 in range(1,len(groupednames[item])):
                    
# #                    groupednames2=copy.deepcopy(groupednames)
# #                    groupednames[item][item0]+= "_"+str(k)
# #                    print(groupednames[item][item0])
#                     while(1):
#                         groupednames2=list(chain.from_iterable(groupednames))
# #                        print(groupednames2)
                        
#                         if groupednames[item][item0]+"_"+str(k) in groupednames2:
#                             k+=1
#                             groupednames[item][item0]+= "_"+str(k)
# #                            print(groupednames[item][item0])
# #                            print('')
#                         else:
#                             groupednames[item][item0]+= "_"+str(k)
# #                            print('notin')
#                             break
                        
#         groupednames=list(chain.from_iterable(groupednames))
# #        print("")
# #        print(groupednames)
#         for item in range(len(DATA)):
#             DATA[item]['SampleName']=groupednames[item]
        
        # DATAMPP = sorted(DATAMPP, key=itemgetter('SampleName')) 
        # names=[d["SampleName"] for d in DATAMPP if "SampleName" in d]
        # groupednames=[list(j) for i, j in groupby(names)]
        # for item in range(len(groupednames)):
        #     if len(groupednames[item])!=1:
        #         for item0 in range(1,len(groupednames[item]),1):
        #             groupednames[item][item0]+= "_"+str(item0)
        # groupednames=list(chain.from_iterable(groupednames))
        # for item in range(len(DATAMPP)):
        #     DATAMPP[item]['SampleName']=groupednames[item]
        
        self.finished.emit()



def extract_jv_params(jv):#function originally written by Rohit Prasana (adapted by JW)
    '''
    Extract Voc, Jsc, FF, Pmax from a given JV curve
        * Assume given JV curve is in volts and mA/cm2
    '''
    resample_step_size = 0.00001 # Voltage step size to use while resampling JV curve to find Pmax

    from scipy.interpolate import interp1d

    # Create a dict to store the parameters. Default values are -1 indicating failure to extract parameter
    params = {'Voc': -1., 'Jsc': -1., 'FF': -1., 'Pmax': -1., 'Roc':-1., 'Rsc':-1., 'Jmpp':-1, 'Vmpp':-1, 'Rshunt':-1, 'Rseries':-1}
    
    try:
        # Extract Jsc by interpolating wrt V
        jv_interp_V = interp1d(jv[0], jv[1], bounds_error=False, fill_value=0.)
        Jsc = jv_interp_V(0.)
        params['Jsc'] = abs(np.around(Jsc, decimals=8))
#            print(Jsc)
#            print(params['Jsc'])
    
        # Extract Voc by interpolating wrt J
        jv_interp_J = interp1d(jv[1], jv[0], bounds_error=False, fill_value=0.)
        Voc = jv_interp_J(0.)
#            print(Voc)
        params['Voc'] = np.around(Voc, decimals=4)
    
        # Resample JV curve over standard interval and find Pmax
        Vrange_new = np.arange(0., Voc, resample_step_size)
#            print(Vrange_new)
        jv_resampled = np.zeros((len(Vrange_new), 3))
        jv_resampled[:,0] = np.copy(Vrange_new)
        jv_resampled[:,1] = jv_interp_V(jv_resampled[:,0])
        jv_resampled[:,2] = np.abs(np.multiply(jv_resampled[:,0], jv_resampled[:,1]))
#            print(jv_resampled)
        pmax=np.max(np.abs(np.multiply(jv_resampled[:,0], jv_resampled[:,1])))
        params['Pmax'] = np.around(np.max(np.abs(np.multiply(jv_resampled[:,0], jv_resampled[:,1]))), decimals=4)
        indPmax=list(jv_resampled[:,2]).index(pmax)
        params['Jmpp']=abs(list(jv_resampled[:,1])[indPmax])
#            print(list(jv_resampled[:,1])[indPmax])
#            print(indPmax)
#            print(jv_interp_J(list(jv_resampled[:,1])[indPmax]))
        params['Vmpp']=1000*abs(list(jv_resampled[:,0])[indPmax])
#            print(params['Vmpp'])
    
        # Calculate fill factor
        params['FF'] = abs(100*np.around(pmax/(Jsc*Voc), decimals=4))
    except:
        print("error with param. calc")
        
    try:
    # Calculate Rsc&Roc 
    # x= [x0 for x0,y0 in sorted(zip(params['Voltage'],params['CurrentDensity']))]
    # y= [0.001*y0 for x0,y0 in sorted(zip(params['Voltage'],params['CurrentDensity']))]
    
        x= [x0 for x0,y0 in sorted(zip(jv[0], jv[1]))]
        y= [0.001*y0 for x0,y0 in sorted(zip(jv[0], jv[1]))]
        
        xSC=[]
        ySC=[]
        for i in range(len(x)):
            if x[i]>=0:
                xSC.append(x[i-3])
                xSC.append(x[i-2])
                xSC.append(x[i-1])
                xSC.append(x[i])
                xSC.append(x[i+1])
                xSC.append(x[i+2])
                ySC.append(y[i-3])
                ySC.append(y[i-2])
                ySC.append(y[i-2])
                ySC.append(y[i])
                ySC.append(y[i+1])
                ySC.append(y[i+2])
                break
    
        xSC=np.array(xSC)
        ySC=np.array(ySC)    
              
        xy=[xi*yi for xi, yi in zip(xSC,ySC)]
        xSC2=[xi**2 for xi in xSC]
        
        params['Rsc'] =abs( 1/(((sum(xSC)*sum(ySC)) - len(xSC)*sum(xy)) / ((sum(xSC)*sum(xSC)) - len(xSC)*sum(xSC2))))  
        # print(AllDATA[sample]['Rsc'])
        
        if params['Jsc']>1:
            xSC=[]
            ySC=[]
            for i in range(len(x)):
                if x[i]>=params['Voc']:
                    xSC.append(x[i-2])
                    xSC.append(x[i-1])
                    xSC.append(x[i])
                    xSC.append(x[i+1])
                    
                    ySC.append(y[i-2])
                    ySC.append(y[i-1])
                    ySC.append(y[i])
                    ySC.append(y[i+1])
                    break
    #                plt.plot(xSC,ySC,'bo')
            xSC=np.array(xSC)
            ySC=np.array(ySC)
            
            xy=[xi*yi for xi, yi in zip(xSC,ySC)]
            xSC2=[xi**2 for xi in xSC]
            params['Roc'] =abs( 1/(((sum(xSC)*sum(ySC)) - len(xSC)*sum(xy)) / ((sum(xSC)*sum(xSC)) - len(xSC)*sum(xSC2))))
        else:
            xSC=x[-3:]
            ySC=y[-3:]
            xSC=np.array(xSC)
            ySC=np.array(ySC)      
            xy=[xi*yi for xi, yi in zip(xSC,ySC)]
            xSC2=[xi**2 for xi in xSC]
            
            params['Roc'] = abs( 1/(((sum(xSC)*sum(ySC)) - len(xSC)*sum(xy)) / ((sum(xSC)*sum(xSC)) - len(xSC)*sum(xSC2))))   
        # print(AllDATA[sample]['Roc'])
#             x= [x0 for x0,y0 in sorted(zip(jv[0],jv[1]))]
#             y= [0.001*y0 for x0,y0 in sorted(zip(jv[0],jv[1]))]


#             xSC=[]
#             ySC=[]
#             for i in range(len(x)):
#                 if x[i]>=0:
#                     xSC.append(x[i-3])
#                     xSC.append(x[i-2])
#                     xSC.append(x[i-1])
#                     xSC.append(x[i])
#                     xSC.append(x[i+1])
#                     xSC.append(x[i+2])
#                     ySC.append(y[i-3])
#                     ySC.append(y[i-2])
#                     ySC.append(y[i-2])
#                     ySC.append(y[i])
#                     ySC.append(y[i+1])
#                     ySC.append(y[i+2])
#                     break
#     #        print(xSC)
#     #        print(ySC)
#     #        plt.plot(xSC,ySC,'bo')
#             xSC=np.array(xSC)
#             ySC=np.array(ySC)    
            
#     #        slope = stats.linregress(xSC,ySC)   
        
#             params['Rsc'] =abs( 1/(((mean(xSC)*mean(ySC)) - mean(xSC*ySC)) / ((mean(xSC)**2) - mean(xSC**2))))    
        
#             if params['Jsc']>1:
#                 xSC=[]
#                 ySC=[]
#                 for i in range(len(x)):
#                     if x[i]>=params['Voc']:
#                         xSC.append(x[i-2])
#                         xSC.append(x[i-1])
#                         xSC.append(x[i])
#                         xSC.append(x[i+1])
                    
#                         ySC.append(y[i-2])
#                         ySC.append(y[i-1])
#                         ySC.append(y[i])
#                         ySC.append(y[i+1])
#                         break
# #                plt.plot(xSC,ySC,'bo')
#                 xSC=np.array(xSC)
#                 ySC=np.array(ySC)      
            
#                 params['Roc'] =abs( 1/(((mean(xSC)*mean(ySC)) - mean(xSC*ySC)) / ((mean(xSC)**2) - mean(xSC**2))))
#             else:
#                 xSC=x[-3:]
#                 ySC=y[-3:]
# #                plt.plot(xSC,ySC,'bo')
#                 xSC=np.array(xSC)
#                 ySC=np.array(ySC)      
            
#                 params['Roc'] = abs(1/(((mean(xSC)*mean(ySC)) - mean(xSC*ySC)) / ((mean(xSC)**2) - mean(xSC**2))) )   
        
        
        
        
#        plt.show()
#        print(params['Rsc'])
#        print(params['Roc'])
#        print(params['Jsc'])
    except:
        print("error with Roc or Rsc calc")
    
    

    return  params

#%%#############
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = IVapp()
    window.show()
    sys.exit(app.exec())













