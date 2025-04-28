import pygame
from pygame.locals import * 
import json
import os

# Import files
from draw import Grid
from bresenham_line import *
from colors import *
from toolbox import ToolBox

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Bresenham Line Drawing Tool")
clock = pygame.time.Clock()

# STATES
STATE_START_SCREEN = "start_screen"
STATE_DRAWING = "drawing"
STATE_LINE1 = "line1"  # First point selected
STATE_LINE2 = "line2"  # Line completed, showing result
STATE_COLOR_SELECT = "color_select"
STATE_SAVE = "save"

current_state = STATE_START_SCREEN
program_data = {
    "grid_cell_size": 50,
    "grid_width": 10,
    "grid_height": 10
}

# Font setup
font = pygame.font.SysFont("Arial", 18)
title_font = pygame.font.SysFont("Arial", 24, bold=True)

# Initialize objects
bresenham_points = BresenhamPoints()
toolbox = ToolBox()
grid = None  # Will be initialized after start screen

# Line drawing variables
first_point = None
preview_point = None
active_color = COLOR_WHITE
lines = []  # Store lines as [(start_point, end_point), color]
active_line_index = -1  # Index of highlighted line

def render_text(text, font, color, surface, x, y):
    """Helper function to render text"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def draw_start_screen():
    """Draw the configuration screen"""
    screen.fill(COLOR_BLACK)
    
    # Title
    render_text("BRESENHAM LINE DRAWING TOOL", title_font, COLOR_WHITE, screen, 150, 50)
    
    # New Drawing Section
    render_text("New Drawing", font, COLOR_WHITE, screen, 200, 120)
    
    # Settings boxes
    pygame.draw.rect(screen, COLOR_WHITE, pygame.Rect(350, 150, 50, 20), 1)
    render_text(str(program_data["grid_cell_size"]), font, COLOR_WHITE, screen, 360, 150)
    render_text("Cell Size", font, COLOR_WHITE, screen, 200, 150)
    
    pygame.draw.rect(screen, COLOR_WHITE, pygame.Rect(350, 180, 50, 20), 1)
    render_text(str(program_data["grid_width"]), font, COLOR_WHITE, screen, 360, 180)
    render_text("Grid Width", font, COLOR_WHITE, screen, 200, 180)
    
    pygame.draw.rect(screen, COLOR_WHITE, pygame.Rect(350, 210, 50, 20), 1)
    render_text(str(program_data["grid_height"]), font, COLOR_WHITE, screen, 360, 210)
    render_text("Grid Height", font, COLOR_WHITE, screen, 200, 210)
    
    # Default values
    render_text("Default", font, COLOR_WHITE, screen, 420, 120)
    render_text("50", font, COLOR_WHITE, screen, 440, 150)
    render_text("10", font, COLOR_WHITE, screen, 440, 180)
    render_text("10", font, COLOR_WHITE, screen, 440, 210)
    
    # Start button
    start_button = pygame.Rect(250, 260, 140, 40)
    pygame.draw.rect(screen, COLOR_GREEN, start_button)
    render_text("CREATE GRID", font, COLOR_BLACK, screen, 270, 270)
    
    return start_button

def draw_toolbar():
    """Draw the toolbar with color selector and options"""
    toolbar_rect = pygame.Rect(0, 0, 640, 40)
    pygame.draw.rect(screen, (50, 50, 50), toolbar_rect)
    
    # Color picker
    color_rect = pygame.Rect(10, 10, 20, 20)
    pygame.draw.rect(screen, active_color, color_rect)
    pygame.draw.rect(screen, COLOR_WHITE, color_rect, 1)
    
    # Eraser tool
    eraser_rect = pygame.Rect(40, 10, 20, 20)
    pygame.draw.rect(screen, (80, 80, 80), eraser_rect)
    pygame.draw.line(screen, COLOR_WHITE, (40, 10), (60, 30), 2)
    pygame.draw.line(screen, COLOR_WHITE, (40, 30), (60, 10), 2)
    
    # Save button
    save_rect = pygame.Rect(70, 10, 60, 20)
    pygame.draw.rect(screen, (80, 80, 80), save_rect)
    render_text("Save", font, COLOR_WHITE, screen, 80, 10)
    
    # Export button
    export_rect = pygame.Rect(140, 10, 60, 20)
    pygame.draw.rect(screen, (80, 80, 80), export_rect)
    render_text("Export", font, COLOR_WHITE, screen, 145, 10)
    
    return color_rect, eraser_rect, save_rect, export_rect

def draw_color_selector():
    """Draw color selection dialog"""
    # Create color dialog
    dialog_rect = pygame.Rect(120, 120, 400, 200)
    pygame.draw.rect(screen, (60, 60, 60), dialog_rect)
    pygame.draw.rect(screen, COLOR_WHITE, dialog_rect, 2)
    
    render_text("Select Color", title_font, COLOR_WHITE, screen, 240, 130)
    
    color_rects = []
    for i, color in enumerate(COLOR_PALETTE):
        rect_x = 150 + (i % 3) * 80
        rect_y = 170 + (i // 3) * 40
        color_rect = pygame.Rect(rect_x, rect_y, 30, 30)
        pygame.draw.rect(screen, color, color_rect)
        pygame.draw.rect(screen, COLOR_WHITE, color_rect, 1)
        color_rects.append(color_rect)
    
    # Cancel button
    cancel_button = pygame.Rect(260, 270, 100, 30)
    pygame.draw.rect(screen, COLOR_RED, cancel_button)
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
    pygame.draw.rect(screen, (60, 60, 60), dialog_rect)
    pygame.draw.rect(screen, COLOR_WHITE, dialog_rect, 2)
    
    render_text("Save Drawing", title_font, COLOR_WHITE, screen, 240, 140)
    render_text("File saved as: drawing.json", font, COLOR_WHITE, screen, 150, 180)
    
    # Save button
    save_button = pygame.Rect(220, 240, 80, 30)
    pygame.draw.rect(screen, COLOR_GREEN, save_button)
    render_text("OK", font, COLOR_BLACK, screen, 250, 245)
    
    pygame.display.flip()
    
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

def export_as_png():
    """Export the drawing as PNG"""
    # Create export dialog
    dialog_rect = pygame.Rect(120, 120, 400, 200)
    pygame.draw.rect(screen, (60, 60, 60), dialog_rect)
    pygame.draw.rect(screen, COLOR_WHITE, dialog_rect, 2)
    
    render_text("Export as PNG", title_font, COLOR_WHITE, screen, 240, 140)
    render_text("File exported as: drawing.png", font, COLOR_WHITE, screen, 150, 180)
    
    # Save button
    save_button = pygame.Rect(220, 240, 80, 30)
    pygame.draw.rect(screen, COLOR_GREEN, save_button)
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
    
    pygame.display.flip()
    
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
    grid.draw_grid()

def find_line_at_point(mouse_pos):
    """Find if a line exists at the given mouse position"""
    grid_x, grid_y = grid.convert_world_coordinates_to_grid_coordinates(mouse_pos[0], mouse_pos[1])
    point = (grid_x, grid_y)
    
    for i, (line, color) in enumerate(lines):
        line_points = bresenham_line(line[0][0], line[0][1], line[1][0], line[1][1])
        if point in line_points:
            return i
    return -1

def main():
    global current_state, grid, first_point, preview_point, active_color, lines, active_line_index
    
    running = True
    start_button = None
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Start Screen
        if current_state == STATE_START_SCREEN:
            start_button = draw_start_screen()
            
        # Drawing Screen - draw the toolbar
        elif current_state in (STATE_DRAWING, STATE_LINE1, STATE_LINE2):
            screen.fill(COLOR_BLACK)
            
            # Draw grid and all existing lines
            grid.draw_grid()
            
            # Draw all saved lines
            for i, (line, color) in enumerate(lines):
                line_points = bresenham_line(line[0][0], line[0][1], line[1][0], line[1][1])
                
                # Highlight the active line
                line_color = COLOR_GREY if i == active_line_index else color
                
                for point in line_points:
                    x, y = point
                    if 0 <= x < program_data["grid_width"] and 0 <= y < program_data["grid_height"]:
                        pygame.draw.rect(screen, line_color, 
                                      pygame.Rect(x * grid.cell_size, y * grid.cell_size, 
                                                grid.cell_size, grid.cell_size))
            
            # Preview line if we have a first point and mouse is over the grid
            if current_state == STATE_LINE1 and preview_point:
                grid_x, grid_y = grid.convert_world_coordinates_to_grid_coordinates(mouse_pos[0], mouse_pos[1])
                if 0 <= grid_x < program_data["grid_width"] and 0 <= grid_y < program_data["grid_height"]:
                    preview_line = bresenham_line(first_point[0], first_point[1], grid_x, grid_y)
                    for point in preview_line:
                        x, y = point
                        if 0 <= x < program_data["grid_width"] and 0 <= y < program_data["grid_height"]:
                            pygame.draw.rect(screen, (100, 100, 100), 
                                          pygame.Rect(x * grid.cell_size, y * grid.cell_size, 
                                                    grid.cell_size, grid.cell_size))
            
            # Redraw grid lines to see cell boundaries clearly
            for x in range(0, program_data["grid_width"] + 1):
                pygame.draw.line(screen, COLOR_GREY, 
                                (x * grid.cell_size, 0), 
                                (x * grid.cell_size, program_data["grid_height"] * grid.cell_size))
            for y in range(0, program_data["grid_height"] + 1):
                pygame.draw.line(screen, COLOR_GREY, 
                                (0, y * grid.cell_size), 
                                (program_data["grid_width"] * grid.cell_size, y * grid.cell_size))
            
            # Draw toolbar
            color_rect, eraser_rect, save_rect, export_rect = draw_toolbar()
            
        # Color selection screen
        elif current_state == STATE_COLOR_SELECT:
            # Keep the drawing visible in the background
            color_rects, cancel_button = draw_color_selector()
            
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                
            elif event.type == MOUSEBUTTONDOWN:
                if current_state == STATE_START_SCREEN and start_button and start_button.collidepoint(event.pos):
                    current_state = STATE_DRAWING
                    init_grid()
                    
                elif current_state == STATE_DRAWING:
                    # Check toolbar buttons
                    color_rect, eraser_rect, save_rect, export_rect = draw_toolbar()
                    
                    if color_rect.collidepoint(event.pos):
                        # Open color picker
                        current_state = STATE_COLOR_SELECT
                    elif eraser_rect.collidepoint(event.pos):
                        # Activate eraser (will delete line on click)
                        active_color = COLOR_BLACK
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
                            # If already selected, delete the line
                            if line_index == active_line_index:
                                lines.pop(line_index)
                                active_line_index = -1
                            else:
                                # Select the line
                                active_line_index = line_index
                        else:
                            # Start drawing a new line
                            grid_x, grid_y = grid.convert_world_coordinates_to_grid_coordinates(event.pos[0], event.pos[1])
                            if 0 <= grid_x < program_data["grid_width"] and 0 <= grid_y < program_data["grid_height"]:
                                first_point = (grid_x, grid_y)
                                preview_point = (grid_x, grid_y)
                                current_state = STATE_LINE1
                                active_line_index = -1  # Deselect any selected line
                
                elif current_state == STATE_LINE1:
                    grid_x, grid_y = grid.convert_world_coordinates_to_grid_coordinates(event.pos[0], event.pos[1])
                    if 0 <= grid_x < program_data["grid_width"] and 0 <= grid_y < program_data["grid_height"]:
                        # Complete the line
                        second_point = (grid_x, grid_y)
                        lines.append([(first_point, second_point), active_color])
                        first_point = None
                        preview_point = None
                        current_state = STATE_DRAWING
                
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
                    grid_x, grid_y = grid.convert_world_coordinates_to_grid_coordinates(event.pos[0], event.pos[1])
                    if 0 <= grid_x < program_data["grid_width"] and 0 <= grid_y < program_data["grid_height"]:
                        preview_point = (grid_x, grid_y)
            
            # Handle start screen inputs to change grid settings
            elif event.type == KEYDOWN and current_state == STATE_START_SCREEN:
                if event.key == K_UP:
                    program_data["grid_cell_size"] += 10
                    if program_data["grid_cell_size"] > 100:
                        program_data["grid_cell_size"] = 100
                elif event.key == K_DOWN:
                    program_data["grid_cell_size"] -= 10
                    if program_data["grid_cell_size"] < 10:
                        program_data["grid_cell_size"] = 10
                elif event.key == K_LEFT:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        program_data["grid_height"] -= 1
                        if program_data["grid_height"] < 5:
                            program_data["grid_height"] = 5
                    else:
                        program_data["grid_width"] -= 1
                        if program_data["grid_width"] < 5:
                            program_data["grid_width"] = 5
                elif event.key == K_RIGHT:
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        program_data["grid_height"] += 1
                        if program_data["grid_height"] > 20:
                            program_data["grid_height"] = 20
                    else:
                        program_data["grid_width"] += 1
                        if program_data["grid_width"] > 20:
                            program_data["grid_width"] = 20
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

# Execute game:
if __name__ == "__main__":
    main()
