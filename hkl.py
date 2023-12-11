"""
Filename: hkl.py


    (1) hkl_convert
"""

#import Image
import numpy as np
import ctypes as ct
import os
import sys
import time
from nexusformat.nexus import *
sys.path.append('hklconv_new/')

#sys.path.append('/home/specuser/Data/clancy/2013-03/hklmap/src/')
#from api.nexus.tree import *
#from api.nexus.napi import NeXusError

#
# stuff for ctypes to call c code to do hkl conversions

### import stuff... like a c header tells python what inputs are needed for the ccode and what to expect as output

#loads the c module
# Assuming libhkl.dll is in the same directory as the script
libhkl_path = os.path.join(os.path.dirname(__file__), 'libhkl.dll')

_libhkl = np.ctypeslib.load_library(libhkl_path, '.')
#_libhkl=ct.cdll['D:/kautzsch/new_refinement_data/codebase_for_users/libhkl']


#header for the calchkl code
_libhkl.calchkl.argtypes=[np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
		       np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
		       ct.c_double,ct.c_double,ct.c_double,ct.c_double,ct.c_double,\
		       np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
		       np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),ct.c_int]
		       
			
_libhkl.calchkl.restype=ct.c_void_p


#void hist(double *Hbin,double *Kbin,double *Lbin,double *HR,double *KR,double *LR,double *counts,double *vol,double *norm,int N,int hn,int kn,int ln);
_libhkl.hist.argtypes=[np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.float32,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.float32,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.float32,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.float32,ndim=1,flags='CONTIGUOUS'),\
			ct.c_int,ct.c_int,ct.c_int,ct.c_int,ct.c_float]

_libhkl.hist.restype=ct.c_void_p


#header for hte arbitrary slab histogram
_libhkl.histarb.argtypes=[np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.float32,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.double,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.float32,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.float32,ndim=1,flags='CONTIGUOUS'),\
			ct.c_float,ct.c_float,\
			np.ctypeslib.ndpointer(dtype = np.float32,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.float32,ndim=1,flags='CONTIGUOUS'),\
			np.ctypeslib.ndpointer(dtype = np.float32,ndim=1,flags='CONTIGUOUS'),\
			ct.c_int,ct.c_int,ct.c_int,ct.c_float]

_libhkl.hist.restype=ct.c_void_p


##
def HISTARB(IN,counts,mon,Q1bin,Q2bin,phat,vec1,vec2,prangemin,prangemax,vol,norm):

	HR=IN.transpose()[0]
	KR=IN.transpose()[1]
	LR=IN.transpose()[2]
	lenQ1=len(Q1bin)
	lenQ2=len(Q2bin)
	N=len(HR)
	I=np.asarray(counts,dtype=np.float32)
#	print 'Pmin = ',prangemin
#	print 'Pmax = ',prangemax
	_libhkl.histarb(Q1bin,Q2bin,phat,HR,KR,LR,vec1,vec2,prangemin,prangemax,I,vol,norm,N,lenQ1,lenQ2,mon)




##
def HIST(IN,counts,mon,Hbin,Kbin,Lbin,vol,norm,errors):

	HR=IN.transpose()[0]
	KR=IN.transpose()[1]
	LR=IN.transpose()[2]
	hn=len(Hbin)
	kn=len(Kbin)
	ln=len(Lbin)
	N=len(HR)
	I=np.asarray(counts,dtype=np.float32)
	#print hn,kn,ln,N,len(I),len(vol)
	_libhkl.hist(Hbin,Kbin,Lbin,HR,KR,LR,I,vol,norm,errors,N,hn,kn,ln,mon)



"""
pol = polar angle for each pixel in array i x j
az  = azamuthal angle for each pixel in array i x j
th = theta angle for the spectrometer
chi = chi angle for the spectrometer
phi = phi angle for the spectrometer
WL = Wavelength of x-rays
U = orientation matrix for the sample
B = B matrix for the sample
"""
##define a python function to setup the ctype and return stuff in a way python will understand
def Calc_HKL(pol,az,eta,mu,chi,phi,WL,U):
	
	#linearize the arrays
	dims=pol.shape
	n=len(dims)
	lin=1
	for i in range(0,n):
		lin=dims[i]*lin
	
	P=pol.reshape(lin)
	A=az.reshape(lin)
	eta=ct.c_double(eta*np.pi/180.0)
	mu=ct.c_double(mu*np.pi/180.0)
	chi=ct.c_double(chi*np.pi/180.0)
	phi=ct.c_double(phi*np.pi/180.0)
	WL=ct.c_double(WL)

	U=U/(2*np.pi)
	U=np.asarray(U).reshape(3*3)
	
	HR=np.empty(len(P),dtype=np.float)
	KR=np.empty(len(P),dtype=np.float)
	LR=np.empty(len(P),dtype=np.float)


	_libhkl.calchkl(P,A,eta,mu,chi,phi,WL,U,HR,KR,LR,len(P))
	IN=np.vstack((HR,KR,LR))
	IN=IN.transpose()
	return IN



##
#Routine to 'unwarp' the detector into the phi' and psi coordinates from the lumsden paper
# i use polar and azuimuthal anlges instead... just a name change to keep confusion down from the instrument angles
#this function was set up for the aug2010 experiment at the APS sector 1.  This would need to be changed for 
#a different experiment
#
#inputs
#D list containing detector parameters
#D=[xo,yo,D,nx,ny,px,py]
#xo=x distance in mm from the centre of the detector to the incident beam
#yo=y distance in mm from the centre of the detector to the incident beam
#D=distance in mm from the place where the incident beam hits the detector to the sample in mm
#nx=number of pixels in the x direction
#ny=number of pixels in the y direction
#px=size of the pixel in the x direction in mm
#py=size of the pixel in the y direction in mm
#
#returns
#pol=polar angles numpy array [nx][ny]
#az=azimuthal angles numpy array [nx][ny]
##
def P_UNWARP(D):
    xo=D[0]
    yo=D[1]
    nx=D[3]
    ny=D[4]
    px=D[5]
    py=D[6]


    D=D[2]
    pol=np.reshape(np.linspace(0,0,nx*ny),(nx,ny))
    az=np.reshape(np.linspace(0,0,nx*ny),(nx,ny))
    Dpp=np.reshape(np.linspace(0,0,nx*ny),(nx,ny))
    for i in range(0,nx):
        for j in range(0,ny):
            
            dx=((i-nx/2))*px+xo
            dy=((j-ny/2))*py+yo
            Dp=np.sqrt(dx**2.0+D**2.0)
            az[i][j]=np.arctan(dy/Dp)
            Dpp[i][j]=np.sqrt(dy**2.0+Dp**2.0)
            pol[i][j]=np.arctan(dx/D)
    return pol, az,Dpp




#inputs are the a1,a2,a3 vectors for the sample
#a's are numpy.array([,,,])
#return
#B=np.matrix(3x3)
def CalcB(a1,a2,a3):
    

    b1=(np.cross(a3,a2))/(np.dot(a1,np.cross(a3,a2)))
    b2=(np.cross(a1,a3))/(np.dot(a1,np.cross(a3,a2)))
    b3=(np.cross(a2,a1))/(np.dot(a1,np.cross(a3,a2)))
    A1=np.sqrt(np.dot(a1,a1))
    A2=np.sqrt(np.dot(a2,a2))
    A3=np.sqrt(np.dot(a3,a3))
    B1=np.sqrt(np.dot(b1,b1))
    B2=np.sqrt(np.dot(b2,b2))
    B3=np.sqrt(np.dot(b3,b3))
    alpha1=np.arccos(np.dot(a2,a3)/(A1*A3))
    beta2=np.arccos(np.dot(b1,b3)/(B1*B3))
    beta3=np.arccos(np.dot(b1,b2)/(B1*B2))
    
    B=np.matrix([[B1,0,0],[B2*np.cos(beta3), B2*np.sin(beta3),0.0],[B3*np.cos(beta2),-B3*np.sin(beta2)*np.cos(alpha1),1.0/A3]])
    return B


#inputs are h ad p vectors for the sample from the data and the calculated B
#h vectors describe the bragg peak the location p describes
#p is a vector containing the angles omega,chi,phi the bragg peak h describes
#B is the B matrix calculated above
#returns
#U = np.matrix(3x3)
def CalcU(H1,H2,P1,P2,B):
    #P's (w,chi,phi)
    #H's (h,k,l)
    P1=P1*np.pi/180.0
    P2=P2*np.pi/180.0


    H1=H1*B
    H2=H2*B
    
    H1=H1.tolist()
    
    H1=np.array(H1[0])

    H2=H2.tolist()
    H2=np.array(H2[0])

   
    
    tc1=H1/np.sqrt(np.dot(H1,H1))
    tc3=np.cross(H1,H2)/(np.sqrt(np.dot(H1,H1))*np.sqrt(np.dot(H2,H2)))
    tc2=np.cross(tc3,tc1)

    up1=np.array([np.cos(P1[0])*np.cos(P1[1])*np.cos(P1[2])-np.sin(P1[0])*np.sin(P1[2]),
                  np.cos(P1[0])*np.cos(P1[1])*np.sin(P1[2])+np.sin(P1[0])*np.cos(P1[2]),
                  np.cos(P1[0])*np.sin(P1[1])])
    
    up2=np.array([np.cos(P2[0])*np.cos(P2[1])*np.cos(P2[2])-np.sin(P2[0])*np.sin(P2[2]),
                  np.cos(P2[0])*np.cos(P2[1])*np.sin(P2[2])+np.sin(P2[0])*np.cos(P2[2]),
                  np.cos(P2[0])*np.sin(P2[1])])

    tp3=np.cross(up1,up2)
    tp2=np.cross(tp3,up1)

    Tc=np.matrix([[tc1[0],tc1[1],tc1[2]],[tc2[0],tc2[1],tc2[2]],[tc3[0],tc3[1],tc3[2]]])
    Tp=np.matrix([[up1[0],up1[1],up1[2]],[tp2[0],tp2[1],tp2[2]],[tp3[0],tp3[1],tp3[2]]])

    Tcinv=np.linalg.inv(Tc)
    U=Tcinv*Tp
    return U



def CorrectU(nu,mu,phi,U):

	nu=nu*np.pi/180.0
	mu=mu*np.pi/180.0
	phi=phi*np.pi/180.0

	NU=np.matrix([[1,0,0],[0,np.cos(nu),np.sin(nu)],[0,-1.0*np.sin(nu),np.cos(nu)]])
	MU=np.matrix([[np.cos(mu),0,-1.0*np.sin(mu)],[0,1,0],[np.sin(mu),0,np.cos(mu)]])
	PHI=np.matrix([[np.cos(phi),np.sin(phi),0],[-1.0*np.sin(phi),np.cos(phi),0],[0,0,1]])
	
	U=U*NU*MU*PHI

	return U


def detchi(pol,az):
	pol=pol*np.pi/180
	az=az*np.pi/180
	
	qpar=np.sqrt(1-np.cos(az)*np.cos(pol)+np.cos(az)*np.cos(az))
	chi=np.arctan(np.sin(az)/qpar)
	return chi



