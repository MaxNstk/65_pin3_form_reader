import datetime
from operator import itemgetter
import cv2
import numpy as np


import time
from pdf2image import convert_from_path
import cv2
import numpy as np

"""  IMAGE CONVERTER - PDF TO JPG"""

generation_date_str = time.strftime('%Y%m%d-%H%M%S')

img_path = f"resultados_jpg/{generation_date_str}.jpg"

images = convert_from_path('modelos_pdf/epcar_4_background_markers.pdf', poppler_path=r'poppler-23.08.0/Library/bin')
for i in range(len(images)):
    # Save pages as images in the pdf
    images[i].save(img_path, 'JPEG')


"""  MARKER INTERPRETER """

result_path = f"saidas_opencv/{generation_date_str}.png"
marker_path = 'markers/target_72px_background.png'

# read image

img = cv2.imread(img_path)
# read template
tmplt = cv2.imread(marker_path)
hh, ww, cc = tmplt.shape

# set arguments
match_thresh = 0.95              # stopping threshold for match value
num_matches = 10                  # stopping threshold for number of matches
match_radius = max(hh,ww)//4      # approx radius of match peaks

# get correlation surface from template matching
corrimg = cv2.matchTemplate(img,tmplt,cv2.TM_SQDIFF_NORMED)
hc, wc = corrimg.shape

# get locations of all peaks higher than match_thresh for up to num_matches
imgcopy = img.copy()
corrcopy = corrimg.copy()

matches = []
for i in range(1, num_matches):
    # get max value and location of max
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(corrcopy)
    x1 = max_loc[0]
    y1 = max_loc[1]
    x2 = x1 + ww
    y2 = y1 + hh
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
    
cv2.imwrite(f'cropped_results/result_img_{generation_date_str}.png', cropped_image)

# save results
# power of 4 exaggeration of correlation image to emphasize peaks
cv2.imwrite('prova_da_epcar_corr.png', (255*cv2.pow(corrimg,4)).clip(0,255).astype(np.uint8))
cv2.imwrite('prova_da_epcar_star_corr_masked.png', (255*cv2.pow(corrcopy,4)).clip(0,255).astype(np.uint8))
cv2.imwrite('prova_da_epcar_star_multi_match.png', imgcopy)

