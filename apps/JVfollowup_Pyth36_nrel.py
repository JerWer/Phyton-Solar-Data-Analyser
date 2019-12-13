#! python3

import os

import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg
import tkinter as tk
from tkinter import Tk, messagebox, Entry, Button, Checkbutton, IntVar, Toplevel, OptionMenu, Frame, StringVar, Scrollbar, Listbox
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
from operator import itemgetter
from itertools import groupby, chain
from datetime import datetime
from dateutil import parser
from statistics import mean


#import THEANALYSER_pyth36 as analyserMain

"""
TODOLIST

- separate forward reverse

"""





#path = 'c:\\projects\\hc2\\'




DATA=[]
usernames=[]

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


###############################################################################             
    
class JVfollowup(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "FollowingJVparameters")
        Toplevel.config(self,background="white")
        self.wm_geometry("500x500")
        center(self)
        self.initUI()


    def initUI(self):
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.canvas0 = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.superframe=Frame(self.canvas0,background="#ffffff")
        self.canvas0.pack(side="left", fill="both", expand=True)
        
        label = tk.Label(self.canvas0, text="JV parameters over time", font=LARGE_FONT, bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)
        
        frame1=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame1.pack(fill=tk.BOTH,expand=1)
        frame1.bind("<Configure>", self.onFrameConfigure)
        self.fig1 = plt.figure(figsize=(3, 2))
        canvas = FigureCanvasTkAgg(self.fig1, frame1)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.JVparamgraph = plt.subplot2grid((1, 5), (0, 0), colspan=5)
        self.toolbar = NavigationToolbar2TkAgg(canvas, frame1)
        self.toolbar.update()
        canvas._tkcanvas.pack(fill = BOTH, expand = 1) 
        
        
        frame2=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame2.pack(fill=tk.X,expand=0)
        
        
        Button(frame2, text="import data", command = self.importdata).pack(side=tk.LEFT,expand=1)

        
        self.Usermenubutton = tk.Menubutton(frame2, text="Choose User", 
                                   indicatoron=True, borderwidth=1, relief="raised")
        self.Usermenu = tk.Menu(self.Usermenubutton, tearoff=False)
        self.Usermenubutton.configure(menu=self.Usermenu)
        self.Usermenubutton.pack(side=tk.LEFT,expand=1)

        
        Ytype = ["Jsc","Voc","FF","Eff","Vmpp","Jmpp","Roc","Rsc"]
        self.YtypeChoice=StringVar()
        self.YtypeChoice.set("Jsc") # default choice
        self.dropMenuFrame = OptionMenu(frame2, self.YtypeChoice, *Ytype, command=self.updateGraph)
        self.dropMenuFrame.pack(side=tk.LEFT,fill=tk.X,expand=1)
        
        
        Button(frame2, text="export graph", command = self.exportGraph).pack(side=tk.LEFT,expand=1)
        
        self.CheckAllgraph = IntVar()
        Checkbutton(frame2,text='all?',variable=self.CheckAllgraph, 
                           onvalue=1,offvalue=0,height=1, width=2, command = (), bg="white").pack(side=tk.LEFT,fill=tk.X,expand=1)

    def on_closing(self):
        global DATA
        global usernames
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            DATA=[]
            usernames=[]
            self.destroy()
            self.master.deiconify()
        
    def onFrameConfigure(self, event):
        #self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))
        self.canvas0.configure(scrollregion=(0,0,500,500))
    
    def importdata(self):
        global DATA
        
#        pathtofolder="//sti1files.epfl.ch/pv-lab/pvlab-commun/Groupe-Perovskite/Experiments/CellParametersFollowUP/"
#        
#        os.chdir(pathtofolder)
#
#        file_pathnew=[]
#        file_path =filedialog.askopenfilenames(title="Please select the .iv files", initialdir =pathtofolder)
#        if file_path!='':
#            filetypes=[os.path.splitext(item)[1] for item in file_path]
#            if len(list(set(filetypes)))==1:
#                filetype=list(set(filetypes))[0]
#                if filetype==".iv":
#                    file_pathnew=file_path
#                    self.getdatalistsfromIVTFfiles(file_pathnew)
#                else:
#                    print("wrong files...")
                    
        path = filedialog.askdirectory()
            
        files = []
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if '.txt' in file and '_pX' in file:
                    files.append(os.path.join(r, file))
        
        print(len(files))
        
        self.getdatalistsfromIVTFfiles(files)
        
        
    def extract_jv_params(self, jv):#function originally written by Rohit Prasana (adapted by JW)
        '''
        Extract Voc, Jsc, FF, Pmax from a given JV curve
            * Assume given JV curve is in volts and mA/cm2
        '''
        resample_step_size = 0.00001 # Voltage step size to use while resampling JV curve to find Pmax
    
        from scipy.interpolate import interp1d, UnivariateSpline
    
        # Create a dict to store the parameters. Default values are -1 indicating failure to extract parameter
        params = {'Voc': -1., 'Jsc': -1., 'FF': -1., 'Pmax': -1., 'Roc':-1., 'Rsc':-1., 'Jmpp':-1, 'Vmpp':-1, 'Rshunt':-1, 'Rseries':-1}
        
        try:
            # Extract Jsc by interpolating wrt V
            jv_interp_V = interp1d(jv[0], jv[1], bounds_error=False, fill_value=0.)
            Jsc = jv_interp_V(0.)
            params['Jsc'] = abs(np.around(Jsc, decimals=3))
        
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
            
            # Calculate Rsc&Roc 
            x= [x0 for x0,y0 in sorted(zip(jv[0],jv[1]))]
            y= [0.001*y0 for x0,y0 in sorted(zip(jv[0],jv[1]))]
    
#            spl = UnivariateSpline(x,y, s=0)
    #        plt.plot(x, spl(x))
    #        plt.plot(x,y,'ro')
    #        plt.show()
    #        splder = spl.derivative(n=1)
    #        plt.plot(x,1/splder(x))
    #        plt.show()
    #        params['Roc']=1./splder(params['Voc'])
    #        params['Rsc']=1./splder(0.)
            
            
    #        print('Rsc')
    #        print(params['Rsc'])
    #        print(params['Roc'])
            
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
    #        print(xSC)
    #        print(ySC)
    #        plt.plot(xSC,ySC,'bo')
            xSC=np.array(xSC)
            ySC=np.array(ySC)    
                
    #        slope = stats.linregress(xSC,ySC)   
            
            params['Rsc'] =abs( 1/(((mean(xSC)*mean(ySC)) - mean(xSC*ySC)) / ((mean(xSC)**2) - mean(xSC**2))))    
            
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
                
                params['Roc'] =abs( 1/(((mean(xSC)*mean(ySC)) - mean(xSC*ySC)) / ((mean(xSC)**2) - mean(xSC**2))))
            else:
                xSC=x[-3:]
                ySC=y[-3:]
#                plt.plot(xSC,ySC,'bo')
                xSC=np.array(xSC)
                ySC=np.array(ySC)      
                
                params['Roc'] = abs(1/(((mean(xSC)*mean(ySC)) - mean(xSC*ySC)) / ((mean(xSC)**2) - mean(xSC**2))) )   
            
            
            
            
#        plt.show()
#        print(params['Rsc'])
#        print(params['Roc'])
#        print(params['Jsc'])
        
        
        except:
            print("error with fits, probably a dark curve...")
    
        return  params    
    

    def getdatalistsfromIVTFfiles(self, file_path): #reads JV and mpp files from NREL
        global DATA        
        
        for i in range(len(file_path)):
            filetoread = open(file_path[i],"r", encoding='ISO-8859-1')
            filerawdata = filetoread.readlines()
            print(i)
            filetype = 0
            if "HEADER START" in filerawdata[0]:
                filetype = 1 #JV file from solar simulator in SERF C215
            elif "Power (mW/cm2)" in filerawdata[0]:
                filetype = 2
            
            if filetype ==1 : #J-V files of SERF C215
                              
                partdict = {}
                partdict["filepath"]=file_path[i]
                
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
                
                partdict["Operator"]='JW'
                              
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
                
                if partdict["FF"]<83 and partdict["FF"]>0 and partdict["Voc"]>0 and partdict["Voc"]<810 and partdict["Jsc"]>0 and partdict["Jsc"]<34 and partdict["Eff"]<21 and partdict["Illumination"]=="Light":
                    DATA.append(partdict)
                

        DATA = sorted(DATA, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATA if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
#        print(groupednames)
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
        
        usernames=list(set([d["Operator"] for d in DATA]))
        print(usernames)
        
        self.UserNames=tuple(usernames)
        self.Usermenu = tk.Menu(self.Usermenubutton, tearoff=False)
        self.Usermenubutton.configure(menu=self.Usermenu)
        self.choicesUsers = {}
        for choice in range(len(self.UserNames)):
            self.choicesUsers[choice] = tk.IntVar(value=0)
            self.Usermenu.add_checkbutton(label=self.UserNames[choice], variable=self.choicesUsers[choice], 
                                 onvalue=1, offvalue=0, command = ())
        print("ready")
        
#    def getdatalistsfromIVTFfiles(self, file_path):
#        global DATA  
#        global usernames
#                
#        for i in range(len(file_path)):
#            filetoread = open(file_path[i],"r")
#            filerawdata = filetoread.readlines()
#            print(i)
#            filetype = 0
#            for item0 in range(len(filerawdata)):
#                if "voltage/current" in filerawdata[item0]:
#                    filetype = 1
#                    break
#                if "IV FRLOOP" in filerawdata[item0]:
#                    filetype =2
#                    break
#            try:         
#                if filetype ==1 or filetype==2: #J-V files and FRLOOP
#                    partdict = {}
#                    
#                    for item in range(len(filerawdata)):
#                        if "Illumination:" in filerawdata[item]:
#                            partdict["Illumination"]=filerawdata[item][14:-1]
#                            break
#                        else:
#                            partdict["Illumination"]="Light"
#                    if partdict["Illumination"]=="Light":
#                    
#                        partdict["SampleName"]=file_path[i].split("/")[-1][:-3]
#                        
#                        for item in range(len(filerawdata)):
#                            if "IV measurement time:" in filerawdata[item]:
#                                #partdict["MeasDayTime"]=filerawdata[item][22:-1]
#                                
#                                partdict["MeasDayTime"]=datetime.strptime(filerawdata[item][22:-1], '%Y-%m-%d %H:%M:%S.%f')
#                                break
#                        for item in range(len(filerawdata)):
#                            if "Cell size [m2]:" in filerawdata[item]:
#                                partdict["CellSurface"]=float(filerawdata[item][17:-1])
#                                break
#                        for item in range(len(filerawdata)):
#                            if "Voc [V]:" in filerawdata[item]:
#                                partdict["Voc"]=float(filerawdata[item][19:-1])*1000
#                                break            
#                        for item in range(len(filerawdata)):
#                            if "Jsc [A/m2]:" in filerawdata[item]:
#                                partdict["Jsc"]=float(filerawdata[item][19:-1])*0.1
#                                break            
#                        for item in range(len(filerawdata)):
#                            if "FF [.]:" in filerawdata[item]:
#                                partdict["FF"]=float(filerawdata[item][18:-1])*100
#                                break            
#                        for item in range(len(filerawdata)):
#                            if "Efficiency [.]:" in filerawdata[item]:
#                                partdict["Eff"]=float(filerawdata[item][19:-1])*100
#                                break
#                        for item in range(len(filerawdata)):
#                            if "Pmpp [W/m2]:" in filerawdata[item]:
#                                partdict["Pmpp"]=float(filerawdata[item][19:-1])
#                                break                
#                        for item in range(len(filerawdata)):
#                            if "Vmpp [V]:" in filerawdata[item]:
#                                partdict["Vmpp"]=float(filerawdata[item][10:-1])*1000
#                                break                
#                        for item in range(len(filerawdata)):
#                            if "Jmpp [A]:" in filerawdata[item]:
#                                partdict["Jmpp"]=float(filerawdata[item][10:-1])*0.1
#                                break   
#                        for item in range(len(filerawdata)):
#                            if "Roc [Ohm.m2]:" in filerawdata[item]:
#                                partdict["Roc"]=float(filerawdata[item][15:-1])*10000
#                                break
#                        for item in range(len(filerawdata)):
#                            if "Rsc [Ohm.m2]:" in filerawdata[item]:
#                                partdict["Rsc"]=float(filerawdata[item][15:-1])*10000
#                                break
#                        partdict["VocFF"]=float(partdict["Voc"])*float(partdict["FF"])*0.01
#                        partdict["RscJsc"]=float(partdict["Rsc"])*float(partdict["Jsc"])*0.001
#                        
#                        for item in range(len(filerawdata)):
#                            if "Vstart:" in filerawdata[item]:
#                                partdict["Vstart"]=float(filerawdata[item][7:-1])
#                                break
#                        for item in range(len(filerawdata)):
#                            if "Vend:" in filerawdata[item]:
#                                partdict["Vend"]=float(filerawdata[item][5:-1])
#                                break
#                        
#                        if abs(float(partdict["Vstart"]))>abs(float(partdict["Vend"])):
#                            partdict["ScanDirection"]="Reverse"
#                        else:
#                            partdict["ScanDirection"]="Forward"
#                        
#                        for item in range(len(filerawdata)):
#                            if "User name:" in filerawdata[item]:
#                                partdict["Operator"]=filerawdata[item][11:-1]
#                                break
#                        
#                        DATA.append(partdict)
#            except:
#                print("except")
#
#        DATA = sorted(DATA, key=itemgetter('SampleName')) 
#        names=[d["SampleName"] for d in DATA if "SampleName" in d]
#        groupednames=[list(j) for i, j in groupby(names)]
#        for item in range(len(groupednames)):
#            if len(groupednames[item])!=1:
#                for item0 in range(1,len(groupednames[item]),1):
#                    groupednames[item][item0]+= "_"+str(item0)
#        groupednames=list(chain.from_iterable(groupednames))
#        for item in range(len(DATA)):
#            DATA[item]['SampleName']=groupednames[item]
#        
#        usernames=list(set([d["Operator"] for d in DATA]))
#        #print(usernames)
#        
#        self.UserNames=tuple(usernames)
#        self.Usermenu = tk.Menu(self.Usermenubutton, tearoff=False)
#        self.Usermenubutton.configure(menu=self.Usermenu)
#        self.choicesUsers = {}
#        for choice in range(len(self.UserNames)):
#            self.choicesUsers[choice] = tk.IntVar(value=0)
#            self.Usermenu.add_checkbutton(label=self.UserNames[choice], variable=self.choicesUsers[choice], 
#                                 onvalue=1, offvalue=0, command = ())
#        print("ready")
        
    def updateGraph(self,a):
        global DATA
        global usernames
        
        takenforplot=[]
        for name, var in self.choicesUsers.items():
            takenforplot.append(var.get())
#        print(takenforplot)
        m=[]
        for i in range(len(takenforplot)):
            if takenforplot[i]==1:
                m.append(usernames[i])
        takenforplot=m
        #print(takenforplot)
        
        #update graph
        self.JVparamgraph.clear()
        if takenforplot==[]:
            paramchoice=self.YtypeChoice.get()
                        
            timelist=[DATA[i]["MeasDayTime2"] for i in range(len(DATA))]
            
            ydat=[DATA[i][paramchoice] for i in range(len(DATA))]
            
            self.JVparamgraph.plot(timelist,ydat,'o')
            
            self.JVparamgraph.set_ylabel(paramchoice, fontsize=14)
            #self.JVparamgraph.set_xlabel('Time', fontsize=14)
            plt.gcf().autofmt_xdate()
            plt.gcf().canvas.draw()
        else:
            
            for item in takenforplot:
                paramchoice=self.YtypeChoice.get()
                timelist=[DATA[i]["MeasDayTime2"] for i in range(len(DATA)) if DATA[i]["Operator"]==item]
                ydat=[DATA[i][paramchoice] for i in range(len(DATA)) if DATA[i]["Operator"]==item]
                self.JVparamgraph.plot(timelist,ydat,'o', label=item)
            
            self.JVparamgraph.set_ylabel(paramchoice, fontsize=14)
            self.JVparamgraph.legend()
            plt.gcf().autofmt_xdate()
            plt.gcf().canvas.draw()
            
    def exportGraph(self):
        global DATA
        global usernames
        
        if self.CheckAllgraph.get()==0:
            f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
            self.fig1.savefig(f, dpi=300)

        else:
            f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))

            Ytype = ["Jsc","Voc","FF","Eff","Vmpp","Jmpp","Roc","Rsc"]
            
            exportdatatotxt=[[DATA[i]["MeasDayTime2"] for i in range(len(DATA))]]

            for paramchoice in Ytype:
                takenforplot=[]
                for name, var in self.choicesUsers.items():
                    takenforplot.append(var.get())
                m=[]
                for i in range(len(takenforplot)):
                    if takenforplot[i]==1:
                        m.append(usernames[i])
                takenforplot=m

                self.JVparamgraph.clear()
                
                if takenforplot==[]:                                
                    timelist=[DATA[i]["MeasDayTime2"] for i in range(len(DATA))]
                    
                    
                    ydat=[DATA[i][paramchoice] for i in range(len(DATA))]
                    exportdatatotxt.append(ydat)
                    
                    self.JVparamgraph.plot(timelist,ydat,'o')
                    
                    self.JVparamgraph.set_ylabel(paramchoice, fontsize=14)
                    plt.gcf().autofmt_xdate()
                    plt.gcf().canvas.draw()
                else:
                    
                    for item in takenforplot:
                        timelist=[DATA[i]["MeasDayTime2"] for i in range(len(DATA)) if DATA[i]["Operator"]==item]
                        ydat=[DATA[i][paramchoice] for i in range(len(DATA)) if DATA[i]["Operator"]==item]
                        self.JVparamgraph.plot(timelist,ydat,'o', label=item)
                    
                    self.JVparamgraph.set_ylabel(paramchoice, fontsize=14)
                    self.JVparamgraph.legend()
                    plt.gcf().autofmt_xdate()
                    plt.gcf().canvas.draw()
                
                self.fig1.savefig(f[:-4]+"_"+paramchoice+f[-4:], dpi=300)
            
            templist=map(list, zip(*exportdatatotxt))
            DATAcompforexport1=["Date\tJsc\tVoc\tFF\tEff\tVmpp\tJmpp\tRoc\tRsc\n"]            
            for item in templist:
                line=""
                for item1 in item:
                    line=line+str(item1)+"\t"
                line=line[:-1]+"\n"
                DATAcompforexport1.append(line)
                
            file = open(str(f[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in DATAcompforexport1)
            file.close()
            
            
###############################################################################        
if __name__ == '__main__':
    
    app = JVfollowup()
    app.mainloop()
