import pygame
from src.config import Config
from src.core.whiteboard import Whiteboard
from src.core.ui_manager import Button, Label, Dialog
from src.core.game_state import GameState

class WhiteboardPlayground(GameState):
    """
    Whiteboard Playground - A free-drawing mode that establishes 
    core whiteboard functionality.
    """
    def __init__(self, screen, game_manager):
        super().__init__(screen, game_manager)
        self.screen = screen
        self.game_manager = game_manager
        self.next_screen_name = None
        self.active_dialog = None
        
        # Set up UI elements
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up UI elements for the whiteboard playground"""
        screen_width, screen_height = self.screen.get_size()
        
        # Get scaled dimensions
        scaled_font_sizes = Config.get_scaled_font_sizes()
        scaled_button_width, scaled_button_height = Config.get_scaled_button_dimensions()
        
        # Calculate whiteboard position and size
        # Leave margin at top for UI controls and at bottom for menu button
        whiteboard_margin_top = Config.scale_height(70)  # Increased for better header spacing
        whiteboard_margin_bottom = Config.scale_height(70)
        whiteboard_width = screen_width - Config.scale_width(40)
        whiteboard_height = screen_height - whiteboard_margin_top - whiteboard_margin_bottom
        whiteboard_x = Config.scale_width(20)
        whiteboard_y = whiteboard_margin_top
        
        # Create whiteboard
        self.whiteboard = Whiteboard(
            self.screen,
            (whiteboard_x, whiteboard_y),
            (whiteboard_width, whiteboard_height),
            self.game_manager
        )
        
        # Title
        self.title_label = Label(
            screen_width // 2,
            Config.scale_height(25),
            "Whiteboard Playground",
            font_size=scaled_font_sizes['large'],
            centered=True
        )
        
        # Header bar
        self.header_rect = pygame.Rect(0, 0, screen_width, Config.scale_height(50))
        
        # Button spacing
        button_spacing = Config.scale_width(20)

        # Clear button - add a direct clear button
        self.clear_button = Button(
            Config.scale_width(75),
            Config.scale_height(10),
            Config.scale_width(60),
            Config.scale_height(30),
            "Clear",
            self.whiteboard.clear_canvas,
            font_size=scaled_font_sizes['small']
        )
        
        # Back to Menu button - more professional with rounded corners
        self.menu_button = Button(
            Config.scale_width(20),
            screen_height - Config.scale_height(60),
            scaled_button_width,
            scaled_button_height,
            "Back to Menu",
            self._back_to_menu_with_check,
            bg_color=Config.BLUE,
            hover_color=(100, 150, 255),
            text_color=Config.WHITE,
            rounded=True,
            font_size=scaled_font_sizes['small']
        )
    
    def handle_event(self, event):
        """Handle pygame events"""
        # Handle dialog events first if active
        if self.active_dialog:
            if self.active_dialog.handle_event(event):
                return True
        
        # Handle resize event
        if event.type == pygame.VIDEORESIZE:
            # Recreate UI elements when window is resized
            self._setup_ui()
            return True
        
        # Pass events to whiteboard
        if self.whiteboard.handle_event(event):
            return True
            
        # Handle button events
        if event.type == pygame.MOUSEMOTION:
            self.menu_button.update(event.pos)
            self.clear_button.update(event.pos)
            
        if self.menu_button.handle_event(event):
            return True
        if self.clear_button.handle_event(event):
            return True
        
        return False
        
    def update(self, dt):
        """Update game state"""
        mouse_pos = pygame.mouse.get_pos()
        self.whiteboard.update(dt)
        
        # Update buttons
        if mouse_pos:
            self.menu_button.update(mouse_pos)
            self.clear_button.update(mouse_pos)
            
        # Update dialog if active
        if self.active_dialog and mouse_pos:
            self.active_dialog.update(mouse_pos)
            
        # Return next screen name if set
        if self.next_screen_name:
            next_name = self.next_screen_name
            self.next_screen_name = None
            return next_name
            
        return None
        
    def draw(self):
        """Render the game"""
        self.screen.fill(Config.LIGHT_GRAY)
        
        # Draw header bar
        pygame.draw.rect(self.screen, Config.BLUE, self.header_rect)
        
        # Draw title
        title_color_original = self.title_label.color
        self.title_label.color = Config.WHITE
        self.title_label.draw(self.screen)
        self.title_label.color = title_color_original
        
        # Draw whiteboard using its render method
        self.whiteboard.render()
        
        # Draw buttons
        self.menu_button.draw(self.screen)
        self.clear_button.draw(self.screen)
        
        # Draw dialog if active
        if self.active_dialog:
            self.active_dialog.draw()
        
    def _back_to_menu_with_check(self):
        """Check if whiteboard has content before going back to menu"""
        if self.whiteboard.has_content():
            # Show confirmation dialog
            def confirm_exit():
                self.active_dialog = None
                self.next_screen_name = 'main_menu'
                
            def cancel_exit():
                self.active_dialog = None
                
            self.active_dialog = Dialog(
                self.screen,
                "You have unsaved work.\nAre you sure you want to exit?",
                confirm_exit,
                cancel_exit,
                title="Return to Menu",
                confirm_text="Exit",
                cancel_text="Cancel"
            )
        else:
            self.next_screen_name = 'main_menu'
            
    def _go_back_to_menu(self):
        """Go back to the main menu"""
        self.next_screen_name = 'main_menu'

    def handle_resize(self):
        screen_width, screen_height = self.screen.get_size()
        self.whiteboard.resize(0, Config.scale_height(80), screen_width, screen_height - Config.scale_height(80))
        self._setup_ui()
        
    # Remove this method as it's handled by returning state name from update
    # def _go_to_menu(self):
    #     self.game_manager.change_state('main_menu') 