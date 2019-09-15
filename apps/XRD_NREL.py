#! python3

import os, datetime

#import matplotlib
#matplotlib.use("TkAgg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.backends.tkagg as tkagg
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg
from matplotlib import collections as matcoll
from matplotlib import colors as mcolors
from tkinter.ttk import Treeview
import tkinter as tk
from tkinter import ttk, Tk, messagebox, Entry, Button, Checkbutton, IntVar, Toplevel, OptionMenu, Frame, StringVar, Scrollbar, Listbox
from tkinter import filedialog
from tkinter import *
from pathlib import Path
import numpy as np
import xlsxwriter
import xlrd
from scipy.interpolate import interp1d, UnivariateSpline
from scipy import integrate, stats
from tkcolorpicker import askcolor 
import six
from functools import partial
import math
import sqlite3
import csv
from scipy.optimize import curve_fit
import peakutils
from peakutils.plot import plot as pplot
from tkinter import font as tkFont
from math import factorial,radians, sin, cos

"""
TODOLIST

- make user manual

- (shift to ref auto)

- export as ref file function

- delete entry from list of samples

- add a "cancel last operation" button, that would be a back button if do a mistake and don't want to but complitely back to original

- FWHM left and right

- crystallite size only: B = K*lambda/(L*cos(theta))
K=0.89 for integral breadth of spherical crystals w/ cubic symmetry
lamda=1.54
L=integral breadth
theta= peak position/2 in radians

- microstrain only
•When microstrain is present, the calculated “Crystallite Size only” will tend to decrease as a function of 2theta
•When crystallite size broadening is present, the calculated “Microstrainonly” will tend to decrease as a function of 2theta

- export williamson-hall plot with linear regression, and fit to find the strain component

https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
make colormap choice an option for the user: text field

- load file parameters that sets all entry text to some user-defined values, 
save param and load param buttons


- add square root, log or linear




"""
#%%
LARGE_FONT= ("Verdana", 12)

def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

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

#%%###############################################################################             
    
class XRDApp(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "XRDApp")
        Toplevel.config(self,background="white")
        self.wm_geometry("780x650")
        center(self)
        self.initUI()


    def initUI(self):
        global refsamplenameslist, Patternsamplenameslist
        
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.canvas0 = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.superframe=Frame(self.canvas0,background="#ffffff")
        self.canvas0.pack(side="left", fill="both", expand=True)
        
        label = tk.Label(self.canvas0, text="XRD DATA Analyzer", font=LARGE_FONT, bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)

        
        self.frame1=Frame(self.canvas0,borderwidth=0,  bg="white")
        self.frame1.pack(fill=tk.BOTH,expand=1)
        self.frame1.bind("<Configure>", self.onFrameConfigure)
        self.frame11=Frame(self.frame1,borderwidth=0,  bg="white")
        self.frame11.pack(fill=tk.BOTH,expand=1)
        self.fig1 = plt.figure(figsize=(1, 3))
        canvas = FigureCanvasTkAgg(self.fig1, self.frame11)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.XRDgraph = plt.subplot2grid((1, 1), (0, 0), colspan=3)
#        self.XRDgraphtwin=self.XRDgraph.twiny()
        self.toolbar = NavigationToolbar2TkAgg(canvas, self.frame11)
        self.toolbar.update()
        canvas._tkcanvas.pack(fill=tk.BOTH,expand=1) 
        
        frame2=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame2.pack(fill=tk.BOTH,expand=0)
        
        frame21=Frame(frame2,borderwidth=0,  bg="lightgrey")
        frame21.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        frame211=Frame(frame21,borderwidth=0,  bg="lightgrey")
        frame211.pack(fill=tk.BOTH,expand=1)
        self.shift = tk.DoubleVar()
        Entry(frame211, textvariable=self.shift,width=3).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.shiftBut = Button(frame211, text="X Shift",command = self.shiftX).pack(side=tk.LEFT,expand=1)
        self.shift.set(0)
        self.shiftYval = tk.DoubleVar()
        Entry(frame211, textvariable=self.shiftYval,width=3).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.shiftYBut = Button(frame211, text="Y Shift",command = self.shiftY).pack(side=tk.LEFT,expand=1)
        self.shiftYval.set(0)
        self.ylabel = IntVar()
        Checkbutton(frame211,text="noylab",variable=self.ylabel, command = lambda: self.updateXRDgraph(0),
                           onvalue=1,offvalue=0,height=1, width=4, fg='black',background='lightgrey').pack(side=tk.LEFT,expand=1)
        self.ylog = IntVar()
        Checkbutton(frame211,text="ylog",variable=self.ylog, command = lambda: self.updateXRDgraph(0),
                           onvalue=1,offvalue=0,height=1, width=4, fg='black',background='lightgrey').pack(side=tk.LEFT,expand=1)

        self.changetoQ = IntVar()
        Checkbutton(frame211,text="q?",variable=self.changetoQ, command = lambda: self.updateXRDgraph(0),
                           onvalue=1,offvalue=0,height=1, width=1, fg='black',background='lightgrey').pack(side=tk.LEFT,expand=1)
        self.CheckLegend = IntVar()
        Checkbutton(frame211,text="",variable=self.CheckLegend, command = lambda: self.updateXRDgraph(0),
                           onvalue=1,offvalue=0,height=1, width=3, fg='black',background='lightgrey').pack(side=tk.LEFT,expand=1)

        self.changeXRDlegend = Button(frame211, text="Legend",
                            command = self.ChangeLegendXRDgraph)
        self.changeXRDlegend.pack(side=tk.LEFT,expand=1)
                        
        frame212=Frame(frame21,borderwidth=0,  bg="lightgrey")
        frame212.pack(fill=tk.BOTH,expand=1)
        self.backgroundorder = tk.IntVar()
        Entry(frame212, textvariable=self.backgroundorder,width=1).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.backgroundorder.set(12)
        self.CheckBkgRemoval = Button(frame212, text="BkgRemovalPoly",command = self.backgroundremoval).pack(side=tk.LEFT,expand=1)
        self.SGwinsize = tk.IntVar()
        Entry(frame212, textvariable=self.SGwinsize,width=1).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.SGwinsize.set(31)
        self.SGorder = tk.IntVar()
        Entry(frame212, textvariable=self.SGorder,width=1).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.SGorder.set(5)
        self.CheckBkgRemoval = Button(frame212, text="SavitzkyGolayFilter",command = self.SavitzkyGolayFiltering).pack(side=tk.LEFT,expand=1)
        self.CheckBkgRemovalImport = Button(frame212, text="BkgRefImport",command = self.backgroundremovalImport).pack(side=tk.LEFT,expand=1)

#        refpattern=StringVar()
#        refpatternlist=['Original','Si','ITO']#to be replace by actual files in a specific folder
#        cbbox = ttk.Combobox(frame212, textvariable=refpattern, values=refpatternlist)            
#        cbbox.pack(side=tk.LEFT,expand=0)
#        refpattern.set(refpatternlist[0])
#        self.refbut = Button(frame212, text="ShiftToRef",command = self.shifttoRef).pack(side=tk.LEFT,expand=1)
                
        frame213=Frame(frame21,borderwidth=0,  bg="lightgrey")
        frame213.pack(fill=tk.BOTH,expand=1)        
        self.rescale = tk.DoubleVar()
        Entry(frame213, textvariable=self.rescale,width=3).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.rescale.set(1000)
        self.rescaleBut = Button(frame213, text="Rescale",command = self.scaleYtoRef).pack(side=tk.LEFT,expand=1)
        self.backtoOriginalBut = Button(frame213, text="BackToOriginal",command = self.backtoOriginal).pack(side=tk.LEFT,expand=1)

        self.showOriginal = IntVar()
        Checkbutton(frame213,text="showOrig.",variable=self.showOriginal, command = lambda: self.updateXRDgraph(0),
                           onvalue=1,offvalue=0,height=1, width=3, fg='black',background='lightgrey').pack(side=tk.LEFT,fill=tk.X,expand=1)

        
        frame22=Frame(frame2,borderwidth=0,  bg="white")
        frame22.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        frame221=Frame(frame22,borderwidth=0,  bg="white")
        frame221.pack(fill=tk.BOTH,expand=1)
        self.importBut = Button(frame221, text="Import",command = self.importDATA).pack(side=tk.LEFT,expand=1)
        self.importRefBut = Button(frame221, text="ImportRef",command = self.importRefDATA).pack(side=tk.LEFT,expand=1)
        self.UpdateBut = Button(frame221, text="Update",command = lambda: self.updateXRDgraph(0)).pack(side=tk.LEFT,expand=1)
        frame222=Frame(frame22,borderwidth=0,  bg="grey")
        frame222.pack(fill=tk.BOTH,expand=1)
        self.ShowPeakDetectionBut = Button(frame222, text="Peak Detection",command = self.PeakDetection).pack(side="left",expand=1)
        self.ChangePeakNameBut = Button(frame222, text="Change Peak Names",command = self.ChangePeakNames).pack(side="left",expand=1)
        self.ScherrerCst = tk.DoubleVar()
        Entry(frame222, textvariable=self.ScherrerCst,width=4).pack(side=tk.LEFT,expand=1)
        self.ScherrerCst.set(0.89)
        tk.Label(frame222, text="ScherrerCst", bg="grey").pack(side=tk.LEFT,expand=1)
        self.CheckPeakNames = IntVar()
        Checkbutton(frame222,text="ShowNames",variable=self.CheckPeakNames, 
                           onvalue=1,offvalue=0,height=1, width=10, command = lambda: self.updateXRDgraph(0),fg='black',background='grey').pack(side=tk.LEFT,expand=1)
        frame223=Frame(frame22,borderwidth=0,  bg="grey")
        frame223.pack(fill=tk.BOTH,expand=1)
        self.AutoPeakDetecAdjust = IntVar()
        Checkbutton(frame223,text="Auto",variable=self.AutoPeakDetecAdjust, 
                           onvalue=1,offvalue=0,height=1, width=3, fg='black',background='grey').pack(side=tk.LEFT,expand=1)
        self.thresholdPeakDet = tk.DoubleVar()
        Entry(frame223, textvariable=self.thresholdPeakDet,width=5).pack(side=tk.LEFT,expand=1)
        self.thresholdPeakDet.set(0.08)
        tk.Label(frame223, text="Threshold", bg="grey").pack(side=tk.LEFT,expand=1)
        self.MinDistPeakDet = tk.DoubleVar()
        Entry(frame223, textvariable=self.MinDistPeakDet,width=3).pack(side=tk.LEFT,expand=1)
        self.MinDistPeakDet.set(20)
        tk.Label(frame223, text="MinDist", bg="grey").pack(side=tk.LEFT,expand=1)
        self.nbofpoints = tk.IntVar()
        Entry(frame223, textvariable=self.nbofpoints,width=5).pack(side=tk.LEFT,expand=1)
        self.nbofpoints.set(35)
        self.basepoints = tk.IntVar()
        Entry(frame223, textvariable=self.basepoints,width=5).pack(side=tk.LEFT,expand=1)
        self.basepoints.set(10)
        self.diffleftright = tk.IntVar()
        Entry(frame223, textvariable=self.diffleftright,width=5).pack(side=tk.LEFT,expand=1)
        self.diffleftright.set(80)
        self.CheckPeakDetec = IntVar()
        Checkbutton(frame223,text="Show",variable=self.CheckPeakDetec, 
                           onvalue=1,offvalue=0,height=1, width=3, command = lambda: self.updateXRDgraph(0),fg='black',background='grey').pack(side=tk.LEFT,expand=1)
        
               
#        frame23=Frame(frame2,borderwidth=0,  bg="lightgrey")
#        frame23.pack(fill=tk.BOTH,expand=1)
#        frame231=Frame(frame23,borderwidth=0,  bg="lightgrey")
#        frame231.pack(fill=tk.BOTH,expand=1)
        self.ExportBut = Button(frame221, text="Export",command =self.Export).pack(side="left",expand=1)
        self.ExportWHBut = Button(frame221, text="ExportWillHall",command =self.ExportWH).pack(side="left",expand=1)
#        self.ExportRefFileBut = Button(frame221, text="ExportasRefFile",command = ()).pack(side="left",expand=1)

        self.TimeEvolBut = Button(frame221, text="TimeEvolGraph",command = self.TimeEvolGraph).pack(side="left",expand=1)

#        self.GraphCheck = IntVar()
#        legend=Checkbutton(frame23,text='Graph',variable=self.GraphCheck, 
#                           onvalue=1,offvalue=0,height=1, width=10, command = (), bg="lightgrey")
#        legend.pack(expand=1)
#        self.PeakData = IntVar()
#        legend=Checkbutton(frame23,text='PeakData',variable=self.PeakData, 
#                           onvalue=1,offvalue=0,height=1, width=10, command = (), bg="lightgrey")
#        legend.pack(expand=1)
        
        frame5=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame5.pack(fill=tk.BOTH,expand=1)
        frame3=Frame(frame5,borderwidth=0,  bg="white")
        frame3.pack(side="left", fill=tk.BOTH,expand=1)
        frame32=Frame(frame3,borderwidth=0,  bg="white")
        frame32.pack(fill=tk.BOTH,expand=1)
        
        #listbox for imported samples
        self.frame3220=Frame(frame32,borderwidth=0,  bg="white")
        self.frame3220.pack(fill=tk.BOTH,expand=1)
        self.frame322=Frame(self.frame3220,borderwidth=0,  bg="white")
        self.frame322.pack(fill=tk.BOTH,expand=1)
        self.frame3221=Frame(self.frame322,borderwidth=0,  bg="white")
        self.frame3221.pack(fill=tk.BOTH,expand=1)
        importedsamplenames = StringVar()
        self.listboxsamples=Listbox(self.frame3221,listvariable=importedsamplenames, selectmode=tk.EXTENDED,width=30, height=3, exportselection=0)
        self.listboxsamples.bind('<<ListboxSelect>>', self.UpdateGraph0)
        self.listboxsamples.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(self.frame3221, orient="vertical")
        scrollbar.config(command=self.listboxsamples.yview)
        scrollbar.pack(side="right", fill="y")
        xscrollbar = tk.Scrollbar(self.frame322, orient="horizontal")
        xscrollbar.config(command=self.listboxsamples.xview)
        xscrollbar.pack(side="bottom", fill="x")
        self.listboxsamples.config(yscrollcommand=scrollbar.set)
        self.listboxsamples.config(xscrollcommand=xscrollbar.set)
        
        for item in Patternsamplenameslist:
            self.listboxsamples.insert(tk.END,item)

        #lisbox for ref pattern
        self.frame323=Frame(frame32,borderwidth=0,  bg="white")
        self.frame323.pack(fill=tk.BOTH,expand=1)
        self.frame3231=Frame(self.frame323,borderwidth=0,  bg="white")
        self.frame3231.pack(fill=tk.BOTH,expand=1)
        refsamplenames = StringVar()
        self.listboxref=Listbox(self.frame3231,listvariable=refsamplenames, selectmode=tk.MULTIPLE,width=30, height=3, exportselection=0)
        self.listboxref.bind('<<ListboxSelect>>', self.updateXRDgraph)
        self.listboxref.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(self.frame3231, orient="vertical")
        scrollbar.config(command=self.listboxref.yview)
        scrollbar.pack(side="right", fill="y")
        self.listboxref.config(yscrollcommand=scrollbar.set)
        
        for item in refsamplenameslist:
            self.listboxref.insert(tk.END,item)
            
        
#        frame321=Frame(frame32,borderwidth=0,  bg="white")
#        frame321.pack(fill=tk.X,expand=0)
#        self.addtolistBut = Button(frame321, text="Add to list",command = ()).pack(side=tk.LEFT,expand=1)
#        self.RemoveFromListBut = Button(frame321, text="Remove from list",command = ()).pack(side=tk.LEFT,expand=1)




        self.frame4=Frame(frame5,borderwidth=0,  bg="white")
        self.frame4.pack(side="right",fill=tk.BOTH,expand=1)
        self.frame41=Frame(self.frame4,borderwidth=0,  bg="white")
        self.frame41.pack(side="right",fill=tk.BOTH,expand=1)
        
        
#        self.addtolistBut = Button(self.frame4, text="Add to list",command = ()).pack(side=tk.LEFT,expand=1)
#        self.TableBuilder(self.frame4)
        self.CreateTable()

#%%############# 
    def on_closing(self):
        global DATA, RefPattDATA, Patternsamplenameslist, colorstylelist
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            DATA={}
            RefPattDATA={}
            Patternsamplenameslist=[]
            colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']
            plt.close()
            self.destroy()
            self.master.deiconify()
    def onFrameConfigure(self, event):
        #self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))
        self.canvas0.configure(scrollregion=(0,0,500,500))

            
#%% Time graph

    def TimeEvolGraph(self):
        global DATA
        
        listofsamplenames=[]
        for key in DATA.keys():
            if len(DATA[key])>6:
                if DATA[key][6]=='itsatimeevoldata':
                    listofsamplenames.append(DATA[key][7][6])
        listofsamplenames=list(set(listofsamplenames))
        
        self.TimeGraphwindow=tk.Tk()
        center(self.TimeGraphwindow)
        
        #check first if there are indeed data that was analysed, so with peak data to use
        
        self.timeevollistbox = Listbox(self.TimeGraphwindow,selectmode=tk.EXTENDED)
        for name in listofsamplenames:
          self.timeevollistbox.insert(tk.END, name)
          self.timeevollistbox.selection_set(0)
        self.timeevollistbox.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.timeevollistbox, orient="vertical")
        scrollbar.config(command=self.timeevollistbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.timeevollistbox.config(yscrollcommand=scrollbar.set)

        frame1=Frame(self.TimeGraphwindow,borderwidth=0,  bg="white")
        frame1.pack(fill=tk.BOTH,expand=0)
        
        tk.Button(frame1, text="Select those samples",
                                    command = self.TimeEvolGraphInterm).pack(fill=tk.X,expand=1)
        self.TimeGraphwindow.mainloop()
    
    def TimeEvolGraphInterm(self):
        global DATA
        #determining list of peaks 
        takensamples = [self.timeevollistbox.get(idx) for idx in self.timeevollistbox.curselection()]
#        print(takensamples)
        self.TimeEvollistofsamplenames=[]
        for key in DATA.keys():
            if len(DATA[key])>6:
                if DATA[key][6]=='itsatimeevoldata':
                    if DATA[key][7][6] in takensamples:
                        self.TimeEvollistofsamplenames.append(key)
#        print(listofsamplenames)
        peakslist=[]
        for key in self.TimeEvollistofsamplenames:
            if DATA[key][4]==[]:
                messagebox.showinfo("Information","You must analysed the peaks first")
                self.TimeGraphwindow.destroy()
                break
            else:
                for item in DATA[key][4]:
                    peakslist.append(round(item["Position"],0))
#        print(peakslist)
        self.peakslist=sorted(list(set(peakslist)))
#        print(self.peakslist)
        self.TimeEvolGraph2()
    
    def TimeEvolGraph2(self):
        global DATA        
        self.TimeGraphwindow.destroy()
        self.TimeGraphwindow2=tk.Toplevel()
        self.TimeGraphwindow2.wm_title("TimeEvolGraph")
        center(self.TimeGraphwindow2)
        self.TimeGraphwindow2.geometry("500x300")
        self.TimeGraphwindow2.protocol("WM_DELETE_WINDOW", self.on_closingtimeevol)
        
        frame0=Frame(self.TimeGraphwindow2,borderwidth=0,  bg="white")
        frame0.pack(fill=tk.BOTH,expand=1)
        self.timeEvolfig = plt.figure(figsize=(3, 2))
        canvas = FigureCanvasTkAgg(self.timeEvolfig, frame0)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.timeEvolfig1 = self.timeEvolfig.add_subplot(111)
        
        frame1=Frame(self.TimeGraphwindow2,borderwidth=0,  bg="white")
        frame1.pack(fill=tk.X,expand=0)
        
        
        self.PeakChoice=StringVar()
        self.PeakChoice.set("Peaks positions")
        PeakChoiceList = self.peakslist
        self.dropMenuPeak = OptionMenu(frame1, self.PeakChoice, *PeakChoiceList, command=()).pack(side="left",fill=tk.X,expand=1)

        ParamChoiceList = ["FWHM","Intensity","PeakArea","IntBreadth","CrystSize"]
        self.ParamChoice=StringVar()
        self.ParamChoice.set("Intensity") # default choice
        self.dropMenuParam = OptionMenu(frame1, self.ParamChoice, *ParamChoiceList, command=()).pack(side="left",fill=tk.X,expand=1)

        frame2=Frame(self.TimeGraphwindow2,borderwidth=0,  bg="white")
        frame2.pack(fill=tk.BOTH,expand=0)
        
        ynormalChoiceList = ["Original","Normalize y, first","Normalize y, max"]
        self.ynormalTimeEvol=StringVar()
        self.ynormalTimeEvol.set("Normalization") # default choice
        self.dropMenuParam = OptionMenu(frame1, self.ynormalTimeEvol, *ynormalChoiceList, command=()).pack(side="left",fill=tk.X,expand=1)

        
#        self.ynormalTimeEvol = IntVar()
#        Checkbutton(frame2,text="Normalize y, first",variable=self.ynormalTimeEvol, command = (),
#                           onvalue=1,offvalue=0,height=1, width=10, fg='black',background='white').pack(side=tk.LEFT,expand=1)
#        self.ynormalTimeEvol.set(0)
#        self.ynormalMaxTimeEvol = IntVar()
#        Checkbutton(frame2,text="Normalize y, max",variable=self.ynormalMaxTimeEvol, command = (),
#                           onvalue=1,offvalue=0,height=1, width=10, fg='black',background='white').pack(side=tk.LEFT,expand=1)
#        self.ynormalMaxTimeEvol.set(0)
        self.xnormalTimeEvol = IntVar()
        Checkbutton(frame2,text="start all x at 0",variable=self.xnormalTimeEvol, command = (),
                           onvalue=1,offvalue=0,height=1, width=10, fg='black',background='white').pack(side=tk.LEFT,expand=1)
        self.xnormalTimeEvol.set(0)
        frame3=Frame(self.TimeGraphwindow2,borderwidth=0,  bg="white")
        frame3.pack(fill=tk.BOTH,expand=0)
        tk.Button(frame3, text="Back to samples selection", command = self.backtoTimeEvolGraph).pack(side=tk.LEFT,fill=tk.BOTH,expand=1) 
        tk.Button(frame3, text="Preview graph", command = self.GenerationTimeEvolGraph).pack(side=tk.LEFT,fill=tk.BOTH,expand=1) 
        tk.Button(frame3, text="Export", command = self.ExportTimeEvolGraph).pack(side=tk.LEFT,fill=tk.BOTH,expand=1) 

    def on_closingtimeevol(self):
        self.TimeGraphwindow2.destroy()
        
        self.frame11.destroy()
        
        self.frame11=Frame(self.frame1,borderwidth=0,  bg="white")
        self.frame11.pack(fill=tk.BOTH,expand=1)
        self.fig1 = plt.figure(figsize=(1, 3))
        canvas = FigureCanvasTkAgg(self.fig1, self.frame11)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.XRDgraph = plt.subplot2grid((1, 1), (0, 0), colspan=3)
#        self.XRDgraphtwin=self.XRDgraph.twiny()
        self.toolbar = NavigationToolbar2TkAgg(canvas, self.frame11)
        self.toolbar.update()
        canvas._tkcanvas.pack(fill=tk.BOTH,expand=1)
        
        self.updateXRDgraph(0)
        
    def backtoTimeEvolGraph(self):
        self.TimeGraphwindow2.destroy()
        self.TimeEvolGraph()
    
    def ExportTimeEvolGraph(self):
        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
        self.timeEvolfig.savefig(f[:-4]+'.png', dpi=300, transparent=False) 
        file = open(str(f[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
        file.writelines("%s" % item for item in self.DATAforexport1)
        file.close()
    
    def GenerationTimeEvolGraph(self):
        global DATA
        self.timeEvolfig1.clear()
        
        timeevolgraphDATA={}
        for samplename in self.TimeEvollistofsamplenames:
            newkey=samplename.split('_')[2]+'_'+samplename.split('_')[3]+'_'+samplename.split('_')[4]+'_'+samplename.split('_')[5]
            if newkey not in timeevolgraphDATA.keys():
                timeevolgraphDATA[newkey]=[[],[]]
            nopeakfound=1
            for peak in DATA[samplename][4]:
                if round(peak["Position"],0)==float(self.PeakChoice.get()):
                    timeevolgraphDATA[newkey][1].append(peak[self.ParamChoice.get()])
                    timeevolgraphDATA[newkey][0].append(float(samplename.split('_')[6]))
                    nopeakfound=0
                    break
            if nopeakfound:
                timeevolgraphDATA[newkey][1].append(0)
                timeevolgraphDATA[newkey][0].append(float(samplename.split('_')[6]))
        
#        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
        
#        self.timeEvolfig = plt.figure(figsize=(6, 4))
#        self.timeEvolfig1 = self.timeEvolfig.add_subplot(111)  
        datafortxtexport=[]
        headings=["",""]
        for key in timeevolgraphDATA:
            if self.ynormalTimeEvol.get()=="Original":
                if self.xnormalTimeEvol.get()==0:#original data
                    self.timeEvolfig1.plot(timeevolgraphDATA[key][0],timeevolgraphDATA[key][1],label=key)
                    self.timeEvolfig1.set_ylabel(self.ParamChoice.get())
                    datafortxtexport.append(timeevolgraphDATA[key][0])
                    datafortxtexport.append(timeevolgraphDATA[key][1])
                else:#time is starting at zero for all curves
                    x=[item-timeevolgraphDATA[key][0][0] for item in timeevolgraphDATA[key][0]]
                    self.timeEvolfig1.plot(x,timeevolgraphDATA[key][1],label=key)
                    self.timeEvolfig1.set_ylabel(self.ParamChoice.get())
                    datafortxtexport.append(x)
                    datafortxtexport.append(timeevolgraphDATA[key][1])
            elif self.ynormalTimeEvol.get()=="Normalize y, first":
                if self.xnormalTimeEvol.get()==0:#y is normalized
                    y=[m/timeevolgraphDATA[key][1][0] for m in timeevolgraphDATA[key][1]]
                    self.timeEvolfig1.plot(timeevolgraphDATA[key][0],y,label=key)
                    self.timeEvolfig1.set_ylabel(self.ParamChoice.get()+" NormalizedFirst")
                    datafortxtexport.append(timeevolgraphDATA[key][0])
                    datafortxtexport.append(y)
                else:#y is normalized and time is starting at zero 
                    try:
                        x=[item-timeevolgraphDATA[key][0][0] for item in timeevolgraphDATA[key][0]]
                        y=[m/timeevolgraphDATA[key][1][0] for m in timeevolgraphDATA[key][1]]
                        self.timeEvolfig1.plot(x,y,label=key)
                        self.timeEvolfig1.set_ylabel(self.ParamChoice.get()+" NormalizedFirst")
                        datafortxtexport.append(x)
                        datafortxtexport.append(y)
                    except ZeroDivisionError:
                        print("ZeroDivisionError")
            elif self.ynormalTimeEvol.get()=="Normalize y, max":
                if self.xnormalTimeEvol.get()==0:#y is normalized
                    y=[m/max(timeevolgraphDATA[key][1]) for m in timeevolgraphDATA[key][1]]
                    self.timeEvolfig1.plot(timeevolgraphDATA[key][0],y,label=key)
                    self.timeEvolfig1.set_ylabel(self.ParamChoice.get()+" NormalizedMax")
                    datafortxtexport.append(timeevolgraphDATA[key][0])
                    datafortxtexport.append(y)
                else:#y is normalized and time is starting at zero
                    x=[item-timeevolgraphDATA[key][0][0] for item in timeevolgraphDATA[key][0]]
                    y=[m/max(timeevolgraphDATA[key][1]) for m in timeevolgraphDATA[key][1]]
                    self.timeEvolfig1.plot(x,y,label=key)
                    self.timeEvolfig1.set_ylabel(self.ParamChoice.get()+" NormalizedMax")
                    datafortxtexport.append(x)
                    datafortxtexport.append(y)
               
                        
            headings[0]+="Time\t"+self.ParamChoice.get()+"\t"
            headings[1]+="\t"+key+"\t"
        headings[0]=headings[0][:-1]+'\n'
        headings[1]=headings[1][:-1]+'\n'
        self.timeEvolfig1.set_xlabel("Time (minutes)")
        self.timeEvolfig1.legend(ncol=1)
        self.timeEvolfig1.set_title("Peak: ~"+str(self.PeakChoice.get()))
#        self.timeEvolfig.savefig(f[:-4]+'.png', dpi=300, transparent=False) 
        
        #export txt files
        datafortxtexport=map(list, six.moves.zip_longest(*datafortxtexport, fillvalue=' '))
        self.DATAforexport1=headings
        for item in datafortxtexport:
            line=""
            for item1 in item:
                line=line+str(item1)+"\t"
            line=line[:-1]+"\n"
            self.DATAforexport1.append(line)
#        file = open(str(f[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
#        file.writelines("%s" % item for item in self.DATAforexport1)
#        file.close() 
        plt.gcf().canvas.draw()
        
#%%    
    def UpdateGraph0(self,a):
        global takenforplot
        
        takenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
#        print(takenforplot)
        self.updateXRDgraph(0)
        
    def updateXRDgraph(self,a):
        global DATA, RefPattDATA, colorstylelist, samplestakenforplot
        global listofanswer, takenforplot
        global listoflinestyle
        global listofcolorstyle,listoflinewidthstyle

#        print(len(DATA.keys()))
#        print(takenforplot)
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
            if self.showOriginal.get():
                if self.changetoQ.get():
                    minX=min(tth_to_q_list(DATA[samplestakenforplot[0]][2]+DATA[samplestakenforplot[0]][0]))
                    maxX=max(tth_to_q_list(DATA[samplestakenforplot[0]][2]+DATA[samplestakenforplot[0]][0]))
                else:
                    minX=min(DATA[samplestakenforplot[0]][2]+DATA[samplestakenforplot[0]][0])
                    maxX=max(DATA[samplestakenforplot[0]][2]+DATA[samplestakenforplot[0]][0])
            else:
                if self.changetoQ.get():
                    minX=min(tth_to_q_list(DATA[samplestakenforplot[0]][2]))
                    maxX=max(tth_to_q_list(DATA[samplestakenforplot[0]][2]))
                else:
                    minX=min(DATA[samplestakenforplot[0]][2])
                    maxX=max(DATA[samplestakenforplot[0]][2])
            minY=min(DATA[samplestakenforplot[0]][3])
            maxY=max(DATA[samplestakenforplot[0]][3])
            for item in samplestakenforplot:
                if self.changetoQ.get():
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
                if self.CheckLegend.get()==1:
                    if self.ylog.get():
                        self.XRDgraph.semilogy(x,y, label=DATA[item][5][2],linestyle=DATA[item][5][0],color=DATA[item][5][1],linewidth=DATA[item][5][3])
    #                    coloridx+=1
                    else:
                        self.XRDgraph.plot(x,y, label=DATA[item][5][2],linestyle=DATA[item][5][0],color=DATA[item][5][1],linewidth=DATA[item][5][3])
    #                    coloridx+=1
                else:
                    if self.ylog.get():
                        self.XRDgraph.semilogy(x,y,linestyle=DATA[item][5][0],color=DATA[item][5][1],linewidth=DATA[item][5][3])
    #                    coloridx+=1
                    else:
                        self.XRDgraph.plot(x,y,linestyle=DATA[item][5][0],color=DATA[item][5][1],linewidth=DATA[item][5][3])
    #                    coloridx+=1
                
                if self.showOriginal.get():
                    if self.changetoQ.get():
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
                    if self.CheckLegend.get()==1:
                        if self.ylog.get():
                            self.XRDgraph.semilogy(x,y, label=DATA[item][5][2]+'_original',linestyle=DATA[item][5][0],color=DATA[item][5][1],linewidth=DATA[item][5][3])
                            coloridx+=1
                        else:
                            self.XRDgraph.plot(x,y, label=DATA[item][5][2]+'_original',linestyle=DATA[item][5][0],color=DATA[item][5][1],linewidth=DATA[item][5][3])
                            coloridx+=1
                    else:
                        if self.ylog.get():
                            self.XRDgraph.semilogy(x,y, linestyle=DATA[item][5][0],color=DATA[item][5][1],linewidth=DATA[item][5][3])
                            coloridx+=1
                        else:
                            self.XRDgraph.plot(x,y, linestyle=DATA[item][5][0],color=DATA[item][5][1],linewidth=DATA[item][5][3])
                            coloridx+=1
                else:
                    coloridx+=1
                
#            if self.changetoQ.get():
#                # Find min and max two theta, make a list of tth values for the tick labels
#                tth_min = int(math.ceil(q_to_tth(minX))); tth_max = int(math.ceil(q_to_tth(maxX)))
#                # If tth_min is odd, increment to use evens
#                if tth_min % 2 == 1:
#                    tth_min += 1
#                tth_list = list(np.arange(tth_min,tth_max,2))
#                
#                # find the q-values associated with these tth values; these are the tick positions in q
#                q_list = tth_to_q_list(tth_list)
#                
#                # New axis sharing y-axis with ax. Ticks at the top
#                self.XRDgraphtwin.spines["top"].set_position(("axes", 1))
#                # Same x limits at xlim
#                self.XRDgraphtwin.set_xlim(self.XRDgraph.get_xlim())
#                # Place the ticks at the right q-positions
#                self.XRDgraphtwin.set_xticks(q_list)
#                # Label the ticks with the tth values
#                self.XRDgraphtwin.set_xticklabels(tth_list, fontsize=14)
#                self.XRDgraphtwin.tick_params(direction='in', pad=1)
#                # Label the axis
#                self.XRDgraphtwin.set_xlabel('$^o2\\theta$ , Cu K-$\\alpha$', position=(0.08,0.97))
            
            #add text for Peak Names
            if self.CheckPeakNames.get():
                for item in range(len(peaknamesforplot)):
                    if self.changetoQ.get():
                        plt.text(peaknamesforplot[item][3],peaknamesforplot[item][1],peaknamesforplot[item][2],rotation=90,verticalalignment='bottom',horizontalalignment='left',multialignment='center')                  
                    else:
                        plt.text(peaknamesforplot[item][0],peaknamesforplot[item][1],peaknamesforplot[item][2],rotation=90,verticalalignment='bottom',horizontalalignment='left',multialignment='center')

            
        #plot from RefPattDATA
        reftakenforplot = [self.listboxref.get(idx) for idx in self.listboxref.curselection()]
        for item in reftakenforplot:
            if self.changetoQ.get():
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
            
            if self.CheckPeakNames.get():
                for item1 in range(len(RefPattDATA[item][0])):
                    if samplestakenforplot!=[]:
                        if RefPattDATA[item][0][item1]>minX and RefPattDATA[item][0][item1]<maxX:
                            plt.text(RefPattDATA[item][0][item1],RefPattDATA[item][1][item1],RefPattDATA[item][2][item1],rotation=90,verticalalignment='bottom',horizontalalignment='left',multialignment='center')
                    else:
                        plt.text(RefPattDATA[item][0][item1],RefPattDATA[item][1][item1],RefPattDATA[item][2][item1],rotation=90,verticalalignment='bottom',horizontalalignment='left',multialignment='center')

        #plot the fits if show is ticked
        if self.CheckPeakDetec.get():
#            print("show")
            if samplestakenforplot!=[]:
                for item in samplestakenforplot:
                    if DATA[item][4]!=[]:
                        for item2 in DATA[item][4]:
                            self.XRDgraph.plot(item2["xydata"][0],item2["xydata"][1],color='black',linewidth=3)
                            self.XRDgraph.plot(item2["xydata"][0],item2["xydata"][2],color='black',linewidth=3)
                            self.XRDgraph.plot(item2["xydata"][3],item2["xydata"][4],color='black',linewidth=3)
        
        #legends and graph styles
        if self.CheckLegend.get()==1:
            if samplestakenforplot!=[] or  reftakenforplot!=[]:
                self.XRDgraph.legend()
        self.XRDgraph.set_ylabel("Intensity (a.u.)")
        if self.changetoQ.get():
            self.XRDgraph.set_xlabel('q (A$^{-1}$)')
        else:
            self.XRDgraph.set_xlabel("2\u0398 (degree)")
        if samplestakenforplot!=[]:
            self.XRDgraph.axis([minX,maxX,minY,1.1*maxY])  
            if self.ylabel.get():
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
        plt.gcf().canvas.draw()
        self.CreateTable()


    class PopulateListofPeakNames(tk.Frame):
        def __init__(self, root):
    
            tk.Frame.__init__(self, root)
            self.canvas0 = tk.Canvas(root, borderwidth=0, background="#ffffff")
            self.frame = tk.Frame(self.canvas0, background="#ffffff")
            self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas0.yview)
            self.canvas0.configure(yscrollcommand=self.vsb.set)
    
            self.vsb.pack(side="right", fill="y")
            self.canvas0.pack(side="left", fill="both", expand=True)
            self.canvas0.create_window((4,4), window=self.frame, anchor="nw", 
                                      tags="self.frame")
    
            self.frame.bind("<Configure>", self.onFrameConfigure)
    
            self.populate()
    
        def populate(self):
            global DATA, listofanswer0, samplestakenforplot
                     
            rowpos=1
            if samplestakenforplot!=[]:
                for item in samplestakenforplot:
                    for item1 in range(len(DATA[item][4])):
                        label=tk.Label(self.frame,text=item,fg='black',background='white')
                        label.grid(row=rowpos,column=0, columnspan=1)
                        label=tk.Label(self.frame,text="%.2f"%DATA[item][4][item1]["Position"],fg='black',background='white')
                        label.grid(row=rowpos,column=1, columnspan=1)
                        textinit = tk.StringVar()
                        listofanswer0[str(DATA[item][4][item1]["Position"])]=Entry(self.frame,textvariable=textinit)
                        listofanswer0[str(DATA[item][4][item1]["Position"])].grid(row=rowpos,column=2, columnspan=2)
                        textinit.set(DATA[item][4][item1]["PeakName"])
        
                        rowpos=rowpos+1
            
        def onFrameConfigure(self, event):
            '''Reset the scroll region to encompass the inner frame'''
            self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))

        
    def ChangePeakNames(self):
        global DATA
        
        self.window = tk.Toplevel()
        self.window.wm_title("Change Peak Names")
        center(self.window)
        self.window.geometry("400x300")
        
        Button(self.window, text="Update",
                            command = self.UpdatePeakNames).pack()
        
        self.PopulateListofPeakNames(self.window).pack(side="top", fill="both", expand=True)
    
    def UpdatePeakNames(self):
        global DATA, listofanswer0, samplestakenforplot, peaknamesforplot
        
        peaknamesforplot=[]
       
        for item in samplestakenforplot:
            for item1 in range(len(DATA[item][4])):
                DATA[item][4][item1]["PeakName"]=listofanswer0[str(DATA[item][4][item1]["Position"])].get()
                peaknamesforplot.append([DATA[item][4][item1]["Position"],DATA[item][4][item1]["Intensity"],DATA[item][4][item1]["PeakName"],tth_to_q(DATA[item][4][item1]["Position"])])
        
        self.window.destroy()
        self.updateXRDgraph(0)

        
#%%    
    def backgroundremoval(self):
        global DATA

        if self.listboxsamples.curselection()!=():
            samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
            if samplestakenforplot!=[]:
                for item in samplestakenforplot:
                    y = DATA[item][3]
                    y=np.array(y)
                    base = peakutils.baseline(y, self.backgroundorder.get())
                    DATA[item][3]=list(y-base)
            
            self.updateXRDgraph(0)

    def SavitzkyGolayFiltering(self):
        global DATA
        if self.SGwinsize.get()>self.SGorder.get() and self.SGwinsize.get()%2==1:
            if self.listboxsamples.curselection()!=():
                samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
                if samplestakenforplot!=[]:
                    for item in samplestakenforplot:
                        y = DATA[item][3]
                        y=np.array(y)
                        DATA[item][3] = savitzky_golay(y, window_size=self.SGwinsize.get(), order=self.SGorder.get())
                
                self.updateXRDgraph(0)
        else:
            messagebox.showinfo("Information","the SG window-size must be larger than the SG order, positive and odd.")
            
            
    def backgroundremovalImport(self):
        global DATA
        
        if self.listboxsamples.curselection()!=():
            filename =filedialog.askopenfilename(title="Please select the XRD file for background")
            
            filetoread = open(filename,"r", encoding='ISO-8859-1')
            filerawdata = list(filetoread.readlines())
#            samplename=os.path.splitext(os.path.basename(filename))[0]
    #            print(samplename)
            xbkg=[]
            ybkg=[]
            for j in range(len(filerawdata)):
                if ',' in filerawdata[j]:
                    xbkg.append(float(filerawdata[j].split(',')[0]))
                    ybkg.append(float(filerawdata[j].split(',')[1]))  
            f = interp1d(xbkg, ybkg, kind='cubic')
            samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
            if samplestakenforplot!=[]:
                for item in samplestakenforplot:
                    y = DATA[item][3]
                    x = DATA[item][2]                   
                    DATA[item][3]=[y[item1]-f(x[item1]) for item1 in range(len(x))]
            
            self.updateXRDgraph(0)
    
    def shiftX(self):
        global DATA
        
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
                x = DATA[item][2]
                DATA[item][2] = [item1+self.shift.get() for item1 in x]
    
        self.updateXRDgraph(0)
        
    def shiftY(self):
        global DATA
#        print("here")
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
#                print(self.shiftYval.get())
                y = DATA[item][3]
                DATA[item][3] = [item1+self.shiftYval.get() for item1 in y]
    
        self.updateXRDgraph(0)
        
    def shifttoRef(self):
        global DATA
#        still to be implemented
#        automatic detection of peaks and comparison to the selected RefPattern
#        then shifts the data to match the ref peak
        
        
        self.updateXRDgraph(0)    
    
    def scaleYtoRef(self):
        global DATA
        
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
                y = DATA[item][3]
                maxy=max(y)
                miny=min(y)
                DATA[item][3]=[((item1-miny)/(maxy-miny))*self.rescale.get() for item1 in y]
        
        self.updateXRDgraph(0)
        
    def backtoOriginal(self):
        global DATA
        
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
                DATA[item][2]=DATA[item][0]
                DATA[item][3]=DATA[item][1]
        
        self.updateXRDgraph(0)

#%%        
   
    def PeakDetection(self):
        global DATA,peaknamesforplot
        peaknamesforplot=[]  
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
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
                if self.AutoPeakDetecAdjust.get():
                    threshold=0.01
                    MinDist=50
                    while(1):
                        indexes = peakutils.indexes(y, thres=threshold, min_dist=MinDist)
                        if len(indexes)<15:
                            self.thresholdPeakDet.set(threshold)
                            self.MinDistPeakDet.set(MinDist)
                            break
                        else:
                            threshold+=0.01
                else:
                    indexes=peakutils.indexes(y, thres=self.thresholdPeakDet.get(), min_dist=self.MinDistPeakDet.get())
#                print("")
#                print(len(indexes))
#                print(len(y))
                for item1 in range(len(indexes)):
                    tempdat={}
                    nbofpoints=self.nbofpoints.get()#on each side of max position
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
                            except ValueError:
                                print('valueerror: ', len(y0))
                            #baseline height
                            bhleft=np.mean(y0[:self.basepoints.get()])
                            bhright=np.mean(y0[-self.basepoints.get():])
#                                baselineheightatmaxpeak=(bhleft+bhright)/2
                            baselineheightatmaxpeak=base[nbofpoints]
#                            print(baselineheightatmaxpeak)
#                            print("")
#                            print(abs(bhleft-bhright))
                            if abs(bhleft-bhright)<self.diffleftright.get():#arbitrary choice of criteria...
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
                                tempdat["CrystSize"]=self.ScherrerCst.get()*0.1*lambdaXRD/(radians(tempdat["IntBreadth"])*cos(radians(tempdat["Position"]/2)))
                                tempdat["xydata"]=[x0,y0, base,[xleftfwhm,xrightfwhm],[yfwhm,yfwhm]]
                                
                                appendcheck=1
                                break
                            else:
                                if nbofpoints>=2*self.basepoints.get():
                                    nbofpoints-=2
                                else:
                                    print("indexerror unsolvable")
                                    print(x[indexes[item1]])
                                    break
                        except IndexError:
                            if nbofpoints>=2*self.basepoints.get():
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
        
#%%
    def importRefDATA(self):#not yet updated to nrel
        global DATA, RefPattDATA, refsamplenameslist

        #ask for the files
        file_path =filedialog.askopenfilenames(title="Please select the reference XRD pattern")
        
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
        self.frame3231.destroy()
        self.frame3231=Frame(self.frame323,borderwidth=0,  bg="white")
        self.frame3231.pack(fill=tk.BOTH,expand=1)
        refsamplenames = StringVar()
        self.listboxref=Listbox(self.frame3231,listvariable=refsamplenames, selectmode=tk.MULTIPLE,width=15, height=3, exportselection=0)
        self.listboxref.bind('<<ListboxSelect>>', self.updateXRDgraph)
        self.listboxref.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(self.frame3231, orient="vertical")
        scrollbar.config(command=self.listboxref.yview)
        scrollbar.pack(side="right", fill="y")
        self.listboxref.config(yscrollcommand=scrollbar.set)
        
        for item in refsamplenameslist:
            self.listboxref.insert(tk.END,item)
            
        #should also export this text file in the crystalloData folder, so it's loaded the next time
        #and ask user to share it with me!
        
    
    def importDATA(self):
        global DATA, Patternsamplenameslist, istheretimedata,colormapname
        
        #ask for the files
        file_path =filedialog.askopenfilenames(title="Please select the XRD files")
        
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
        self.frame322.destroy()
        self.frame3221.destroy()
        self.frame322=Frame(self.frame3220,borderwidth=0,  bg="white")
        self.frame322.pack(fill=tk.BOTH,expand=1)
        self.frame3221=Frame(self.frame322,borderwidth=0,  bg="white")
        self.frame3221.pack(fill=tk.BOTH,expand=1)
        importedsamplenames = StringVar()
        self.listboxsamples=Listbox(self.frame3221,listvariable=importedsamplenames, selectmode=tk.EXTENDED,width=15, height=3, exportselection=0)
        self.listboxsamples.bind('<<ListboxSelect>>', self.UpdateGraph0)
        self.listboxsamples.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(self.frame3221, orient="vertical")
        scrollbar.config(command=self.listboxsamples.yview)
        scrollbar.pack(side="right", fill="y")
        xscrollbar = tk.Scrollbar(self.frame322, orient="horizontal")
        xscrollbar.config(command=self.listboxsamples.xview)
        xscrollbar.pack(side="bottom", fill="x")
        self.listboxsamples.config(yscrollcommand=scrollbar.set)
        self.listboxsamples.config(xscrollcommand=xscrollbar.set)
        
        for item in Patternsamplenameslist:
            self.listboxsamples.insert(tk.END,item)
        
#%%

    def Export(self):
        global DATA 
        
        
        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
        self.fig1.savefig(f, dpi=300) 

        
        testdata=['name\tPeakName\tPosition\tPositionQ\tIntensity\tFWHM\tPeakArea\tIntegralBreadth\n']
        
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
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
        
        
        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
#        self.fig1.savefig(f, dpi=300) 
        
        testdata=['name\tPosition\tFWHM\t4Sin(theta)/lambda\tBCos(theta)/lambda\n']
        
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
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
    def CreateTable(self):
        global DATA
        global testdata
        testdata=[]
        #self.parent.grid_rowconfigure(0,weight=1)
        #self.parent.grid_columnconfigure(0,weight=1)
#        self.parent.config(background="white")
        
        self.frame41.destroy()
        self.frame41=Frame(self.frame4,borderwidth=0,  bg="white")
        self.frame41.pack(side="right",fill=tk.BOTH,expand=1)
                    
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for key in samplestakenforplot:
                for item in DATA[key][4]:
                    testdata.append([key,item["PeakName"],"%.2f"%item["Position"],"%.2f"%item["PositionQ"],"%.2f"%item["Intensity"],"%.2f"%item["FWHM"],"%.2f"%item["PeakArea"],"%.2f"%item["IntBreadth"],"%.2f"%item["CrystSize"]])
            
        self.tableheaders=('name','PeakName','Position (2\u0398)','Position q','Intensity (a.u.)','FWHM (2\u0398)','PeakArea','IntBreadth (2\u0398)', 'CrystalliteSize KL/dcos(thet)(nm)')
                    
        # Set the treeview
        self.tree = Treeview(self.frame41, columns=self.tableheaders, show="headings")
        
        for col in self.tableheaders:
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sortby(self.tree, c, 0))
            self.tree.column(col, width=int(round(1.1*tkFont.Font().measure(col.title()))), anchor='n')   
        
        scrollbar = tk.Scrollbar(self.frame41, orient="vertical")
        scrollbar.config(command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=scrollbar.set)
        scrollbar = tk.Scrollbar(self.frame41, orient="horizontal")
        scrollbar.config(command=self.tree.xview)
        scrollbar.pack(side="bottom", fill="x")
        self.tree.config(xscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill=tk.BOTH, expand=1)
        
        self.treeview = self.tree
        
        self.insert_data(testdata)    
    
    def insert_data(self, testdata):
        for item in testdata:
            self.treeview.insert('', 'end', values=item)

    def sortby(self, tree, col, descending):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]), reverse=descending)
        except ValueError:
            data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col,text=col.capitalize(), command=lambda _col_=col: self.sortby(tree, _col_, int(not descending)))
#%%############# 
        
    def ChangeLegendXRDgraph(self):
        global DATA, RefPattDATA, colorstylelist, samplestakenforplot


        self.window = tk.Toplevel()
        self.window.wm_title("Change Legends")
        center(self.window)
        self.window.geometry("550x300")
        
        Button(self.window, text="Update",
                            command = self.UpdateXRDLegMod).pack()
        
        Button(self.window, text="Reorder",
                            command = self.reorder).pack()

        self.PopulateListofSampleStylingXRD(self.window).pack(side="top", fill="both", expand=True)
    
    def UpdateXRDLegMod(self):
        global listofanswer, takenforplot
        global listoflinestyle,DATA
        global listofcolorstyle,listoflinewidthstyle

        leglist=[]
        for e in listofanswer:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        for item in range(len(takenforplot)):
            DATA[takenforplot[item]][5][2]=leglist[item]
        
        leglist=[]
        for e in listoflinestyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        for item in range(len(takenforplot)):
            DATA[takenforplot[item]][5][0]=leglist[item]        
        leglist=[]
        for e in listofcolorstyle:
            if type(e)==tuple:
                leglist.append(mpl.colors.to_hex(e, keep_alpha=False))
            elif type(e)==str:
                leglist.append(e) 
            elif type(e)!=str:
                leglist.append(e.get())
                
        for item in range(len(takenforplot)):
            DATA[takenforplot[item]][5][1]=leglist[item]  
        leglist=[]
        for e in listoflinewidthstyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e) 
        for item in range(len(takenforplot)):
            DATA[takenforplot[item]][5][3]=int(leglist[item]) 
                
#        print('UpdateSpectLegMod')
#        print(takenforplot)
        self.updateXRDgraph(0)
        self.window.destroy()
        self.ChangeLegendXRDgraph()

    class PopulateListofSampleStylingXRD(tk.Frame):
        def __init__(self, root):
    
            tk.Frame.__init__(self, root)
            self.canvas0 = tk.Canvas(root, borderwidth=0, background="#ffffff")
            self.frame = tk.Frame(self.canvas0, background="#ffffff")
            self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas0.yview)
            self.canvas0.configure(yscrollcommand=self.vsb.set)
    
            self.vsb.pack(side="right", fill="y")
            self.canvas0.pack(side="left", fill="both", expand=True)
            self.canvas0.create_window((4,4), window=self.frame, anchor="nw", 
                                      tags="self.frame")
    
            self.frame.bind("<Configure>", self.onFrameConfigure)
    
            self.populate()
    
        def populate(self):
            global takenforplot,DATA
            global colorstylelist
            global listofanswer
            global listoflinestyle
            global listofcolorstyle, listoflinewidthstyle
            
            
            DATAx=DATA
            listofanswer=[]
#            sampletotake=[]
#            if takenforplot!=[]:
#                for item in takenforplot:
#                    sampletotake.append(DATAx[item][0])
                    
            listoflinestyle=[]
            listofcolorstyle=[]
            listoflinewidthstyle=[]
            
            
            for item in takenforplot:
                listoflinestyle.append(DATAx[item][5][0])
                listofcolorstyle.append(DATAx[item][5][1])
                listofanswer.append(DATAx[item][5][2])
                listoflinewidthstyle.append(str(DATAx[item][5][3]))
#            print(takenforplot)
#            print(listofanswer)
            rowpos=1
            for item1 in range(len(takenforplot)): 
                label=tk.Label(self.frame,text=takenforplot[item1],fg='black',background='white')
                label.grid(row=rowpos,column=0, columnspan=1)
                textinit = tk.StringVar()
                #self.listofanswer.append(Entry(self.window,textvariable=textinit))
                listofanswer[item1]=Entry(self.frame,textvariable=textinit)
                listofanswer[item1].grid(row=rowpos,column=1, columnspan=2)
                textinit.set(DATAx[takenforplot[item1]][5][2])
    
                linestylelist = ["-","--","-.",":"]
                listoflinestyle[item1]=tk.StringVar()
                listoflinestyle[item1].set(DATAx[takenforplot[item1]][5][0]) # default choice
                OptionMenu(self.frame, listoflinestyle[item1], *linestylelist, command=()).grid(row=rowpos, column=4, columnspan=2)
                 
                """
                listofcolorstyle[item1]=tk.StringVar()
                listofcolorstyle[item1].set(DATAx[item1][10]) # default choice
                OptionMenu(self.frame, listofcolorstyle[item1], *colorstylelist, command=()).grid(row=rowpos, column=6, columnspan=2)
                """
#                print(listofcolorstyle[item1])
#                print(tuple(listofcolorstyle[item1]))
                self.positioncolor=item1
#                rgb=list(listofcolorstyle[item1])[0:3]
#                print(listofcolorstyle[item1])
#                print(rgb)
                
#                print('#{:02x}{:02x}{:02x}'.format(*rgb)) 
#                colstyle=Button(self.frame, text='Select Color', foreground=tuple(listofcolorstyle[item1]), command=partial(self.getColor,item1))
                if type(listofcolorstyle[item1])==tuple:
                    colstyle=Button(self.frame, text='Select Color', foreground=mpl.colors.to_hex(list(listofcolorstyle[item1]), keep_alpha=False), command=partial(self.getColor,item1))
                    colstyle.grid(row=rowpos, column=6, columnspan=2)
                else:
                    colstyle=Button(self.frame, text='Select Color', foreground=listofcolorstyle[item1], command=partial(self.getColor,item1))
                    colstyle.grid(row=rowpos, column=6, columnspan=2)
                
                linewidth = tk.StringVar()
                listoflinewidthstyle[item1]=Entry(self.frame,textvariable=linewidth)
                listoflinewidthstyle[item1].grid(row=rowpos,column=8, columnspan=1)
                linewidth.set(str(DATAx[takenforplot[item1]][5][3]))
                
                rowpos=rowpos+1
                        
#                    else:
#                        listofanswer[item1]=str(DATAx[item1][5])
#                        listoflinestyle.append(str(DATAx[item1][9]))
#                        listofcolorstyle.append(str(DATAx[item1][10]))
#                        listoflinewidthstyle.append(str(DATAx[item1][29]))
            #print(listofanswer)
            
        def getColor(self,rowitem):
            global listofcolorstyle
            color = askcolor(color="red", parent=self.frame, title="Color Chooser", alpha=False)
            listofcolorstyle[rowitem]=color[1]
            
            
        def onFrameConfigure(self, event):
            '''Reset the scroll region to encompass the inner frame'''
            self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))
    
    class Drag_and_Drop_Listbox(tk.Listbox):
        #A tk listbox with drag'n'drop reordering of entries.
        def __init__(self, master, **kw):
            #kw['selectmode'] = tk.MULTIPLE
            kw['selectmode'] = tk.SINGLE
            kw['activestyle'] = 'none'
            tk.Listbox.__init__(self, master, kw)
            self.bind('<Button-1>', self.getState, add='+')
            self.bind('<Button-1>', self.setCurrent, add='+')
            self.bind('<B1-Motion>', self.shiftSelection)
            self.curIndex = None
            self.curState = None
        def setCurrent(self, event):
            ''' gets the current index of the clicked item in the listbox '''
            self.curIndex = self.nearest(event.y)
        def getState(self, event):
            ''' checks if the clicked item in listbox is selected '''
            #i = self.nearest(event.y)
            #self.curState = self.selection_includes(i)
            self.curState = 1
        def shiftSelection(self, event):
            ''' shifts item up or down in listbox '''
            i = self.nearest(event.y)
            if self.curState == 1:
              self.selection_set(self.curIndex)
            else:
              self.selection_clear(self.curIndex)
            if i < self.curIndex:
              # Moves up
              x = self.get(i)
              selected = self.selection_includes(i)
              self.delete(i)
              self.insert(i+1, x)
              if selected:
                self.selection_set(i+1)
              self.curIndex = i
            elif i > self.curIndex:
              # Moves down
              x = self.get(i)
              selected = self.selection_includes(i)
              self.delete(i)
              self.insert(i-1, x)
              if selected:
                self.selection_set(i-1)
              self.curIndex = i
              

    def reorder(self): 
        global takenforplot
        
#        DATAx=self.DATA
#        sampletotake=[]
#        if takenforplot!=[]:
#            for item in takenforplot:
#                sampletotake.append(DATAx[item][0])
                    
        self.reorderwindow = tk.Tk()
        center(self.reorderwindow)
        self.listbox = self.Drag_and_Drop_Listbox(self.reorderwindow)
        for name in takenforplot:
          self.listbox.insert(tk.END, name)
          self.listbox.selection_set(0)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.listbox, orient="vertical")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        printbut = tk.Button(self.reorderwindow, text="reorder",
                                    command = self.printlist)
        printbut.pack()
        self.reorderwindow.mainloop()    
            
    def printlist(self):
        global takenforplot
        global listofanswer
        global listoflinestyle
        global listofcolorstyle,listoflinewidthstyle
        
        #need to reorder at same time all other lists
        newtakenforplot=[]
        newlistofanswer=[]
        newlistoflinestyle=[]
        newlistofcolorstyle=[]
        newlistoflinewidthstyle=[]
        newlist=list(self.listbox.get(0,tk.END))
        for item in newlist:
            for i in range(len(takenforplot)):
                if takenforplot[i]==item:
                    newtakenforplot.append(takenforplot[i])
                    newlistofanswer.append(listofanswer[i])
                    newlistoflinestyle.append(listoflinestyle[i])
                    newlistofcolorstyle.append(listofcolorstyle[i])
                    newlistoflinewidthstyle.append(listoflinewidthstyle[i])
        takenforplot=newtakenforplot
        listofanswer=newlistofanswer
        listoflinestyle=newlistoflinestyle
        listofcolorstyle=newlistofcolorstyle
        listoflinewidthstyle=newlistoflinewidthstyle
        
        self.UpdateXRDLegMod()
        self.reorderwindow.destroy()

            
#%%#############         
###############################################################################        
if __name__ == '__main__':
    
    app = XRDApp()
    app.mainloop()


