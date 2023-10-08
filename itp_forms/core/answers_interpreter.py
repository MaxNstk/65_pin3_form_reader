

import os
import cv2

from itp_forms.core.config import Config
from itp_forms.core.image_handler import ImageHandler


class AnswersInterpreter:

    alphabet = tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ')


    def interpret_answers(self, answers_folder):
        pages = []
        for page in os.listdir(answers_folder):
            file = os.path.join(answers_folder, page) 
            pages.append(self.interpret_page(file))

    def interpret_page(self, file):  
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
                    for col_idx, col in enumerate(row):
                        if col <= max_filled_cell_color:
                            info['filled_questions'][row_idx+1] += f' {self.alphabet[col_idx]}'
                        elif col <= max_doubtful_cell_color:
                            info['doubt_questions'][row_idx+1] += f' {self.alphabet[col_idx]}'

            cv2.imshow("Image with ROI", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows() 
       

        # w = int(Config.instance().cell_size_x_px * width_reason)
        # h = int(Config.instance().cell_size_y_px * height_reason)
        # x = int(Config.instance().grouping_1_x1 * width_reason)
        # y = int(Config.instance().grouping_1_y1 * height_reason)
        
        # roi = image[y:y+h, x:x+w]

        # # Calculate the mean color within the ROI
        # mean_color = cv2.mean(roi)

        # # Check if the mean color is close to gray or black
        # # You can adjust the threshold values as needed
        # gray_threshold = 100  # Adjust this threshold for gray
        # black_threshold = 20  # Adjust this threshold for black

        # if mean_color[0] <= black_threshold:
        #     print("The ROI is filled with black.")
        # elif mean_color[0] <= gray_threshold:
        #     print("The ROI is filled with gray.")
        # else:
        #     print("The ROI is neither black nor gray.")

        # # Display the ROI and its mean color (for visualization purposes)
        # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw a green rectangle around the ROI
        # cv2.imshow("Image with ROI", image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows() 


            