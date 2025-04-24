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
        
        # Title
        self.title_label = Label(
            screen_width // 2,
            screen_height // 3,
            f"{self.feature_name}",
            font_size=Config.FONT_LARGE,
            centered=True
        )
        
        # Coming soon message
        self.message_label = Label(
            screen_width // 2,
            screen_height // 2,
            "Coming Soon!",
            font_size=Config.FONT_LARGE,
            color=Config.RED,
            centered=True
        )
        
        # Additional info
        self.info_label = Label(
            screen_width // 2,
            screen_height // 2 + 70,
            "This feature is currently under development.",
            font_size=Config.FONT_MEDIUM,
            centered=True
        )
        
        # Back button
        self.back_button = Button(
            screen_width // 2 - Config.BUTTON_WIDTH // 2,
            screen_height - 100,
            Config.BUTTON_WIDTH,
            Config.BUTTON_HEIGHT,
            "Back to Menu",
            self._go_back_to_menu
        )
            
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEMOTION:
            # Update button hover state
            self.back_button.update(event.pos)
            
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
        
        # Draw labels
        self.title_label.draw(self.screen)
        self.message_label.draw(self.screen)
        self.info_label.draw(self.screen)
        
        # Draw back button
        self.back_button.draw(self.screen)
        
    def _go_back_to_menu(self):
        """Go back to the main menu"""
        from src.screens.main_menu import MainMenu
        self.next_screen = MainMenu(self.screen, self.game_state) 