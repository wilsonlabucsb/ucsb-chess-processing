import tkinter as tk
from tkinter import filedialog, ttk
import os

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        data_dir.set(folder_path)
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder_path)
        update_folder_list(folder_path)
        os.chdir(folder_path)

def update_folder_list(folder_path):
    folders = [f for f in os.listdir(folder_path) if f.isdigit() and os.path.isdir(os.path.join(folder_path, f))]
    sorted_folders = sorted(folders, key=lambda x: int(x))

    # Clear and update the first Listbox
    folder_listbox.delete(0, tk.END)
    for folder in sorted_folders:
        folder_listbox.insert(tk.END, folder)

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

def select_folders_to_index():
    selected_folders = listbox_new_column.curselection()
    folders_to_index.set(selected_folders)
    selected_folders_label.config(
        text=f"Selected Folders: {', '.join(listbox_new_column.get(index) for index in selected_folders)}")

def run_ormfinder():
    # Get the value of the orm_folder variable
    selected_folder = orm_folder.get()

    # Run the specified code in a new terminal
    ormfinder_path = os.path.join(script_file_path, "auto_ormfinder_tkinter.py")
    os.system(f"python {ormfinder_path} {selected_folder}")

def run_indexer():
    # Get the value of the data_dir variable
    data_dir_val = data_dir.get().replace("\\", "/")
    orm_dir_val = orm_folder.get().replace("\\", "/")

    # Get the selected indices from the listbox
    selected_indices = listbox_new_column.curselection()

    # Retrieve the folder names using the indices
    selected_folders = [listbox_new_column.get(index).replace("\\", "/") for index in selected_indices]

    print(f"Selected folders: {selected_folders}.")

    # Determine the indexing mode
    selected_indexing_mode = indexing_mode.get()

    # Construct the indexer_path based on the indexing mode
    if selected_indexing_mode == "1 stack (faster)":
        indexer_path = os.path.join(script_file_path, "Pil6M_HKLConv_3D_2022_1rot.py")
    elif selected_indexing_mode == "3 stacks (higher quality)":
        indexer_path = os.path.join(script_file_path, "Pil6M_HKLConv_3D_2022_3rot.py")
    else:
        # Default to the original path if the mode is not recognized
        indexer_path = os.path.join(script_file_path, "Pil6M_HKLConv_3D_2022_tkinter.py")

    for folder in selected_folders:
        folder_path = os.path.join(data_dir_val, folder)
        folder_path = folder_path.replace("\\", "/")
        hkl_limits_string = f"{Hlim_var.get()} {Hstep_var.get()} {Klim_var.get()} {Kstep_var.get()} {Llim_var.get()} {Lstep_var.get()}"
        os.system(f"python {indexer_path} {folder_path}"+"/"+f" {orm_dir_val}"+"/ "+ hkl_limits_string)



# Create the main window
root = tk.Tk()
root.title("CHESS Data Processing")

# Create StringVars to store the selected folder path and ORM folder
data_dir = tk.StringVar()
orm_folder = tk.StringVar()
folders_to_index = tk.StringVar()
# Get the filepath of the "ormfinder" script file
script_file_path = os.path.dirname(os.path.abspath(__file__))

# Create a frame for the first column
frame_column1 = tk.Frame(root)
frame_column1.grid(row=0, column=0, pady=10, padx=5, sticky=tk.N)

# Create a label to display the selected folder path
label_text = "Select directory with temperature folders:"
label = tk.Label(frame_column1, text=label_text)
label.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create an Entry widget to display the selected folder path
entry_path = tk.Entry(frame_column1, textvariable=data_dir, state='readonly', width=40)
entry_path.grid(row=1, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a button to open the file dialog
button = tk.Button(frame_column1, text="Browse...", command=select_folder)
button.grid(row=2, column=0, pady=10, padx=5, sticky=tk.W)

# Create a frame for the second column
frame_column2 = tk.Frame(root)
frame_column2.grid(row=0, column=2, pady=10, padx=5, sticky=tk.N)

# Create a label for the folder selection list
listbox_label = tk.Label(frame_column2, text="Select a directory to use as the ORM:")
listbox_label.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a Listbox to display available folders
folder_listbox = tk.Listbox(frame_column2, selectmode=tk.SINGLE, width=40)
folder_listbox.grid(row=1, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a button to select the ORM folder
select_button = tk.Button(frame_column2, text="Confirm", command=select_orm_folder)
select_button.grid(row=2, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a label for the confirmation text
confirmation_label1 = tk.Label(frame_column2, text="")
confirmation_label1.grid(row=3, column=0, columnspan=2, pady=0, padx=5, sticky=tk.W)

# Create a label for the confirmation text
confirmation_label2 = tk.Label(frame_column2, text="")
confirmation_label2.grid(row=4, column=0, columnspan=2, pady=0, padx=5, sticky=tk.W)

# Add a new button to run the ormfinder code
run_button = tk.Button(frame_column2, text="Run ORM Finder", command=run_ormfinder)
run_button.grid(row=5, column=0, pady=20, padx=5, sticky=tk.SW)

# Create a frame for the second column
frame_column3 = tk.Frame(root)
frame_column3.grid(row=0, column=3, pady=10, padx=5, sticky=tk.N)

# Create a new label for the second column
indexing_column_label = tk.Label(frame_column3, text="Select temperatures to index:")
indexing_column_label.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a Listbox for the new column with multi-selection
listbox_new_column = tk.Listbox(frame_column3, selectmode=tk.MULTIPLE, width=40)
listbox_new_column.grid(row=1, column=0, rowspan=2, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a button to select folders in the new column
select_folders_button = tk.Button(frame_column3, text="Confirm", command=select_folders_to_index)
select_folders_button.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a label to display the selected folders
selected_folders_label = tk.Label(frame_column3, text="")
selected_folders_label.grid(row=4, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Dropdown menu for indexing mode
indexing_mode_label = tk.Label(frame_column3, text="Indexing Mode:")
indexing_mode_label.grid(row=5, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

indexing_mode_options = ["1 stack (faster)", "3 stacks (higher quality)"]
indexing_mode = tk.StringVar()
indexing_mode.set(indexing_mode_options[0])  # Default value

indexing_mode_menu = ttk.Combobox(frame_column3, textvariable=indexing_mode, values=indexing_mode_options)
indexing_mode_menu.grid(row=6, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Entry widgets for variables Hlim, Hstep, Klim, Kstep, Llim, and Lstep
Hlim_var = tk.StringVar()
Hstep_var = tk.StringVar()
Klim_var = tk.StringVar()
Kstep_var = tk.StringVar()
Llim_var = tk.StringVar()
Lstep_var = tk.StringVar()
Hlim_var.set(5.1)
Hstep_var.set(0.01)
Klim_var.set(5.1)
Kstep_var.set(0.01)
Llim_var.set(9.1)
Lstep_var.set(0.02)

entry_hlim = tk.Entry(frame_column3, textvariable=Hlim_var)
entry_hstep = tk.Entry(frame_column3, textvariable=Hstep_var)
entry_klim = tk.Entry(frame_column3, textvariable=Klim_var)
entry_kstep = tk.Entry(frame_column3, textvariable=Kstep_var)
entry_llim = tk.Entry(frame_column3, textvariable=Llim_var)
entry_lstep = tk.Entry(frame_column3, textvariable=Lstep_var)

row = 7
tk.Label(frame_column3, text="H limit:").grid(row=row, column=0, padx=5, sticky=tk.W)
entry_hlim.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
row += 1

tk.Label(frame_column3, text="H step:").grid(row=row, column=0, padx=5, sticky=tk.W)
entry_hstep.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
row += 1

tk.Label(frame_column3, text="K limit:").grid(row=row, column=0, padx=5, sticky=tk.W)
entry_klim.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
row += 1

tk.Label(frame_column3, text="K step:").grid(row=row, column=0, padx=5, sticky=tk.W)
entry_kstep.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
row += 1

tk.Label(frame_column3, text="L limit:").grid(row=row, column=0, padx=5, sticky=tk.W)
entry_llim.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
row += 1

tk.Label(frame_column3, text="L step:").grid(row=row, column=0, padx=5, sticky=tk.W)
entry_lstep.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
row += 1

# Button to begin indexing
run_index_button = tk.Button(frame_column3, text="Run Indexer", command=run_indexer)
run_index_button.grid(row=13, column=0, columnspan=2, pady=20, padx=5, sticky=tk.SW)


# Run the Tkinter event loop
root.mainloop()
