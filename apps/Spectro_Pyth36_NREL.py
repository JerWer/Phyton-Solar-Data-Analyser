#! python3

import os
import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg

import tkinter as tk
from tkinter import Listbox, Entry, Button,messagebox, Checkbutton, IntVar, Toplevel, OptionMenu, Frame, StringVar
from tkinter import filedialog
#import ttk
from tkinter import *
#import FileDialog
from pathlib import Path
import numpy as np
import copy
import csv
from timeit import default_timer as timer
from operator import truediv as div
from math import log, pow 
from XRD_NREL import savitzky_golay
from tkcolorpicker import askcolor 
from functools import partial


"""



"""

LARGE_FONT= ("Verdana", 16)
SMALL_FONT= ("Verdana", 10)

echarge = 1.60218e-19
planck = 6.62607e-34
lightspeed = 299792458
DATAspectro={}
SpectlegendMod=[]
titSpect=0
Patternsamplenameslist=[]
takenforplot=[]
listofanswer=[]
listoflinestyle=[]
listofcolorstyle=[]
listoflinewidthstyle=[]
colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']


def center(win):
    """
    centers a tkinter window
    :param win: the root or Toplevel window to center
    """
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
    
###############################################################################             

class SpectroApp(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "SpectroApp")
        Toplevel.config(self,background="white")
        self.wm_geometry("700x500")
        center(self)
        self.initUI()
        
    def initUI(self):
        global Patternsamplenameslist
        
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        label = tk.Label(self, text="UV-vis spectrophotometric DATA Analyzer", font=LARGE_FONT,  bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)
        
        frame1=Frame(self,borderwidth=0,  bg="white")
        frame1.pack(fill=tk.BOTH,expand=1)
        
        self.fig = plt.figure(figsize=(3, 2))
        canvas = FigureCanvasTkAgg(self.fig, frame1)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.Spectrograph=self.fig.add_subplot(111)
        self.toolbar = NavigationToolbar2TkAgg(canvas, frame1)
        self.toolbar.update()
        canvas._tkcanvas.pack(fill = BOTH, expand = 1) 
        
        frame02=Frame(self,borderwidth=0,  bg="white")
        frame02.pack(fill=tk.X,side=tk.LEFT,expand=0)
        
        frame2=Frame(frame02,borderwidth=0,  bg="white")
        frame2.pack(fill=tk.X,expand=0)
        
        self.helpbutton = Button(frame2, text="Help",
                            command = self.Help)
        self.helpbutton.pack(side=tk.LEFT,expand=1)
        self.importdat = Button(frame2, text="Import DATA",
                            command = self.onOpen)
        self.importdat.pack(side=tk.LEFT,expand=1)
#        self.menubutton = tk.Menubutton(frame2, text="Choose wisely", 
#                                   indicatoron=True, borderwidth=1, relief="raised")
#        self.menu = tk.Menu(self.menubutton, tearoff=False)
#        self.menubutton.configure(menu=self.menu)
#        self.menubutton.pack(side=tk.LEFT,expand=1)
        self.update = Button(frame2, text="Update Graph",
                            command = lambda: self.UpdateGraph(0), width=15)
        self.update.pack(side=tk.LEFT,expand=1)
        
        
        self.exportgraph = Button(frame2, text="Export this graph",
                            command = self.ExportGraph)
        self.exportgraph.pack(side=tk.LEFT,expand=1)
        
        self.SGwinsize = tk.IntVar()
        Entry(frame2, textvariable=self.SGwinsize,width=1).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.SGwinsize.set(31)
        self.SGorder = tk.IntVar()
        Entry(frame2, textvariable=self.SGorder,width=1).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.SGorder.set(5)
        self.CheckSG = Button(frame2, text="SavitzkyGolayFilter",command = self.SavitzkyGolayFiltering).pack(side=tk.LEFT,expand=1)
        self.back = Button(frame2, text="Back",command = self.backtoOriginal).pack(side=tk.LEFT,expand=1)

        
        frame3=Frame(frame02,borderwidth=0,  bg="white")
        frame3.pack(fill=tk.X,expand=0)
        
        Button(frame3, text="AbsCoeff&Tauc", command = self.AbsCoeffAndTauc).pack(side=tk.LEFT,expand=1)
        self.changespectlegend = Button(frame3, text="change legend",
                            command = self.ChangeLegendSpectgraph)
        self.changespectlegend.pack(side=tk.LEFT,expand=1)
        self.exportdat = Button(frame3, text="Export All DATA",
                            command = self.sortandexportspectro)
        self.exportdat.pack(side=tk.LEFT,expand=1)
        
        frame4=Frame(frame3,borderwidth=0,  bg="white")
        frame4.pack(side=tk.LEFT,fill=tk.X,expand=0)

        frame41=Frame(frame4,borderwidth=0,  bg="white")
        frame41.pack(side=tk.LEFT, expand=0)        
        frame411=Frame(frame41,borderwidth=0,  bg="white")
        frame411.pack(side=tk.TOP,expand=0)
        frame412=Frame(frame41,borderwidth=0,  bg="white")
        frame412.pack(side=tk.BOTTOM,expand=0)

        self.minx = tk.IntVar()
        Entry(frame411, textvariable=self.minx,width=5).pack(side=tk.LEFT,expand=1)
        tk.Label(frame412, text="Min X", bg="white").pack(side=tk.LEFT,expand=1)
        self.minx.set(300)
        self.maxx = tk.IntVar()
        Entry(frame411, textvariable=self.maxx,width=5).pack(side=tk.LEFT,expand=1)
        tk.Label(frame412, text="Max X", bg="white").pack(side=tk.LEFT,expand=1)
        self.maxx.set(1200)
        self.miny = tk.IntVar()
        Entry(frame411, textvariable=self.miny,width=5).pack(side=tk.LEFT,expand=1)
        tk.Label(frame412, text="Min Y", bg="white").pack(side=tk.LEFT,expand=1)
        self.miny.set(0)
        self.maxy = tk.IntVar()
        Entry(frame411, textvariable=self.maxy,width=5).pack(side=tk.LEFT,expand=1)
        tk.Label(frame412, text="Max Y", bg="white").pack(side=tk.LEFT,expand=1)
        self.maxy.set(100)
        
        frame42=Frame(frame4,borderwidth=0,  bg="white")
        frame42.pack(side=tk.RIGHT, expand=0)
        frame421=Frame(frame42,borderwidth=0,  bg="white")
        frame421.pack(expand=0)
        frame422=Frame(frame42,borderwidth=0,  bg="white")
        frame422.pack(expand=0)
        frame423=Frame(frame42,borderwidth=0,  bg="white")
        frame423.pack(expand=0)
        
        
        self.CheckLegend = IntVar()
        legend=Checkbutton(frame423,text='Legend',variable=self.CheckLegend, 
                           onvalue=1,offvalue=0,height=1, width=10,command=lambda: self.UpdateGraph(0), bg="white")
        legend.pack(side=tk.LEFT,expand=1)
        

        self.pos1 = IntVar()
        pos=Checkbutton(frame421,text=None,variable=self.pos1, 
                           onvalue=2,offvalue=0,height=1, width=1,command=lambda: self.UpdateGraph(0), bg="white")
        pos.pack(side=tk.LEFT,expand=1)
        self.pos2 = IntVar()
        pos=Checkbutton(frame421,text=None,variable=self.pos1, 
                           onvalue=1,offvalue=0,height=1, width=1,command=lambda: self.UpdateGraph(0), bg="white")
        pos.pack(side=tk.LEFT,expand=1)
        self.pos3 = IntVar()
        pos=Checkbutton(frame422,text=None,variable=self.pos1, 
                           onvalue=3,offvalue=0,height=1, width=1,command=lambda: self.UpdateGraph(0), bg="white")
        pos.pack(side=tk.LEFT,expand=1)
        self.pos4 = IntVar()
        pos=Checkbutton(frame422,text=None,variable=self.pos1, 
                           onvalue=4,offvalue=0,height=1, width=1,command=lambda: self.UpdateGraph(0), bg="white")
        pos.pack(side=tk.LEFT,expand=1)
        
        self.frame5=Frame(self,borderwidth=0,  bg="white")
        self.frame5.pack(fill=tk.BOTH,side=tk.RIGHT,expand=1)
        self.frame51=Frame(self.frame5,borderwidth=0,  bg="white")
        self.frame51.pack(fill=tk.BOTH,expand=1)
        importedsamplenames = StringVar()
        self.listboxsamples=Listbox(self.frame51,listvariable=importedsamplenames, selectmode=tk.MULTIPLE,width=15, height=3, exportselection=0)
        self.listboxsamples.bind('<<ListboxSelect>>', self.UpdateGraph0)
        self.listboxsamples.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(self.frame51, orient="vertical")
        scrollbar.config(command=self.listboxsamples.yview)
        scrollbar.pack(side="right", fill="y")
        self.listboxsamples.config(yscrollcommand=scrollbar.set)
        
        for item in Patternsamplenameslist:
            self.listboxsamples.insert(tk.END,item)
        
    def on_closing(self):
        global Patternsamplenameslist
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            
            Patternsamplenameslist=[]
            plt.close()
            self.destroy()
            self.master.deiconify()
            
    def Help(self):
              
        self.window = tk.Toplevel()
        self.window.wm_title("HelpDesk")
        self.window.geometry("780x550")
        self.window.config(background="white")
        center(self.window)

        label = tk.Label(self.window, text="Help!", font=("Verdana", 30), bg="white")
        label.pack()
        label = tk.Label(self.window, text="   ", font=("Verdana", 30), bg="white")
        label.pack()
        label = tk.Label(self.window, text="How do I name my files?", font=("Verdana", 20), bg="white")
        label.pack()
#        label = tk.Label(self.window, text="With the UV-vis spectrophotometer, you can measure:\nTotal reflectance: _TR\nTotal transmittance: _TT\nDiffuse reflectance: _DR\nDiffuse transmittance: _DT", font=("Verdana", 12), bg="white")
#        label.pack() 
#        label = tk.Label(self.window, text="By ending your measurement names with _TR, _TT, _DR or _DT, the program will be able to \nrecognise them, group them, and calculate the total absorptance.", font=("Verdana", 12), bg="white")
#        label.pack()
#        label = tk.Label(self.window, text="   ", font=("Verdana", 30), bg="white")
#        label.pack()
        label = tk.Label(self.window, text="Which files can I use?", font=("Verdana", 20), bg="white")
        label.pack()
#        label = tk.Label(self.window, text="ASC File: .Sample.Raw.asc\nExcel: .Sample.Raw.csv", font=("Verdana", 12), bg="white")
#        label.pack()
#        label = tk.Label(self.window, text="   ", font=("Verdana", 12), bg="white")
#        label.pack()
#        label = tk.Label(self.window, text="Example:\nNameOfSample_TR, which then become the file: NameOfSample_TR.Sample.Raw.asc", font=("Verdana", 12), bg="white")
#        label.pack()
            
        
    def onOpen(self):
        
        self.GetSpectroDATA()
#        self.names = ()
#        self.names=self.SampleNames(self.DATA)
#        self.menu = tk.Menu(self.menubutton, tearoff=False)
#        self.menubutton.configure(menu=self.menu)
#        self.choices = {}
#        for choice in range(len(self.names)):
#            self.choices[choice] = tk.IntVar(value=0)
#            self.menu.add_checkbutton(label=self.names[choice], variable=self.choices[choice], 
#                                 onvalue=1, offvalue=0, command = self.UpdateGraph)
        end = timer()
        print("Ready! %s seconds" %(end-self.start))

    def GetSpectroDATA(self):
        global Patternsamplenameslist
        
        file_path = filedialog.askopenfilenames()

        print("Importing...")
        self.start = timer()
        
        directory = str(Path(file_path[0]).parent.parent)+'\\resultFilesSpectro'
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.chdir(directory)
        else :
            os.chdir(directory)
            
        if os.path.splitext(file_path[0])[1] ==".csv":
            DATA = {}
            for item in range(len(file_path)):
                with open(file_path[item], encoding='ISO-8859-1') as csvfile:
                    readCSV = list(csv.reader(csvfile, delimiter=','))
                    
                    samplenames=readCSV[0]
                    dataWaveInt=readCSV[2:]
                    print(len(dataWaveInt))
                    for item in range(len(samplenames)):
                        if samplenames[item]!='':
                            dataWave = []
                            dataInt = []
                            discard=1
#                            print(samplenames[item])
                            if '_TT' in samplenames[item]:
                                curvetype="TT"
                                samplenameshort = samplenames[item][:-3]
                            elif '_TR' in samplenames[item]:
                                curvetype="TR"
                                samplenameshort = samplenames[item][:-3]
                            elif "Baseline" in samplenames[item]:
                                discard=0
                            if discard:    
#                                print(samplenames[item])
                                for item1 in range(len(dataWaveInt)):
#                                    print(dataWaveInt[item1])
#                                    if dataWaveInt[item1][0]=='':
                                    try:
                                        if dataWaveInt[item1]==[]:
                                            break
                                    except:
                                        pass
                                    try:
                                        if dataWaveInt[item1][0]=='':
                                            break
                                    except:
                                        pass
#                                    print(dataWaveInt[item1][item])
                                    dataWave.append(dataWaveInt[item1][item])
                                    dataInt.append(dataWaveInt[item1][item+1])
                                dataWave=list(map(float,dataWave))
                                dataInt=list(map(float,dataInt))
                                #[0 samplenameshort, 1 curvetype, 2 dataWave, 3 dataInt, 4 dataIntorig, 5 longnameorig, 6 longnamemod, 7 linestyle, 8 linecolor, 9 linewidth]
                                DATA[samplenames[item]] = [samplenameshort, curvetype, dataWave, dataInt,dataInt,samplenames[item],samplenames[item],'-',colorstylelist[len(DATA.keys())],int(2)]
                                Patternsamplenameslist.append(samplenames[item])
#                                print(samplenameshort)
        elif os.path.splitext(file_path[0])[1] ==".txt": 
             DATA = {}
             for item in range(len(file_path)):
                file = open(file_path[item], encoding='ISO-8859-1')
                filedat = file.readlines()
                
                samplename=filedat[0].split(' ')[0]
                wave=[]
                absorb=[]
                for item1 in range(2,len(filedat)):
                    wave.append(float(filedat[item1].split('\t')[0]))
                    absorb.append(float(filedat[item1].split('\t')[1]))
                
                DATA[samplename+'_A']=[samplename,'A',wave,absorb,absorb,samplename+'_A',samplename+'_A','-',colorstylelist[len(DATA.keys())],int(2)]
                Patternsamplenameslist.append(samplename+'_A')
                 
                            
#                    dataWave=list(map(float,dataWave[1:]))
#                    dataInt=list(map(float,dataInt[1:]))
        
#        if os.path.splitext(file_path[0])[1] ==".asc": #for files .Sample.Raw.asc , file with spectro info at beginning, data starts after occurence of #DATA
#            DATA = []
#            for item in range(len(file_path)):                
#                if os.path.split(file_path[item])[1][-15:]==".Sample.Raw.asc":
#                    samplename=os.path.split(file_path[item])[1][:-15]
#                else:
#                    samplename=os.path.split(file_path[item])[1][:-4]
#            
#                if samplename[-3:]=="_TT" or samplename[-3:]=="-TT": 
#                    curvetype="TT"
#                    samplenameshort = samplename[:-3]
#                elif samplename[-2:]=="_T" or samplename[-2:]=="-T":
#                    curvetype="TT"
#                    samplenameshort = samplename[:-2]
#                elif samplename[-3:]=="_TR" or samplename[-3:]=="-TR":
#                    curvetype="TR" 
#                    samplenameshort = samplename[:-3]
#                elif  samplename[-2:]=="_R" or samplename[-2:]=="-R":
#                    curvetype="TR" 
#                    samplenameshort = samplename[:-2]
#                elif samplename[-3:]=="_DR" or samplename[-3:]=="-DR" :
#                    curvetype="DR" 
#                    samplenameshort = samplename[:-3]
#                elif samplename[-3:]=="_DT" or samplename[-3:]=="-DT" :
#                    curvetype="DT"
#                    samplenameshort = samplename[:-3]
#                
#                file1 = open(file_path[item])
#                content = file1.readlines()
#                file1.close()
#                
#                dataCurve = content[(content.index('#DATA\n') + 1):len(content)]
#                dataWave = []
#                dataInt = []
#                for i in range(len(dataCurve)):
#                    pos = dataCurve[i].find('\t')
#                    dataWave.append(dataCurve[i][:pos])
#                    dataInt.append(dataCurve[i][pos+1:-1])
#                dataWave=list(map(float,dataWave[1:]))
#                dataInt=list(map(float,dataInt[1:]))
#                datadict = [samplenameshort, curvetype, dataWave, dataInt]
#                DATA.append(datadict)
#                
#        elif os.path.splitext(file_path[0])[1] ==".csv":   #for excel files .Sample.Raw.csv (only two columns, data starts at second line)
#            DATA = []
#            for item in range(len(file_path)):
#                samplename=os.path.split(file_path[item])[1][:-15]
#                        
#                if samplename[-3:]=="_TT" or samplename[-3:]=="-TT": 
#                    curvetype="TT"
#                    samplenameshort = samplename[:-3]
#                elif samplename[-2:]=="_T" or samplename[-2:]=="-T":
#                    curvetype="TT"
#                    samplenameshort = samplename[:-2]
#                elif samplename[-3:]=="_TR" or samplename[-3:]=="-TR":
#                    curvetype="TR" 
#                    samplenameshort = samplename[:-3]
#                elif  samplename[-2:]=="_R" or samplename[-2:]=="-R":
#                    curvetype="TR" 
#                    samplenameshort = samplename[:-2]
#                elif samplename[-3:]=="_DR" or samplename[-3:]=="-DR" :
#                    curvetype="DR" 
#                    samplenameshort = samplename[:-3]
#                elif samplename[-3:]=="_DT" or samplename[-3:]=="-DT" :
#                    curvetype="DT"
#                    samplenameshort = samplename[:-3]
#                    
#                with open(file_path[item]) as csvfile:
#                    readCSV = csv.reader(csvfile, delimiter=',')
#                    
#                    dataWave = []
#                    dataInt = []
#                    for row in readCSV:
#                        dataWave.append(row[0])
#                        dataInt.append(row[1])
#                    dataWave=list(map(float,dataWave[1:]))
#                    dataInt=list(map(float,dataInt[1:]))
#                datadict = [samplenameshort, curvetype, dataWave, dataInt]
#                DATA.append(datadict)    

#DATA[samplenames[item]] = [samplenameshort, curvetype, dataWave, dataInt,dataInt,samplenames[item],samplenames[item],'-',colorstylelist[len(DATA.keys())],int(2)]
        
        DATADICTtot = []
        
        if os.path.splitext(file_path[0])[1] !=".txt": 
            DATA2 = copy.deepcopy(DATA)
            while DATA != {}:
                listpositions = []
                names=list(DATA.keys())
                name = DATA[names[0]][0]
                for i in names:
                    if DATA[i][0] == name:
                        listpositions.append(i)
    
                datadict = {'Name': name, 'Wave': DATA[names[0]][2], 'TR': [],'TT':[],'A':[],'DR':[],'DT':[]}
                for i in listpositions:
                    if DATA[i][1]=='TR':
                        datadict['TR']=DATA[i][3]
                    elif DATA[i][1]=='TT':
                        datadict['TT']=DATA[i][3]
                    elif DATA[i][1]=='DR':
                        datadict['DR']=DATA[i][3]
                    elif DATA[i][1]=='DT':
                        datadict['DT']=DATA[i][3]
                if datadict['TR']!=[] and datadict['TT']!=[]:   
                    print(name)
                    refl = [float(i) for i in datadict['TR']]
                    trans = [float(i) for i in datadict['TT']]
                    absorpt = [float(i) for i in [100 - (x + y) for x, y in zip(refl, trans)]]
                    print(absorpt)
                    datadict['A']=absorpt
                    DATA2[name+'_A']=[name,'A',DATA[names[0]][2],absorpt,absorpt,name+'_A',name+'_A','-',colorstylelist[len(DATA2.keys())],int(2)]
                    Patternsamplenameslist.append(name+'_A')
                DATADICTtot.append(datadict)
                for index in sorted(listpositions, reverse=True):
                    del DATA[index]
            self.DATADICTtot=DATADICTtot
            self.DATA=DATA2
        else:
            self.DATA=DATA
#        print(self.DATA.keys())
        
        #update the listbox
        self.frame51.destroy()
        self.frame51=Frame(self.frame5,borderwidth=0,  bg="white")
        self.frame51.pack(fill=tk.BOTH,expand=1)
        importedsamplenames = StringVar()
        self.listboxsamples=Listbox(self.frame51,listvariable=importedsamplenames, selectmode=tk.MULTIPLE,width=15, height=3, exportselection=0)
        self.listboxsamples.bind('<<ListboxSelect>>', self.UpdateGraph0)
        self.listboxsamples.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(self.frame51, orient="vertical")
        scrollbar.config(command=self.listboxsamples.yview)
        scrollbar.pack(side="right", fill="y")
        self.listboxsamples.config(yscrollcommand=scrollbar.set)
        
        for item in Patternsamplenameslist:
            self.listboxsamples.insert(tk.END,item)
        
            
#    def SampleNames(self, DATAx):
#        Names = list(self.names)
#        for item in range(len(DATAx)):
#            Names.append(DATAx[item][0]+'_'+ DATAx[item][1])
#        return tuple(Names)
            
    def sortandexportspectro(self):
        
        keyslist=list(self.DATA.keys())
        namesshort=list(dict.fromkeys([self.DATA[item][0] for item in keyslist]))
        
        for name in namesshort:
            l=[]
            for i in keyslist:
                if self.DATA[i][0]==name:
                    l.append(['Wavelength']+['nm']+self.DATA[i][2])
                    l.append([self.DATA[i][1]]+['%']+self.DATA[i][3])
                
                    content=np.array(l).T.tolist()
                    content1=[]
                    for j in range(len(content)):
                        strr=''
                        for k in range(len(content[j])):
                            strr = strr + content[j][k]+'\t'
                        strr = strr[:-1]+'\n'
                        content1.append(strr)
                        
            file = open(name + '.txt','w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in content1)
            file.close()
    
    def UpdateGraph0(self,a):
        global titSpect
        global SpectlegendMod, takenforplot
        
        takenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        
        self.UpdateGraph(0)
        
    def UpdateGraph(self,a):
        global titSpect
        global SpectlegendMod, takenforplot
#        try:
        if self.DATA!={}:        
            DATAx=self.DATA
    #            sampletotake=[]
    #            namelist=[self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
    #            for name, var in namelist:
    #                sampletotake.append(var.get())
    #            sampletotake=[i for i,x in enumerate(sampletotake) if x == 1]
            if takenforplot!=[]:
                sampletotake=takenforplot
            else:
                sampletotake=[]
#            print('UpdateGraph')
#            print(sampletotake)
    #            else:
    #            sampletotake = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
    #            takenforplot=sampletotake
    #            if takenforplot!=[]:
    #                sampletotake=takenforplot
#            print(DATAx.keys())
            self.Spectrograph.clear()
            for i in sampletotake:
                x = DATAx[i][2]
                y = DATAx[i][3]
                if self.CheckLegend.get()==1:
                    self.Spectrograph.plot(x,y,label=DATAx[i][6],linestyle=DATAx[i][7],color=DATAx[i][8],linewidth=DATAx[i][9])
                else:
                    m=DATAx[i][7]
                    mm=DATAx[i][8]
                    mmm=DATAx[i][9]
                    self.Spectrograph.plot(x,y,linestyle=m,color=mm,linewidth=mmm)        
            
            self.Spectrograph.set_ylabel('Intensity (%)')
            self.Spectrograph.set_xlabel('Wavelength (nm)')
            if self.CheckLegend.get()==1:
                if self.pos1.get()!=0:
                    self.leg=self.Spectrograph.legend(loc=self.pos1.get())
                elif self.pos2.get()!=0:
                    self.leg=self.Spectrograph.legend(loc=self.pos2.get())
                elif self.pos3.get()!=0:
                    self.leg=self.Spectrograph.legend(loc=self.pos3.get())
                elif self.pos4.get()!=0:
                    self.leg=self.Spectrograph.legend(loc=self.pos4.get())
                else:
                    self.leg=self.Spectrograph.legend(loc=0)
            self.Spectrograph.axis([self.minx.get(),self.maxx.get(),self.miny.get(),self.maxy.get()])
            plt.gcf().canvas.draw()
    #        except AttributeError:
    #            print("you need to import data first...")
        
    def ExportGraph(self):
        try:
            f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
            self.fig.savefig(f, dpi=300, bbox_extra_artists=(self.leg,), transparent=True) 
        except:
            print("there is an exception...check legend maybe...")
    
    def GiveSpectatitle(self):
        self.window = tk.Toplevel()
        self.window.wm_title("Change title of spectro graph")
        center(self.window)
        self.window.geometry("325x55")
        self.titleSpect = tk.StringVar()
        entry=Entry(self.window, textvariable=self.titleSpect,width=40)
        entry.grid(row=0,column=0,columnspan=1)
        self.addtitlebutton = Button(self.window, text="Update",
                            command = self.giveSpectatitleupdate)
        self.addtitlebutton.grid(row=1, column=0, columnspan=1)
    def giveSpectatitleupdate(self): 
        global titSpect
        titSpect=1
        self.UpdateGraph(0)
    

    class PopulateListofSampleStylingSpectro(tk.Frame):
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
            global takenforplot, SpectlegendMod,DATAspectro
            global colorstylelist
            global listofanswer
            global listoflinestyle
            global listofcolorstyle, listoflinewidthstyle
            
            
            DATAx=DATAspectro
            listofanswer=[]
#            sampletotake=[]
#            if takenforplot!=[]:
#                for item in takenforplot:
#                    sampletotake.append(DATAx[item][0])
                    
            listoflinestyle=[]
            listofcolorstyle=[]
            listoflinewidthstyle=[]
            
            
            for item in takenforplot:
                listoflinestyle.append(DATAx[item][7])
                listofcolorstyle.append(DATAx[item][8])
                listofanswer.append(DATAx[item][6])
                listoflinewidthstyle.append(str(DATAx[item][9]))
#            print(takenforplot)
#            print(listofanswer)
            rowpos=1
            for item1 in range(len(takenforplot)): 
                label=tk.Label(self.frame,text=DATAx[takenforplot[item1]][5],fg='black',background='white')
                label.grid(row=rowpos,column=0, columnspan=1)
                textinit = tk.StringVar()
                #self.listofanswer.append(Entry(self.window,textvariable=textinit))
                listofanswer[item1]=Entry(self.frame,textvariable=textinit)
                listofanswer[item1].grid(row=rowpos,column=1, columnspan=2)
                textinit.set(DATAx[takenforplot[item1]][6])
    
                linestylelist = ["-","--","-.",":"]
                listoflinestyle[item1]=tk.StringVar()
                listoflinestyle[item1].set(DATAx[takenforplot[item1]][7]) # default choice
                OptionMenu(self.frame, listoflinestyle[item1], *linestylelist, command=()).grid(row=rowpos, column=4, columnspan=2)
                 
                """
                listofcolorstyle[item1]=tk.StringVar()
                listofcolorstyle[item1].set(DATAx[item1][10]) # default choice
                OptionMenu(self.frame, listofcolorstyle[item1], *colorstylelist, command=()).grid(row=rowpos, column=6, columnspan=2)
                """
                self.positioncolor=item1
                colstyle=Button(self.frame, text='Select Color', foreground=listofcolorstyle[item1], command=partial(self.getColor,item1))
                colstyle.grid(row=rowpos, column=6, columnspan=2)
                
                
                linewidth = tk.StringVar()
                listoflinewidthstyle[item1]=Entry(self.frame,textvariable=linewidth)
                listoflinewidthstyle[item1].grid(row=rowpos,column=8, columnspan=1)
                linewidth.set(str(DATAx[takenforplot[item1]][9]))
                
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
        
        self.UpdateSpectLegMod()
        self.reorderwindow.destroy()
        

        
    def ChangeLegendSpectgraph(self):
        global SpectlegendMod,DATAspectro
        DATAspectro=self.DATA
        if self.CheckLegend.get()==1:
            self.window = tk.Toplevel()
            self.window.wm_title("Change Legends")
            center(self.window)
            self.window.geometry("450x300")
            
            Button(self.window, text="Update",
                                command = self.UpdateSpectLegMod).pack()
            
            Button(self.window, text="Reorder",
                                command = self.reorder).pack()
    
            self.PopulateListofSampleStylingSpectro(self.window).pack(side="top", fill="both", expand=True)
     
        
#            self.changeSpectlegend = Button(self.window, text="Update",
#                                command = self.UpdateSpectLegMod)
#            self.changeSpectlegend.grid(row=0, column=0, columnspan=3)
#    
#            self.listofanswer=[]
#            for rowitem in range(len(SpectlegendMod)):
#                label=tk.Label(self.window,text=SpectlegendMod[rowitem][0])
#                label.grid(row=rowitem+1,column=0, columnspan=1)
#                textinit = tk.StringVar()
#                self.listofanswer.append(Entry(self.window,textvariable=textinit))
#                textinit.set(SpectlegendMod[rowitem][1])
#                self.listofanswer[rowitem].grid(row=rowitem+1,column=1, columnspan=2)
            
    def UpdateSpectLegMod(self):
        global SpectlegendMod
        global listofanswer, takenforplot
        global listoflinestyle
        global listofcolorstyle,listoflinewidthstyle

        leglist=[]
        for e in listofanswer:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        for item in range(len(takenforplot)):
            self.DATA[takenforplot[item]][6]=leglist[item]
        
        leglist=[]
        for e in listoflinestyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        for item in range(len(takenforplot)):
            self.DATA[takenforplot[item]][7]=leglist[item]        
        leglist=[]
        for e in listofcolorstyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e) 
        for item in range(len(takenforplot)):
            self.DATA[takenforplot[item]][8]=leglist[item]  
        leglist=[]
        for e in listoflinewidthstyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e) 
        for item in range(len(takenforplot)):
            self.DATA[takenforplot[item]][9]=int(leglist[item]) 
                
#        print('UpdateSpectLegMod')
#        print(takenforplot)
        self.UpdateGraph(0)
        self.window.destroy()
        self.ChangeLegendSpectgraph()
        
    def AbsCoeffAndTauc(self):
        self.AbsCoeffAndTaucWin = tk.Toplevel()
        self.AbsCoeffAndTaucWin.wm_title("AbsCoeff, Tauc plot")
        self.AbsCoeffAndTaucWin.geometry("280x250")
        center(self.AbsCoeffAndTaucWin)
        
        #names=self.SampleNames(self.DATA)
        
#        names=[item[0]+'-'+item[1] for item in self.DATA]
#        
#        namesshort=[]
#        for item in names:
#            if item.split("-")[0] not in namesshort:
#                namesshort.append(item.split("-")[0])
        
        names=list(self.DATA.keys())
        namesshort=list(dict.fromkeys([self.DATA[item][0] for item in names]))
        
        label = tk.Label(self.AbsCoeffAndTaucWin, text="Select:", font=12, bg="white",fg="black")
        label.pack(fill=tk.X, expand=1)
        
        self.RTchoice=StringVar()
        self.dropMenuTauc = OptionMenu(self.AbsCoeffAndTaucWin, self.RTchoice, *namesshort, command=())
        self.dropMenuTauc.pack(expand=1)
        self.RTchoice.set("")
        
        label = tk.Label(self.AbsCoeffAndTaucWin, text="Thickness:", font=12, bg="white",fg="black")
        label.pack(fill=tk.X, expand=1)
        
        self.thickness = tk.DoubleVar()
        Entry(self.AbsCoeffAndTaucWin, textvariable=self.thickness,width=5).pack()
        self.thickness.set(100)
        
        label = tk.Label(self.AbsCoeffAndTaucWin, text="Transition type:", font=12, bg="white",fg="black")
        label.pack(fill=tk.X, expand=1)

        transitions=["1/2 for direct allowed", "3/2 for direct forbidden", "2 for indirect allowed", "3 for indirect forbidden"]
        self.TransitionChoice=StringVar()
        self.dropMenuTaucTrans = OptionMenu(self.AbsCoeffAndTaucWin, self.TransitionChoice, *transitions, command=())
        self.dropMenuTaucTrans.pack(expand=1)
        self.TransitionChoice.set(transitions[0])
        
        ExportTauc = Button(self.AbsCoeffAndTaucWin, text="Export",width=15, command = self.AbsCoeffAndTaucSave)
        ExportTauc.pack(fill=tk.X, expand=1)
        
        label = tk.Label(self.AbsCoeffAndTaucWin, text="AbsCoeff=-Log(TT/(1-TR))/thickness;", font=("Verdana", 8), bg="white",fg="black")
        label.pack(fill=tk.BOTH, expand=1)
        label = tk.Label(self.AbsCoeffAndTaucWin, text="Tauc=(AbsCoeff * energy)^TransitionCoeff;", font=("Verdana", 8), bg="white",fg="black")
        label.pack(fill=tk.BOTH, expand=1)
        
        

    def AbsCoeffAndTaucSave(self):
        
        if self.RTchoice.get()!="":
            if self.thickness.get()!=0:
            
                reflectance=[]
                transmittance=[]
                absorptance=[]
                wavelength=[]
                sampletotake=[]
                
                keysData=list(self.DATA.keys())
#                names=[self.DATA[item][0]+'-'+self.DATA[item][1] for item in keysData]
                sampletotake=[i for i in keysData if self.RTchoice.get()==self.DATA[i][0]]
                
                if len(sampletotake)>0:
                    wavelength=self.DATA[sampletotake[0]][2]
                    for item in sampletotake:
                        if "_TR" in item:
                            reflectance=self.DATA[item][3]
                        elif "_TT" in item:
                            transmittance=self.DATA[item][3]
                        elif "_A" in item:
                            absorptance=self.DATA[item][3]  
                
                if reflectance!=[] and transmittance != [] and absorptance!=[] and wavelength!=[]:
                    f = filedialog.asksaveasfilename(defaultextension=".txt",initialfile= self.DATA[sampletotake[0]][0]+"_AbscoefTauc.txt", filetypes = (("text file", "*.txt"),("All Files", "*.*")))
            
                    c = lightspeed
                    h = 4.1e-15
                    dataFactor=0.01
                    
                    transition=0.5
                    if self.TransitionChoice.get()=="1/2 for direct allowed":
                        transition=0.5
                    elif self.TransitionChoice.get()=="3/2 for direct forbidden":
                        transition=1.5
                    elif self.TransitionChoice.get()=="2 for indirect allowed":
                        transition=2
                    elif self.TransitionChoice.get()=="3 for indirect forbidden":
                        transition=3
                    
                    energy=[(c*h)/(float(x)/1e9) for x in wavelength]
                    m=[dataFactor*float(x) for x in transmittance]
                    n=[1-dataFactor*float(x) for x in reflectance]
                    o=list(map(div, m,n))
                    o=[abs(x) for x in o]
                    o=list(map(log,o))
                    abscoeff=[-float(x)/(self.thickness.get()*1e-7) for x in o]
                    ahc=[pow(abs(abscoeff[i]*energy[i]),float(transition)) for i in range(len(energy))]
                    logalpha=[log(abs(i)) for i in abscoeff]
                    
                    taucdata=[]
                    taucdata.append(wavelength)
                    taucdata.append(energy)
                    taucdata.append(reflectance)
                    taucdata.append(transmittance)
                    taucdata.append(absorptance)
                    taucdata.append(logalpha)
                    taucdata.append(abscoeff)
                    taucdata.append(ahc)
                    
                    taucdata=list(map(list,zip(*taucdata)))
                    
                    taucdata=[["Wavelength","Energy","Reflectance","Transmittance","Absorptance","LogAlpha","AbsCoeff","Tauc"]]+taucdata
            
                    file = open(f,'w', encoding='ISO-8859-1')
                    file.writelines("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % tuple(item) for item in taucdata)
                    file.close()
                else:
                    print("cannot find the corresponding TR and TT files")
            else:
                print("the thickness should be non-zero")
        else:
            print("choose a sample")
        
    def SavitzkyGolayFiltering(self):
        
        if self.SGwinsize.get()>self.SGorder.get() and self.SGwinsize.get()%2==1:
            if self.listboxsamples.curselection()!=():
                samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
                if samplestakenforplot!=[]:
                    for item in samplestakenforplot:
                        y = self.DATA[item][3]
                        y=np.array(y)
                        self.DATA[item][3] = savitzky_golay(y, window_size=self.SGwinsize.get(), order=self.SGorder.get())
                
                self.UpdateGraph(0)
        else:
            messagebox.showinfo("Information","the SG window-size must be larger than the SG order, positive and odd.")

    def backtoOriginal(self):
        
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
                self.DATA[item][3]=self.DATA[item][4]
        
        self.UpdateGraph(0)        
        
###############################################################################        
if __name__ == '__main__':
    app = SpectroApp()
    #app.geometry("720x750")
    center(app)
    app.mainloop()



