import pygame
from src.config import Config
from src.core.ui_manager import Button, Label, GridLayout
from src.games.playground import WhiteboardPlayground
from src.games.shapes import DrawBasicShapes
from src.screens.coming_soon import ComingSoonScreen

class MainMenu:
    """
    Main menu screen that provides access to all games and features.
    """
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        self.next_screen = None
        
        # Set up UI elements
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up UI elements for the main menu"""
        screen_width, screen_height = self.screen.get_size()
        
        # Get scaled dimensions
        scaled_font_sizes = Config.get_scaled_font_sizes()
        scaled_button_width, scaled_button_height = Config.get_scaled_button_dimensions()
        
        # Header bar
        self.header_rect = pygame.Rect(0, 0, screen_width, Config.scale_height(80))
        
        # Title
        self.title_label = Label(
            screen_width // 2,
            Config.scale_height(40),
            "CursorDraw",
            font_size=scaled_font_sizes['large'],
            centered=True
        )
        
        # Subtitle
        self.subtitle_label = Label(
            screen_width // 2,
            Config.scale_height(100),
            "Improve your cursor control through drawing games",
            font_size=scaled_font_sizes['medium'],
            centered=True
        )
        
        # Calculate spacing based on screen dimensions
        h_spacing = Config.scale_width(20)
        v_spacing = Config.scale_height(20)
        
        # Create game grid with improved styling
        self.game_grid = GridLayout(
            (screen_width - (scaled_button_width * 3 + h_spacing * 2)) // 2,
            Config.scale_height(150),
            scaled_button_width,
            scaled_button_height,
            3,  # 3 columns
            h_spacing,  # horizontal spacing
            v_spacing   # vertical spacing
        )
        
        # Add implemented games
        for game_name in Config.IMPLEMENTED_GAMES:
            button = Button(
                0, 0,  # Will be positioned by grid
                scaled_button_width,
                scaled_button_height,
                game_name,
                lambda name=game_name: self._start_game(name),
                bg_color=Config.GREEN,
                hover_color=(100, 200, 100),
                text_color=Config.WHITE,
                rounded=True,
                font_size=scaled_font_sizes['small']
            )
            self.game_grid.add_item(button)
            
        # Add coming soon games
        for game_name in Config.COMING_SOON_GAMES:
            button = Button(
                0, 0,  # Will be positioned by grid
                scaled_button_width,
                scaled_button_height,
                game_name,
                lambda name=game_name: self._show_coming_soon(name),
                bg_color=Config.GRAY,
                text_color=Config.WHITE,
                disabled=True,
                rounded=True,
                font_size=scaled_font_sizes['small']
            )
            self.game_grid.add_item(button)
            
        # Settings button
        self.settings_button = Button(
            screen_width - scaled_button_width - Config.scale_width(20),
            screen_height - scaled_button_height - Config.scale_height(20),
            scaled_button_width,
            scaled_button_height,
            "Settings",
            self._show_settings,
            bg_color=Config.BLUE,
            hover_color=(100, 150, 255),
            text_color=Config.WHITE,
            rounded=True,
            font_size=scaled_font_sizes['small']
        )
            
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEMOTION:
            self.update(event.pos)
        elif event.type == pygame.VIDEORESIZE:
            # Recreate UI elements when window is resized
            self._setup_ui()
            
        # Pass event to grid
        self.game_grid.handle_event(event)
        
        # Pass event to settings button
        self.settings_button.handle_event(event)
        
    def update(self, mouse_pos=None):
        """Update menu state"""
        if mouse_pos:
            # Update game grid buttons
            self.game_grid.update(mouse_pos)
            
            # Update settings button
            self.settings_button.update(mouse_pos)
            
        # Return next screen if set
        if self.next_screen:
            next_screen = self.next_screen
            self.next_screen = None
            return next_screen
            
        return None
        
    def render(self):
        """Render the menu"""
        # Clear screen with a gradient effect
        self.screen.fill(Config.WHITE)
        
        # Get screen dimensions
        screen_width, screen_height = self.screen.get_size()
        
        # Draw header bar
        pygame.draw.rect(self.screen, Config.BLUE, self.header_rect)
        
        # Draw title with white color for contrast against blue background
        title_color_original = self.title_label.color
        self.title_label.color = Config.WHITE
        self.title_label.draw(self.screen)
        self.title_label.color = title_color_original
        
        # Draw subtitle
        self.subtitle_label.draw(self.screen)
        
        # Draw game grid
        self.game_grid.draw(self.screen)
        
        # Draw settings button
        self.settings_button.draw(self.screen)
        
        # Draw a decorative line below the subtitle
        pygame.draw.line(
            self.screen,
            Config.GRAY,
            (screen_width // 4, Config.scale_height(120)),
            (3 * screen_width // 4, Config.scale_height(120)),
            Config.scale_height(2)
        )
        
    def _start_game(self, game_name):
        """Start the selected game"""
        self.game_state.set_current_game(game_name)
        
        if game_name == "Whiteboard Playground":
            self.next_screen = WhiteboardPlayground(self.screen, self.game_state)
        elif game_name == "Draw Basic Shapes":
            self.next_screen = DrawBasicShapes(self.screen, self.game_state)
        else:
            # For implemented games that don't have a class yet
            self.next_screen = ComingSoonScreen(self.screen, self.game_state, game_name)
            
    def _show_coming_soon(self, game_name):
        """Show the coming soon screen for a game"""
        self.next_screen = ComingSoonScreen(self.screen, self.game_state, game_name)
        
    def _show_settings(self):
        """Show settings screen (not implemented in Phase 1)"""
        # For Phase 1, we just show a coming soon screen
        self.next_screen = ComingSoonScreen(self.screen, self.game_state, "Settings") 