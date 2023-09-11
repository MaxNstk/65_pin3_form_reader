import cv2
import numpy as np 
import time

from marker import Marker
from markers_list import MarkerList


class ImageHandler:

    base_image_path:str
    template_path:str = 'markers/target_72px_background.png'

    base_image: np.ndarray = None
    template: np.ndarray = None

    template_height: np.ndarray = None
    template_width: np.ndarray = None

    match_thresh = 0.95              
    markers_amount = 4 

    markers:MarkerList

    def __init__(self, base_image_path,template_path='markers/target_72px_background.png') -> None:
        self.base_image_path = base_image_path
        self.template_path = template_path
        self.set_images_info()

    def set_images_info(self):
        self.base_image = cv2.imread(self.base_image_path)
        self.template = cv2.imread(self.template_path)
        self.template_height, self.template_width, _ = self.template.shape
        self.match_radius = max(self.template_height,self.template_width)//4

    def cropp_image(self):

        generation_date_str = time.strftime('%Y%m%d-%H%M%S')

        # get correlation surface from template matching
        correlation_img = cv2.matchTemplate(self.base_image,self.template,cv2.TM_SQDIFF_NORMED)

        # get locations of all peaks higher than match_thresh for up to num_matches
        img_copy = self.base_image.copy()
        corrcopy = correlation_img.copy()

        self.markers = MarkerList()
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
            
        cv2.imwrite(f'results/cropped_results/result_img_{generation_date_str}.png', cropped_image)

        # power of 4 exaggeration of correlation image to emphasize peaks
        # cv2.imwrite(f'results/correlated_images/corr_{generation_date_str}.png', (255*cv2.pow(corrimg,4)).clip(0,255).astype(np.uint8))
        # cv2.imwrite(f'results/correlated_images/corr_masked_{generation_date_str}.png', (255*cv2.pow(corrcopy,4)).clip(0,255).astype(np.uint8))
        # cv2.imwrite(f'results/correlated_images/original_img_{generation_date_str}.png', imgcopy)
