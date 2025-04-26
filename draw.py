import pygame
from pygame.locals import * 
from colors import * 
import math

class InitialValues:
    ZOOM_LEVEL = 1
    CELL_SIZE = 50

class Grid(InitialValues):
    """
    Create
    Reposition
    Zoom in Zoom Out
    """
    def __init__(self, screen):
        self.zoom_level: int = InitialValues.ZOOM_LEVEL 
        self.cell_size: int = InitialValues.CELL_SIZE * self.zoom_level
        self.x_map_displacement: int = 0
        self.y_map_displacement: int = 0
        self.screen = screen
        self.cells = []

    def zoom(self, zoom_level):
        self.zoom_level = zoom_level
        self.cell_size: int = 50 * self.zoom_level

    def move(self, new_displacement):
        pass

    def move_map(self):
        pass

    def convert_world_coordinates_to_grid_coordinates(self, x, y):
        """ 
        Convert (48, 30)
        To 0,0
        Because cell size is 50
        Accounts for x_y displacement
        """
        grid_x = math.floor(x/self.cell_size)
        grid_y = math.floor(y/self.cell_size)
        return grid_x, grid_y

    def increase_resolution(self):
        pass

    # Draw Functions
    def draw_grid(self) -> None:
        # Get full width window...

        for x in range(0, 10):
            self.cells.append([])
            for y in range(0, 10):
                self.cells[x].append(0)
                pygame.draw.rect(self.screen, COLOR_WHITE, 
                        pygame.Rect(x*self.cell_size, y*self.cell_size, self.cell_size, self.cell_size), 1) 
        # print(self.cells)
        pygame.display.flip()  # Updates Screen
    
    def draw_cells(self) -> None:
        pass

    def edit_array(self, x, y, val):
        self.cells[x][y] = val

    def flip_cell(self, x, y):
        if self.cells[x][y] == 1:
            self.edit_array(x,y, 0)
        elif self.cells[x][y] == 0:
            self.edit_array(x,y, 1)

    def select_dot_from_mouse_coordinates(self, mouse_x, mouse_y):
        # Array or not array
        x, y = self.convert_world_coordinates_to_grid_coordinates(mouse_x, mouse_y)
        x_loop = 0
        y_loop = 0
        self.flip_cell(x,y)
        for line in self.cells:
            for i in line:
                if i == 1:
                    pygame.draw.rect(self.screen, COLOR_WHITE, 
                                pygame.Rect(y_loop*self.cell_size, x_loop*self.cell_size, self.cell_size, self.cell_size), 0)
                elif i == 0:
                    pygame.draw.rect(self.screen, COLOR_BLACK, 
                                pygame.Rect(y_loop*self.cell_size, x_loop*self.cell_size, self.cell_size, self.cell_size), 0)    
                x_loop += 1
            y_loop += 1
            x_loop = 0
        self.draw_grid()
        pygame.display.flip()



