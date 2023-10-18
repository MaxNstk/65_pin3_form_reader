import asyncio
import os
from time import sleep
import time
import cv2
import numpy as np
from itp_forms.core.marker import Marker

from itp_forms.core.markers_list import MarkerList

class ImageHandler:

    base_image: np.ndarray
    template: np.ndarray

    match_thresh = 0.95
    markers_amount = 4

    markers:MarkerList

    cropped_image: np.ndarray = None

    x_axis_distortion_px: int = 0
    y_axis_distortion_px: int = 0

    key_mapping = {
            'enter': 13,
            'esc': 27,
            # Add more key mappings as needed
        }

    def __init__(self, base_image_path=None, cropped_image_path=None ,template_path=os.path.join('utils','markers','target_72px_background.png')) -> None:
        if cropped_image_path:
            self.cropped_image = cv2.imread(cropped_image_path)
        if base_image_path:
            self.base_image = cv2.imread(base_image_path)
            self.template = cv2.imread(template_path)
            self.set_images_info()

    def set_images_info(self):        
        template_height, template_width, _ = self.template.shape
        self.match_radius = max(template_height, template_width)//4
        self.set_markers()

        self.x_axis_cropped_area_size = self.markers.marker_a.x_center - self.markers.marker_b.x_center
        self.y_axis_cropped_area_size = self.markers.marker_a.y_center - self.markers.marker_c.y_center

        self.x_axis_distortion_px = self.markers.marker_a.x_center - self.markers.marker_c.x_center
        self.y_axis_distortion_px = self.markers.marker_a.y_center - self.markers.marker_b.y_center

    def get_correct_positions(self, x,y):
        correct_x = x + ((1-((self.y_axis_cropped_area_size - y) / self.y_axis_cropped_area_size)) * self.x_axis_distortion_px)
        correct_y = y + ((1-((self.x_axis_cropped_area_size - x) / self.x_axis_cropped_area_size)) * self.y_axis_distortion_px)
        return correct_x, correct_y
    
    def set_markers(self):
        # get correlation surface from template matching
        correlation_img = cv2.matchTemplate(self.base_image,self.template,cv2.TM_SQDIFF_NORMED)

        # get locations of all peaks higher than match_thresh for up to num_matches
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

    def cropp_image(self):
        if not self.cropped_image:
            self.set_markers()

        img_copy = self.base_image.copy()
        self.markers.draw_rectangle_around_markers(img_copy)
        self.markers.connect_markers(img_copy)
        self.cropped_image = self.markers.cropp_around(img_copy)

        return self.cropped_image
    

    def configure_initial_positions(self,path=None):
        image = self.cropped_image
        if path:
            image = cv2.imread(path)
        cv2.imshow('Selecionar célular inicial', image)

        start_x, start_y, end_x, end_y = -1, -1, -1, -1

        drawing = False

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
                # if path:
                #     cv2.imwrite(path, image)
                break

            # Check for Esc key
            elif key == self.key_mapping['esc']:
                break
            
        cv2.destroyAllWindows()  # Close the OpenCV window
        x1, x2 = (start_x, end_x) if start_x < end_x else (end_x, start_x)
        y1, y2 = (start_y, end_y) if start_y < end_y else (end_y, start_y)
        return x1, y1, x2, y2

    def save_cropped_image(self, path):
        cv2.imwrite(path, self.cropped_image)
    
    def read_answers(answers_path: str):
        return
    
    def rotate_image(self):

        # Define the two points in pixel coordinates
        point1 = self.markers.marker_a.get_center_coordinates()
        point2 = self.markers.marker_c.get_center_coordinates()

        # Calculate the angle of rotation to align the points in the y-axis
        dy = point2[1] - point1[1]
        angle = np.arctan2(dy, abs(point2[0] - point1[0]))  # Calculate the angle in radians

        # Get the image center point (assumes it's the center)
        image_center = tuple(np.array(self.cropped_image.shape[1::-1]) / 2)

        # Create a rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(image_center, np.degrees(angle), scale=1)

        # Apply the rotation to the image
        rotated_image = cv2.warpAffine(self.cropped_image, rotation_matrix, self.cropped_image.shape[1::-1], flags=cv2.INTER_LINEAR)

        # Display or save the rotated image
        # cv2.imwrite(f"media/teste/{time.strftime('%Y%m%d-%H%M%S')}.jpg",rotated_image)
        # cv2.imshow('Rotated Image', rotated_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # If you want to save the rotated image
        # cv2.imwrite('rotated_image.jpg', rotated_image)