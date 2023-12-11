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
        selected_path = os.path.join(os.getcwd(),selected_folder)
        orm_folder.set(selected_path)

        # Check for the existence of "ormatrix_auto.nxs"
        confirmation_label1.config(text=f"\t Using {selected_folder} K scan to solve ORM.")
        print(os.listdir(selected_path))
        orm_file_path = os.path.join(selected_folder, "ormatrix_auto.nxs")
        if os.path.exists(orm_file_path):
            confirmation_label2.config(text="\t ormatrix_auto.nxs found!")
        else:
            confirmation_label2.config(text="\t No existing ORM found.")

def select_folders_to_index():
    selected_folders = listbox_new_column.curselection()
    folders_to_index.set(selected_folders)
    selected_folders_label.config(text=f"Selected Folders: {', '.join(listbox_new_column.get(index) for index in selected_folders)}")

def run_ormfinder():
    # Get the value of the orm_folder variable
    selected_folder = orm_folder.get()

    # Run the specified code in a new terminal
    ormfinder_path = os.path.join(script_file_path,"auto_ormfinder_tkinter.py")
    os.system(f"python {ormfinder_path} {selected_folder}")

def run_indexer():
    # Get the value of the data_dir variable
    data_dir_val = data_dir.get()
    orm_dir_val = orm_folder.get()
    
    # Get the selected indices from the listbox
    selected_indices = listbox_new_column.curselection()
    
    # Retrieve the folder names using the indices
    selected_folders = [listbox_new_column.get(index) for index in selected_indices]
    
    print(f"Selected folders: {selected_folders}")
    
    # Run the specified code in a new terminal
    indexer_path = os.path.join(script_file_path, "Pil6M_HKLConv_3D_2022_tkinter.py")
    
    for folder in selected_folders:
        folder_path = os.path.join(data_dir_val, folder)
        os.system(f"python {indexer_path} {folder_path} {orm_dir_val}")



# Create the main window
root = tk.Tk()
root.title("CHESS Data Processing")

# Create StringVars to store the selected folder path and ORM folder
data_dir = tk.StringVar()
orm_folder = tk.StringVar()
folders_to_index = tk.StringVar()
# Get the filepath of the "ormfinder" script file
script_file_path = os.path.dirname(os.path.abspath(__file__))


# Create a label to display the selected folder path
label_text = "Select directory with temperature folders:"
label = tk.Label(root, text=label_text)
label.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create an Entry widget to display the selected folder path
entry_path = tk.Entry(root, textvariable=data_dir, state='readonly', width=40)
entry_path.grid(row=1, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a button to open the file dialog
button = tk.Button(root, text="Browse...", command=select_folder)
button.grid(row=2, column=0, pady=10, padx=5, sticky=tk.W)

# Add a new line before the Listbox
tk.Label(root, text="").grid(row=2, column=0)

# Create a label for the folder selection list
listbox_label = tk.Label(root, text="Select a directory to use as the ORM:")
listbox_label.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a Listbox to display available folders
folder_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=40)
folder_listbox.grid(row=4, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a button to select the ORM folder
select_button = tk.Button(root, text="Select ORM Folder", command=select_orm_folder)
select_button.grid(row=5, column=0, columnspan=2, pady=10, padx=5, sticky=tk.W)

# Create a label for the confirmation text
confirmation_label1 = tk.Label(root, text="")
confirmation_label1.grid(row=6, column=0, columnspan=2, pady=0, padx=5, sticky=tk.W)

# Create a label for the confirmation text
confirmation_label2 = tk.Label(root, text="")
confirmation_label2.grid(row=7, column=0, columnspan=2, pady=0, padx=5, sticky=tk.W)

# Add a new button to run the ormfinder code
run_button = tk.Button(root, text="Run ORM Finder", command=run_ormfinder)
run_button.grid(row=8, column=0, pady=20, padx=5, sticky=tk.W)

# Add a new column to the right with a new label
indexing_column_label = tk.Label(root, text="Select temperatures to index:")
indexing_column_label.grid(row=9, column=0, pady=10, padx=5, sticky=tk.W)

# Create a Listbox for the new column with multi-selection
listbox_new_column = tk.Listbox(root, selectmode=tk.MULTIPLE, width=40)
listbox_new_column.grid(row=10, column=0, rowspan=2, pady=10, padx=5, sticky=tk.W)

# Create a button to select folders in the new column
select_folders_button = tk.Button(root, text="Select Folders", command=select_folders_to_index)
select_folders_button.grid(row=12, column=0, pady=10, padx=5, sticky=tk.W)

# Create a label to display the selected folders
selected_folders_label = tk.Label(root, text="")
selected_folders_label.grid(row=13, column=0, pady=10, padx=5, sticky=tk.W)

# Button to begin indexing
run_index_button = tk.Button(root, text="Run Indexer", command=run_indexer)
run_index_button.grid(row=14, column=0, pady=20, padx=5, sticky=tk.W)

# Run the Tkinter event loop
root.mainloop()
