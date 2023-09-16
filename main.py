import time
from image_handler import ImageHandler

from pdf_converter import PDFConverter

generation_date_str = time.strftime('%Y%m%d-%H%M%S')
img_path=f"results/image_results/{generation_date_str}.png"

PDFConverter.convert_to_jpg(pdf_path='modelos_pdf/nosso_modelo.pdf', result_path=img_path)

handler = ImageHandler(base_image_path=img_path)
handler.cropp_image()
handler.show_image()
