import os
import tkinter as tk
from tkinter import filedialog, ttk


def select_folder():
  folder_path = filedialog.askdirectory()
  if folder_path:
    data_dir.set(folder_path)
    entry_path.delete(0, tk.END)
    entry_path.insert(0, folder_path)
    update_folder_list(folder_path)

def select_out_folder():
  folder_path = filedialog.askdirectory()
  if folder_path:
    out_dir.set(folder_path)
    entry_path_out.delete(0, tk.END)
    entry_path_out.insert(0, folder_path)

def select_calib_file():
  file_path = filedialog.askopenfilename(filetypes=[("PONI File", "*.poni")])
  if file_path:
    calib_file.set(file_path)
    entry_path_calib.delete(0, tk.END)
    entry_path_calib.insert(0, file_path)


def select_spec_file():
  file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
  if file_path:
    spec_file.set(file_path)
    entry_path_spec.delete(0, tk.END)
    entry_path_spec.insert(0, file_path)


def select_mask_file():
  file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
  if file_path:
    mask_file.set(file_path)
    entry_path_mask.delete(0, tk.END)
    entry_path_mask.insert(0, file_path)



def update_folder_list(folder_path):
  folders = [f for f in os.listdir(folder_path) if f.isdigit() and os.path.isdir(os.path.join(folder_path, f))]
  sorted_folders = sorted(folders, key=lambda x: int(x))

  # # Clear and update the first Listbox
  # folder_listbox.delete(0, tk.END)
  # for folder in sorted_folders:
  #   folder_listbox.insert(tk.END, folder)

  # Clear and update the second Listbox
  listbox_new_column.delete(0, tk.END)
  for folder in sorted_folders:
    listbox_new_column.insert(tk.END, folder)


def select_orm_folder():
  selected_index = folder_listbox.curselection()
  if selected_index:
    selected_folder = folder_listbox.get(selected_index)
    selected_path = os.path.join(os.getcwd(), selected_folder)
    orm_folder.set(selected_path)

    # Check for the existence of "ormatrix_auto.nxs"
    confirmation_label1.config(text=f" Looking for orientation matrix at {selected_folder} K...")
    print(os.listdir(selected_path))
    orm_file_path = os.path.join(selected_folder, "ormatrix_auto.nxs")
    if os.path.exists(orm_file_path):
      confirmation_label2.config(text=" ormatrix_auto.nxs found!")
    else:
      confirmation_label2.config(text=" No orientation matrix found.\nUse ORM Finder to solve before indexing.")


def select_folders_to_stack():
  global selected_folders_names
  selected_folders_indices = listbox_new_column.curselection()
  folders_to_stack.set(selected_folders_indices)
  selected_folders_names = [listbox_new_column.get(index) for index in selected_folders_indices]
  selected_folders_label.config(
    text=f"Selected Folders: {', '.join(listbox_new_column.get(index) for index in selected_folders_indices)}")


def queue_indexer():
  global job_file_path, selected_folders_names

  # Get the value of the data_dir variable
  data_dir_val = data_dir.get().replace("\\", "/")
  out_dir_val = out_dir.get().replace("\\", "/")
  spec_file_val = spec_file.get().replace("\\", "/")
  calib_file_val = calib_file.get().replace("\\", "/")
  mask_file_val = mask_file.get().replace("\\", "/")

  print(f"Selected folders: {selected_folders_names}.")

  # Determine the indexing mode
  # selected_indexing_mode = indexing_mode.get()

  # Construct the stacker path
  stacker_path = os.path.join(script_file_path, "stack_em_all.py")

  for folder in selected_folders_names:
    folder_path = os.path.join(data_dir_val, folder)
    folder_path = folder_path.replace("\\", "/")

    scan_folders = []  # Empty list to store folder names
    for scan_folder in os.listdir(folder_path + '/'):
      scan_folders.append(scan_folder)
    scan_folders.sort()

    # For reference:
    # specfile = sys.argv[1]
    # calibfile = sys.argv[2]
    # maskfile = sys.argv[3]
    # sample_name = sys.argv[4]
    # scan_num = int(sys.argv[5])
    # temperature = int(sys.argv[6])
    # temperdir = sys.argv[6]
    # raw_dir = sys.argv[7]
    # outpath = sys.argv[8]

    for scan_folder in scan_folders:
      command = f"python {stacker_path} {spec_file_val} {calib_file_val} {mask_file_val} {scan_folder[:-4]} {scan_folder[-3:]} {folder} {data_dir_val+'/'+folder+'/'+scan_folder+'/'} {out_dir_val+'/'+folder+'/'}"

      # Create or append to the job file
      job_file_path = os.path.join(script_file_path, "job_file.txt")

      with open(job_file_path, "a") as job_file:
        job_file.write(command + "\n")
  # Call the function to update job queue
  update_indexing_queue()


def update_indexing_queue():
  global job_file_path
  job_file_path = os.path.join(script_file_path, "job_file.txt")
  # Read the job file and extract the second filepath from each line
  with open(job_file_path, "r") as job_file:
    indexing_queue_listbox.delete(0, tk.END)  # Clear the Listbox
    for line in job_file:
      parts = line.split()
      if len(parts) >= 2:
        status = parts[-1] if len(parts) > 2 else ""  # Check for status
        second_filepath = parts[8]

        # Check if the job is not completed
        if "[COMPLETED]" not in status:
          # Find the strings "3rot" or "1rot" in the line
          if "3rot" in line:
            indexing_queue_listbox.insert(tk.END, "3rot " + second_filepath)
          elif "1rot" in line:
            indexing_queue_listbox.insert(tk.END, "1rot " + second_filepath)
          elif "stack" in line:
            indexing_queue_listbox.insert(tk.END, "stack " + second_filepath)


def delete_command_from_job_file(command):
  # Read the existing contents of the job file
  with open(job_file_path, "r") as job_file:
    lines = job_file.readlines()

  # Write the lines back to the file excluding the line with the selected command
  with open(job_file_path, "w") as job_file:
    for line in lines:
      if command not in line:
        job_file.write(line)


# Function to delete the selected command
def delete_selected_command():
  selected_index = indexing_queue_listbox.curselection()
  if selected_index:
    selected_command = indexing_queue_listbox.get(selected_index)
    delete_command_from_job_file(selected_command)
    update_indexing_queue()  # Refresh the indexing queue listbox


def open_new_terminal():
  # Commands to activate conda environment and run Python script
  commands = [
    "conda activate chess",
    "python start_queue.py"
  ]

  # Construct the full command based on the OS
  if tk.Tk().tk.call('tk', 'windowingsystem') == 'x11':
    # On Linux
    command = f"xterm -e {'; '.join(commands)}"
  elif tk.Tk().tk.call('tk', 'windowingsystem') == 'win32':
    # On Windows
    command = f"cmd /K {' && '.join(commands)}"

  # Execute the command in a new process
  subprocess.Popen(command, shell=True)


#############################################################################

# Create the main window
root = tk.Tk()
root.title("CHESS Frame Stacking")


# Create StringVars to store the selected folder path and ORM folder
data_dir = tk.StringVar()
# orm_folder = tk.StringVar()
out_dir = tk.StringVar()
calib_file = tk.StringVar()
spec_file = tk.StringVar()
mask_file = tk.StringVar()
folders_to_stack = tk.StringVar()

# Get the filepath of the script files
script_file_path = os.path.dirname(os.path.abspath(__file__))

#########################################################################

# Create a frame for the first column
frame_column1 = tk.Frame(root)
frame_column1.grid(row=0, column=0, pady=10, padx=5, sticky=tk.N)

## Select raw folder #########
row = 0
# Create a label to display the selected folder path
label_text = "Select raw frames directory with temperature folders:"
label = tk.Label(frame_column1, text=label_text)
label.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1
# Create an Entry widget to display the selected folder path
entry_path = tk.Entry(frame_column1, textvariable=data_dir, state='readonly', width=40)
entry_path.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1
# Create a button to open the file dialog
button = tk.Button(frame_column1, text="Browse...", command=select_folder)
button.grid(row=row, column=0, pady=10, padx=5, sticky=tk.W)
row+=1

## Select out folder #########
# Create a label to display the selected folder path
label_text_out = "Select stacked frames directory:"
label_out = tk.Label(frame_column1, text=label_text_out)
label_out.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1
# Create an Entry widget to display the selected folder path
entry_path_out = tk.Entry(frame_column1, textvariable=out_dir, state='readonly', width=40)
entry_path_out.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1
# Create a button to open the file dialog
button_out = tk.Button(frame_column1, text="Browse...", command=select_out_folder)
button_out.grid(row=row, column=0, pady=10, padx=5, sticky=tk.W)
row+=1

## Select calibration file (.poni) #########
# Create a label to display the selected folder path
label_text_calib = "Select calibration (*.poni) file:"
label_calib = tk.Label(frame_column1, text=label_text_calib)
label_calib.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1
# Create an Entry widget to display the selected folder path
entry_path_calib = tk.Entry(frame_column1, textvariable=calib_file, state='readonly', width=40)
entry_path_calib.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1
# Create a button to open the file dialog
button_calib = tk.Button(frame_column1, text="Browse...", command=select_calib_file)
button_calib.grid(row=row, column=0, pady=10, padx=5, sticky=tk.W)
row+=1

## Select spec file #########
# Create a label to display the selected folder path
label_text_spec = "Select spec file:"
label_spec = tk.Label(frame_column1, text=label_text_spec)
label_spec.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1
# Create an Entry widget to display the selected folder path
entry_path_spec = tk.Entry(frame_column1, textvariable=spec_file, state='readonly', width=40)
entry_path_spec.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1
# Create a button to open the file dialog
button_spec = tk.Button(frame_column1, text="Browse...", command=select_spec_file)
button_spec.grid(row=row, column=0, pady=10, padx=5, sticky=tk.W)
row+=1

## Select mask file #########
# Create a label to display the selected folder path
label_text_mask = "Select mask file:"
label_mask = tk.Label(frame_column1, text=label_text_mask)
label_mask.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1
# Create an Entry widget to display the selected folder path
entry_path_mask = tk.Entry(frame_column1, textvariable=mask_file, state='readonly', width=40)
entry_path_mask.grid(row=row, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
row+=1
# Create a button to open the file dialog
button_mask = tk.Button(frame_column1, text="Browse...", command=select_mask_file)
button_mask.grid(row=row, column=0, pady=10, padx=5, sticky=tk.W)
row+=1


#########################################################################

# # Create a separator between the columns
# separator1 = ttk.Separator(root, orient="vertical")
# separator1.grid(row=0, column=1, sticky="ns", padx=5, pady=10)
#
# # Create a frame for the second column
# frame_column2 = tk.Frame(root)
# frame_column2.grid(row=0, column=2, pady=10, padx=5, sticky=tk.N)
#
# # Create a label for the folder selection list
# listbox_label = tk.Label(frame_column2, text="Select a directory to use as the ORM:")
# listbox_label.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
#
# # Create a Listbox to display available folders
# folder_listbox = tk.Listbox(frame_column2, selectmode=tk.SINGLE, width=40)
# folder_listbox.grid(row=1, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
#
# # Create a button to select the ORM folder
# select_button = tk.Button(frame_column2, text="Confirm", command=select_orm_folder)
# select_button.grid(row=2, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
#
# # Create a label for the confirmation text
# confirmation_label1 = tk.Label(frame_column2, text="")
# confirmation_label1.grid(row=3, column=0, columnspan=2, pady=0, padx=5, sticky=tk.W)
#
# # Create a label for the confirmation text
# confirmation_label2 = tk.Label(frame_column2, text="")
# confirmation_label2.grid(row=4, column=0, columnspan=2, pady=0, padx=5, sticky=tk.W)
#
# # Add a new button to run the ormfinder code
# run_button = tk.Button(frame_column2, text="Run ORM Finder", command=run_ormfinder)
# run_button.grid(row=5, column=0, pady=20, padx=5, sticky=tk.SW)

##########################################################################

# Create a separator between the columns
separator2 = ttk.Separator(root, orient="vertical")
separator2.grid(row=0, column=3, sticky="ns", padx=5, pady=10)

# Create a frame for the second column
frame_column3 = tk.Frame(root)
frame_column3.grid(row=0, column=4, pady=10, padx=5, sticky=tk.N)

# Create a new label for the second column
indexing_column_label = tk.Label(frame_column3, text="Select temperatures to stack:")
indexing_column_label.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a Listbox for the new column with multi-selection
listbox_new_column = tk.Listbox(frame_column3, selectmode=tk.MULTIPLE, width=40)
listbox_new_column.grid(row=1, column=0, rowspan=2, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a button to select folders in the new column
select_folders_button = tk.Button(frame_column3, text="Confirm", command=select_folders_to_stack)
select_folders_button.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a label to display the selected folders
selected_folders_label = tk.Label(frame_column3, text="")
selected_folders_label.grid(row=4, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# # Dropdown menu for indexing mode
# indexing_mode_label = tk.Label(frame_column3, text="Indexing Mode:")
# indexing_mode_label.grid(row=5, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)
#
# indexing_mode_options = ["1 stack (faster)", "3 stacks (higher quality)"]
# indexing_mode = tk.StringVar()
# indexing_mode.set(indexing_mode_options[0])  # Default value
#
# indexing_mode_menu = ttk.Combobox(frame_column3, textvariable=indexing_mode, values=indexing_mode_options, width=30)
# indexing_mode_menu.grid(row=6, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Entry widgets for variables Hlim, Hstep, Klim, Kstep, Llim, and Lstep
# Hlim_var = tk.StringVar()
# Hstep_var = tk.StringVar()
# Klim_var = tk.StringVar()
# Kstep_var = tk.StringVar()
# Llim_var = tk.StringVar()
# Lstep_var = tk.StringVar()
# Hlim_var.set(5.1)
# Hstep_var.set(0.01)
# Klim_var.set(5.1)
# Kstep_var.set(0.01)
# Llim_var.set(9.1)
# Lstep_var.set(0.02)

# entry_hlim = tk.Entry(frame_column3, textvariable=Hlim_var)
# entry_hstep = tk.Entry(frame_column3, textvariable=Hstep_var)
# entry_klim = tk.Entry(frame_column3, textvariable=Klim_var)
# entry_kstep = tk.Entry(frame_column3, textvariable=Kstep_var)
# entry_llim = tk.Entry(frame_column3, textvariable=Llim_var)
# entry_lstep = tk.Entry(frame_column3, textvariable=Lstep_var)

# row = 7
# tk.Label(frame_column3, text="H limit:").grid(row=row, column=0, padx=5, sticky=tk.W)
# entry_hlim.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
# row += 1
#
# tk.Label(frame_column3, text="H step:").grid(row=row, column=0, padx=5, sticky=tk.W)
# entry_hstep.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
# row += 1
#
# tk.Label(frame_column3, text="K limit:").grid(row=row, column=0, padx=5, sticky=tk.W)
# entry_klim.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
# row += 1
#
# tk.Label(frame_column3, text="K step:").grid(row=row, column=0, padx=5, sticky=tk.W)
# entry_kstep.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
# row += 1
#
# tk.Label(frame_column3, text="L limit:").grid(row=row, column=0, padx=5, sticky=tk.W)
# entry_llim.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
# row += 1
#
# tk.Label(frame_column3, text="L step:").grid(row=row, column=0, padx=5, sticky=tk.W)
# entry_lstep.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
# row += 1

# Button to begin indexing
run_index_button = tk.Button(frame_column3, text="Submit to queue", command=queue_indexer)
run_index_button.grid(row=13, column=0, columnspan=2, pady=20, padx=5, sticky=tk.SW)

##########################################################################

# Create a frame for the second column
frame_column4 = tk.Frame(root)
frame_column4.grid(row=0, column=6, pady=10, padx=5, sticky=tk.N)

row = 0
tk.Label(frame_column4, text="Job Queue:").grid(row=row, column=0, padx=5, pady=10, sticky=tk.W)
row += 1

# Create a Listbox for the indexing queue
indexing_queue_listbox = tk.Listbox(frame_column4, selectmode=tk.SINGLE, width=50)
indexing_queue_listbox.grid(row=row, column=0, pady=10, padx=5, sticky=tk.W)
row += 1

update_indexing_queue()

updated_queue_button = tk.Button(frame_column4, text="Refresh queue", command=update_indexing_queue)
updated_queue_button.grid(row=row, column=0, pady=10, padx=5, sticky=tk.W)
row += 1

# Add this button in your frame_column4 initialization section
delete_button = tk.Button(frame_column4, text="Delete Selected", command=delete_selected_command)
delete_button.grid(row=row, column=0, pady=10, padx=5, sticky=tk.W)
row += 1


tk.Label(frame_column4, text="Run start_queue.py to begin queue.").grid(row=row, column=0, padx=5, pady=10, sticky=tk.W)
row += 1

# Run the Tkinter event loop
root.mainloop()
#
# #################################################################
# # INPUTS
# folder_name = 'RbV3Sb5Sn'
# sample_name = 'ACS5_11_s7'
# specfile='M:/wilson-4148-a_AVSS/raw6M/RbV3Sb5Sn/'+folder_name
# calibfile="M:/wilson-4148-a_AVSS/raw6M/calibrations/CeO2_26keV.poni"
# maskfile="M:/wilson-4148-a_AVSS/raw6M/calibrations/mask_D2.edf"
# raw_dir = 'M:/wilson-4148-a_AVSS/raw6M/'+folder_name+'/'+sample_name+'/'
# out_dir = 'M:/wilson-4148-a_AVSS/ACS5_11_s7_15K_StacknIndex/'+folder_name+'/'+sample_name+'/'
# #################################################################
#
#
#
#
# folders=[] # Empty list to store folder names
# for item in os.listdir(raw_dir):
#   try:
#     folders.append(int(item)) # If folder can be converted to int, add it
#   except:
#     pass # Otherwise don't add it
# folders.sort() # Sort from low to high T
# folders = [str(i) for i in folders] # Convert to strings
#
#
# print('\nRaw directory: ' + raw_dir)
# print('\nAvailable folders: ')
# [print("["+str(i)+"] "+str(name)) for i,name in enumerate(folders)]
#
# selection_str = input("Enter a comma-separated list of indices to select for stacking: ")
# indices = [int(i) for i in selection_str.split(',')]
# folders = [folders[i] for i in indices]
#
# print('\n\nSelected folders: ' + str(folders))
#
#
#
#
# val = input('Continue? (y/n): ')
# if val=='y':
#   for folder in folders:
#     scan_folders=[] # Empty list to store folder names
#     for scan_folder in os.listdir(raw_dir+folder+'/'):
#       scan_folders.append(scan_folder)
#     scan_folders.sort()
#
#     print('\nScan directory: ' + raw_dir + folder)
#     print('\nAvailable folders: ')
#     [print("["+str(i)+"] "+str(name)) for i,name in enumerate(scan_folders)]
#
#     selection_str = input("Enter a comma-separated list of indices to select for stacking: ")
#     indices = [int(i) for i in selection_str.split(',')]
#     scan_folders = [scan_folders[i] for i in indices]
#
#     print('\n\nSelected folders: ' + str(scan_folders))
#
#     for scan_folder in scan_folders:
#       scan_num=scan_folder[-3:]
#       temperature=folder
#       raw_path = raw_dir+folder+"/"+scan_folder+"/"
#       out_path = out_dir+folder+"/"
#       os.system("python SGA_stack_em_all_2022_batch.py"+" "+specfile+" "+calibfile+" "+maskfile+" "+sample_name+" "+scan_num+" "+temperature+" "+raw_path+" "+out_path)
# else:
#   pass
