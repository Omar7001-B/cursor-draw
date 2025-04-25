import pygame
from typing import List, Tuple, Optional, Dict
from src.config import Config
from src.core.ui_manager import Button, Label, Dialog
from src.core.whiteboard import Whiteboard
from src.utils.text_path_generator import TextPathGenerator
from src.utils.path_detection import PathDetection
from src.utils.accuracy import AccuracyTracker

class TraceTheSentence:
    """
    A game where players trace sentences to improve handwriting and cursor control.
    """
    
    def __init__(self, screen: pygame.Surface, game_state):
        self.screen = screen
        self.game_state = game_state
        self.next_screen = None
        
        # Get screen dimensions
        self.screen_width, self.screen_height = self.screen.get_size()
        
        # Initialize game state
        self.current_sentence_index = 0
        self.drawn_points = []
        self.current_text_paths = []
        self.is_tracing = False
        self.sentence_completed = False
        self.point_count = 0
        self.last_evaluation_time = 0
        self.auto_progress_timer = None
        
        # Initialize difficulty settings
        self.difficulty_settings = {
            "Easy": 20,      # Larger tolerance
            "Medium": 15,    # Medium tolerance
            "Hard": 10       # Smaller tolerance
        }
        self.current_difficulty = "Medium"
        
        # Sample sentences for each difficulty
        self.sentences_data = [
            {
                "text": "Hello World",
                "name": "Hello World",
                "difficulty": 1
            },
            {
                "text": "Practice Makes Perfect",
                "name": "Practice Makes Perfect",
                "difficulty": 1.2
            },
            {
                "text": "Keep Going Forward",
                "name": "Keep Going Forward",
                "difficulty": 1.3
            },
            {
                "text": "You Can Do It",
                "name": "You Can Do It",
                "difficulty": 1.4
            }
        ]
        
        # Set up UI elements
        self._setup_ui()
        
        # Initialize accuracy tracker
        self.accuracy_tracker = AccuracyTracker()
        
        # Generate first sentence
        self._generate_current_sentence()
        
    def _setup_ui(self):
        """Set up UI elements for the game"""
        # Get scaled dimensions
        scaled_font_sizes = Config.get_scaled_font_sizes()
        scaled_button_width, scaled_button_height = Config.get_scaled_button_dimensions()
        
        # Header bar height
        header_height = Config.scale_height(60)
        
        # Create whiteboard with specific dimensions
        whiteboard_width = self.screen_width - Config.scale_width(260)  # Leave more space for accuracy panel
        whiteboard_height = self.screen_height - header_height - Config.scale_height(180)  # Space for header and controls
        
        self.whiteboard = Whiteboard(
            self.screen,
            (Config.scale_width(20), header_height + Config.scale_height(60)),  # Position below header
            (whiteboard_width, whiteboard_height),
            show_controls=False  # Hide default controls
        )
        
        # Create sentence label
        self.sentence_label = Label(
            self.screen_width // 2,
            Config.scale_height(30),
            "Sentence",
            font_size=scaled_font_sizes['medium'],
            centered=True
        )
        
        # Create instruction label
        self.instruction_label = Label(
            self.screen_width // 2,
            self.screen_height - Config.scale_height(40),
            "Trace the sentence to improve your handwriting",
            font_size=scaled_font_sizes['small'],
            centered=True
        )
        
        # Create accuracy panel with more width
        self.accuracy_panel_rect = pygame.Rect(
            self.screen_width - Config.scale_width(240),
            header_height + Config.scale_height(80),
            Config.scale_width(220),
            Config.scale_height(200)
        )
        
        # Button spacing and dimensions
        button_margin = Config.scale_width(20)
        button_width = scaled_button_width * 0.85  # Slightly smaller buttons
        button_spacing = (whiteboard_width - 4 * button_width - 2 * button_margin) / 3
        button_y = self.screen_height - Config.scale_height(100)  # Move buttons up
        
        # Create buttons with proper spacing
        self.menu_button = Button(
            Config.scale_width(20),
            button_y,
            button_width,
            scaled_button_height,
            "Back to Menu",
            self._back_to_menu,
            bg_color=Config.BLUE,
            hover_color=(100, 150, 255),
            text_color=Config.WHITE,
            rounded=True,
            font_size=scaled_font_sizes['small']
        )
        
        self.clear_button = Button(
            Config.scale_width(20) + button_width + button_spacing,
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
        
        self.next_sentence_button = Button(
            Config.scale_width(20) + (button_width + button_spacing) * 2,
            button_y,
            button_width,
            scaled_button_height,
            "Next Sentence",
            self._next_sentence,
            bg_color=Config.GREEN,
            hover_color=(100, 200, 100),
            text_color=Config.WHITE,
            disabled=True,
            rounded=True,
            font_size=scaled_font_sizes['small']
        )
        
        self.random_sentence_button = Button(
            Config.scale_width(20) + (button_width + button_spacing) * 3,
            button_y,
            button_width,
            scaled_button_height,
            "Random",
            self._random_sentence,
            bg_color=Config.LIGHT_GRAY,
            hover_color=Config.GRAY,
            text_color=Config.BLACK,
            rounded=True,
            font_size=scaled_font_sizes['small']
        )
        
        # Create difficulty buttons with better spacing
        difficulty_button_width = Config.scale_width(80)
        difficulty_button_height = Config.scale_height(30)
        difficulty_start_x = Config.scale_width(20)
        difficulty_y = header_height + Config.scale_height(20)
        
        self.difficulty_buttons = {}
        diff_colors = {
            "Easy": (100, 200, 100),    # Light green
            "Medium": (200, 150, 50),    # Orange
            "Hard": (200, 100, 100)      # Red
        }
        
        for i, difficulty in enumerate(self.difficulty_settings.keys()):
            self.difficulty_buttons[difficulty] = Button(
                difficulty_start_x + (difficulty_button_width + Config.scale_width(10)) * i,
                difficulty_y,
                difficulty_button_width,
                difficulty_button_height,
                difficulty,
                lambda d=difficulty: self._set_difficulty(d),
                bg_color=diff_colors[difficulty] if difficulty == self.current_difficulty else Config.LIGHT_GRAY,
                hover_color=diff_colors[difficulty],
                text_color=Config.WHITE if difficulty == self.current_difficulty else Config.BLACK,
                rounded=True,
                font_size=scaled_font_sizes['small']
            )
            
        # Initialize dialog as None
        self.active_dialog = None
        
    def _generate_current_sentence(self):
        """Generate the current sentence based on the index"""
        if self.current_sentence_index >= len(self.sentences_data):
            # Loop back to first sentence if we've gone through all sentences
            self.current_sentence_index = 0
        
        # Get current sentence data
        sentence_data = self.sentences_data[self.current_sentence_index]
        
        # Get whiteboard dimensions
        wb_width, wb_height = self.whiteboard.size
        
        # Create a completely new white surface
        self.whiteboard.drawing_engine.surface = pygame.Surface((wb_width, wb_height))
        self.whiteboard.drawing_engine.surface.fill(Config.WHITE)
        
        # Calculate an appropriate size for the text (based on whiteboard)
        base_size = min(wb_width, wb_height) // 8
        
        # Adjust size based on difficulty
        size = base_size // sentence_data["difficulty"]
        
        # Generate text paths
        self.current_text_paths = TextPathGenerator.generate_text_path(
            sentence_data["text"],
            (wb_width // 6, wb_height // 3),  # Start position
            size
        )
        
        # Update sentence label
        self.sentence_label.text = sentence_data["name"]
        
        # Reset tracing state
        self.drawn_points = []
        self.accuracy_tracker.reset()
        self.accuracy_tracker.set_current_shape(sentence_data["name"])
        self.is_tracing = False
        self.sentence_completed = False
        self.next_sentence_button.disabled = True
        self.auto_progress_timer = None
        
        # Draw the text outline
        TextPathGenerator.draw_text_outline(
            self.whiteboard.drawing_engine.surface,
            self.current_text_paths,
            Config.BLUE,
            width=4,
            alpha=100
        )
        
        # Add to drawing history
        self.whiteboard.drawing_engine._add_to_history()
        
    def _clear_drawing(self):
        """Clear the current drawing but keep the text outline"""
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
        self.accuracy_tracker.set_current_shape(self.sentences_data[self.current_sentence_index]["name"])
        
        # Update button state
        self.next_sentence_button.disabled = not self.sentence_completed
        
        # Redraw the text outline
        TextPathGenerator.draw_text_outline(
            self.whiteboard.drawing_engine.surface,
            self.current_text_paths,
            Config.BLUE,
            width=4,
            alpha=100
        )
        
        # Add this clear action to the drawing history
        self.whiteboard.drawing_engine._add_to_history()
        
    def _next_sentence(self):
        """Proceed to the next sentence"""
        if self.sentence_completed:
            self.current_sentence_index += 1
            # Clear whiteboard and regenerate sentence
            self._generate_current_sentence()
            
    def _random_sentence(self):
        """Switch to a random sentence"""
        import random
        
        # Get a random sentence index different from current
        if len(self.sentences_data) > 1:
            new_index = self.current_sentence_index
            while new_index == self.current_sentence_index:
                new_index = random.randint(0, len(self.sentences_data) - 1)
            self.current_sentence_index = new_index
        else:
            # If only one sentence, just restart it
            pass
            
        # Generate the new sentence with a clear whiteboard
        self._generate_current_sentence()
        
    def _set_difficulty(self, difficulty: str):
        """Set the current difficulty level"""
        if difficulty in self.difficulty_settings:
            # Update button colors
            for button in self.difficulty_buttons.values():
                if button.text == difficulty:
                    button.bg_color = Config.GREEN
                else:
                    button.bg_color = Config.LIGHT_GRAY
            
            # Update current difficulty
            self.current_difficulty = difficulty
            
            # Reset the current sentence
            self._clear_drawing()
            
    def _back_to_menu(self):
        """Return to the main menu"""
        from src.screens.main_menu import MainMenu
        self.next_screen = MainMenu(self.screen, self.game_state)
        
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
        
        # Flatten all text paths into one list for evaluation
        all_points = []
        for path in self.current_text_paths:
            all_points.extend(path)
        
        metrics = PathDetection.calculate_tracing_accuracy(
            self.drawn_points,
            all_points,
            tolerance=tolerance  # Use difficulty-based tolerance
        )
        
        # Update accuracy tracker
        self.accuracy_tracker.update_metrics(metrics)
        
        # Check if sentence is completed
        if metrics["percentage"] >= 85 and not self.sentence_completed:
            self.sentence_completed = True
            self.next_sentence_button.disabled = False
            
            # Only set auto-progress timer on final evaluation
            if is_final:
                # Show completion dialog
                def close_dialog():
                    self.active_dialog = None
                    # Set timer for auto-progression (3 seconds)
                    self.auto_progress_timer = pygame.time.get_ticks() + 3000
                    
                self.active_dialog = Dialog(
                    self.screen,
                    f"Great job! You traced the sentence correctly.\n" +
                    f"Accuracy: {metrics['percentage']:.1f}%\n" +
                    "Moving to next sentence in 3 seconds...",
                    close_dialog,
                    None,
                    title="Sentence Completed!",
                    confirm_text="OK"
                )
        
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.VIDEORESIZE:
            # Recreate UI elements when window is resized
            self._setup_ui()
            return
            
        # Handle dialog events if active
        if self.active_dialog:
            if self.active_dialog.handle_event(event):
                return
                
        # Handle button events
        self.menu_button.handle_event(event)
        self.clear_button.handle_event(event)
        self.next_sentence_button.handle_event(event)
        self.random_sentence_button.handle_event(event)
        
        # Handle difficulty buttons
        for button in self.difficulty_buttons.values():
            button.handle_event(event)
            
        # Get whiteboard rect for collision detection
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
            self.next_sentence_button.update(mouse_pos)
            self.random_sentence_button.update(mouse_pos)
            
            # Update difficulty buttons
            for button in self.difficulty_buttons.values():
                button.update(mouse_pos)
            
        # Update dialog if active
        if self.active_dialog and mouse_pos:
            self.active_dialog.update(mouse_pos)
            
        # Check for auto-progression timer
        if self.auto_progress_timer and pygame.time.get_ticks() > self.auto_progress_timer:
            self.auto_progress_timer = None
            self._next_sentence()  # Automatically progress to next sentence
            
        # Return next screen if set
        if self.next_screen:
            next_screen = self.next_screen
            self.next_screen = None
            return next_screen
            
        return None
        
    def render(self):
        """Render the game screen"""
        # Clear screen
        self.screen.fill(Config.WHITE)
        
        # Draw header bar
        pygame.draw.rect(self.screen, Config.BLUE, (0, 0, self.screen_width, Config.scale_height(60)))
        
        # Draw sentence label with white color for contrast
        title_color_original = self.sentence_label.color
        self.sentence_label.color = Config.WHITE
        self.sentence_label.draw(self.screen)
        self.sentence_label.color = title_color_original
        
        # Draw whiteboard
        self.whiteboard.render()
        
        # Draw accuracy panel
        self.accuracy_tracker.draw_accuracy_panel(
            self.screen,
            (self.accuracy_panel_rect.x, self.accuracy_panel_rect.y),
            (self.accuracy_panel_rect.width, self.accuracy_panel_rect.height)
        )
        
        # Draw buttons
        self.menu_button.draw(self.screen)
        self.clear_button.draw(self.screen)
        self.next_sentence_button.draw(self.screen)
        self.random_sentence_button.draw(self.screen)
        
        # Draw difficulty buttons
        for button in self.difficulty_buttons.values():
            button.draw(self.screen)
            
        # Draw instruction label
        self.instruction_label.draw(self.screen)
        
        # Draw dialog if active
        if self.active_dialog:
            self.active_dialog.draw() 