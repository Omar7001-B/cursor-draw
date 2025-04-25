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
    
    # Get the screen info to ensure our window fits within screen boundaries
    screen_info = pygame.display.Info()
    available_width = screen_info.current_w
    available_height = screen_info.current_h
    
    # Adjust initial window size if necessary to fit screen
    window_width = min(Config.SCREEN_WIDTH, available_width - 100)  # Increase margin
    window_height = min(Config.SCREEN_HEIGHT, available_height - 100)  # Increase margin for window controls
    
    # Update Config to reflect the adjusted size
    Config.SCREEN_WIDTH = window_width
    Config.SCREEN_HEIGHT = window_height
    
    # Position the window properly - ensure it's not at the edge of the screen
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{50},{50}"  # Position at (50,50)
    
    # Set up the game window with resizable flag
    screen = pygame.display.set_mode(
        (window_width, window_height),
        pygame.RESIZABLE
    )
    pygame.display.set_caption("CursorDraw")
    
    # Force the window to be positioned correctly by moving it after creation
    # This helps ensure the window decorations (title bar) are visible
    pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
    
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
                
                # Ensure the window doesn't exceed screen boundaries
                width = min(width, available_width - 100)
                height = min(height, available_height - 100)
                
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