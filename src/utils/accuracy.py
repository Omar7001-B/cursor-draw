import pygame
from typing import Dict, Any, Tuple, Optional
from src.config import Config

class AccuracyTracker:
    """
    Tracks and displays accuracy metrics for the shape tracing games.
    """
    
    def __init__(self):
        """Initialize the accuracy tracker with default values."""
        self.reset()
        
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
    
    def update_metrics(self, metrics: Dict[str, Any]):
        """
        Update the accuracy metrics.
        
        Args:
            metrics: Dictionary of accuracy metrics from path detection
        """
        self.metrics.update(metrics)
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
        
        # Draw panel background
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, Config.WHITE, panel_rect)
        pygame.draw.rect(surface, Config.BLACK, panel_rect, 2)
        
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
        
        # Draw grade
        grade = self.get_grade()
        grade_color = self._get_grade_color(grade)
        grade_surf = grade_font.render(grade, True, grade_color)
        grade_rect = grade_surf.get_rect(center=(x + width//2, y + 60))
        surface.blit(grade_surf, grade_rect)
        
        # Draw percentage
        percentage_text = f"{self.metrics['percentage']:.1f}%"
        percentage_surf = title_font.render(percentage_text, True, Config.BLACK)
        percentage_rect = percentage_surf.get_rect(midtop=(x + width//2, y + 90))
        surface.blit(percentage_surf, percentage_rect)
        
        # Draw feedback message
        feedback = self.get_feedback_message()
        feedback_surf = detail_font.render(feedback, True, Config.BLACK)
        feedback_rect = feedback_surf.get_rect(midtop=(x + width//2, y + 130))
        surface.blit(feedback_surf, feedback_rect)
        
        # Draw detailed metrics if requested
        if show_details and height > 200:
            detail_y = y + 160
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
    
    def _get_grade_color(self, grade: str) -> Tuple[int, int, int]:
        """Get a color for a given grade."""
        if grade.startswith('A'):
            return (0, 128, 0)  # Green
        elif grade.startswith('B'):
            return (0, 100, 200)  # Blue
        elif grade.startswith('C'):
            return (255, 165, 0)  # Orange
        elif grade.startswith('D'):
            return (200, 100, 50)  # Dark Orange
        else:
            return (200, 0, 0)  # Red 