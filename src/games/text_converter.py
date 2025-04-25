import pygame
import pytesseract
import pyperclip
from PIL import Image
import io

from src.core.game_state import GameState
from src.core.whiteboard import Whiteboard
from src.core.ui_manager import Button
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY

class TextConverterGame(GameState):
    def __init__(self, screen, game_manager):
        super().__init__(screen, game_manager)
        self.whiteboard = Whiteboard(0, 50, SCREEN_WIDTH, SCREEN_HEIGHT - 150, show_controls=False)
        self.recognized_text = ""
        self.text_display_rect = pygame.Rect(10, SCREEN_HEIGHT - 90, SCREEN_WIDTH - 120, 80)
        self.copy_button = Button(SCREEN_WIDTH - 110, SCREEN_HEIGHT - 70, 100, 40, "Copy", self.copy_text)
        self.back_button = Button(10, 10, 100, 30, "Back", self.go_back)
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 32)

        # Tesseract path might need configuration depending on the system
        # Uncomment and set path if necessary:
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def handle_event(self, event):
        if self.whiteboard.handle_event(event):
            # If whiteboard handled mouse up after drawing, trigger OCR
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.whiteboard.drawing_engine.is_drawing:
                 # Ensure drawing is finished before processing
                 self.whiteboard.drawing_engine.stop_drawing()
                 self.recognize_drawing()
            return True
            
        if self.copy_button.handle_event(event):
            return True
        if self.back_button.handle_event(event):
            return True
        return False

    def update(self, dt):
        self.whiteboard.update(dt)
        self.copy_button.update(dt)
        self.back_button.update(dt)

    def draw(self):
        self.screen.fill(WHITE)
        self.whiteboard.draw()

        # Draw text display area
        pygame.draw.rect(self.screen, GRAY, self.text_display_rect, 2, border_radius=5)
        text_surface = self.font.render(self.recognized_text, True, BLACK)
        text_rect = text_surface.get_rect(topleft=(self.text_display_rect.x + 10, self.text_display_rect.y + 10))
        self.screen.blit(text_surface, text_rect)

        # Draw Header
        header_surface = self.large_font.render("Whiteboard to Text", True, BLACK)
        self.screen.blit(header_surface, (SCREEN_WIDTH // 2 - header_surface.get_width() // 2, 10))

        # Draw Instruction
        instruction_surface = self.font.render("Draw text on the whiteboard. Release mouse to recognize.", True, BLACK)
        self.screen.blit(instruction_surface, (10, SCREEN_HEIGHT - 115))

        self.copy_button.draw(self.screen)
        self.back_button.draw(self.screen)

    def recognize_drawing(self):
        try:
            # Get the drawing surface from the engine
            drawing_surface = self.whiteboard.drawing_engine.drawing_surface
            
            # Convert Pygame surface to PIL Image
            img_str = pygame.image.tostring(drawing_surface, 'RGB')
            img_pil = Image.frombytes('RGB', drawing_surface.get_size(), img_str)
            
            # Perform OCR using pytesseract
            # Improve accuracy by specifying language and page segmentation mode if needed
            # config='--psm 6' often works well for blocks of text
            self.recognized_text = pytesseract.image_to_string(img_pil, config='--psm 6').strip()
            print(f"Recognized Text: {self.recognized_text}") # For debugging

        except Exception as e:
            self.recognized_text = f"OCR Error: {e}"
            print(f"Error during OCR: {e}")

    def copy_text(self):
        if self.recognized_text:
            pyperclip.copy(self.recognized_text)
            print("Text copied to clipboard!") # Optional feedback
            # Maybe add visual feedback like button text change briefly

    def go_back(self):
        self.game_manager.change_state('main_menu') 