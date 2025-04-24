import pygame
import math  # Add explicit import for math module
from typing import Dict, Any, Tuple, Optional
from src.config import Config

class AccuracyTracker:
    """
    Tracks and displays accuracy metrics for the shape tracing games.
    """
    
    def __init__(self):
        """Initialize the accuracy tracker with default values."""
        self.reset()
        self.last_update_time = 0  # For animations
        
    def reset(self):
        """Reset all tracking metrics."""
        self.metrics = {
            "percentage": 0.0,
            "on_path_points": 0,
            "total_points": 0,
            "avg_distance": 0.0,
            "max_distance": 0.0,
            "completed": False
        }
        self.attempts = 0
        self.best_percentage = 0.0
        self.prev_percentage = 0.0  # For tracking changes
        self.animation_progress = 0.0  # For smooth value changes
        
    def update_metrics(self, metrics: Dict[str, Any]):
        """
        Update the accuracy metrics.
        
        Args:
            metrics: Dictionary of accuracy metrics from path detection
        """
        # Save previous value for animation
        self.prev_percentage = self.metrics["percentage"]
        
        # Update metrics
        self.metrics.update(metrics)
        self.animation_progress = 0.0  # Reset animation progress
        self.last_update_time = pygame.time.get_ticks()
        
        # Only count as a new attempt if this is a substantial update
        if metrics.get("total_points", 0) > 10 and not self.metrics.get("completed", False):
            self.attempts += 1
        
        # Update best percentage if current is better
        if self.metrics["percentage"] > self.best_percentage:
            self.best_percentage = self.metrics["percentage"]
            
        # Check if the shape is considered completed (based on accuracy threshold)
        if self.metrics["percentage"] >= 85.0:  # 85% accuracy threshold for success
            self.metrics["completed"] = True
    
    def is_completed(self) -> bool:
        """Check if the current shape is completed successfully."""
        return self.metrics["completed"]
    
    def get_grade(self) -> str:
        """Get a letter grade based on accuracy percentage."""
        percentage = self.metrics["percentage"]
        
        if percentage >= 95:
            return "A+"
        elif percentage >= 90:
            return "A"
        elif percentage >= 85:
            return "B+"
        elif percentage >= 80:
            return "B"
        elif percentage >= 75:
            return "C+"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
    
    def get_feedback_message(self) -> str:
        """Get a feedback message based on the current accuracy."""
        percentage = self.metrics["percentage"]
        attempts = self.attempts
        total_points = self.metrics.get("total_points", 0)
        
        # If very few points, give encouragement
        if total_points < 10:
            return "Start tracing the shape..."
        
        if percentage >= 90:
            return "Excellent tracing!"
        elif percentage >= 80:
            return "Great job!"
        elif percentage >= 70:
            return "Good tracing, keep practicing!"
        elif percentage >= 60:
            return "Not bad, try to stay on the lines."
        elif percentage >= 50:
            return "Try to follow the shape more closely."
        elif attempts <= 2:
            return "Take your time and trace carefully."
        else:
            return "Keep practicing, you'll get better!"
    
    def draw_accuracy_panel(self, surface: pygame.Surface, position: Tuple[int, int], 
                          size: Tuple[int, int], show_details: bool = True):
        """
        Draw an accuracy panel on the given surface.
        
        Args:
            surface: Pygame surface to draw on
            position: (x, y) top-left position of the panel
            size: (width, height) size of the panel
            show_details: Whether to show detailed metrics or just summary
        """
        x, y = position
        width, height = size
        
        # Update animation progress (smooth transitions)
        current_time = pygame.time.get_ticks()
        if self.animation_progress < 1.0:
            time_since_update = (current_time - self.last_update_time) / 1000.0  # seconds
            self.animation_progress = min(1.0, self.animation_progress + time_since_update * 3.0)  # Animate over ~0.33 seconds
        
        # Calculate interpolated percentage for smooth animation
        display_percentage = self.prev_percentage + (self.metrics["percentage"] - self.prev_percentage) * self.animation_progress
        
        # Draw panel background with slight gradient
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, Config.WHITE, panel_rect)
        pygame.draw.rect(surface, Config.BLACK, panel_rect, 2)
        
        # Add subtle gradient background based on completion percentage
        if display_percentage > 0:
            gradient_color = self._get_grade_color(self.get_grade(), alpha=30)
            gradient_height = int(panel_rect.height * min(1.0, display_percentage / 100.0))
            gradient_rect = pygame.Rect(x+2, y+panel_rect.height-gradient_height, width-4, gradient_height)
            gradient_surface = pygame.Surface((gradient_rect.width, gradient_rect.height), pygame.SRCALPHA)
            gradient_surface.fill(gradient_color)
            surface.blit(gradient_surface, gradient_rect)
        
        # Get scaled font sizes
        scaled_font_sizes = Config.get_scaled_font_sizes()
        
        # Create fonts
        title_font = pygame.font.SysFont(None, scaled_font_sizes['medium'])
        grade_font = pygame.font.SysFont(None, scaled_font_sizes['large'])
        detail_font = pygame.font.SysFont(None, scaled_font_sizes['small'])
        
        # Draw title
        title_surf = title_font.render("Accuracy", True, Config.BLACK)
        title_rect = title_surf.get_rect(midtop=(x + width//2, y + 10))
        surface.blit(title_surf, title_rect)
        
        # Draw grade with slightly larger size and pulsing effect if completed
        grade = self.get_grade()
        grade_color = self._get_grade_color(grade)
        
        # Add pulsing effect for completed shapes
        if self.metrics["completed"]:
            pulse = 0.5 + 0.5 * abs(math.sin(current_time / 200))  # Use math.sin instead of pygame.math.sin
            grade_size = int(scaled_font_sizes['large'] * (1.0 + pulse * 0.15))  # Increase size by up to 15%
            grade_font = pygame.font.SysFont(None, grade_size)
        
        grade_surf = grade_font.render(grade, True, grade_color)
        grade_rect = grade_surf.get_rect(center=(x + width//2, y + 60))
        surface.blit(grade_surf, grade_rect)
        
        # Draw percentage with animated value change
        percentage_text = f"{display_percentage:.1f}%"
        percentage_surf = title_font.render(percentage_text, True, Config.BLACK)
        percentage_rect = percentage_surf.get_rect(midtop=(x + width//2, y + 90))
        surface.blit(percentage_surf, percentage_rect)
        
        # Draw small progress bar under percentage
        progress_width = width - 40
        progress_rect = pygame.Rect(x + 20, y + 120, progress_width, 8)
        pygame.draw.rect(surface, Config.LIGHT_GRAY, progress_rect)
        filled_width = int(progress_width * min(1.0, display_percentage / 100.0))
        if filled_width > 0:
            filled_rect = pygame.Rect(x + 20, y + 120, filled_width, 8)
            pygame.draw.rect(surface, grade_color, filled_rect)
        pygame.draw.rect(surface, Config.BLACK, progress_rect, 1)
        
        # Draw feedback message
        feedback = self.get_feedback_message()
        feedback_surf = detail_font.render(feedback, True, Config.BLACK)
        feedback_rect = feedback_surf.get_rect(midtop=(x + width//2, y + 140))
        surface.blit(feedback_surf, feedback_rect)
        
        # Draw detailed metrics if requested
        if show_details and height > 200:
            detail_y = y + 170
            line_height = 25
            
            # Draw metrics
            metrics_items = [
                f"Points on path: {self.metrics['on_path_points']}/{self.metrics['total_points']}",
                f"Avg. distance: {self.metrics['avg_distance']:.1f} px",
                f"Best attempt: {self.best_percentage:.1f}%",
                f"Attempts: {self.attempts}"
            ]
            
            for item in metrics_items:
                item_surf = detail_font.render(item, True, Config.BLACK)
                item_rect = item_surf.get_rect(topleft=(x + 15, detail_y))
                surface.blit(item_surf, item_rect)
                detail_y += line_height
            
            # Draw completion indicator
            if self.metrics["completed"]:
                completion_text = "COMPLETED!"
                completion_surf = detail_font.render(completion_text, True, (0, 128, 0))
                completion_rect = completion_surf.get_rect(midbottom=(x + width//2, y + height - 15))
                surface.blit(completion_surf, completion_rect)
    
    def _get_grade_color(self, grade: str, alpha: int = 255) -> Tuple[int, int, int] or Tuple[int, int, int, int]:
        """
        Get a color for a given grade.
        
        Args:
            grade: The letter grade
            alpha: Optional alpha value (0-255)
        
        Returns:
            RGB or RGBA color tuple
        """
        if grade.startswith('A'):
            color = (0, 128, 0)  # Green
        elif grade.startswith('B'):
            color = (0, 100, 200)  # Blue
        elif grade.startswith('C'):
            color = (255, 165, 0)  # Orange
        elif grade.startswith('D'):
            color = (200, 100, 50)  # Dark Orange
        else:
            color = (200, 0, 0)  # Red
            
        if alpha < 255:
            return (*color, alpha)
        return color 