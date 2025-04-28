import pygame

class ToolBox:
    def __init__(self):
        self.gradient_width = 400
        self.gradient_height = 20
        self.gradient_surface = self.create_gradient_surface(self.gradient_width, self.gradient_height)
        self.gradient_rect = self.gradient_surface.get_rect(topleft=(10, 10)) 

        # gradient color picker where you can drag the circle
        self.selector_pos = (self.gradient_rect.left, self.gradient_rect.centery)

        self.selected_color = (255, 0, 0)

        # erase button (basically changes the color to white but might change this)
        self.erase_color = (255, 255, 255)
        self.erase_button = pygame.Rect(10, self.gradient_rect.bottom + 20, 50, 30)

    # creates the gradient for the color picker
    def create_gradient_surface(self, width, height):
        surface = pygame.Surface((width, height))
        for x in range(width):
            hue = (x / width) * 360
            color = pygame.Color(0)
            color.hsva = (hue, 100, 100, 100)
            pygame.draw.line(surface, color, (x, 0), (x, height))
        return surface
    
    def draw(self, surface):
        surface.blit(self.gradient_surface, self.gradient_rect)

        pygame.draw.circle(surface, self.selected_color, self.selector_pos, 8)
        pygame.draw.circle(surface, (0, 0, 0), self.selector_pos, 9, 2)

        pygame.draw.rect(surface, self.erase_color, self.erase_button)
        pygame.draw.rect(surface, (0, 0, 0), self.erase_button, 2)
        pygame.draw.line(surface, (255, 0, 0), self.erase_button.topleft, self.erase_button.bottomright, 2)
        pygame.draw.line(surface, (255, 0, 0), self.erase_button.topright, self.erase_button.bottomleft, 2)

    def handle_event(self, event):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            if event.buttons[0]: 
                pos = event.pos

                if self.gradient_rect.collidepoint(pos):
                    self.selector_pos = (pos[0], self.gradient_rect.centery)
                    rel_x = pos[0] - self.gradient_rect.left
                    rel_y = self.gradient_rect.centery - self.gradient_rect.top
                    self.selected_color = self.gradient_surface.get_at((rel_x, rel_y))[:3]
                    return self.selected_color

                if self.erase_button.collidepoint(pos):
                    self.selected_color = self.erase_color
                    return self.selected_color

        return None