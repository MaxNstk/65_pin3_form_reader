

from operator import itemgetter
import cv2
from marker import Marker


class MarkerList:

    markers:list = []
    sorted_x_markers:list
    sorted_y_markers:list

    def add(self, marker:Marker):
        self.markers.append(marker)
    
    def length(self):
        return len(self.markers)

    def sort_sides(self):
        self.sorted_x_markers = sorted(self.markers, key=lambda marker: marker.x_center)
        self.sorted_y_markers = sorted(self.markers, key=lambda marker: marker.y_center)

    def connect_markers(self, img):
        self.sort_sides()

        # Sort the matched points by x-coordinate
        for i in range(0,len(self.sorted_x_markers) - 1, 2):
            x1, y1 = self.sorted_x_markers[i].get_center_coordinates()
            x2, y2 = self.sorted_x_markers[i + 1].get_center_coordinates()
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 255), 2)

        for i in range(0,len(self.sorted_y_markers) - 1, 2):
            x1, y1 = self.sorted_y_markers[i].get_center_coordinates()
            x2, y2 = self.sorted_y_markers[i + 1].get_center_coordinates()
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 255), 2)
    
    def draw_rectangle_around_markers(self, img, color=(0,0,255)):
        for marker in self.markers:
            marker.highlight(img, color)
    
    def cropp_around(self, img):
        self.sort_sides()
        # return img[self.sorted_y_matches[0][1]:self.sorted_y_matches[3][1],self.sorted_x_matches[0][0]:self.sorted_x_matches[3][0]]
        return img[self.sorted_y_markers[0].y_center:self.sorted_y_markers[3].y_center,self.sorted_x_markers[0].x_center:self.sorted_x_markers[3].x_center]