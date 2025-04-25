import pygame
import pytesseract
import pyperclip
from PIL import Image
import io
import threading # Import threading

from src.core.game_state import GameState
from src.core.whiteboard import Whiteboard
from src.core.ui_manager import Button
from src.config import Config

# Define custom event type
OCR_COMPLETE = pygame.USEREVENT + 1

class TextConverterGame(GameState):
    def __init__(self, screen, game_manager):
        super().__init__(screen, game_manager)
        # Define position and size as tuples
        whiteboard_pos = (0, 50)
        whiteboard_size = (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT - 150)
        # Pass tuples to Whiteboard constructor
        self.whiteboard = Whiteboard(screen, whiteboard_pos, whiteboard_size, show_controls=False)
        self.recognized_text = ""
        self.text_display_rect = pygame.Rect(10, Config.SCREEN_HEIGHT - 90, Config.SCREEN_WIDTH - 120, 80)
        self.copy_button = Button(Config.SCREEN_WIDTH - 110, Config.SCREEN_HEIGHT - 70, 100, 40, "Copy", self.copy_text)
        self.back_button = Button(10, 10, 100, 30, "Back", self.go_back)
        self.clear_button = Button(120, 10, 100, 30, "Clear", self.clear_whiteboard_and_text)
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 32)
        self.processing = False # Flag to indicate OCR is running

        # Tesseract path might need configuration depending on the system
        # Uncomment and set path if necessary:
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def handle_event(self, event):
        # Handle custom OCR complete event first
        if event.type == OCR_COMPLETE:
             self.recognized_text = event.result
             self.processing = False
             print(f"OCR Event Received: {event.result}")
             return True 

        # Handle buttons first (allow even if processing)
        button_handled = False
        if self.copy_button.handle_event(event):
            button_handled = True
        if self.back_button.handle_event(event):
            button_handled = True 
        if self.clear_button.handle_event(event):
             button_handled = True
             
        if button_handled:
             return True

        # Always handle whiteboard events (drawing should not be blocked)
        whiteboard_handled = self.whiteboard.handle_event(event)

        # Trigger OCR *only* if drawing stopped AND OCR is not already processing
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if whiteboard_handled and not self.whiteboard.drawing_engine.is_drawing: 
                if not self.processing: # Only start if not already processing
                    self.recognize_drawing() 
                else:
                     print("OCR already in progress, skipping new request.") # Optional debug msg

        return whiteboard_handled # Return True if whiteboard handled the event

    def update(self, dt):
        self.whiteboard.update(dt)
        # Get mouse position for UI elements
        mouse_pos = pygame.mouse.get_pos()
        self.copy_button.update(mouse_pos)
        self.back_button.update(mouse_pos)
        self.clear_button.update(mouse_pos)
        # Return None as this state doesn't trigger changes via update
        return None

    def draw(self):
        self.screen.fill(Config.WHITE)
        self.whiteboard.render()

        # Draw text display area
        pygame.draw.rect(self.screen, Config.GRAY, self.text_display_rect, 2, border_radius=5)
        
        display_text = self.recognized_text
        # Show processing indicator if OCR is running
        if self.processing: 
             display_text = "Processing..."

        # Wrap and render the text (result, error, or processing indicator)
        lines = self.wrap_text(display_text, self.font, self.text_display_rect.width - 20) # Use helper
        y_offset = self.text_display_rect.y + 10
        for line in lines:
             text_surface = self.font.render(line, True, Config.BLACK)
             # Ensure text stays within the display rect vertically
             if y_offset + self.font.get_linesize() <= self.text_display_rect.bottom - 10:
                  self.screen.blit(text_surface, (self.text_display_rect.x + 10, y_offset))
                  y_offset += self.font.get_linesize()
             else:
                  break # Stop drawing lines if they overflow the box

        # Draw Header
        header_surface = self.large_font.render("Whiteboard to Text", True, Config.BLACK)
        self.screen.blit(header_surface, (Config.SCREEN_WIDTH // 2 - header_surface.get_width() // 2, 10))

        # Draw Instruction
        instruction_surface = self.font.render("Draw text on the whiteboard. Release mouse to recognize.", True, Config.BLACK)
        self.screen.blit(instruction_surface, (10, Config.SCREEN_HEIGHT - 115))

        self.copy_button.draw(self.screen)
        self.back_button.draw(self.screen)
        self.clear_button.draw(self.screen)

    def _perform_ocr(self, surface_copy):
        """Function to run OCR in a background thread."""
        ocr_result = ""
        try:
            # Convert Pygame surface to PIL Image
            img_str = pygame.image.tostring(surface_copy, 'RGB')
            img_pil = Image.frombytes('RGB', surface_copy.get_size(), img_str)

            # Perform OCR
            recognized = pytesseract.image_to_string(img_pil, config='--psm 6').strip()
            
            if not recognized:
                 ocr_result = "(No text detected)"
            else:
                 ocr_result = recognized
                 
            print(f"OCR Thread Recognized Text: {ocr_result}") # For debugging

        except pytesseract.TesseractNotFoundError:
             ocr_result = "OCR Error: Tesseract not found. Check installation/path."
             print("OCR Thread Error: Tesseract not found.")
        except Exception as e:
            ocr_result = f"OCR Error: {type(e).__name__}"
            print(f"OCR Thread Error: {e}")
        finally:
            # Post custom event with the result
            pygame.event.post(pygame.event.Event(OCR_COMPLETE, {'result': ocr_result}))

    def recognize_drawing(self):
        if self.processing: # Prevent overlapping calls
             return
             
        self.processing = True
        self.recognized_text = "Processing..." # Set indicator text

        # Get a *copy* of the surface to pass to the thread
        # This avoids potential issues with the main thread modifying the surface
        surface_to_process = self.whiteboard.drawing_engine.surface.copy()

        # Create and start the OCR thread
        ocr_thread = threading.Thread(target=self._perform_ocr, args=(surface_to_process,))
        ocr_thread.start()
        # We don't join() the thread here, as that would block
        # The result will come back via the OCR_COMPLETE event

    def copy_text(self):
        # Only copy if not processing and text is not an error/indicator message
        if not self.processing and self.recognized_text and not self.recognized_text.startswith("OCR Error") and not self.recognized_text.startswith("("):
            pyperclip.copy(self.recognized_text)
            print("Text copied to clipboard!")
        else:
             print("Nothing valid to copy.")

    def go_back(self):
        self.game_manager.change_state('main_menu')

    def clear_whiteboard_and_text(self):
        """Clears the whiteboard drawing and the recognized text."""
        print("Clear button clicked - attempting to clear engine canvas.")
        engine = self.whiteboard.drawing_engine
        engine.clear_canvas(animated=False) 
        
        # Force a refresh/redraw or state update within whiteboard?
        # Let's try resetting the size - might trigger internal refresh (unlikely needed)
        self.whiteboard.size = self.whiteboard.size 
        
        self.recognized_text = ""
        self.processing = False

    # Helper function for text wrapping (add this method to the class)
    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            # Handle potential newlines within the text itself
            sub_words = word.split('\n')
            for i, sub_word in enumerate(sub_words):
                test_line = current_line + sub_word + " "
                # Check width
                if font.size(test_line.strip())[0] <= max_width:
                    current_line = test_line
                else:
                    # Word doesn't fit, start new line
                    lines.append(current_line.strip())
                    current_line = sub_word + " "
                # If there was a newline, force a line break after the sub_word
                if i < len(sub_words) - 1:
                     lines.append(current_line.strip())
                     current_line = "" 
        lines.append(current_line.strip())
        return lines 