

import cv2


class Config:

    _instance = None
    
    template_height_px:int
    template_width_px:int

    template_width_ss:int = 1000
    template_height_ss:int = None

    first_cell_x1:int
    first_cell_y1:int
    first_cell_x1:int
    first_cell_y2:int

    column_amount: int
    row_amount: int

    ss_between_column: int
    ss_between_rows: int

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = cls()
    
    def set_template_size(self, template_path):
        template_height, template_width, _ = cv2.imread(template_path).shape
        self.template_width_px = int(template_width)
        self.template_height_px = int(template_height)
        self.calculate_proportion()        

    def calculate_proportion(self):
        self.template_height_ss = self.template_height_px * (self.template_width_ss / self.template_width_px)

    def parse_px_posisiton_to_ss_position(self, x_px, y_px):
        return int((x_px / self.template_width_px) * self.template_width_ss), int((y_px / self.template_height_px) * self.template_height_ss)

    def to_json(self):
        raise NotImplementedError
    
    def from_json(self, json_path):
        return NotImplementedError
    
    def set_initial_marker(self, positions):
        self.first_cell_x1, self.first_cell_y1, self.first_cell_x1, self.first_cell_y2 = positions


# c = Config(200, 100)

# a, b = c.parse_px_posisiton_to_ss_position(100, 50)
# print