import os
from pdf2image import convert_from_path
from django.conf import settings


class PDFConverter:
    
    """  IMAGE CONVERTER - PDF TO JPG"""

    @staticmethod
    def convert_to_jpg(pdf_path:str, result_path:str):
        images = convert_from_path(pdf_path)
        if len(images) != 1:
            raise Exception(f"O pdf base precisa possuir apenas 1 página! Quantidade atual: {len(images)}")
        images[0].save(result_path, 'JPEG')
    
    @staticmethod
    def convert_to_pdf_massive(pdf_path:str, folder:str):
        images = convert_from_path(pdf_path)
        for idx, image in enumerate(images, 1):
            image.save(os.path.join(folder,f'p{idx}.jpeg'), 'JPEG')