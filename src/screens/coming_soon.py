import pygame
from src.config import Config
from src.core.ui_manager import Button, Label

class ComingSoonScreen:
    """
    Screen shown when a feature is not yet implemented.
    """
    def __init__(self, screen, game_state, feature_name):
        self.screen = screen
        self.game_state = game_state
        self.feature_name = feature_name
        self.next_screen = None
        
        # Set up UI elements
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up UI elements for the coming soon screen"""
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
            f"{self.feature_name}",
            font_size=scaled_font_sizes['large'],
            centered=True
        )
        
        # Coming soon message
        self.message_label = Label(
            screen_width // 2,
            screen_height // 2,
            "Coming Soon!",
            font_size=scaled_font_sizes['large'],
            color=Config.RED,
            centered=True
        )
        
        # Additional info
        self.info_label = Label(
            screen_width // 2,
            screen_height // 2 + Config.scale_height(70),
            "This feature is currently under development.",
            font_size=scaled_font_sizes['medium'],
            centered=True
        )
        
        # Back button
        self.back_button = Button(
            screen_width // 2 - scaled_button_width // 2,
            screen_height - Config.scale_height(100),
            scaled_button_width,
            scaled_button_height,
            "Back to Menu",
            self._go_back_to_menu,
            bg_color=Config.BLUE,
            hover_color=(100, 150, 255),
            text_color=Config.WHITE,
            rounded=True,
            font_size=scaled_font_sizes['small']
        )
            
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEMOTION:
            # Update button hover state
            self.back_button.update(event.pos)
        elif event.type == pygame.VIDEORESIZE:
            # Recreate UI elements when window is resized
            self._setup_ui()
            
        # Handle button clicks
        self.back_button.handle_event(event)
        
    def update(self, mouse_pos=None):
        """Update screen state"""
        if mouse_pos:
            # Update back button
            self.back_button.update(mouse_pos)
            
        # Return next screen if set
        if self.next_screen:
            next_screen = self.next_screen
            self.next_screen = None
            return next_screen
            
        return None
        
    def render(self):
        """Render the screen"""
        # Clear screen
        self.screen.fill(Config.WHITE)
        
        # Draw header bar
        pygame.draw.rect(self.screen, Config.BLUE, self.header_rect)
        
        # Draw title with white color for contrast against blue background
        title_color_original = self.title_label.color
        self.title_label.color = Config.WHITE
        self.title_label.draw(self.screen)
        self.title_label.color = title_color_original
        
        # Draw coming soon box with scaled dimensions
        box_width = Config.scale_width(600)
        box_height = Config.scale_height(300)
        box_rect = pygame.Rect(
            (self.screen.get_width() - box_width) // 2,
            (self.screen.get_height() - box_height) // 2 - Config.scale_height(30),
            box_width,
            box_height
        )
        pygame.draw.rect(self.screen, Config.LIGHT_GRAY, box_rect, border_radius=Config.scale_height(15))
        pygame.draw.rect(self.screen, Config.GRAY, box_rect, Config.scale_height(3), border_radius=Config.scale_height(15))
        
        # Draw labels
        self.message_label.draw(self.screen)
        self.info_label.draw(self.screen)
        
        # Draw back button
        self.back_button.draw(self.screen)
        
    def _go_back_to_menu(self):
        """Go back to the main menu"""
        from src.screens.main_menu import MainMenu
        self.next_screen = MainMenu(self.screen, self.game_state) 