import numpy as np
import pandas as pd
from nexusformat.nexus import *
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from scipy.optimize import minimize
from scipy.optimize import basinhopping
from scipy.optimize import brute
from scipy.optimize import fmin
import hkl
import time
import sys,os
import logging
from os.path import exists
import gc
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk  # Make sure to have the Pillow library installed



def get_peaklist(projectdir,stack_file,valmin,valmax,lower_bound,upper_bound):
    if float(valmax)!=1.0:
        projdir=projectdir
        percofmax=float(valmax)
        percofmin=float(valmin)
        lower_bound=float(lower_bound)
        upper_bound=float(upper_bound)
        print("Loading stack...")
        stack=nxload(projectdir+stack_file)
        nxsetmemory(100000)
        Iall=stack.data.counts.nxdata
        print("Stack loaded.")
        peaksmax=np.max(Iall)
        print("Max intensity is ",peaksmax)
        print("Finding peaks...")
        peaks=np.logical_and(Iall<percofmax*peaksmax, Iall>percofmin*peaksmax)
        peaks.shape
        listofpeaks=np.asarray(np.where(peaks)).T

        while len(listofpeaks)<lower_bound:
            print("Number of peaks found: "+str(len(listofpeaks)))
            percofmin=percofmin-0.1
            print('Not enough peaks found.')
            gc.collect()
            print('Decreasing to: '+str(percofmin))
            print("Finding peaks...")
            peaks=np.logical_and(Iall<percofmax*peaksmax, Iall>percofmin*peaksmax)
            peaks.shape
            listofpeaks=np.asarray(np.where(peaks)).T
            #print(len(listofpeaks))
        if len(listofpeaks)>upper_bound:
            while len(listofpeaks)>upper_bound:
                print("Number of peaks found: "+str(len(listofpeaks)))
                percofmin=percofmin+0.02
                print('Too many peaks found.')
                print('Increasing to: '+str(percofmin))
                print("Finding peaks...")
                peaks=np.logical_and(Iall<percofmax*peaksmax, Iall>percofmin*peaksmax)
                peaks.shape
                listofpeaks=np.asarray(np.where(peaks)).T
            if len(listofpeaks)<lower_bound:
                    while len(listofpeaks)<lower_bound:
                        print("Number of peaks found: "+str(len(listofpeaks)))
                        percofmin=percofmin-0.01
                        print('Not enough peaks found.')
                        gc.collect()
                        print('Decreasing to: '+str(percofmin))
                        print("Finding peaks...")
                        peaks=np.logical_and(Iall<percofmax*peaksmax, Iall>percofmin*peaksmax)
                        peaks.shape
                        listofpeaks=np.asarray(np.where(peaks)).T
        print(len(listofpeaks))



        #print(listofpeaks.shape)
        #for i in range(0,len(listofpeaks)):
        #	print(np.asarray(listofpeaks[i]))
        peaksout=projdir+"peaklist1"
        while os.path.exists(peaksout):
            peaklistnum=int(outfile[-5:-4])
            peaksout=peaksout[:-5]+str(peaklistnum+1)+".nxs"
        np.save(peaksout,listofpeaks)
    else:
        projdir=projectdir
        percofmax=float(valmax)
        percofmin=float(valmin)
        stack_file = sorted([f for f in os.listdir(projectdir) if f.startswith("stack")])[0]
        print("Loading stack...")
        stack=nxload(projectdir+stack_file)
        nxsetmemory(100000)
        Iall=stack.data.counts.nxdata
        print("Stack loaded.")
        peaksmax=np.max(Iall)
        print("Max intensity is ",peaksmax)
        print("Percent Min is ",percofmin)
        print("Percent Max is ",percofmax)
        print("Min # peaks is ",lower_bound)
        print("Max # peaks is ",upper_bound)
        print("Finding peaks...")
        peaks=Iall>percofmin*peaksmax
        peaks.shape
        listofpeaks=np.asarray(np.where(peaks)).T
        print(listofpeaks)

        while len(listofpeaks)<lower_bound:
            print("Number of peaks found: "+str(len(listofpeaks)))
            percofmin=percofmin-0.1
            print('Not enough peaks found.')
            gc.collect()
            print('Decreasing to: '+str(percofmin))
            print("Max intensity is ",peaksmax)
            print("Percent Min is ",percofmin)
            print("Percent Max is ",percofmax)
            print("Min # peaks is ",lower_bound)
            print("Max # peaks is ",upper_bound)
            print("Finding peaks...")
            peaks=Iall>percofmin*peaksmax
            peaks.shape
            listofpeaks=np.asarray(np.where(peaks)).T
            print(listofpeaks)
        if len(listofpeaks)>upper_bound:
            while len(listofpeaks)>upper_bound:
                print("Number of peaks found: "+str(len(listofpeaks)))
                percofmin=percofmin+0.02
                print('Too many peaks found.')
                print('Increasing to: '+str(percofmin))

                peaks=Iall>percofmin*peaksmax
                peaks.shape
                listofpeaks=np.asarray(np.where(peaks)).T
            if len(listofpeaks)<lower_bound:
                while len(listofpeaks)<lower_bound:
                    print("Number of peaks found: "+str(len(listofpeaks)))
                    percofmin=percofmin-0.01
                    print('Not enough peaks found.')
                    gc.collect()
                    print('Decreasing to: '+str(percofmin))

                    peaks=Iall>percofmin*peaksmax
                    peaks.shape
                    listofpeaks=np.asarray(np.where(peaks)).T
        print(len(listofpeaks))



        #print(listofpeaks.shape)
        #for i in range(0,len(listofpeaks)):
        #	print(np.asarray(listofpeaks[i]))
        peaksout=projdir+"peaklist1"
        while os.path.exists(peaksout):
            peaklistnum=int(outfile[-5:-4])
            peaksout=peaksout[:-5]+str(peaklistnum+1)+".nxs"
        np.save(peaksout,listofpeaks)

def get_length_plist(projectdir):
    peaklist=np.load(projectdir+"peaklist1.npy")
    return len(peaklist)

def get_cell_params_from_file():
    filepath = filedialog.askopenfilename(title="Select Unit Cell Parameters File", filetypes=[("Text Files", "*.txt")])

    if exists(filepath):
        df = pd.read_csv(filepath, header=None)
        uca_var.set(float(df[0]))
        ucb_var.set(float(df[1]))
        ucc_var.set(float(df[2]))
        ucal_var.set(float(df[3]))
        ucbe_var.set(float(df[4]))
        ucga_var.set(float(df[5]))
    else:
        print("File not found.")


def get_cell_params_from_entry():
    try:
        uca = float(uca_var.get())
        ucb = float(ucb_var.get())
        ucc = float(ucc_var.get())
        ucal = float(ucal_var.get())
        ucbe = float(ucbe_var.get())
        ucga = float(ucga_var.get())

        # Do something with the values, for example, print them
        print("Unit Cell Parameters:")
        print(f"a = {uca}")
        print(f"b = {ucb}")
        print(f"c = {ucc}")
        print(f"alpha = {ucal}")
        print(f"beta = {ucbe}")
        print(f"gamma = {ucga}")
        
        uc_saved_label.config(text="Saved!")

    except ValueError:
        print("Invalid input. Please enter valid numeric values.")
    

def find_euler(projectdir):
    proj=projectdir
    peakfile=projectdir+"peaklist1.npy"
    stack_file = sorted([f for f in os.listdir(projectdir) if f.startswith("stack")])[0]
    w=nxload(projectdir+stack_file)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(proj+"ormfinder.log"),
            logging.StreamHandler(sys.stdout)
            ]
        )

    peaklist=np.load(peakfile)
    peaknum=len(peaklist)
    logging.info("Loaded {n} peak points from file.".format(n=peaknum))
    prelimflag=0

    uca = float(1)
    ucb = float(1)
    ucc = float(1)
    ucal = float(90)
    ucbe = float(90)
    ucga = float(90)

    if (peaknum > 75):
        shortpeaklist=peaklist[:20]
        shortpeaknum=len(shortpeaklist)
        prelimflag=1
        
        uca = float(uca_var.get())
        ucb = float(ucb_var.get())
        ucc = float(ucc_var.get())
        ucal = float(ucal_var.get())
        ucbe = float(ucbe_var.get())
        ucga = float(ucga_var.get())

    logging.info("UCell: {a} {b} {c} {al} {be} {ga}".format(a=uca,b=ucb,c=ucc,al=ucal,be=ucbe,ga=ucga))
    philu=w.data.phi.nxdata

    wl=w.geo.wl
    logging.info("Wavelength  = {wl}".format(wl=wl))
    eta=w.psic.eta
    mu=w.psic.mu
    chi=w.psic.chi
    dpsi=0.0*np.pi/180.0
    myaz=np.asarray(w.geo.az.data)
    mypol=np.asarray(w.geo.pol.data)
    #mytth=np.sqrt((myaz*myaz) + (mypol*mypol))
    #mypsi=np.asarray(w.geo.psi.data)
    #newpol=mytth*np.cos(mypsi+(np.pi*0.5)+dpsi)
    #newaz=-mytth*np.sin(mypsi+(np.pi*0.5)+dpsi)
    newpol=mypol
    newaz=myaz

    def XYtoPOLAZ(X,Y):
        return newpol[X,Y],newaz[X,Y]

    #speed this up by only doing calcB once, passing B to the minfunc
    def calcB(a,b,c,alpha,beta,gamma):
        a1=a
        a2=b
        a3=c
        alpha1=alpha*np.pi/180.0
        alpha2=beta*np.pi/180.0
        alpha3=gamma*np.pi/180.0
        Vt = (1.0 - (np.cos(alpha1)*np.cos(alpha1)) - (np.cos(alpha2)*np.cos(alpha2)) - (np.cos(alpha3)*np.cos(alpha3)))
        Vt = Vt + (2.0*np.cos(alpha1)*np.cos(alpha2)*np.cos(alpha3))
        V = (Vt**0.5)*a1*a2*a3
        b1=2.0*np.pi*a2*a3*np.sin(alpha1)/V
        b2=2.0*np.pi*a3*a1*np.sin(alpha2)/V
        b3=2.0*np.pi*a1*a2*np.sin(alpha3)/V
        betanum=((np.cos(alpha2)*np.cos(alpha3)) - np.cos(alpha1))
        betaden=(np.sin(alpha2)*np.sin(alpha3))
        beta1=np.arccos(betanum/betaden)
        betanum=((np.cos(alpha1)*np.cos(alpha3)) - np.cos(alpha2))
        betaden=(np.sin(alpha1)*np.sin(alpha3))
        beta2=np.arccos(betanum/betaden)
        betanum=((np.cos(alpha1)*np.cos(alpha2)) - np.cos(alpha3))
        betaden=(np.sin(alpha1)*np.sin(alpha2))
        beta3=np.arccos(betanum/betaden)
        UB=np.zeros(9)
        UB[0]=b1
        UB[1]=b2*np.cos(beta3)
        UB[2]=b3*np.cos(beta2)
        UB[3]=0.0
        UB[4]=-b2*np.sin(beta3)
        UB[5]=b3*np.sin(beta2)*np.cos(alpha1)
        UB[6]=0.0
        UB[7]=0.0
        UB[8]=-b3
        return UB

    def calcUB(eu1,eu2,eu3,UB):
        r = R.from_euler('zxz', [eu1, eu2, eu3])
        UBR=np.matmul(r.as_matrix(),UB.reshape(3,3))
        return UBR

    def chisq_U(peaklist,wl,UBR,eta,mu,chi):
        peaknum=len(peaklist)
        chisq=0.0
        for i in range(0,peaknum):
            pol,az=XYtoPOLAZ(peaklist[i][0],peaklist[i][1])
            phi=philu[peaklist[i][2]]
            IN=hkl.Calc_HKL(np.asarray([pol]),np.asarray([az]),eta,mu,chi,phi,wl,UBR)
            dvec=IN-np.rint(IN)
            chisq=chisq+np.linalg.norm(dvec)
        return chisq/peaknum


    def minfuncU(eu,UB,peaklist,wl):
        UBR=calcUB(eu[0],eu[1],eu[2],UB)
        chisq=chisq_U(peaklist,wl,UBR.T,eta,mu,chi)
        return chisq

    def minfuncWL(fitwl,eu0,eu1,eu2,a,b,c,alpha,beta,gamma,peaklist):
        UBR=calcUB(eu0,eu1,eu2,a,b,c,alpha,beta,gamma)
        chisq=chisq_U(peaklist,fitwl[0],UBR.T,eta,mu,chi)
        return chisq

    myUB=calcB(uca, ucb, ucc, ucal, ucbe, ucga)
    print("Calculated B", myUB)

    if (prelimflag):
        x0=[0,0,0]
        logging.info("Preliminary fitting of first 20 points, starting config A")
        minimizer_kwargs = {"method": "BFGS", "args": (myUB, shortpeaklist, wl)}
        #    pre1 = basinhopping(minfuncU, x0, stepsize=np.pi/30.0, T=0.25, minimizer_kwargs=minimizer_kwargs, niter=100, seed=20)
        pre1 = basinhopping(minfuncU, x0, T=0.002, minimizer_kwargs=minimizer_kwargs)
        logging.info("Eu angles: {angs},  chisq: {chisq}".format(angs=pre1.x,chisq=pre1.fun))
        x0=[0.5,1.0,0.25]
        logging.info("Preliminary fitting of first 20 points, starting config B")
        minimizer_kwargs = {"method": "BFGS", "args": (myUB, shortpeaklist, wl)}
        #    pre2 = basinhopping(minfuncU, x0, stepsize=np.pi/30.0, T=0.25, minimizer_kwargs=minimizer_kwargs, niter=100, seed=21)
        pre2 = basinhopping(minfuncU, x0, T=0.002, minimizer_kwargs=minimizer_kwargs)
        logging.info("Eu angles: {angs},  chisq: {chisq}".format(angs=pre2.x,chisq=pre2.fun))

    #if (pre1.fun<pre2.fun):
    #	x0=pre1.x
    #else:
    #	x0=pre2.x

    x0=[0,0,0]

    logging.info("Fitting all peaks. Starting Eu angles: {angs}".format(angs=x0))

    minimizer_kwargs = {"method": "BFGS", "args": (myUB, peaklist, wl)}
    #ret1 = basinhopping(minfuncU, x0, stepsize=np.pi/30.0, T=0.2, minimizer_kwargs=minimizer_kwargs, niter=100, seed=22)
    ret1 = basinhopping(minfuncU, x0, T=0.002, minimizer_kwargs=minimizer_kwargs)
    logging.info("Eu angles: {angs},  chisq: {chisq}".format(angs=ret1.x,chisq=ret1.fun))

    x0=ret1.x
    minimizer_kwargs = {"method": "BFGS", "args": (myUB, peaklist, wl)}
    ret2 = basinhopping(minfuncU, x0, minimizer_kwargs=minimizer_kwargs, niter=300, seed=23)
    logging.info("Eu angles: {angs},  chisq: {chisq}".format(angs=ret2.x,chisq=ret2.fun))

    x0=ret2.x
    minimizer_kwargs = {"method": "BFGS", "args": (myUB, peaklist, wl)}
    ret3 = basinhopping(minfuncU, x0, stepsize=np.pi/30.0, T=0.005, minimizer_kwargs=minimizer_kwargs, niter=100, seed=24)
    logging.info("Eu angles: {angs},  chisq: {chisq}".format(angs=ret3.x,chisq=ret3.fun))

    print('Done fitting peaks!')
    return uca,ucb,ucc,ucal,ucbe,ucga,ret3.x


def get_ubr(projectdir,uca,ucb,ucc,ucal,ucbe,ucga,angs):
    stack_file = sorted([f for f in os.listdir(projectdir) if f.startswith("stack")])[0]
    w=nxload(projectdir+stack_file)
    auto_eu=angs
    wl=w.geo.wl

    def calcUB(eu1,eu2,eu3,a,b,c,alpha,beta,gamma):
        a1=a
        a2=b
        a3=c
        alpha1=alpha*np.pi/180.0
        alpha2=beta*np.pi/180.0
        alpha3=gamma*np.pi/180.0
        Vt = (1.0 - (np.cos(alpha1)*np.cos(alpha1)) - (np.cos(alpha2)*np.cos(alpha2)) - (np.cos(alpha3)*np.cos(alpha3)))
        Vt = Vt + (2.0*np.cos(alpha1)*np.cos(alpha2)*np.cos(alpha3))
        V = (Vt**0.5)*a1*a2*a3
        b1=2.0*np.pi*a2*a3*np.sin(alpha1)/V
        b2=2.0*np.pi*a3*a1*np.sin(alpha2)/V
        b3=2.0*np.pi*a1*a2*np.sin(alpha3)/V
        betanum=((np.cos(alpha2)*np.cos(alpha3)) - np.cos(alpha1))
        betaden=(np.sin(alpha2)*np.sin(alpha3))
        beta1=np.arccos(betanum/betaden)
        betanum=((np.cos(alpha1)*np.cos(alpha3)) - np.cos(alpha2))
        betaden=(np.sin(alpha1)*np.sin(alpha3))
        beta2=np.arccos(betanum/betaden)
        betanum=((np.cos(alpha1)*np.cos(alpha2)) - np.cos(alpha3))
        betaden=(np.sin(alpha1)*np.sin(alpha2))
        beta3=np.arccos(betanum/betaden)
        UB=np.zeros(9)
        UB[0]=b1
        UB[1]=b2*np.cos(beta3)
        UB[2]=b3*np.cos(beta2)
        UB[3]=0.0
        UB[4]=-b2*np.sin(beta3)
        UB[5]=b3*np.sin(beta2)*np.cos(alpha1)
        UB[6]=0.0
        UB[7]=0.0
        UB[8]=-b3
        r = R.from_euler('zxz', [eu1, eu2, eu3])
        UBR=np.matmul(r.as_matrix(),UB.reshape(3,3))
        return UBR

    UBRfinal=calcUB(auto_eu[0], auto_eu[1],  auto_eu[2], uca, ucb, ucc, ucal, ucbe, ucga)

    return UBRfinal,w,wl

def check_peaklist(projectdir,UBRfinal,w,wl):
    peakfile=projectdir+"peaklist1.npy"
    philu=w.data.phi.nxdata
    #print(wl)
    eta=w.psic.eta
    mu=w.psic.mu
    chi=w.psic.chi
    #dpsi=0.09*np.pi/180.0
    dpsi=0.0*np.pi/180.0
    myaz=np.asarray(w.geo.az.data)
    mypol=np.asarray(w.geo.pol.data)
    mytth=np.sqrt((myaz*myaz) + (mypol*mypol))
    mypsi=np.asarray(w.geo.psi.data)
    newpol=mytth*np.cos(mypsi+(np.pi*0.5)+dpsi)
    newaz=-mytth*np.sin(mypsi+(np.pi*0.5)+dpsi)
    newpol=mypol
    newaz=myaz

    def XYtoPOLAZ(X,Y):
        return newpol[X,Y],newaz[X,Y]

    peaklist=np.load(peakfile)
    peaknum=len(peaklist)

    def printconvpeaks(peaklist,wl,UBR,eta,mu,chi):
        peaknum=len(peaklist)
        chisq=0.0
        for i in range(0,peaknum):
            pol,az=XYtoPOLAZ(peaklist[i][0],peaklist[i][1])
            #        phi=peaklist[i][2]
            phi=philu[peaklist[i][2]]
            IN=hkl.Calc_HKL(np.asarray([pol]),np.asarray([az]),eta,mu,chi,phi,wl,UBR)
            print(IN)

    printconvpeaks(peaklist,wl,UBRfinal.T,eta,mu,chi)

def save_orm(projectdir,UBRfinal,uca,ucb,ucc,ucal,ucbe,ucga):
    ormout=projectdir+"ormatrix_auto.nxs"
    dpsi=0.0

    print(UBRfinal.ravel().tolist())
    np.save(ormout,UBRfinal)

    ormnex=NXroot()
    ormnex.unitcell=NXentry()
    ormnex.unitcell.a=NXfield(uca, name='a')
    ormnex.unitcell.b=NXfield(ucb, name='b')
    ormnex.unitcell.c=NXfield(ucc, name='c')
    ormnex.unitcell.alpha=NXfield(ucal, name='alpha')
    ormnex.unitcell.beta=NXfield(ucbe, name='beta')
    ormnex.unitcell.gamma=NXfield(ucga, name='gamma')

    ormnex.ormatrix=NXentry()
    ormnex.ormatrix.U=NXfield(UBRfinal, name='Orientation_Matrix')
    ormnex.dspi=NXentry()
    ormnex.dspi.dpsi=NXfield(dpsi, name='detector psi offset')
    ormnex.save(ormout)

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_path = folder_path.rstrip(os.path.sep) + "/"  # Ensure it ends with a forward slash
        orm_folder.set(folder_path)
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder_path)
        os.chdir(folder_path)
        check_for_peaklist()
        update_stack_file_list()

def check_for_peaklist():
    folder_path = orm_folder.get()
    # Check for existing peaklist files
    peaklist_files = [file for file in os.listdir(folder_path) if file.startswith("peaklist") and file.endswith(".npy")]

    if peaklist_files:
        message = "Existing peaklist found."
        # You can display the message in a label or any other way you prefer
        existing_peaklist_label.config(text=message)
    else:
        existing_peaklist_label.config(text="No existing peaklist found.")

def call_get_peaklist():
    # Display a warning message
    is_sure = messagebox.askyesno("Warning", "Are you sure you want to find peaks?")

    # Check if the user clicked "Yes"
    if is_sure:
        folder_path = orm_folder.get()
        value_min = float(val_min.get())
        value_max = float(val_max.get())
        lower_bound_value = int(lower_bound.get())
        upper_bound_value = int(upper_bound.get())

        # Call the get_peaklist function
        get_peaklist(folder_path, stack_file.get(), value_min, value_max, lower_bound_value, upper_bound_value)

        # Update the number of peaks label
        num_peaks_label.config(text="Number of peaks found: {length}".format(length=get_length_plist(folder_path)))

        # Display confirmation message
        messagebox.showinfo("Confirmation", "Finished finding peaks!")
    else:
        # User clicked "No" or closed the dialog
        print("Operation canceled.")

def orient():
    # Get the value of the orm_folder variable
    selected_folder = orm_folder.get()

    # Call the functions
    uca, ucb, ucc, ucal, ucbe, ucga, angs = find_euler(selected_folder)
    UBRfinal, w, wl = get_ubr(selected_folder, uca, ucb, ucc, ucal, ucbe, ucga, angs)
    check_peaklist(selected_folder, UBRfinal, w, wl)
    save_orm(selected_folder, UBRfinal, uca, ucb, ucc, ucal, ucbe, ucga)

    # Display confirmation message
    messagebox.showinfo("Confirmation", "Finished solving orientation matrix!")

# Function to refresh the image
def refresh_image():
    image_file_path = orm_folder.get() + "histogram.png"
    img = Image.open(image_file_path)
    img = img.resize((300, 300), Image.ANTIALIAS)  # Adjust the size as needed
    photo = ImageTk.PhotoImage(img)
    image_label.config(image=photo)
    image_label.image = photo

def get_histogram():
    projectdir = orm_folder.get()
    projdir = projectdir
    stack_file_val = stack_file.get()
    
    print("Loading stack...")
    stack = nxload(projectdir + stack_file_val)
    nxsetmemory(100000)
    
    Iall = stack.data.counts.nxdata[stack.data.counts.nxdata > 1000]
    peaksmax=np.max(Iall)
    # Plotting the histogram on a y log scale with 20 bins
    fig = plt.figure(figsize=(2,2),dpi=180)
    ax = fig.add_axes([0,0,1,1])
    ax.hist(Iall/peaksmax, bins=20, color='blue', edgecolor='black')
    plt.yscale('log')  # Set y-axis to log scale
    
    # Adding labels and title
    plt.xlabel('$I/I_{max}$')
    plt.ylabel('# peaks (log scale)')
    plt.title('Histogram of Pixel Intensities')
    
    # Save the plot as an image file
    plt.savefig(projdir + 'histogram.png', bbox_inches='tight', dpi=300)
    del Iall
    del stack
    gc.collect()
    refresh_image()

def update_stack_file_list():
    orm_folder_path = orm_folder.get()

    # Check if orm_folder_path is a valid directory
    if not os.path.isdir(orm_folder_path):
        # Handle the case where orm_folder_path is not a valid directory
        print("Invalid directory path:", orm_folder_path)
        return

    # Get a list of all files ending with ".nxs" in orm_folder
    nxs_files = [f for f in os.listdir(orm_folder_path) if f.endswith(".nxs")]

    # Clear and update the stack_file_listbox
    stack_file_listbox.delete(0, tk.END)
    for nxs_file in nxs_files:
        stack_file_listbox.insert(tk.END, nxs_file)

def confirm_stack_file():
    selected_item_index = stack_file_listbox.curselection()
    if selected_item_index:
        selected_item = stack_file_listbox.get(selected_item_index)
        stack_file.set(selected_item)
        existing_peaklist_label.config(text=f"Selected file: {selected_item}")
    else:
        existing_peaklist_label.config(text="No file selected. Please select a file.")

# Create the main window
root = tk.Tk()
root.title("Orientation Matrix Finder")

# First Column (Frame1)
frame1 = ttk.Frame(root)
frame1.grid(row=0, column=0, pady=10, padx=5, sticky=tk.N)

row = 0
label_text = "Select orm directory:"
label = tk.Label(frame1, text=label_text)
label.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1

# Check if sys.argv[1] is available
default_folder = sys.argv[1] if len(sys.argv) > 1 else ""
default_folder = default_folder.rstrip(os.path.sep) + "/"  # Ensure it ends with a forward slash

# Create an Entry widget to display the selected folder path
orm_folder = tk.StringVar(value=default_folder)  # Set the default value
entry_path = tk.Entry(frame1, textvariable=orm_folder, state='readonly', width=40)
entry_path.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1

# Create a button to open the file dialog
button = tk.Button(frame1, text="Browse...", command=select_folder)
button.grid(row=row, column=0, pady=10, padx=5, sticky=tk.W)
row+=1

stack_file = tk.StringVar(value='')

stack_file_label = tk.Label(frame1, text="Select a stack file to use for orienting:")
stack_file_label.grid(row=row, column=0, pady=10, padx=5, sticky=tk.W)
row+=1

# Add a listbox of the files that end in .nxs within the directory
stack_file_listbox = tk.Listbox(frame1, selectmode=tk.SINGLE, width=40)
stack_file_listbox.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1

if default_folder:
    update_stack_file_list()

# Add a button "Confirm" that assigns the selection from the listbox to a variable called stack_file
confirm_button = tk.Button(frame1, text="Confirm", command=confirm_stack_file)
confirm_button.grid(row=row, column=0, pady=10, padx=5, sticky=tk.W)
row += 1

# Add a label to display the existing peaklist message

existing_peaklist_label = tk.Label(frame1, text="")
existing_peaklist_label.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1

# Second Column (Frame2)
frame2 = ttk.Frame(root)
frame2.grid(row=0, column=1, pady=10, padx=5, sticky=tk.N)

# Create button to call get_peaklist function
get_peaklist_button = tk.Button(frame2, text="Generate peak histogram", command=get_histogram)
get_peaklist_button.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
hist_row=row
row+=1

# Create labels and entry widgets for parameters
tk.Label(frame2, text="Minimum # peaks:").grid(row=row, column=0, pady=5, padx=5, sticky=tk.E)
lower_bound = tk.DoubleVar(value=50)
tk.Entry(frame2, textvariable=lower_bound, width=10).grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)
row+=1

tk.Label(frame2, text="Maximum # peaks:").grid(row=row, column=0, pady=5, padx=5, sticky=tk.E)
upper_bound = tk.DoubleVar(value=150)
tk.Entry(frame2, textvariable=upper_bound, width=10).grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)
row+=1

tk.Label(frame2, text="Minimum intensity (%):").grid(row=row, column=0, pady=5, padx=5, sticky=tk.E)
val_min = tk.DoubleVar(value=0.9)
tk.Entry(frame2, textvariable=val_min, width=10).grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)
row+=1

tk.Label(frame2, text="Maximum intensity (%):").grid(row=row, column=0, pady=5, padx=5, sticky=tk.E)
val_max = tk.DoubleVar(value=1.0)
tk.Entry(frame2, textvariable=val_max, width=10).grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)
row+=1

# Create button to call get_peaklist function
get_peaklist_button = tk.Button(frame2, text="Generate new peaklist", command=call_get_peaklist)
get_peaklist_button.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1

# Add a label to display the number of peaks found
num_peaks_label = tk.Label(frame2, text="")
num_peaks_label.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

end_hist_row=row

# Create a label to display the image
image_label = tk.Label(frame2)
image_label.grid(row=hist_row, column=2, rowspan=end_hist_row-hist_row, pady=10, padx=5, sticky=tk.W)
row=hist_row
# Create a button to refresh the image
refresh_button = tk.Button(frame2, text="Refresh Image", command=refresh_image)
refresh_button.grid(row=hist_row, column=1, pady=10, padx=5, sticky=tk.E)


# Third Column (Frame3)
frame3 = ttk.Frame(root)
frame3.grid(row=0, column=2, pady=10, padx=5, sticky=tk.N)

# Create StringVars to store unit cell parameters
uca_var = tk.StringVar()
ucb_var = tk.StringVar()
ucc_var = tk.StringVar()
ucal_var = tk.StringVar()
ucbe_var = tk.StringVar()
ucga_var = tk.StringVar()

# Browse button to select unit cell parameters file
browse_button = tk.Button(frame3, text="Browse for Unit Cell Parameters", command=get_cell_params_from_file)
browse_button.grid(row=row, column=0, pady=10, padx=5)
row+=1

# Entry boxes for unit cell parameters
tk.Label(frame3, text="a").grid(row=row, column=0, padx=5, sticky=tk.E)
uca_entry = tk.Entry(frame3, textvariable=uca_var, width=10)
uca_entry.grid(row=row, column=1, padx=5, sticky=tk.W)
row += 1

tk.Label(frame3, text="b").grid(row=row, column=0, padx=5, sticky=tk.E)
ucb_entry = tk.Entry(frame3, textvariable=ucb_var, width=10)
ucb_entry.grid(row=row, column=1, padx=5, sticky=tk.W)
row += 1

tk.Label(frame3, text="c").grid(row=row, column=0, padx=5, sticky=tk.E)
ucc_entry = tk.Entry(frame3, textvariable=ucc_var, width=10)
ucc_entry.grid(row=row, column=1, padx=5, sticky=tk.W)
row += 1

tk.Label(frame3, text="alpha").grid(row=row, column=0, padx=5, sticky=tk.E)
ucal_entry = tk.Entry(frame3, textvariable=ucal_var, width=10)
ucal_entry.grid(row=row, column=1, padx=5, sticky=tk.W)
row += 1

tk.Label(frame3, text="beta").grid(row=row, column=0, padx=5, sticky=tk.E)
ucbe_entry = tk.Entry(frame3, textvariable=ucbe_var, width=10)
ucbe_entry.grid(row=row, column=1, padx=5, sticky=tk.W)
row += 1

tk.Label(frame3, text="gamma").grid(row=row, column=0, padx=5, sticky=tk.E)
ucga_entry = tk.Entry(frame3, textvariable=ucga_var, width=10)
ucga_entry.grid(row=row, column=1, padx=5, sticky=tk.W)
row += 1

# Button to get unit cell parameters from entry boxes
get_params_button = tk.Button(frame3, text="Save unit cell parameters", command=get_cell_params_from_entry)
get_params_button.grid(row=row, column=0, pady=10)
row+=1

# Add a label to confirm uc parameters
uc_saved_label = tk.Label(frame3, text="")
uc_saved_label.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1

# Add a horizontal Separator
separator_horizontal3 = ttk.Separator(frame3, orient="horizontal")
separator_horizontal3.grid(row=row, column=0, columnspan=3, sticky="ew", pady=10)
row += 1

# Create button to complete orienting
orient_button = tk.Button(frame3, text="Solve orientation matrix", command=orient)
orient_button.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1


# Run the Tkinter event loop
root.mainloop()

# find_peaks = True
# while find_peaks == True:
# 	use_default_values=input("Use default peak finding values? (y/n): ")
# 	if default=='y':
# 		lower_bound=50
# 		upper_bound=150
# 		val=0.9
# 	else:
# 		lower_bound = int(input("Set minimum number of peaks: "))
# 		upper_bound = int(input("Set maximum number of peaks: "))
# 		val = float(input("Enter percentage of max intensity for peak finding (0.0 <-> 1.0): "))
# 	get_peaklist(main_proj_dir,val,lower_bound,upper_bound)
# 	get_length_plist(main_proj_dir)
# 	ans = input("Proceed (y) or retry (n): ")
# 	if ans == 'n':
# 		pass
# 	if ans == 'y':
# 		find_peaks = False

