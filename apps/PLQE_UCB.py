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
from scipy import signal, integrate
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

        filename=os.path.split(file_paths[i])[-1][:-9]
        
        #samplenumber
        samplenumber=filename.split('_')[0]
        DATA[samplenumber]={}
    
    for i in range(len(file_paths)):
        plt.close()
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
#        print(filetype)
        DATA[samplenumber][filetype]={}
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
                indexes.tolist()
                break
            else:
                if threshold<1:
                    threshold+=0.01
                else:
                    indexes=[]
                    break
#        print(x[indexes[0]])
        if len(indexes)!=0:
            base=list(peakutils.baseline(yarray,1))
    #        print(base)
            plt.plot(x,base)
            
            indexLeft=0
            indexRight=-1
            peakheight=y[indexes[0]]-base[indexes[0]]
            i=1
#            print(len(y))
#            print(indexes[0])
            while 1:
                
                if y[indexes[0]+i]-base[indexes[0]+i]<=0:
                    indexRight=indexes[0]+i
                    break
                elif indexes[0]+i==len(y)-1:
                    break
                else:
                    i+=1
            i=1
            while 1:
                if y[indexes[0]-i]-base[indexes[0]-i]<=0:
                    indexLeft=indexes[0]-i
                    break
                elif indexes[0]-i==0:
                    break  
                else:
                    i+=1
#            print(x[indexLeft])
#            print(x[indexRight])
            restrictedX=[x[item] for item in range(indexLeft,indexRight,1)]
            restrictedY=[y[item] for item in range(indexLeft,indexRight,1)]
            restrictedBase=[base[item] for item in range(indexLeft,indexRight,1)]
            plt.plot(restrictedX, restrictedY)
#            print('')
            #calculate area
#            f = interp1d(restrictedX, np.array(restrictedY)-np.array(restrictedBase), kind='cubic')
#            plt.plot(restrictedX, f(restrictedX))
#            f2 = lambda x0: f(x0)
#            peakarea = integrate.quad(f2,restrictedX[0],restrictedX[-1])[0]
#            print(peakarea)
            
            peakarea=np.trapz(np.array(restrictedY)-np.array(restrictedBase),dx=1)
#            print(peakarea)

            #normalize area
            
            PL_area_norm = peakarea * (10**OD) * (150 / LaserPower) * (1000 / Int_Time)
            
            print('PL_area_norm: ',PL_area_norm)
        else:
            PL_area_norm=0
            print('no peak')
        plt.show()
        #export control graphs with overlay baseline lines and area taken
        
        DATA[samplenumber][filetype]={'LaserPower':LaserPower, 'type': filetype, 'Int_Time':Int_Time, 'OD': OD, 'wave': x, 
            'intensity': y, 'baseline': base, 'peakarea': peakarea, 'PL_area_norm': PL_area_norm}

    #calculate PLQE with Richard Friend's formula
    
    print('')
    for key in list(DATA.keys()):
        for key1 in list(DATA[key].keys()):
#            print(key1)
            if key1=='laserPLemptysphere':
                L_a = DATA[key][key1]['PL_area_norm']
            elif key1=='laserPLoffsample':
                L_b = DATA[key][key1]['PL_area_norm']
            elif key1=='laserPLonsample':
                L_c = DATA[key][key1]['PL_area_norm']
            elif key1=='samplePLon':
                P_c = DATA[key][key1]['PL_area_norm']
            elif key1=='samplePLoff':
                P_b = DATA[key][key1]['PL_area_norm']
        
        A = 1 - L_c / L_b
        ext_PLQE = (P_c - (1 - A) * P_b) / (L_a * A)
        print('PLQE: ',ext_PLQE*100,'%')


























