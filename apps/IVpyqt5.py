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
DATA = [] #[{"SampleName":, "CellNumber": , "MeasDayTime":, "CellSurface":, "Voc":, "Jsc":, "FF":, "Eff":, "Pmpp":, "Vmpp":, "Jmpp":, "Roc":, "Rsc":, "VocFF":, "RscJsc":, "NbPoints":, "Delay":, "IntegTime":, "Vstart":, "Vend":, "Illumination":, "ScanDirection":, "ImaxComp":, "Isenserange":,"AreaJV":, "Operator":, "MeasComment":, "IVData":}]
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

DATAMPP = []
DATAdark = []
DATAFV=[]

numbLightfiles=0
numbDarkfiles=0

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

        finish = QAction("Quit", self)
        finish.triggered.connect(lambda: self.closeEvent(1))

        self.ui.pushButton_ImportData.clicked.connect(self.startimporting)
    
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
                            self.thread.start()
                            
                        elif 'Notes' in filerawdata[1]:
                            print("CUB files")
                            # self.getdatalistsfromCUBfiles(file_path)
                            finished=1
                        else:
                            print("NREL files")
                            # self.getdatalistsfromNRELfiles(file_path)
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


    def setProgressVal(self, val):
        global file_path
        global DATA, DATAdark
        global DATAMPP, numbLightfiles, numbDarkfiles
        
        self.ui.progressBar_ImportData.setValue(val)
        print(len(DATA))
        
        # if DATAMPP!=[]:
        #     self.mppnames = ()
        #     self.mppnames=self.SampleMppNames(DATAMPP)
        #     self.mppmenu = tk.Menu(self.mppmenubutton, tearoff=False)
        #     self.mppmenubutton.configure(menu=self.mppmenu)
        #     self.choicesmpp = {}
        #     for choice in range(len(self.mppnames)):
        #         self.choicesmpp[choice] = tk.IntVar(value=0)
        #         self.mppmenu.add_checkbutton(label=self.mppnames[choice], variable=self.choicesmpp[choice], 
        #                               onvalue=1, offvalue=0, command = self.UpdateMppGraph0)
        
        # self.updateTable()
        
        # self.updategrouptoplotdropbutton()
        # self.updateCompgrouptoplotdropbutton()
        # self.updateHistgrouptoplotdropbutton()
        # self.UpdateGroupGraph(1)
        # self.UpdateCompGraph(1)
        
    def updateTable(self):
        print('updating table')



#%%#############
# self.getdatalistsfromIVTFfiles(file_pathnew)
# self.getdatalistsfromIVHITfiles(file_path)

# self.getdatalistsfromNRELcigssetup(file_path)
# self.getdatalistsfromNRELfiles(file_path)

# self.getdatalistsfromCUBfiles(file_path)

class Thread_getdatalistsfromNRELfiles(QThread):
    
    change_value = pyqtSignal(int)
    def __init__(self, file_path, parent=None):
        QThread.__init__(self, parent)
        self.file_path=file_path
        
    def run(self):
        global DATA, DATAdark
        global DATAMPP, numbLightfiles, numbDarkfiles
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
            elif "Power (mW/cm2)" in filerawdata[0]:
                filetype = 2
            elif "V\tI" in filerawdata[0]:
                filetype = 3
                print("JVT")
            
            
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
#                        print(partdict["MeasDayTime2"])
#                        print(partdict["MeasDayTime"].split(' ')[-2])
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
                    
#                DATA.append(partdict)

                if partdict["Illumination"]=="Light":
                    DATA.append(partdict)
                    numbLightfiles+=1
                else:
                    partdict["SampleName"]=partdict["SampleName"]+'_D'
                    DATA.append(partdict)
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
                
                
                partdict["MeasDayTime2"]='2020-01-29 12:55:00'
                partdict["MeasDayTime"]='Wed, Jan 29, 2020 0:00:00'
                        
                partdict["MeasComment"]="-"
                partdict["aftermpp"]=1
                partdict["Vstart"]=0
                partdict["Vend"]=0
                partdict["NbPoints"]=0      
                partdict["CellSurface"]=0.1  
                partdict["Delay"]=0    
                partdict["IntegTime"]=0
                        
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
                partdict["Setup"]="JVT"              
                partdict["RefNomCurr"]=999
                partdict["RefMeasCurr"]=999
                partdict["AirTemp"]=999
                partdict["ChuckTemp"]=999
                    
#                DATA.append(partdict)
                DATA.append(partdict)
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

                partdict["CellSurface"]= float(filerawdata[0].split('\t')[-1])

                partdict["Delay"]=0
                partdict["IntegTime"]=0
                partdict["Vstep"]=0
                partdict["Vstart"]=0
                partdict["Vend"]=0
                partdict["ExecTime"]=0
                partdict["Operator"]='unknown'
                partdict["Group"]="Default group"
                
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
                partdict["MppData"]=mpppartdat
                partdict["SampleName"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime"]).replace(':','').replace(' ','-')
                DATAMPP.append(partdict)                
                
            self.change_value.emit(100*(i+1)/len(self.file_path))
        
        DATA = sorted(DATA, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATA if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
        print(groupednames)
        for item in range(len(groupednames)):
            if len(groupednames[item])>1 and groupednames[item][0][-1]!='D':
                positions=[]
                effrev=0
                efffor=0
                for item2 in range(len(DATA)):
                    if DATA[item2]['SampleName']==groupednames[item][0]:
                        positions.append(item2)
                        if DATA[item2]["ScanDirection"]=="Reverse":
                            effrev=DATA[item2]['Eff']
                        else:
                            efffor=DATA[item2]['Eff']
                    if len(positions)==len(groupednames[item]):
                        break
                try:
                    hyste=100*(effrev-efffor)/effrev
                    for item2 in range(len(positions)):
                        DATA[positions[item2]]['HI']=hyste
#                        print(hyste)
                except:
                    print("except HI")
        
        for item in range(len(groupednames)):
            if len(groupednames[item])!=1:
                k=1
                for item0 in range(1,len(groupednames[item])):
                    
#                    groupednames2=copy.deepcopy(groupednames)
#                    groupednames[item][item0]+= "_"+str(k)
#                    print(groupednames[item][item0])
                    while(1):
                        groupednames2=list(chain.from_iterable(groupednames))
#                        print(groupednames2)
                        
                        if groupednames[item][item0]+"_"+str(k) in groupednames2:
                            k+=1
                            groupednames[item][item0]+= "_"+str(k)
#                            print(groupednames[item][item0])
#                            print('')
                        else:
                            groupednames[item][item0]+= "_"+str(k)
#                            print('notin')
                            break
                        
        groupednames=list(chain.from_iterable(groupednames))
#        print("")
#        print(groupednames)
        for item in range(len(DATA)):
            DATA[item]['SampleName']=groupednames[item]
        
        DATAMPP = sorted(DATAMPP, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATAMPP if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
        for item in range(len(groupednames)):
            if len(groupednames[item])!=1:
                for item0 in range(1,len(groupednames[item]),1):
                    groupednames[item][item0]+= "_"+str(item0)
        groupednames=list(chain.from_iterable(groupednames))
        for item in range(len(DATAMPP)):
            DATAMPP[item]['SampleName']=groupednames[item]
        
        self.change_value.emit(0)



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













