import pygame
import math
from src.config import Config

class DrawingEngine:
    """
    Core drawing engine that handles drawing operations on a canvas.
    This is used for all drawing activities in the application.
    """
    def __init__(self, width, height, bg_color=Config.WHITE):
        # Create drawing surface
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.surface = pygame.Surface((width, height))
        self.surface.fill(bg_color)
        
        # Drawing state
        self.is_drawing = False
        self.last_pos = None
        
        # Brush properties
        self.brush_size_index = 1  # Default to medium
        self.brush_color_index = 0  # Default to black
        self.eraser_mode = False
        
        # History for undo/redo
        self.history = [pygame.Surface.copy(self.surface)]
        self.history_index = 0
        self.max_history = 10
        
    @property
    def brush_size(self):
        return Config.BRUSH_SIZES[self.brush_size_index]
        
    @property
    def brush_color(self):
        return Config.BRUSH_COLORS[self.brush_color_index] if not self.eraser_mode else self.bg_color
        
    def start_drawing(self, pos):
        """Start a new drawing operation"""
        self.is_drawing = True
        self.last_pos = pos
        # Draw a single dot at the starting position
        pygame.draw.circle(self.surface, self.brush_color, pos, self.brush_size // 2)
        
    def draw_to(self, pos):
        """Continue drawing to a new position"""
        if not self.is_drawing or self.last_pos is None:
            return
            
        # Draw a line from last position to current position
        self._draw_line(self.last_pos, pos)
        self.last_pos = pos
        
    def stop_drawing(self):
        """End the current drawing operation"""
        if self.is_drawing:
            self.is_drawing = False
            self.last_pos = None
            self._add_to_history()
            
    def clear_canvas(self, animated=False):
        """Clear the canvas, with optional animation effect"""
        if animated:
            # Perform clearing animation
            clear_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            for alpha in range(0, 256, 15):
                clear_surf.fill((self.bg_color[0], self.bg_color[1], self.bg_color[2], alpha))
                temp_surf = self.surface.copy()
                temp_surf.blit(clear_surf, (0, 0))
                # Signal that this is an animation frame, not final state
                yield temp_surf
                pygame.time.delay(20)
        
        # Finally, clear the actual canvas
        self.surface.fill(self.bg_color)
        self._add_to_history()
        
    def set_brush_size(self, size_index):
        """Set the brush size by index"""
        if 0 <= size_index < len(Config.BRUSH_SIZES):
            self.brush_size_index = size_index
            
    def set_brush_color(self, color_index):
        """Set the brush color by index"""
        if 0 <= color_index < len(Config.BRUSH_COLORS):
            self.brush_color_index = color_index
            self.eraser_mode = False
            
    def toggle_eraser(self):
        """Toggle eraser mode on/off"""
        self.eraser_mode = not self.eraser_mode
        
    def undo(self):
        """Undo the last drawing operation"""
        if self.history_index > 0:
            self.history_index -= 1
            self.surface = pygame.Surface.copy(self.history[self.history_index])
            
    def redo(self):
        """Redo a previously undone drawing operation"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.surface = pygame.Surface.copy(self.history[self.history_index])
            
    def save_image(self, filename):
        """Save the current canvas as an image file"""
        pygame.image.save(self.surface, filename)
        
    def _draw_line(self, start, end):
        """Draw a smooth line between two points"""
        # Calculate the distance between points
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = max(1, math.sqrt(dx*dx + dy*dy))
        
        # Determine how many points we need to interpolate
        num_points = max(2, int(distance // 2))
        
        # Draw intermediate points for smooth line
        for i in range(num_points):
            t = i / (num_points - 1)
            x = int(start[0] + dx * t)
            y = int(start[1] + dy * t)
            pygame.draw.circle(self.surface, self.brush_color, (x, y), self.brush_size // 2)
            
    def _add_to_history(self):
        """Add current state to history stack"""
        # Remove any future history if we're in the middle of the stack
        self.history = self.history[:self.history_index + 1]
        
        # Add current state
        self.history.append(pygame.Surface.copy(self.surface))
        self.history_index = len(self.history) - 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
            self.history_index = len(self.history) - 1 