from typing import List, Tuple, Dict
import math

class NumberPathGenerator:
    """
    Utility class for generating paths for numbers.
    Each number is defined as a series of points that form its shape.
    """
    
    @staticmethod
    def generate_number_path(number: int, center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """
        Generate a path for a given number.
        
        Args:
            number: The number to generate a path for (0-9)
            center: The center point (x, y) for the number
            size: The size of the number
            
        Returns:
            List of points that form the number's path
        """
        # Get the number's path generator method
        generator_method = getattr(NumberPathGenerator, f"_generate_{number}", None)
        if generator_method is None:
            # Default to a simple vertical line if number not implemented
            return NumberPathGenerator._generate_default(center, size)
            
        return generator_method(center, size)
    
    @staticmethod
    def _generate_default(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate a default vertical line for unimplemented numbers"""
        x, y = center
        half_height = size // 2
        return [(x, y - half_height), (x, y + half_height)]
    
    @staticmethod
    def _generate_0(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for number 0"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points for the oval
        points = []
        num_points = 20
        for i in range(num_points + 1):
            angle = 2 * math.pi * i/num_points
            px = x + math.cos(angle) * width//2
            py = y + math.sin(angle) * half_size
            points.append((int(px), int(py)))
            
        return points
    
    @staticmethod
    def _generate_1(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for number 1"""
        x, y = center
        half_size = size // 2
        width = size * 0.3
        
        # Calculate points
        top_left = (x - width, y - half_size)
        top = (x, y - half_size)
        bottom = (x, y + half_size)
        bottom_left = (x - width, y + half_size)
        bottom_right = (x + width, y + half_size)
        
        return [top_left, top, bottom, bottom_left, bottom_right]
    
    @staticmethod
    def _generate_2(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for number 2"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points
        top_left = (x - width//2, y - half_size)
        top_right = (x + width//2, y - half_size)
        middle_right = (x + width//2, y)
        middle_left = (x - width//2, y)
        bottom_left = (x - width//2, y + half_size)
        bottom_right = (x + width//2, y + half_size)
        
        return [top_left, top_right, middle_right, middle_left, bottom_left, bottom_right]
    
    @staticmethod
    def _generate_3(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for number 3"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points
        top_left = (x - width//2, y - half_size)
        top_right = (x + width//2, y - half_size)
        middle = (x, y)
        bottom_left = (x - width//2, y + half_size)
        bottom_right = (x + width//2, y + half_size)
        
        return [top_left, top_right, middle, bottom_right, bottom_left]
    
    @staticmethod
    def _generate_4(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for number 4"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points
        top_left = (x - width//2, y - half_size)
        middle_left = (x - width//2, y)
        middle_right = (x + width//2, y)
        top_right = (x + width//2, y - half_size)
        bottom_right = (x + width//2, y + half_size)
        
        return [top_left, middle_left, middle_right, top_right, bottom_right]
    
    @staticmethod
    def _generate_5(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for number 5"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points
        top_right = (x + width//2, y - half_size)
        top_left = (x - width//2, y - half_size)
        middle_left = (x - width//2, y)
        middle_right = (x + width//2, y)
        bottom_right = (x + width//2, y + half_size)
        bottom_left = (x - width//2, y + half_size)
        
        return [top_right, top_left, middle_left, middle_right, bottom_right, bottom_left]
    
    @staticmethod
    def _generate_6(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for number 6"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points for the bottom circle
        points = []
        num_points = 12
        for i in range(num_points + 1):
            angle = math.pi * (1 + i/num_points)
            px = x + math.cos(angle) * width//2
            py = y + math.sin(angle) * half_size//2
            points.append((int(px), int(py + half_size//2)))
            
        # Add the stem
        top = (x - width//2, y - half_size)
        points = [top] + points
        
        return points
    
    @staticmethod
    def _generate_7(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for number 7"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points
        top_left = (x - width//2, y - half_size)
        top_right = (x + width//2, y - half_size)
        bottom = (x - width//4, y + half_size)
        
        return [top_left, top_right, bottom]
    
    @staticmethod
    def _generate_8(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for number 8"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        quarter_size = size // 4
        
        # Calculate points for two circles
        points = []
        num_points = 12
        
        # Top circle
        for i in range(num_points + 1):
            angle = 2 * math.pi * i/num_points
            px = x + math.cos(angle) * width//2
            py = y - quarter_size + math.sin(angle) * quarter_size
            points.append((int(px), int(py)))
            
        # Bottom circle
        for i in range(num_points + 1):
            angle = 2 * math.pi * i/num_points
            px = x + math.cos(angle) * width//2
            py = y + quarter_size + math.sin(angle) * quarter_size
            points.append((int(px), int(py)))
            
        return points
    
    @staticmethod
    def _generate_9(center: Tuple[int, int], size: int) -> List[Tuple[int, int]]:
        """Generate path for number 9"""
        x, y = center
        half_size = size // 2
        width = size * 0.6
        
        # Calculate points for the top circle
        points = []
        num_points = 12
        for i in range(num_points + 1):
            angle = math.pi * (2 - i/num_points)
            px = x + math.cos(angle) * width//2
            py = y + math.sin(angle) * half_size//2
            points.append((int(px), int(py - half_size//2)))
            
        # Add the stem
        bottom = (x + width//2, y + half_size)
        points.append(bottom)
        
        return points 