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
- make a 2-subfig graph per sample, one for glass, one for ITO
- 3 colors for the intensities

- graph with all samples of same conditions: e.g. all glass-0pt4, 
- later put that in gui and selectable
- or table with sortable columns

- dictionaries for sample name, glass-ito, intensities


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
        #get the data in dictionaries
        DATA={}
        for i in range(len(file_path_csv)):
            filename=os.path.split(file_path_csv[i])[-1]
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
            images = list(map(ImageTk.open, fignames))
            widths, heights = zip(*(i.size for i in images))
            total_width = max(widths)
            max_height = sum(heights)
            new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
            new_im.paste(im=images[0],box=(0,0))
            new_im.paste(im=images[1],box=(0,heights[0]))
            new_im.save(key+'.png')
            for item in fignames:   
                os.remove(item)
            plt.close("all")
            
        
###############################################################################        
if __name__ == '__main__':
    PLSummary()        
        
        
        
        
        
        
        
        
        
        
        
        
