# REN JOSEPH E. AYANGCO
# EARLAN JOSH Q. SABILLANO
# JEA KATRINA G. JALANDONI

import pygame
from colors import *

class ToolBox:
    def __init__(self):
        self.toolbar_rect = pygame.Rect(0, 0, 640, 50)

        # Buttons inside the toolbar
        self.button_padding = 10
        self.button_height = 30
        self.button_width = 60

        self.color_button = pygame.Rect(10, 10, 30, 30)
        self.eraser_button = pygame.Rect(50, 10, 30, 30)
        self.save_button = pygame.Rect(100, 10, self.button_width, self.button_height)
        self.export_button = pygame.Rect(170, 10, self.button_width + 10, self.button_height)

        self.selected_color = COLOR_WHITE
        self.clicked_action = None  # 'color', 'eraser', 'save', 'export'

        self.font = pygame.font.SysFont("Arial", 16)

    def draw(self, surface):
        # Draw toolbar background
        pygame.draw.rect(surface, (60, 60, 60), self.toolbar_rect)

        mouse_pos = pygame.mouse.get_pos()

        # Draw Color Button
        self._draw_button(surface, self.color_button, self.selected_color, hover_highlight=True, is_icon="color", mouse_pos=mouse_pos)

        # Draw Eraser Button
        self._draw_button(surface, self.eraser_button, (220, 220, 220), hover_highlight=True, is_icon="eraser", mouse_pos=mouse_pos)

        # Draw Save Button
        self._draw_button(surface, self.save_button, (80, 80, 80), text="Save", hover_highlight=True, mouse_pos=mouse_pos)

        # Draw Export Button
        self._draw_button(surface, self.export_button, (80, 80, 80), text="Export", hover_highlight=True, mouse_pos=mouse_pos)

    def _draw_button(self, surface, rect, color, text=None, hover_highlight=False, is_icon=None, mouse_pos=(0, 0)):
        # Check if hovered
        hovered = rect.collidepoint(mouse_pos)
        draw_color = color

        if hover_highlight and hovered:
            draw_color = tuple(min(c + 40, 255) for c in color)

        pygame.draw.rect(surface, draw_color, rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_WHITE, rect, 2, border_radius=6)  # white border

        if is_icon == "color":
            # Draw small paintbrush (simple triangle)
            pygame.draw.polygon(surface, (0, 0, 0), [
                (rect.x + 7, rect.y + 7),
                (rect.x + 23, rect.y + 7),
                (rect.x + 15, rect.y + 23)
            ])
        elif is_icon == "eraser":
            # Draw eraser icon (cross)
            pygame.draw.line(surface, (255, 0, 0), rect.topleft, rect.bottomright, 2)
            pygame.draw.line(surface, (255, 0, 0), rect.topright, rect.bottomleft, 2)

        if text:
            text_surface = self.font.render(text, True, COLOR_WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        """Handle clicks and return actions."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.color_button.collidepoint(pos):
                self.clicked_action = 'color'
                return 'color'
            elif self.eraser_button.collidepoint(pos):
                self.clicked_action = 'eraser'
                return 'eraser'
            elif self.save_button.collidepoint(pos):
                self.clicked_action = 'save'
                return 'save'
            elif self.export_button.collidepoint(pos):
                self.clicked_action = 'export'
                return 'export'
        return None

    def set_color(self, color):
        """Set the selected drawing color."""
        self.selected_color = color

    def get_color(self):
        """Get the currently selected drawing color."""
        return self.selected_color
