import cv2
import numpy as np

from itp_forms.core.marker import Marker



class MarkerList:

    markers:list

    marker_a: Marker # esquerda acima
    marker_b: Marker # direita acima
    marker_c: Marker # esquerda baixo
    marker_d: Marker # direita baixo

    template:np.ndarray 

    def __init__(self, template) -> None:
        self.template = template
        self.markers = []

    def set_markers(self):
        sorted_y_markers = sorted(self.markers, key=lambda marker: marker.y_center)
        self.marker_a, self.marker_b = sorted(sorted_y_markers[:2], key=lambda marker: marker.x_center)
        self.marker_c, self.marker_d = sorted(sorted_y_markers[2:], key=lambda marker: marker.x_center)

    # todo fazer 4 atributos um para cada marker
    def add(self, marker:Marker):
        self.markers.append(marker)
        if self.length() == 4:
            self.set_markers()
    
    def length(self): 
        return len(self.markers)

    def connect_markers(self, img):
        cv2.line(img, self.marker_a.get_center_coordinates(), self.marker_b.get_center_coordinates(), (0, 255, 255), 2)
        cv2.line(img, self.marker_a.get_center_coordinates(), self.marker_c.get_center_coordinates(), (0, 255, 255), 2)
        cv2.line(img, self.marker_b.get_center_coordinates(), self.marker_d.get_center_coordinates(), (0, 255, 255), 2)
        cv2.line(img, self.marker_c.get_center_coordinates(), self.marker_d.get_center_coordinates(), (0, 255, 255), 2)

    def draw_rectangle_around_markers(self, img, color=(0,0,255)):
        for marker in self.markers:
            marker.highlight(img, color)
    
    def cropp_around(self, img):
        return img[self.marker_a.y_center:self.marker_c.y_center,self.marker_a.x_center:self.marker_b.x_center]
    
    def get_vertical_orientation(self):
        pass