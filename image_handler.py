
from operator import itemgetter
import cv2
import numpy as np 
import time

class ImageHandler:

    base_image_path = None
    template_path = 'markers/target_72px_background.png'

    def __init__(self, base_image_path,template_path='markers/target_72px_background.png') -> None:
        self.base_image_path = base_image_path
        self.template_path = template_path
    
        
    def cropp_image(self):

        generation_date_str = time.strftime('%Y%m%d-%H%M%S')

        # read image
        base_img = cv2.imread(self.base_image_path)
        # read template
        template = cv2.imread(self.template_path)
        template_height, template_width, template_c = template.shape

        # set arguments
        match_thresh = 0.95              # stopping threshold for match value
        num_matches = 4                  # stopping threshold for number of matches
        match_radius = max(template_height,template_width)//4      # approx radius of match peaks

        # get correlation surface from template matching
        corrimg = cv2.matchTemplate(base_img,template,cv2.TM_SQDIFF_NORMED)
        hc, wc = corrimg.shape

        # get locations of all peaks higher than match_thresh for up to num_matches
        imgcopy = base_img.copy()
        corrcopy = corrimg.copy()

        matches = []
        for i in range(0, num_matches):
            # get max value and location of max
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(corrcopy)
            x1 = max_loc[0]
            y1 = max_loc[1]
            x2 = x1 + template_width
            y2 = y1 + template_height
            loc = str(x1) + "," + str(y1)
            if max_val > match_thresh:
                matches.append([int((x1 + x2)/2), int((y1 + y2)/2)])
                print("match number:", i, "match value:", max_val, "match x,y:", loc)
                # draw draw blue bounding box to define match location
                cv2.rectangle(imgcopy, (x1,y1), (x2,y2), (0,0,255), 2)
                # draw black filled circle over copy of corrimg 
                cv2.circle(corrcopy, (x1,y1), match_radius, 0, -1)
                # faster alternate - insert black rectangle
                # corrcopy[y1:y2, x1:x2] = 0
                i = i + 1
            else:
                break

        if len(matches) != 4:
            raise Exception(f"Número de marcadores detectados difere de 4: {len(matches)} encontrados")

        # Sort the matched points by x-coordinate
        sorted_x_matches = (sorted(matches, key=itemgetter(0)))
        for i in range(0,len(sorted_x_matches) - 1, 2):
            x1, y1 = sorted_x_matches[i]
            x2, y2 = sorted_x_matches[i + 1]
            cv2.line(imgcopy, (x1, y1), (x2, y2), (0, 255, 255), 2)

        sorted_y_matches = (sorted(matches, key=itemgetter(1)))
        for i in range(0,len(sorted_y_matches) - 1, 2):
            x1, y1 = sorted_y_matches[i]
            x2, y2 = sorted_y_matches[i + 1]
            cv2.line(imgcopy, (x1, y1), (x2, y2), (0, 255, 255), 2)

        cropped_image = imgcopy.copy()[sorted_y_matches[0][1]:sorted_y_matches[3][1],sorted_x_matches[0][0]:sorted_x_matches[3][0]]
            
        cv2.imwrite(f'results/cropped_results/result_img_{generation_date_str}.png', cropped_image)

        # power of 4 exaggeration of correlation image to emphasize peaks
        cv2.imwrite(f'results/correlated_images/corr_{generation_date_str}.png', (255*cv2.pow(corrimg,4)).clip(0,255).astype(np.uint8))
        cv2.imwrite(f'results/correlated_images/corr_masked_{generation_date_str}.png', (255*cv2.pow(corrcopy,4)).clip(0,255).astype(np.uint8))
        cv2.imwrite(f'results/correlated_images/original_img_{generation_date_str}.png', imgcopy)


