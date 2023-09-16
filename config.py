

class Config:

    """ """
    
    template_height_px:int
    template_width_px:int

    template_width_ss:int = 1000
    template_heigth_ss:int = None


    first_cell_start_x:int
    first_cell_end_x:int

    first_cell_start_y:int
    first_cell_start_y:int

    column_amount: int

    def __init__(self, template_height, template_width) -> None:
        self.template_height = template_height
        self.template_width = template_width
    

    def calculate_proportion(self):
        self.template_heigth_ss = (self.template_height_px * self.template_width_ss)/1000