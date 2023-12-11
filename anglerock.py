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


def anglerock(H,K,L,stack,ormat,WL,U,data,norm,errors,workingdir,stacknum):
  ap=time.time()
  dtype = np.dtype(np.uint16)

  #counter for number of files processed
  count=0

  #import the spec read command ... it reads the spec scan to get the angles and monitor information for the scan
  angs=np.linspace(0,0,6)
  #in this case, we are flyscanning phi. Need to change for other angle scans
  tth=0.0
  #    eta=stack.psic.eta.nxdata
  #    eta=stack.psic.eta.nxdata+.385385
  #    chi=stack.psic.chi.nxdata+.053053
  #    eta=stack.psic.eta.nxdata+.77
  #    chi=stack.psic.chi.nxdata+.05
  eta=stack.psic.eta.nxdata
  chi=stack.psic.chi.nxdata
  phi=stack.data.phi.nxdata
  #kludge from rot_macro phi speed error - for greven
  #    phi=phi*360.0/360.15
  #    phi=phi*360.0/360.1
  #    phi=phi*360.1/360.0
  #    phi=phi*360.0/359.6

  #print "Phi = ",phi
  nu=0.0
  mu=0.0

  dpsi=ormat.dspi.dpsi.nxdata
  myaz=np.asarray(stack.geo.az.data)
  mypol=np.asarray(stack.geo.pol.data)
  mytth=np.sqrt((myaz*myaz) + (mypol*mypol))
  mypsi=np.asarray(stack.geo.psi.data)
  pol2=mytth*np.cos(mypsi+(np.pi*0.5)+dpsi)
  az2=-mytth*np.sin(mypsi+(np.pi*0.5)+dpsi)

  n=range(0,len(phi))

  print("Loading stack...")
  Iall=stack.data.counts.nxdata
  print("Stack loaded...")


  #filenames for tiff images
  #process the tiffs
  #    for i in range(0,len(phi)):
  for i in range(0,len(phi)):
    short_workingdir = "/".join(workingdir.split("/")[-5:-1])
    print('From '+short_workingdir+' scannum='+str(stack.spec.scannum)+' stacknum='+str(stacknum)+' Loaded frame '+str(i))
    #        I=stack.data.counts[:,:,i].nxdata
    if (stack.norm.icnorm[i]>0.00):
      framenorm=1.0/(stack.norm.icnorm[i]*stack.norm.solidangle) #normalize solid angle and ionchamber
      count=count+1
      IN=hkl.Calc_HKL(pol2,az2,eta,mu,chi,phi[i],WL,U)
      hkl.HIST(IN,(Iall[:,:,i]*framenorm).ravel(),1.0,H,K,L,data,norm,errors)    

  bp=time.time()
  n=len(n)
  print("It took ",bp-ap," seconds to process ",count," frames!!!")

  # print("Clearing Iall from memory.")
  # gc.collect()
  # sleep(10)
  # print("Memory cleared.")

  Iall=0
  return U