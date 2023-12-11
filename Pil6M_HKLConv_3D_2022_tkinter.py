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

import tkinter as tk
from tkinter import Listbox, Button, Label, StringVar, Entry, filedialog, messagebox


# Import code from anglerock.py
from anglerock import anglerock


#######################################################
####  input parameters                      ####
#######################################################
# Define the hkl space to histogram and define/zero data structures
H=np.arange(-5.1,5.1, 0.01)
K=np.arange(-5.1,5.1, 0.01)
L=np.arange(-9.1,9.1, 0.02)

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

#some physical constants
PC=4.13566733e-15 	# planks constant in si
c=2.99792458e8 		# speed of light


#############################################################################



def browse_for_directory(entry_var):
    directory = filedialog.askdirectory()
    entry_var.set(directory)
    update_rotations_list()

def update_rotations_list():
    global rotations_list
    rotations_list = sorted([file for file in os.listdir(workingdir_var.get()) if file.startswith("stack")])
    update_listbox()

def update_listbox():
    listbox.delete(0, tk.END)
    for rotation in rotations_list:
        listbox.insert(tk.END, rotation)

def update_selected_list():
    global num_rotations
    global selected_folders
    selected_indices = listbox.curselection()
    num_rotations = len(selected_indices)
    selected_folders = ', '.join([rotations_list[i] for i in selected_indices])
    selection_var.set(selected_folders)

def call_index():
    result = messagebox.askyesno("Confirmation", "Are you sure you want to begin indexing?")
    if result:
        begin_indexing()

def begin_indexing():
    global num_rotations
    global output_filename
    # Check if the output file already exists
    num_suffix = 1
    output_filename = f"{num_rotations}rot_hkli_{num_suffix:03d}.nxs"

    while os.path.exists(os.path.join(workingdir_var.get(), output_filename)):
        num_suffix += 1
        output_filename = f"{num_rotations}rot_hkli_{num_suffix:03d}.nxs"
        
    print(f"Output filename: {output_filename}")
    # Call the index function
    index()

def index():
    global norm
    global H
    global K
    global L
    global output_filename
    # Perform indexing logic here
    print("Indexing in progress...")

    outpath = os.path.join(workingdir_var.get(), output_filename)
    print(f"Outpath = {outpath}")
    nxsetmemory(100000)
    
    # Load the orientation info
    ormpath = os.path.join(ormdir_var.get(), "ormatrix_auto.nxs")
    ormat = nxload(ormpath)
    
    # Orientation matrix from file
    U = ormat.ormatrix.U
    U = U.T  # To match spec convention
    
    # Split the selected_folders string into a list
    selected_folders_list = [folder.strip() for folder in selected_folders.split(',')]

    for i, rotation in enumerate(selected_folders_list):
        stack = nxload(os.path.join(workingdir_var.get(), rotation))

        # Incident energy and wavelength
        WL = stack.geo.wl  # Wavelength
        print('\nwavelength = ' + str(WL))

        success = False
        while not success:
            try:
                print("\nProcessing rotation " + str(i + 1) + " of " + str(len(selected_folders_list)) + "...")
                W2 = anglerock(H, K, L, stack, ormat, WL, U, data, norm, errors, workingdir, i + 1)
                success = True
                print("Stack " + str(i + 1) + " processed successfully.")

            except MemoryError:
                print("Unable to allocate enough memory! Try closing other programs.")
            except OSError:
                print("Unable to allocate enough memory! Try closing other programs.")
            except Exception as e:
                print(e)

            if not success:
                print("Trying again...")
        print("Clearing stack from memory...")
        del stack
        gc.collect()
        print("Memory cleared.")

    dataout = data.clip(0.0) / norm.clip(0.9)

    del norm
    dataout = dataout.reshape(len(H), len(K), len(L))
    H = H.astype('float32')
    K = K.astype('float32')
    L = L.astype('float32')
    H = NXfield(H, name='H', long_name='H')
    K = NXfield(K, name='K', long_name='K')
    L = NXfield(L, name='L', long_name='L')
    dataout = NXfield(dataout, name='counts', long_name='counts')

    G = NXdata(dataout, (H, K, L))

    G.save(outpath)

    


# Define rotations_list here
rotations_list = []

# Initialize num_rotations
num_rotations = 0

root = tk.Tk()
root.title("Indexer")

# Initialize row variable
row = 0

# Check if sys.argv inputs are provided
print(len(sys.argv))
if len(sys.argv) >= 3:
    workingdir_var = StringVar(value=sys.argv[1])
    ormdir_var = StringVar(value=sys.argv[2])
    print("Imported directories from parent application.")
else:
    workingdir_var = StringVar()
    ormdir_var = StringVar()

# Browse for working directory
Label(root, text="Directory to index:").grid(row=row, column=0, pady=5, sticky="w")
workingdir_entry = Entry(root, textvariable=workingdir_var, state="readonly", width=40)
workingdir_entry.grid(row=row + 1, column=0, padx=5, pady=5, sticky="w")
Button(root, text="Browse", command=lambda: browse_for_directory(workingdir_var)).grid(row=row + 1, column=1, padx=5, pady=5, sticky="w")

# Increment row
row += 2

# Browse for orm directory
Label(root, text="ORM directory:").grid(row=row, column=0, pady=5, sticky="w")
ormdir_entry = Entry(root, textvariable=ormdir_var, state="readonly", width=40)
ormdir_entry.grid(row=row + 1, column=0, padx=5, pady=5, sticky="w")
Button(root, text="Browse", command=lambda: browse_for_directory(ormdir_var)).grid(row=row + 1, column=1, padx=5, pady=5, sticky="w")

# Increment row
row += 2

# Display a listbox with available files
Label(root, text="Select stacks to include:").grid(row=row, column=0, pady=5, sticky="w")
listbox = Listbox(root, selectmode="multiple")
listbox.grid(row=row + 1, column=0, padx=5, pady=5, sticky="w")

if len(sys.argv) >= 3:
    update_rotations_list()
    update_listbox()
    print("updated listbox")
    
# Increment row
row += 2

# Button to update selected list
update_button = Button(root, text="Confirm", command=update_selected_list)
update_button.grid(row=row, column=0, padx=5, pady=5, sticky="w")

# Increment row
row += 1

# Display selected stacks
selection_var = StringVar()
Label(root, text="Selected stacks:").grid(row=row, column=0, pady=5, sticky="w")
selected_label = Label(root, textvariable=selection_var)
selected_label.grid(row=row + 1, column=0, padx=5, pady=5, sticky="w")

# Increment row
row += 2

# Button to call indexing function
index_button = Button(root, text="Call index()", command=call_index)
index_button.grid(row=row, column=0, padx=5, pady=5, sticky="w")

root.mainloop()





