import os
from pdf2image import convert_from_path

class PDFConverter:
    
    """  IMAGE CONVERTER - PDF TO JPG"""

    @staticmethod
    def convert_to_jpg(pdf_path:str, result_path:str):
        images = convert_from_path(pdf_path, poppler_path=r'poppler-23.08.0/Library/bin')
        if len(images) != 1:
            raise Exception(f"O pdf base precisa possuir apenas 1 página! Quantidade atual: {len(images)}")
        images[0].save(result_path, 'JPEG')
    
    @staticmethod
    def convert_to_pdf_massive(pdf_path:str, folder:str):
        images = convert_from_path(pdf_path, poppler_path=r'poppler-23.08.0/Library/bin')
        for idx, image in enumerate(images, 1):
            image.save(os.path.join(folder,f'p{idx}.jpeg'), 'JPEG')