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
from matplotlib import collections as matcoll
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
from scipy.optimize import curve_fit
import peakutils
from peakutils.plot import plot as pplot
from math import factorial,radians, sin, cos

from PyQt5.uic import loadUiType
Ui_MainWindow, QMainWindow = loadUiType('XRDgui.ui')

LARGE_FONT= ("Verdana", 12)
DATA={}# {"name":[[x original...],[y original...],[x corrected...],[y corrected...],[{"Position":1,"PeakName":'(005)',"Intensity":1,"FWHM":1},...],[linestyle, colorstyle, answer, linewidthstyle]],"name2":[]}
#takenforplot=[]
#listofanswer=[]
#listoflinestyle=[]
#listofcolorstyle=[]
#listoflinewidthstyle=[]

colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']
owd = os.getcwd()

xrdRefPattDir	= os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'crystalloData')	# materials data


reflist=os.listdir(xrdRefPattDir)
refsamplenameslist=[]
for item in reflist:
    refsamplenameslist.append(item.split('.')[0])

RefPattDATA={}
os.chdir(xrdRefPattDir)
for item in range(len(refsamplenameslist)):
    RefPattDATA[refsamplenameslist[item]]=[[],[],[]]
    if reflist[item].split('.')[1]=='txt':
        filetoread = open(reflist[item],"r", encoding='ISO-8859-1')
        filerawdata = filetoread.readlines()
        for row in filerawdata:
            RefPattDATA[refsamplenameslist[item]][0].append(float(row.split("\t")[0]))
            RefPattDATA[refsamplenameslist[item]][1].append(float(row.split("\t")[1]))
            try:
                RefPattDATA[refsamplenameslist[item]][2].append(str(row.split("\t")[2])[:-1])
            except:
                RefPattDATA[refsamplenameslist[item]][2].append("")
    
#print(RefPattDATA["jems-Si"])

os.chdir(owd)
#refsamplenameslist=["Si","pkcubic"]#to be replaced by reading the folder and putting all data in a list and getting the file names in this list
Patternsamplenameslist=[]

listofanswer0={}
samplestakenforplot=[]
peaknamesforplot=[]

takenforplot=[]
listofanswer=[]
listoflinestyle=[]
listofcolorstyle=[]
listoflinewidthstyle=[]

lambdaXRD=1.5406

colormapname="jet"

def q_to_tth(Q):
    "convert q to tth, lam is wavelength in angstrom"
    return 360/np.pi * np.arcsin(Q * lambdaXRD / (4 * np.pi))

def tth_to_q(tth):
    "convert tth to q, lam is wavelength in angstrom"
    return 4 * np.pi * np.sin(tth * np.pi/(2 * 180)) / lambdaXRD

def q_to_tth_list(Q):
    "convert q to tth, lam is wavelength in angstrom"
    return [360/np.pi * np.arcsin(Qitem * lambdaXRD / (4 * np.pi)) for Qitem in Q]

def tth_to_q_list(tth):
    "convert tth to q, lam is wavelength in angstrom"
    return [4 * np.pi * np.sin(tthitem * np.pi/(2 * 180)) / lambdaXRD for tthitem in tth]

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')


class XRDapp(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        global refsamplenameslist 
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.fig = Figure()
        self.XRDgraph = self.fig.add_subplot(111)
        self.addmpl(self.fig,self.ui.verticalLayout_mplwidget, self.ui.mplwidget)
        
        
        self.ui.actionimport_data.triggered.connect(self.importDATA)
        self.ui.actionimport_ref.triggered.connect(self.importRefDATA)
        self.ui.actionExport_export.triggered.connect(self.Export)
        self.ui.actionExportWillHall.triggered.connect(self.ExportWH)
        self.ui.actionExport_as_Ref.triggered.connect(self.ExportasRef)

        # self.ui.actionmakeTimeGraph.triggered.connect(self.TimeEvolGraph)
        
        self.ui.listWidget_refpatt.addItems(refsamplenameslist)
        self.ui.listWidget_refpatt.itemClicked.connect(self.UpdateGraph0)
        self.ui.listWidget_samples.itemClicked.connect(self.UpdateGraph0)
        
        self.ui.checkBox_shownames.toggled.connect(lambda: self.updateXRDgraph(0))
        self.ui.checkBox_show.toggled.connect(lambda: self.updateXRDgraph(0))
        self.ui.checkBox_legend.toggled.connect(lambda: self.updateXRDgraph(0))
        self.ui.checkBox_ylabel.toggled.connect(lambda: self.updateXRDgraph(0))
        self.ui.checkBox_Qspace.toggled.connect(lambda: self.updateXRDgraph(0))
        self.ui.checkBox_showOrig.toggled.connect(lambda: self.updateXRDgraph(0))
        
        self.ui.pushButton_BkgRemovalPoly.clicked.connect(self.backgroundremoval)
        self.ui.pushButton_SGfilter.clicked.connect(self.SavitzkyGolayFiltering)
        self.ui.pushButton_Xshift.clicked.connect(self.shiftX)
        self.ui.pushButton_Yshift.clicked.connect(self.shiftY)
        self.ui.pushButton_rescale.clicked.connect(self.scaleYtoRef)
        self.ui.pushButton_Backtooriginal.clicked.connect(self.backtoOriginal)
        self.ui.pushButton_detectpeaks.clicked.connect(self.PeakDetection)
        self.ui.pushButton_peaknames.clicked.connect(self.ConfirmPeaknamechanges)
        
        
    def addmpl(self, fig, whereLayout, whereWidget):
        self.canvas = FigureCanvas(fig)
        whereLayout.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, 
                whereWidget, coordinates=True)
        whereLayout.addWidget(self.toolbar)
        
#%%
    def importRefDATA(self):#not yet updated to nrel
        global DATA, RefPattDATA, refsamplenameslist

        #ask for the files
        file_path = QFileDialog.getOpenFileNames(caption = 'Please select the reference XRD pattern')[0]
        
        #read the files and fill the RefPattDATA dictionary 
        for filename in file_path:
            filetoread = open(filename,"r", encoding='ISO-8859-1')
            filerawdata = filetoread.readlines()
            samplename=os.path.splitext(os.path.basename(filename))[0]
            refsamplenameslist.append(samplename)
            
            RefPattDATA[samplename]=[[],[],[]]
            for row in filerawdata:
                RefPattDATA[samplename][0].append(float(row.split("\t")[0]))
                RefPattDATA[samplename][1].append(float(row.split("\t")[1]))
                try:
                    RefPattDATA[samplename][2].append(str(row.split("\t")[2])[:-1])
                except:
                    RefPattDATA[samplename][2].append("")

        
        
        #update the listbox
                    
        self.ui.listWidget_refpatt.addItems(refsamplenameslist)
            
        #should also export this text file in the crystalloData folder, so it's loaded the next time
        #and ask user to share it with me!
        
    
    def importDATA(self):
        global DATA, Patternsamplenameslist, istheretimedata,colormapname
        
        #ask for the files
        file_path = QFileDialog.getOpenFileNames(caption = "Please select the XRD files")[0]
        
#        print(len(DATA))
#        print(len(file_path))
        num_plots=len(DATA)+len(file_path)
#        plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.tab20(np.linspace(0, 1, num_plots))))

        cmap = plt.get_cmap(colormapname)
        colors = cmap(np.linspace(0, 1.0, num_plots))
        colors=[tuple(item) for item in colors]
        
#        print(colors[0])
                
        #read the files and fill the DATA dictionary 
        for filename in file_path:
            tempdat=[]
            filetoread = open(filename,"r", encoding='ISO-8859-1')
            filerawdata = list(filetoread.readlines())
            samplename, fileextension=os.path.splitext(os.path.basename(filename))
#            print(samplename)
            x=[]
            y=[]
            
#            print(fileextension)
                
#            for item in filerawdata:
#                x.append(float(item.split(' ')[0]))
#                y.append(float(item.split(' ')[1]))
            
#            for item in filerawdata:
#                print(item)
#                print(item.split(',')[0])
#                x.append(float(item.split(',')[0]))
#                y.append(float(item.split(',')[1]))  
#                
#            tempdat.append(x)#original x data
#            tempdat.append(y)#original y data
#            tempdat.append(x)#corrected x, set as the original on first importation
#            tempdat.append(y)#corrected y, set as the original on first importation 
#            tempdat.append([])#peak data, list of dictionaries
#            tempdat.append([])#
#            
#            DATA[samplename]=tempdat
#            Patternsamplenameslist.append(samplename)
            
            if fileextension =='.raw':
                for j in range(3):
                    print(filerawdata[j])
#                    if '*' not in filerawdata[j]:
#                        x.append(float(filerawdata[j].split(' ')[0]))#assume 2theta
#                        y.append(float(filerawdata[j].split(' ')[1]))  
#                tempdat.append(x)#original x data 2theta
#                tempdat.append(y)#original y data
#                tempdat.append(x)#corrected x, set as the original on first importation 2theta
#                tempdat.append(y)#corrected y, set as the original on first importation 
#                tempdat.append([])#peak data, list of dictionaries
#                tempdat.append([])#
#                
#                DATA[samplename]=tempdat
#                Patternsamplenameslist.append(samplename)
            elif fileextension =='.ras':
                for j in range(len(filerawdata)):
                    if '*' not in filerawdata[j]:
                        x.append(float(filerawdata[j].split(' ')[0]))#assume 2theta
                        y.append(float(filerawdata[j].split(' ')[1]))  
                tempdat.append(x)#original x data 2theta
                tempdat.append(y)#original y data
                tempdat.append(x)#corrected x, set as the original on first importation 2theta
                tempdat.append(y)#corrected y, set as the original on first importation 
                tempdat.append([])#peak data, list of dictionaries
                tempdat.append(['-',colors[len(DATA.keys())],samplename,int(2)])

                DATA[samplename]=tempdat
                Patternsamplenameslist.append(samplename)
            
            elif fileextension =='.csv':
                for j in range(64,len(filerawdata),2):
                    x.append(float(filerawdata[j].split(',')[0]))#assume 2theta
                    y.append(float(filerawdata[j].split(',')[1]))  
                tempdat.append(x)#original x data 2theta
                tempdat.append(y)#original y data
                tempdat.append(x)#corrected x, set as the original on first importation 2theta
                tempdat.append(y)#corrected y, set as the original on first importation 
                tempdat.append([])#peak data, list of dictionaries
                tempdat.append(['-',colors[len(DATA.keys())],samplename,int(2)])

                DATA[samplename]=tempdat
                Patternsamplenameslist.append(samplename)
                
            elif '3DExplore ascii' in filerawdata[0]:#for Smartlab
                for j in range(len(filerawdata)):
                    if '#' not in filerawdata[j]:
#                        print(filerawdata[j])
                        try:
                            x.append(float(filerawdata[j].split('\t')[0]))#assume 2theta
                            y.append(float(filerawdata[j].split('\t')[1])) 
                        except:
                            pass
                tempdat.append(x)#original x data 2theta
                tempdat.append(y)#original y data
                tempdat.append(x)#corrected x, set as the original on first importation 2theta
                tempdat.append(y)#corrected y, set as the original on first importation 
                tempdat.append([])#peak data, list of dictionaries
                tempdat.append(['-',colors[len(DATA.keys())],samplename,int(2)])
                
                DATA[samplename]=tempdat
                Patternsamplenameslist.append(samplename)
                
            elif '!@!!' in filerawdata[0]:#for Brucker
                for j in range(16,len(filerawdata)):
                    x.append(float(filerawdata[j].split(' ')[0]))#assume 2theta
                    y.append(float(filerawdata[j].split(' ')[1]))  
                tempdat.append(x)#original x data 2theta
                tempdat.append(y)#original y data
                tempdat.append(x)#corrected x, set as the original on first importation 2theta
                tempdat.append(y)#corrected y, set as the original on first importation 
                tempdat.append([])#peak data, list of dictionaries
#                print(len(DATA.keys()))
#                tempdat.append(['-',colorstylelist[len(DATA.keys())],samplename,int(2)])
                tempdat.append(['-',colors[len(DATA.keys())],samplename,int(2)])
                if len(samplename.split('_'))==7:
                    tempdat.append('itsatimeevoldata')
                    #[batch#,sample#,temperature,time,position,nametemp,nametemppos]
                    tempdat.append([samplename.split('_')[2],samplename.split('_')[3],samplename.split('_')[4],float(samplename.split('_')[6]),samplename.split('_')[5],samplename.split('_')[2]+'_'+samplename.split('_')[3]+'_'+samplename.split('_')[4],samplename.split('_')[2]+'_'+samplename.split('_')[3]+'_'+samplename.split('_')[4]+'_'+samplename.split('_')[5]])

                DATA[samplename]=tempdat
                Patternsamplenameslist.append(samplename)
                
            else:#if no information: DMAX
                i=0
                for j in range(len(filerawdata)):
                    if ',' in filerawdata[j]:
                        x.append(float(filerawdata[j].split(',')[0]))
                        y.append(float(filerawdata[j].split(',')[1]))  
                    else:
                        tempdat.append(x)#original x data
                        tempdat.append(y)#original y data
                        tempdat.append(x)#corrected x, set as the original on first importation
                        tempdat.append(y)#corrected y, set as the original on first importation 
                        tempdat.append([])#peak data, list of dictionaries
                        tempdat.append(['-',colors[len(DATA.keys())],samplename+str(i),int(2)])
                        
                        DATA[samplename+str(i)]=tempdat
                        Patternsamplenameslist.append(samplename+str(i))
                        i+=1
                        x=[]
                        y=[]
                        tempdat=[]
        
        #update the listbox
        self.ui.listWidget_samples.addItems(Patternsamplenameslist)

#%%

    def Export(self):
        global DATA 
        
        f = QFileDialog.getSaveFileName(self, 'Save graph', ".png", "graph file (*.png);; All Files (*)")[0]
        self.fig.savefig(f, dpi=300) 

        
        testdata=['name\tPeakName\tPosition\tPositionQ\tIntensity\tFWHM\tPeakArea\tIntegralBreadth\n']
        
        samplestakenforplot = [str(x.text()) for x in self.ui.listWidget_samples.selectedItems()]
        if samplestakenforplot!=[]:
            #exporting the peak analysis results
            for key in samplestakenforplot:
                for item in DATA[key][4]:
                    testdata.append(key +'\t'+ item["PeakName"]+'\t'+str("%.2f"%item["Position"])+'\t'+str("%.2f"%item["PositionQ"])+'\t'+str("%.2f"%item["Intensity"])+'\t'+str("%.2f"%item["FWHM"])+'\t'+str("%.2f"%item["PeakArea"])+'\t'+str("%.2f"%item["IntBreadth"])+'\n')
            
            file = open(f[:-4]+"PeakDat.txt",'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in testdata)
            file.close()    
        
            #exporting the data from the graph
            headline=''
            headline2=''
            columns=[]
            for key in samplestakenforplot:    
                columns.append(DATA[key][2])
                columns.append(DATA[key][3])
                headline+='2theta\tIntensity\t'
                headline2+='\t'+key+'\t'
            headline=[headline[:-1]+'\n',headline2[:-1]+'\n']
            for item in list(map(list,zip(*columns))):
                line=''
                for item2 in item:
                    line+=str(item2)+'\t'
                line=line[:-1]+'\n'
                headline.append(line)
            file = open(f[:-4]+"PatternDat.txt",'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in headline)
            file.close()
            
    def ExportWH(self):
        global DATA, lambdaXRD
        
        
        f = QFileDialog.getSaveFileName(self, 'Save graph', ".png", "graph file (*.png);; All Files (*)")[0]
#        self.fig.savefig(f, dpi=300) 
        
        testdata=['name\tPosition\tFWHM\t4Sin(theta)/lambda\tBCos(theta)/lambda\n']
        
        samplestakenforplot = [str(x.text()) for x in self.ui.listWidget_samples.selectedItems()]
        if samplestakenforplot!=[]:
            #exporting the peak analysis results
            for key in samplestakenforplot:
                for item in DATA[key][4]:
                    xWH=4*sin(radians(item["Position"]/2))/(0.1*lambdaXRD) #4sin(theta)/lambda
                    yWH=item["IntBreadth"]*cos(radians(item["Position"]/2))/(0.1*lambdaXRD) #
                    testdata.append(key +'\t'+str("%.2f"%item["Position"])+'\t'+str("%.2f"%item["FWHM"])+'\t'+str("%.2f"%xWH)+'\t'+str("%.2f"%yWH)+'\n')
            
            file = open(f[:-4]+"WH.txt",'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in testdata)
            file.close()    
        
    def ExportasRef(self):
        global DATA,RefPattDATA
        
        print("tobedone")
        
#%%    
    def UpdateGraph0(self,a):
        global takenforplot
        
        takenforplot = [str(x.text()) for x in self.ui.listWidget_samples.selectedItems()]
        # print(takenforplot)
        self.updateXRDgraph(0)
        
    def updateXRDgraph(self,a):
        global DATA, RefPattDATA, colorstylelist, samplestakenforplot
        global listofanswer, takenforplot
        global listoflinestyle
        global listofcolorstyle,listoflinewidthstyle

#        print(len(DATA.keys()))
        # print(takenforplot)
#        if DATA!={}:
        self.XRDgraph.clear()
#        self.XRDgraphtwin.clear()

        
        coloridx=0
        #plot patterns from DATA
#            samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if takenforplot!=[]:
            samplestakenforplot=takenforplot
        else:
            samplestakenforplot=[]
        if samplestakenforplot!=[]:
            if self.ui.checkBox_showOrig.isChecked():
                if self.ui.checkBox_Qspace.isChecked():
                    minX=min(tth_to_q_list(DATA[samplestakenforplot[0]][2]+DATA[samplestakenforplot[0]][0]))
                    maxX=max(tth_to_q_list(DATA[samplestakenforplot[0]][2]+DATA[samplestakenforplot[0]][0]))
                else:
                    minX=min(DATA[samplestakenforplot[0]][2]+DATA[samplestakenforplot[0]][0])
                    maxX=max(DATA[samplestakenforplot[0]][2]+DATA[samplestakenforplot[0]][0])
            else:
                if self.ui.checkBox_Qspace.isChecked():
                    minX=min(tth_to_q_list(DATA[samplestakenforplot[0]][2]))
                    maxX=max(tth_to_q_list(DATA[samplestakenforplot[0]][2]))
                else:
                    minX=min(DATA[samplestakenforplot[0]][2])
                    maxX=max(DATA[samplestakenforplot[0]][2])
            minY=min(DATA[samplestakenforplot[0]][3])
            maxY=max(DATA[samplestakenforplot[0]][3])
            for item in samplestakenforplot:
                if self.ui.checkBox_Qspace.isChecked():
                    x = tth_to_q_list(DATA[item][2])
                else:
                    x = DATA[item][2]
                y = DATA[item][3]
                if min(x)<minX:
                    minX=min(x)
                if max(x)>maxX:
                    maxX=max(x)
                if min(y)<minY:
                    minY=min(y)
                if max(y)>maxY:
                    maxY=max(y)
                if self.ui.checkBox_legend.isChecked():
                    self.XRDgraph.plot(x,y, label=DATA[item][5][2],linestyle=DATA[item][5][0],color=DATA[item][5][1],linewidth=DATA[item][5][3])
    #                    coloridx+=1
                else:
                    self.XRDgraph.plot(x,y,linestyle=DATA[item][5][0],color=DATA[item][5][1],linewidth=DATA[item][5][3])
    #                    coloridx+=1
                
                if self.ui.checkBox_showOrig.isChecked():
                    if self.ui.checkBox_Qspace.isChecked():
                        x = tth_to_q_list(DATA[item][0])
                    else:
                        x = DATA[item][0]
                    y = DATA[item][1]
                    if min(x)<minX:
                        minX=min(x)
                    if max(x)>maxX:
                        maxX=max(x)
                    if min(y)<minY:
                        minY=min(y)
                    if max(y)>maxY:
                        maxY=max(y)
                    if self.ui.checkBox_legend.isChecked():
                        self.XRDgraph.plot(x,y, label=DATA[item][5][2]+'_original',linestyle=DATA[item][5][0],color=DATA[item][5][1],linewidth=DATA[item][5][3])
                        coloridx+=1
                    else:
                        self.XRDgraph.plot(x,y, linestyle=DATA[item][5][0],color=DATA[item][5][1],linewidth=DATA[item][5][3])
                        coloridx+=1
                else:
                    coloridx+=1
            
            #add text for Peak Names
            if self.ui.checkBox_shownames.isChecked():
                for item in range(len(peaknamesforplot)):
                    if self.ui.checkBox_Qspace.isChecked():
                        self.XRDgraph.text(peaknamesforplot[item][3],peaknamesforplot[item][1],peaknamesforplot[item][2],rotation=90,verticalalignment='bottom',horizontalalignment='left',multialignment='center')                  
                    else:
                        self.XRDgraph.text(peaknamesforplot[item][0],peaknamesforplot[item][1],peaknamesforplot[item][2],rotation=90,verticalalignment='bottom',horizontalalignment='left',multialignment='center')

            
        #plot from RefPattDATA
        reftakenforplot = [str(x.text()) for x in self.ui.listWidget_refpatt.selectedItems()]
        for item in reftakenforplot:
            if self.ui.checkBox_Qspace.isChecked():
                x = tth_to_q_list(RefPattDATA[item][0])
            else:
                x = RefPattDATA[item][0]
            y = RefPattDATA[item][1]
            
            lines = []
            for i in range(len(x)):
                pair=[(x[i],0), (x[i], y[i])]
                lines.append(pair)
            
            linecoll = matcoll.LineCollection(lines, color='black', linestyle='dashed') 
#            linecoll = matcoll.LineCollection(lines)
            self.XRDgraph.add_collection(linecoll)
            self.XRDgraph.scatter(x,y,label=item, color=colorstylelist[coloridx])
            coloridx+=1
            
            if self.ui.checkBox_shownames.isChecked():
                for item1 in range(len(RefPattDATA[item][0])):
                    if samplestakenforplot!=[]:
                        if RefPattDATA[item][0][item1]>minX and RefPattDATA[item][0][item1]<maxX:
                            self.XRDgraph.text(RefPattDATA[item][0][item1],RefPattDATA[item][1][item1],RefPattDATA[item][2][item1],rotation=90,verticalalignment='bottom',horizontalalignment='left',multialignment='center')
                    else:
                        self.XRDgraph.text(RefPattDATA[item][0][item1],RefPattDATA[item][1][item1],RefPattDATA[item][2][item1],rotation=90,verticalalignment='bottom',horizontalalignment='left',multialignment='center')

        #plot the fits if show is ticked
        if self.ui.checkBox_show.isChecked():
#            print("show")
            if samplestakenforplot!=[]:
                for item in samplestakenforplot:
                    if DATA[item][4]!=[]:
                        for item2 in DATA[item][4]:
                            self.XRDgraph.plot(item2["xydata"][0],item2["xydata"][1],color='black',linewidth=3)
                            self.XRDgraph.plot(item2["xydata"][0],item2["xydata"][2],color='black',linewidth=3)
                            self.XRDgraph.plot(item2["xydata"][3],item2["xydata"][4],color='black',linewidth=3)
        
        #legends and graph styles
        if self.ui.checkBox_legend.isChecked():
            if samplestakenforplot!=[] or  reftakenforplot!=[]:
                self.XRDgraph.legend()
        self.XRDgraph.set_ylabel("Intensity (a.u.)")
        if self.ui.checkBox_Qspace.isChecked():
            self.XRDgraph.set_xlabel('q (A$^{-1}$)')
        else:
            self.XRDgraph.set_xlabel("2\u0398 (degree)")
        if samplestakenforplot!=[]:
            self.XRDgraph.axis([minX,maxX,minY,1.1*maxY])  
            if self.ui.checkBox_ylabel.isChecked():
                self.XRDgraph.set_yticklabels([])
                self.XRDgraph.set_yticks([])
                
#            self.XRDgraph.tick_params(direction='in', pad=1)
#            if self.changetoQ.get()==0:
#                self.XRDgraphtwin.axis([minX,maxX,minY,1.1*maxY])
#                self.XRDgraphtwin.tick_params(direction='in', pad=1)
#                self.XRDgraphtwin.set_xticklabels([])
#            else:
#                self.XRDgraphtwin.axis([q_to_tth(minX),q_to_tth(maxX),minY,1.1*maxY])
#                self.XRDgraphtwin.tick_params(direction='in', pad=1)
#                self.XRDgraphtwin.set_xlabel('$^o2\\theta$ , Cu K-$\\alpha$', position=(0.08,0.97))
#        
        self.fig.canvas.draw_idle()
        self.CreateTable()
        
    def CreateTable(self):
        global DATA
        dictdata={}
        testdata=[]
        try:
            samplestakenforplot = [str(x.text()) for x in self.ui.listWidget_samples.selectedItems()]
            if samplestakenforplot!=[]:
                for key in samplestakenforplot:
                    for item in DATA[key][4]:
                        testdata.append([key,item["PeakName"],"%.2f"%item["Position"],"%.2f"%item["PositionQ"],"%.2f"%item["Intensity"],"%.2f"%item["FWHM"],"%.2f"%item["PeakArea"],"%.2f"%item["IntBreadth"],"%.2f"%item["CrystSize"]])
                
            self.ui.tableWidget.setHorizontalHeaderLabels(['name','PeakName','Position (2\u0398)','Position q','Intensity (a.u.)','FWHM (2\u0398)','PeakArea','IntBreadth (2\u0398)', 'CrystalliteSize KL/dcos(thet)(nm)'])

            self.ui.tableWidget.setRowCount(len(testdata))
            i=0
            for item in testdata:
                self.ui.tableWidget.setItem(i,0,QTableWidgetItem(item[0]))
                self.ui.tableWidget.setItem(i,1,QTableWidgetItem(item[1]))
                self.ui.tableWidget.setItem(i,2,QTableWidgetItem('%.2f' % float(item[2])))
                self.ui.tableWidget.setItem(i,3,QTableWidgetItem('%.2f' % float(item[3])))
                self.ui.tableWidget.setItem(i,4,QTableWidgetItem('%.2f' % float(item[4])))
                self.ui.tableWidget.setItem(i,5,QTableWidgetItem('%.2f' % float(item[5])))
                self.ui.tableWidget.setItem(i,6,QTableWidgetItem('%.2f' % float(item[6])))
                self.ui.tableWidget.setItem(i,7,QTableWidgetItem('%.2f' % float(item[7])))
                self.ui.tableWidget.setItem(i,8,QTableWidgetItem('%.2f' % float(item[8])))
                i+=1
        except RuntimeError:
            pass
        
        
    def ConfirmPeaknamechanges(self):
        global DATA
                    
        samplestakenforplot = [str(x.text()) for x in self.ui.listWidget_samples.selectedItems()]

        for item in samplestakenforplot:
            for item1 in range(len(DATA[item][4])):
                DATA[item][4][item1]["PeakName"]=self.ui.tableWidget.item(item1,1).text()
                peaknamesforplot.append([DATA[item][4][item1]["Position"],DATA[item][4][item1]["Intensity"],DATA[item][4][item1]["PeakName"],tth_to_q(DATA[item][4][item1]["Position"])])
        self.updateXRDgraph(0)

#%%    
    def backgroundremoval(self):
        global DATA

        
        samplestakenforplot = [str(x.text()) for x in self.ui.listWidget_samples.selectedItems()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
                y = DATA[item][3]
                y=np.array(y)
                base = peakutils.baseline(y, self.ui.spinBox_PolyNumb.value())
                DATA[item][3]=list(y-base)
        
        self.updateXRDgraph(0)

    def SavitzkyGolayFiltering(self):
        global DATA
        if self.ui.spinBox_SGfilter1.value()>self.ui.spinBox_SGfilter2.value() and self.ui.spinBox_SGfilter1.value()%2==1:
            if self.ui.listWidget_samples.selectedItems()!=():
                samplestakenforplot = [str(x.text()) for x in self.ui.listWidget_samples.selectedItems()]
                if samplestakenforplot!=[]:
                    for item in samplestakenforplot:
                        y = DATA[item][3]
                        y=np.array(y)
                        DATA[item][3] = savitzky_golay(y, window_size=self.ui.spinBox_SGfilter1.value(), order=self.ui.spinBox_SGfilter2.value())
                
                self.updateXRDgraph(0)
        else:
            QMessageBox.information(self, 'Information', "the SG window-size must be larger than the SG order, positive and odd.")
            
            
#     def backgroundremovalImport(self):
#         global DATA
        
#         if self.listboxsamples.curselection()!=():
#             filename =filedialog.askopenfilename(title="Please select the XRD file for background")
            
#             filetoread = open(filename,"r", encoding='ISO-8859-1')
#             filerawdata = list(filetoread.readlines())
# #            samplename=os.path.splitext(os.path.basename(filename))[0]
#     #            print(samplename)
#             xbkg=[]
#             ybkg=[]
#             for j in range(len(filerawdata)):
#                 if ',' in filerawdata[j]:
#                     xbkg.append(float(filerawdata[j].split(',')[0]))
#                     ybkg.append(float(filerawdata[j].split(',')[1]))  
#             f = interp1d(xbkg, ybkg, kind='cubic')
#             samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
#             if samplestakenforplot!=[]:
#                 for item in samplestakenforplot:
#                     y = DATA[item][3]
#                     x = DATA[item][2]                   
#                     DATA[item][3]=[y[item1]-f(x[item1]) for item1 in range(len(x))]
            
#             self.updateXRDgraph(0)
    
    def shiftX(self):
        global DATA
                        
        samplestakenforplot = [str(x.text()) for x in self.ui.listWidget_samples.selectedItems()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
                x = DATA[item][2]
                DATA[item][2] = [item1+self.ui.doubleSpinBox_Xshift.value() for item1 in x]
    
        self.updateXRDgraph(0)
        
    def shiftY(self):
        global DATA
#        print("here")
        samplestakenforplot = [str(x.text()) for x in self.ui.listWidget_samples.selectedItems()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
#                print(self.shiftYval.get())
                y = DATA[item][3]
                DATA[item][3] = [item1+self.ui.doubleSpinBox_Yshift.value() for item1 in y]
    
        self.updateXRDgraph(0)
        
#     def shifttoRef(self):
#         global DATA
# #        still to be implemented
# #        automatic detection of peaks and comparison to the selected RefPattern
# #        then shifts the data to match the ref peak
        
        
#         self.updateXRDgraph(0)    
    
    def scaleYtoRef(self):
        global DATA
        
        samplestakenforplot = [str(x.text()) for x in self.ui.listWidget_samples.selectedItems()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
                y = DATA[item][3]
                maxy=max(y)
                miny=min(y)
                DATA[item][3]=[((item1-miny)/(maxy-miny))*self.ui.doubleSpinBox_rescale.value() for item1 in y]
        
        self.updateXRDgraph(0)
        
    def backtoOriginal(self):
        global DATA
        
        samplestakenforplot = [str(x.text()) for x in self.ui.listWidget_samples.selectedItems()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
                DATA[item][2]=DATA[item][0]
                DATA[item][3]=DATA[item][1]
        
        self.updateXRDgraph(0)
        
#%%        
   
    def PeakDetection(self):
        global DATA,peaknamesforplot
        peaknamesforplot=[]  
        samplestakenforplot = [str(x.text()) for x in self.ui.listWidget_samples.selectedItems()]
        if samplestakenforplot!=[]:
#            positionlist=[]
#            peaknamelist=[]
#            intensitylist=[]
#            fwhmlist=[]
#            print("")
            for item in samplestakenforplot:
                print(item)
                #reinitialize list of dict
                DATA[item][4]=[]
                x=np.array(DATA[item][2])
                y=np.array(DATA[item][3])
                #get peak position
                if self.ui.checkBox_auto.isChecked():
                    threshold=0.01
                    MinDist=50
                    while(1):
                        indexes = peakutils.indexes(y, thres=threshold, min_dist=MinDist)
                        if len(indexes)<15:
                            self.ui.doubleSpinBox_threshold.setValue(threshold)
                            self.ui.spinBox_MinDist.setValue(MinDist)
                            break
                        else:
                            threshold+=0.01
                else:
                    indexes=peakutils.indexes(y, thres=self.ui.doubleSpinBox_threshold.value(), min_dist=self.ui.spinBox_MinDist.value())
#                print("")
#                print(len(indexes))
#                print(len(y))
                for item1 in range(len(indexes)):
                    tempdat={}
                    nbofpoints=self.ui.spinBox_A.value()#on each side of max position
                    appendcheck=0
#                    print(indexes[item1])
                    
                    while(1):
                        try:
                            x0=x[indexes[item1]-nbofpoints:indexes[item1]+nbofpoints]
                            y0=y[indexes[item1]-nbofpoints:indexes[item1]+nbofpoints]
#                            print('')
#                            print(len(y0))
                            try:
                                base=list(peakutils.baseline(y0,1))
                                baselineheightatmaxpeak=base[nbofpoints]
                            except ValueError:
                                print('valueerror: ', len(y0))
                                baselineheightatmaxpeak=0
                            #baseline height
                            bhleft=np.mean(y0[:self.ui.spinBox_B.value()])
                            bhright=np.mean(y0[-self.ui.spinBox_B.value():])
#                                baselineheightatmaxpeak=(bhleft+bhright)/2
#                            baselineheightatmaxpeak=base[nbofpoints]
#                            print(baselineheightatmaxpeak)
#                            print("")
#                            print(abs(bhleft-bhright))
                            if abs(bhleft-bhright)<self.ui.spinBox_C.value():#arbitrary choice of criteria...
                                #find FWHM
                                d=y0-((max(y0)-bhright)/2)
                                ind=np.where(d>bhright)[0]
                                
                                hl=(x0[ind[0]-1]*y0[ind[0]]-y0[ind[0]-1]*x0[ind[0]])/(x0[ind[0]-1]-x0[ind[0]])
                                ml=(y0[ind[0]-1]-hl)/x0[ind[0]-1]
                                yfwhm=((max(y0)-baselineheightatmaxpeak)/2)+baselineheightatmaxpeak
                                xleftfwhm=(yfwhm - hl)/ml
                                hr=(x0[ind[-1]]*y0[ind[-1]+1]-y0[ind[-1]]*x0[ind[-1]+1])/(x0[ind[-1]]-x0[ind[-1]+1])
                                mr=(y0[ind[-1]]-hr)/x0[ind[-1]]
                                xrightfwhm=(yfwhm - hr)/mr
                                
                                FWHM=abs(xrightfwhm-xleftfwhm)
#                                Peakheight=max(y0)-baselineheightatmaxpeak
                                Peakheight=max(y0)-baselineheightatmaxpeak
                                center=x[indexes[item1]]
#                                f = interp1d(x0, y0-base, kind='cubic')
#                                x2 = lambda x: f(x)
#                                peakarea = integrate.quad(x2,x0[0],x0[-1])[0]
                                peakarea = integrate.trapz(y0-base)

#                                print(nbofpoints)
#                                print(baselineheightatmaxpeak)
                                tempdat["Position"]=center
                                tempdat["PositionQ"]=tth_to_q(center)
                                tempdat["FWHM"]=FWHM
                                tempdat["Intensity"]=Peakheight
                                tempdat["PeakArea"]=peakarea
                                tempdat["IntBreadth"]=peakarea/Peakheight
                                tempdat["PeakName"]=''
                                tempdat["CrystSize"]=self.ui.doubleSpinBox_ScherrerCst.value()*0.1*lambdaXRD/(radians(tempdat["IntBreadth"])*cos(radians(tempdat["Position"]/2)))
                                tempdat["xydata"]=[x0,y0, base,[xleftfwhm,xrightfwhm],[yfwhm,yfwhm]]
                                
                                appendcheck=1
                                break
                            else:
                                if nbofpoints>=2*self.ui.spinBox_B.value():
                                    nbofpoints-=2
                                else:
                                    print("indexerror unsolvable")
                                    print(x[indexes[item1]])
                                    break
                        except IndexError:
                            if nbofpoints>=2*self.ui.spinBox_B.value():
                                nbofpoints-=2
                            else:
                                print("indexerror unsolvable")
                                break
                        
                    if appendcheck:
                        DATA[item][4].append(tempdat)
        
        for item in samplestakenforplot:
            for item1 in range(len(DATA[item][4])):
                peaknamesforplot.append([DATA[item][4][item1]["Position"],DATA[item][4][item1]["Intensity"],DATA[item][4][item1]["PeakName"],DATA[item][4][item1]["PositionQ"]])
 
        self.CreateTable()
        self.updateXRDgraph(0)
#%% Time graph

#     def TimeEvolGraph(self):
#         global DATA
        
#         listofsamplenames=[]
#         for key in DATA.keys():
#             if len(DATA[key])>6:
#                 if DATA[key][6]=='itsatimeevoldata':
#                     listofsamplenames.append(DATA[key][7][6])
#         listofsamplenames=list(set(listofsamplenames))
        
#         self.TimeGraphwindow=tk.Tk()
#         center(self.TimeGraphwindow)
        
#         #check first if there are indeed data that was analysed, so with peak data to use
        
#         self.timeevollistbox = Listbox(self.TimeGraphwindow,selectmode=tk.EXTENDED)
#         for name in listofsamplenames:
#           self.timeevollistbox.insert(tk.END, name)
#           self.timeevollistbox.selection_set(0)
#         self.timeevollistbox.pack(fill=tk.BOTH, expand=True)
#         scrollbar = tk.Scrollbar(self.timeevollistbox, orient="vertical")
#         scrollbar.config(command=self.timeevollistbox.yview)
#         scrollbar.pack(side="right", fill="y")
        
#         self.timeevollistbox.config(yscrollcommand=scrollbar.set)

#         frame1=Frame(self.TimeGraphwindow,borderwidth=0,  bg="white")
#         frame1.pack(fill=tk.BOTH,expand=0)
        
#         tk.Button(frame1, text="Select those samples",
#                                     command = self.TimeEvolGraphInterm).pack(fill=tk.X,expand=1)
#         self.TimeGraphwindow.mainloop()
    
#     def TimeEvolGraphInterm(self):
#         global DATA
#         #determining list of peaks 
#         takensamples = [self.timeevollistbox.get(idx) for idx in self.timeevollistbox.curselection()]
# #        print(takensamples)
#         self.TimeEvollistofsamplenames=[]
#         for key in DATA.keys():
#             if len(DATA[key])>6:
#                 if DATA[key][6]=='itsatimeevoldata':
#                     if DATA[key][7][6] in takensamples:
#                         self.TimeEvollistofsamplenames.append(key)
# #        print(listofsamplenames)
#         peakslist=[]
#         for key in self.TimeEvollistofsamplenames:
#             if DATA[key][4]==[]:
#                 messagebox.showinfo("Information","You must analysed the peaks first")
#                 self.TimeGraphwindow.destroy()
#                 break
#             else:
#                 for item in DATA[key][4]:
#                     peakslist.append(round(item["Position"],0))
# #        print(peakslist)
#         self.peakslist=sorted(list(set(peakslist)))
# #        print(self.peakslist)
#         self.TimeEvolGraph2()
    
#     def TimeEvolGraph2(self):
#         global DATA        
#         self.TimeGraphwindow.destroy()
#         self.TimeGraphwindow2=tk.Toplevel()
#         self.TimeGraphwindow2.wm_title("TimeEvolGraph")
#         center(self.TimeGraphwindow2)
#         self.TimeGraphwindow2.geometry("500x300")
#         self.TimeGraphwindow2.protocol("WM_DELETE_WINDOW", self.on_closingtimeevol)
        
#         frame0=Frame(self.TimeGraphwindow2,borderwidth=0,  bg="white")
#         frame0.pack(fill=tk.BOTH,expand=1)
#         self.timeEvolfig = plt.figure(figsize=(3, 2))
#         canvas = FigureCanvasTkAgg(self.timeEvolfig, frame0)
#         canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
#         self.timeEvolfig1 = self.timeEvolfig.add_subplot(111)
        
#         frame1=Frame(self.TimeGraphwindow2,borderwidth=0,  bg="white")
#         frame1.pack(fill=tk.X,expand=0)
        
        
#         self.PeakChoice=StringVar()
#         self.PeakChoice.set("Peaks positions")
#         PeakChoiceList = self.peakslist
#         self.dropMenuPeak = OptionMenu(frame1, self.PeakChoice, *PeakChoiceList, command=()).pack(side="left",fill=tk.X,expand=1)

#         ParamChoiceList = ["FWHM","Intensity","PeakArea","IntBreadth","CrystSize"]
#         self.ParamChoice=StringVar()
#         self.ParamChoice.set("Intensity") # default choice
#         self.dropMenuParam = OptionMenu(frame1, self.ParamChoice, *ParamChoiceList, command=()).pack(side="left",fill=tk.X,expand=1)

#         frame2=Frame(self.TimeGraphwindow2,borderwidth=0,  bg="white")
#         frame2.pack(fill=tk.BOTH,expand=0)
        
#         ynormalChoiceList = ["Original","Normalize y, first","Normalize y, max"]
#         self.ynormalTimeEvol=StringVar()
#         self.ynormalTimeEvol.set("Normalization") # default choice
#         self.dropMenuParam = OptionMenu(frame1, self.ynormalTimeEvol, *ynormalChoiceList, command=()).pack(side="left",fill=tk.X,expand=1)

        
# #        self.ynormalTimeEvol = IntVar()
# #        Checkbutton(frame2,text="Normalize y, first",variable=self.ynormalTimeEvol, command = (),
# #                           onvalue=1,offvalue=0,height=1, width=10, fg='black',background='white').pack(side=tk.LEFT,expand=1)
# #        self.ynormalTimeEvol.set(0)
# #        self.ynormalMaxTimeEvol = IntVar()
# #        Checkbutton(frame2,text="Normalize y, max",variable=self.ynormalMaxTimeEvol, command = (),
# #                           onvalue=1,offvalue=0,height=1, width=10, fg='black',background='white').pack(side=tk.LEFT,expand=1)
# #        self.ynormalMaxTimeEvol.set(0)
#         self.xnormalTimeEvol = IntVar()
#         Checkbutton(frame2,text="start all x at 0",variable=self.xnormalTimeEvol, command = (),
#                            onvalue=1,offvalue=0,height=1, width=10, fg='black',background='white').pack(side=tk.LEFT,expand=1)
#         self.xnormalTimeEvol.set(0)
#         frame3=Frame(self.TimeGraphwindow2,borderwidth=0,  bg="white")
#         frame3.pack(fill=tk.BOTH,expand=0)
#         tk.Button(frame3, text="Back to samples selection", command = self.backtoTimeEvolGraph).pack(side=tk.LEFT,fill=tk.BOTH,expand=1) 
#         tk.Button(frame3, text="Preview graph", command = self.GenerationTimeEvolGraph).pack(side=tk.LEFT,fill=tk.BOTH,expand=1) 
#         tk.Button(frame3, text="Export", command = self.ExportTimeEvolGraph).pack(side=tk.LEFT,fill=tk.BOTH,expand=1) 

#     def on_closingtimeevol(self):
#         self.TimeGraphwindow2.destroy()
        
#         self.frame11.destroy()
        
#         self.frame11=Frame(self.frame1,borderwidth=0,  bg="white")
#         self.frame11.pack(fill=tk.BOTH,expand=1)
#         self.fig1 = plt.figure(figsize=(1, 3))
#         canvas = FigureCanvasTkAgg(self.fig1, self.frame11)
#         canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
#         self.XRDgraph = plt.subplot2grid((1, 1), (0, 0), colspan=3)
# #        self.XRDgraphtwin=self.XRDgraph.twiny()
#         self.toolbar = NavigationToolbar2TkAgg(canvas, self.frame11)
#         self.toolbar.update()
#         canvas._tkcanvas.pack(fill=tk.BOTH,expand=1)
        
#         self.updateXRDgraph(0)
        
#     def backtoTimeEvolGraph(self):
#         self.TimeGraphwindow2.destroy()
#         self.TimeEvolGraph()
    
#     def ExportTimeEvolGraph(self):
#         f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
#         self.timeEvolfig.savefig(f[:-4]+'.png', dpi=300, transparent=False) 
#         file = open(str(f[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
#         file.writelines("%s" % item for item in self.DATAforexport1)
#         file.close()
    
#     def GenerationTimeEvolGraph(self):
#         global DATA
#         self.timeEvolfig1.clear()
        
#         timeevolgraphDATA={}
#         for samplename in self.TimeEvollistofsamplenames:
#             newkey=samplename.split('_')[2]+'_'+samplename.split('_')[3]+'_'+samplename.split('_')[4]+'_'+samplename.split('_')[5]
#             if newkey not in timeevolgraphDATA.keys():
#                 timeevolgraphDATA[newkey]=[[],[]]
#             nopeakfound=1
#             for peak in DATA[samplename][4]:
#                 if round(peak["Position"],0)==float(self.PeakChoice.get()):
#                     timeevolgraphDATA[newkey][1].append(peak[self.ParamChoice.get()])
#                     timeevolgraphDATA[newkey][0].append(float(samplename.split('_')[6]))
#                     nopeakfound=0
#                     break
#             if nopeakfound:
#                 timeevolgraphDATA[newkey][1].append(0)
#                 timeevolgraphDATA[newkey][0].append(float(samplename.split('_')[6]))
        
# #        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
        
# #        self.timeEvolfig = plt.figure(figsize=(6, 4))
# #        self.timeEvolfig1 = self.timeEvolfig.add_subplot(111)  
#         datafortxtexport=[]
#         headings=["",""]
#         for key in timeevolgraphDATA:
#             if self.ynormalTimeEvol.get()=="Original":
#                 if self.xnormalTimeEvol.get()==0:#original data
#                     self.timeEvolfig1.plot(timeevolgraphDATA[key][0],timeevolgraphDATA[key][1],label=key)
#                     self.timeEvolfig1.set_ylabel(self.ParamChoice.get())
#                     datafortxtexport.append(timeevolgraphDATA[key][0])
#                     datafortxtexport.append(timeevolgraphDATA[key][1])
#                 else:#time is starting at zero for all curves
#                     x=[item-timeevolgraphDATA[key][0][0] for item in timeevolgraphDATA[key][0]]
#                     self.timeEvolfig1.plot(x,timeevolgraphDATA[key][1],label=key)
#                     self.timeEvolfig1.set_ylabel(self.ParamChoice.get())
#                     datafortxtexport.append(x)
#                     datafortxtexport.append(timeevolgraphDATA[key][1])
#             elif self.ynormalTimeEvol.get()=="Normalize y, first":
#                 if self.xnormalTimeEvol.get()==0:#y is normalized
#                     y=[m/timeevolgraphDATA[key][1][0] for m in timeevolgraphDATA[key][1]]
#                     self.timeEvolfig1.plot(timeevolgraphDATA[key][0],y,label=key)
#                     self.timeEvolfig1.set_ylabel(self.ParamChoice.get()+" NormalizedFirst")
#                     datafortxtexport.append(timeevolgraphDATA[key][0])
#                     datafortxtexport.append(y)
#                 else:#y is normalized and time is starting at zero 
#                     try:
#                         x=[item-timeevolgraphDATA[key][0][0] for item in timeevolgraphDATA[key][0]]
#                         y=[m/timeevolgraphDATA[key][1][0] for m in timeevolgraphDATA[key][1]]
#                         self.timeEvolfig1.plot(x,y,label=key)
#                         self.timeEvolfig1.set_ylabel(self.ParamChoice.get()+" NormalizedFirst")
#                         datafortxtexport.append(x)
#                         datafortxtexport.append(y)
#                     except ZeroDivisionError:
#                         print("ZeroDivisionError")
#             elif self.ynormalTimeEvol.get()=="Normalize y, max":
#                 if self.xnormalTimeEvol.get()==0:#y is normalized
#                     y=[m/max(timeevolgraphDATA[key][1]) for m in timeevolgraphDATA[key][1]]
#                     self.timeEvolfig1.plot(timeevolgraphDATA[key][0],y,label=key)
#                     self.timeEvolfig1.set_ylabel(self.ParamChoice.get()+" NormalizedMax")
#                     datafortxtexport.append(timeevolgraphDATA[key][0])
#                     datafortxtexport.append(y)
#                 else:#y is normalized and time is starting at zero
#                     x=[item-timeevolgraphDATA[key][0][0] for item in timeevolgraphDATA[key][0]]
#                     y=[m/max(timeevolgraphDATA[key][1]) for m in timeevolgraphDATA[key][1]]
#                     self.timeEvolfig1.plot(x,y,label=key)
#                     self.timeEvolfig1.set_ylabel(self.ParamChoice.get()+" NormalizedMax")
#                     datafortxtexport.append(x)
#                     datafortxtexport.append(y)
               
                        
#             headings[0]+="Time\t"+self.ParamChoice.get()+"\t"
#             headings[1]+="\t"+key+"\t"
#         headings[0]=headings[0][:-1]+'\n'
#         headings[1]=headings[1][:-1]+'\n'
#         self.timeEvolfig1.set_xlabel("Time (minutes)")
#         self.timeEvolfig1.legend(ncol=1)
#         self.timeEvolfig1.set_title("Peak: ~"+str(self.PeakChoice.get()))
# #        self.timeEvolfig.savefig(f[:-4]+'.png', dpi=300, transparent=False) 
        
#         #export txt files
#         datafortxtexport=map(list, six.moves.zip_longest(*datafortxtexport, fillvalue=' '))
#         self.DATAforexport1=headings
#         for item in datafortxtexport:
#             line=""
#             for item1 in item:
#                 line=line+str(item1)+"\t"
#             line=line[:-1]+"\n"
#             self.DATAforexport1.append(line)
# #        file = open(str(f[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
# #        file.writelines("%s" % item for item in self.DATAforexport1)
# #        file.close() 
#         plt.gcf().canvas.draw()
        
#%%#############
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = XRDapp()
    window.show()
    sys.exit(app.exec())

