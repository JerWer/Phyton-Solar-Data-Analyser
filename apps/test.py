#! python3

import os
from tkinter import filedialog
import csv
import math
from tkinter import Tk, messagebox
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from scipy import integrate
from scipy.interpolate import interp1d
import peakutils
from peakutils.plot import plot as pplot
import xlsxwriter
import xlrd
from matplotlib import colors as mcolors

#def listofpeakinfo(x,y,indexes,samplename):#x and y are np.arrays
#
#    peakdata=[]
#    try:
#        plt.clear()
#    except:
#        pass
#    plt.figure(figsize=(10,6))
#    plt.plot(x,y,'black',label=samplename)
#    
#    
#    for item in range(len(indexes)):
#        nbofpoints=80#on each side of max position
#        while(1):
#            try:
#                x0=x[indexes[item]-nbofpoints:indexes[item]+nbofpoints]
#                y0=y[indexes[item]-nbofpoints:indexes[item]+nbofpoints]
#                base=list(peakutils.baseline(y0,1))
#                #baseline height
#                bhleft=np.mean(y0[:20])
#                bhright=np.mean(y0[-20:])
##                baselineheightatmaxpeak=(bhleft+bhright)/2
#                baselineheightatmaxpeak=base[nbofpoints]
#                
#                if abs(bhleft-bhright)<100:#arbitrary choice of criteria...
#                    #find FWHM
#                    d=y0-((max(y0)-bhright)/2)
#                    ind=np.where(d>bhright)[0]
#                    
#                    hl=(x0[ind[0]-1]*y0[ind[0]]-y0[ind[0]-1]*x0[ind[0]])/(x0[ind[0]-1]-x0[ind[0]])
#                    ml=(y0[ind[0]-1]-hl)/x0[ind[0]-1]
#                    yfwhm=((max(y0)-baselineheightatmaxpeak)/2)+baselineheightatmaxpeak
#                    xleftfwhm=(yfwhm - hl)/ml
#                    hr=(x0[ind[-1]]*y0[ind[-1]+1]-y0[ind[-1]]*x0[ind[-1]+1])/(x0[ind[-1]]-x0[ind[-1]+1])
#                    mr=(y0[ind[-1]]-hr)/x0[ind[-1]]
#                    xrightfwhm=(yfwhm - hr)/mr
#                    
#                    FWHM=abs(xrightfwhm-xleftfwhm)
#                    Peakheight=max(y0)-baselineheightatmaxpeak
#                    center=x[indexes[item]]
#                    
#                    
#                    plt.plot(x0, y0, 'red')
##                    plt.plot([x0[0],x0[-1]],[bhleft,bhright],'blue')
#                    plt.plot(x0,base,'blue')
##                    plt.plot(x0,y0,ms=0)
#                    plt.plot([xleftfwhm,xrightfwhm],[yfwhm,yfwhm],'green')
#                    plt.text(center,max(y0)+200,str('%.1f' % float(center)),rotation=90,verticalalignment='bottom',horizontalalignment='center',multialignment='center')
##                    nbpoints=50
##                    plt.plot(x[indexes[item]-nbpoints:indexes[item]+nbpoints],peakutils.baseline(y[indexes[item]-nbpoints:indexes[item]+nbpoints],1),'blue')
#                    
#                    peakdata.append([center,FWHM,Peakheight])
##                    peakdata.append([center,Peakheight])
#                    break
#                else:
#                    if nbofpoints>=15:
#                        nbofpoints-=10
#                    else:
#                        print("indexerror unsolvable")
#                        break
#            except IndexError:
#                if nbofpoints>=15:
#                    nbofpoints-=10
#                else:
#                    print("indexerror unsolvable")
#                    break
#    plt.scatter(x[indexes],y[indexes],c='red',s=12)
#    plt.legend()
#    plt.ylabel("Intensity (a.u.)")
#    plt.xlabel("2\u0398 (degree)")
##    plt.savefig(samplename+'.pdf')
#    plt.show()
##    plt.close()
#    return peakdata
#
#
#
#file_path =filedialog.askopenfilenames(title="Please select the XRD files")
##select a result folder
#
#current_path=os.path.dirname(os.path.dirname(file_path[0]))
##    print(current_path)
##folderName = filedialog.askdirectory(title = "choose a folder to export the auto-analysis results", initialdir=current_path)
#os.chdir(current_path)
#
#DATA=[]
###analyze and create data list
###export graphs on-the-fly
##
##for filename in file_path:
##    filetoread = open(filename,"r", encoding='ISO-8859-1')
##    filerawdata = filetoread.readlines()
##    samplename=os.path.splitext(os.path.basename(filename))[0]
##
##    x=[]
##    y=[]
##        
##    i=0
##    for j in range(len(filerawdata)):
##        if ',' in filerawdata[j]:
##            x.append(float(filerawdata[j].split(',')[0]))
##            y.append(float(filerawdata[j].split(',')[1]))  
##        else:
##            x=np.array(x)
##            y=np.array(y)
###            threshold=0.01
###            MinDist=50
###            while(1):
###                indexes = peakutils.indexes(y, thres=threshold, min_dist=MinDist)
###        #        print(len(indexes))
###                if len(indexes)<15:
###                    break
###                else:
###                    threshold+=0.01
###            
###            dat=listofpeakinfo(x,y,indexes,samplename)
###            
###            DATA.append([str(samplename)+str(i),x,y])#[samplename,X,Y,[[center,FWHM,Peakheight],[]...],maxpeakheight]
##
##            
##            plt.figure(figsize=(10,6))
##            plt.plot(x,y,'black',label=samplename)  
##            plt.scatter(x,peakutils.baseline(y,7),c='red',s=5) 
###            plt.scatter(x,peakutils.baseline(y,7),c='blue',s=5)
###            plt.scatter(x,peakutils.baseline(y,8),c='green',s=5)
##              
##            i+=1
##            x=[]
##            y=[]            
##            
#lambdaXRD=1.54
#
#def q_to_tth(Q):
#    "convert q to tth, lam is wavelength in angstrom"
#    return 360/np.pi * np.arcsin(Q * lambdaXRD / (4 * np.pi))
#
#def tth_to_q(tth):
#    "convert tth to q, lam is wavelength in angstrom"
#    return 4 * np.pi * np.sin(tth * np.pi/(2 * 180)) / lambdaXRD    
#
#for filename in file_path:
#    filetoread = open(filename,"r", encoding='ISO-8859-1')
#    filerawdata = list(filetoread.readlines())
#    samplename=os.path.splitext(os.path.basename(filename))[0]
#
##    filedat=[]
##    for j in range(len(filerawdata)):
##        filedat.append(str(q_to_tth(float(filerawdata[j].split(',')[0])))+'\t'+filerawdata[j].split(',')[1])
##        
##    file = open(samplename+".txt",'w', encoding='ISO-8859-1')
##    file.writelines("%s" % item for item in filedat)
##    file.close() 
#    
#    x=[]
#    y=[]
#    for j in range(len(filerawdata)):
#        x.append(q_to_tth(float(filerawdata[j].split(',')[0])))
#        y.append(float(filerawdata[j].split(',')[1]))  
#    x=np.array(x)
#    y=np.array(y)
#    threshold=0.01
#    MinDist=50
#    while(1):
#        indexes = peakutils.indexes(y, thres=threshold, min_dist=MinDist)
##        print(len(indexes))
#        if len(indexes)<15:
#            break
#        else:
#            threshold+=0.01
#    
##    dat=listofpeakinfo(x,y,indexes,samplename)
#    dat2=[x[indexes],y[indexes]]
##    print(len(dat2[0]))
#            
##    dat2=list(map(list, zip(*dat)))
#    
#    y=[1000*(m-min(dat2[1]))/(max(dat2[1])-min(dat2[1])) for m in dat2[1]]#rescale between 0 and 1000
#
##    print(len(y))
#    filedat=[]
#    for j in range(len(dat2[0])):
#        filedat.append(str(dat2[0][j])+'\t'+str(y[j])+'\n')
#        
#    file = open('RohitJACS_'+samplename+".txt",'w', encoding='ISO-8859-1')
#    file.writelines("%s" % item for item in filedat)
#    file.close()     
#    
#
#
#"""
#need to make autoanalysis of peaks
#get position and intensities
#normalize to 1000
#export list of peaks for ref
#
#"""
#
#
#
#
#
#
#
#
#
#
##!python
#import numpy as np
#from math import factorial
#
#def savitzky_golay(y, window_size, order, deriv=0, rate=1):
#    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
#    The Savitzky-Golay filter removes high frequency noise from data.
#    It has the advantage of preserving the original shape and
#    features of the signal better than other types of filtering
#    approaches, such as moving averages techniques.
#    Parameters
#    ----------
#    y : array_like, shape (N,)
#        the values of the time history of the signal.
#    window_size : int
#        the length of the window. Must be an odd integer number.
#    order : int
#        the order of the polynomial used in the filtering.
#        Must be less then `window_size` - 1.
#    deriv: int
#        the order of the derivative to compute (default = 0 means only smoothing)
#    Returns
#    -------
#    ys : ndarray, shape (N)
#        the smoothed signal (or it's n-th derivative).
#    Notes
#    -----
#    The Savitzky-Golay is a type of low-pass filter, particularly
#    suited for smoothing noisy data. The main idea behind this
#    approach is to make for each point a least-square fit with a
#    polynomial of high order over a odd-sized window centered at
#    the point.
#    Examples
#    --------
#    t = np.linspace(-4, 4, 500)
#    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
#    ysg = savitzky_golay(y, window_size=31, order=4)
#    import matplotlib.pyplot as plt
#    plt.plot(t, y, label='Noisy signal')
#    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
#    plt.plot(t, ysg, 'r', label='Filtered signal')
#    plt.legend()
#    plt.show()
#    References
#    ----------
#    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
#       Data by Simplified Least Squares Procedures. Analytical
#       Chemistry, 1964, 36 (8), pp 1627-1639.
#    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
#       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
#       Cambridge University Press ISBN-13: 9780521880688
#    """
#    
#
#    try:
#        window_size = np.abs(np.int(window_size))
#        order = np.abs(np.int(order))
#    except ValueError:
#        raise ValueError("window_size and order have to be of type int")
#    if window_size % 2 != 1 or window_size < 1:
#        raise TypeError("window_size size must be a positive odd number")
#    if window_size < order + 2:
#        raise TypeError("window_size is too small for the polynomials order")
#    order_range = range(order+1)
#    half_window = (window_size -1) // 2
#    # precompute coefficients
#    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
#    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
#    # pad the signal at the extremes with
#    # values taken from the signal itself
#    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
#    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
#    y = np.concatenate((firstvals, y, lastvals))
#    return np.convolve( m[::-1], y, mode='valid')
#
#t = np.linspace(-4, 4, 500)
#y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
#ysg = savitzky_golay(y, window_size=31, order=4)
#import matplotlib.pyplot as plt
#plt.plot(t, y, label='Noisy signal')
#plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
#plt.plot(t, ysg, 'r', label='Filtered signal')
#plt.legend()
#plt.show()

#
#import matplotlib.pyplot as plt
#import numpy as np
#
#x = np.arange(0.0, 2, 0.01)
#y1 = np.sin(2 * np.pi * x)
#y2 = 1.2 * np.sin(4 * np.pi * x)
#fig=plt.figure()
#ax1=fig.add_subplot(111)
##fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
#
#ax1.fill_between(x, 0, y1)
#ax1.set_ylabel('between y1 and 0')
#
#ax1.fill_between(x, y1, 1)
#ax1.set_ylabel('between y1 and 1')
##
##ax3.fill_between(x, y1, y2)
##ax3.set_ylabel('between y1 and y2')
##ax3.set_xlabel('x')

#import webcolors
#
#def closest_colour(requested_colour):
#    min_colours = {}
#    for key, name in webcolors.css3_hex_to_names.items():
#        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
#        rd = (r_c - requested_colour[0]) ** 2
#        gd = (g_c - requested_colour[1]) ** 2
#        bd = (b_c - requested_colour[2]) ** 2
#        min_colours[(rd + gd + bd)] = name
#    return min_colours[min(min_colours.keys())]
#
#def get_colour_name(requested_colour):
#    try:
#        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
#    except ValueError:
#        closest_name = closest_colour(requested_colour)
#        actual_name = None
#    return actual_name, closest_name
#
#requested_colour = (1, 0, 0)
#actual_name, closest_name = get_colour_name(requested_colour)
#
#print("Actual colour name:", actual_name, ", closest colour name:", closest_name)



#plt.hist([[1,1,4,5,6,6,6,8,8,8,8],[2,2,2,3,3,7,7]],bins=5, alpha=0.6, histtype= 'barstacked', range=[0,10], density=False, cumulative=False, edgecolor='black', linewidth=1.2, color=['red','blue'], label=["one", 'two'])
#plt.xlabel('Efficiency')
#plt.ylabel('counts')
#plt.legend()
#plt.show()


a=[1,1,1]
b=[[2],[2],[2],[2]]

c=[a]+b
print(c)

