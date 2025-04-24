import pygame
from src.config import Config
from src.core.whiteboard import Whiteboard
from src.core.ui_manager import Button, Label, Dialog

class WhiteboardPlayground:
    """
    Whiteboard Playground - A free-drawing mode that establishes 
    core whiteboard functionality.
    """
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        self.next_screen = None
        self.active_dialog = None
        
        # Set up UI elements
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up UI elements for the whiteboard playground"""
        screen_width, screen_height = self.screen.get_size()
        
        # Calculate whiteboard position and size
        # Leave margin at top for UI controls and at bottom for menu button
        whiteboard_margin_top = 60
        whiteboard_margin_bottom = 70
        whiteboard_width = screen_width - 40
        whiteboard_height = screen_height - whiteboard_margin_top - whiteboard_margin_bottom
        whiteboard_x = 20
        whiteboard_y = whiteboard_margin_top
        
        # Create whiteboard
        self.whiteboard = Whiteboard(
            self.screen,
            (whiteboard_x, whiteboard_y),
            (whiteboard_width, whiteboard_height),
            self.game_state
        )
        
        # Title
        self.title_label = Label(
            screen_width // 2,
            20,
            "Whiteboard Playground",
            font_size=Config.FONT_MEDIUM,
            centered=True
        )
        
        # Back to Menu button
        self.menu_button = Button(
            20,
            screen_height - 60,
            Config.BUTTON_WIDTH,
            Config.BUTTON_HEIGHT,
            "Back to Menu",
            self._back_to_menu_with_check
        )
            
    def handle_event(self, event):
        """Handle pygame events"""
        # Handle dialog events first if active
        if self.active_dialog:
            if self.active_dialog.handle_event(event):
                return
        
        # Pass events to whiteboard
        if self.whiteboard.handle_event(event):
            return
            
        # Handle menu button events
        if event.type == pygame.MOUSEMOTION:
            self.menu_button.update(event.pos)
            
        self.menu_button.handle_event(event)
        
    def update(self, mouse_pos=None):
        """Update game state"""
        # Update whiteboard
        self.whiteboard.update(mouse_pos)
        
        # Update menu button
        if mouse_pos:
            self.menu_button.update(mouse_pos)
            
        # Update dialog if active
        if self.active_dialog and mouse_pos:
            self.active_dialog.update(mouse_pos)
            
        # Return next screen if set
        if self.next_screen:
            next_screen = self.next_screen
            self.next_screen = None
            return next_screen
            
        return None
        
    def render(self):
        """Render the game"""
        # Clear screen
        self.screen.fill(Config.LIGHT_GRAY)
        
        # Draw title
        self.title_label.draw(self.screen)
        
        # Draw whiteboard
        self.whiteboard.render()
        
        # Draw menu button
        self.menu_button.draw(self.screen)
        
        # Draw dialog if active
        if self.active_dialog:
            self.active_dialog.draw()
        
    def _back_to_menu_with_check(self):
        """Check if whiteboard has content before going back to menu"""
        if self.whiteboard.has_content():
            # Show confirmation dialog
            def confirm_exit():
                self._go_back_to_menu()
                self.active_dialog = None
                
            def cancel_exit():
                self.active_dialog = None
                
            self.active_dialog = Dialog(
                self.screen,
                "You have unsaved work.\nAre you sure you want to exit?",
                confirm_exit,
                cancel_exit
            )
        else:
            # No content, go back directly
            self._go_back_to_menu()
            
    def _go_back_to_menu(self):
        """Go back to the main menu"""
        from src.screens.main_menu import MainMenu
        self.next_screen = MainMenu(self.screen, self.game_state) 