#! python3

import os
from tkinter import filedialog
import csv
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from scipy import integrate
from scipy.interpolate import interp1d, UnivariateSpline
import peakutils
from peakutils.plot import plot as pplot
from PIL import Image as ImageTk
from scipy import signal, integrate
from scipy.signal import chirp, find_peaks, peak_widths
from scipy import stats
from statistics import mean
"""


"""

def extract_jv_params(jv):#function originally written by Rohit Prasana (adapted by JW)
        '''
        Extract Voc, Jsc, FF, Pmax from a given JV curve
            * Assume given JV curve is in volts and mA/cm2
        '''
        resample_step_size = 0.00001 # Voltage step size to use while resampling JV curve to find Pmax
        
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


#load files
ready=0
j=0
while j<2:
    try: 
        file_paths =filedialog.askopenfilenames(title="Please select the SPA files")
        filetypes=[os.path.splitext(item)[1] for item in file_paths]
        filetype=list(set(filetypes))[0]
        if filetype==".txt":
            ready=1 
            directory = filedialog.askdirectory(title="Where saving?")
                
            if not os.path.exists(directory):
                os.makedirs(directory)
                os.chdir(directory)
            else :
                os.chdir(directory)
            break
        else:
            print("Please select correct PL files")
            j+=1
    except:
        print("no file selected")
        j+=1
        
if ready:
    DATA={}#{sample1: {Reverse:{TimesSec:[],datetimes:[],voltagelists:[[],[],...],currentlists:[[],[]...],Voc:[],Jsc:[],FF:[],Power:[]},Forward:{}},sample2:{...}}
    for i in range(len(file_paths)):

        filename=os.path.split(file_paths[i])[-1]
#        print(filename)
        #samplenumber
        samplenumber=filename.split(' ')[0]
#        print(samplenumber)
        
        if samplenumber not in list(DATA.keys()):
            print(samplenumber)
            DATA[samplenumber]={'TimesSec':[],'date':[], 'times':[],'Reverse':{'voltagelists':[],'currentlists':[],'Voc':[],'Jsc':[],'FF':[],'Power':[]},'Forward':{'voltagelists':[],'currentlists':[],'Voc':[],'Jsc':[],'FF':[],'Power':[]}}
            
        filetoread = open(file_paths[i],"r", encoding='ISO-8859-1')
        filerawdata = list(filetoread.readlines())
    
        #extract  time in seconds, line 2
        
        DATA[samplenumber]['TimesSec'].append(float(filerawdata[2].split(' ')[4]))
#            print(timeSec)

        #extract date/time: line 12
        DATA[samplenumber]['date'].append(filerawdata[12].split(' ')[1].split(':')[1])
#            print(date)
        DATA[samplenumber]['times'].append(filerawdata[12].split(' ')[2])
#            print(time)
        
        #extract number of points, npts
        for row in filerawdata:
            if 'Sweep Number of Points' in row:
                npts=int(float(row.split(':')[1]))
#                    print(npts)
                break

        #extract JVdata: line 14, put all in one list
        #then Forw is first npts, Rev is last npts
        
        forwV=[]
        forwI=[]
        revV=[]
        revI=[]
        for item in range(14,14+npts):
            forwV.append(-float(filerawdata[item].split('\t')[0]))
            forwI.append(1000*float(filerawdata[item].split('\t')[1]))#to mA
        for item in range(14+npts-1,14+2*npts-1):
            revV.append(-float(filerawdata[item].split('\t')[0]))
            revI.append(1000*float(filerawdata[item].split('\t')[1]))#to mA

        #calculate JV parameters from those lists
        
        JVparamForw=extract_jv_params([forwV,forwI])
#        print(JVparamForw)
        JVparamRev=extract_jv_params([revV,revI])
#        print(JVparamRev)
        
        DATA[samplenumber]['Reverse']['voltagelists'].append(revV)
        DATA[samplenumber]['Reverse']['currentlists'].append(revI)
        DATA[samplenumber]['Reverse']['Voc'].append(JVparamRev['Voc'])
        DATA[samplenumber]['Reverse']['Jsc'].append(JVparamRev['Jsc'])
        DATA[samplenumber]['Reverse']['FF'].append(JVparamRev['FF'])
        DATA[samplenumber]['Reverse']['Power'].append(JVparamRev['Pmax'])
        DATA[samplenumber]['Forward']['voltagelists'].append(forwV)
        DATA[samplenumber]['Forward']['currentlists'].append(forwI)
        DATA[samplenumber]['Forward']['Voc'].append(JVparamForw['Voc'])
        DATA[samplenumber]['Forward']['Jsc'].append(JVparamForw['Jsc'])
        DATA[samplenumber]['Forward']['FF'].append(JVparamForw['FF'])
        DATA[samplenumber]['Forward']['Power'].append(JVparamForw['Pmax'])

#export graphs over time of JVparam, for each samplename
#export graph of JVcurves over time for each samplename
samplenames=list(DATA.keys())

for sample in samplenames:
    fig = plt.figure(figsize=(15, 10))
    Vocsubfig=fig.add_subplot(221)
    Jscsubfig=fig.add_subplot(222)
    FFsubfig=fig.add_subplot(223)
    Effsubfig=fig.add_subplot(224)
    
    listsfortxtexport=[]
    
    x=[(item-min(DATA[sample]['TimesSec']))/3600 for item in DATA[sample]['TimesSec']]
    listsfortxtexport.append(x)
    y1=[item/DATA[sample]['Reverse']['Voc'][0] for item in DATA[sample]['Reverse']['Voc']]
    listsfortxtexport.append(y1)
    Vocsubfig.plot(x,y1,color='black', label=sample+'_Reverse')
    y2=[item/DATA[sample]['Forward']['Voc'][0] for item in DATA[sample]['Forward']['Voc']]
    listsfortxtexport.append(y2)
    Vocsubfig.plot(x,y2,color='grey', label=sample+'_Forward')
    Vocsubfig.axis([min(x),max(x),0,max(y1+y2)])
    Vocsubfig.axhline(y=0.8,color='r')
    Vocsubfig.legend()
    Vocsubfig.set_xlabel('Time (hrs)')
    Vocsubfig.set_ylabel('Normalized Voc')

#    x=[(item-min(DATA[sample]['TimesSec']))/3600 for item in DATA[sample]['TimesSec']]
    y1=[item/DATA[sample]['Reverse']['Jsc'][0] for item in DATA[sample]['Reverse']['Jsc']]
    listsfortxtexport.append(y1)
    Jscsubfig.plot(x,y1,color='black', label=sample+'_Reverse')
    y2=[item/DATA[sample]['Forward']['Jsc'][0] for item in DATA[sample]['Forward']['Jsc']]
    listsfortxtexport.append(y2)
    Jscsubfig.plot(x,y2,color='grey', label=sample+'_Forward')
    Jscsubfig.axis([min(x),max(x),0,max(y1+y2)])
    Jscsubfig.axhline(y=0.8,color='r')
    Jscsubfig.legend()
    Jscsubfig.set_xlabel('Time (hrs)')
    Jscsubfig.set_ylabel('Normalized Jsc')
    
#    x=[(item-min(DATA[sample]['TimesSec']))/3600 for item in DATA[sample]['TimesSec']]
    y1=[item/DATA[sample]['Reverse']['FF'][0] for item in DATA[sample]['Reverse']['FF']]
    listsfortxtexport.append(y1)
    FFsubfig.plot(x,y1,color='black', label=sample+'_Reverse')
    y2=[item/DATA[sample]['Forward']['FF'][0] for item in DATA[sample]['Forward']['FF']]
    listsfortxtexport.append(y2)
    FFsubfig.plot(x,y2,color='grey', label=sample+'_Forward')
    FFsubfig.axis([min(x),max(x),0,max(y1+y2)])
    FFsubfig.axhline(y=0.8,color='r')
    FFsubfig.legend()
    FFsubfig.set_xlabel('Time (hrs)')
    FFsubfig.set_ylabel('Normalized FF')
    
#    x=[(item-min(DATA[sample]['TimesSec']))/3600 for item in DATA[sample]['TimesSec']]
    y1=[item/DATA[sample]['Reverse']['Power'][0] for item in DATA[sample]['Reverse']['Power']]
    listsfortxtexport.append(y1)
    Effsubfig.plot(x,y1,color='black', label=sample+'_Reverse')
    y2=[item/DATA[sample]['Forward']['Power'][0] for item in DATA[sample]['Forward']['Power']]
    listsfortxtexport.append(y2)
    Effsubfig.plot(x,y2,color='grey', label=sample+'_Forward')
    Effsubfig.axis([min(x),max(x),0,max(y1+y2)])
    Effsubfig.axhline(y=0.8,color='r')
    Effsubfig.legend()
    Effsubfig.set_xlabel('Time (hrs)')
    Effsubfig.set_ylabel('Normalized Power')
    
    
    fig.savefig(sample+'.png')
    plt.close()
    #export text files with all data: timeSecNormalized, Voc, Jsc, FF, Power
    
    DATAtoexport=['Time\tVocRev\tVocFor\tJscRev\tJscFor\tFFRev\tFFFor\tPowerRev\tPowerFor\n']
    for item in zip(*listsfortxtexport):
        line=""
        for item1 in item:
            line=line+str(item1)+"\t"
        line=line[:-1]+"\n"
        DATAtoexport.append(line)
    
    file = open(sample+"JVparamdat.txt",'w', encoding='ISO-8859-1')
    file.writelines("%s" % item for item in DATAtoexport)
    file.close()

    
    
    #export JV curves in graph
    colormapname="jet"
    cmap = plt.get_cmap(colormapname)
    colors = cmap(np.linspace(0, 1.0, len(DATA[sample]['Reverse']['voltagelists'])))
    colors=[tuple(item) for item in colors]
    
    fig = plt.figure(figsize=(20, 10))
    reversefig=fig.add_subplot(121)
    forwardfig=fig.add_subplot(122)
    xminRev=0
    xmaxRev=0
    ymaxRev=0
    xminFor=0
    xmaxFor=0
    ymaxFor=0
    for i in range(len(DATA[sample]['Reverse']['voltagelists'])):
        if min(DATA[sample]['Reverse']['voltagelists'][i])<xminRev:
            xminRev=min(DATA[sample]['Reverse']['voltagelists'][i])
        if max(DATA[sample]['Reverse']['voltagelists'][i])>xmaxRev:
            xmaxRev=max(DATA[sample]['Reverse']['voltagelists'][i])
        if min(DATA[sample]['Forward']['voltagelists'][i])<xminFor:
            xminFor=min(DATA[sample]['Forward']['voltagelists'][i])
        if max(DATA[sample]['Forward']['voltagelists'][i])>xmaxFor:
            xmaxFor=max(DATA[sample]['Forward']['voltagelists'][i])
        if max(DATA[sample]['Forward']['currentlists'][i])>ymaxFor:
            ymaxFor=max(DATA[sample]['Forward']['currentlists'][i])   
        if max(DATA[sample]['Reverse']['currentlists'][i])>ymaxRev:
            ymaxRev=max(DATA[sample]['Reverse']['currentlists'][i]) 
        reversefig.plot(DATA[sample]['Reverse']['voltagelists'][i],DATA[sample]['Reverse']['currentlists'][i],color=colors[i])
        forwardfig.plot(DATA[sample]['Forward']['voltagelists'][i],DATA[sample]['Forward']['currentlists'][i],color=colors[i])
    
    reversefig.set_xlabel('Voltage')
    reversefig.set_ylabel('Current')
    forwardfig.set_xlabel('Voltage')
    forwardfig.set_ylabel('Current')
    forwardfig.axhline(y=0,color='k')
    reversefig.axhline(y=0,color='k')
    forwardfig.axvline(x=0,color='k')
    reversefig.axvline(x=0,color='k')
    forwardfig.set_title('Forward scans')
    reversefig.set_title('Reverse scans')
    reversefig.axis([xminRev,xmaxRev,-1,ymaxRev])
    forwardfig.axis([xminFor,xmaxFor,-1,ymaxFor])
    
    fig.savefig(sample+'_JV.png')
    
    plt.close()
    
    #export JV curves data, with time in headline
    
    
    
    
    