import asyncio
import os
from time import sleep
import time
import cv2
import numpy as np
from itp_forms.core.marker import Marker

from itp_forms.core.markers_list import MarkerList

class ImageHandler:

    """ Classe utilitária responsável por manipular imagens
        identificando marcadores, cortando elas, capturando informações...
    """

    base_image: np.ndarray
    template: np.ndarray

    match_thresh = 0.95
    markers_amount = 4

    markers:MarkerList

    cropped_image: np.ndarray = None

    x_axis_distortion_px: int = 0
    y_axis_distortion_px: int = 0

    key_mapping = {
            'enter': 13,
            'esc': 27,
            # Add more key mappings as needed
        }

    def __init__(self, base_image_path=None, cropped_image_path=None ,template_path=os.path.join('utils','markers','target_72px_background.png')) -> None:
        if cropped_image_path:
            self.cropped_image = cv2.imread(cropped_image_path)
        if base_image_path:
            self.base_image = cv2.imread(base_image_path)
            self.template = cv2.imread(template_path)
            self.set_images_info()

    def set_images_info(self):   
        """ Seta informações necessárias para fazer operações com a imagem"""     
        template_height, template_width, _ = self.template.shape
        self.match_radius = max(template_height, template_width)//4
        self.set_markers()

        self.x_axis_cropped_area_size = self.markers.marker_a.x_center - self.markers.marker_b.x_center
        self.y_axis_cropped_area_size = self.markers.marker_a.y_center - self.markers.marker_c.y_center

        self.x_axis_distortion_px = self.markers.marker_a.x_center - self.markers.marker_c.x_center
        self.y_axis_distortion_px = self.markers.marker_a.y_center - self.markers.marker_b.y_center

    def get_correct_positions(self, x,y):
        """ esse método corrige uma possível inclinação da folha. Pega o valor da diferença entre os a coordenada dos dois marcadores,
            multiplica pela "parte" que esse x corresponde de toda inclinação (supoe-se que a diferença entre os marcadores seja 100%,
            a coordenada está em algum ponto no meio disso, fazemos uma regra de 3 para saber o quão inclinada esse ponto está em comparação com o todo)
            e soma-se essa correção ao valor original. Para funcionar, o base deve ter os marcadores corretamente alinhados
        """
        correct_x = x + ((1-((self.y_axis_cropped_area_size - y) / self.y_axis_cropped_area_size)) * self.x_axis_distortion_px)
        correct_y = y + ((1-((self.x_axis_cropped_area_size - x) / self.x_axis_cropped_area_size)) * self.y_axis_distortion_px)
        return correct_x, correct_y
    
    # def set_markers(self):
    """ função de detecção de marcadores antiga, que não funciona direito com certos modelos """
    #     """ Define os marcadores da imagem"""

    #     correlation_img = cv2.matchTemplate(self.base_image,self.template,cv2.TM_SQDIFF_NORMED)

    #     corrcopy = correlation_img.copy()

    #     self.markers = MarkerList(self.template)
    #     for i in range(0, self.markers_amount):      
    #         _, max_val, _, max_loc = cv2.minMaxLoc(corrcopy)

    #         if max_val > 0.95:
    #             marker = Marker(max_loc[0],max_loc[1], self.template)
    #             self.markers.add(marker)  

    #             cv2.circle(corrcopy, (marker.x1,marker.y1), self.match_radius, 0, -1)
    #             i = i + 1               
    #         else:
    #             break

    #     if self.markers.length() != 4:
    #         raise Exception(f"Número de marcadores detectados difere de 4: {self.markers.length()} encontrados")

    # Blob detector function with parameters

    def set_markers(self):

        # Parameters will need tweaking depending on the specific size and characteristics of the blobs

        # Set up the detector with default parameters.
        params = cv2.SimpleBlobDetector_Params()
        
        # Filter by Area.
        params.filterByArea = True
        params.minArea = 200 # Minimum area of the blobs
        params.maxArea = 3000 # Maximum area of the blobs
        
        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = 0.85 # Minimum circularity of the blobs
        params.maxCircularity = 1.0 # Maximum circularity of the blobs

        # Filter by Inertia (ratio of the minor axis to the major axis)
        params.filterByInertia = True
        params.minInertiaRatio = 0.9  # Circles will have a ratio near 1
        
        # Filter by Convexity (how much the shape fills its convex hull)
        params.filterByConvexity = True
        params.minConvexity = 0.85
        
        # Create a detector with the parameters
        detector = cv2.SimpleBlobDetector_create(params)
        
        # Detect blobs
        keypoints = detector.detect(self.base_image)
        
        # Draw detected blobs as red circles.
        # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of the blob
        im_with_keypoints = cv2.drawKeypoints(self.base_image, keypoints, np.array([]), (0, 0, 255),
                                            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
        self.markers = MarkerList(self.template)
        for keypoint in keypoints:
            marker = Marker(keypoint.pt[0],keypoint.pt[1], keypoint.size)
            self.markers.add(marker)

        # return im_with_keypoints, keypoints

        # Save the image with keypoints for review
        output_image_path = f"testes/{time.strftime('%Y%m%d-%H%M%S')}.jpeg"
        cv2.imwrite(output_image_path, im_with_keypoints)

    def cropp_image(self):
        """ corta a imagem através da localização dos marcadores"""
        if not self.cropped_image:
            self.set_markers()

        img_copy = self.base_image.copy()
        self.markers.draw_rectangle_around_markers(img_copy)
        self.markers.connect_markers(img_copy)
        self.cropped_image = self.markers.cropp_around(img_copy)

        return self.cropped_image
    

    def configure_initial_positions(self,path=None):
        """ configura as posições do agrupamento incial, responável por abrir a janela do openCV
            e gerenciar os cliques para desenhar o retangulo e capturar as cordenadas
        """
        image = self.cropped_image
        if path:
            image = cv2.imread(path)
        cv2.imshow('Defina a celula inicial', image)

        start_x, start_y, end_x, end_y = -1, -1, -1, -1

        drawing = False

        def select_shape(event, x, y, flags, param):
            """ define as posições conforme o clique do usuário"""
            nonlocal start_x, start_y, end_x, end_y, drawing

            if event == cv2.EVENT_LBUTTONDOWN:
                start_x, start_y = x, y
                end_x, end_y = x, y
                drawing = True

            elif event == cv2.EVENT_LBUTTONUP:
                end_x, end_y = x, y
                drawing = False

            elif event == cv2.EVENT_MOUSEMOVE and start_x != -1 and drawing:
                end_x, end_y = x, y


        cv2.setMouseCallback('Defina a celula inicial', select_shape)

        while True:
            clone = image.copy()

            #desenha um retangulo nas posições definidas
            if start_x != -1:
                cv2.rectangle(clone, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

            cv2.imshow('Defina a celula inicial', clone)
            key = cv2.waitKey(1) & 0xFF

            # Ao pressionar enter salva
            if key == self.key_mapping['enter']:
                cv2.rectangle(image, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
                break

            # Ao pressionar esc sai
            elif key == self.key_mapping['esc']:
                break
            
        cv2.destroyAllWindows()
        x1, x2 = (start_x, end_x) if start_x < end_x else (end_x, start_x)
        y1, y2 = (start_y, end_y) if start_y < end_y else (end_y, start_y)
        return x1, y1, x2, y2

    

    def configure_positions(self, path=None):
        """ configura as posições dos agrupamentos eceto do primeiro
            ao inves de desenhar o retangulo, captura somente uma coordenada, superior a direita
        """
        image = self.cropped_image
        if path:
            image = cv2.imread(path)
        cv2.imshow('Selecione a posicao inicial do agrupamento desejado', image)

        x, y = -1, -1

        def select_point(event, current_x, current_y, flags, param):
            nonlocal x, y

            if event == cv2.EVENT_LBUTTONDOWN:
                image_copy = image.copy()
                x, y = current_x, current_y
                cv2.circle(image_copy, (x, y), 5, (0, 255, 0), -1)
                cv2.imshow('Selecione a posicao inicial do agrupamento desejado', image_copy)

        cv2.setMouseCallback('Selecione a posicao inicial do agrupamento desejado', select_point)

        while True:
            key = cv2.waitKey(1) & 0xFF

            if key == self.key_mapping['enter']:
                break

            elif key == self.key_mapping['esc']:
                break

        cv2.destroyAllWindows()

        return x, y
    
    def save_cropped_image(self, path):
        """ salva a imagem cortada em um path """
        cv2.imwrite(path, self.cropped_image)   