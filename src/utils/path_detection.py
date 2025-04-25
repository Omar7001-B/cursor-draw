import math
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import pygame

class PathDetection:
    """
    Utility class for detecting and measuring the accuracy of a drawn path
    against a target path or shape.
    """
    
    # Add a cache to avoid repeated calculations
    _distance_cache = {}
    
    @staticmethod
    def calculate_distance_to_shape(point: Tuple[int, int], shape_points: List[Tuple[int, int]]) -> float:
        """
        Calculate the minimum distance from a point to a shape defined by a list of points.
        
        Args:
            point: The (x, y) coordinates of the point
            shape_points: A list of (x, y) coordinates defining the shape
            
        Returns:
            The minimum distance from the point to the shape
        """
        if not shape_points:
            return float('inf')
        
        # Check if this calculation has been cached
        cache_key = (point, tuple(shape_points))
        if cache_key in PathDetection._distance_cache:
            return PathDetection._distance_cache[cache_key]
            
        # Find the minimum distance to any line segment in the shape
        min_distance = float('inf')
        
        # Optimize by sampling shape points if there are many
        stride = max(1, len(shape_points) // 20)  # Sample at most 20 segments for performance
        indices = range(0, len(shape_points), stride)
        
        for i in indices:
            # Get the current line segment
            p1 = shape_points[i]
            p2 = shape_points[(i + stride) % len(shape_points)]  # Wrap around to the first point
            
            # Calculate distance from point to line segment
            dist = PathDetection._distance_point_to_line_segment(point, p1, p2)
            min_distance = min(min_distance, dist)
        
        # Store in cache for future use (limit cache size)
        if len(PathDetection._distance_cache) > 1000:
            PathDetection._distance_cache.clear()  # Avoid memory issues by clearing cache if too large
        PathDetection._distance_cache[cache_key] = min_distance
            
        return min_distance
    
    @staticmethod
    def _distance_point_to_line_segment(point: Tuple[int, int], line_start: Tuple[int, int], 
                                        line_end: Tuple[int, int]) -> float:
        """
        Calculate the distance from a point to a line segment.
        
        Args:
            point: The (x, y) coordinates of the point
            line_start: The (x, y) coordinates of the line segment start
            line_end: The (x, y) coordinates of the line segment end
            
        Returns:
            The distance from the point to the line segment
        """
        # Faster implementation using direct calculations rather than numpy operations
        x, y = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Calculate the squared length of the line segment
        dx = x2 - x1
        dy = y2 - y1
        len_sq = dx*dx + dy*dy
        
        # Handle degenerate case (point or extremely short segment)
        if len_sq < 1e-6:
            # Distance to a point
            dx1 = x - x1
            dy1 = y - y1
            return math.sqrt(dx1*dx1 + dy1*dy1)
            
        # Calculate the projection position
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / len_sq))
        
        # Calculate the closest point on the line segment
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        
        # Return the distance to the projection
        dx = x - proj_x
        dy = y - proj_y
        return math.sqrt(dx*dx + dy*dy)
    
    @staticmethod
    def calculate_tracing_accuracy(drawn_path: List[Tuple[int, int]], 
                                  target_path: List[Tuple[int, int]],
                                  tolerance: int = 10) -> Dict[str, Any]:
        """
        Calculate the accuracy of a drawn path compared to a target path.
        
        Args:
            drawn_path: List of (x, y) coordinates representing the user's drawn path
            target_path: List of (x, y) coordinates representing the target path
            tolerance: Maximum distance (in pixels) for a point to be considered "on path"
            
        Returns:
            Dictionary containing accuracy metrics:
                - percentage: Overall accuracy percentage (0-100)
                - on_path_points: Number of points that were on the path
                - total_points: Total number of points in the drawn path
                - avg_distance: Average distance from drawn points to target path
                - max_distance: Maximum distance from any drawn point to target path
        """
        if not drawn_path or not target_path:
            return {
                "percentage": 0.0,
                "on_path_points": 0,
                "total_points": len(drawn_path) if drawn_path else 0,
                "avg_distance": float('inf'),
                "max_distance": float('inf')
            }
        
        # Optimize by sampling drawn points if there are too many
        # For real-time feedback, we don't need to process every point
        sample_drawn_path = drawn_path
        if len(drawn_path) > 50:  # If more than 50 points, sample
            stride = len(drawn_path) // 50 + 1
            sample_drawn_path = drawn_path[::stride]
            
        # Cache target_path as tuple for using in distance calculations
        target_path_tuple = tuple(target_path)
        
        # Calculate distances from each drawn point to the target path
        distances = []
        on_path_count = 0
        max_distance = 0
        
        distance_sum = 0
        
        for point in sample_drawn_path:
            dist = PathDetection.calculate_distance_to_shape(point, target_path)
            distance_sum += dist
            
            if dist <= tolerance:
                on_path_count += 1
                
            max_distance = max(max_distance, dist)
        
        # Calculate metrics
        sample_total = len(sample_drawn_path)
        total_points = len(drawn_path)
        # Scale up the counts based on the sampling
        if sample_total < total_points:
            scale_factor = total_points / sample_total
            on_path_count = int(on_path_count * scale_factor)
            
        accuracy_percentage = (on_path_count / total_points) * 100 if total_points > 0 else 0
        avg_distance = distance_sum / sample_total if sample_total > 0 else float('inf')
        
        return {
            "percentage": accuracy_percentage,
            "on_path_points": on_path_count,
            "total_points": total_points,
            "avg_distance": avg_distance,
            "max_distance": max_distance
        }
    
    @staticmethod
    def generate_shape_path(shape_type: str, center: Tuple[int, int], size: int, 
                           num_points: int = 64) -> List[Tuple[int, int]]:
        """
        Generate a path of points that define a standard shape.
        
        Args:
            shape_type: Type of shape ("circle", "square", "triangle", etc.)
            center: (x, y) center coordinates
            size: Size parameter (radius for circle, side length for square, etc.)
            num_points: Number of points to generate for curved shapes
            
        Returns:
            List of (x, y) coordinates defining the shape's path
        """
        shape_type = shape_type.lower()
        cx, cy = center
        
        if shape_type == "circle":
            # Generate a circle with the specified number of points
            points = []
            for i in range(num_points):
                angle = 2 * math.pi * i / num_points
                x = cx + size * math.cos(angle)
                y = cy + size * math.sin(angle)
                points.append((int(x), int(y)))
            return points
            
        elif shape_type == "square":
            # Generate a square with 4 corners
            half_size = size // 2
            return [
                (cx - half_size, cy - half_size),  # Top-left
                (cx + half_size, cy - half_size),  # Top-right
                (cx + half_size, cy + half_size),  # Bottom-right
                (cx - half_size, cy + half_size)   # Bottom-left
            ]
            
        elif shape_type == "triangle":
            # Generate an equilateral triangle
            height = int(size * math.sqrt(3) / 2)
            return [
                (cx, cy - height * 2//3),             # Top
                (cx - size // 2, cy + height // 3),   # Bottom-left
                (cx + size // 2, cy + height // 3)    # Bottom-right
            ]
            
        elif shape_type == "rectangle":
            # Generate a rectangle (width = 2*size, height = size)
            return [
                (cx - size, cy - size // 2),    # Top-left
                (cx + size, cy - size // 2),    # Top-right
                (cx + size, cy + size // 2),    # Bottom-right
                (cx - size, cy + size // 2)     # Bottom-left
            ]
            
        elif shape_type == "diamond":
            # Generate a diamond (rhombus)
            return [
                (cx, cy - size),       # Top
                (cx + size, cy),       # Right
                (cx, cy + size),       # Bottom
                (cx - size, cy)        # Left
            ]
            
        else:
            # Default to circle if shape is not recognized
            return PathDetection.generate_shape_path("circle", center, size, num_points)
    
    @staticmethod
    def draw_shape_outline(surface: pygame.Surface, shape_points: List[Tuple[int, int]], 
                         color: Tuple[int, int, int], width: int = 1,
                         alpha: int = 128) -> None:
        """
        Draw a shape outline on a pygame surface.
        
        Args:
            surface: Pygame surface to draw on
            shape_points: List of (x, y) coordinates defining the shape
            color: RGB color tuple
            width: Line width in pixels
            alpha: Transparency level (0-255)
        """
        if len(shape_points) < 2:
            return
            
        # Create a temporary surface for the shape with transparency
        temp_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Draw the shape on the temporary surface
        if len(shape_points) > 2:
            pygame.draw.polygon(temp_surface, (*color, alpha), shape_points, width)
        else:
            # For just two points, draw a line
            pygame.draw.line(temp_surface, (*color, alpha), shape_points[0], shape_points[1], width)
            
        # Blit the temporary surface onto the main surface
        surface.blit(temp_surface, (0, 0)) 