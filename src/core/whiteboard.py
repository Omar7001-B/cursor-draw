import pygame
import os
import datetime
from src.config import Config
from src.core.drawing_engine import DrawingEngine
from src.core.ui_manager import Button, Label, Dialog

class Whiteboard:
    """
    Reusable whiteboard component that combines a DrawingEngine with UI controls
    for brush size, color, eraser, etc.
    """
    def __init__(self, screen, pos, size, game_state=None, show_controls=True):
        self.screen = screen
        self.pos = pos
        self.size = size
        self.game_state = game_state
        self.show_controls = show_controls
        
        # Set up drawing surface and engine
        self.drawing_engine = DrawingEngine(size[0], size[1])
        
        # Create UI elements if controls are shown
        self.ui_elements = []
        self.active_dialog = None
        self.eraser_button = None  # Track eraser button separately
        
        if show_controls:
            self._setup_ui()
        
    def _setup_ui(self):
        """Set up UI elements for the whiteboard"""
        x, y = self.pos
        width, height = self.size
        
        # Get scaled dimensions
        scaled_font_sizes = Config.get_scaled_font_sizes()
        
        # UI Control panel at the top
        ui_height = Config.scale_height(50)
        ui_width = width
        ui_x = x
        ui_y = y - ui_height
        
        # Calculate button positions
        button_width = Config.scale_width(100)
        button_height = Config.scale_height(40)
        spacing = Config.scale_width(10)
        
        # Color selection buttons
        color_names = ["Black", "Red", "Blue"]
        colors = [Config.BLACK, Config.RED, Config.BLUE]
        color_x = ui_x + spacing
        
        for i, (color_name, color) in enumerate(zip(color_names, colors)):
            button = Button(
                color_x + (button_width + spacing) * i,
                ui_y + Config.scale_height(5),
                button_width,
                button_height,
                color_name,
                lambda idx=i: self.set_color(idx),
                bg_color=color,
                text_color=Config.WHITE if color == Config.BLACK else Config.BLACK,
                font_size=scaled_font_sizes['small']
            )
            self.ui_elements.append(button)
            
        # Brush size buttons
        size_labels = ["Small", "Medium", "Large"]
        size_x = color_x + (button_width + spacing) * 3 + spacing
        
        for i, label in enumerate(size_labels):
            button = Button(
                size_x + (button_width + spacing) * i,
                ui_y + Config.scale_height(5),
                button_width,
                button_height,
                label,
                lambda idx=i: self.set_brush_size(idx),
                font_size=scaled_font_sizes['small']
            )
            self.ui_elements.append(button)
            
        # Action buttons (Eraser, Clear, Save)
        action_x = size_x + (button_width + spacing) * 3 + spacing
        
        # Eraser button - store reference to update its visual state
        self.eraser_button = Button(
            action_x,
            ui_y + Config.scale_height(5),
            button_width,
            button_height,
            "Eraser",
            self.toggle_eraser,
            bg_color=Config.LIGHT_GRAY,
            hover_color=Config.GRAY,
            font_size=scaled_font_sizes['small']
        )
        self.ui_elements.append(self.eraser_button)
        
        # Clear button
        clear_button = Button(
            action_x + button_width + spacing,
            ui_y + Config.scale_height(5),
            button_width,
            button_height,
            "Clear",
            self.clear_canvas,
            font_size=scaled_font_sizes['small']
        )
        self.ui_elements.append(clear_button)
        
        # Save button
        save_button = Button(
            action_x + (button_width + spacing) * 2,
            ui_y + Config.scale_height(5),
            button_width,
            button_height,
            "Save",
            self.save_canvas,
            font_size=scaled_font_sizes['small']
        )
        self.ui_elements.append(save_button)
            
    def handle_event(self, event):
        """Handle pygame events"""
        # Check for resize events
        if event.type == pygame.VIDEORESIZE:
            self._resize()
            return True
            
        # Handle UI events if controls are shown
        if self.show_controls:
            # First handle any active dialogs
            if self.active_dialog:
                if self.active_dialog.handle_event(event):
                    return True
                
            # Then handle normal UI events
            for element in self.ui_elements:
                if element.handle_event(event):
                    return True
        
        # Handle drawing events
        canvas_rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if canvas_rect.collidepoint(event.pos):
                # Convert screen coordinates to canvas coordinates
                canvas_pos = (event.pos[0] - self.pos[0], event.pos[1] - self.pos[1])
                self.drawing_engine.start_drawing(canvas_pos)
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            if self.drawing_engine.is_drawing and canvas_rect.collidepoint(event.pos):
                # Convert screen coordinates to canvas coordinates
                canvas_pos = (event.pos[0] - self.pos[0], event.pos[1] - self.pos[1])
                self.drawing_engine.draw_to(canvas_pos)
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left release
            if self.drawing_engine.is_drawing:
                self.drawing_engine.stop_drawing()
                return True
                
        return False
        
    def update(self, mouse_pos=None):
        """Update the whiteboard state"""
        if self.show_controls and mouse_pos:
            # Update UI elements
            for element in self.ui_elements:
                if hasattr(element, 'update'):
                    element.update(mouse_pos)
                    
            # Update dialog if active
            if self.active_dialog:
                self.active_dialog.update(mouse_pos)
        
        return None  # Whiteboard doesn't return a next screen
        
    def render(self):
        """Render the whiteboard and its UI"""
        # Draw the canvas border
        pygame.draw.rect(self.screen, Config.BLACK, 
                         (self.pos[0]-2, self.pos[1]-2, self.size[0]+4, self.size[1]+4), 2)
        
        # Draw the canvas (drawing surface)
        self.screen.blit(self.drawing_engine.surface, self.pos)
        
        # Draw UI elements if controls are shown
        if self.show_controls:
            for element in self.ui_elements:
                if hasattr(element, 'draw'):
                    element.draw(self.screen)
                    
            # Draw dialog if active
            if self.active_dialog:
                self.active_dialog.draw()
                
    def set_color(self, color_index):
        """Set the current brush color"""
        self.drawing_engine.set_brush_color(color_index)
        # Turn off eraser mode when selecting a color
        if self.eraser_button and self.drawing_engine.eraser_mode:
            self.drawing_engine.eraser_mode = False
            self.eraser_button.bg_color = Config.LIGHT_GRAY
        
    def set_brush_size(self, size_index):
        """Set the current brush size"""
        self.drawing_engine.set_brush_size(size_index)
        
    def toggle_eraser(self):
        """Toggle eraser mode"""
        self.drawing_engine.toggle_eraser()
        
        # Update eraser button appearance based on mode
        if self.eraser_button:
            if self.drawing_engine.eraser_mode:
                # Eraser is active
                self.eraser_button.bg_color = Config.GRAY
                self.eraser_button.hover_color = Config.DARK_GRAY
            else:
                # Eraser is inactive
                self.eraser_button.bg_color = Config.LIGHT_GRAY
                self.eraser_button.hover_color = Config.GRAY
        
    def clear_canvas(self):
        """Clear the canvas with confirmation dialog"""
        if self.drawing_engine.surface.get_at((0, 0)) == self.drawing_engine.surface.get_at((self.size[0]-1, self.size[1]-1)) == self.drawing_engine.bg_color:
            # Canvas is already clear, no need for dialog
            return
            
        def confirm_clear():
            # Clear animation
            for _ in self.drawing_engine.clear_canvas(animated=True):
                pass  # We could render the animation frames here if needed
            self.active_dialog = None
            
        def cancel_clear():
            self.active_dialog = None
            
        self.active_dialog = Dialog(
            self.screen,
            "You will lose your current drawing.\nDo you want to continue?",
            confirm_clear,
            cancel_clear,
            title="Clear Canvas",
            confirm_text="Clear",
            cancel_text="Cancel"
        )
        
    def save_canvas(self):
        """Save the canvas as an image"""
        # Create data directory if it doesn't exist
        os.makedirs(Config.SAVE_DIRECTORY, exist_ok=True)
        
        # Generate a filename based on current date/time
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(Config.SAVE_DIRECTORY, f"drawing_{timestamp}.png")
        
        # Save the image
        self.drawing_engine.save_image(filename)
        
        # Show confirmation dialog
        def close_dialog():
            self.active_dialog = None
            
        self.active_dialog = Dialog(
            self.screen,
            f"Your drawing was saved successfully as:\n{filename}",
            close_dialog,
            None,
            title="Save Successful",
            confirm_text="OK"
        )
        
    def has_content(self):
        """Check if the canvas has any content drawn on it"""
        # Simple heuristic: check if not all pixels are background color
        # This is a simplification; a more robust check would compare the
        # current surface with a blank one
        for x in range(0, self.size[0], 10):  # Sample every 10 pixels
            for y in range(0, self.size[1], 10):
                if self.drawing_engine.surface.get_at((x, y)) != self.drawing_engine.bg_color:
                    return True
        return False
    
    def _resize(self):
        """Handle window resize by recreating the UI elements"""
        # Clear existing UI elements
        self.ui_elements = []
        
        # Recreate UI if controls are shown
        if self.show_controls:
            self._setup_ui() 