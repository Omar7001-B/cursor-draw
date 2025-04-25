from typing import List, Tuple, Dict
import math

class LetterPathGenerator:
    """
    Utility class for generating paths for letters.
    Each letter is defined as a series of points that form its shape.
    """
    
    @staticmethod
    def generate_letter_path(letter: str, center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """
        Generate a path for a given letter.
        
        Args:
            letter: The letter to generate a path for
            center: The center point (x, y) for the letter
            size: The size of the letter
            
        Returns:
            List of points that form the letter's path
        """
        # Convert letter to uppercase for consistency
        letter = letter.upper()
        
        # Get the letter's path generator method
        generator_method = getattr(LetterPathGenerator, f"_generate_{letter}", None)
        if generator_method is None:
            # Default to a simple vertical line if letter not implemented
            return LetterPathGenerator._generate_default(center, size)
            
        return generator_method(center, size)
    
    @staticmethod
    def _generate_default(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate a default vertical line for unimplemented letters"""
        x, y = center
        half_height = size // 2
        return [(x, y - half_height), (x, y + half_height)]
    
    @staticmethod
    def _generate_A(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for letter A"""
        x, y = center
        half_size = size // 2
        width = size * 0.8
        
        # Calculate points
        top = (x, y - half_size)
        bottom_left = (x - width//2, y + half_size)
        bottom_right = (x + width//2, y + half_size)
        middle_left = (x - width//4, y)
        middle_right = (x + width//4, y)
        
        # Return points in drawing order
        return [bottom_left, top, bottom_right, middle_left, middle_right]
    
    @staticmethod
    def _generate_B(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for letter B"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points
        top = (x - half_size//2, y - half_size)
        bottom = (x - half_size//2, y + half_size)
        middle = (x - half_size//2, y)
        
        # Calculate control points for curves
        top_curve = [
            (x, y - half_size),
            (x + width//2, y - half_size),
            (x + width//2, y - half_size//2),
            (x + width//2, y),
            (x, y)
        ]
        
        bottom_curve = [
            (x, y),
            (x + width//2, y),
            (x + width//2, y + half_size//2),
            (x + width//2, y + half_size),
            (x, y + half_size)
        ]
        
        return [top] + top_curve + [middle] + bottom_curve + [bottom]
    
    @staticmethod
    def _generate_C(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for letter C"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points for the curve
        points = []
        num_points = 12
        for i in range(num_points):
            angle = math.pi * (1.5 - i/(num_points-1))
            px = x + math.cos(angle) * width//2
            py = y + math.sin(angle) * half_size
            points.append((int(px), int(py)))
            
        return points
    
    @staticmethod
    def _generate_O(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for letter O"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points for the full circle
        points = []
        num_points = 20
        for i in range(num_points + 1):
            angle = 2 * math.pi * i/num_points
            px = x + math.cos(angle) * width//2
            py = y + math.sin(angle) * half_size
            points.append((int(px), int(py)))
            
        return points
    
    @staticmethod
    def _generate_I(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for letter I"""
        x, y = center
        half_size = size // 2
        width = size * 0.2
        
        # Calculate points
        top_left = (x - width, y - half_size)
        top_right = (x + width, y - half_size)
        bottom_left = (x - width, y + half_size)
        bottom_right = (x + width, y + half_size)
        middle_top = (x, y - half_size)
        middle_bottom = (x, y + half_size)
        
        return [top_left, top_right, middle_top, middle_bottom, bottom_left, bottom_right]
    
    @staticmethod
    def _generate_L(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for letter L"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points
        top = (x - width//2, y - half_size)
        middle = (x - width//2, y + half_size)
        right = (x + width//2, y + half_size)
        
        return [top, middle, right]
    
    @staticmethod
    def _generate_T(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for letter T"""
        x, y = center
        half_size = size // 2
        width = size * 0.8
        
        # Calculate points
        left = (x - width//2, y - half_size)
        right = (x + width//2, y - half_size)
        middle_top = (x, y - half_size)
        middle_bottom = (x, y + half_size)
        
        return [left, right, middle_top, middle_bottom]
    
    @staticmethod
    def _generate_E(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for letter E"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points
        top_left = (x - width//2, y - half_size)
        top_right = (x + width//2, y - half_size)
        middle_left = (x - width//2, y)
        middle_right = (x + width//2 * 0.8, y)
        bottom_left = (x - width//2, y + half_size)
        bottom_right = (x + width//2, y + half_size)
        
        return [top_left, top_right, top_left, middle_left, middle_right, middle_left, bottom_left, bottom_right] 