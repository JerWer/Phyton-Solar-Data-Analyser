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


"""




- export txt files with data of graphs


"""

def PLSummary():
    ready=0
    j=0
    while j<2:
        try: 
            file_path_csv =filedialog.askopenfilenames(title="Please select the PL files")
            if file_path_csv!='':
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
        #treat single measurements
        #get the data in dictionaries
        DATA={}
        for i in range(len(file_path_csv)):
            filename=os.path.split(file_path_csv[i])[-1]
            if 'time' not in filename:
                samplename=filename.split('_')[0]+'_'+filename.split('_')[1]
                if samplename not in DATA.keys():
                    DATA[samplename]={}
                position=filename.split('_')[2]
                if position not in DATA[samplename].keys():
                    DATA[samplename][position]={}
                laserintensity=filename.split('_')[3]+'_'+filename.split('_')[4]
                if laserintensity not in DATA[samplename][position].keys():
                    DATA[samplename][position][laserintensity]=[[],[]]
                txtfile=["Wavelength"+"\t"+"Intensity"+"\n","nm"+ "\t"+ "-"+"\n"," \t"+samplename+'-'+position+'-'+laserintensity+"\n"," \t \n"]
                with open(file_path_csv[i]) as csvfile:
                    readCSV = csv.reader(csvfile, delimiter='\t')        
                    
                    for row in readCSV:
        #                print(row)
                        if row!=[]:
                            if '#' not in row[0]:
                                DATA[samplename][position][laserintensity][0].append(float(row[0]))
                                DATA[samplename][position][laserintensity][1].append(float(row[1]))
                                txtfile.append(str('%.3f' % float(row[0]))+'\t'+row[1]+"\n")
                    file = open(samplename+'-'+position+'-'+laserintensity+'.txt','w', encoding='ISO-8859-1')
                    file.writelines("%s" % item for item in txtfile)
                    file.close()        
        #sort, plot and export
        
        for key in DATA.keys():
            fignames=[]
            for key2 in DATA[key].keys():
                for key3 in DATA[key][key2].keys():
                    plt.plot(DATA[key][key2][key3][0],DATA[key][key2][key3][1],label=key3)
                plt.xlabel('Wavelength (nm)')
                plt.ylabel('PL intensity (-)')
                plt.title(key+'_'+key2)
                plt.legend()
                plt.savefig(key+'_'+key2+'.png',dpi=300)
                fignames.append(key+'_'+key2+'.png')
                plt.close()
#            images = list(map(ImageTk.open, fignames))
#            widths, heights = zip(*(i.size for i in images))
#            total_width = max(widths)
#            max_height = sum(heights)
#            new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
#            new_im.paste(im=images[0],box=(0,0))
#            new_im.paste(im=images[1],box=(0,heights[0]))
#            new_im.save(key+'.png')
#            for item in fignames:   
#                os.remove(item)
            plt.close("all")
        for key in DATA.keys():
            for key2 in DATA[key].keys():
                for key3 in DATA[key][key2].keys():
                    plt.plot(DATA[key][key2][key3][0],DATA[key][key2][key3][1],label=key2+'_'+key3)
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('PL intensity (-)')
            plt.title(key)
            plt.legend(loc='lower right', bbox_to_anchor=(1.2, 0.5))
            plt.savefig(key+'.png',dpi=300)
            plt.close()
        plt.close("all")    
        
        
        
        #treat time measurements
        DATA={}
        totaltimedict={}
        for i in range(len(file_path_csv)):
            filename=os.path.split(file_path_csv[i])[-1]
            if 'time' in filename:
                samplename=filename.split('_')[0]+'_'+filename.split('_')[1]+'_'+filename.split('_')[2]
                if samplename not in DATA.keys():
                    DATA[samplename]={}
                    totaltimedict[samplename]={}
                timenumb=filename.split('_')[3]
                if timenumb not in DATA[samplename].keys():
                    DATA[samplename][timenumb]={}
                    totaltimedict[samplename][timenumb]={}
                position=filename.split('_')[5]
                if position not in DATA[samplename][timenumb].keys():
                    DATA[samplename][timenumb][position]=[[],[]]
                    totaltimedict[samplename][timenumb][position]=0
                with open(file_path_csv[i]) as csvfile:
                    readCSV = list(csv.reader(csvfile, delimiter='\t')) 
                    for row in range(len(readCSV)):
                        if readCSV[row]!=[]:
#                            print(row)
                            if '#Cycles=' in readCSV[row][0]:
#                                print(float(row[0][8:]))
                                totaltimedict[samplename][timenumb][position]=readCSV[row][0][8:]+' x '+readCSV[row+1][0][13:]+' = '+ str(float(readCSV[row][0][8:])*float(readCSV[row+1][0][13:]))+' seconds'
                            if '#' not in readCSV[row][0]:
                                DATA[samplename][timenumb][position][0].append(float(readCSV[row][0]))
                                DATA[samplename][timenumb][position][1].append(float(readCSV[row][1]))
        
        heightposition={}
        for key in DATA.keys():
            for key3 in DATA[key].keys():
#                print(key3)
#                print(list(DATA[key][key3].keys()))
                sortedlistofkeys=sorted(list(DATA[key][key3].keys()))
#                print(sortedlistofkeys)
                num_plots = len(sortedlistofkeys)
#                print(sortedlistofkeys)
#                colormap = plt.cm.gist_ncar
                plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.Spectral(np.linspace(0, 1, num_plots))))
                minX=0
                maxY=0
                height=[]
                positions=[]
                
                for key2 in sortedlistofkeys:
                    if key2==sortedlistofkeys[0]:   
                        minX=min(DATA[key][key3][key2][0]) 
                        maxY=max(DATA[key][key3][key2][1])
                        plt.plot(DATA[key][key3][key2][0],DATA[key][key3][key2][1],label='start')
                    elif key2==sortedlistofkeys[-1]:
                        plt.plot(DATA[key][key3][key2][0],DATA[key][key3][key2][1],label='end')
                        tottime=totaltimedict[key][key3][key2]
                        print(tottime)
                    else:
                        plt.plot(DATA[key][key3][key2][0],DATA[key][key3][key2][1])
                    if min(DATA[key][key3][key2][0])<minX:
                        minX=min(DATA[key][key3][key2][0])
                    if max(DATA[key][key3][key2][1])>maxY:
                        maxY=max(DATA[key][key3][key2][1])
                    
                    height.append(max(DATA[key][key3][key2][1]))
                    positions.append(DATA[key][key3][key2][0][DATA[key][key3][key2][1].index(max(DATA[key][key3][key2][1]))])
                
                
                    
                plt.text(minX,maxY,tottime, fontsize=8)      
                plt.xlabel('Wavelength (nm)')
                plt.ylabel('PL intensity (-)')
                plt.title(key+key3+'_time')
                plt.legend(loc='lower right')
                plt.savefig(key+key3+'_time.png',dpi=300)
                plt.close()
                
                numbpoints=len(height)
                
                x=range(0,numbpoints*int(float(tottime.split(' ')[2])),int(float(tottime.split(' ')[2])))
                heightposition[key+key3]=[x,height,positions]
                plt.plot(x,height)
                plt.xlabel('Time (s)')
                plt.ylabel('PL intensity (-)')
                plt.savefig(key+key3+'_timeHeight.png',dpi=300)
                plt.close()
                plt.plot(x,positions)
                plt.xlabel('Time (s)')
                plt.ylabel('Wavelength (nm)')
                plt.title(key+key3+'_timePositions')
                plt.savefig(key+key3+'_timePositions.png',dpi=300)
                plt.close()
                
        num_plots=len(list(heightposition.keys()))
        plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.tab20(np.linspace(0, 1, num_plots))))
        for key in heightposition.keys():
            y=[1+(heightposition[key][1][i]-heightposition[key][1][0])/heightposition[key][1][0] for i in range(len(heightposition[key][1]))]
            plt.plot(heightposition[key][0],y,label=key)
        plt.xlabel('time (s)')
        plt.ylabel('PL intensity (-)')
        plt.legend(loc='lower left', bbox_to_anchor=(1, 0))
#        extent = plt.get_window_extent().transformed(plt.dpi_scale_trans.inverted())
        plt.savefig('PeakHeightEvolution.png',dpi=300,bbox_inches='tight', pad_inches=0.1)
        plt.close()  
        num_plots=len(list(heightposition.keys()))
        plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.tab20(np.linspace(0, 1, num_plots))))
        for key in heightposition.keys():
            y=[1+(heightposition[key][2][i]-heightposition[key][2][0])/heightposition[key][2][0] for i in range(len(heightposition[key][2]))]
            plt.plot(heightposition[key][0],y,label=key)
        plt.xlabel('time (s)')
        plt.ylabel('Peak position (nm)')
        plt.legend(loc='lower left', bbox_to_anchor=(1, 0))
#        extent = plt.get_window_extent().transformed(plt.dpi_scale_trans.inverted())
        plt.savefig('PeakPositionEvolution.png',dpi=300,bbox_inches='tight', pad_inches=0.1)
        plt.close() 


        #export txt file with all time data 
        
        
###############################################################################        
if __name__ == '__main__':
    PLSummary()        
        
        
        
        
        
        
        
        
        
        
        
        
