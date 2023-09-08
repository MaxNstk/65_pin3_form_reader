import pdfplumber
import openpyxl

# import module
from pdf2image import convert_from_path


images = convert_from_path('modelos_pdf/modelo_branco_com_marcadores.pdf', poppler_path=r'C:/UDESC/pin3/65_pin3_form_reader/poppler-23.08.0/Library/bin')
for i in range(len(images)):
	# Save pages as images in the pdf
	images[i].save('modelos_jpeg/teste.jpg', 'JPEG')

import cv2
import numpy as np

image_path = "modelos_jpeg/teste.jpg"
image = cv2.imread(image_path)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

edges = cv2.Canny(gray, threshold1=30, threshold2=100)

contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

min_area = 1000  # You can adjust this threshold based on your needs

for contour in contours:
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
    
    if len(approx) == 4 and cv2.contourArea(contour) > min_area:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

cv2.imshow("Black Squares Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
