
# Code Snippet Taken from PyGame Website
# Taken from husano896's PR thread (slightly modified)
import pygame
from pygame.locals import QUIT, MOUSEWHEEL, MOUSEBUTTONDOWN, MOUSEMOTION

pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
clicked_things = []
def main():
   while True:
      for event in pygame.event.get():
         if event.type == QUIT:
            pygame.quit()
            return
         elif event.type == MOUSEWHEEL:
            print(event)
            print(event.y)  # The MOUSEWHEEL event has a 'y' attribute for scroll direction
         elif event.type == MOUSEBUTTONDOWN:
            print(f"Mouse clicked at: {event.pos}")  # Print the position of the mouse click
            clicked_things.append(event.pos)
            for x in clicked_things:
               print({x})
         elif event.type == MOUSEMOTION:
            print(f"Mouse moved to: {event.pos}")  # Print the current mouse position

      clock.tick(60)

# Execute game:
main()
