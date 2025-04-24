import pygame
import os
from src.config import Config

class Button:
    """A clickable button with hover effects"""
    def __init__(self, x, y, width, height, text, callback=None, font_size=None, 
                 bg_color=Config.LIGHT_GRAY, hover_color=Config.GRAY, text_color=Config.BLACK,
                 disabled=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font_size = font_size or Config.FONT_SMALL
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.disabled = disabled
        self.hovered = False
        
    def draw(self, surface):
        """Draw the button on the given surface"""
        # Determine color based on state
        if self.disabled:
            color = Config.DARK_GRAY
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.bg_color
            
        # Draw button background
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, Config.BLACK, self.rect, 2)  # Border
        
        # Draw button text
        font = pygame.font.SysFont(None, self.font_size)
        text_surf = font.render(self.text, True, self.text_color if not self.disabled else Config.GRAY)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        """Update the button's hover state"""
        if not self.disabled:
            self.hovered = self.rect.collidepoint(mouse_pos)
        
    def handle_event(self, event):
        """Handle mouse events on the button"""
        if self.disabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.hovered:
                if self.callback:
                    self.callback()
                return True
        return False
        
class Label:
    """A text label"""
    def __init__(self, x, y, text, font_size=None, color=Config.BLACK, centered=False):
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size or Config.FONT_SMALL
        self.color = color
        self.centered = centered
        
    def draw(self, surface):
        """Draw the label on the given surface"""
        font = pygame.font.SysFont(None, self.font_size)
        text_surf = font.render(self.text, True, self.color)
        if self.centered:
            text_rect = text_surf.get_rect(center=(self.x, self.y))
        else:
            text_rect = text_surf.get_rect(topleft=(self.x, self.y))
        surface.blit(text_surf, text_rect)
        
class Dialog:
    """A dialog box with message and confirm/cancel buttons"""
    def __init__(self, screen, message, confirm_callback=None, cancel_callback=None):
        self.screen = screen
        self.message = message
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback
        
        # Create dialog rectangle
        width, height = 400, 200
        screen_width, screen_height = screen.get_size()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.rect = pygame.Rect(x, y, width, height)
        
        # Create buttons
        button_y = y + height - 70
        self.confirm_button = Button(
            x + width//4 - Config.BUTTON_WIDTH//2, 
            button_y,
            Config.BUTTON_WIDTH//2, 
            Config.BUTTON_HEIGHT//2,
            "Yes", 
            self.confirm,
            bg_color=Config.GREEN
        )
        
        self.cancel_button = Button(
            x + 3*width//4 - Config.BUTTON_WIDTH//2,
            button_y,
            Config.BUTTON_WIDTH//2,
            Config.BUTTON_HEIGHT//2,
            "No",
            self.cancel,
            bg_color=Config.RED
        )
        
    def draw(self):
        """Draw the dialog box"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw dialog background
        pygame.draw.rect(self.screen, Config.WHITE, self.rect)
        pygame.draw.rect(self.screen, Config.BLACK, self.rect, 2)  # Border
        
        # Draw message
        font = pygame.font.SysFont(None, Config.FONT_MEDIUM)
        lines = self.message.split('\n')
        for i, line in enumerate(lines):
            text_surf = font.render(line, True, Config.BLACK)
            text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.y + 60 + i * 30))
            self.screen.blit(text_surf, text_rect)
        
        # Draw buttons
        self.confirm_button.draw(self.screen)
        self.cancel_button.draw(self.screen)
        
    def update(self, mouse_pos):
        """Update button hover states"""
        self.confirm_button.update(mouse_pos)
        self.cancel_button.update(mouse_pos)
        
    def handle_event(self, event):
        """Handle events for the dialog"""
        # Handle button events
        if self.confirm_button.handle_event(event) or self.cancel_button.handle_event(event):
            return True
        return False
        
    def confirm(self):
        """Handle confirm button click"""
        if self.confirm_callback:
            self.confirm_callback()
            
    def cancel(self):
        """Handle cancel button click"""
        if self.cancel_callback:
            self.cancel_callback()
            
class GridLayout:
    """Grid layout for organizing buttons/items in rows and columns"""
    def __init__(self, x, y, item_width, item_height, columns, h_spacing=10, v_spacing=10):
        self.x = x
        self.y = y
        self.item_width = item_width
        self.item_height = item_height
        self.columns = columns
        self.h_spacing = h_spacing
        self.v_spacing = v_spacing
        self.items = []
        
    def add_item(self, item):
        """Add an item to the grid"""
        self.items.append(item)
        self._reposition_items()
        
    def _reposition_items(self):
        """Update positions of all items in the grid"""
        for i, item in enumerate(self.items):
            row = i // self.columns
            col = i % self.columns
            
            x = self.x + col * (self.item_width + self.h_spacing)
            y = self.y + row * (self.item_height + self.v_spacing)
            
            # Update position based on the type of item
            if hasattr(item, 'rect'):
                item.rect.x = x
                item.rect.y = y
            elif hasattr(item, 'x') and hasattr(item, 'y'):
                item.x = x
                item.y = y
                
    def draw(self, surface):
        """Draw all items in the grid"""
        for item in self.items:
            if hasattr(item, 'draw'):
                item.draw(surface)
                
    def update(self, mouse_pos):
        """Update all items in the grid"""
        for item in self.items:
            if hasattr(item, 'update'):
                item.update(mouse_pos)
                
    def handle_event(self, event):
        """Handle events for all items in the grid"""
        for item in self.items:
            if hasattr(item, 'handle_event'):
                if item.handle_event(event):
                    return True
        return False 