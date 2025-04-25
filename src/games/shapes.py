import pygame
import math
from typing import List, Tuple, Dict, Any, Optional
from src.config import Config
from src.core.whiteboard import Whiteboard
from src.core.ui_manager import Button, Label, Dialog
from src.utils.path_detection import PathDetection
from src.utils.accuracy import AccuracyTracker

class DrawBasicShapes:
    """
    Draw Basic Shapes - A game where users trace over shapes to improve cursor control.
    """
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        self.next_screen = None
        self.active_dialog = None
        
        # Set up shape tracing state
        self.shapes_data = [
            {"name": "Circle", "type": "circle", "difficulty": 1},
            {"name": "Square", "type": "square", "difficulty": 1},
            {"name": "Triangle", "type": "triangle", "difficulty": 1},
            {"name": "Rectangle", "type": "rectangle", "difficulty": 2},
            {"name": "Diamond", "type": "diamond", "difficulty": 2},
            # More shapes can be added here with increasing difficulty
        ]
        
        self.current_shape_index = 0
        self.current_shape_points = []
        self.drawn_points = []
        self.accuracy_tracker = AccuracyTracker()
        self.is_tracing = False
        self.shape_completed = False
        self.auto_progress_timer = None  # Timer for automatic progression
        
        # Set up UI elements
        self._setup_ui()
        
        # Generate the first shape
        self._generate_current_shape()
        
    def _setup_ui(self):
        """Set up UI elements for the shape tracing game"""
        screen_width, screen_height = self.screen.get_size()
        
        # Get scaled dimensions
        scaled_font_sizes = Config.get_scaled_font_sizes()
        scaled_button_width, scaled_button_height = Config.get_scaled_button_dimensions()
        
        # Calculate whiteboard position and size - leave more space for accuracy panel
        accuracy_panel_width = Config.scale_width(220)  # Increase width for panel
        whiteboard_margin_top = Config.scale_height(80)  # Increased for better header spacing
        whiteboard_margin_bottom = Config.scale_height(80)  # Increased for button spacing
        whiteboard_width = screen_width - Config.scale_width(40) - accuracy_panel_width
        whiteboard_height = screen_height - whiteboard_margin_top - whiteboard_margin_bottom
        whiteboard_x = Config.scale_width(20)
        whiteboard_y = whiteboard_margin_top
        
        # Create whiteboard
        self.whiteboard = Whiteboard(
            self.screen,
            (whiteboard_x, whiteboard_y),
            (whiteboard_width, whiteboard_height),
            self.game_state,
            show_controls=False  # Hide controls for cleaner tracing experience
        )
        
        # Title
        self.title_label = Label(
            screen_width // 2,
            Config.scale_height(25),
            "Draw Basic Shapes",
            font_size=scaled_font_sizes['large'],
            centered=True
        )
        
        # Header bar
        self.header_rect = pygame.Rect(0, 0, screen_width, Config.scale_height(60))
        
        # Shape name label - position above the whiteboard
        self.shape_label = Label(
            whiteboard_x + whiteboard_width // 2,
            whiteboard_y - Config.scale_height(25),
            "Circle",  # Will be updated in _generate_current_shape
            font_size=scaled_font_sizes['medium'],
            centered=True
        )
        
        # Instruction label - position below the whiteboard with proper spacing
        self.instruction_label = Label(
            whiteboard_x + whiteboard_width // 2,
            whiteboard_y + whiteboard_height + Config.scale_height(10),
            "Trace the shape as accurately as you can",
            font_size=scaled_font_sizes['small'],
            centered=True
        )
        
        # Calculate button positions with proper spacing to avoid overlap
        # Use a more professional layout with even margins
        button_margin = Config.scale_width(20)
        button_width = scaled_button_width * 0.85  # Slightly smaller buttons to fit 4 of them
        button_spacing = (whiteboard_width - 4 * button_width - 2 * button_margin) / 3
        button_y = screen_height - Config.scale_height(45)  # Move up slightly
        
        # Back to Menu button - leftmost
        self.menu_button = Button(
            whiteboard_x + button_margin,
            button_y,
            button_width,
            scaled_button_height,
            "Back to Menu",
            self._back_to_menu_with_check,
            bg_color=Config.BLUE,
            hover_color=(100, 150, 255),
            text_color=Config.WHITE,
            rounded=True,
            font_size=scaled_font_sizes['small']
        )
        
        # Clear button - second from left
        clear_x = whiteboard_x + button_margin + button_width + button_spacing
        self.clear_button = Button(
            clear_x,
            button_y,
            button_width,
            scaled_button_height,
            "Clear",
            self._clear_drawing,
            bg_color=Config.LIGHT_GRAY,
            hover_color=Config.GRAY,
            text_color=Config.BLACK,
            rounded=True,
            font_size=scaled_font_sizes['small']
        )
        
        # Random Shape button - third from left
        random_x = clear_x + button_width + button_spacing
        self.random_shape_button = Button(
            random_x,
            button_y,
            button_width,
            scaled_button_height,
            "Random Shape",
            self._random_shape,
            bg_color=(50, 180, 150),  # Teal color
            hover_color=(80, 210, 180),
            text_color=Config.WHITE,
            rounded=True,
            font_size=scaled_font_sizes['small']
        )
        
        # Next Shape button - rightmost (initially disabled)
        next_x = random_x + button_width + button_spacing
        self.next_shape_button = Button(
            next_x,
            button_y,
            button_width,
            scaled_button_height,
            "Next Shape",
            self._next_shape,
            bg_color=Config.GREEN,
            hover_color=(100, 200, 100),
            text_color=Config.WHITE,
            rounded=True,
            font_size=scaled_font_sizes['small'],
            disabled=True
        )
        
        # Calculate accuracy panel position (right side of whiteboard)
        self.accuracy_panel_pos = (
            whiteboard_x + whiteboard_width + Config.scale_width(20),
            whiteboard_y
        )
        self.accuracy_panel_size = (
            accuracy_panel_width,
            Config.scale_height(320)  # Slightly taller for more information
        )
        
    def _generate_current_shape(self):
        """Generate the current shape based on the index"""
        if self.current_shape_index >= len(self.shapes_data):
            # Loop back to first shape if we've gone through all shapes
            self.current_shape_index = 0
        
        # Get current shape data
        shape_data = self.shapes_data[self.current_shape_index]
        
        # Clear the whiteboard first to ensure old drawings and shapes are gone
        self.whiteboard.drawing_engine.clear_canvas()
        
        # Get whiteboard dimensions
        wb_width, wb_height = self.whiteboard.size
        
        # Calculate an appropriate size for the shape (based on whiteboard)
        base_size = min(wb_width, wb_height) // 3
        
        # Adjust size based on difficulty
        size = base_size // shape_data["difficulty"]
        
        # Generate shape points
        self.current_shape_points = PathDetection.generate_shape_path(
            shape_data["type"],
            (wb_width // 2, wb_height // 2),  # Center of whiteboard
            size
        )
        
        # Update shape label
        self.shape_label.text = shape_data["name"]
        
        # Reset tracing state
        self.drawn_points = []
        self.accuracy_tracker.reset()
        self.is_tracing = False
        self.shape_completed = False
        self.next_shape_button.disabled = True
        self.auto_progress_timer = None
        
        # Draw the shape outline
        PathDetection.draw_shape_outline(
            self.whiteboard.drawing_engine.surface,
            self.current_shape_points,
            Config.BLUE,
            width=4,
            alpha=100
        )
        
        # Update the accuracy tracker with the current shape name
        self.accuracy_tracker.set_current_shape(shape_data["name"])
        
    def _back_to_menu_with_check(self):
        """Return to main menu with confirmation if needed"""
        # Only show confirmation if user has started tracing
        if len(self.drawn_points) > 0 and not self.shape_completed:
            def confirm_exit():
                self.active_dialog = None
                from src.screens.main_menu import MainMenu
                self.next_screen = MainMenu(self.screen, self.game_state)
                
            def cancel_exit():
                self.active_dialog = None
                
            self.active_dialog = Dialog(
                self.screen,
                "You haven't completed this shape yet.\nAre you sure you want to exit?",
                confirm_exit,
                cancel_exit,
                title="Return to Menu",
                confirm_text="Yes",
                cancel_text="No"
            )
        else:
            from src.screens.main_menu import MainMenu
            self.next_screen = MainMenu(self.screen, self.game_state)
    
    def _clear_drawing(self):
        """Clear the current drawing but keep the shape outline"""
        # First create a new blank surface by filling with white
        self.whiteboard.drawing_engine.clear_canvas()
        
        # Reset drawn points and tracing state
        self.drawn_points = []
        self.is_tracing = False
        self.accuracy_tracker.reset()
        self.next_shape_button.disabled = not self.shape_completed
        
        # Redraw the shape outline
        PathDetection.draw_shape_outline(
            self.whiteboard.drawing_engine.surface,
            self.current_shape_points,
            Config.BLUE,
            width=4,
            alpha=100
        )
        
        # Set the current shape name in the accuracy tracker
        self.accuracy_tracker.set_current_shape(self.shapes_data[self.current_shape_index]["name"])
        
        # Add this clear action to the drawing history
        self.whiteboard.drawing_engine._add_to_history()
    
    def _next_shape(self):
        """Proceed to the next shape"""
        if self.shape_completed:
            self.current_shape_index += 1
            # Clear whiteboard and regenerate shape
            self._generate_current_shape()
            
    def _random_shape(self):
        """Switch to a random shape"""
        import random
        
        # Get a random shape index different from current
        if len(self.shapes_data) > 1:
            new_index = self.current_shape_index
            while new_index == self.current_shape_index:
                new_index = random.randint(0, len(self.shapes_data) - 1)
            self.current_shape_index = new_index
        else:
            # If only one shape, just restart it
            pass
            
        # Generate the new shape with a clear whiteboard
        self._generate_current_shape()
    
    def _evaluate_tracing(self, is_final=False):
        """
        Evaluate the tracing accuracy and update metrics
        
        Args:
            is_final: Whether this is the final evaluation after drawing is complete
        """
        if len(self.drawn_points) < 5:
            # Not enough data to evaluate
            return
        
        # Calculate accuracy
        metrics = PathDetection.calculate_tracing_accuracy(
            self.drawn_points,
            self.current_shape_points,
            tolerance=15  # Pixel tolerance for "on path"
        )
        
        # Update accuracy tracker
        self.accuracy_tracker.update_metrics(metrics)
        
        # For final evaluation (when drawing is complete)
        if is_final:
            # Enable next shape button if completed
            if self.accuracy_tracker.is_completed() and not self.shape_completed:
                self.shape_completed = True
                self.next_shape_button.disabled = False
                
                # Show completion dialog
                def close_dialog():
                    self.active_dialog = None
                    # Set timer for auto-progression (3 seconds)
                    self.auto_progress_timer = pygame.time.get_ticks() + 3000
                    
                self.active_dialog = Dialog(
                    self.screen,
                    f"Great job! You completed the {self.shapes_data[self.current_shape_index]['name']}.\n" +
                    f"Accuracy: {metrics['percentage']:.1f}%\n" +
                    "Moving to next shape in 3 seconds...",
                    close_dialog,
                    None,
                    title="Shape Completed!",
                    confirm_text="OK"
                )
            
    # Modify the real-time accuracy evaluation to reduce frequency
    point_count = 0
    last_evaluation_time = 0
    
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
            self._generate_current_shape()  # Regenerate shape with new dimensions
            return
        
        # Handle button events
        if event.type == pygame.MOUSEMOTION:
            self.menu_button.update(event.pos)
            self.clear_button.update(event.pos)
            self.next_shape_button.update(event.pos)
            self.random_shape_button.update(event.pos)
            
        self.menu_button.handle_event(event)
        self.clear_button.handle_event(event)
        self.next_shape_button.handle_event(event)
        self.random_shape_button.handle_event(event)
        
        # Handle drawing events
        canvas_rect = pygame.Rect(
            self.whiteboard.pos[0], 
            self.whiteboard.pos[1], 
            self.whiteboard.size[0], 
            self.whiteboard.size[1]
        )
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if canvas_rect.collidepoint(event.pos):
                # Convert screen coordinates to canvas coordinates
                canvas_pos = (
                    event.pos[0] - self.whiteboard.pos[0], 
                    event.pos[1] - self.whiteboard.pos[1]
                )
                self.whiteboard.drawing_engine.start_drawing(canvas_pos)
                self.is_tracing = True
                self.drawn_points = [canvas_pos]  # Start tracking points
                self.point_count = 1
                self.last_evaluation_time = pygame.time.get_ticks()
                
        elif event.type == pygame.MOUSEMOTION:
            if self.whiteboard.drawing_engine.is_drawing and canvas_rect.collidepoint(event.pos):
                # Convert screen coordinates to canvas coordinates
                canvas_pos = (
                    event.pos[0] - self.whiteboard.pos[0], 
                    event.pos[1] - self.whiteboard.pos[1]
                )
                self.whiteboard.drawing_engine.draw_to(canvas_pos)
                self.drawn_points.append(canvas_pos)  # Track point for accuracy
                self.point_count += 1
                
                # Only update accuracy every 10 points or after 100ms to reduce performance impact
                current_time = pygame.time.get_ticks()
                if (self.point_count >= 10 or (current_time - self.last_evaluation_time) > 100):
                    self._evaluate_tracing(is_final=False)
                    self.point_count = 0
                    self.last_evaluation_time = current_time
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left release
            if self.whiteboard.drawing_engine.is_drawing:
                self.whiteboard.drawing_engine.stop_drawing()
                self.is_tracing = False
                
                # Evaluate the tracing if we have drawn points
                if len(self.drawn_points) > 0:
                    self._evaluate_tracing(is_final=True)
        
    def update(self, mouse_pos=None):
        """Update game state"""
        # Update UI buttons
        if mouse_pos:
            self.menu_button.update(mouse_pos)
            self.clear_button.update(mouse_pos)
            self.next_shape_button.update(mouse_pos)
            self.random_shape_button.update(mouse_pos)
            
        # Update dialog if active
        if self.active_dialog and mouse_pos:
            self.active_dialog.update(mouse_pos)
            
        # Check for auto-progression timer
        if self.auto_progress_timer and pygame.time.get_ticks() > self.auto_progress_timer:
            self.auto_progress_timer = None
            self._next_shape()  # Automatically progress to next shape
            
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
        
        # Draw shape label
        self.shape_label.draw(self.screen)
        
        # Draw instruction label
        self.instruction_label.draw(self.screen)
        
        # Draw whiteboard
        self.whiteboard.render()
        
        # We no longer need to draw the shape outline here as it's drawn
        # directly on the whiteboard surface when generated or cleared
        
        # Draw accuracy panel
        self.accuracy_tracker.draw_accuracy_panel(
            self.screen,
            self.accuracy_panel_pos,
            self.accuracy_panel_size,
            show_details=True
        )
        
        # Draw buttons
        self.menu_button.draw(self.screen)
        self.clear_button.draw(self.screen)
        self.random_shape_button.draw(self.screen)
        self.next_shape_button.draw(self.screen)
        
        # Draw dialog if active
        if self.active_dialog:
            self.active_dialog.draw() 