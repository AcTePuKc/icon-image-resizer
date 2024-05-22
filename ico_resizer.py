from PIL import Image, ImageTk
from tkinter import filedialog, Tk, Label, Button, messagebox, IntVar, Radiobutton, Frame, TclError, StringVar, OptionMenu
import os  # Import os for file path manipulation
import subprocess  # For opening the file explorer

def load_image():
    global image_path, image, photo_image
    image_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("All Images", "*.jpg;*.png;*.ico"), ("JPEG Images", "*.jpg"), ("PNG Images", "*.png"), ("ICO Files", "*.ico")]
    )

    if image_path:
        try:
            image = Image.open(image_path)
            display_image()
        except (IOError, OSError) as e:
            messagebox.showerror("Error", f"Error loading image: {str(e)}")

def display_image():
    """Displays the loaded image in the window."""
    global image_label, photo_image
    try:
        # Resize the image to fit the preview window (300x300 px), maintaining the aspect ratio
        image.thumbnail((300, 300))
        photo_image = ImageTk.PhotoImage(image)
        image_label.config(image=photo_image)
        image_label.image = photo_image  # Prevent garbage collection
    except (AttributeError, TclError):
        # Handle potential errors when displaying non-image formats
        pass

def load_default_image():
    global image, photo_image
    image = Image.new("RGB", (300, 300), color="grey")  # Create a default grey image
    photo_image = ImageTk.PhotoImage(image)
    image_label.config(image=photo_image)
    image_label.image = photo_image

def resize_and_save():
    if not hasattr(image, "resize"):
        messagebox.showerror("Error", "No image loaded to resize.")
        return

    selected_size = size_var.get()
    if selected_size == 0:
        messagebox.showerror("Error", "Please select a size to resize.")
        return

    output_format = format_var.get()
    if output_format not in ["ICO", "PNG", "JPG"]:
        messagebox.showerror("Error", "Please select a valid output format.")
        return

    try:
        resized_image = image.resize((selected_size, selected_size), Image.LANCZOS)
        filename, ext = os.path.splitext(image_path)
        new_ext = '.' + output_format.lower()
        new_filepath = f"{filename}_{selected_size}x{selected_size}{new_ext}"
        resized_image.save(new_filepath, format=output_format)
        print(f"Image resized and saved to: {new_filepath}")
        open_folder_button.config(state="normal")  # Enable the open folder button
        saved_filepath.set(new_filepath)  # Update the saved file path
    except Exception as e:
        messagebox.showerror("Error", f"Failed to resize and save image: {str(e)}")

def open_folder():
    filepath = saved_filepath.get()
    if not filepath:
        messagebox.showinfo("Info", "No file saved yet.")
        return

    folder_path = os.path.dirname(filepath)
    try:
        if os.name == 'nt':  # Windows
            os.startfile(folder_path)
        elif os.name == 'posix':  # macOS, Linux
            subprocess.Popen(['open', folder_path])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open folder: {str(e)}")

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        self.tooltip = Label(self.widget, text=self.text, background="yellow", relief="solid", borderwidth=1)
        self.tooltip.place(x=event.x, y=event.y)

    def hide_tooltip(self, event):
        self.tooltip.destroy()

# Initialize Tkinter window
root = Tk()
root.title("Image Resizer")

# Title label
title_label = Label(root, text="Image Resizer", font=("Arial", 16, "bold"), fg="blue")
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# Image preview frame
image_frame = Frame(root, width=300, height=300, bg="grey")
image_frame.grid(row=1, column=0, rowspan=3, padx=10, pady=10)
image_frame.grid_propagate(False)  # Prevent the frame from resizing

# Image label for displaying the image
image_label = Label(image_frame)
image_label.pack(expand=True)

# Load default image on startup
load_default_image()

# Load image button
load_button = Button(root, text="Load Image", command=load_image)
load_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
load_button_tooltip = ToolTip(load_button, "Click to load an image")

# Select size label
select_size_label = Label(root, text="Select Size:")
select_size_label.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# Radio button variables and labels
size_var = IntVar(value=0)

size_button_frame = Frame(root)
size_button_frame.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

size_label1 = Radiobutton(size_button_frame, text="16x16", variable=size_var, value=16)
size_label1.pack(side="left", padx=10)

size_label2 = Radiobutton(size_button_frame, text="32x32", variable=size_var, value=32)
size_label2.pack(side="left", padx=10)

size_label3 = Radiobutton(size_button_frame, text="64x64", variable=size_var, value=64)
size_label3.pack(side="left", padx=10)

# Output format label and dropdown
format_label = Label(root, text="Select Output Format:")
format_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

format_var = StringVar(root)
format_var.set("ICO")  # Default value

format_dropdown = OptionMenu(root, format_var, "ICO", "PNG", "JPG")
format_dropdown.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

# Resize and save button
save_button = Button(root, text="Resize and Save", command=resize_and_save)
save_button.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

# Saved file path
saved_filepath = StringVar()
saved_filepath_label = Label(root, textvariable=saved_filepath)
saved_filepath_label.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

# Open folder button
open_folder_button = Button(root, text="Open Folder", command=open_folder, state="disabled")
open_folder_button.grid(row=7, column=0, columnspan=2, pady=5, sticky="ew")

# Keep the window running
root.mainloop()
