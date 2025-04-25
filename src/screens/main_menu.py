import pygame
from src.config import Config
from src.core.ui_manager import Button, Label, GridLayout
from src.games.playground import WhiteboardPlayground
from src.games.shapes import DrawBasicShapes
from src.games.letters import TraceTheLetter
from src.games.numbers import TraceTheNumber
from src.games.sentence import TraceTheSentence
from src.games.text_converter import TextConverterGame
from src.screens.coming_soon import ComingSoonScreen

class MainMenu:
    """
    Main menu screen that provides access to all games and features.
    """
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.game_manager = game_manager
        self.next_screen_name = None
        
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
            self._setup_ui()
            return True
            
        # Pass event to grid
        if self.game_grid.handle_event(event):
            return True
        
        # Pass event to settings button
        if self.settings_button.handle_event(event):
            return True
            
        return False
        
    def update(self, dt):
        """Update menu state"""
        mouse_pos = pygame.mouse.get_pos()
        # Update game grid buttons
        self.game_grid.update(mouse_pos)
        # Update settings button
        self.settings_button.update(mouse_pos)
            
        # Return next screen name if set
        if self.next_screen_name:
            next_name = self.next_screen_name
            self.next_screen_name = None
            return next_name
            
        return None
        
    def draw(self):
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
        """Request state change to the selected game"""
        self.next_screen_name = game_name
            
    def _show_coming_soon(self, game_name):
        """Request state change to the coming soon screen"""
        self.next_screen_name = f"coming_soon_{game_name}"
        
    def _show_settings(self):
        """Request state change to settings screen"""
        self.next_screen_name = "settings" 