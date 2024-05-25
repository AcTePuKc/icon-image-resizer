# Image Resizer App
Icon and Image Resizer

This is a simple Icon and Image Resizing application built using Python and Tkinter. It allows users to load an image, resize it to different sizes, and save it in various formats.

## Features

- Load an image (supports JPEG, PNG, ICO, BMP, TIFF, and GIF formats).
- Resize the image to predefined sizes or custom dimensions.
- Maintain aspect ratio during resizing (optional).
- Select the output format (ICO, PNG, JPG, BMP, TIFF, or GIF) for the resized image.
- Batch resize multiple images at once.
- Drag & Drop function for a single file conversation.
- Save the resized image to the selected format.
- Open the folder containing the saved image.
- View and manage recent files list.
- Set default save and load directories through the settings menu.
- Clear recent files list.

## Known Issues

- The save directory might not update correctly during the session. To ensure the correct save directory is used, set the directory in the settings, then restart the application.
- PNG to JPG is not working
## Requirements

- Python 3.x
- Pillow library (for image processing)
- Tkinter library (for GUI)
- tkinterdnd2 library (for drag-and-drop functionality)
- Subprocess library (for opening the file explorer)
- Collections library (for handling recent files)
- Logging library (for application logging)

## Usage

1. Clone the repository:

   ```
   git clone https://github.com/AcTePuKc/icon-image-resizer.git
   ```
2. Navigate to the project directory:

    ```
    cd icon-image-resizer
    ```
3. Install the required libraries:
    ```
    pip install -r requirements.txt
    ```
4. Run the application:
   ```
   python image_resizer.py
   ```
5. Load an image using the "Load Image" button or drag and drop an image into the application.
6. Select the image and click Open.
7. Select the desired size and output format.
8. Click on "Resize and Save" or "Batch Resize and Save" to save the resized image(s).
9. Click on "Open Folder" to locate the saved image.
10. Use the Settings menu to set default directories and other preferences.

## Screenshots
I might add some in the future, but probably NOT :)

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/AcTePuKc/icon-image-resizer/blob/main/LICENSE) file for details.

## Contributing
Feel free to submit issues, fork the repository and send pull requests!

---

If you have any other suggestions or changes, feel free to let me know!
