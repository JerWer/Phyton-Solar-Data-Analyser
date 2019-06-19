#! python3

import os,datetime
import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg

import tkinter as tk
from tkinter import *
from tkinter.ttk import Treeview
from tkinter import messagebox, Button, Label, Frame, Entry, Checkbutton, IntVar, Toplevel, Scrollbar, Canvas, OptionMenu, StringVar

from tkinter import filedialog
from pathlib import Path
import numpy as np
import copy
import xlsxwriter
import xlrd
from scipy.interpolate import interp1d
from scipy import integrate
from operator import itemgetter
from itertools import groupby, chain
#import PIL
from PIL import Image as ImageTk
from matplotlib.ticker import MaxNLocator
from tkinter import font as tkFont
from matplotlib.transforms import Bbox
import pickle
import six
from tkinter import colorchooser
from functools import partial
import darktolight as DtoL
import os.path
import shutil
import sqlite3
from dateutil import parser
import pandas as pd
from statistics import mean 
from scipy.optimize import curve_fit
"""
TODOLIST

- open/read .dac files
- profile by summing each line
- map: each column is one profile => contourplot or 3D profile with x=wavelength, y=time, z=intensity
- profile fitting, decay time, other properties?



"""
def fitfuncExpdec2(x,y0,A1,A2,t1,t2):
    return y0 + A1*np.exp(-x/t1) + A2*np.exp(-x/t2)

def fitfuncExpdec1(x,y0,A1,t1):
    return y0 + A1*np.exp(-x/t1)


file_paths = filedialog.askopenfilenames()

for file_path in file_paths:
    filetoread = open(file_path,"r", encoding='ISO-8859-1')
    filerawdata = filetoread.readlines()
    filename=os.path.splitext(os.path.basename(file_path))[0]
    
    #line=filerawdata[1].split('\t')
    #print(line)
    
    Matrixdata ={} #dict of dict of number, x=time, y=wavelength, z=intensity
    profile=[[],[],[]]#[time,sumofintensitiesonallwavelengths]
    Wavelengths=filerawdata[0].split('\t')[1:]
    #print(Wavelengths)
    for i in range(1,len(filerawdata)):
        line=filerawdata[i].split('\t')
        
    ##    print(line)
    #    break
        sumofline=0
    #    print(len(line))
    #    print(len(Wavelengths))
        for j in range(1,len(line)):
            Matrixdata[line[0]]={}
            Matrixdata[line[0]][Wavelengths[j-1]]=float(line[j])
            sumofline+=float(line[j])
    #    print()
        profile[0].append(float(line[0]))
        profile[1].append(sumofline)
    
    indexofmax=profile[1].index(max(profile[1]))
    baselinelist=[profile[1][j] for j in range(indexofmax-25,indexofmax-15)]
#    profile[2]=[(m-min(profile[1]))/(max(profile[1])-min(profile[1])) for m in profile[1]]
    profile[2]=[(m-mean(baselinelist))/(max(profile[1])-mean(baselinelist)) for m in profile[1]]
    
    plt.plot(profile[0],profile[2],label=filename)
    
    xx=profile[0][indexofmax:]
    yy=profile[2][indexofmax:]
    popt, pcov = curve_fit(fitfuncExpdec2, np.array(xx), np.array(yy), p0=(0,1,1, 10000, 10000))
#    print(popt)
    fitydat=[fitfuncExpdec2(x,*popt) for x in xx]
    
    t1=list(popt)[3]
    t2=list(popt)[4]
    tottime=t1+t2
    plt.plot(xx,fitydat,label='t1+t2: '+"%.2f"%t1+" + %.2f"%t2+" = %.2f"%tottime)

    filetoexport=["time\tintensity\tnormalized\tfit\n","ns\t-\t-\t-\n"]+[str(profile[0][i])+'\t'+str(profile[1][i])+'\t'+str(profile[2][i])+'\t'+str(fitydat[i])+'\n' for i in range(len(profile[0]))]
    
    file = open(str(str(Path(file_path))[:-4]+"_data_"+"%.2f"%tottime+".txt"),'w', encoding='ISO-8859-1')
    file.writelines("%s" % item for item in filetoexport)
    file.close() 
plt.title("fit func: y0 + A1*np.exp(-x/t1) + A2*np.exp(-x/t2)")
plt.legend()
plt.savefig(os.path.join(os.path.dirname(file_path),'graph.png'),dpi=300)
plt.show()
















