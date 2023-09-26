import time
import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk

from image_handler import ImageHandler
from pdf_converter import PDFConverter


class App:
    
    app: tk.Tk
    image_handler: ImageHandler

    def start(self):
        self.app = tk.Tk()
        self.app.title("OpenCV Image Drawing")

        open_button = tk.Button(self.app, text="Open Image", command=self.select_image)
        open_button.pack()
        # Create a label widget to display the OpenCV image
        self.label = tk.Label(self.app)
        self.label.pack()

        self.app.mainloop()


    def select_image(self):
        file_path = None
        while not file_path:
            file_path = filedialog.askopenfilename()
        image_path = f"results/image_results/{time.strftime('%Y%m%d-%H%M%S')}.png"
        PDFConverter.convert_to_jpg(pdf_path=file_path, result_path=image_path)
        self.image_handler = ImageHandler(image_path)
        self.image = self.image_handler.cropp_image()
        self.display_image()

        # cv2.imshow('Upload de imagem inicial', file_path)
    
    def display_image(self):
        if hasattr(self,'image'):
            image_rgb = cv2.cvtColor(self.image_handler.cropped_image, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_rgb)
            photo = ImageTk.PhotoImage(image=image_pil)

            # Update the label with the new image
            self.label.config(image=photo)
            self.label.image = photo

App().start()