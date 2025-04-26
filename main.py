
# Code Snippet Taken from PyGame Website
# Taken from husano896's PR thread (slightly modified)
import pygame
from pygame.locals import * 

# Import files
from draw import Grid

pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
grid = Grid(screen)


def main():
   grid.draw_grid()
   while True:
      for event in pygame.event.get():
         if event.type == QUIT:
            pygame.quit()
            return
         elif event.type == MOUSEWHEEL:
            print(event)
            print(event.y)  # The MOUSEWHEEL event has a 'y' attribute for scroll direction
         elif event.type == MOUSEBUTTONDOWN:
            # print(f"Mouse clicked at: {event.pos}")  # Print the position of the mouse click
            grid.select_dot_from_mouse_coordinates(event.pos[0], event.pos[1])
         elif event.type == MOUSEMOTION:
            pass
            # print(f"Mouse moved to: {event.pos}")  # Print the current mouse position
      clock.tick(60)

# Execute game:
main()
