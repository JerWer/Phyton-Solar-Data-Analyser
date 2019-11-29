#! python3


import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
#import panda as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable

	
#data = np.random.rand(4, 6)
#print(data)
#heat_map = sb.heatmap(data, cmap='Greys',vmin=0, vmax=2)
#	
#plt.show()


#x,y,z = np.loadtxt('C:\\Users\\jwerner\\Documents\\DATA\\interferometer Profilo\\191120-taylor-PbSn\\DEE_Anneal_p3.asc',skiprows =116, delimiter="\t", usecols=(0,1,2),unpack=True)

#print(x)
#data = pd.DataFrame(data={'x':x, 'y':y, 'z':z})
#data = data.pivot(index='x', columns='y', values='z')
#sb.heatmap(data)
#plt.show()

filetoread = open('C:\\Users\\jwerner\\Documents\\DATA\\interferometer Profilo\\191120-taylor-PbSn\\NoAnti_Anneal_p4.asc',"r", encoding='ISO-8859-1')
filerawdata = list(filetoread.readlines())
x=[]
y=[]
z=[]
data=[]
for i in range(116,len(filerawdata)):
    if 'Intensity' in filerawdata[i].split('\t')[0]:
        break
    else:
        x.append(float(filerawdata[i].split('\t')[0]))
        y.append(float(filerawdata[i].split('\t')[1]))
        if filerawdata[i].split('\t')[2] !='\n':
            z.append(0.514*0.163*float(filerawdata[i].split('\t')[2]))
        else:
            z.append(0)
            
#for i in range(116,len(filerawdata)):
#    if 'Intensity' in filerawdata[i].split('\t')[0]:
#        for j in range(i+1,len(filerawdata)):
#            x.append(float(filerawdata[j].split('\t')[0]))
#            y.append(float(filerawdata[j].split('\t')[1]))
#            if filerawdata[j].split('\t')[2] !='\n':
#                z.append(0.163*float(filerawdata[j].split('\t')[2]))
#            else:
#                z.append(0)

x=np.array(x)
y=np.array(y)
z=np.array(z)
zmin=min(z)
zmax=max(z)
print(zmin)
print(zmax)
shape = np.unique(x).shape[0],np.unique(y).shape[0]
x_arr0 = x.reshape(shape)
y_arr0 = y.reshape(shape)
z_arr0 = z.reshape(shape)



filetoread = open('C:\\Users\\jwerner\\Documents\\DATA\\interferometer Profilo\\191120-taylor-PbSn\\DEE_Anneal_p4.asc',"r", encoding='ISO-8859-1')
filerawdata = list(filetoread.readlines())
x=[]
y=[]
z=[]
data=[]
for i in range(116,len(filerawdata)):
    if 'Intensity' in filerawdata[i].split('\t')[0]:
        break
    else:
        x.append(float(filerawdata[i].split('\t')[0]))
        y.append(float(filerawdata[i].split('\t')[1]))
        if filerawdata[i].split('\t')[2] !='\n':
            z.append(0.514*0.163*float(filerawdata[i].split('\t')[2]))
        else:
            z.append(0)
            
#for i in range(116,len(filerawdata)):
#    if 'Intensity' in filerawdata[i].split('\t')[0]:
#        for j in range(i+1,len(filerawdata)):
#            x.append(float(filerawdata[j].split('\t')[0]))
#            y.append(float(filerawdata[j].split('\t')[1]))
#            if filerawdata[j].split('\t')[2] !='\n':
#                z.append(float(filerawdata[j].split('\t')[2]))
#            else:
#                z.append(0)

x=np.array(x)
y=np.array(y)
z=np.array(z)
if min(z)<zmin:
    zmin=min(z)
if max(z)>zmax:
    zmax=max(z)
shape = np.unique(x).shape[0],np.unique(y).shape[0]
x_arr = x.reshape(shape)
y_arr = y.reshape(shape)
z_arr = z.reshape(shape)




filetoread = open('C:\\Users\\jwerner\\Documents\\DATA\\interferometer Profilo\\191120-taylor-PbSn\\N2_Anneal_p3.asc',"r", encoding='ISO-8859-1')
filerawdata = list(filetoread.readlines())
x=[]
y=[]
z=[]
data=[]
for i in range(116,len(filerawdata)):
    if 'Intensity' in filerawdata[i].split('\t')[0]:
        break
    else:
        x.append(float(filerawdata[i].split('\t')[0]))
        y.append(float(filerawdata[i].split('\t')[1]))
        if filerawdata[i].split('\t')[2] !='\n':
            z.append(0.514*0.163*float(filerawdata[i].split('\t')[2]))
        else:
            z.append(0)
            
#for i in range(116,len(filerawdata)):
#    if 'Intensity' in filerawdata[i].split('\t')[0]:
#        for j in range(i+1,len(filerawdata)):
#            x.append(float(filerawdata[j].split('\t')[0]))
#            y.append(float(filerawdata[j].split('\t')[1]))
#            if filerawdata[j].split('\t')[2] !='\n':
#                z.append(float(filerawdata[j].split('\t')[2]))
#            else:
#                z.append(0)

x=np.array(x)
y=np.array(y)
z=np.array(z)
if min(z)<zmin:
    zmin=min(z)
if max(z)>zmax:
    zmax=max(z)
shape = np.unique(x).shape[0],np.unique(y).shape[0]
x_arr1 = x.reshape(shape)
y_arr1 = y.reshape(shape)
z_arr1 = z.reshape(shape)

fig, (ax0,ax,ax1) = plt.subplots(nrows=1, ncols=3,figsize=(18, 23))
#fig, ax0 = plt.subplots(nrows=1, ncols=1,figsize=(10, 10))


im = ax0.pcolormesh(x_arr0,y_arr0,z_arr0,vmin=zmin,vmax=zmax,cmap='Greys')
#divider = make_axes_locatable(ax0)
#cax1 = divider.append_axes("right", size="5%", pad=0.05)
#fig.colorbar(im, cax=cax1)
ax0.set_aspect(aspect=1)
ax0.set_axis_off()
ax0.text(5,85,"Untreated, annealed", fontsize=18, color='white')


im = ax.pcolormesh(x_arr,y_arr,z_arr,vmin=zmin,vmax=zmax,cmap='Greys')
#divider = make_axes_locatable(ax)
#cax1 = divider.append_axes("right", size="5%", pad=0.05)
#fig.colorbar(im, cax=cax1)
ax.set_aspect(aspect=1)
#ax.get_yaxis().set_visible(False)
ax.set_axis_off()
ax.text(5,85,"DEE, annealed", fontsize=18, color='white')


im1 = ax1.pcolormesh(x_arr1,y_arr1,z_arr1,vmin=zmin,vmax=zmax,cmap='Greys')
#divider = make_axes_locatable(ax1)
#cax1 = divider.append_axes("right", size="5%", pad=0.05)
#fig.colorbar(im1, cax=cax1)
ax1.set_aspect(aspect=1)
#ax1.get_yaxis().tick_right()
ax1.set_axis_off()
ax1.text(5,85,"N2, annealed", fontsize=18, color='white')


fig.subplots_adjust(right=0.94,
                    wspace=0.01, hspace=0)
cb_ax = fig.add_axes([0.95, 0.423, 0.01, 0.16])
cbar = fig.colorbar(im, cax=cb_ax)
cb_ax.set_ylabel("Height (um)")


#fig.colorbar(im1, ax=ax1, fraction=0.035)
#plt.tight_layout()
plt.show()

fig.savefig('C:\\Users\\jwerner\\Documents\\DATA\\interferometer Profilo\\191120-taylor-PbSn\\noVSdeeVSn2.tiff', dpi=300) 





#filetoread = open('C:\\Users\\jwerner\\Documents\\DATA\\interferometer Profilo\\dataZach\\IZOMvH50xVSI.asc',"r", encoding='ISO-8859-1')
#filerawdata = list(filetoread.readlines())
#x=[]
#y=[]
#z=[]
#data=[]
#for i in range(140,len(filerawdata)):
#    if 'Intensity' in filerawdata[i].split('\t')[0]:
#        break
#    else:
#        x.append(float(filerawdata[i].split('\t')[0]))
#        y.append(float(filerawdata[i].split('\t')[1]))
#        if filerawdata[i].split('\t')[2] !='\n':
#            z.append(0.163*float(filerawdata[i].split('\t')[2]))
#        else:
#            z.append(0)
#            
##for i in range(116,len(filerawdata)):
##    if 'Intensity' in filerawdata[i].split('\t')[0]:
##        for j in range(i+1,len(filerawdata)):
##            x.append(float(filerawdata[j].split('\t')[0]))
##            y.append(float(filerawdata[j].split('\t')[1]))
##            if filerawdata[j].split('\t')[2] !='\n':
##                z.append(0.163*float(filerawdata[j].split('\t')[2]))
##            else:
##                z.append(0)
#
#x=np.array(x)
#y=np.array(y)
#z=np.array(z)
#zmin=min(z)
#zmax=max(z)
#print(zmin)
#print(zmax)
#shape = np.unique(x).shape[0],np.unique(y).shape[0]
#x_arr0 = x.reshape(shape)
#y_arr0 = y.reshape(shape)
#z_arr0 = z.reshape(shape)
#
#
#fig, ax0 = plt.subplots(nrows=1, ncols=1,figsize=(10, 10))
#im = ax0.pcolormesh(x_arr0,y_arr0,z_arr0,vmin=zmin,vmax=zmax,cmap='Greys')
#divider = make_axes_locatable(ax0)
#cax1 = divider.append_axes("right", size="5%", pad=0.05)
#fig.colorbar(im, cax=cax1)
#ax0.set_aspect(aspect=1)
##ax0.set_axis_off()
#
#
#plt.show()









