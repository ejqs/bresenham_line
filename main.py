import pygame
from pygame.locals import * 
import json
import os
import math

# Import files
from draw import Grid
from bresenham_line import *
from colors import *
from toolbox import ToolBox

class Screen:
    """A class to manage the pygame display globally with dirty rect handling"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Screen, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize the pygame display"""
        pygame.init()
        self.display = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Bresenham Line Drawing Tool")
        self.clock = pygame.time.Clock()
        self.dirty_rects = []
        
    def get_display(self):
        """Get the pygame display surface"""
        return self.display
        
    def mark_dirty(self, rect):
        """Mark a rectangle as needing update"""
        self.dirty_rects.append(rect)
        
    def update(self):
        """Update only the dirty parts of the screen"""
        pygame.display.update(self.dirty_rects)
        self.dirty_rects = []
        
    def fill(self, color, rect=None):
        """Fill the screen or a rect with a color and mark as dirty"""
        if rect:
            self.display.fill(color, rect)
            self.mark_dirty(rect)
        else:
            self.display.fill(color)
            self.mark_dirty(self.display.get_rect())
            
    def blit(self, surface, dest, area=None):
        """Blit a surface and mark the area as dirty"""
        self.display.blit(surface, dest, area)
        if area:
            rect = pygame.Rect(dest, area.size)
        else:
            rect = pygame.Rect(dest, surface.get_size())
        self.mark_dirty(rect)
            
    def draw_rect(self, color, rect, width=0):
        """Draw a rectangle and mark it as dirty"""
        pygame.draw.rect(self.display, color, rect, width)
        self.mark_dirty(rect)
        
    def draw_line(self, color, start_pos, end_pos, line_width=1):
        """Draw a line and mark its rect as dirty"""
        pygame.draw.line(self.display, color, start_pos, end_pos, line_width)
        # Calculate the rect that contains the line
        x = min(start_pos[0], end_pos[0])
        y = min(start_pos[1], end_pos[1])
        rect_width = abs(end_pos[0] - start_pos[0]) + line_width
        rect_height = abs(end_pos[1] - start_pos[1]) + line_width
        # Ensure minimum dimensions
        rect_width = max(rect_width, 1)
        rect_height = max(rect_height, 1)
        self.mark_dirty(pygame.Rect(x, y, rect_width, rect_height))

# Initialize the global screen
screen_manager = Screen()
screen = screen_manager.get_display()
clock = screen_manager.clock

# STATES
STATE_START_SCREEN = "start_screen"
STATE_DRAWING = "drawing"
STATE_LINE1 = "line1"  # First point selected
STATE_LINE2 = "line2"  # Line completed, showing result
STATE_COLOR_SELECT = "color_select"
STATE_SAVE = "save"

# Drawing Tool Modes
MODE_PEN = "pen"    # Drawing lines
MODE_ERASE = "erase"  # Erasing lines

# UI Constants
TOOLBAR_HEIGHT = 50  # Height of the toolbar

current_state = STATE_START_SCREEN
current_mode = MODE_PEN  # Default mode is pen
program_data = {
    "grid_cell_size": 50,
    "grid_width": 10,
    "grid_height": 10
}

# Font setup
font = pygame.font.SysFont("Arial", 18)
title_font = pygame.font.SysFont("Arial", 24, bold=True)

# Settings input fields
SETTING_NONE = 0
SETTING_CELL_SIZE = 1
SETTING_GRID_WIDTH = 2
SETTING_GRID_HEIGHT = 3
active_setting = SETTING_NONE
input_text = ""

# Initialize objects
bresenham_points = BresenhamPoints()
toolbox = ToolBox()
grid = None  # Will be initialized after start screen

# Line drawing variables
first_point = None
preview_point = None
last_preview_line = []  # Store the last preview line for cleanup
active_color = COLOR_WHITE
lines = []  # Store lines as [(start_point, end_point), color]
active_line_index = -1  # Index of highlighted line

def render_text(text, font, color, surface, x, y):
    """Helper function to render text"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)
    screen_manager.mark_dirty(text_rect)  # Mark the text rect as dirty

def draw_start_screen():
    """Draw the configuration screen"""
    global active_setting, input_text
    
    screen_manager.fill(COLOR_BLACK)
    
    # Title
    render_text("SIMPLELINE", title_font, COLOR_WHITE, screen, 150, 50)
    
    # New Drawing Section
    render_text("New Drawing", font, COLOR_WHITE, screen, 200, 120)
    
    # Settings boxes with highlighting for active field
    cell_size_rect = pygame.Rect(350, 150, 50, 20)
    cell_border_width = 2 if active_setting == SETTING_CELL_SIZE else 1
    cell_border_color = COLOR_GREEN if active_setting == SETTING_CELL_SIZE else COLOR_WHITE
    pygame.draw.rect(screen, cell_border_color, cell_size_rect, cell_border_width)
    screen_manager.mark_dirty(pygame.Rect(350, 150, 50, 20))
    
    # Show input text if being edited, otherwise show current value
    if active_setting == SETTING_CELL_SIZE:
        text_to_show = input_text + "|" if len(input_text) < 3 else input_text  # Add cursor
    else:
        text_to_show = str(program_data["grid_cell_size"])
    render_text(text_to_show, font, COLOR_WHITE, screen, 360, 150)
    render_text("Cell Size", font, COLOR_WHITE, screen, 200, 150)
    render_text("(Click to edit)", font, COLOR_WHITE, screen, 200, 240)
    
    grid_width_rect = pygame.Rect(350, 180, 50, 20)
    width_border_width = 2 if active_setting == SETTING_GRID_WIDTH else 1
    width_border_color = COLOR_GREEN if active_setting == SETTING_GRID_WIDTH else COLOR_WHITE
    pygame.draw.rect(screen, width_border_color, grid_width_rect, width_border_width)
    screen_manager.mark_dirty(pygame.Rect(350, 180, 50, 20))
    
    if active_setting == SETTING_GRID_WIDTH:
        text_to_show = input_text + "|" if len(input_text) < 3 else input_text
    else:
        text_to_show = str(program_data["grid_width"])
    render_text(text_to_show, font, COLOR_WHITE, screen, 360, 180)
    render_text("Grid Width", font, COLOR_WHITE, screen, 200, 180)
    
    grid_height_rect = pygame.Rect(350, 210, 50, 20)
    height_border_width = 2 if active_setting == SETTING_GRID_HEIGHT else 1
    height_border_color = COLOR_GREEN if active_setting == SETTING_GRID_HEIGHT else COLOR_WHITE
    pygame.draw.rect(screen, height_border_color, grid_height_rect, height_border_width)
    screen_manager.mark_dirty(pygame.Rect(350, 210, 50, 20))
    
    if active_setting == SETTING_GRID_HEIGHT:
        text_to_show = input_text + "|" if len(input_text) < 3 else input_text
    else:
        text_to_show = str(program_data["grid_height"])
    render_text(text_to_show, font, COLOR_WHITE, screen, 360, 210)
    render_text("Grid Height", font, COLOR_WHITE, screen, 200, 210)
    
    # Default values
    render_text("Default", font, COLOR_WHITE, screen, 420, 120)
    render_text("50", font, COLOR_WHITE, screen, 440, 150)
    render_text("10", font, COLOR_WHITE, screen, 440, 180)
    render_text("10", font, COLOR_WHITE, screen, 440, 210)
    
    # Start button
    start_button = pygame.Rect(250, 260, 140, 40)
    screen_manager.draw_rect(COLOR_GREEN, start_button)
    render_text("CREATE GRID", font, COLOR_BLACK, screen, 270, 270)
    
    # Load button
    load_button = pygame.Rect(250, 310, 140, 40)
    screen_manager.draw_rect(COLOR_BLUE, load_button)
    render_text("LOAD DRAWING", font, COLOR_BLACK, screen, 260, 320)
    
    return start_button, load_button, cell_size_rect, grid_width_rect, grid_height_rect

def draw_toolbar():
    """Draw the toolbar with color selector and options"""
    global current_mode
    
    toolbar_rect = pygame.Rect(0, 0, 640, TOOLBAR_HEIGHT)
    screen_manager.draw_rect((50, 50, 50), toolbar_rect)
    
    # Color picker
    color_rect = pygame.Rect(10, 10, 20, 20)
    screen_manager.draw_rect(active_color, color_rect)
    screen_manager.draw_rect(COLOR_WHITE, color_rect, 1)
    
    # Drawing tool - pen icon
    pen_rect = pygame.Rect(40, 10, 20, 20)
    # Highlight if this is the active tool
    bg_color = (100, 150, 100) if current_mode == MODE_PEN else (80, 80, 80)
    screen_manager.draw_rect(bg_color, pen_rect)
    # Draw pen icon (diagonal line)
    screen_manager.draw_line(COLOR_WHITE, (42, 25), (58, 15), 2)
    screen_manager.draw_rect(COLOR_WHITE, pen_rect, 1)
    
    # Eraser tool
    eraser_rect = pygame.Rect(70, 10, 20, 20)
    # Highlight if this is the active tool
    bg_color = (100, 150, 100) if current_mode == MODE_ERASE else (80, 80, 80)
    screen_manager.draw_rect(bg_color, eraser_rect)
    # Draw eraser icon (X)
    screen_manager.draw_line(COLOR_WHITE, (72, 12), (88, 28), 2)
    screen_manager.draw_line(COLOR_WHITE, (72, 28), (88, 12), 2)
    screen_manager.draw_rect(COLOR_WHITE, eraser_rect, 1)
    
    # Save button
    save_rect = pygame.Rect(100, 10, 60, 20)
    screen_manager.draw_rect((80, 80, 80), save_rect)
    render_text("Save", font, COLOR_WHITE, screen, 110, 10)
    
    # Export button
    export_rect = pygame.Rect(170, 10, 60, 20)
    screen_manager.draw_rect((80, 80, 80), export_rect)
    render_text("Export", font, COLOR_WHITE, screen, 175, 10)
    
    # Mode indicator text
    mode_text = "Mode: " + ("Drawing" if current_mode == MODE_PEN else "Erasing")
    render_text(mode_text, font, COLOR_WHITE, screen, 240, 10)
    
    return color_rect, pen_rect, eraser_rect, save_rect, export_rect

def draw_color_selector():
    """Draw color selection dialog"""
    # Create color dialog
    dialog_rect = pygame.Rect(120, 120, 400, 200)
    screen_manager.draw_rect((60, 60, 60), dialog_rect)
    screen_manager.draw_rect(COLOR_WHITE, dialog_rect, 2)
    
    render_text("Select Color", title_font, COLOR_WHITE, screen, 240, 130)
    
    color_rects = []
    for i, color in enumerate(COLOR_PALETTE):
        rect_x = 150 + (i % 3) * 80
        rect_y = 170 + (i // 3) * 40
        color_rect = pygame.Rect(rect_x, rect_y, 30, 30)
        screen_manager.draw_rect(color, color_rect)
        screen_manager.draw_rect(COLOR_WHITE, color_rect, 1)
        color_rects.append(color_rect)
    
    # Cancel button
    cancel_button = pygame.Rect(260, 270, 100, 30)
    screen_manager.draw_rect(COLOR_RED, cancel_button)
    render_text("Cancel", font, COLOR_WHITE, screen, 280, 275)
    
    return color_rects, cancel_button

def save_drawing():
    """Save the drawing as JSON"""
    save_data = {
        "grid_size": (program_data["grid_width"], program_data["grid_height"]),
        "cell_size": program_data["grid_cell_size"],
        "lines": []
    }
    
    for line, color in lines:
        save_data["lines"].append({
            "start": line[0],
            "end": line[1],
            "color": color
        })
    
    # Create save dialog
    dialog_rect = pygame.Rect(120, 120, 400, 200)
    screen_manager.draw_rect((60, 60, 60), dialog_rect)
    screen_manager.draw_rect(COLOR_WHITE, dialog_rect, 2)
    
    render_text("Save Drawing", title_font, COLOR_WHITE, screen, 240, 140)
    render_text("File saved as: drawing.json", font, COLOR_WHITE, screen, 150, 180)
    
    # Save button
    save_button = pygame.Rect(220, 240, 80, 30)
    screen_manager.draw_rect(COLOR_GREEN, save_button)
    render_text("OK", font, COLOR_BLACK, screen, 250, 245)
    
    screen_manager.update()
    
    # Save to file
    with open('drawing.json', 'w') as f:
        json.dump(save_data, f)
    
    # Wait for user to dismiss dialog
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == MOUSEBUTTONDOWN:
                if save_button.collidepoint(event.pos):
                    waiting = False
    
    return True

def load_drawing():
    """Load a drawing from a JSON file"""
    global program_data, lines, grid
    
    # Create load dialog
    dialog_rect = pygame.Rect(120, 120, 400, 200)
    screen_manager.draw_rect((60, 60, 60), dialog_rect)
    screen_manager.draw_rect(COLOR_WHITE, dialog_rect, 2)
    
    render_text("Load Drawing", title_font, COLOR_WHITE, screen, 240, 140)
    render_text("Loading from: drawing.json", font, COLOR_WHITE, screen, 150, 180)
    
    try:
        with open('drawing.json', 'r') as f:
            save_data = json.load(f)
        
        # Update program data
        if "grid_size" in save_data:
            program_data["grid_width"] = save_data["grid_size"][0]
            program_data["grid_height"] = save_data["grid_size"][1]
        if "cell_size" in save_data:
            program_data["grid_cell_size"] = save_data["cell_size"]
        
        # Clear existing lines and load saved lines
        lines = []
        for line_data in save_data["lines"]:
            # Handle different formats of start/end coordinates
            # If start/end are arrays like [x, y]
            if isinstance(line_data["start"], list):
                start = (line_data["start"][0], line_data["start"][1])
            # If start/end are objects like {"x": x, "y": y}
            else:
                start = (line_data["start"]["x"], line_data["start"]["y"])
                
            if isinstance(line_data["end"], list):
                end = (line_data["end"][0], line_data["end"][1])
            else:
                end = (line_data["end"]["x"], line_data["end"]["y"])
                
            # Handle different color formats (tuple, list, hex string)
            color = line_data["color"]
            if isinstance(color, str) and color.startswith("#"):
                # Convert hex color to RGB tuple
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                color = (r, g, b)
            elif isinstance(color, list):
                # Convert list to tuple
                color = tuple(color)
                
            lines.append([(start, end), color])
        
        # Initialize the grid with the loaded settings
        init_grid()
        
        result_message = "Drawing loaded successfully!"
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        result_message = f"Error loading file: {str(e)}"
    
    render_text(result_message, font, COLOR_WHITE, screen, 150, 200)
    
    # OK button
    ok_button = pygame.Rect(220, 240, 80, 30)
    screen_manager.draw_rect(COLOR_GREEN, ok_button)
    render_text("OK", font, COLOR_BLACK, screen, 250, 245)
    
    screen_manager.update()
    
    # Wait for user to dismiss dialog
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == MOUSEBUTTONDOWN:
                if ok_button.collidepoint(event.pos):
                    waiting = False
    
    return True

def export_as_png():
    """Export the drawing as PNG"""
    # Create export dialog
    dialog_rect = pygame.Rect(120, 120, 400, 200)
    screen_manager.draw_rect((60, 60, 60), dialog_rect)
    screen_manager.draw_rect(COLOR_WHITE, dialog_rect, 2)
    
    render_text("Export as PNG", title_font, COLOR_WHITE, screen, 240, 140)
    render_text("File exported as: drawing.png", font, COLOR_WHITE, screen, 150, 180)
    
    # Save button
    save_button = pygame.Rect(220, 240, 80, 30)
    screen_manager.draw_rect(COLOR_GREEN, save_button)
    render_text("OK", font, COLOR_BLACK, screen, 250, 245)
    
    # Save the screen region containing just the grid
    grid_surface = pygame.Surface((
        program_data["grid_width"] * program_data["grid_cell_size"],
        program_data["grid_height"] * program_data["grid_cell_size"]
    ))
    grid_surface.fill(COLOR_BLACK)
    
    # Redraw the grid on the new surface
    for line, color in lines:
        points = bresenham_line(line[0][0], line[0][1], line[1][0], line[1][1])
        for point in points:
            x, y = point
            pygame.draw.rect(grid_surface, color, 
                pygame.Rect(x * program_data["grid_cell_size"], 
                           y * program_data["grid_cell_size"], 
                           program_data["grid_cell_size"], 
                           program_data["grid_cell_size"]))
    
    # Draw grid lines
    for x in range(0, program_data["grid_width"] + 1):
        pygame.draw.line(grid_surface, COLOR_GREY, 
                        (x * program_data["grid_cell_size"], 0), 
                        (x * program_data["grid_cell_size"], program_data["grid_height"] * program_data["grid_cell_size"]))
    for y in range(0, program_data["grid_height"] + 1):
        pygame.draw.line(grid_surface, COLOR_GREY, 
                        (0, y * program_data["grid_cell_size"]), 
                        (program_data["grid_width"] * program_data["grid_cell_size"], y * program_data["grid_cell_size"]))
    
    pygame.image.save(grid_surface, "drawing.png")
    
    screen_manager.update()
    
    # Wait for user to dismiss dialog
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == MOUSEBUTTONDOWN:
                if save_button.collidepoint(event.pos):
                    waiting = False
    
    return True

def init_grid():
    """Initialize the grid with the current settings"""
    global grid
    grid = Grid(screen)
    grid.cell_size = program_data["grid_cell_size"]
    # Create empty 2D array based on grid dimensions
    grid.cells = []
    for x in range(program_data["grid_width"]):
        grid.cells.append([])
        for y in range(program_data["grid_height"]):
            grid.cells[x].append(0)
    
    # Replace the original draw_grid method with a custom one that respects our dimensions
    # and positions the grid below the toolbar
    def custom_draw_grid():
        # Fill the background
        screen.fill(COLOR_BLACK)
        
        # Draw the grid cells - offset by TOOLBAR_HEIGHT
        for x in range(0, program_data["grid_width"]):
            for y in range(0, program_data["grid_height"]):
                pygame.draw.rect(screen, COLOR_WHITE, 
                    pygame.Rect(x*grid.cell_size, y*grid.cell_size + TOOLBAR_HEIGHT, 
                              grid.cell_size, grid.cell_size), 1)
        
        # Mark the entire grid area as dirty
        grid_area = pygame.Rect(0, TOOLBAR_HEIGHT, 
                           program_data["grid_width"] * grid.cell_size,
                           program_data["grid_height"] * grid.cell_size)
        screen_manager.mark_dirty(grid_area)
        
        return True
    
    # Replace the original method
    grid.draw_grid = custom_draw_grid
    grid.draw_grid()

def clean_preview_line():
    """Clean up the previous preview line by redrawing the cells with their original color"""
    global last_preview_line, grid
    
    # Check if grid exists and if there are points to clean
    if not last_preview_line or grid is None:
        return
        
    for point in last_preview_line:
        x, y = point
        if 0 <= x < program_data["grid_width"] and 0 <= y < program_data["grid_height"]:
            # Redraw cell with background color - with toolbar offset
            cell_rect = pygame.Rect(x * grid.cell_size, y * grid.cell_size + TOOLBAR_HEIGHT, 
                                  grid.cell_size, grid.cell_size)
            screen_manager.draw_rect(COLOR_BLACK, cell_rect)
            
            # Check if this cell is part of any existing line
            for i, (line, color) in enumerate(lines):
                line_points = bresenham_line(line[0][0], line[0][1], line[1][0], line[1][1])
                if point in line_points:
                    # Redraw the cell with the appropriate color
                    line_color = COLOR_GREY if i == active_line_index else color
                    screen_manager.draw_rect(line_color, cell_rect)
                    break
            
    # Also mark the grid lines as dirty for the affected cells
    for point in last_preview_line:
        x, y = point
        if 0 <= x < program_data["grid_width"] and 0 <= y < program_data["grid_height"]:
            # Redraw grid lines for this cell - with toolbar offset
            screen_manager.draw_line(COLOR_GREY, 
                                   (x * grid.cell_size, y * grid.cell_size + TOOLBAR_HEIGHT), 
                                   ((x+1) * grid.cell_size, y * grid.cell_size + TOOLBAR_HEIGHT))
            screen_manager.draw_line(COLOR_GREY, 
                                   (x * grid.cell_size, y * grid.cell_size + TOOLBAR_HEIGHT), 
                                   (x * grid.cell_size, (y+1) * grid.cell_size + TOOLBAR_HEIGHT))
            screen_manager.draw_line(COLOR_GREY, 
                                   ((x+1) * grid.cell_size, y * grid.cell_size + TOOLBAR_HEIGHT), 
                                   ((x+1) * grid.cell_size, (y+1) * grid.cell_size + TOOLBAR_HEIGHT))
            screen_manager.draw_line(COLOR_GREY, 
                                   (x * grid.cell_size, (y+1) * grid.cell_size + TOOLBAR_HEIGHT), 
                                   ((x+1) * grid.cell_size, (y+1) * grid.cell_size + TOOLBAR_HEIGHT))
    
    last_preview_line = []

def draw_preview_line(start_point, end_point):
    """Draw a preview line between two grid points and store it for later cleanup"""
    global last_preview_line
    
    # First clean up the previous preview line
    clean_preview_line()
    
    # Calculate and draw the new preview line
    preview_line = bresenham_line(start_point[0], start_point[1], end_point[0], end_point[1])
    for point in preview_line:
        x, y = point
        if 0 <= x < program_data["grid_width"] and 0 <= y < program_data["grid_height"]:
            cell_rect = pygame.Rect(x * grid.cell_size, y * grid.cell_size + TOOLBAR_HEIGHT,
                                  grid.cell_size, grid.cell_size)
            screen_manager.draw_rect((100, 100, 100), cell_rect)
    
    # Store this preview line for future cleanup
    last_preview_line = preview_line

def find_line_at_point(mouse_pos):
        """Find if a line exists at the given mouse position"""
        # Adjust mouse position to account for toolbar offset
        adjusted_y = mouse_pos[1] - TOOLBAR_HEIGHT
        
        # Only convert if the mouse is in the grid area
        if adjusted_y >= 0:
            grid_x = math.floor(mouse_pos[0]/grid.cell_size)
            grid_y = math.floor(adjusted_y/grid.cell_size)
            point = (grid_x, grid_y)
            
            # Check if point is within grid bounds
            if 0 <= grid_x < program_data["grid_width"] and 0 <= grid_y < program_data["grid_height"]:
                for i, (line, color) in enumerate(lines):
                    line_points = bresenham_line(line[0][0], line[0][1], line[1][0], line[1][1])
                    if point in line_points:
                        return i
        return -1

def apply_setting_value():
    """Apply the current input text to the appropriate setting"""
    global active_setting, input_text, program_data
    
    if not input_text:  # If empty, don't update
        return
        
    try:
        value = int(input_text)
        
        if active_setting == SETTING_CELL_SIZE:
            # Restrict to valid range
            value = max(10, min(value, 100))
            program_data["grid_cell_size"] = value
        elif active_setting == SETTING_GRID_WIDTH:
            # Restrict to valid range
            value = max(5, min(value, 200))
            program_data["grid_width"] = value
        elif active_setting == SETTING_GRID_HEIGHT:
            # Restrict to valid range
            value = max(5, min(value, 200))
            program_data["grid_height"] = value
    except ValueError:
        # If the input isn't a valid number, don't update
        pass
    
    # Reset input state
    input_text = ""
    active_setting = SETTING_NONE

def convert_mouse_to_grid(mouse_pos):
    """Convert mouse coordinates to grid coordinates, accounting for toolbar offset"""
    # Adjust for toolbar offset
    adjusted_y = mouse_pos[1] - TOOLBAR_HEIGHT
    
    # Only convert if mouse is in the grid area
    if adjusted_y >= 0:
        grid_x = math.floor(mouse_pos[0] / grid.cell_size)
        grid_y = math.floor(adjusted_y / grid.cell_size)
        
        # Check if within grid bounds
        if 0 <= grid_x < program_data["grid_width"] and 0 <= grid_y < program_data["grid_height"]:
            return grid_x, grid_y
    
    return None  # Return None if not in grid area

def main():
    global current_state, grid, first_point, preview_point, last_preview_line, active_color, lines, active_line_index, current_mode, active_setting, input_text
    
    running = True
    start_button = None
    load_button = None
    needs_redraw = True  # Flag to control full screen redraw
    previous_state = None
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Only redraw what needs to be redrawn
        if current_state != previous_state:
            needs_redraw = True  # Full redraw when state changes
            previous_state = current_state
            # Clean up any preview line when state changes
            clean_preview_line()
            
        # Start Screen
        if current_state == STATE_START_SCREEN and needs_redraw:
            start_button, load_button, cell_size_rect, grid_width_rect, grid_height_rect = draw_start_screen()
            needs_redraw = False
            
        # Drawing Screen - draw the toolbar
        elif current_state in (STATE_DRAWING, STATE_LINE1, STATE_LINE2):
            if needs_redraw:
                screen_manager.fill(COLOR_BLACK)
                grid.draw_grid()
                needs_redraw = False
            
            # Draw all saved lines - only redraw if there's a change
            for i, (line, color) in enumerate(lines):
                line_points = bresenham_line(line[0][0], line[0][1], line[1][0], line[1][1])
                
                # Highlight the active line
                line_color = COLOR_GREY if i == active_line_index else color
                
                for point in line_points:
                    x, y = point
                    if 0 <= x < program_data["grid_width"] and 0 <= y < program_data["grid_height"]:
                        cell_rect = pygame.Rect(x * grid.cell_size, y * grid.cell_size + TOOLBAR_HEIGHT, 
                                              grid.cell_size, grid.cell_size)
                        screen_manager.draw_rect(line_color, cell_rect)
            
            # Preview line if we have a first point and mouse is over the grid
            if current_state == STATE_LINE1 and first_point:
                # Get grid coordinates using our new helper function
                grid_coords = convert_mouse_to_grid(mouse_pos)
                
                if grid_coords:
                    grid_x, grid_y = grid_coords
                    current_preview = (grid_x, grid_y)
                    if current_preview != preview_point:
                        preview_point = current_preview
                        draw_preview_line(first_point, preview_point)
            
            # Redraw grid lines to see cell boundaries clearly
            for x in range(0, program_data["grid_width"] + 1):
                screen_manager.draw_line(COLOR_GREY, 
                                        (x * grid.cell_size, TOOLBAR_HEIGHT), 
                                        (x * grid.cell_size, program_data["grid_height"] * grid.cell_size + TOOLBAR_HEIGHT))
            for y in range(0, program_data["grid_height"] + 1):
                screen_manager.draw_line(COLOR_GREY, 
                                        (0, y * grid.cell_size + TOOLBAR_HEIGHT), 
                                        (program_data["grid_width"] * grid.cell_size, y * grid.cell_size + TOOLBAR_HEIGHT))
            
            # Draw toolbar
            color_rect, pen_rect, eraser_rect, save_rect, export_rect = draw_toolbar()
            
        # Color selection screen
        elif current_state == STATE_COLOR_SELECT and needs_redraw:
            # Keep the drawing visible in the background
            color_rects, cancel_button = draw_color_selector()
            needs_redraw = False
            
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                
            elif event.type == MOUSEBUTTONDOWN:
                if current_state == STATE_START_SCREEN:
                    if start_button and start_button.collidepoint(event.pos):
                        # Before starting, apply any pending changes
                        if active_setting != SETTING_NONE:
                            apply_setting_value()
                        current_state = STATE_DRAWING
                        init_grid()
                    elif load_button and load_button.collidepoint(event.pos):
                        if load_drawing():
                            current_state = STATE_DRAWING
                    elif cell_size_rect.collidepoint(event.pos):
                        active_setting = SETTING_CELL_SIZE
                        input_text = str(program_data["grid_cell_size"])
                        needs_redraw = True
                    elif grid_width_rect.collidepoint(event.pos):
                        active_setting = SETTING_GRID_WIDTH
                        input_text = str(program_data["grid_width"])
                        needs_redraw = True
                    elif grid_height_rect.collidepoint(event.pos):
                        active_setting = SETTING_GRID_HEIGHT
                        input_text = str(program_data["grid_height"])
                        needs_redraw = True
                    else:
                        # If clicked outside input fields, apply any pending changes
                        if active_setting != SETTING_NONE:
                            apply_setting_value()
                            active_setting = SETTING_NONE
                            needs_redraw = True
                elif current_state == STATE_DRAWING:
                    # Check toolbar buttons
                    color_rect, pen_rect, eraser_rect, save_rect, export_rect = draw_toolbar()
                    
                    if color_rect.collidepoint(event.pos):
                        # Open color picker
                        current_state = STATE_COLOR_SELECT
                    elif pen_rect.collidepoint(event.pos):
                        # Switch to pen tool mode
                        current_mode = MODE_PEN
                        needs_redraw = True  # Update toolbar to show selected tool
                    elif eraser_rect.collidepoint(event.pos):
                        # Switch to eraser mode
                        current_mode = MODE_ERASE
                        needs_redraw = True  # Update toolbar to show selected tool
                        # Check if clicking on existing line to erase it
                        line_index = find_line_at_point(event.pos)
                        if line_index >= 0:
                            # Erase the line by removing it from the lines list
                            lines.pop(line_index)
                            active_line_index = -1
                            needs_redraw = True  # Force redraw to update the screen
                    elif save_rect.collidepoint(event.pos):
                        # Save drawing
                        if not save_drawing():
                            running = False
                    elif export_rect.collidepoint(event.pos):
                        # Export drawing as PNG
                        if not export_as_png():
                            running = False
                    else:
                        # Check if clicking on existing line
                        line_index = find_line_at_point(event.pos)
                        if line_index >= 0:
                            if current_mode == MODE_ERASE:
                                # In eraser mode, delete the line
                                lines.pop(line_index)
                                active_line_index = -1
                                needs_redraw = True
                            elif line_index == active_line_index:
                                # In pen mode, if already selected, deselect it
                                active_line_index = -1
                            else:
                                # In pen mode, select the line
                                active_line_index = line_index
                        elif current_mode == MODE_PEN:
                            # Use our consistent coordinate conversion function
                            grid_coords = convert_mouse_to_grid(event.pos)
                            if grid_coords:
                                grid_x, grid_y = grid_coords
                                first_point = (grid_x, grid_y)
                                preview_point = (grid_x, grid_y)
                                current_state = STATE_LINE1
                                active_line_index = -1  # Deselect any selected line
                
                elif current_state == STATE_LINE1:
                    # Adjust mouse position to account for toolbar offset
                    adjusted_y = event.pos[1] - TOOLBAR_HEIGHT
                    
                    # Only proceed if mouse is in grid area
                    if adjusted_y >= 0:
                        grid_x = math.floor(event.pos[0]/grid.cell_size)
                        grid_y = math.floor(adjusted_y/grid.cell_size)
                        
                        if 0 <= grid_x < program_data["grid_width"] and 0 <= grid_y < program_data["grid_height"]:
                            # Clean up the preview line
                            clean_preview_line()
                            
                            # Complete the line
                            second_point = (grid_x, grid_y)
                            lines.append([(first_point, second_point), active_color])
                            first_point = None
                            preview_point = None
                            current_state = STATE_DRAWING
                            needs_redraw = True  # Force redraw to show the new line properly
                
                elif current_state == STATE_COLOR_SELECT:
                    color_rects, cancel_button = draw_color_selector()
                    
                    # Check if a color was clicked
                    for i, rect in enumerate(color_rects):
                        if rect.collidepoint(event.pos):
                            active_color = COLOR_PALETTE[i]
                            current_state = STATE_DRAWING
                            break
                    
                    # Check if cancel was clicked
                    if cancel_button.collidepoint(event.pos):
                        current_state = STATE_DRAWING
            
            elif event.type == MOUSEMOTION:
                if current_state == STATE_LINE1:
                    # Use our consistent coordinate conversion function
                    grid_coords = convert_mouse_to_grid(event.pos)
                    if grid_coords:
                        grid_x, grid_y = grid_coords
                        # Only update if we moved to a different grid cell
                        current_preview = (grid_x, grid_y)
                        if current_preview != preview_point:
                            preview_point = current_preview
                            draw_preview_line(first_point, preview_point)
            
            # Handle ESC key to cancel line drawing and other keyboard inputs
            elif event.type == KEYDOWN:
                if current_state == STATE_START_SCREEN:
                    # Handle direct keyboard input for settings
                    if active_setting != SETTING_NONE:
                        if event.key == K_ESCAPE:
                            # Cancel editing the setting
                            active_setting = SETTING_NONE
                            input_text = ""
                            needs_redraw = True
                        elif event.key == K_RETURN or event.key == K_KP_ENTER:
                            # Confirm the setting
                            apply_setting_value()
                            needs_redraw = True
                        elif event.key == K_BACKSPACE:
                            # Remove last character
                            input_text = input_text[:-1]
                            needs_redraw = True
                        elif event.unicode.isdigit() and len(input_text) < 3:
                            # Add digit to input text if it's not too long
                            input_text += event.unicode
                            needs_redraw = True
                    # Continue with default navigation keys
                    elif event.key == K_UP:
                        program_data["grid_cell_size"] += 10
                        if program_data["grid_cell_size"] > 100:
                            program_data["grid_cell_size"] = 100
                        needs_redraw = True
                    elif event.key == K_DOWN:
                        program_data["grid_cell_size"] -= 10
                        if program_data["grid_cell_size"] < 10:
                            program_data["grid_cell_size"] = 10
                        needs_redraw = True
                    elif event.key == K_LEFT:
                        if pygame.key.get_mods() & KMOD_SHIFT:
                            program_data["grid_height"] -= 1
                            if program_data["grid_height"] < 5:
                                program_data["grid_height"] = 5
                        else:
                            program_data["grid_width"] -= 1
                            if program_data["grid_width"] < 5:
                                program_data["grid_width"] = 5
                        needs_redraw = True
                    elif event.key == K_RIGHT:
                        if pygame.key.get_mods() & KMOD_SHIFT:
                            program_data["grid_height"] += 1
                            if program_data["grid_height"] > 20:
                                program_data["grid_height"] = 20
                        else:
                            program_data["grid_width"] += 1
                            if program_data["grid_width"] > 20:
                                program_data["grid_width"] = 20
                        needs_redraw = True
                    
                # Add ESC key handling when in the middle of drawing a line
                elif current_state == STATE_LINE1 and event.key == K_ESCAPE:
                    # Cancel the current line drawing operation
                    clean_preview_line()
                    first_point = None
                    preview_point = None
                    current_state = STATE_DRAWING
                    render_text("Line drawing canceled", font, COLOR_RED, screen, 300, 10)
                    # Make sure this message disappears after a brief time
                    pygame.time.set_timer(pygame.USEREVENT + 1, 1500)  # Set timer for 1.5 seconds
    
        # Handle timer events (for temporary messages)
            elif event.type == pygame.USEREVENT + 1:
                # Clear the cancellation message by redrawing the toolbar
                if current_state == STATE_DRAWING:
                    color_rect, pen_rect, eraser_rect, save_rect, export_rect = draw_toolbar()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Disable the timer
    
        screen_manager.update()
        clock.tick(60)
    
    pygame.quit()

# Execute game:
if __name__ == "__main__":
    main()
