import asyncio
import cv2
import numpy as np 

from marker import Marker
from markers_list import MarkerList


class ImageHandler:

    base_image: np.ndarray
    template: np.ndarray

    match_thresh = 0.95
    markers_amount = 4

    markers:MarkerList

    cropped_image: np.ndarray

    key_mapping = {
            'enter': 13,
            'esc': 27,
            # Add more key mappings as needed
        }

    def __init__(self, base_image_path,template_path='static/markers/target_72px_background.png') -> None:
        self.base_image = cv2.imread(base_image_path)
        self.template = cv2.imread(template_path)
        self.set_images_info()

    def set_images_info(self):        
        template_height, template_width, _ = self.template.shape
        self.match_radius = max(template_height, template_width)//4

    def cropp_image(self,):

        # get correlation surface from template matching
        correlation_img = cv2.matchTemplate(self.base_image,self.template,cv2.TM_SQDIFF_NORMED)

        # get locations of all peaks higher than match_thresh for up to num_matches
        img_copy = self.base_image.copy()
        corrcopy = correlation_img.copy()

        self.markers = MarkerList(self.template)
        for i in range(0, self.markers_amount):      
            # get max value and location of max
            _, max_val, _, max_loc = cv2.minMaxLoc(corrcopy)

            if max_val > self.match_thresh:
                marker = Marker(max_loc[0],max_loc[1], self.template)
                self.markers.add(marker)  
                cv2.circle(corrcopy, (marker.x1,marker.y1), self.match_radius, 0, -1)
                i = i + 1               
            else:
                break

        if self.markers.length() != 4:
            raise Exception(f"Número de marcadores detectados difere de 4: {self.markers.length()} encontrados")

        self.markers.draw_rectangle_around_markers(img_copy)
        self.markers.connect_markers(img_copy)
        self.cropped_image = self.markers.cropp_around(img_copy)

        return self.cropped_image
    

    async def configure_initial_positions(self,path=None):
        image = self.cropped_image
        if path:
            image = cv2.imread(path)
        cv2.imshow('Selecionar célular inicial', image)

        # Initialize variables to store the starting and ending coordinates
        start_x, start_y, end_x, end_y = -1, -1, -1, -1

        drawing = False
        # Function to handle mouse events

        def select_shape(event, x, y, flags, param):
            nonlocal start_x, start_y, end_x, end_y, drawing

            if event == cv2.EVENT_LBUTTONDOWN:
                start_x, start_y = x, y
                end_x, end_y = x, y
                drawing = True

            elif event == cv2.EVENT_LBUTTONUP:
                end_x, end_y = x, y
                drawing = False

            elif event == cv2.EVENT_MOUSEMOVE and start_x != -1 and drawing:
                end_x, end_y = x, y


        cv2.setMouseCallback('Selecionar célular inicial', select_shape)

        while True:
            clone = image.copy()

            if start_x != -1:
                cv2.rectangle(clone, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

            cv2.imshow('Selecionar célular inicial', clone)
            key = cv2.waitKey(1) & 0xFF

            # Check for Enter key
            if key == self.key_mapping['enter']:
                cv2.rectangle(image, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
                if path:
                    cv2.imwrite(path, image)
                break

            # Check for Esc key
            elif key == self.key_mapping['esc']:
                break
            
            await asyncio.sleep(0.1)  # Sleep briefly to avoid high CPU usage


        # Extract the selected ROI from the original image
        
        # return start_x, start_y, end_x, end_y

    def save_cropped_image(self, path):
        cv2.imwrite(path, self.cropped_image)