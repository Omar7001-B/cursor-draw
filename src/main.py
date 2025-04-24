import os
import sys
import pygame
from pygame.locals import *

# Add the parent directory to the path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.config import Config
from src.screens.main_menu import MainMenu
from src.core.game_state import GameState

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up the game window with resizable flag
    screen = pygame.display.set_mode(
        (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT),
        pygame.RESIZABLE
    )
    pygame.display.set_caption("CursorDraw")
    
    # Initialize clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Create game state
    game_state = GameState()
    
    # Start with the main menu
    current_screen = MainMenu(screen, game_state)
    
    # Main game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == VIDEORESIZE:
                # Handle window resize event
                width, height = event.size
                # Update the Config values to reflect the new size
                Config.SCREEN_WIDTH = width
                Config.SCREEN_HEIGHT = height
                # Recreate the display surface with the new size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                # Recreate the current screen with the new surface
                if isinstance(current_screen, MainMenu):
                    current_screen = MainMenu(screen, game_state)
                else:
                    # Get the current screen type and recreate it
                    screen_type = type(current_screen)
                    if hasattr(current_screen, 'feature_name'):
                        current_screen = screen_type(screen, game_state, current_screen.feature_name)
                    else:
                        current_screen = screen_type(screen, game_state)
            else:
                # Pass events to current screen
                current_screen.handle_event(event)
        
        # Update current screen
        next_screen = current_screen.update(pygame.mouse.get_pos())
        
        # Change screens if needed
        if next_screen and next_screen != current_screen:
            current_screen = next_screen
        
        # Render current screen
        current_screen.render()
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(Config.FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 