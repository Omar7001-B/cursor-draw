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
from src.games.playground import WhiteboardPlayground
from src.games.shapes import DrawBasicShapes
from src.games.letters import TraceTheLetter
from src.games.numbers import TraceTheNumber
from src.games.sentence import TraceTheSentence
from src.games.text_converter import TextConverterGame
from src.screens.coming_soon import ComingSoonScreen
# Note: Settings screen might not exist yet, handle appropriately

# Define GameStateManager at the top level
class GameStateManager:
    def __init__(self, screen):
        self.screen = screen
        self.states = {}
        self.active_state_name = None
        self.active_state = None
        self._register_states()

    def _register_states(self):
        self.register_state('main_menu', MainMenu)
        self.register_state('Whiteboard Playground', WhiteboardPlayground)
        self.register_state('Draw Basic Shapes', DrawBasicShapes)
        self.register_state('Trace the Letter', TraceTheLetter)
        self.register_state('Trace the Number', TraceTheNumber)
        self.register_state('Trace the Sentence', TraceTheSentence)
        self.register_state('Whiteboard to Text', TextConverterGame)
        self.register_state('coming_soon', ComingSoonScreen) # Generic coming soon
        # Register specific coming soon states
        for game_name in Config.COMING_SOON_GAMES:
             state_name = f"coming_soon_{game_name}"
             self.register_state(state_name, lambda screen, manager, name=game_name: ComingSoonScreen(screen, manager, name))
        # Register settings coming soon state
        self.register_state("settings", lambda screen, manager: ComingSoonScreen(screen, manager, "Settings"))

    def register_state(self, name, state_class):
        self.states[name] = state_class
        
    def change_state(self, state_name, *args, **kwargs):
        if self.active_state:
             if hasattr(self.active_state, 'exit'):
                 self.active_state.exit() # Optional cleanup

        if state_name in self.states:
            self.active_state_name = state_name
            # Pass self (game_manager) to the state constructor
            self.active_state = self.states[state_name](self.screen, self, *args, **kwargs) 
            if hasattr(self.active_state, 'enter'):
                self.active_state.enter() # Optional setup
        else:
            print(f"Warning: State '{state_name}' not registered.")
            # Fallback or error handling
            if 'main_menu' in self.states and state_name != 'main_menu':
                self.change_state('main_menu')
            else:
                 print(f"Error: Cannot switch to unregistered state '{state_name}'.")
                 pygame.quit()
                 sys.exit(1)
        
    def handle_event(self, event):
        if self.active_state:
            # Pass event to the active state's handle_event method
            handled = self.active_state.handle_event(event)
            # Optionally return the result if states need to signal handling
            # return handled 
            
    def update(self, dt):
        if self.active_state:
            # Call the active state's update method
            next_state_name = self.active_state.update(dt) 
            # If the update method returned a state name, change state
            if next_state_name and isinstance(next_state_name, str) and next_state_name != self.active_state_name:
                self.change_state(next_state_name)
    
    def draw(self):
        if self.active_state:
            # Call the active state's draw method
            self.active_state.draw()
            
    def handle_resize(self):
        if self.active_state:
            # Check if the active state has its own resize handler
            if hasattr(self.active_state, 'handle_resize'):
                self.active_state.handle_resize()
            else: 
                # Default behavior: try to recreate the state
                print(f"Recreating state {self.active_state_name} after resize (default behavior).")
                try:
                    # Attempt to get constructor args if stored (requires states to store them)
                    current_args = getattr(self.active_state, '_init_args', ()) 
                    current_kwargs = getattr(self.active_state, '_init_kwargs', {})
                    # Recreate the state instance
                    self.active_state = self.states[self.active_state_name](self.screen, self, *current_args, **current_kwargs)
                except Exception as e:
                    # Fallback if recreation fails
                    print(f"Error recreating state after resize: {e}. Falling back to main menu.")
                    if 'main_menu' in self.states:
                        self.change_state('main_menu')
                    else: 
                        # Critical error if main menu state is missing
                        print("Error: Main menu state not found. Cannot recover from resize error.")
                        pygame.quit()
                        sys.exit(1)
                            
    def get_current_state_instance(self):
        # Return the currently active state object
        return self.active_state

def main():
    # Initialize pygame
    pygame.init()
    
    # Get the screen info to ensure our window fits within screen boundaries
    screen_info = pygame.display.Info()
    available_width = screen_info.current_w
    available_height = screen_info.current_h
    
    # Adjust initial window size if necessary to fit screen
    window_width = min(Config.SCREEN_WIDTH, available_width - 150)  # Increase margin further
    window_height = min(Config.SCREEN_HEIGHT, available_height - 150)  # Increase margin further
    
    # Update Config to reflect the adjusted size
    Config.SCREEN_WIDTH = window_width
    Config.SCREEN_HEIGHT = window_height
    
    # Center the window on the screen
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center the window instead of specifying position
    
    # Set up the game window with resizable flag
    screen = pygame.display.set_mode(
        (window_width, window_height),
        pygame.RESIZABLE
    )
    pygame.display.set_caption("CursorDraw")
    
    # Additional initialization to ensure window decorations are visible
    # Forcing a small initial resize helps on some systems
    screen = pygame.display.set_mode(
        (window_width - 1, window_height - 1),
        pygame.RESIZABLE
    )
    
    # Then set it back to intended size
    screen = pygame.display.set_mode(
        (window_width, window_height),
        pygame.RESIZABLE
    )
    
    # Initialize clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Create game state manager
    game_manager = GameStateManager(screen)
    
    # Start with the main menu state
    game_manager.change_state('main_menu') 
    
    # Main game loop
    running = True
    while running:
        # Event handling
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                running = False
            elif event.type == VIDEORESIZE:
                # Handle window resize event
                width, height = event.size
                
                # Ensure the window doesn't exceed screen boundaries
                width = min(width, available_width - 150)
                height = min(height, available_height - 150)
                
                # Update the Config values to reflect the new size
                Config.SCREEN_WIDTH = width
                Config.SCREEN_HEIGHT = height
                
                # Recreate the display surface with the new size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                game_manager.screen = screen # Update screen reference
                
                # Let the game manager handle recreating the current screen
                game_manager.handle_resize()
            else:
                # Pass events via game manager
                game_manager.handle_event(event)
        
        # Update current screen via game manager
        dt = clock.tick(Config.FPS) / 1000.0 # Calculate delta time
        game_manager.update(dt)
        
        # Render current screen via game manager
        game_manager.draw()
        
        # Update display
        pygame.display.flip()
        
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 