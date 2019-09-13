#! python3

import os
from tkinter import filedialog
import csv
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from scipy import integrate
from scipy.interpolate import interp1d
import peakutils
from peakutils.plot import plot as pplot
from PIL import Image as ImageTk
from scipy import signal
from scipy.signal import chirp, find_peaks, peak_widths

"""


"""


#load files
ready=0
j=0
while j<2:
    try: 
        file_paths =filedialog.askopenfilenames(title="Please select the PL files")
        filetypes=[os.path.splitext(item)[1] for item in file_paths]
        filetype=list(set(filetypes))[0]
        if filetype==".arc_data":
            ready=1 
#            directory = filedialog.askdirectory(title="Where saving?")
#                
#            if not os.path.exists(directory):
#                os.makedirs(directory)
#                os.chdir(directory)
#            else :
#                os.chdir(directory)
            break
        else:
            print("Please select correct PL files")
            j+=1
    except:
        print("no file selected")
        j+=1

#finds peak, calculate area, extract OD, power, integtime
if ready:
    DATA={}
    for i in range(len(file_paths)):
        partdict={}
        filename=os.path.split(file_paths[i])[-1][:-9]
        print(filename)
        
        #samplenumber
        samplenumber=filename.split('_')[0]
        
        #extract OD, power, integtime
        filenamesplit=filename.split('_')
        for item in filenamesplit:
            if 'mW' in item:
                LaserPower=float(item[:-2])
            if 'ms' in item:
                Int_Time=float(item[:-2])
            if 'OD' in item:
                OD=float(item[2:])
        
        #extract which type of file it is
        filetype=filename.split('_')[1]
        
        #get data
        filetoread = open(file_paths[i],"r", encoding='ISO-8859-1')
        filerawdata = list(filetoread.readlines())
        x=[]
        y=[]
        for lines in filerawdata:
            if '#' not in lines and lines!='\n':
                x.append(float(lines.split('\t')[0]))
                y.append(float(lines.split('\t')[1]))
        plt.plot(x,y)
        if filetype=='samplePLon':
            yfiltered=list(signal.savgol_filter(y,
                               53, # window size used for filtering
                               3)) # order of fitted polynomial 
            plt.plot(x,yfiltered)
            y=yfiltered
        
        #find peak
        
        yarray=np.array(y)
        threshold=0.01
        MinDist=50
        while(1):
            indexes = peakutils.indexes(yarray, thres=threshold, min_dist=MinDist)
            if len(indexes)==1:
                break
            else:
                threshold+=0.01
        print(x[indexes[0]])
        
        base=list(peakutils.baseline(yarray,1))
#        print(base)
        plt.plot(x,base)
        
        #calculate area
        f = interp1d(x, yarray-base, kind='cubic')
        plt.plot(x, f(x))
        f2 = lambda x0: f(x0)
        peakarea = integrate.quad(f2,x[0],x[-1])[0]
        print(peakarea)
        
        #normalize area
        
        PL_area_norm = peakarea * (10**OD) * (150 / LaserPower) * (1000 / Int_Time)
        
        print(PL_area_norm)
        
        #export control graphs with overlay baseline lines and area taken
        
        DATA[samplenumber]={'LaserPower':LaserPower, 'type': filetype, 'Int_Time':Int_Time, 'OD': OD, 'wave': x, 
            'intensity': y, 'baseline': base, 'peakarea': peakarea, 'PL_area_norm': PL_area_norm}

    #calculate PLQE with Richard Friend's formula
    for key in list(DATA.keys):
        L_a = DATA[key][PL_area_norm]
        L_b = 
        L_c = 
        P_c = 
        P_b = 
        A = 1 - L_c ./ L_b;
        ext_PLQE = (P_c - (1 - A) .* P_b) ./ (L_a .* A);


























