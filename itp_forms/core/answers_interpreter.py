

import os
from threading import Thread
import cv2
from django.shortcuts import redirect
from openpyxl import Workbook

from itp_forms.core.config import Config
from itp_forms.core.image_handler import ImageHandler


class AnswersInterpreter:

    alphabet = tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    def __init__(self,answers_folder) -> None:
        self.answers_folder = answers_folder
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.title = f"Exportação de do formulário {os.path.basename(self.answers_folder)}"

    def interpret_answers(self):
        threads = []
        for row, page in enumerate(os.listdir(self.answers_folder), 1):
            file = os.path.join(self.answers_folder, page) 
            # pages.append(self.interpret_page(file, row))
            thread = Thread(target=self.interpret_page, args=(file, row))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.wb.save('media/teste/foi.xlsx')
        return redirect("render_answers")
        
    def interpret_page(self, file, ws_row_index):  
        """
            1 : A
            2: B C
            3: 0 -- Rrepresenta que não há certeza da leitura feita
        """ 

        info = {
            'filled_questions':{},
            'doubt_questions':{}        
        }
        
        handler = ImageHandler(base_image_path=file)
        image = handler.cropp_image()
        # handler.rotate_image()

        image_height, image_width, _ = image.shape

        # todo mudar 
        # config = Config.from_json(open('utils/configs/20231004-194329_config.json', '+a'))
        config = Config.instance()
        x_axis_reason, y_axis_reason = config.get_multiply_reason(image_height, image_width)

        x_space_between_cells = config.x_space_between_cells * x_axis_reason
        y_space_between_cells = config.y_space_between_cells * y_axis_reason

        cell_size_x_px = config.cell_size_x_px * x_axis_reason
        cell_size_y_px = config.cell_size_y_px * y_axis_reason
        
        mean_cells_color = []

        highest_mean_color = 0
        lowest_mean_color = 999

        # para cada agrupamento
        for i in range(1,5):
            grouping = []

            # verifica se o agrupamento tem todas informações necessarias
            if not config.grouping_has_all_info(i):
                break

            # cada coluna é uma questão
            for row in range(getattr(config, f'grouping_{i}_row_amount')):
                print("")
                row_cells = []

                for column in range(config.column_amount):
                    x1 = (getattr(config,f'grouping_{i}_x1') * x_axis_reason) + ((cell_size_x_px + x_space_between_cells) * column)                
                    y1 = (getattr(config,f'grouping_{i}_y1') * y_axis_reason) + ((cell_size_y_px + y_space_between_cells) * row)
                    cell = image[int(y1):int(y1+cell_size_y_px), int(x1):int(x1+cell_size_x_px)]
                    mean_color = cv2.mean(cell)[0]

                    if mean_color > highest_mean_color:
                        highest_mean_color = mean_color
                    elif mean_color < lowest_mean_color:
                        lowest_mean_color = mean_color

                    row_cells.append(mean_color)
                    print(str(int(mean_color))+"  ", end="")
                    cv2.rectangle(
                        image, (int(x1), int(y1)), 
                        (int(x1+cell_size_x_px), int(y1+cell_size_y_px)),
                        (0, 255, 0), 2
                    )
                grouping.append(row_cells)  
            mean_cells_color.append(grouping)          
        
        if mean_cells_color:
            color_diff = highest_mean_color - lowest_mean_color

            max_filled_cell_color = int(lowest_mean_color + ((1 - config.fill_precentage_to_consider_filled/100)*color_diff))
            max_doubtful_cell_color = int(lowest_mean_color + ((1- config.fill_precentage_to_consider_doubtful/100)*color_diff))

            for grouping in mean_cells_color:
                for row_idx, row in enumerate(grouping):
                    info['filled_questions'][row_idx+1] = ''
                    info['doubt_questions'][row_idx+1] = ''
                    ws_cell = self.ws[f"{self.alphabet[row_idx]}{ws_row_index}"]
                    ws_cell.value = ''
                    for col_idx, col in enumerate(row):
                        if col <= max_filled_cell_color:
                            info['filled_questions'][row_idx+1] += f' {self.alphabet[col_idx]}'
                            ws_cell.value = ws_cell.value + f' {self.alphabet[col_idx]}'
                        elif col <= max_doubtful_cell_color:
                            info['doubt_questions'][row_idx+1] += f' {self.alphabet[col_idx]}'

            # cv2.imshow("Image with ROI", image)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows() 
            # return mean_cells_color
    