#~# This code takes a stack of detector images from a theta rock, and a working ORmatrix from spec file, and generates a reciprocal space volume #~#
#~# Original version written by J.P. Castellan, Argonne, 2011.  Subsequently modified by Castellan and Ruff, for use at CHESS with Pilatus300K   #~#
#~# THIS is the CHESS kludge for 6M data, to test against the mighty ANL discovery engine workflow
## Modified to accept a nexus datastack, calibrated/ corrected via pyFAI, 2020/2021

from PIL import Image
import numpy as np
import ctypes as ct
import os
import sys
import signal
import time
from nexusformat.nexus import *
import hkl
from pylab import *
from scipy import *
import gc

# Import code from anglerock.py
from anglerock import anglerock

#some physical constants
PC=4.13566733e-15 	# planks constant in si
c=2.99792458e8 		# speed of light

workingdir=sys.argv[1]
ormdir=sys.argv[2]
Hlim=float(sys.argv[3])
Hstep=float(sys.argv[4])
Klim=float(sys.argv[5])
Kstep=float(sys.argv[6])
Llim=float(sys.argv[7])
Lstep=float(sys.argv[8])

nxsetmemory(100000)
stack1,stack2,stack3 = sorted([workingdir+f for f in os.listdir(workingdir) if f.startswith("stack")])
# stack1=nxload(workingdir+"stack1.nxs")
# stack2=nxload(workingdir+"stack2.nxs")
# stack3=nxload(workingdir+"stack3.nxs")

#load the orientation info
ormat=nxload(ormdir+"ormatrix_auto.nxs")

#incident energy and wavelength
WL=stack1.geo.wl #wavelength
print('wavelength = ' + str(WL)) 

# Define the hkl space to histogram and define/zero data structures
H=np.arange(-Hlim,Hlim, Hstep)
K=np.arange(-Klim,Klim, Kstep)
L=np.arange(-Llim,Llim, Lstep)


#If file already exists, append 001
file_name = '3rot_hkli.nxs'

suffix = 1
while os.path.exists(workingdir+file_name):
  file_name=file_name[:-4]+"_"+str(suffix)+".nxs"
  suffix+=1
    
outpath=workingdir+file_name

#where to write the nexus file (the output)
nxs_name=file_name[:-4]

print('\nOutput file: ' + str(outpath))

#######################################################
####  End of input parameters                      ####
#######################################################

print('H = ',H)
print('K = ',K)
print('L = ',L)
print("n_bins = " + str(len(H)*len(K)*len(L)))


#create the data storage arrays
data=np.zeros((len(H)*len(K)*len(L)),dtype=np.float32)
norm=np.zeros((len(H)*len(K)*len(L)),dtype=np.float32)
errors=np.zeros((len(H)*len(K)*len(L)),dtype=np.float32)

#ormatric from file
U=ormat.ormatrix.U

#U=reshape(U,(3,3))
U=U.T# To match spec convention??
#U=np.matrix(U)

#process rotation 1
success=False
while not success:
  try:
    print("Processing rotation 1...")
    W2=anglerock(H,K,L,stack1,ormat,WL,U,data,norm,errors,workingdir,1)
    success=True
    print("Stack 1 processed successfully.")

  except MemoryError:
    print("Unable to allocate enough memory! Try closing other programs.")
  except OSError:
    print("Unable to allocate enough memory! Try closing other programs.")
  except Exception as e:
    print(e)

  if not success:
    print("Trying again...")
print("Clearing stack from memory...")
del stack1
gc.collect()
print("Memory cleared.")

#process rotation 2
success=False
while not success:
  try:
    print("Processing rotation 2...")
    W2=anglerock(H,K,L,stack2,ormat,WL,U,data,norm,errors,workingdir,2)
    success=True
    print("Stack 2 processed successfully.")
  except MemoryError:
    print("Unable to allocate enough memory! Try closing other programs.")
  except OSError:
    print("Unable to allocate enough memory! Try closing other programs.")
  except Exception as e:
    print(e)

  if not success:
      print("Trying again...")
print("Clearing stack from memory...")
del stack2
gc.collect()
print("Memory cleared.")


#process rotation 3
success=False
while not success:
  try:
    print("Processing rotation 3...")
    W2=anglerock(H,K,L,stack3,ormat,WL,U,data,norm,errors,workingdir,3)
    success=True
    print("Stack 3 processed successfully.")
  except MemoryError:
    print("Unable to allocate enough memory! Try closing other programs.")
  except OSError:
    print("Unable to allocate enough memory! Try closing other programs.")
  except Exception as e:
    print(e)

  if not success:
    print("Trying again...")
print("Clearing stack from memory...")
del stack3
gc.collect()
print("Memory cleared.")

    
dataout=data.clip(0.0)/norm.clip(0.9)

del norm
dataout=dataout.reshape(len(H),len(K),len(L))
H=H.astype('float32')
K=K.astype('float32')
L=L.astype('float32')
H=NXfield(H,name='H',long_name='H')
K=NXfield(K,name='K',long_name='K')
L=NXfield(L,name='L',long_name='L')
dataout=NXfield(dataout,name='counts',long_name='counts')
    
G=NXdata(dataout,(H,K,L))

G.save(outpath)

