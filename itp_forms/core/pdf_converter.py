import os
from pdf2image import convert_from_path
from django.conf import settings
import platform


class PDFConverter:
    
    """ Classe utilitária, serve para converter arquivos pdf em jpeg"""

    @staticmethod
    def convert_to_jpg(pdf_path:str, result_path:str):
        """ Converte um arquivo unico """
        print('platform.system():  '+platform.system())
        print("os.path.join('poppler-23.08.0','Library','bin') " +os.path.join(settings.BASE_DIR,'poppler-23.08.0','Library','bin'))

        if platform.system() == 'Windows':
            images = convert_from_path(pdf_path, poppler_path=os.path.join(settings.BASE_DIR, 'poppler-23.08.0','Library','bin'))
        else:
            images = convert_from_path(pdf_path)
        if len(images) != 1:
            raise Exception(f"O pdf base precisa possuir apenas 1 página! Quantidade atual: {len(images)}")
        images[0].save(result_path, 'JPEG')
    
    @staticmethod
    def convert_to_pdf_massive(pdf_path:str, folder:str):

        """ Converte um conjunto de arquivos, recebe a pasta e coloca o indice dele em frente a cada um """
        images = convert_from_path(pdf_path, poppler_path=os.path.join(settings.BASE_DIR, 'poppler-23.08.0','Library','bin'))
        for idx, image in enumerate(images, 1):
            image.save(os.path.join(folder,f'p{idx}.jpeg'), 'JPEG')