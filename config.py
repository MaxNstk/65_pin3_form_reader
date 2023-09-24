

class Config:

    """ """
    
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

    def __init__(self, template_width_px, template_height_px) -> None:
        self.template_width_px = int(template_width_px)
        self.template_height_px = int(template_height_px)
        self.calculate_proportion()

    def calculate_proportion(self):
        self.template_height_ss = self.template_height_px * (self.template_width_ss / self.template_width_px)

    def parse_px_posisiton_to_ss_position(self, x_px, y_px):
        return int((x_px / self.template_width_px) * self.template_width_ss), int((y_px / self.template_height_px) * self.template_height_ss)

    def to_json(self):
        raise NotImplementedError
    
    def from_json(self, json_path):
        return NotImplementedError
    
# c = Config(200, 100)

# a, b = c.parse_px_posisiton_to_ss_position(100, 50)
# print