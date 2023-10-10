

import json
import os
import time
import cv2


class Config:

    _instance = None
    
    template_height_px:int
    template_width_px:int

    cell_size_x_px:int
    cell_size_y_px:int

    column_amount: int

    y_space_between_cells: int
    x_space_between_cells: int

    grouping_1_row_amount:int = None
    grouping_1_x1:int = None
    grouping_1_y1:int = None

    grouping_2_row_amount:int = None
    grouping_2_x1:int = None
    grouping_2_y1:int = None

    grouping_3_row_amount:int = None
    grouping_3_x1:int = None
    grouping_3_y1:int = None

    grouping_4_row_amount:int = None
    grouping_4_x1:int = None
    grouping_4_y1:int = None

    fill_precentage_to_consider_filled = 70
    fill_precentage_to_consider_doubtful = 50

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = cls()
    
    @staticmethod
    def is_empty():
        if Config._instance is None: return True
        conf = Config.instance()
        return not conf.grouping_1_row_amount or not conf.grouping_1_x1 or not conf.grouping_1_y1
    
    def set_template_size(self, template_path):
        template_height, template_width, _ = cv2.imread(template_path).shape
        self.template_width_px = int(template_width)
        self.template_height_px = int(template_height)

    def get_multiply_reason(self, image_height, image_width):
        return image_height / self.template_height_px, image_width / self.template_width_px

    def to_json(self, folder):
        json_object = json.dumps(Config.instance().__dict__)
        with open(os.path.join(folder, f"{time.strftime('%Y%m%d-%H%M%S')}_config.json"), "w") as outfile:
            outfile.write(json_object) 
    
    @classmethod
    def from_json(cls, json_file):
        file_content = json_file.read().decode('utf-8')   
        data = json.loads(file_content)
        Config.reset()
        for k,v in data.items():
            setattr(cls.instance(), k,v)

    def set_initial_marker(self, positions):
        self.grouping_1_x1, self.grouping_1_y1, first_cell_x2, first_cell_y2 = positions
        self.cell_size_x_px = first_cell_x2 - self.grouping_1_x1
        self.cell_size_y_px = first_cell_y2 - self.grouping_1_y1

    def draw_marker_px(self, image, x1, y1):
       cv2.rectangle(
            image, (x1, y1), 
            (x1+self.cell_size_x_px, y1+self.cell_size_y_px),
            (0, 255, 0), 2
        ) 
    
    def draw_positions(self, image_path):
        image = cv2.imread(image_path)

        # para cada agrupamento
        for i in range(4):
            # verifica se o agrupamento tem tods informações necessarias
            if not self.grouping_has_all_info(i+1):
                continue

            for column in range(self.column_amount):
                for row in range(getattr(self, f'grouping_{i+1}_row_amount')):
                    self.draw_marker_px(
                        image, 
                        getattr(self,f'grouping_{i+1}_x1') + ((self.cell_size_x_px + self.x_space_between_cells)*column), 
                        getattr(self,f'grouping_{i+1}_y1') + ((self.cell_size_y_px + self.y_space_between_cells)*row),
                    )


        cv2.imwrite(image_path, image)
    
    def grouping_has_all_info(self, grouping_idx):
       return getattr(self,f'grouping_{grouping_idx}_row_amount') and getattr(self,f'grouping_{grouping_idx}_x1') and getattr(self,f'grouping_{grouping_idx}_y1')
    
    def get_questions_amount(self):
        result = 0
        if self.grouping_1_row_amount:
            result += self.grouping_1_row_amount
        if self.grouping_2_row_amount:
            result += self.grouping_2_row_amount
        if self.grouping_3_row_amount:
            result += self.grouping_3_row_amount
        if self.grouping_4_row_amount:
            result += self.grouping_4_row_amount
        return result
        

