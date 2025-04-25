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
            self.game_state
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
            Config.scale_width(20) + scaled_button_width + button_spacing,
            screen_height - Config.scale_height(60),
            scaled_button_width,
            scaled_button_height,
            "Clear",
            self._clear_drawing,
            bg_color=Config.LIGHT_GRAY,
            hover_color=Config.GRAY,
            text_color=Config.BLACK,
            rounded=True,
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
    
    def _clear_drawing(self):
        """Clear the canvas immediately without confirmation dialog"""
        # Get the current whiteboard size
        wb_width, wb_height = self.whiteboard.size
        
        # Create a completely new white surface
        self.whiteboard.drawing_engine.surface = pygame.Surface((wb_width, wb_height))
        self.whiteboard.drawing_engine.surface.fill(Config.WHITE)
        
        # Reset strokes list in drawing engine
        self.whiteboard.drawing_engine.strokes = []
        
        # Add this clear action to the drawing history
        self.whiteboard.drawing_engine._add_to_history()
            
    def handle_event(self, event):
        """Handle pygame events"""
        # Handle dialog events first if active
        if self.active_dialog:
            if self.active_dialog.handle_event(event):
                return
        
        # Handle resize event
        if event.type == pygame.VIDEORESIZE:
            # Recreate UI elements when window is resized
            self._setup_ui()
            return
        
        # Pass events to whiteboard
        if self.whiteboard.handle_event(event):
            return
            
        # Handle button events
        if event.type == pygame.MOUSEMOTION:
            self.menu_button.update(event.pos)
            self.clear_button.update(event.pos)
            
        self.menu_button.handle_event(event)
        self.clear_button.handle_event(event)
        
    def update(self, mouse_pos=None):
        """Update game state"""
        # Update whiteboard
        self.whiteboard.update(mouse_pos)
        
        # Update buttons
        if mouse_pos:
            self.menu_button.update(mouse_pos)
            self.clear_button.update(mouse_pos)
            
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
        
        # Draw header bar
        pygame.draw.rect(self.screen, Config.BLUE, self.header_rect)
        
        # Draw title
        title_color_original = self.title_label.color
        self.title_label.color = Config.WHITE
        self.title_label.draw(self.screen)
        self.title_label.color = title_color_original
        
        # Draw whiteboard
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
                self._go_back_to_menu()
                self.active_dialog = None
                
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
            # No content, go back directly
            self._go_back_to_menu()
            
    def _go_back_to_menu(self):
        """Go back to the main menu"""
        from src.screens.main_menu import MainMenu
        self.next_screen = MainMenu(self.screen, self.game_state) 