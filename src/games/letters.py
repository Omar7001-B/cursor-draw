import pygame
import math
import random
from typing import List, Tuple, Dict, Any, Optional
from src.config import Config
from src.core.whiteboard import Whiteboard
from src.core.ui_manager import Button, Label, Dialog
from src.utils.path_detection import PathDetection
from src.utils.accuracy import AccuracyTracker
from src.utils.letter_path_generator import LetterPathGenerator
from src.core.game_state import GameState

class TraceTheLetter(GameState):
    """
    Trace the Letter - A game where users trace over letter guides to improve precision.
    """
    def __init__(self, screen, game_manager):
        super().__init__(screen, game_manager)
        self.screen = screen
        self.game_manager = game_manager
        self.next_screen_name = None
        self.active_dialog = None
        self.request_menu_exit = False
        
        # Difficulty settings - tolerance for accuracy (higher = easier)
        self.difficulty_settings = {
            "Easy": 20,       # 20px tolerance - most forgiving
            "Medium": 15,     # 15px tolerance - balanced
            "Hard": 10        # 10px tolerance - most challenging
        }
        self.current_difficulty = "Medium"  # Default to medium difficulty
        
        # Set up letter tracing state
        self.letters_data = self._generate_letters_data()
        self.current_letter_index = 0
        self.current_letter_points = []
        self.drawn_points = []
        self.accuracy_tracker = AccuracyTracker()
        self.is_tracing = False
        self.letter_completed = False
        self.auto_progress_timer = None  # Timer for automatic progression
        
        # Set up UI elements
        self._setup_ui()
        
        # Generate the first letter
        self._generate_current_letter()
    
    def _generate_letters_data(self):
        """Generate data for uppercase letters A-Z"""
        letters = []
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        for i, letter in enumerate(alphabet):
            # Customize difficulty: A-H easy, I-P medium, Q-Z hard
            difficulty = 1 if i < 8 else (2 if i < 16 else 3)
            letters.append({
                "name": f"Letter {letter}",
                "letter": letter,
                "difficulty": difficulty
            })
        return letters
        
    def _setup_ui(self):
        """Set up UI elements for the letter tracing game"""
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
            show_controls=False
        )
        
        # Title
        self.title_label = Label(
            screen_width // 2,
            Config.scale_height(25),
            "Trace the Letter",
            font_size=scaled_font_sizes['large'],
            centered=True
        )
        
        # Header bar
        self.header_rect = pygame.Rect(0, 0, screen_width, Config.scale_height(60))
        
        # Letter label - position above the whiteboard
        self.letter_label = Label(
            whiteboard_x + whiteboard_width // 2,
            whiteboard_y - Config.scale_height(25),
            "A",  # Will be updated in _generate_current_letter
            font_size=scaled_font_sizes['medium'],
            centered=True
        )
        
        # Instruction label - position below the whiteboard with proper spacing
        self.instruction_label = Label(
            whiteboard_x + whiteboard_width // 2,
            whiteboard_y + whiteboard_height + Config.scale_height(10),
            "Trace the letter as accurately as you can",
            font_size=scaled_font_sizes['small'],
            centered=True
        )
        
        # Set up difficulty selector in the top-right corner
        difficulty_panel_width = Config.scale_width(300)
        difficulty_panel_height = Config.scale_height(40)
        difficulty_panel_x = screen_width - difficulty_panel_width - Config.scale_width(20)
        difficulty_panel_y = Config.scale_height(10)
        
        self.difficulty_label = Label(
            difficulty_panel_x,
            difficulty_panel_y,
            "Difficulty:",
            font_size=scaled_font_sizes['small'],
            centered=False
        )
        
        # Create difficulty buttons
        diff_button_width = Config.scale_width(70)
        diff_button_height = Config.scale_height(30)
        diff_button_y = difficulty_panel_y + Config.scale_height(5)
        
        diff_colors = {
            "Easy": Config.GREEN,
            "Medium": (255, 165, 0),  # Orange
            "Hard": Config.RED
        }
        
        self.difficulty_buttons = {}
        for i, (diff_name, diff_color) in enumerate(diff_colors.items()):
            button_x = difficulty_panel_x + Config.scale_width(80) + i * (diff_button_width + Config.scale_width(10))
            
            # Highlight the current difficulty
            is_current = diff_name == self.current_difficulty
            button_bg = diff_color if is_current else Config.LIGHT_GRAY
            text_color = Config.WHITE if is_current else Config.BLACK
            
            self.difficulty_buttons[diff_name] = Button(
                button_x,
                diff_button_y,
                diff_button_width,
                diff_button_height,
                diff_name,
                lambda d=diff_name: self._set_difficulty(d),
                bg_color=button_bg,
                hover_color=diff_color,
                text_color=text_color,
                rounded=True,
                font_size=scaled_font_sizes['small']
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
            self._request_menu_exit,
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
        
        # Random Letter button - third from left
        random_x = clear_x + button_width + button_spacing
        self.random_letter_button = Button(
            random_x,
            button_y,
            button_width,
            scaled_button_height,
            "Random Letter",
            self._random_letter,
            bg_color=(50, 180, 150),  # Teal color
            hover_color=(80, 210, 180),
            text_color=Config.WHITE,
            rounded=True,
            font_size=scaled_font_sizes['small']
        )
        
        # Next Letter button - rightmost (initially disabled)
        next_x = random_x + button_width + button_spacing
        self.next_letter_button = Button(
            next_x,
            button_y,
            button_width,
            scaled_button_height,
            "Next Letter",
            self._next_letter,
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
    
    def _set_difficulty(self, difficulty):
        """Change the current difficulty setting"""
        if difficulty in self.difficulty_settings:
            self.current_difficulty = difficulty
            
            # Update button appearances
            for diff_name, button in self.difficulty_buttons.items():
                if diff_name == difficulty:
                    # Highlight selected difficulty
                    if diff_name == "Easy":
                        button.bg_color = Config.GREEN
                    elif diff_name == "Medium":
                        button.bg_color = (255, 165, 0)  # Orange
                    elif diff_name == "Hard":
                        button.bg_color = Config.RED
                    button.text_color = Config.WHITE
                else:
                    # Reset other buttons
                    button.bg_color = Config.LIGHT_GRAY
                    button.text_color = Config.BLACK
    
    def _generate_current_letter(self):
        """Generate the current letter based on the index"""
        if self.current_letter_index >= len(self.letters_data):
            # Loop back to first letter if we've gone through all letters
            self.current_letter_index = 0
        
        # Get current letter data
        letter_data = self.letters_data[self.current_letter_index]
        
        # Get whiteboard dimensions
        wb_width, wb_height = self.whiteboard.size
        
        # Create a completely new white surface
        self.whiteboard.drawing_engine.surface = pygame.Surface((wb_width, wb_height))
        self.whiteboard.drawing_engine.surface.fill(Config.WHITE)
        
        # Calculate an appropriate size for the letter (based on whiteboard)
        base_size = min(wb_width, wb_height) // 2.5
        
        # Adjust size based on difficulty
        size = base_size // letter_data["difficulty"]
        
        # Generate letter points using the LetterPathGenerator
        try:
            self.current_letter_points = LetterPathGenerator.generate_letter_path(
                letter_data["letter"],
                (wb_width // 2, wb_height // 2),  # Center of whiteboard
                size
            )
        except AttributeError:
            # Fallback to simple square if letter generation not implemented yet
            self.current_letter_points = PathDetection.generate_shape_path(
                "square",
                (wb_width // 2, wb_height // 2),
                size // 2
            )
        
        # Update letter label
        self.letter_label.text = letter_data["letter"]
        
        # Reset tracing state
        self.drawn_points = []
        self.accuracy_tracker.reset()
        self.accuracy_tracker.set_current_shape(letter_data["name"])
        self.is_tracing = False
        self.letter_completed = False
        self.next_letter_button.disabled = True
        self.auto_progress_timer = None
        
        # Draw the letter outline
        PathDetection.draw_shape_outline(
            self.whiteboard.drawing_engine.surface,
            self.current_letter_points,
            Config.BLUE,
            width=4,
            alpha=100
        )
        
        # Add to drawing history
        self.whiteboard.drawing_engine._add_to_history()
    
    def _request_menu_exit(self):
        """Sets the flag to request returning to the main menu."""
        if len(self.drawn_points) > 0 and not self.letter_completed:
            self.request_menu_exit = True
        else:
            self.request_menu_exit = True
    
    def _clear_drawing(self):
        """Clear the current drawing but keep the letter outline"""
        # Get the current whiteboard size
        wb_width, wb_height = self.whiteboard.size
        
        # Create a completely new white surface
        self.whiteboard.drawing_engine.surface = pygame.Surface((wb_width, wb_height))
        self.whiteboard.drawing_engine.surface.fill(Config.WHITE)
        
        # Reset drawn points and tracing state
        self.drawn_points = []
        self.is_tracing = False
        
        # Reset and update the accuracy tracker
        self.accuracy_tracker.reset()
        self.accuracy_tracker.set_current_shape(self.letters_data[self.current_letter_index]["name"])
        
        # Update button state
        self.next_letter_button.disabled = not self.letter_completed
        
        # Redraw the letter outline
        PathDetection.draw_shape_outline(
            self.whiteboard.drawing_engine.surface,
            self.current_letter_points,
            Config.BLUE,
            width=4,
            alpha=100
        )
        
        # Add this clear action to the drawing history
        self.whiteboard.drawing_engine._add_to_history()
    
    def _next_letter(self):
        """Proceed to the next letter"""
        if self.letter_completed:
            self.current_letter_index += 1
            # Clear whiteboard and regenerate letter
            self._generate_current_letter()
            
    def _random_letter(self):
        """Switch to a random letter"""
        import random
        
        # Get a random letter index different from current
        if len(self.letters_data) > 1:
            new_index = self.current_letter_index
            while new_index == self.current_letter_index:
                new_index = random.randint(0, len(self.letters_data) - 1)
            self.current_letter_index = new_index
        else:
            # If only one letter, just restart it
            pass
            
        # Generate the new letter with a clear whiteboard
        self._generate_current_letter()
    
    def _evaluate_tracing(self, is_final=False):
        """
        Evaluate the tracing accuracy and update metrics
        
        Args:
            is_final: Whether this is the final evaluation after drawing is complete
        """
        if len(self.drawn_points) < 5:
            # Not enough data to evaluate
            return
        
        # Calculate accuracy with difficulty-based tolerance
        tolerance = self.difficulty_settings[self.current_difficulty]
        
        metrics = PathDetection.calculate_tracing_accuracy(
            self.drawn_points,
            self.current_letter_points,
            tolerance=tolerance  # Use difficulty-based tolerance
        )
        
        # Update accuracy tracker
        self.accuracy_tracker.update_metrics(metrics)
        
        # For final evaluation (when drawing is complete)
        if is_final:
            # Enable next letter button if completed
            if self.accuracy_tracker.is_completed() and not self.letter_completed:
                self.letter_completed = True
                self.next_letter_button.disabled = False
                
                # Show completion dialog
                def close_dialog():
                    self.active_dialog = None
                    # Set timer for auto-progression (3 seconds)
                    self.auto_progress_timer = pygame.time.get_ticks() + 3000
                    
                self.active_dialog = Dialog(
                    self.screen,
                    f"Great job! You traced {self.letters_data[self.current_letter_index]['letter']} correctly.\n" +
                    f"Accuracy: {metrics['percentage']:.1f}%\n" +
                    "Moving to next letter in 3 seconds...",
                    close_dialog,
                    None,
                    title="Letter Completed!",
                    confirm_text="OK"
                )
    
    # Point tracking for real-time evaluation
    point_count = 0
    last_evaluation_time = 0
    
    def handle_event(self, event):
        """Handle pygame events"""
        # Handle dialog events first if active
        if self.active_dialog:
            if self.active_dialog.handle_event(event):
                return True
        
        # Handle resize event
        if event.type == pygame.VIDEORESIZE:
            self.handle_resize()
            return True
        
        # Handle button events
        button_handled = False
        if self.menu_button.handle_event(event): button_handled = True
        if self.clear_button.handle_event(event): button_handled = True
        if self.random_letter_button.handle_event(event): button_handled = True
        if self.next_letter_button.handle_event(event): button_handled = True
        for button in self.difficulty_buttons.values():
            if button.handle_event(event): button_handled = True
        
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
        
        return button_handled or False
        
    def update(self, dt):
        """Update game state"""
        mouse_pos = pygame.mouse.get_pos()
        self.whiteboard.update(dt)
        
        # Update UI buttons
        self.menu_button.update(mouse_pos)
        self.clear_button.update(mouse_pos)
        self.random_letter_button.update(mouse_pos)
        self.next_letter_button.update(mouse_pos)
        for button in self.difficulty_buttons.values():
            button.update(mouse_pos)
        
        # Update dialog if active
        if self.active_dialog:
            self.active_dialog.update(mouse_pos)
            
        # Check for auto-progression timer
        if self.auto_progress_timer and pygame.time.get_ticks() > self.auto_progress_timer:
            self.auto_progress_timer = None
            self._next_letter()  # Automatically progress to next letter
            
        # Check for state transition request
        if self.request_menu_exit:
            self.request_menu_exit = False
            return 'main_menu'
            
        return None
        
    def draw(self):
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
        
        # Draw difficulty selector
        self.difficulty_label.draw(self.screen)
        for button in self.difficulty_buttons.values():
            button.draw(self.screen)
        
        # Draw letter label
        self.letter_label.draw(self.screen)
        
        # Draw instruction label
        self.instruction_label.draw(self.screen)
        
        # Draw whiteboard
        self.whiteboard.render()
        
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
        self.random_letter_button.draw(self.screen)
        self.next_letter_button.draw(self.screen)
        
        # Draw dialog if active
        if self.active_dialog:
            self.active_dialog.draw()
    
    def handle_resize(self):
        self._setup_ui()
        self._generate_current_letter()
        
    def render(self):
        self.draw() 