
import cv2
import numpy as np


class Marker:

    template: np.ndarray

    x1: int
    x2: int
    y1: int
    y2: int
    template_height: int
    template_width: int
    x_center: int
    y_center: int

    def __init__(self,x1,y1:int, template:np.ndarray) -> None:
        self.x1, self.y1 = x1,y1
        self.template = template
        self.set_postitions()
    
    def set_postitions(self):
        self.template_height, self.template_width,_ = self.template.shape

        self.x2 = self.x1 + self.template_width
        self.y2 = self.y1 + self.template_height
        
        self.x_center = int((self.x1 + self.x2) / 2)
        self.y_center = int((self.y1 + self.y2) / 2)
    
    def highlight(self,img, color=(0,0,255)):
        cv2.rectangle(img, (self.x1,self.y1), (self.x2,self.y2), color, 2)
    
    def get_center_coordinates(self):
        return self.x_center, self.y_center
    
    # def draw_circle()