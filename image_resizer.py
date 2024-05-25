import os
import sys
from PIL import Image, ImageTk
from tkinter import filedialog, Tk, Label, Button, messagebox, IntVar, Radiobutton, Frame, StringVar, OptionMenu, Entry, Checkbutton, Text, Scrollbar, Menu, Toplevel, Spinbox, TclError
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import ttk
import logging
from logging.handlers import RotatingFileHandler
from collections import deque
from config_manager import load_settings, save_settings, get_setting, set_setting
from recent_file_manager import load_recent_files, save_recent_files

# Correct logging configuration
log_handler = RotatingFileHandler('image_resizer.log', maxBytes=5000000, backupCount=5)
logging.basicConfig(handlers=[log_handler], level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

# Deque to store the last N saved files
last_files = deque(maxlen=20)

def load_initial_settings():
    global save_directory, size_var, format_var, maintain_aspect_ratio_var, last_files
    save_directory = get_setting('Settings', 'last_save_directory', script_directory)
    print(f"Initial save directory loaded: {save_directory}")  # Debug statement
    if save_directory:
        save_directory_label.config(text=f"Save Directory: {save_directory}")
    size_var.set(get_setting('Settings', 'default_size', 0, int))
    format_var.set(get_setting('Settings', 'default_format', 'ICO'))
    maintain_aspect_ratio_var.set(get_setting('Settings', 'maintain_aspect_ratio', 0, int))
    last_files = deque(load_recent_files(), maxlen=get_setting('Settings', 'recent_files_limit', 20, int))
    update_last_files_display()  # Ensure recent files are displayed on startup

def load_image(file_path=None):
    global image_path, image, photo_image
    image_path = None
    if file_path:
        image_path = file_path
    else:
        initialdir = get_setting('Settings', 'last_load_directory', '')
        image_path = filedialog.askopenfilename(
            title="Select an Image",
            initialdir=initialdir,
            filetypes=[("All Images", "*.jpg;*.png;*.ico;*.bmp;*.tiff;*.gif"), 
                       ("JPEG Images", "*.jpg"), ("PNG Images", "*.png"), 
                       ("ICO Files", "*.ico"), ("BMP Files", "*.bmp"), 
                       ("TIFF Files", "*.tiff"), ("GIF Files", "*.gif")]
        )
    if image_path:
        try:
            image = Image.open(image_path)
            display_image()
            set_setting('Settings', 'last_load_directory', os.path.dirname(image_path))
            logging.info(f"Loaded image: {image_path}")
        except (IOError, OSError) as e:
            logging.error(f"Error loading image: {str(e)}")
            messagebox.showerror("Error", f"Error loading image: {str(e)}")
    else:
        image = None

def display_image():
    global image_label, photo_image
    if image:
        try:
            image.thumbnail((300, 300))
            photo_image = ImageTk.PhotoImage(image)
            image_label.config(image=photo_image)
            image_label.image = photo_image
        except (AttributeError, TclError):
            pass

def load_default_image():
    global image, photo_image
    image = Image.new("RGB", (300, 300), color="grey")
    photo_image = ImageTk.PhotoImage(image)
    image_label.config(image=photo_image)
    image_label.image = photo_image

def resize_and_save():
    if not hasattr(image, "resize"):
        messagebox.showerror("Error", "Please select an image.")
        return

    custom_width = custom_width_var.get()
    custom_height = custom_height_var.get()

    if custom_width.isdigit() and custom_height.isdigit():
        selected_size = (int(custom_width), int(custom_height))
        size_var.set(0)
    elif size_var.get() != 0:
        selected_size = (size_var.get(), size_var.get())
    else:
        messagebox.showerror("Error", "Please enter valid custom width and height or select a size.")
        return

    output_format = format_var.get()
    if output_format not in ["ICO", "PNG", "JPG", "BMP", "TIFF", "GIF"]:
        messagebox.showerror("Error", "Please select a valid output format.")
        return

    try:
        if maintain_aspect_ratio_var.get() == 1 and selected_size[0] != selected_size[1]:
            image_aspect_ratio = image.width / image.height
            if selected_size[0] / selected_size[1] > image_aspect_ratio:
                new_size = (int(selected_size[1] * image_aspect_ratio), selected_size[1])
            else:
                new_size = (selected_size[0], int(selected_size[0] / image_aspect_ratio))
        else:
            new_size = selected_size

        resized_image = image.resize(new_size, Image.LANCZOS)

        if output_format == "JPG":
            resized_image = resized_image.convert("RGB")

        filename, ext = os.path.splitext(image_path)
        new_ext = '.' + output_format.lower()
        new_filename = f"{os.path.basename(filename)}_{new_size[0]}x{new_size[1]}{new_ext}"

        print(f"Using save directory: {save_directory}")  # Debug statement
        if save_directory:
            new_filepath = os.path.join(save_directory, new_filename)
        else:
            new_filepath = os.path.join(os.path.dirname(image_path), new_filename)

        resized_image.save(new_filepath, format=output_format)
        logging.info(f"Image resized and saved to: {new_filepath}")
        open_folder_button.config(state="normal")
        saved_filepath.set(new_filepath)
        add_to_last_files(new_filepath)
    except Exception as e:
        logging.error(f"Failed to resize and save image: {str(e)}")
        messagebox.showerror("Error", f"Failed to resize and save image: {str(e)}")

        
def open_folder(filepath=None):
    if not filepath:
        filepath = saved_filepath.get()
        if not filepath:
            messagebox.showinfo("Info", "No file saved yet.")
            return

    folder_path = os.path.dirname(filepath)
    try:
        if os.name == 'nt':
            os.startfile(folder_path)
        elif os.name == 'posix':
            subprocess.Popen(['open', folder_path])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open folder: {str(e)}")

def select_save_directory():
    global save_directory
    selected_directory = filedialog.askdirectory(title="Select Save Directory", initialdir=save_directory)
    if selected_directory:
        save_directory = selected_directory
        save_directory_label.config(text=f"Save Directory: {save_directory}")
        set_setting('Settings', 'last_save_directory', save_directory)
        save_settings()
        print(f"Save directory updated to: {save_directory}")  # Debug statement

def add_to_last_files(filepath):
    last_files.append(filepath)
    update_last_files_display()
    save_recent_files(last_files)

def load_recent_files():
    config = load_settings()
    files = []
    if 'Files' in config:
        for key in sorted(config['Files'], key=lambda k: int(k.split('_')[1])):
            files.append(config['Files'][key])
    return files
def update_last_files_display():
    last_files_text.config(state="normal")
    last_files_text.delete(1.0, "end")
    for filepath in last_files:
        last_files_text.insert("end", filepath + "\n")
    last_files_text.config(state="disabled")
    last_files_text.see("end")  # Scroll to the bottom

def clear_last_files():
    last_files.clear()
    update_last_files_display()
    clear_last_files_from_config()

def clear_last_files_from_config():
    config = load_settings()
    if 'Files' in config:
        config.remove_section('Files')
    save_settings(config)    

def validate_custom_size(event=None):
    custom_width = custom_width_var.get()
    custom_height = custom_height_var.get()
    if custom_width.isdigit() and custom_height.isdigit():
        size_var.set(0)
    elif not custom_width.isdigit() or not custom_height.isdigit():
        size_var.set(0)

def clear_custom_size():
    custom_width_var.set("")
    custom_height_var.set("")
    size_var.set(0)

def resize_and_save_batch():
    file_paths = filedialog.askopenfilenames(
        title="Select Images for Batch Processing",
        initialdir=get_setting('Settings', 'last_load_directory', ''),
        filetypes=[("All Images", "*.jpg;*.png;*.ico;*.bmp;*.tiff;*.gif"), ("JPEG Images", "*.jpg"), ("PNG Images", "*.png"), 
                   ("ICO Files", "*.ico"), ("BMP Files", "*.bmp"), ("TIFF Files", "*.tiff"), ("GIF Files", "*.gif")]
    )

    if not file_paths:
        return

    custom_width = custom_width_var.get()
    custom_height = custom_height_var.get()

    if custom_width.isdigit() and custom_height.isdigit():
        selected_size = (int(custom_width), int(custom_height))
        size_var.set(0)
    elif size_var.get() != 0:
        selected_size = (size_var.get(), size_var.get())
    else:
        messagebox.showerror("Error", "Please enter valid custom width and height or select a size.")
        return

    output_format = format_var.get()
    if output_format not in ["ICO", "PNG", "JPG", "BMP", "TIFF", "GIF"]:
        messagebox.showerror("Error", "Please select a valid output format.")
        return

    progress["maximum"] = len(file_paths)
    progress["value"] = 0

    for idx, file_path in enumerate(file_paths):
        try:
            img = Image.open(file_path)
            if maintain_aspect_ratio_var.get() == 1 and selected_size[0] != selected_size[1]:
                image_aspect_ratio = img.width / img.height
                if selected_size[0] / selected_size[1] > image_aspect_ratio:
                    new_size = (int(selected_size[1] * image_aspect_ratio), selected_size[1])
                else:
                    new_size = (selected_size[0], int(selected_size[0] / image_aspect_ratio))
            else:
                new_size = selected_size

            resized_img = img.resize(new_size, Image.LANCZOS)

            if output_format == "JPG":
                resized_img = resized_img.convert("RGB")

            filename, ext = os.path.splitext(file_path)
            new_ext = '.' + output_format.lower()
            new_filename = f"{os.path.basename(filename)}_{new_size[0]}x{new_size[1]}{new_ext}"

            if save_directory:
                new_filepath = os.path.join(save_directory, new_filename)
            else:
                new_filepath = os.path.join(os.path.dirname(file_path), new_filename)

            resized_img.save(new_filepath, format=output_format)
            logging.info(f"Image resized and saved to: {new_filepath}")
            add_to_last_files(new_filepath)

            progress["value"] = idx + 1
            root.update_idletasks()
        except Exception as e:
            logging.error(f"Failed to resize and save image {file_path}: {str(e)}")

    messagebox.showinfo("Info", "Batch processing completed.")
    open_folder_button.config(state="normal")
    progress["value"] = 0

def show_settings():
    settings_window = Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("620x300")
    settings_window.attributes('-topmost', True)  # Ensure the settings window stays on top

    settings_frame = Frame(settings_window)
    settings_frame.pack(fill="both", expand=True)

    Label(settings_frame, text="Settings", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=10)

    Label(settings_frame, text="Default Save Directory:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    def_save_dir_entry = Entry(settings_frame, width=50)
    def_save_dir_entry.grid(row=1, column=1, pady=5)
    def_save_dir_entry.insert(0, save_directory)

    def select_directory(entry_widget):
        settings_window.attributes('-topmost', False)  # Remove always-on-top attribute before opening the dialog
        directory = filedialog.askdirectory(title="Select Directory")
        settings_window.attributes('-topmost', True)  # Re-enable always-on-top attribute after closing the dialog
        if directory:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, directory)
            set_setting('Settings', 'last_save_directory', directory)  # Save the directory immediately

    def save_def_save_dir():
        set_setting('Settings', 'last_save_directory', def_save_dir_entry.get())
        save_directory_label.config(text=f"Save Directory: {def_save_dir_entry.get()}")  # Update the label immediately

    def_save_dir_button = Button(settings_frame, text="Browse", command=lambda: select_directory(def_save_dir_entry))
    def_save_dir_button.grid(row=1, column=2, padx=5)

    Label(settings_frame, text="Default Load Directory:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    def_load_dir_entry = Entry(settings_frame, width=50)
    def_load_dir_entry.grid(row=2, column=1, pady=5)
    def_load_dir_entry.insert(0, get_setting('Settings', 'last_load_directory', ''))

    def save_def_load_dir():
        set_setting('Settings', 'last_load_directory', def_load_dir_entry.get())

    def_load_dir_button = Button(settings_frame, text="Browse", command=lambda: select_directory(def_load_dir_entry))
    def_load_dir_button.grid(row=2, column=2, padx=5)

    Label(settings_frame, text="Recent Files Limit:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    rec_files_limit_spinbox = Spinbox(settings_frame, from_=1, to=100, width=5)
    rec_files_limit_spinbox.grid(row=3, column=1, pady=5)
    rec_files_limit_spinbox.delete(0, "end")
    rec_files_limit_spinbox.insert(0, int(get_setting('Settings', 'recent_files_limit', 20)))

    def save_rec_files_limit():
        global last_files
        new_limit = int(rec_files_limit_spinbox.get())
        last_files = deque(last_files, maxlen=new_limit)
        set_setting('Settings', 'recent_files_limit', new_limit)
        save_recent_files(list(last_files))

    Label(settings_frame, text="Default Output Format:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    def_output_format_var = StringVar(settings_window)
    def_output_format_var.set(format_var.get())
    def_output_format_dropdown = OptionMenu(settings_frame, def_output_format_var, "ICO", "PNG", "JPG", "BMP", "TIFF", "GIF")
    def_output_format_dropdown.grid(row=4, column=1, pady=5)

    def save_def_output_format():
        format_var.set(def_output_format_var.get())
        set_setting('Settings', 'default_format', def_output_format_var.get())

    Label(settings_frame, text="Default Size Options (comma separated):").grid(row=5, column=0, sticky="e", padx=5, pady=5)
    def_size_entry = Entry(settings_frame, width=50)
    def_size_entry.grid(row=5, column=1, pady=5)
    def_size_entry.insert(0, "16,32,64")

    def save_def_size():
        sizes = [int(s) for s in def_size_entry.get().split(",") if s.isdigit()]
        if sizes:
            global size_var
            size_var = IntVar(value=sizes[0])
            for widget in size_button_frame.winfo_children():
                widget.destroy()
            for size in sizes:
                Radiobutton(size_button_frame, text=f"{size}x{size}", variable=size_var, value=size).pack(side="left", padx=10)
            set_setting('Settings', 'default_size', sizes[0])

    def_aspect_ratio_var = IntVar(value=maintain_aspect_ratio_var.get())
    def_aspect_ratio_check = Checkbutton(settings_frame, text="Maintain aspect ratio by default", variable=def_aspect_ratio_var)
    def_aspect_ratio_check.grid(row=6, column=0, columnspan=2, pady=5)

    def save_def_aspect_ratio():
        maintain_aspect_ratio_var.set(def_aspect_ratio_var.get())
        set_setting('Settings', 'maintain_aspect_ratio', def_aspect_ratio_var.get())

    def save_all_settings():
        save_def_save_dir()
        save_def_load_dir()
        save_rec_files_limit()
        save_def_output_format()
        save_def_size()
        save_def_aspect_ratio()
        messagebox.showinfo("Settings", "Settings saved successfully!")
        settings_window.destroy()

    Button(settings_frame, text="Save and Close", command=save_all_settings).grid(row=7, column=0, columnspan=2, pady=10)

def show_help():
    help_window = Toplevel(root)
    help_window.title("Help")
    help_window.geometry("600x230")

    Label(help_window, text="Help", font=("Arial", 14)).pack(pady=10)
    help_text = Text(help_window, wrap="word", height=150, width=100)
    help_text.pack(pady=10)
    help_text.insert("1.0", "Instructions:\n\n1. Load an image using 'Load Image' or drag and drop an image.\n"
                            "2. Select a size or enter custom dimensions.\n"
                            "3. Choose an output format.\n"
                            "4. Click 'Resize and Save' or 'Batch Resize and Save' for multiple images.\n"
                            "5. Use 'Open Folder' to view saved images.\n"
                            "6. Set the save directory using 'Settings' in the menu.\n"
                            "7. Recent files are displayed below and can be cleared with 'Clear'.")
    help_text.config(state="disabled")

# Initialize Tkinter window with TkinterDnD
root = TkinterDnD.Tk()
root.title("Image Resizer")
root.geometry("660x840")

# Menu bar
menu_bar = Menu(root)
root.config(menu=menu_bar)

# Adding Settings menu
settings_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Settings", command=show_settings)

# Adding Help menu
help_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Help", command=show_help)

# Title label
title_label = Label(root, text="Image Resizer", font=("Arial", 16, "bold"), fg="blue")
title_label.grid(row=0, column=0, columnspan=3, pady=10)

# Image preview frame
image_frame = Frame(root, width=300, height=300, bg="grey")
image_frame.grid(row=1, column=0, rowspan=4, padx=10, pady=10)
image_frame.grid_propagate(False)

# Image label for displaying the image
image_label = Label(image_frame)
image_label.pack(expand=True)

# Load default image on startup
load_default_image()

# Load image button
load_button = Button(root, text="Load Image", command=load_image)
load_button.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

# Drag and drop functionality
def on_drop(event):
    file_path = event.data
    file_path = file_path.replace('{', '').replace('}', '')  # Clean up path
    load_image(file_path)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

# Select size label
select_size_label = Label(root, text="Select Size:")
select_size_label.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# Radio button variables and labels
size_var = IntVar(value=0)

size_button_frame = Frame(root)
size_button_frame.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

size_label1 = Radiobutton(size_button_frame, text="16x16", variable=size_var, value=16)
size_label1.pack(side="left", padx=10)

size_label2 = Radiobutton(size_button_frame, text="32x32", variable=size_var, value=32)
size_label2.pack(side="left", padx=10)

size_label3 = Radiobutton(size_button_frame, text="64x64", variable=size_var, value=64)
size_label3.pack(side="left", padx=10)

# Aspect ratio maintenance checkbox
maintain_aspect_ratio_var = IntVar(value=0)
maintain_aspect_ratio_checkbox = Checkbutton(root, text="Maintain aspect ratio", variable=maintain_aspect_ratio_var)
maintain_aspect_ratio_checkbox.grid(row=4, column=1, columnspan=2, pady=5, sticky="w")

# Custom size entries
custom_size_frame = Frame(root)
custom_size_frame.grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

custom_size_label = Label(custom_size_frame, text="Custom Size:")
custom_size_label.pack(side="left", padx=10)

custom_width_var = StringVar()
custom_width_entry = Entry(custom_size_frame, textvariable=custom_width_var, width=5)
custom_width_entry.pack(side="left", padx=5)
custom_width_entry.bind("<KeyRelease>", validate_custom_size)

x_label = Label(custom_size_frame, text="x")
x_label.pack(side="left", padx=5)

custom_height_var = StringVar()
custom_height_entry = Entry(custom_size_frame, textvariable=custom_height_var, width=5)
custom_height_entry.pack(side="left", padx=5)
custom_height_entry.bind("<KeyRelease>", validate_custom_size)

# Clear button
clear_button = Button(custom_size_frame, text="Clear", command=clear_custom_size)
clear_button.pack(side="left", padx=10)

# Output format label and dropdown
format_label = Label(root, text="Select Output Format:")
format_label.grid(row=6, column=0, padx=10, pady=10, sticky="w")

format_var = StringVar(root)
format_var.set("ICO")

format_dropdown = OptionMenu(root, format_var, "ICO", "PNG", "JPG", "BMP", "TIFF", "GIF")
format_dropdown.grid(row=6, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

# Resize and save button
save_button = Button(root, text="Resize and Save", command=resize_and_save)
save_button.grid(row=7, column=0, columnspan=1, pady=10, sticky="ew")

# Resize and save batch button
batch_button = Button(root, text="Batch Resize and Save", command=resize_and_save_batch)
batch_button.grid(row=7, column=1, columnspan=2, pady=10, sticky="ew")

# Saved file path
saved_filepath = StringVar()
saved_filepath_label = Label(root, textvariable=saved_filepath)
saved_filepath_label.grid(row=8, column=0, columnspan=3, padx=10, pady=5)

# Open folder button
open_folder_button = Button(root, text="Open Folder", command=open_folder, state="disabled")
open_folder_button.grid(row=9, column=0, columnspan=1, pady=5, sticky="ew")

# Frame for displaying last saved files
last_files_frame = Frame(root)
last_files_frame.grid(row=10, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

# Scrollable text widget to display last saved files
scrollbar = Scrollbar(last_files_frame)
scrollbar.pack(side="right", fill="y")

last_files_text = Text(last_files_frame, height=10, width=60, state="disabled", yscrollcommand=scrollbar.set)
last_files_text.pack(side="left", fill="both", expand=True)

scrollbar.config(command=last_files_text.yview)

# Clear button
clear_files_button = Button(last_files_frame, text="Clear Recent Files", command=clear_last_files)
clear_files_button.pack(side="right", padx=10)

# Progress bar for batch processing
progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress.grid(row=11, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

# Save directory label
save_directory_label = Label(root, text="Save Directory: Not Selected", fg="green")
save_directory_label.grid(row=12, column=0, columnspan=3, padx=10, pady=5)
# Initialize the save directory variable
save_directory = get_setting('Settings', 'last_save_directory', script_directory)
if save_directory:
    save_directory_label.config(text=f"Save Directory: {save_directory}")

# Load initial settings
load_initial_settings()

# Keep the window running
root.mainloop()
