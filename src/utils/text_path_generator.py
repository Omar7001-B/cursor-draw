from typing import List, Tuple, Dict
import pygame
import math
from src.utils.letter_path_generator import LetterPathGenerator

class TextPathGenerator:
    """
    Utility class for generating paths for text sentences.
    Converts text into a series of points that form the letters.
    """
    
    @staticmethod
    def generate_text_path(text: str, start_pos: Tuple[int, int], size: int, line_spacing: int = 1.5) -> List[List[Tuple[int, int]]]:
        """
        Generate paths for a text string.
        
        Args:
            text: The text to generate paths for
            start_pos: The starting position (x, y) for the text
            size: The size (height) of the letters
            line_spacing: Line spacing multiplier (1.5 means 1.5 times the letter height)
            
        Returns:
            List of paths, where each path is a list of points
        """
        x, y = start_pos
        paths = []
        letter_width = size * 0.8  # Approximate width of each letter
        space_width = letter_width * 0.5  # Width of space between letters
        word_spacing = letter_width  # Width of space between words
        
        # Split text into lines based on width
        lines = TextPathGenerator._split_text_into_lines(text, letter_width, word_spacing, 800)  # Assuming max width of 800px
        
        current_y = y
        for line in lines:
            current_x = x
            
            for word in line.split():
                for i, char in enumerate(word):
                    if char.isspace():
                        current_x += space_width
                        continue
                        
                    # Generate path for the character
                    char_path = LetterPathGenerator.generate_letter_path(
                        char,
                        (current_x + letter_width/2, current_y),
                        size
                    )
                    paths.append(char_path)
                    
                    # Move to next character position
                    current_x += letter_width + space_width
                
                # Add space between words
                current_x += word_spacing - space_width  # Subtract one space_width since we already added it
            
            # Move to next line
            current_y += size * line_spacing
            
        return paths
    
    @staticmethod
    def _split_text_into_lines(text: str, letter_width: float, word_spacing: float, max_width: int) -> List[str]:
        """Split text into lines that fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            # Calculate width of word including spacing
            word_width = len(word) * (letter_width + word_spacing/2)
            
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width + word_spacing
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(" ".join(current_line))
            
        return lines
    
    @staticmethod
    def draw_text_outline(surface: pygame.Surface, paths: List[List[Tuple[int, int]]], 
                         color: Tuple[int, int, int], width: int = 2, alpha: int = 100):
        """
        Draw the text outline on a surface.
        
        Args:
            surface: Pygame surface to draw on
            paths: List of paths (each path is a list of points)
            color: RGB color tuple
            width: Line width
            alpha: Transparency (0-255)
        """
        # Create a temporary surface for alpha blending
        temp_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Draw each path
        for path in paths:
            if len(path) < 2:
                continue
                
            # Draw the path
            pygame.draw.lines(temp_surface, (*color, alpha), False, path, width)
        
        # Blit the temporary surface onto the main surface
        surface.blit(temp_surface, (0, 0)) 