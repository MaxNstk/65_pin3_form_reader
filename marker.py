
import cv2
import numpy as np


class Marker:
    
    x1: int
    x2: int
    y1: int
    y2: int

    x_center: int
    y_center: int

    def __init__(self,x1,y1:int, template:np.ndarray) -> None:
        self.x1, self.y1 = x1, y1
        self.set_postitions(template)
    
    def set_postitions(self, template):
        template_height, template_width, _ = template.shape

        self.x2 = self.x1 + template_width
        self.y2 = self.y1 + template_height
        
        self.x_center = int((self.x1 + self.x2) / 2)
        self.y_center = int((self.y1 + self.y2) / 2)
    
    def highlight(self,img, color=(0,0,255)):
        cv2.rectangle(img, (self.x1,self.y1), (self.x2,self.y2), color, 2)
    
    def get_center_coordinates(self):
        return self.x_center, self.y_center
    
    # def draw_circle()