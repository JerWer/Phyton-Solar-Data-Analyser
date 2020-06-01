import sys
import datetime
import os
from pathlib import Path
import numpy as np
from statistics import mean
import sqlite3
#%%######################################################################################################
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Qt5Agg")
#%%######################################################################################################
from PyQt5 import QtWidgets
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
from scipy.interpolate import interp1d, UnivariateSpline
import math


from PyQt5.uic import loadUiType
Ui_MainWindow, QMainWindow = loadUiType('EQEgui.ui')

"""
- drag&drop listwidget
- SG filter
- check multiple file types and put some safety guards
- test exporting

"""


LARGE_FONT= ("Verdana", 12)

echarge = 1.60218e-19
planck = 6.62607e-34
lightspeed = 299792458

file = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'spectratxtfiles','AM15G.txt'), encoding='ISO-8859-1')
am15g = file.readlines()
file.close()
dataWave = []
dataInt = []
for i in range(len(am15g)):
    pos = am15g[i].find('\t')
    dataWave.append(float(am15g[i][:pos]))
    dataInt.append(float(am15g[i][pos+1:-1]))
  
SpectIntensFct = interp1d(dataWave,dataInt)

def modification_date(path_to_file):
    return datetime.datetime.fromtimestamp(os.path.getmtime(path_to_file)).strftime("%Y-%m-%d %H:%M:%S")

titEQE=0
firstimport=1
EQElegendMod=[]
DATAFORGRAPH=[]
DATAforexport=[]
takenforplot=[]
listofanswer=[]
listoflinestyle=[]
listofcolorstyle=[]
listoflinewidthstyle=[]
colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']
stitching=0

class EQEapp(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.fig = Figure()
        self.EQEgraph = self.fig.add_subplot(111)
        self.EQEgraphY2 = self.EQEgraph.twinx()
        self.addmpl(self.fig,self.ui.verticalLayout_mplwidget, self.ui.mplwidget)
        
        # self.ui.actionHelp.triggered.connect(self.Helpcall)
        self.ui.actionImport_DATA.triggered.connect(self.onOpenEQE)
        self.ui.actionExport_All_DATA.triggered.connect(self.sortandexportEQEdat)
        self.ui.actionExport_Graph_DATA.triggered.connect(self.ExportEQEGraph)
        
        # self.ui.pushButton_SGFilter.clicked.connect(self.SavitzkyGolayFiltering)
        # self.ui.pushButton_goback.clicked.connect(self.backtoOriginal)
        
        self.ui.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ui.listWidget.itemClicked.connect(self.select)
        
        self.ui.checkBox_legend.toggled.connect(self.UpdateEQEGraph)
        self.ui.radioButton_topleft.toggled.connect(self.UpdateEQEGraph)
        self.ui.radioButton_topright.toggled.connect(self.UpdateEQEGraph)
        self.ui.radioButton_bottomleft.toggled.connect(self.UpdateEQEGraph)
        self.ui.radioButton_bottomright.toggled.connect(self.UpdateEQEGraph)
        self.ui.radioButton_outside.toggled.connect(self.UpdateEQEGraph)
        self.ui.radioButton_best.toggled.connect(self.UpdateEQEGraph)
        self.ui.spinBox_fontsize.valueChanged.connect(self.UpdateEQEGraph)
        
        self.ui.checkBox_Jsc.toggled.connect(self.UpdateEQEGraph)
        self.ui.checkBox_Eg.toggled.connect(self.UpdateEQEGraph)
        
        self.ui.comboBox.currentTextChanged.connect(self.UpdateEQEGraph)
        self.ui.checkBox_integrJsc.toggled.connect(self.UpdateEQEGraph)
        self.ui.checkBox_showsecreteg.toggled.connect(self.UpdateEQEGraph)
        self.ui.pushButton_stitchEQEs.clicked.connect(self.StitchEQE)
        self.ui.pushButton_CalcCurrent.clicked.connect(self.CalcCurrent)
        
        # self.ui.pushButton_updatefromlistwidget.clicked.connect(self.select)


    def addmpl(self, fig, whereLayout, whereWidget):
        self.canvas = FigureCanvas(fig)
        whereLayout.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, 
                whereWidget, coordinates=True)
        whereLayout.addWidget(self.toolbar)
        
    def choiceYtype(self,a):
        self.UpdateEQEGraph()
        
    def onOpenEQE(self):
        global DATAFORGRAPH
        self.GetEQEDATA()
        self.initlistbox()
        
    def ncolumneqe(self, n):
        twocolumneqe = [['Wavelength','EQE'],['nm','-']]
        for i in range(1,n-1):
            twocolumneqe[0].append('EQE')
            twocolumneqe[1].append('-')
        return twocolumneqe
    def ncolumneqeJsc(self, n):
        twocolumneqe = [['Wavelength','Current density'],['nm','mA/cm2']]
        for i in range(1,n-1):
            twocolumneqe[0].append('Current density')
            twocolumneqe[1].append('mA/cm2')
        return twocolumneqe
    
    def AM15GParticlesinnm(self, x):
        return (x*10**(-9))*SpectIntensFct(x)/(planck*lightspeed)
    
    #%%###########        
    def GetEQEDATA(self):
        global DATAFORGRAPH
        global colorstylelist,firstimport,stitching
        
        if stitching==0:
            file_path = QFileDialog.getOpenFileNames(caption = 'Please select the eqe files')[0]
        else:
            file_path=[stitching]
            stitching=0
#        print(file_path[0])
#        print(modification_date(file_path[0]))
#        
#        print(os.path.basename(file_path[0].split('.')[0]))
#        print("")
        integrationJscYes=0
#        MsgBox = messagebox.askquestion("IntegrJsc?", "Do you want to calculate the Integrated Jsc curve?\nWarning: it will slow a bit down the importation")
#        if MsgBox == 'yes':
#            integrationJscYes=1
        
            
        directory = str(Path(file_path[0]).parent.parent)+'\\resultFilesEQE'
        
#        print(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.chdir(directory)
        else :
            os.chdir(directory)
        
        try:
            if firstimport:
                DATA=[] # [{'Name':, 'Jsc':, 'Eg':, 'NbColumn':, 'DATA': [[wavelength],[eqe],[eqe]...]}]
    #            AllNames = []
                firstimport=0
            else:
                DATA=copy.deepcopy(self.DATA)
    #            AllNames = []
        except:
            DATA=[] # [{'Name':, 'Jsc':, 'Eg':, 'NbColumn':, 'DATA': [[wavelength],[eqe],[eqe]...]}]
            firstimport=0
        
        # print(len(file_path))
        
        for k in range(len(file_path)):
            
            if os.path.splitext(file_path[k])[1]==".xls":
    #            samplename=os.path.basename(file_path[k].split('.')[0]).replace('-','_')  
                samplename=file_path[k].replace('\\','/') 
                samplename=samplename.split('/')[-1].replace('-','_').split('.')[0]
                
                print(samplename)
                batchnumb=samplename.split('_')[0]
                samplenumb=samplename.split('_')[1]
                
                wb = xlrd.open_workbook(file_path[k])
                sheet_names = wb.sheet_names()
                print('Sample: %2f' % float(k+1))    
                for j in range(len(sheet_names)):
                    if 'Sheet' not in sheet_names[j]:
#                        AllNames.append(sheet_names[j])
                        print(sheet_names[j])
                        xlsheet = wb.sheet_by_index(j)
                        cell1 = xlsheet.cell(0,0).value
                        rownb = cell1[cell1.index('(')+1:cell1.index('x')-1]
                        columnnb = cell1[cell1.index('x')+2:cell1.index(')')]
                        comment = xlsheet.cell(1,0).value
                        datetime=modification_date(file_path[k])
                        datadict = {'dateTime': datetime, 'filepath':file_path[k],'Name': sheet_names[j],'Jsc':[],'Eg':[],
                                    'EgTauc':[],'lnDat':[],'EgLn':[],'EuLn':[],'stderrEgLn':[],'NbColumn':columnnb, 
                                    'DATA': [],'tangent': [],'tangentLn': [], 'comment': comment, 'Vbias':[],'filterbias':[],'ledbias':[],
                                    'batchnumb': batchnumb, 'samplenumb': samplenumb}   
                        for i in range(int(columnnb)):
                            partdat = []
                            for h in range(3,int(rownb)+3,1):
                                partdat.append(xlsheet.cell(h,i).value)
                            datadict['DATA'].append(partdat)
                        if integrationJscYes:
                            datadict['integJsclist']=[datadict['DATA'][0]]
                        else:
                            datadict['integJsclist']=[[]]
    #                    try:
                        for i in range(1,int(columnnb),1):
                            cell1 = xlsheet.cell(2,i).value
                            datadict['Vbias'].append(cell1[cell1.index('=')+2:cell1.index(',')])
                            datadict['filterbias'].append(cell1[cell1.index(',')+2:cell1.index('L')-2])
                            datadict['ledbias'].append(cell1[cell1.index('#')+2:cell1.index('J')-2])
    #                            print(datadict['Vbias'])
                            #jsc calculation
                            x = datadict['DATA'][0]
                            y = datadict['DATA'][i]
                            if len(x)>3:
                                spl = UnivariateSpline(x, y, s=0)
                                f = interp1d(x, y, kind='cubic')
                                x2 = lambda x0: self.AM15GParticlesinnm(x0)*f(x0)
                                integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],datadict['DATA'][0][-1])[0]
                                datadict['Jsc'].append(integral)
                                print(datadict['Jsc'][-1])
                                integlist=[]
                                if integrationJscYes:
                                    for item in x:
                                        integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],item)[0]
                                        integlist.append(integral)
                                datadict['integJsclist'].append(integlist)
                                #Eg calculation from linear normal curve
                                splder = spl.derivative(n=1)
                                splderlist = []
                                newx=[]
                                for item in x :
                                    if item >400:
                                        splderlist.append(splder(item))
                                        newx.append(item)
                                minder=splderlist.index(min(splderlist))
                                xhighslope = newx[minder]
                                yhighslope = spl(newx[minder]).tolist()
                                yprimehighslope = splder(newx[minder]).tolist()
                                Eg= 1239.8/(xhighslope - yhighslope/yprimehighslope)
                                datadict['Eg'].append(Eg)
                                datadict['tangent'].append([yprimehighslope, yhighslope-yprimehighslope*xhighslope])#[pente,ordonnee a l'origine]
    
                                #Eg calculation from ln(EQE) curve
                                xE=[]
                                yln=[]
                                for xi in range(len(x)):
                                    if y[xi]>0:
                                        xE.append(1239.8/x[xi])
                                        yln.append(math.log(100*y[xi]))
    
                                datadict['lnDat'].append([xE,yln])
                                
                                xErestricted=[]
                                ylnrestricted=[]
                                
                                for xi in range(len(xE)-1,-1,-1):
                                    if yln[xi]<3 and yln[xi]>-2:
                                        xErestricted.append(xE[xi])
                                        ylnrestricted.append(yln[xi])
                                xErestricted.append(999)
                                ylnrestricted.append(999)
                                xErestricted2=[]
                                ylnrestricted2=[]
                                for xi in range(len(xErestricted)-1):
                                    xErestricted2.append(xErestricted[xi])
                                    ylnrestricted2.append(ylnrestricted[xi])
                                    if abs(xErestricted[xi]-xErestricted[xi+1])>0.3:
                                        break
                                if len(xErestricted2)>1:
                                    slope, intercept, r_value, p_value, std_err = stats.linregress(xErestricted2,ylnrestricted2)
                                                                    
                                    datadict['EgLn'].append(-intercept/slope)
                                    datadict['EuLn'].append(1000/slope)#Eu calculation from ln(EQE) curve slope at band edge
                                    datadict['tangentLn'].append([slope, intercept,xErestricted2,ylnrestricted2])#[pente,ordonnee a l'origine]
                                    datadict['stderrEgLn'].append([std_err,len(xErestricted2)])
                                else:
                                    print("EgLn not found enough points...")
                                    datadict['EgLn'].append(999)
                                    datadict['EuLn'].append(999)#Eu calculation from ln(EQE) curve slope at band edge
                                    datadict['tangentLn'].append([999, 999,[999],[999]])#[pente,ordonnee a l'origine]
                                    datadict['stderrEgLn'].append([999,999])
                                
                                #Tauc plots
                                try:
                                    xtauc=[1239.8/xm for xm in x]
                                    ytauc=[((math.log(1-y[m]))**2)*(xtauc[m]**2) for m in range(len(y)) ]
                                    xtauc=xtauc[::-1]
                                    ytauc=ytauc[::-1]
                                    spl = UnivariateSpline(xtauc, ytauc, s=0)
                                    splder = spl.derivative(n=1)
                                    splderlist = []
                                    newx=[]
                                    for item in xtauc :
                                        if item <2:
                                            splderlist.append(splder(item))
                                            newx.append(item)
                                    
                                    maxder=splderlist.index(max(splderlist))
                                    xhighslope = newx[maxder]
                                    yhighslope = spl(newx[maxder]).tolist()
                                    yprimehighslope = splder(newx[maxder]).tolist()
                                    Eg= (xhighslope - yhighslope/yprimehighslope)
                                    
                                    m=yprimehighslope
                                    h=yhighslope-yprimehighslope*xhighslope
                                    x2=Eg
                                    x=np.linspace(x2,x2+0.1,10)
                                    y=eval('m*x+h')
                                    datadict['EgTauc'].append([Eg,xtauc,ytauc,m,h])
                                except:
                                    datadict['EgTauc'].append([999,[],[],999,999])
                                                            
                            else:
                                datadict['EgTauc'].append([999,[],[],999,999])
                                datadict['Jsc'].append(999)
                                datadict['Eg'].append(999)
                                datadict['tangent'].append([999, 999])#[pente,ordonnee a l'origine]
                                datadict['EgLn'].append(999)
                                datadict['EuLn'].append(999)#Eu calculation from ln(EQE) curve slope at band edge
                                datadict['tangentLn'].append([999, 999,[999],[999]])#[pente,ordonnee a l'origine]
                                datadict['stderrEgLn'].append([999,999])
                                datadict['lnDat'].append([[999],[999]])
        
    #                    except:
    #                        print("some error with m>k in Spline...")
                        DATA.append(datadict)
            elif os.path.splitext(file_path[k])[1]==".txt":
                
                file = open(file_path[k], encoding='ISO-8859-1')
                filedat = file.readlines()
                file.close()
                if filedat[1].split('\t')[0]!='':
                    samplename=file_path[k].replace('\\','/') 
                    samplename=samplename.split('/')[-1].replace('-','_').split('.')[0]
                    print(samplename)
    #                AllNames.append(samplename)
                    batchnumb=samplename.split('_')[0]
                    samplenumb=samplename.split('_')[1]
                    
                    
                    datetime=modification_date(file_path[k])
                    datadict = {'dateTime': datetime, 'filepath':file_path[k],'Name': samplename,'Jsc':[],'Eg0':[],'EgIP':[],
                                        'EgTauc':[],'EgTauc2':[],'lnDat':[],'EgLn':[],'EuLn':[],'stderrEgLn':[],'NbColumn':2, 
                                        'DATA': [],'tangent': [],'tangentLn': [], 'comment': "", 'Vbias':[],'filterbias':[],'ledbias':[],
                                        'batchnumb': batchnumb, 'samplenumb': samplenumb}   
                    
                    
                    datadict['DATA']=[[],[]]
                    for item in filedat:
                        try:
                            datadict['DATA'][0].append(float(item.split('\t')[0]))
                            datadict['DATA'][1].append(float(item.split('\t')[1]))
                        except:
                            pass
                    
                    m=list(zip(*sorted(zip(datadict['DATA'][0],datadict['DATA'][1]), key=lambda pair: pair[0])))
                    
                    datadict['DATA'][0]=list(m[0])
                    datadict['DATA'][1]=list(m[1])
                    x=datadict['DATA'][0]
                    y=datadict['DATA'][1]
                    spl = UnivariateSpline(x, y, s=0)
                    f = interp1d(x, y, kind='cubic')
                    x2 = lambda x0: self.AM15GParticlesinnm(x0)*f(x0)
                    integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],datadict['DATA'][0][-1])[0]
                    datadict['Jsc'].append(integral)
                    if integrationJscYes:
                        datadict['integJsclist']=[datadict['DATA'][0]]
                    else:
                        datadict['integJsclist']=[[]]
                    integlist=[]
                    if integrationJscYes:
                        for item in x:
                            integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],item)[0]
                            integlist.append(integral)
                    datadict['integJsclist'].append(integlist)
                                  
                    #Eg calculation from linear normal curve
                    splder = spl.derivative(n=1)
                    splderlist = []
                    newx=[]
                    for item in x :
                        if item >400:
                            splderlist.append(splder(item))
                            newx.append(item)
                    if splderlist==[]:
                        datadict['Eg0'].append(0)
                        datadict['tangent'].append([0, 0])
                    else:
                        minder=splderlist.index(min(splderlist))
                        xhighslope = newx[minder]
                        datadict['EgIP'].append(1239.8/xhighslope)
                        yhighslope = spl(newx[minder]).tolist()
                        yprimehighslope = splder(newx[minder]).tolist()
                        Eg= 1239.8/(xhighslope - yhighslope/yprimehighslope)#intercept of x-axis
                        datadict['Eg0'].append(Eg)
                        datadict['tangent'].append([yprimehighslope, yhighslope-yprimehighslope*xhighslope])#[pente,ordonnee a l'origine]
                        print('EgIP: ', datadict['EgIP'][0])
                        print('Eg0: ', datadict['Eg0'][0])
        
                    #Eg calculation from ln(EQE) curve
                    xE=[]
                    yln=[]
                    for xi in range(len(x)):
                        if y[xi]>0:
                            xE.append(1239.8/x[xi])
                            yln.append(math.log(100*y[xi]))
    
                    datadict['lnDat'].append([xE,yln])
                    
                    xErestricted=[]
                    ylnrestricted=[]
                    
                    for xi in range(len(xE)-1,-1,-1):
                        if yln[xi]<3 and yln[xi]>-2:
                            xErestricted.append(xE[xi])
                            ylnrestricted.append(yln[xi])
                    xErestricted.append(999)
                    ylnrestricted.append(999)
                    xErestricted2=[]
                    ylnrestricted2=[]
                    for xi in range(len(xErestricted)-1):
                        xErestricted2.append(xErestricted[xi])
                        ylnrestricted2.append(ylnrestricted[xi])
                        if abs(xErestricted[xi]-xErestricted[xi+1])>0.3:
                            break
                    if len(xErestricted2)>1:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(xErestricted2,ylnrestricted2)
                                                        
                        datadict['EgLn'].append(-intercept/slope)
                        datadict['EuLn'].append(1000/slope)#Eu calculation from ln(EQE) curve slope at band edge
                        datadict['tangentLn'].append([slope, intercept,xErestricted2,ylnrestricted2])#[pente,ordonnee a l'origine]
                        datadict['stderrEgLn'].append([std_err,len(xErestricted2)])
                    else:
                        print("EgLn not found enough points...")
                        datadict['EgLn'].append(999)
                        datadict['EuLn'].append(999)#Eu calculation from ln(EQE) curve slope at band edge
                        datadict['tangentLn'].append([999, 999,[999],[999]])#[pente,ordonnee a l'origine]
                        datadict['stderrEgLn'].append([999,999])
                    
                    #Tauc plots
#                    try:
#                        xtauc=[1239.8/xm for xm in x]
#                        ytauc=[((math.log(1-y[m]))**2)*(xtauc[m]**2) for m in range(len(y)) ]
#                        xtauc=xtauc[::-1]
#                        ytauc=ytauc[::-1]
#                        spl = UnivariateSpline(xtauc, ytauc, s=0)
#                        splder = spl.derivative(n=1)
#                        splderlist = []
#                        newx=[]
#                        for item in xtauc :
#                            if item <2:
#                                splderlist.append(splder(item))
#                                newx.append(item)
#                        
#                        maxder=splderlist.index(max(splderlist))
#                        xhighslope = newx[maxder]
#                        yhighslope = spl(newx[maxder]).tolist()
#                        yprimehighslope = splder(newx[maxder]).tolist()
#                        Eg= (xhighslope - yhighslope/yprimehighslope)
#                        
#                        m=yprimehighslope
#                        h=yhighslope-yprimehighslope*xhighslope
#                        x2=Eg
#                        x=np.linspace(x2,x2+0.1,10)
#                        y=eval('m*x+h')
#                        datadict['EgTauc2'].append([Eg,xtauc,ytauc,m,h])
#                    except:
#                        datadict['EgTauc2'].append([999,[],[],999,999])
                    
                    try:
                        xtauc=[1239.8/xm for xm in x]
                        ytauc=[(y[m]*xtauc[m])**2 for m in range(len(y)) ]
                        xtauc=xtauc[::-1]
                        ytauc=ytauc[::-1]
                        spl = UnivariateSpline(xtauc, ytauc, s=0)
                        splder = spl.derivative(n=1)
                        splderlist = []
                        newx=[]
                        for item in xtauc :
                            if item <2:
                                splderlist.append(splder(item))
                                newx.append(item)
                        
                        maxder=splderlist.index(max(splderlist))
                        xhighslope = newx[maxder]
                        yhighslope = spl(newx[maxder]).tolist()
                        yprimehighslope = splder(newx[maxder]).tolist()
                        Eg= (xhighslope - yhighslope/yprimehighslope)
                        
                        m=yprimehighslope
                        h=yhighslope-yprimehighslope*xhighslope
                        x2=Eg
                        x=np.linspace(x2,x2+0.1,10)
                        y=eval('m*x+h')
                        datadict['EgTauc'].append([Eg,xtauc,ytauc,m,h])
                    except:
                        datadict['EgTauc'].append([999,[],[],999,999])
                    
#                    print('EgTauc: ', datadict['EgTauc'][0][0])                    

                    
                    datadict['Vbias'].append('')
                    datadict['filterbias'].append('')
                    datadict['ledbias'].append('')
                    
                    
                    DATA.append(datadict)
                else:#for III-V EQE setup NREL
                    print('EQEiii-v')
                    firstline=filedat[0].split('\t')
                    columnsofEQE=[]
                    columnsofIQE=[]
                    for item in range(len(firstline)):
                        if 'EQE' in firstline[item]:
                            columnsofEQE.append(item)
                        elif 'IQE' in firstline[item]:
                            columnsofIQE.append(item)
                    
                    #select EQE&IQE meas
                    for indexEQE in columnsofEQE+columnsofIQE:
                        samplename=firstline[indexEQE]
                        samplename=samplename.split('/')[-1].replace('-','_').split('.')[0]
                        
                        datetime=modification_date(file_path[k])
                        datadict = {'dateTime': datetime, 'filepath':file_path[k],'Name': samplename,'Jsc':[],'Eg':[],
                                        'EgTauc':[],'lnDat':[],'EgLn':[],'EuLn':[],'stderrEgLn':[],'NbColumn':2, 
                                        'DATA': [],'tangent': [],'tangentLn': [], 'comment': "", 'Vbias':[],'filterbias':[],'ledbias':[],
                                        'batchnumb': '', 'samplenumb': ''}   
                        datadict['DATA']=[[],[]]
                        for row in range(1,len(filedat)):
                            if filedat[row].split('\t')[indexEQE+1]!='':
                                datadict['DATA'][0].append(float(filedat[row].split('\t')[indexEQE+1]))
                                datadict['DATA'][1].append(float(filedat[row].split('\t')[indexEQE+2]))

                        m=list(zip(*sorted(zip(datadict['DATA'][0],datadict['DATA'][1]), key=lambda pair: pair[0])))
                
                        datadict['DATA'][0]=list(m[0])
                        datadict['DATA'][1]=list(m[1])
                        x=datadict['DATA'][0]
                        y=datadict['DATA'][1]
                        spl = UnivariateSpline(x, y, s=0)
                        f = interp1d(x, y, kind='cubic')
                        x2 = lambda x0: self.AM15GParticlesinnm(x0)*f(x0)
                        integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],datadict['DATA'][0][-1])[0]
                        datadict['Jsc'].append(integral)
                        if integrationJscYes:
                            datadict['integJsclist']=[datadict['DATA'][0]]
                        else:
                            datadict['integJsclist']=[[]]
                        integlist=[]
                        if integrationJscYes:
                            for item in x:
                                integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],item)[0]
                                integlist.append(integral)
                        datadict['integJsclist'].append(integlist)
                                      
                        #Eg calculation from linear normal curve
                        splder = spl.derivative(n=1)
                        splderlist = []
                        newx=[]
                        for item in x :
                            if item >400:
                                splderlist.append(splder(item))
                                newx.append(item)
                        minder=splderlist.index(min(splderlist))
                        xhighslope = newx[minder]
                        yhighslope = spl(newx[minder]).tolist()
                        yprimehighslope = splder(newx[minder]).tolist()
                        Eg= 1239.8/(xhighslope - yhighslope/yprimehighslope)
                        datadict['Eg'].append(Eg)
                        datadict['tangent'].append([yprimehighslope, yhighslope-yprimehighslope*xhighslope])#[pente,ordonnee a l'origine]
            
                        #Eg calculation from ln(EQE) curve
                        xE=[]
                        yln=[]
                        for xi in range(len(x)):
                            if y[xi]>0:
                                xE.append(1239.8/x[xi])
                                yln.append(math.log(100*y[xi]))
        
                        datadict['lnDat'].append([xE,yln])
                        
                        xErestricted=[]
                        ylnrestricted=[]
                        
                        for xi in range(len(xE)-1,-1,-1):
                            if yln[xi]<3 and yln[xi]>-2:
                                xErestricted.append(xE[xi])
                                ylnrestricted.append(yln[xi])
                        xErestricted.append(999)
                        ylnrestricted.append(999)
                        xErestricted2=[]
                        ylnrestricted2=[]
                        for xi in range(len(xErestricted)-1):
                            xErestricted2.append(xErestricted[xi])
                            ylnrestricted2.append(ylnrestricted[xi])
                            if abs(xErestricted[xi]-xErestricted[xi+1])>0.3:
                                break
                        if len(xErestricted2)>1:
                            slope, intercept, r_value, p_value, std_err = stats.linregress(xErestricted2,ylnrestricted2)
                                                            
                            datadict['EgLn'].append(-intercept/slope)
                            datadict['EuLn'].append(1000/slope)#Eu calculation from ln(EQE) curve slope at band edge
                            datadict['tangentLn'].append([slope, intercept,xErestricted2,ylnrestricted2])#[pente,ordonnee a l'origine]
                            datadict['stderrEgLn'].append([std_err,len(xErestricted2)])
                        else:
                            print("EgLn not found enough points...")
                            datadict['EgLn'].append(999)
                            datadict['EuLn'].append(999)#Eu calculation from ln(EQE) curve slope at band edge
                            datadict['tangentLn'].append([999, 999,[999],[999]])#[pente,ordonnee a l'origine]
                            datadict['stderrEgLn'].append([999,999])
                        
                        #Tauc plots
                        try:
                            xtauc=[1239.8/xm for xm in x]
                            ytauc=[((math.log(1-y[m]))**2)*(xtauc[m]**2) for m in range(len(y)) ]
                            xtauc=xtauc[::-1]
                            ytauc=ytauc[::-1]
                            spl = UnivariateSpline(xtauc, ytauc, s=0)
                            splder = spl.derivative(n=1)
                            splderlist = []
                            newx=[]
                            for item in xtauc :
                                if item <2:
                                    splderlist.append(splder(item))
                                    newx.append(item)
                            
                            maxder=splderlist.index(max(splderlist))
                            xhighslope = newx[maxder]
                            yhighslope = spl(newx[maxder]).tolist()
                            yprimehighslope = splder(newx[maxder]).tolist()
                            Eg= (xhighslope - yhighslope/yprimehighslope)
                            
                            m=yprimehighslope
                            h=yhighslope-yprimehighslope*xhighslope
                            x2=Eg
                            x=np.linspace(x2,x2+0.1,10)
                            y=eval('m*x+h')
                            datadict['EgTauc'].append([Eg,xtauc,ytauc,m,h])
                        except:
                            datadict['EgTauc'].append([999,[],[],999,999])
                                            
                        datadict['Vbias'].append('')
                        datadict['filterbias'].append('')
                        datadict['ledbias'].append('')
                        
                        
                        DATA.append(datadict)
                        
                    #calculate reflectance meas
                    for indexEQE in range(len(columnsofEQE)):
                        if firstline[columnsofEQE[indexEQE]][:-3]==firstline[columnsofIQE[indexEQE]][:-3]:
                            samplename=firstline[columnsofEQE[indexEQE]][:-3]
                            datadict = {'dateTime': datetime, 'filepath':'','Name': samplename +'_R','Jsc':[],'Eg':[],
                                                'EgTauc':[],'lnDat':[],'EgLn':[],'EuLn':[],'stderrEgLn':[],'NbColumn':2, 
                                                'DATA': [],'tangent': [],'tangentLn': [], 'comment': "", 'Vbias':[],
                                                'filterbias':[],'ledbias':[],
                                                'batchnumb': '', 'samplenumb': ''} 
                            datadict['DATA']=[[],[]]
                            for row in range(1,len(filedat)):
                                if filedat[row].split('\t')[columnsofEQE[indexEQE]+1]!='':
                                    datadict['DATA'][0].append(float(filedat[row].split('\t')[columnsofEQE[indexEQE]+1]))
                                    datadict['DATA'][1].append(1-float(filedat[row].split('\t')[columnsofEQE[indexEQE]+2])/float(filedat[row].split('\t')[columnsofIQE[indexEQE]+2]))
                            
                            m=list(zip(*sorted(zip(datadict['DATA'][0],datadict['DATA'][1]), key=lambda pair: pair[0])))
                            
                            datadict['DATA'][0]=list(m[0])
                            datadict['DATA'][1]=list(m[1])
                            
                            x=datadict['DATA'][0]
                            y=datadict['DATA'][1]
            #                print(x)
                            spl = UnivariateSpline(x, y, s=0)
                            f = interp1d(x, y, kind='cubic')
                            x2 = lambda x0: self.AM15GParticlesinnm(x0)*f(x0)
                            integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],datadict['DATA'][0][-1])[0]
                            datadict['Jsc'].append(integral)
                            
                            datadict['integJsclist']=[[],[]]
                            datadict['EgTauc'].append([99,[],[],99,99])
                            datadict['Eg'].append(99)
                            datadict['tangent'].append([99, 99])#[pente,ordonnee a l'origine]
                            datadict['EgLn'].append(99)
                            datadict['EuLn'].append(99)#Eu calculation from ln(EQE) curve slope at band edge
                            datadict['tangentLn'].append([99, 99,[99],[99]])#[pente,ordonnee a l'origine]
                            datadict['stderrEgLn'].append([99,99])
                            datadict['lnDat'].append([[99],[99]])                
                            datadict['Vbias'].append('')
                            datadict['filterbias'].append('')
                            datadict['ledbias'].append('')
                            DATA.append(datadict)        
            
            elif os.path.splitext(file_path[k])[1]=='': #file from NREL S&TF 136
#                print(os.path.splitext(file_path[k])[1])
#                print(file_path[k])
#                print('')
                samplename=file_path[k].replace('\\','/') 
                samplename=samplename.split('/')[-1].replace('-','_').split('.')[0]
                print(samplename)
#                AllNames.append(samplename)
                batchnumb=samplename.split('_')[0]
                samplenumb=samplename.split('_')[1]
                
                
                if 'header' not in samplename:
                    file = open(file_path[k], encoding='ISO-8859-1')
                    filedat = file.readlines()
                    file.close()
                    datetime=modification_date(file_path[k])
                    datadict = {'dateTime': datetime, 'filepath':file_path[k],'Name': samplename,'Jsc':[],'Eg0':[],'EgIP':[],
                                        'EgTauc':[],'EgTauc2':[],'lnDat':[],'EgLn':[],'EuLn':[],'stderrEgLn':[],'NbColumn':2, 
                                        'DATA': [],'tangent': [],'tangentLn': [], 'comment': "", 'Vbias':[],'filterbias':[],'ledbias':[],
                                        'batchnumb': batchnumb, 'samplenumb': samplenumb} 
    
                    #get EQE data
                    datadict['DATA']=[[],[]]
    #                filedat.pop(0)
                    for item in filedat:
#                        print(item.split('\t')[0])
                        if item.split('\t')[0] !='\n':
                            datadict['DATA'][0].append(float(item.split('\t')[0]))
                            datadict['DATA'][1].append(float(item.split('\t')[7])/100)
                    
                    m=list(zip(*sorted(zip(datadict['DATA'][0],datadict['DATA'][1]), key=lambda pair: pair[0])))
                    
                    datadict['DATA'][0]=list(m[0])
                    datadict['DATA'][1]=list(m[1])
                    x=datadict['DATA'][0]
                    y=datadict['DATA'][1]
    #                print(x)
                    spl = UnivariateSpline(x, y, s=0)
                    f = interp1d(x, y, kind='cubic')
                    x2 = lambda x0: self.AM15GParticlesinnm(x0)*f(x0)
                    if datadict['DATA'][0][0]>280:
                        integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],datadict['DATA'][0][-1])[0]
                    else:
                        integral = echarge/10*integrate.quad(x2,280,datadict['DATA'][0][-1])[0]
                    datadict['Jsc'].append(integral)
                    if integrationJscYes:
                        datadict['integJsclist']=[datadict['DATA'][0]]
                    else:
                        datadict['integJsclist']=[[]]
                    integlist=[]
                    if integrationJscYes:
                        for item in x:
                            integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],item)[0]
                            integlist.append(integral)
                    datadict['integJsclist'].append(integlist)
                                  
                    #Eg calculation from linear normal curve
                    splder = spl.derivative(n=1)
                    splderlist = []
                    newx=[]
                    for item in x :
                        if item >400:
                            splderlist.append(splder(item))
                            newx.append(item)
                    minder=splderlist.index(min(splderlist))
                    xhighslope = newx[minder]
                    datadict['EgIP'].append(1239.8/xhighslope)
                    yhighslope = spl(newx[minder]).tolist()
                    yprimehighslope = splder(newx[minder]).tolist()
                    Eg= 1239.8/(xhighslope - yhighslope/yprimehighslope)
                    datadict['Eg0'].append(Eg)
                    datadict['tangent'].append([yprimehighslope, yhighslope-yprimehighslope*xhighslope])#[pente,ordonnee a l'origine]
        
                    #Eg calculation from ln(EQE) curve
                    xE=[]
                    yln=[]
                    for xi in range(len(x)):
                        if y[xi]>0:
                            xE.append(1239.8/x[xi])
                            yln.append(math.log(100*y[xi]))
    
                    datadict['lnDat'].append([xE,yln])
                    
                    xErestricted=[]
                    ylnrestricted=[]
                    
                    for xi in range(len(xE)-1,-1,-1):
                        if yln[xi]<3 and yln[xi]>-2:
                            xErestricted.append(xE[xi])
                            ylnrestricted.append(yln[xi])
                    xErestricted.append(999)
                    ylnrestricted.append(999)
                    xErestricted2=[]
                    ylnrestricted2=[]
                    for xi in range(len(xErestricted)-1):
                        xErestricted2.append(xErestricted[xi])
                        ylnrestricted2.append(ylnrestricted[xi])
                        if abs(xErestricted[xi]-xErestricted[xi+1])>0.3:
                            break
                    if len(xErestricted2)>1:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(xErestricted2,ylnrestricted2)
                                                        
                        datadict['EgLn'].append(-intercept/slope)
                        datadict['EuLn'].append(1000/slope)#Eu calculation from ln(EQE) curve slope at band edge
                        datadict['tangentLn'].append([slope, intercept,xErestricted2,ylnrestricted2])#[pente,ordonnee a l'origine]
                        datadict['stderrEgLn'].append([std_err,len(xErestricted2)])
                    else:
                        print("EgLn not found enough points...")
                        datadict['EgLn'].append(999)
                        datadict['EuLn'].append(999)#Eu calculation from ln(EQE) curve slope at band edge
                        datadict['tangentLn'].append([999, 999,[999],[999]])#[pente,ordonnee a l'origine]
                        datadict['stderrEgLn'].append([999,999])
                    
                    #Tauc plots
#                    try:
#                        xtauc=[1239.8/xm for xm in x]
#                        ytauc=[((math.log(1-y[m]))**2)*(xtauc[m]**2) for m in range(len(y)) ]
#                        xtauc=xtauc[::-1]
#                        ytauc=ytauc[::-1]
#                        spl = UnivariateSpline(xtauc, ytauc, s=0)
#                        splder = spl.derivative(n=1)
#                        splderlist = []
#                        newx=[]
#                        for item in xtauc :
#                            if item <2:
#                                splderlist.append(splder(item))
#                                newx.append(item)
#                        
#                        maxder=splderlist.index(max(splderlist))
#                        xhighslope = newx[maxder]
#                        yhighslope = spl(newx[maxder]).tolist()
#                        yprimehighslope = splder(newx[maxder]).tolist()
#                        Eg= (xhighslope - yhighslope/yprimehighslope)
#                        
#                        m=yprimehighslope
#                        h=yhighslope-yprimehighslope*xhighslope
#                        x2=Eg
#                        x=np.linspace(x2,x2+0.1,10)
#                        y=eval('m*x+h')
#                        datadict['EgTauc'].append([Eg,xtauc,ytauc,m,h])
#                    except:
#                        datadict['EgTauc'].append([999,[],[],999,999])
                        
                    try:
                        xtauc=[1239.8/xm for xm in x]
                        ytauc=[(y[m]*xtauc[m])**2 for m in range(len(y)) ]
                        xtauc=xtauc[::-1]
                        ytauc=ytauc[::-1]
                        spl = UnivariateSpline(xtauc, ytauc, s=0)
                        splder = spl.derivative(n=1)
                        splderlist = []
                        newx=[]
                        for item in xtauc :
                            if item <2:
                                splderlist.append(splder(item))
                                newx.append(item)
                        
                        maxder=splderlist.index(max(splderlist))
                        xhighslope = newx[maxder]
                        yhighslope = spl(newx[maxder]).tolist()
                        yprimehighslope = splder(newx[maxder]).tolist()
                        Eg= (xhighslope - yhighslope/yprimehighslope)
                        
                        m=yprimehighslope
                        h=yhighslope-yprimehighslope*xhighslope
                        x2=Eg
                        x=np.linspace(x2,x2+0.1,10)
                        y=eval('m*x+h')
                        datadict['EgTauc'].append([Eg,xtauc,ytauc,m,h])
                    except:
                        datadict['EgTauc'].append([999,[],[],999,999])    
                        
                        
                    datadict['Vbias'].append('')
                    datadict['filterbias'].append('')
                    datadict['ledbias'].append('')                   
                    DATA.append(datadict)
                    
#                    print(filedat[1].split('\t'))
#                    if 'NaN' not in filedat[1].split('\t')[8]:
#                        print('')
#                        #get IQE data
#                        datadict = {'dateTime': datetime, 'filepath':file_path[k],'Name': samplename +'_IQE','Jsc':[],'Eg':[],
#                                            'EgTauc':[],'lnDat':[],'EgLn':[],'EuLn':[],'stderrEgLn':[],'NbColumn':2, 
#                                            'DATA': [],'tangent': [],'tangentLn': [], 'comment': "", 'Vbias':[],
#                                            'filterbias':[],'ledbias':[],
#                                            'batchnumb': batchnumb +'_IQE', 'samplenumb': samplenumb +'_IQE'} 
#                        datadict['DATA']=[[],[]]
#    #                    filedat.pop(0)
#                        for item in filedat:
#                            datadict['DATA'][0].append(float(item.split('\t')[0]))
#                            datadict['DATA'][1].append(float(item.split('\t')[8])/100)
#                        
#                        m=list(zip(*sorted(zip(datadict['DATA'][0],datadict['DATA'][1]), key=lambda pair: pair[0])))
#                        
#                        datadict['DATA'][0]=list(m[0])
#                        datadict['DATA'][1]=list(m[1])
#                        
#                        x=datadict['DATA'][0]
#                        y=datadict['DATA'][1]
#        #                print(x)
#                        spl = UnivariateSpline(x, y, s=0)
#                        f = interp1d(x, y, kind='cubic')
#                        x2 = lambda x0: self.AM15GParticlesinnm(x0)*f(x0)
#                        integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],datadict['DATA'][0][-1])[0]
#                        datadict['Jsc'].append(integral)
#                        if integrationJscYes:
#                            datadict['integJsclist']=[datadict['DATA'][0]]
#                        else:
#                            datadict['integJsclist']=[[]]
#                        integlist=[]
#                        if integrationJscYes:
#                            for item in x:
#                                integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],item)[0]
#                                integlist.append(integral)
#                        datadict['integJsclist'].append(integlist)
#                        #Eg calculation from linear normal curve
#                        splder = spl.derivative(n=1)
#                        splderlist = []
#                        newx=[]
#                        for item in x :
#                            if item >400:
#                                splderlist.append(splder(item))
#                                newx.append(item)
#                        minder=splderlist.index(min(splderlist))
#                        xhighslope = newx[minder]
#                        yhighslope = spl(newx[minder]).tolist()
#                        yprimehighslope = splder(newx[minder]).tolist()
#                        Eg= 1239.8/(xhighslope - yhighslope/yprimehighslope)
#                        datadict['Eg'].append(Eg)
#                        datadict['tangent'].append([yprimehighslope, yhighslope-yprimehighslope*xhighslope])#[pente,ordonnee a l'origine]
#        
#                        
#                        datadict['integJsclist']=[[],[]]
#                        datadict['EgTauc'].append([99,[],[],99,99])
#                        datadict['EgLn'].append(99)
#                        datadict['EuLn'].append(99)#Eu calculation from ln(EQE) curve slope at band edge
#                        datadict['tangentLn'].append([99, 99,[99],[99]])#[pente,ordonnee a l'origine]
#                        datadict['stderrEgLn'].append([99,99])
#                        datadict['lnDat'].append([[99],[99]]) 
#                        datadict['Vbias'].append('')
#                        datadict['filterbias'].append('')
#                        datadict['ledbias'].append('')
#                        DATA.append(datadict)
#                        
                        #get R data
#                        datadict = {'dateTime': datetime, 'filepath':file_path[k],'Name': samplename +'_R','Jsc':[],'Eg':[],
#                                            'EgTauc':[],'lnDat':[],'EgLn':[],'EuLn':[],'stderrEgLn':[],'NbColumn':2, 
#                                            'DATA': [],'tangent': [],'tangentLn': [], 'comment': "", 'Vbias':[],
#                                            'filterbias':[],'ledbias':[],
#                                            'batchnumb': batchnumb +'_R', 'samplenumb': samplenumb +'_R'} 
#                        datadict['DATA']=[[],[]]
#    #                    filedat.pop(0)
#                        for item in filedat:
#                            datadict['DATA'][0].append(float(item.split('\t')[0]))
#                            datadict['DATA'][1].append(float(item.split('\t')[9])/100)
#                        
#                        m=list(zip(*sorted(zip(datadict['DATA'][0],datadict['DATA'][1]), key=lambda pair: pair[0])))
#                        
#                        datadict['DATA'][0]=list(m[0])
#                        datadict['DATA'][1]=list(m[1])
#                        
#                        x=datadict['DATA'][0]
#                        y=datadict['DATA'][1]
#        #                print(x)
#                        spl = UnivariateSpline(x, y, s=0)
#                        f = interp1d(x, y, kind='cubic')
#                        x2 = lambda x0: self.AM15GParticlesinnm(x0)*f(x0)
#                        integral = echarge/10*integrate.quad(x2,datadict['DATA'][0][0],datadict['DATA'][0][-1])[0]
#                        datadict['Jsc'].append(integral)
#                        
#                        datadict['integJsclist']=[[],[]]
#                        datadict['EgTauc'].append([99,[],[],99,99])
#                        datadict['Eg'].append(99)
#                        datadict['tangent'].append([99, 99])#[pente,ordonnee a l'origine]
#                        datadict['EgLn'].append(99)
#                        datadict['EuLn'].append(99)#Eu calculation from ln(EQE) curve slope at band edge
#                        datadict['tangentLn'].append([99, 99,[99],[99]])#[pente,ordonnee a l'origine]
#                        datadict['stderrEgLn'].append([99,99])
#                        datadict['lnDat'].append([[99],[99]])                
#                        datadict['Vbias'].append('')
#                        datadict['filterbias'].append('')
#                        datadict['ledbias'].append('')
#                        DATA.append(datadict)                
#                        #get SR data
#                        datadict = {'dateTime': datetime, 'filepath':file_path[k],'Name': samplename +'_SR','Jsc':[],'Eg':[],
#                                            'EgTauc':[],'lnDat':[],'EgLn':[],'EuLn':[],'stderrEgLn':[],'NbColumn':2, 
#                                            'DATA': [],'tangent': [],'tangentLn': [], 'comment': "", 'Vbias':[],
#                                            'filterbias':[],'ledbias':[],
#                                            'batchnumb': batchnumb +'_SR', 'samplenumb': samplenumb +'_SR'} 
#                        datadict['DATA']=[[],[]]
#                        filedat.pop(0)
#                        for item in filedat:
#                            datadict['DATA'][0].append(float(item.split('\t')[0]))
#                            datadict['DATA'][1].append(float(item.split('\t')[10]))
#                        
#                        m=list(zip(*sorted(zip(datadict['DATA'][0],datadict['DATA'][1]), key=lambda pair: pair[0])))
#                        
#                        datadict['DATA'][0]=list(m[0])
#                        datadict['DATA'][1]=list(m[1])
#                        
#                        datadict['integJsclist']=[[],[]]
#                        datadict['EgTauc'].append([99,[],[],99,99])
#                        datadict['Jsc'].append(99)
#                        datadict['Eg'].append(99)
#                        datadict['tangent'].append([99, 99])#[pente,ordonnee a l'origine]
#                        datadict['EgLn'].append(99)
#                        datadict['EuLn'].append(99)#Eu calculation from ln(EQE) curve slope at band edge
#                        datadict['tangentLn'].append([99, 99,[99],[99]])#[pente,ordonnee a l'origine]
#                        datadict['stderrEgLn'].append([99,99])
#                        datadict['lnDat'].append([[99],[99]])                
#                        datadict['Vbias'].append('')
#                        datadict['filterbias'].append('')
#                        datadict['ledbias'].append('')
#                        DATA.append(datadict)                 
                
                
                

        print(len(DATA))
        self.DATA=DATA
        DATAforgraph=[] # [0 samplenameshort, 1 jsc, 2 dataWave, 3 dataInt, 4 Eg, 5 NameMod, 6 Name_Jsc, 7 Name_Eg, 8 Name_Jsc_Eg, 9 linestyle, 10 linecolor, 11 slope, 12 h, 13 slopeLn, 14 hln, 
                            #15 dataEnergyLn, 16 dataIntLn, 17 ptstgtLnX, 18 ptstgtLnY, 19 EgTauc, 20 xtauc, 21 ytauc, 22 mtauc, 23 htauc, 24 Name_Egln, 25 Name_Jsc_Egln, 26 Name_Egtauc, 27 Name_Jsc_Egtauc, 28 integJsclist , 29 linewidth]
        for i in range(len(DATA)):
            for j in range(len(DATA[i]['Jsc'])):
                DATAforgraph.append([DATA[i]['Name']+'_'+str(j),DATA[i]['Jsc'][j],DATA[i]['DATA'][0],DATA[i]['DATA'][j+1],
                                     DATA[i]['Eg0'][j],
                                     DATA[i]['Name']+'_'+str(j),
                                     DATA[i]['Name']+'_'+str(j)+'_'+'Jsc: %.2f' % DATA[i]['Jsc'][j],
                                     DATA[i]['Name']+'_'+str(j)+'_'+'Eg0: %.2f' % DATA[i]['Eg0'][j],
                                     DATA[i]['Name']+'_'+str(j)+'_'+'Jsc: %.2f' % DATA[i]['Jsc'][j]+'_'+'Eg0: %.2f' % DATA[i]['Eg0'][j],
                                     '-',colorstylelist[i],
                                     DATA[i]['tangent'][j][0], DATA[i]['tangent'][j][1], DATA[i]['tangentLn'][j][0],DATA[i]['tangentLn'][j][1],DATA[i]['lnDat'][j][0],DATA[i]['lnDat'][j][1],
                                     DATA[i]['tangentLn'][j][2],DATA[i]['tangentLn'][j][3],DATA[i]['EgTauc'][j][0],DATA[i]['EgTauc'][j][1],DATA[i]['EgTauc'][j][2],DATA[i]['EgTauc'][j][3],DATA[i]['EgTauc'][j][4],
                                     DATA[i]['Name']+'_'+str(j)+'_'+'Egln: %.2f' % DATA[i]['EgLn'][j],
                                     DATA[i]['Name']+'_'+str(j)+'_'+'Jsc: %.2f' % DATA[i]['Jsc'][j]+'_'+'Egln: %.2f' % DATA[i]['EgLn'][j],
                                     DATA[i]['Name']+'_'+str(j)+'_'+'EgTauc: %.2f' % DATA[i]['EgTauc'][j][0],
                                     DATA[i]['Name']+'_'+str(j)+'_'+'Jsc: %.2f' % DATA[i]['Jsc'][j]+'_'+'EgTauc: %.2f' % DATA[i]['EgTauc'][j][0],
                                     DATA[i]['integJsclist'][j+1],int(2)
                                     ])
        DATAFORGRAPH = DATAforgraph
        QMessageBox.information(self, 'Information', "It's done")
#        print("It's done")
#        self.initlistbox()
        
#%%#############        
    def initlistbox(self):
        self.names = ()
        self.names=self.SampleNames(DATAFORGRAPH)
        self.ui.listWidget.addItems(self.names)
        
        self.ui.comboBox_calccurrent.addItems(self.names)
        
    def sortandexportEQEdat(self):
        global DATAFORGRAPH
        DATA=self.DATA
        
#        selectedtoexport=list(self.listboxsamples.curselection())
##        print(selectedtoexport)
#        selectedtoexport=[self.listboxsamples.get(i) for i in selectedtoexport]
##        print(selectedtoexport)

        
        #creating excel summary file
        Summary = []
        for i in range(len(DATA)):
            for j in range(len(DATA[i]['Jsc'])):
#                print(DATA[i]['Name']+'_'+str(j)+'_'+ '%.2f' % DATA[i]['Jsc'][j])
#                if DATA[i]['Name']+'_'+str(j)+'_'+ '%.2f' % DATA[i]['Jsc'][j] in selectedtoexport:
                Summary.append([DATA[i]['Name'],DATA[i]['Jsc'][j],DATA[i]['Eg0'][j],DATA[i]['EgLn'][j],
                                DATA[i]['EuLn'][j],DATA[i]['stderrEgLn'][j][0],DATA[i]['stderrEgLn'][j][1],
                                DATA[i]['EgTauc'][j][0],DATA[i]['EgIP'][j],DATA[i]['comment'],DATA[i]['Vbias'][j],
                                DATA[i]['filterbias'][j],DATA[i]['ledbias'][j],DATA[i]['dateTime']])
        Summary.insert(0,['Sample Name','Jsc','Eg0','EgLn','EuLn','stderrEgLn','nbptsEgLn','EgTauc','EgIP','comment','Vbias','filterbias','ledbias','datetimeMod'])
        workbook = xlsxwriter.Workbook('Summary.xlsx')
        worksheet = workbook.add_worksheet()
        row=0
        for name, jsc, eg, egln, euln, stderr, nbptEgLn, EgTauc, EgIP, comment, Vbias, filterbias, ledbias, dateandtime in Summary:
            worksheet.write(row, 0, name)
            if jsc!=999:
                worksheet.write(row, 1, jsc)
            else:
                worksheet.write(row, 1, ' ')
            if eg!=999:
                worksheet.write(row, 2, eg)
            else:
                worksheet.write(row, 2, ' ')
            if egln!=999:
                worksheet.write(row, 3, egln)
            else:
                worksheet.write(row, 3, ' ')
            if euln!=999:
                worksheet.write(row, 4, euln)
            else:
                worksheet.write(row, 4, ' ')
            if stderr!=999:
                worksheet.write(row, 5, stderr)
            else:
                worksheet.write(row, 5, ' ')
            if nbptEgLn!=999:
                worksheet.write(row, 6, nbptEgLn)
            else:
                worksheet.write(row, 6, ' ')
            if EgTauc!=999:
                worksheet.write(row, 7, EgTauc)
            else:
                worksheet.write(row, 7, ' ')
            if EgIP!=999:
                worksheet.write(row, 8, EgIP)
            else:
                worksheet.write(row, 8, ' ')    
                
            worksheet.write(row, 9, comment)
            worksheet.write(row, 10, Vbias)
            worksheet.write(row, 11, filterbias)
            worksheet.write(row, 12, ledbias)
            worksheet.write(row, 13, dateandtime)
            row += 1
        workbook.close()
        
        #creating text files with eqe data and currents
        for i in range(len(DATA)):
            listeqe=self.ncolumneqe(int(DATA[i]['NbColumn']))
            listeqe += np.asarray(DATA[i]['DATA']).T.tolist()
            content1=[]
            for j in range(len(listeqe)):
                strr=''
                for k in range(len(listeqe[j])):
                    strr = strr + str(listeqe[j][k])+'\t'
                strr = strr[:-1]+'\n'
                content1.append(strr)
            
            namerow =DATA[i]['Name']+'\t'
            for k in range(len(DATA[i]['Jsc'])):
                namerow +='J = '+'%.2f' % DATA[i]['Jsc'][k]+' mA/cm2\t'
            namerow=namerow[:-1]+'\n'   
            content1.insert(2,namerow)    
                
            file = open(DATA[i]['Name'] + '.txt','w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in content1)
            file.close()
        
        #creating text files with eqe integrated total Jsc
        for i in range(len(DATA)):
            if DATA[i]['integJsclist'][0]!=[]:
                listeqe=self.ncolumneqeJsc(int(DATA[i]['NbColumn']))
                listeqe += np.asarray(DATA[i]['integJsclist']).T.tolist()
                content1=[]
                for j in range(len(listeqe)):
                    strr=''
                    for k in range(len(listeqe[j])):
                        strr = strr + str(listeqe[j][k])+'\t'
                    strr = strr[:-1]+'\n'
                    content1.append(strr)
                
                namerow =DATA[i]['Name']+'\t'
                for k in range(len(DATA[i]['Jsc'])):
                    namerow +='J = '+'%.2f' % DATA[i]['Jsc'][k]+' mA/cm2\t'
                namerow=namerow[:-1]+'\n'   
                content1.insert(2,namerow)    
                    
                file = open(DATA[i]['Name'] + '_integJsc.txt','w', encoding='ISO-8859-1')
                file.writelines("%s" % item for item in content1)
                file.close()
            
        #creating graphs
        plt.clf()
        for i in range(len(DATA)):
            for k in range(1,int(DATA[i]['NbColumn']),1):
                x=DATA[i]['DATA'][0]
#                print(x[0])
#                print(x[-1])
                plt.plot(x,DATA[i]['DATA'][k])
                plt.axis([x[0],x[-1],0,1])
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('EQE (-)')
            text='Jsc= '
            for m in range(len(DATA[i]['Jsc'])):
                text += '%.2f' % DATA[i]['Jsc'][m]+ '; '
            text+='Eg= '
            for m in range(len(DATA[i]['Eg0'])):
                text += '%.2f' % DATA[i]['Eg0'][m]+ '; '
            text=text[:-2]
            plt.annotate(DATA[i]['Name']+' - '+text, xy=(0.1,1.01), xycoords='axes fraction', fontsize=12,
                                                horizontalalignment='left', verticalalignment='bottom')
            plt.savefig(DATA[i]['Name']+'.png')
            plt.clf()
        
        #creating graphs for integJsc
        if DATA[0]['integJsclist'][0]!=[]:
            plt.clf()
            maxyvalues=[]
            for i in range(len(DATA)):
                for k in range(1,int(DATA[i]['NbColumn']),1):
                    x=DATA[i]['integJsclist'][0]
                    plt.plot(x,DATA[i]['integJsclist'][k],label=DATA[i]['Name']+'_'+'%.2f'% DATA[i]['Jsc'][k-1])
                    maxyvalues.append(DATA[i]['integJsclist'][k][-1])
            plt.legend()
            plt.axis([x[0],x[-1],0,math.ceil(max(maxyvalues))])
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('Integrated Jsc (mA/cm2)')
            plt.savefig('integJsc.png')
            plt.clf()
        
        
        plt.close()
        self.destroy()
        self.__init__()
        self.UpdateEQEGraph()
#        self.initlistbox()
     
    def WriteEQEtoDatabase(self):
        DATA=self.DATA 
        
        #connection to DB
        path = QFileDialog.getOpenFileNames(caption = 'Please select the DB file')[0]
        self.db_conn=sqlite3.connect(path)
        self.theCursor=self.db_conn.cursor()
        
        self.theCursor.execute("SELECT batchname FROM batch")
        batchnamesdb=self.theCursor.fetchall()
        print(batchnamesdb)
        self.theCursor.execute("SELECT samplename FROM samples")
        batchnamesdb=self.theCursor.fetchall()
        print(batchnamesdb)
        
        print("EQEs...")
        
        for i in range(len(DATA)):
            batchname=DATA[i]["batchnumb"]
#            print(batchname)
            samplenumber=DATA[i]["samplenumb"]
#            print(samplenumber)
            samplenumber = batchname+'_'+samplenumber
#            samplenumber = DATA[i]["Name"]
#            print(samplenumber)
            
            self.theCursor.execute("SELECT id FROM batch WHERE batchname=?",(batchname,))
            batch_id_exists = self.theCursor.fetchone()[0]
            self.theCursor.execute("SELECT id FROM samples WHERE samplename=?",(samplenumber,))            
            sample_id_exists = self.theCursor.fetchone()[0]
            self.theCursor.execute("SELECT id FROM cells WHERE samples_id=? AND batch_id=?",(sample_id_exists, batch_id_exists))            
            cellletter_id_exists = self.theCursor.fetchall()[0][0]
#            print(cellletter_id_exists)

            if batch_id_exists and sample_id_exists and cellletter_id_exists:
                for j in range(len(DATA[i]['Jsc'])):
                    uniquedatentry=DATA[i]['Name']+str(DATA[i]['dateTime'])+str(DATA[i]['Jsc'][j])
                    uniquedatentry=uniquedatentry.replace(' ','')
                    uniquedatentry=uniquedatentry.replace(':','')
                    uniquedatentry=uniquedatentry.replace('.','')
                    uniquedatentry=uniquedatentry.replace('-','')
                    uniquedatentry=uniquedatentry.replace('_','')
                    try:
                        self.db_conn.execute("""INSERT INTO eqemeas (
                                EQEmeasname,
                                EQEmeasnameDateTimeEQEJsc,
                                commenteqe,
                                DateTimeEQE,
                                Vbias,
                                filter,
                                LEDbias,
                                integJsc,
                                Eg0,
                                EgIP,
                                EgTauc,
                                EgLn,
                                linktofile,
                                samples_id,
                                batch_id,
                                cells_id
                            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (DATA[i]['Name'],
                             uniquedatentry,
                             DATA[i]['comment'],
                             DATA[i]['dateTime'],
                             DATA[i]['Vbias'][j],
                             DATA[i]['filterbias'][j],
                             DATA[i]['ledbias'][j],
                             DATA[i]['Jsc'][j],
                             DATA[i]['Eg0'][j],
                             DATA[i]['EgIP'][j],
                             DATA[i]['EgTauc'][j][0],
                             DATA[i]['EgLn'][j],
                             DATA[i]['filepath'],
                             sample_id_exists,
                             batch_id_exists,
                             cellletter_id_exists))
                        self.db_conn.commit()
                    except sqlite3.IntegrityError:
                        print("the file already exists in the DB")
        
        #disconnect from DB
        self.theCursor.close()
        self.db_conn.close()
        
        #exit window
#        print("it's in the DB!")
        QMessageBox.information(self,'Information', "it's in the DB!")
        
#%%#############         
    def SampleNames(self, DATAx):#for DATAFORGRAPH
        Names = list(self.names)
        for item in range(len(DATAx)):
            Names.append(DATAx[item][0]+'_'+ '%.2f' % DATAx[item][1])
        return tuple(Names)
    
    def UpdateEQEGraph(self):
        global titEQE
        global takenforplot
        global DATAFORGRAPH
        global DATAforexport
        global colorstylelist
        
#        takenforplot=list(self.listboxsamples.curselection())
        
        DATAx=DATAFORGRAPH
        
        sampletotake=[]
        DATAforexport=[]
        
        if takenforplot!=[]:
            sampletotake=takenforplot
            # print(sampletotake)
        
        if self.ui.comboBox.currentText()=="linear":
            if not self.ui.checkBox_integrJsc.isChecked():
                self.EQEgraph.clear()
                self.EQEgraphY2.clear()
                self.EQEgraphY2.get_yaxis().set_visible(False)
                EQEfig=self.EQEgraph
                for i in range(len(sampletotake)):
                    x = DATAx[sampletotake[i]][2]
                    y = DATAx[sampletotake[i]][3]
                    
                    colx=["Wavelength","nm"," "]+x
                    coly=["EQE","-",DATAx[sampletotake[i]][5]]+y
                    DATAforexport.append(colx)
                    DATAforexport.append(coly)
                    
                    if self.ui.checkBox_legend.isChecked():
                        if not self.ui.checkBox_Jsc.isChecked() and not self.ui.checkBox_Eg.isChecked():
                            EQEfig.plot(x,y,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                        elif self.ui.checkBox_Jsc.isChecked() and not self.ui.checkBox_Eg.isChecked():
                            EQEfig.plot(x,y,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                        elif not self.ui.checkBox_Jsc.isChecked() and self.ui.checkBox_Eg.isChecked():
                            EQEfig.plot(x,y,label=DATAx[sampletotake[i]][7],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                        elif self.ui.checkBox_Jsc.isChecked() and self.ui.checkBox_Eg.isChecked():
                            EQEfig.plot(x,y,label=DATAx[sampletotake[i]][8],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    else:
                        EQEfig.plot(x,y,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    
                    if self.ui.checkBox_showsecreteg.isChecked():
                        m=DATAx[sampletotake[i]][11]
                        h=DATAx[sampletotake[i]][12]
                        x2=1239.8/DATAx[sampletotake[i]][4]
                        x=np.linspace(x2-100,x2,10)
                        #x=np.array(range(int(round(x2-100)),int(round(x2))))
                        y=eval('m*x+h')
                        EQEfig.plot(x,y)
                            
                self.EQEgraph.set_ylabel('EQE (-)', fontsize=self.ui.spinBox_fontsize.value())
                self.EQEgraph.set_xlabel('Wavelength (nm)', fontsize=self.ui.spinBox_fontsize.value())
                
                
            else:#if wants the Jsc integrated curve in 2-y-axis graph
                self.EQEgraph.clear()
                self.EQEgraphY2.clear()
                self.EQEgraphY2.get_yaxis().set_visible(True)
                EQEfig=self.EQEgraph
                ax2=self.EQEgraphY2
                maxyvalues=[]
                for i in range(len(sampletotake)):
                    try:
                        x = DATAx[sampletotake[i]][2]
                        y = DATAx[sampletotake[i]][3]
                        y2= DATAx[sampletotake[i]][28]
                        maxyvalues.append(y2[-1])
                        colx=["Wavelength","nm"," "]+x
                        coly=["EQE","-",DATAx[sampletotake[i]][5]]+y
                        coly2=["Jsc","mA/cm2",DATAx[sampletotake[i]][5]]+y2
                        DATAforexport.append(colx)
                        DATAforexport.append(coly)
                        DATAforexport.append(coly2)
                        
                        if self.ui.checkBox_legend.isChecked():
                            if not self.ui.checkBox_Jsc.isChecked() and not self.ui.checkBox_Eg.isChecked():
                                EQEfig.plot(x,y,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                                ax2.plot(x,y2,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])                      
                            elif self.ui.checkBox_Jsc.isChecked() and not self.ui.checkBox_Eg.isChecked():
                                EQEfig.plot(x,y,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                                ax2.plot(x,y2,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                            elif not self.ui.checkBox_Jsc.isChecked() and self.ui.checkBox_Eg.isChecked():
                                EQEfig.plot(x,y,label=DATAx[sampletotake[i]][7],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                                ax2.plot(x,y2,label=DATAx[sampletotake[i]][7],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])                        
                            elif self.ui.checkBox_Jsc.isChecked() and self.ui.checkBox_Eg.isChecked():
                                EQEfig.plot(x,y,label=DATAx[sampletotake[i]][8],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                                ax2.plot(x,y2,label=DATAx[sampletotake[i]][8],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])                    
                        else:
                            EQEfig.plot(x,y,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                            ax2.plot(x,y2,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                            
                        if self.ui.checkBox_showsecreteg.isChecked():
                            m=DATAx[sampletotake[i]][11]
                            h=DATAx[sampletotake[i]][12]
                            x2=1239.8/DATAx[sampletotake[i]][4]
                            x=np.linspace(x2-100,x2,10)
                            #x=np.array(range(int(round(x2-100)),int(round(x2))))
                            y=eval('m*x+h')
                            EQEfig.plot(x,y)
                    except:
                        pass
                            
                self.EQEgraph.set_ylabel('EQE (-)', fontsize=self.ui.spinBox_fontsize.value())
                self.EQEgraphY2.set_ylabel('Jsc',fontsize=self.ui.spinBox_fontsize.value())
                self.EQEgraph.set_xlabel('Wavelength (nm)', fontsize=self.ui.spinBox_fontsize.value())
                
            
        elif self.ui.comboBox.currentText()=="log":
            self.EQEgraph.clear()
            self.EQEgraphY2.clear()
            self.EQEgraphY2.get_yaxis().set_visible(False)
#            self.EQEgraphY2.get_xaxis().set_visible(False)
            EQEfig=self.EQEgraph
            minxlist=[]
            maxxlist=[]
            minylist=[]
            maxylist=[]
            for i in range(len(sampletotake)):
                x = DATAx[sampletotake[i]][15]
                y = DATAx[sampletotake[i]][16]
                minxlist.append(x[0])
                maxxlist.append(x[-1])
                minylist.append(min(y))
                maxylist.append(max(y))
                
                colx=["Energy","eV"," "]+x
                coly=["Ln(EQE)","-",DATAx[sampletotake[i]][5]]+y
                DATAforexport.append(colx)
                DATAforexport.append(coly)
                
                if self.ui.checkBox_legend.isChecked():
                    if not self.ui.checkBox_Jsc.isChecked() and not self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    elif self.ui.checkBox_Jsc.isChecked() and not self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    elif not self.ui.checkBox_Jsc.isChecked() and self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][24],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    elif self.ui.checkBox_Jsc.isChecked() and self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][25],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                else:
                    EQEfig.plot(x,y,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                
                if self.ui.checkBox_showsecreteg.isChecked():
                    m=DATAx[sampletotake[i]][13]
                    h=DATAx[sampletotake[i]][14]
                    x2=DATAx[sampletotake[i]][4]
                    x=np.linspace(x2-0.1,x2+0.1,10)
                    y=eval('m*x+h')
                    EQEfig.plot(x,y)
                    EQEfig.plot(DATAx[sampletotake[i]][17],DATAx[sampletotake[i]][18],'ro')
                    
            self.EQEgraph.set_ylabel('Ln(EQE) (-)', fontsize=self.ui.spinBox_fontsize.value())
            self.EQEgraph.set_xlabel('Energy (eV)', fontsize=self.ui.spinBox_fontsize.value())
            
        elif self.ui.comboBox.currentText()=="Tauc1":
            self.EQEgraph.clear()
            self.EQEgraphY2.clear()
            self.EQEgraphY2.get_yaxis().set_visible(False)
            EQEfig=self.EQEgraph
            minxlist=[]
            maxxlist=[]
            minylist=[]
            maxylist=[]
            for i in range(len(sampletotake)):
                x = DATAx[sampletotake[i]][20]
                y = DATAx[sampletotake[i]][21]                
                minxlist.append(x[0])
                maxxlist.append(x[-1])
                minylist.append(min(y))
                maxylist.append(max(y))
                colx=["Energy","eV"," "]+x
                coly=["(EQE*E)^2","(eV)^2",DATAx[sampletotake[i]][5]]+y
                DATAforexport.append(colx)
                DATAforexport.append(coly)
                
                if self.ui.checkBox_legend.isChecked():
                    if not self.ui.checkBox_Jsc.isChecked() and not self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    elif self.ui.checkBox_Jsc.isChecked() and not self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    elif not self.ui.checkBox_Jsc.isChecked() and self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][26],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    elif self.ui.checkBox_Jsc.isChecked() and self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][27],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                else:
                    EQEfig.plot(x,y,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                
                if self.ui.checkBox_showsecreteg.isChecked():
                    m=DATAx[sampletotake[i]][22]
                    h=DATAx[sampletotake[i]][23]
                    x2=DATAx[sampletotake[i]][19]
                    x=np.linspace(x2,x2+0.1,10)
                    y=eval('m*x+h')
                    EQEfig.plot(x,y)
                
            self.EQEgraph.set_ylabel("(EQE*E)^2 (eV)^2", fontsize=self.ui.spinBox_fontsize.value())
            self.EQEgraph.set_xlabel('Energy (eV)', fontsize=self.ui.spinBox_fontsize.value())
            
#        elif self.ui.comboBox.currentText()=="Tauc2":
#            self.EQEgraph.clear()
#            self.EQEgraphY2.clear()
#            self.EQEgraphY2.get_yaxis().set_visible(False)
#            EQEfig=self.EQEgraph
#            minxlist=[]
#            maxxlist=[]
#            minylist=[]
#            maxylist=[]
#            for i in range(len(sampletotake)):
#                x = DATAx[sampletotake[i]][20]
#                y = DATAx[sampletotake[i]][21]                
#                minxlist.append(x[0])
#                maxxlist.append(x[-1])
#                minylist.append(min(y))
#                maxylist.append(max(y))
#                colx=["Energy","eV"," "]+x
#                coly=["Ln(1-EQE)^2 * E^2","a.u.",DATAx[sampletotake[i]][5]]+y
#                DATAforexport.append(colx)
#                DATAforexport.append(coly)
#                
#                if self.CheckLegend.get()==1:
#                    if self.CheckLegJsc.get()==0 and self.CheckLegEg.get()==0:
#                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
#                    elif self.CheckLegJsc.get()==1 and self.CheckLegEg.get()==0:
#                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
#                    elif self.CheckLegJsc.get()==0 and self.CheckLegEg.get()==1:
#                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][26],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
#                    elif self.CheckLegJsc.get()==1 and self.CheckLegEg.get()==1:
#                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][27],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
#                else:
#                    EQEfig.plot(x,y,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
#                
#                if self.CheckTangent.get()==1:
#                    m=DATAx[sampletotake[i]][22]
#                    h=DATAx[sampletotake[i]][23]
#                    x2=DATAx[sampletotake[i]][19]
#                    x=np.linspace(x2,x2+0.1,10)
#                    y=eval('m*x+h')
#                    EQEfig.plot(x,y)
#                
#            self.EQEgraph.set_ylabel('Ln(1-EQE)^2 * E^2 (a.u.)', fontsize=14)
#            self.EQEgraph.set_xlabel('Energy (eV)', fontsize=14)
#            if titEQE:
#                self.EQEgraph.set_title(self.titleEQE.get())
#            if self.CheckLegend.get()==1:
#                if self.pos1.get()==5:
#                    self.leg=EQEfig.legend(bbox_to_anchor=(1, 0.5), loc=2, ncol=1)
#                elif self.pos1.get()==1 or self.pos1.get()==2  or self.pos1.get()==3 or self.pos1.get()==4:   
#                    self.leg=EQEfig.legend(loc=self.pos1.get())
#                else:
#                    self.leg=EQEfig.legend(loc=0)
##            if self.CheckAutoscale.get()==0:        
##                self.EQEgraph.axis([self.minx.get(),self.maxx.get(),self.miny.get(),self.maxy.get()])
#            self.EQEgraph.axis([min(minxlist),max(maxxlist),min(minylist),math.ceil(max(maxylist))])
#            plt.gcf().canvas.draw()    
            
        elif self.ui.comboBox.currentText()=="NormalizedBySingle":
            self.EQEgraph.clear()
            self.EQEgraphY2.clear()
            self.EQEgraphY2.get_yaxis().set_visible(False)
            EQEfig=self.EQEgraph
            for i in range(len(sampletotake)):
                x = DATAx[sampletotake[i]][2]
                y1 = DATAx[sampletotake[i]][3]
                
                y=[(m-min(y1))/(max(y1)-min(y1)) for m in y1]
                
                colx=["Wavelength","nm"," "]+x
                coly=["Norm. EQE","-",DATAx[sampletotake[i]][5]]+y
                DATAforexport.append(colx)
                DATAforexport.append(coly)
                
                if self.ui.checkBox_legend.isChecked():
                    if not self.ui.checkBox_Jsc.isChecked() and not self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    elif self.ui.checkBox_Jsc.isChecked() and not self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    elif not self.ui.checkBox_Jsc.isChecked() and self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][7],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    elif self.ui.checkBox_Jsc.isChecked() and self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][8],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                else:
                    EQEfig.plot(x,y,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
            self.EQEgraph.set_ylabel('Norm. EQE (-)', fontsize=self.ui.spinBox_fontsize.value())
            self.EQEgraph.set_xlabel('Wavelength (nm)', fontsize=self.ui.spinBox_fontsize.value())
            
        elif self.ui.comboBox.currentText()=="NormalizedByAll":
            self.EQEgraph.clear()
            self.EQEgraphY2.clear()
            self.EQEgraphY2.get_yaxis().set_visible(False)
            EQEfig=self.EQEgraph
            AllY=[]
            for i in range(len(sampletotake)):
                AllY+=DATAx[sampletotake[i]][3]
            miny=min(AllY)
            maxy=max(AllY)
            
            for i in range(len(sampletotake)):
                x = DATAx[sampletotake[i]][2]
                y1 = DATAx[sampletotake[i]][3]
                
                y=[(m-miny)/(maxy-miny) for m in y1]
                
                colx=["Wavelength","nm"," "]+x
                coly=["Norm. EQE","-",DATAx[sampletotake[i]][5]]+y
                DATAforexport.append(colx)
                DATAforexport.append(coly)
                
                if self.ui.checkBox_legend.isChecked():
                    if not self.ui.checkBox_Jsc.isChecked() and not self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][5],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    elif self.ui.checkBox_Jsc.isChecked() and not self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][6],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    elif not self.ui.checkBox_Jsc.isChecked() and self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][7],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                    elif self.ui.checkBox_Jsc.isChecked() and self.ui.checkBox_Eg.isChecked():
                        EQEfig.plot(x,y,label=DATAx[sampletotake[i]][8],linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
                else:
                    EQEfig.plot(x,y,linestyle=DATAx[sampletotake[i]][9],color=DATAx[sampletotake[i]][10],linewidth=DATAx[sampletotake[i]][29])
            self.EQEgraph.set_ylabel('Norm. EQE (-)', fontsize=self.ui.spinBox_fontsize.value())
            self.EQEgraph.set_xlabel('Wavelength (nm)', fontsize=self.ui.spinBox_fontsize.value())
        
        
        if self.ui.checkBox_legend.isChecked():
            if self.ui.radioButton_topleft.isChecked():
                self.leg=self.EQEgraph.legend(loc=2, fontsize = self.ui.spinBox_fontsize.value())
            elif self.ui.radioButton_topright.isChecked():
                self.leg=self.EQEgraph.legend(loc=1, fontsize = self.ui.spinBox_fontsize.value())
            elif self.ui.radioButton_bottomleft.isChecked():
                self.leg=self.EQEgraph.legend(loc=3, fontsize = self.ui.spinBox_fontsize.value())
            elif self.ui.radioButton_bottomright.isChecked():
                self.leg=self.EQEgraph.legend(loc=4, fontsize = self.ui.spinBox_fontsize.value())
            elif self.ui.radioButton_outside.isChecked():
                self.leg=self.EQEgraph.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1, fontsize = self.ui.spinBox_fontsize.value())
            elif self.ui.radioButton_best.isChecked():
                self.leg=self.EQEgraph.legend(loc=0, fontsize = self.ui.spinBox_fontsize.value())
        
        for item in ([self.EQEgraph.title, self.EQEgraph.xaxis.label, self.EQEgraph.yaxis.label] +
                     self.EQEgraph.get_xticklabels() + self.EQEgraph.get_yticklabels()):
            item.set_fontsize(self.ui.spinBox_fontsize.value())
                
        self.fig.canvas.draw_idle()
            
#%%#############             
        
    def ExportEQEGraph(self):
        global DATAforexport 
        #graphname = self.entrytext.get()
        #plt.savefig(graphname +'.png', bbox_extra_artists=(self.leg,), bbox_inches='tight') 
        try:
            path = QFileDialog.getSaveFileName(self, 'Save graph', ".png", "graph file (*.png);; All Files (*)")[0]

            if self.ui.checkBox_legend.isChecked():
                self.fig.savefig(path, dpi=300, bbox_extra_artists=(self.leg,))#, transparent=True)
            else:
                self.fig.savefig(path, dpi=300)#, transparent=True)
                    
            DATAforexport=map(list, six.moves.zip_longest(*DATAforexport, fillvalue=' '))

            DATAforexport1=[]
            for item in DATAforexport:
                line=""
                for item1 in item:
                    line=line+str(item1)+"\t"
                line=line[:-1]+"\n"
                DATAforexport1.append(line)
                
            file = open(str(path[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in DATAforexport1)
            file.close() 
        except:
            QMessageBox.information(self,'Information', "there is an exception...check legend maybe...")
             
    # class PopulateListofSampleStylingEQE(tk.Frame):
    #     def __init__(self, root):
    
    #         tk.Frame.__init__(self, root)
    #         self.canvas0 = tk.Canvas(root, borderwidth=0, background="#ffffff")
    #         self.frame = tk.Frame(self.canvas0, background="#ffffff")
    #         self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas0.yview)
    #         self.canvas0.configure(yscrollcommand=self.vsb.set)
    
    #         self.vsb.pack(side="right", fill="y")
    #         self.canvas0.pack(side="left", fill="both", expand=True)
    #         self.canvas0.create_window((4,4), window=self.frame, anchor="nw", 
    #                                   tags="self.frame")
    
    #         self.frame.bind("<Configure>", self.onFrameConfigure)
    
    #         self.populate()
    
    #     def populate(self):
    #         global DATAFORGRAPH
    #         global takenforplot
    #         global colorstylelist
    #         global listofanswer
    #         global listoflinestyle
    #         global listofcolorstyle, listoflinewidthstyle
    #         DATAx=DATAFORGRAPH
    #         listofanswer=[]
    #         sampletotake=[]
    #         if takenforplot!=[]:
    #             for item in takenforplot:
    #                 sampletotake.append(DATAx[item][0])
                    
    #         listoflinestyle=[]
    #         listofcolorstyle=[]
    #         listoflinewidthstyle=[]
    #         for item in range(len(DATAx)):
    #             listoflinestyle.append(DATAx[item][9])
    #             listofcolorstyle.append(DATAx[item][10])
    #             listofanswer.append(DATAx[item][0])
    #             listoflinewidthstyle.append(str(DATAx[item][29]))
            
    #         rowpos=1
    #         forbiddenrange=[]
    #         for itemm in sampletotake:
    #             for item1 in range(len(DATAx)): 
    #                 if item1 not in forbiddenrange:
    #                     if DATAx[item1][0] == itemm:
    #                         #print(itemm)
    #                         forbiddenrange.append(item1)
    #                         label=tk.Label(self.frame,text=DATAx[item1][0],fg='black',background='white')
    #                         label.grid(row=rowpos,column=0, columnspan=1)
    #                         textinit = tk.StringVar()
    #                         #self.listofanswer.append(Entry(self.window,textvariable=textinit))
    #                         listofanswer[item1]=Entry(self.frame,textvariable=textinit)
    #                         listofanswer[item1].grid(row=rowpos,column=1, columnspan=2)
    #                         textinit.set(DATAx[item1][5])
                
    #                         linestylelist = ["-","--","-.",":"]
    #                         listoflinestyle[item1]=tk.StringVar()
    #                         listoflinestyle[item1].set(DATAx[item1][9]) # default choice
    #                         OptionMenu(self.frame, listoflinestyle[item1], *linestylelist, command=()).grid(row=rowpos, column=4, columnspan=2)
                             
    #                         """
    #                         listofcolorstyle[item1]=tk.StringVar()
    #                         listofcolorstyle[item1].set(DATAx[item1][10]) # default choice
    #                         OptionMenu(self.frame, listofcolorstyle[item1], *colorstylelist, command=()).grid(row=rowpos, column=6, columnspan=2)
    #                         """
    #                         self.positioncolor=item1
    #                         colstyle=Button(self.frame, text='Select Color', foreground=listofcolorstyle[item1], command=partial(self.getColor,item1))
    #                         colstyle.grid(row=rowpos, column=6, columnspan=2)
                            
                            
    #                         linewidth = tk.StringVar()
    #                         listoflinewidthstyle[item1]=Entry(self.frame,textvariable=linewidth)
    #                         listoflinewidthstyle[item1].grid(row=rowpos,column=8, columnspan=1)
    #                         linewidth.set(str(DATAx[item1][29]))
                            
    #                         rowpos=rowpos+1
                            
    #                     else:
    #                         listofanswer[item1]=str(DATAx[item1][5])
    #                         listoflinestyle.append(str(DATAx[item1][9]))
    #                         listofcolorstyle.append(str(DATAx[item1][10]))
    #                         listoflinewidthstyle.append(str(DATAx[item1][29]))
    #         #print(listofanswer)
            
    #     def getColor(self,rowitem):
    #         global listofcolorstyle
    #         color = askcolor(color="red", parent=self.frame, title="Color Chooser", alpha=False)
    #         listofcolorstyle[rowitem]=color[1]
            
            
    #     def onFrameConfigure(self, event):
    #         '''Reset the scroll region to encompass the inner frame'''
    #         self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))
    
    # class Drag_and_Drop_Listbox(tk.Listbox):
    #     #A tk listbox with drag'n'drop reordering of entries.
    #     def __init__(self, master, **kw):
    #         #kw['selectmode'] = tk.MULTIPLE
    #         kw['selectmode'] = tk.SINGLE
    #         kw['activestyle'] = 'none'
    #         tk.Listbox.__init__(self, master, kw)
    #         self.bind('<Button-1>', self.getState, add='+')
    #         self.bind('<Button-1>', self.setCurrent, add='+')
    #         self.bind('<B1-Motion>', self.shiftSelection)
    #         self.curIndex = None
    #         self.curState = None
    #     def setCurrent(self, event):
    #         ''' gets the current index of the clicked item in the listbox '''
    #         self.curIndex = self.nearest(event.y)
    #     def getState(self, event):
    #         ''' checks if the clicked item in listbox is selected '''
    #         #i = self.nearest(event.y)
    #         #self.curState = self.selection_includes(i)
    #         self.curState = 1
    #     def shiftSelection(self, event):
    #         ''' shifts item up or down in listbox '''
    #         i = self.nearest(event.y)
    #         if self.curState == 1:
    #           self.selection_set(self.curIndex)
    #         else:
    #           self.selection_clear(self.curIndex)
    #         if i < self.curIndex:
    #           # Moves up
    #           x = self.get(i)
    #           selected = self.selection_includes(i)
    #           self.delete(i)
    #           self.insert(i+1, x)
    #           if selected:
    #             self.selection_set(i+1)
    #           self.curIndex = i
    #         elif i > self.curIndex:
    #           # Moves down
    #           x = self.get(i)
    #           selected = self.selection_includes(i)
    #           self.delete(i)
    #           self.insert(i-1, x)
    #           if selected:
    #             self.selection_set(i-1)
    #           self.curIndex = i
              

    # def reorder(self): 
    #     global DATAFORGRAPH
    #     global takenforplot
    #     DATAx=DATAFORGRAPH
    #     sampletotake=[]
    #     if takenforplot!=[]:
    #         for item in takenforplot:
    #             sampletotake.append(DATAx[item][0])
                    
    #     self.reorderwindow = tk.Tk()
    #     center(self.reorderwindow)
    #     self.listbox = self.Drag_and_Drop_Listbox(self.reorderwindow)
    #     for name in sampletotake:
    #       self.listbox.insert(tk.END, name)
    #       self.listbox.selection_set(0)
    #     self.listbox.pack(fill=tk.BOTH, expand=True)
    #     scrollbar = tk.Scrollbar(self.listbox, orient="vertical")
    #     scrollbar.config(command=self.listbox.yview)
    #     scrollbar.pack(side="right", fill="y")
        
    #     self.listbox.config(yscrollcommand=scrollbar.set)
        
    #     printbut = tk.Button(self.reorderwindow, text="reorder",
    #                                 command = self.printlist)
    #     printbut.pack()
    #     self.reorderwindow.mainloop()    
            
    # def printlist(self):
    #     global DATAFORGRAPH
    #     global takenforplot
    #     takenforplot=[]
    #     sampletotake=list(self.listbox.get(0,tk.END))
    #     for item in sampletotake:
    #         for i in range(len(DATAFORGRAPH)):
    #             if DATAFORGRAPH[i][0]==item:
    #                 takenforplot.append(i)
    #     self.UpdateEQELegMod()
    #     self.reorderwindow.destroy()
        
    # def ChangeLegendEQEgraph(self):       
        
    #     if self.CheckLegend.get()==1:        
    #         self.window = tk.Toplevel()
    #         self.window.wm_title("Change Legends")
    #         center(self.window)
    #         self.window.geometry("450x300")
            
    #         Button(self.window, text="Update",
    #                             command = self.UpdateEQELegMod).pack()
            
    #         Button(self.window, text="Reorder",
    #                             command = self.reorder).pack()
    
    #         self.PopulateListofSampleStylingEQE(self.window).pack(side="top", fill="both", expand=True)
        
    # def UpdateEQELegMod(self):
    #     global DATAFORGRAPH
    #     global listofanswer
    #     global listoflinestyle
    #     global listofcolorstyle,listoflinewidthstyle

    #     leglist=[]
    #     for e in listofanswer:
    #         if type(e)!=str:
    #             leglist.append(e.get())
    #         else:
    #             leglist.append(e)
    #     for item in range(len(DATAFORGRAPH)):
    #         DATAFORGRAPH[item][5]=leglist[item]
    #         DATAFORGRAPH[item][6]= leglist[item]+'_'+'Jsc: %.2f' % DATAFORGRAPH[item][1]
    #         DATAFORGRAPH[item][7]= leglist[item]+'_'+'Eg: %.2f' % DATAFORGRAPH[item][4]
    #         DATAFORGRAPH[item][8]= leglist[item]+'_'+'Jsc: %.2f' % DATAFORGRAPH[item][1]+'_'+'Eg: %.2f' % DATAFORGRAPH[item][4]
    #     leglist=[]
    #     for e in listoflinestyle:
    #         if type(e)!=str:
    #             leglist.append(e.get())
    #         else:
    #             leglist.append(e)
    #     for item in range(len(DATAFORGRAPH)):
    #         DATAFORGRAPH[item][9]=leglist[item]        
    #     leglist=[]
    #     for e in listofcolorstyle:
    #         if type(e)!=str:
    #             leglist.append(e.get())
    #         else:
    #             leglist.append(e) 
    #     for item in range(len(DATAFORGRAPH)):
    #         DATAFORGRAPH[item][10]=leglist[item]  
    #     leglist=[]
    #     for e in listoflinewidthstyle:
    #         if type(e)!=str:
    #             leglist.append(e.get())
    #         else:
    #             leglist.append(e) 
    #     for item in range(len(DATAFORGRAPH)):
    #         DATAFORGRAPH[item][29]=int(leglist[item]) 
                
        
    #     self.UpdateEQEGraph()
    #     self.window.destroy()
    #     self.ChangeLegendEQEgraph()

    def CalcCurrent(self):
        global DATAFORGRAPH
        itempos=0
        item=0
        for item in range(len(DATAFORGRAPH)):
            if DATAFORGRAPH[item][0]+'_'+'%.2f' % float(DATAFORGRAPH[item][1])==self.ui.comboBox_calccurrent.currentText():
                itempos=item
                break
        try:    
            x = DATAFORGRAPH[itempos][2]
            y = DATAFORGRAPH[itempos][3]
            f = interp1d(x, y, kind='cubic')
            x2 = lambda x: self.AM15GParticlesinnm(x)*f(x)
            integral = echarge/10*integrate.quad(x2,self.ui.spinBox_from.value(),self.ui.spinBox_to.value())[0]
            self.ui.doubleSpinBox_calcjsc.setValue(integral)
        except ValueError:
            QMessageBox.information(self,'Information', "a limit value is outside of interpolation range,\nmin: "+str(x[0])+", max: "+str(x[-1]))
        
    def select(self):
        global takenforplot
        # takenforplot = [str(self.ui.listWidget.selectedItems()[i].text()) for i in range(len(self.ui.listWidget.selectedItems()))]
        takenforplot = [i.row() for i in self.ui.listWidget.selectedIndexes()]
        self.UpdateEQEGraph()
        
    def CalculateIQE(self):
        print("IQE")
        """
        - check that a sample is selected, retrieve it or do nothing if no selected
        if more than 1 is selected, will apply same procedure to all individually
        - ask which procedure to follow: all simulation or mix? drop down list with 2 equations
        put some info and explanation text
        - when click next button, will close window and ask to find the required files
        - reading file(s)
        - computing IQE: need to interpolate all the data as they will certainly have different step sizes between spectro and simulation and EQEmeas
        - importing the IQE data in the EQE app same as when import new data => samplename_IQEcomputed
        
        """
    def StitchEQE(self):
        print("stitching")
        global takenforplot
        global DATAFORGRAPH, stitching
        
        DATAx=DATAFORGRAPH
        sampletotake=takenforplot
        
        newDatlistx=[]
        newDatlisty=[]
        
        for i in range(len(sampletotake)):
#            newDatlistx.append(DATAx[sampletotake[i]][2])
#            newDatlisty.append(DATAx[sampletotake[i]][3])
            newDatlistx+=DATAx[sampletotake[i]][2]
            newDatlisty+=DATAx[sampletotake[i]][3]
        overlapx=Repeat(newDatlistx)
#        print(overlapx)
        newx=[]
        newy=[]
        seen=[]
        for item in range(len(newDatlistx)):
            if newDatlistx[item] not in overlapx[0]:
                newx.append(newDatlistx[item])
                newy.append(newDatlisty[item])
            elif newDatlistx[item] in overlapx[0] and newDatlistx[item] not in seen:
                newx.append(newDatlistx[item])
                seen.append(newDatlistx[item])
                indexlist=overlapx[0].index(newDatlistx[item])
                newy.append((newDatlisty[overlapx[1][indexlist][0]]+newDatlisty[overlapx[1][indexlist][1]])/2)

        #export txt file with new data where the original file was imported from
        datexport=[]
        for i in range(len(newx)):
            datexport.append(str(newx[i])+'\t'+str(newy[i])+'\n')
        # stitching = filedialog.asksaveasfilename(defaultextension=".txt")
        stitching = QFileDialog.getOpenFileNames()[0]


        file = open(stitching,'w', encoding='ISO-8859-1')
        file.writelines("%s" % item for item in datexport)
        file.close()
        #reimport that file with import function
        self.onOpenEQE()
        
        
        
def Repeat(x): 
    _size = len(x) 
    repeated = [] 
    repindices=[]
    for i in range(_size): 
        k = i + 1
        for j in range(k, _size): 
            if x[i] == x[j] and x[i] not in repeated: 
                repeated.append(x[i]) 
                repindices.append([i,j])
                
    return [repeated, repindices]
        
        
#%%#############         
#%%#############
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = EQEapp()
    window.show()
    sys.exit(app.exec())

