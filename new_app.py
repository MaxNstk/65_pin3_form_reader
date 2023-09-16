import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk

# Initialize variables
image = None
drawing = False
start_x, start_y, end_x, end_y = -1, -1, -1, -1
file_path = None

def open_image():
    global image, file_path
    file_path = filedialog.askopenfilename()
    if file_path:
        image = cv2.imread(file_path)
        display_image()

def display_image():
    global file_path, image
    if image is not None:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        photo = ImageTk.PhotoImage(image=image_pil)

        # Update the label with the new image
        label.config(image=photo)
        label.image = photo

def start_draw(event):
    global drawing, start_x, start_y
    drawing = True
    start_x, start_y = event.x, event.y

def end_draw(event):
    global drawing, end_x, end_y, image
    if drawing:
        end_x, end_y = event.x, event.y
        # Process the drawn shape (e.g., draw a rectangle)
        cv2.rectangle(image, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
        # cv2.imwrite(file_path, image)
        display_image()
        drawing = False

def update_image():
    # Continuously update the displayed image
    display_image()
    app.after(100, update_image)  # Adjust the delay as needed

app = tk.Tk()
app.title("OpenCV Real-Time Shape Selection")

# Create a label widget to display the OpenCV image
label = tk.Label(app)
label.pack()

# Create an "Open Image" button
open_button = tk.Button(app, text="Open Image", command=open_image)
open_button.pack()

# Bind mouse events for drawing
label.bind("<ButtonPress-1>", start_draw)
label.bind("<ButtonRelease-1>", end_draw)

# Start the image update loop
update_image()

app.mainloop()
