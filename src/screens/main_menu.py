import pygame
from src.config import Config
from src.core.ui_manager import Button, Label, GridLayout
from src.games.playground import WhiteboardPlayground
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
        
        # Title
        self.title_label = Label(
            screen_width // 2,
            50,
            "CursorDraw",
            font_size=Config.FONT_LARGE,
            centered=True
        )
        
        # Subtitle
        self.subtitle_label = Label(
            screen_width // 2,
            100,
            "Improve your cursor control through drawing games",
            font_size=Config.FONT_MEDIUM,
            centered=True
        )
        
        # Create game grid
        self.game_grid = GridLayout(
            (screen_width - (Config.BUTTON_WIDTH * 3 + 20 * 2)) // 2,
            150,
            Config.BUTTON_WIDTH,
            Config.BUTTON_HEIGHT,
            3,  # 3 columns
            20,  # horizontal spacing
            20   # vertical spacing
        )
        
        # Add implemented games
        for game_name in Config.IMPLEMENTED_GAMES:
            button = Button(
                0, 0,  # Will be positioned by grid
                Config.BUTTON_WIDTH,
                Config.BUTTON_HEIGHT,
                game_name,
                lambda name=game_name: self._start_game(name),
                bg_color=Config.GREEN
            )
            self.game_grid.add_item(button)
            
        # Add coming soon games
        for game_name in Config.COMING_SOON_GAMES:
            button = Button(
                0, 0,  # Will be positioned by grid
                Config.BUTTON_WIDTH,
                Config.BUTTON_HEIGHT,
                game_name,
                lambda name=game_name: self._show_coming_soon(name),
                bg_color=Config.GRAY,
                disabled=True
            )
            self.game_grid.add_item(button)
            
        # Settings button
        self.settings_button = Button(
            screen_width - Config.BUTTON_WIDTH - 20,
            screen_height - Config.BUTTON_HEIGHT - 20,
            Config.BUTTON_WIDTH,
            Config.BUTTON_HEIGHT,
            "Settings",
            self._show_settings
        )
            
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEMOTION:
            self.update(event.pos)
            
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
        # Clear screen
        self.screen.fill(Config.WHITE)
        
        # Draw title and subtitle
        self.title_label.draw(self.screen)
        self.subtitle_label.draw(self.screen)
        
        # Draw game grid
        self.game_grid.draw(self.screen)
        
        # Draw settings button
        self.settings_button.draw(self.screen)
        
    def _start_game(self, game_name):
        """Start the selected game"""
        self.game_state.set_current_game(game_name)
        
        if game_name == "Whiteboard Playground":
            self.next_screen = WhiteboardPlayground(self.screen, self.game_state)
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