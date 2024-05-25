
import cv2
import numpy as np


class Marker:

    """ Represente um marcador presente na imagem """

    x_center: int
    y_center: int

    template_size: int

    def __init__(self,x_center,y_center: int, template_size) -> None:
        self.x_center = int(x_center)
        self.y_center = int(y_center)
        self.template_size = int(template_size)
    
    def highlight(self,img, color=(0,0,255)):
        """ desenha um retangulo ao redor de mim mesmo """
        cv2.rectangle(img, (int(self.x_center/self.template_size),int(self.y_center/self.template_size)),
                       (int(self.x_center/self.template_size),int(self.y_center/self.template_size)), color, 2)
    
    def get_center_coordinates(self):
        """ retorna as coordenadas centrais """
        return self.x_center, self.y_center
    