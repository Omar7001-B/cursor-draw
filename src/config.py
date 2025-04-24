class Config:
    # Screen settings
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768
    FPS = 60
    
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (50, 50, 50)
    
    # Font settings
    FONT_SMALL = 24
    FONT_MEDIUM = 36
    FONT_LARGE = 48
    
    # Button settings
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 60
    BUTTON_PADDING = 20
    
    # Whiteboard settings
    BRUSH_SIZES = [5, 10, 15]  # Small, Medium, Large
    BRUSH_COLORS = [BLACK, RED, BLUE]
    ERASER_SIZE = 20
    
    # File paths
    SAVE_DIRECTORY = "data"
    FONT_DIRECTORY = "src/assets/fonts"
    
    # Game state settings
    IMPLEMENTED_GAMES = ["Whiteboard Playground"]
    COMING_SOON_GAMES = [
        "Draw Basic Shapes",
        "Trace the Letter",
        "Trace the Number",
        "Trace the Sentence",
        "Whiteboard to Text"
    ] 