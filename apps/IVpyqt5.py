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
from IVpyqt5gui import Ui_MainWindow

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
                            
                        elif 'Notes' in filerawdata[1]:
                            print("CUB files")
                            # self.getdatalistsfromCUBfiles(file_path)
                            finished=1
                        else:
                            print("NREL files")
                            self.thread = Thread_getdatalistsfromNRELfiles(file_path)
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
        
        self.updateTable(DATA)

        
    def updateTable(self, dictdata):
        
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
        
        groupnames=[]
        for i in range(self.ui.tableWidget.rowCount()):
            sn=self.ui.tableWidget.item(i,1).text()+'_'+str(self.ui.tableWidget.item(i,2).text()).replace(' ','_').replace(':','-')+'_'+'%.2f'%float(self.ui.tableWidget.item(i,3).text())
            DATA[sn]['Group']=self.ui.tableWidget.item(i,0).text()
            groupnames.append(self.ui.tableWidget.item(i,0).text())
            
        groupnames=set(groupnames)
        self.ui.listWidget_BoxPlotGroup.addItems(groupnames)
        self.ui.listWidget_HistoGroups.addItems(groupnames)
        
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
        # try:
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
        
        # except:
        #     print("there is an exception while saving MPP")    
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


    def UpdateBoxGraph(self):
        global DATA
        global groupstoplot
        global DATAgroupforexport
        
        DATAgroupforexport=[]
        fontsizegroup=self.ui.spinBox_BoxPlotFontsize.value()
        DATAx=copy.deepcopy(DATA)
        
        samplesgroups = self.ui.listWidget_BoxPlotGroup.selectedItems()
        samplesgroups=[item.text() for item in samplesgroups]
        print(samplesgroups)
        
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
                            
                            
                            
                            
        print(grouplistdict)
                                
        
    def GraphBoxsave_as(self):
        global DATA


#%%#############
# self.getdatalistsfromIVTFfiles(file_pathnew)
# self.getdatalistsfromIVHITfiles(file_path)

# self.getdatalistsfromNRELcigssetup(file_path)
# self.getdatalistsfromNRELfiles(file_path)

# self.getdatalistsfromCUBfiles(file_path)

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
        # for i in range(len(file_path)):
        #     time.sleep(0.5)
        #     print(i)
        #     self.change_value.emit(100*(i+1)/len(file_path))
        
        
        
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
                num_plots=len(DATA.keys())+len(file_path)
                cmap = plt.get_cmap(colormapname)
                colors = cmap(np.linspace(0, 1.0, num_plots))
                colors=[tuple(item) for item in colors]
                # print('mpp')
            elif "V\tI" in filerawdata[0]:
                filetype = 3
                num_plots=len(DATAMPP.keys())+len(file_path)
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













