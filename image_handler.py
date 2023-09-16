import cv2
import numpy as np 
import time

from marker import Marker
from markers_list import MarkerList


class ImageHandler:

    base_image: 0
    template: 0

    match_thresh = 0.95
    markers_amount = 4

    markers:MarkerList

    def __init__(self, base_image_path,template_path='markers/target_72px_background.png') -> None:
        self.base_image = cv2.imread(base_image_path)
        self.template = cv2.imread(template_path)
        self.set_images_info()

    def set_images_info(self):        
        template_height, template_width, _ = self.template.shape
        self.match_radius = max(template_height, template_width)//4

    def cropp_image(self):

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
            raise Exception(f"Número de marcadores detectados difere de 4: {len(self.markers.length())} encontrados")

        self.markers.draw_rectangle_around_markers(img_copy)
        self.markers.connect_markers(img_copy)
        cropped_image = self.markers.cropp_around(img_copy)
            
        generation_date_str = time.strftime('%Y%m%d-%H%M%S')
        cv2.imwrite(f'results/cropped_results/result_img_{generation_date_str}.png', cropped_image)
          # power of 4 exaggeration of correlation image to emphasize peaks
          # cv2.imwrite(f'results/correlated_images/corr_{generation_date_str}.png', (255*cv2.pow(corrimg,4)).clip(0,255).astype(np.uint8))
          # cv2.imwrite(f'results/correlated_images/corr_masked_{generation_date_str}.png', (255*cv2.pow(corrcopy,4)).clip(0,255).astype(np.uint8))
          # cv2.imwrite(f'results/correlated_images/original_img_{generation_date_str}.png', imgcopy)
    

    def show_image(self, image_path):
        image = cv2.imread(image_path)

        # Create a copy of the image for drawing purposes
        display_image = image.copy()

        # Create variables to store the selection coordinates
        selection_start = None
        selection_end = None
        selecting = False

        # Define a callback function for mouse events
        def select_region(event, x, y, flags, param):
            global selecting, selection_start, selection_end

            if event == cv2.EVENT_LBUTTONDOWN:
                selecting = True
                selection_start = (x, y)

            elif event == cv2.EVENT_MOUSEMOVE:
                if selecting:
                    selection_end = (x, y)
                    display_image = image.copy()  # Refresh the display image
                    cv2.rectangle(display_image, selection_start, selection_end, (0, 255, 0), 2)
                    cv2.imshow('Image', display_image)

            elif event == cv2.EVENT_LBUTTONUP:
                selecting = False
                selection_end = (x, y)
                cv2.rectangle(display_image, selection_start, selection_end, (0, 255, 0), 2)
                cv2.imshow('Image', display_image)

            # Create a window and set the mouse callback function
            cv2.imshow('Image', display_image)
            cv2.setMouseCallback('Image', select_region)

            # Wait for a key press and close the window when done
            cv2.waitKey(0)
            cv2.destroyAllWindows()
