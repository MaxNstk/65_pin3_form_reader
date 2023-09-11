
from operator import itemgetter
import cv2
import numpy as np 
import time

class ImageHandler:

    base_image_path = None
    template_path = 'markers/target_72px_background.png'
    base_img:np.array
    template:np.array
    template_height:int
    template_width:int

    match_thresh = 0.95              # stopping threshold for match value
    num_matches = 4                  # stopping threshold for number of matches


    def __init__(self, base_image_path,template_path='markers/target_72px_background.png') -> None:
        self.base_image_path = base_image_path
        self.template_path = template_path
        self.set_images_info()
    

    def set_images_info(self):
        self.base_img = cv2.imread(self.base_image_path)
        self.template = cv2.imread(self.template_path)
        self.template_height, self.template_width, _ = self.template.shape
        self.match_radius = max(self.template_height,self.template_width)//4 # approx radius of match peaks
    
    # get locations of all peaks higher than match_thresh for up to num_matches
    def get_matches(self,base_img, correlated_img):
        matches = []
        for i in range(0, self.num_matches):
            # get max value and location of max
            _, max_val, _, max_loc = cv2.minMaxLoc(correlated_img)
            x1 = max_loc[0]
            y1 = max_loc[1]
            x2 = x1 + self.template_width
            y2 = y1 + self.template_height
            
            if max_val > self.match_thresh:
                center_X = int((x1 + x2)/2)
                center_y = int((y1 + y2)/2)
                matches.append([center_X, center_y])
                print("match number:", i, "match value:", max_val, "match x,y:", str(center_X), print(center_y))
                # draw draw blue bounding box to define match location
                cv2.rectangle(base_img, (x1,y1), (x2,y2), (0,0,255), 2)
                # draw black filled circle over copy of correlation_surface_img 
                cv2.circle(correlated_img, (x1,y1), self.match_radius, 0, -1)
                i = i + 1
            else:
                break

        if len(matches) != self.num_matches:
            raise Exception(f"Número de marcadores detectados difere de 4: {len(matches)} encontrados") 
        self.matches = matches
    
    def _cropp_image(self,img):
        return img[self.sorted_y_matches[0][1]:self.sorted_y_matches[3][1],self.sorted_x_matches[0][0]:self.sorted_x_matches[3][0]]

    def sort_matches(self):
        self.sorted_x_matches = (sorted(self.matches, key=itemgetter(0)))
        self.sorted_y_matches = (sorted(self.matches, key=itemgetter(1)))

    def draw_line_connection_matches(self, img):
        # Sort the matched points by x-coordinate
        
        for i in range(0,len(self.sorted_x_matches) - 1, 2):
            x1, y1 = self.sorted_x_matches[i]
            x2, y2 = self.sorted_x_matches[i + 1]
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 255), 2)
        
        for i in range(0,len(self.sorted_y_matches) - 1, 2):
            x1, y1 = self.sorted_y_matches[i]
            x2, y2 = self.sorted_y_matches[i + 1]
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 255), 2)

    def cropp_image(self):

        generation_date_str = time.strftime('%Y%m%d-%H%M%S')
        imgcopy = self.base_img.copy()

        # get correlation surface from template matching
        correlation_surface_img = cv2.matchTemplate(self.base_img,self.template,cv2.TM_SQDIFF_NORMED)
        corrcopy = correlation_surface_img.copy()
        
        self.get_matches(imgcopy,corrcopy)      
        self.sort_matches()
        self.draw_line_connection_matches(imgcopy)
        cropped_image = self._cropp_image(imgcopy)

        cv2.imwrite(f'results/cropped_results/result_img_{generation_date_str}.png', cropped_image)
        # power of 4 exaggeration of correlation image to emphasize peaks
        cv2.imwrite(f'results/other_images/corr_{generation_date_str}.png', (255*cv2.pow(correlation_surface_img,4)).clip(0,255).astype(np.uint8))
        cv2.imwrite(f'results/other_images/corr_masked_{generation_date_str}.png', (255*cv2.pow(corrcopy,4)).clip(0,255).astype(np.uint8))
        cv2.imwrite(f'results/other_images/original_img_{generation_date_str}.png', imgcopy)


