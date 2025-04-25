class Config:
    # Screen settings
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768
    FPS = 60
    
    # Base dimensions for relative calculations
    BASE_WIDTH = 1024
    BASE_HEIGHT = 768
    
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
    IMPLEMENTED_GAMES = [
        "Whiteboard Playground",
        "Draw Basic Shapes",
        "Trace the Letter",
        "Trace the Number",
        "Trace the Sentence",
        "Whiteboard to Text"
    ]
    COMING_SOON_GAMES = [
        # No games coming soon currently
    ]
    
    @classmethod
    def scale_width(cls, width):
        """Scale a width value based on current screen width"""
        return int(width * cls.SCREEN_WIDTH / cls.BASE_WIDTH)
    
    @classmethod
    def scale_height(cls, height):
        """Scale a height value based on current screen height"""
        return int(height * cls.SCREEN_HEIGHT / cls.BASE_HEIGHT)
    
    @classmethod
    def scale_font(cls, size):
        """Scale a font size based on screen dimensions"""
        # Use the smaller of the two scale factors to ensure text fits
        scale_factor = min(cls.SCREEN_WIDTH / cls.BASE_WIDTH, cls.SCREEN_HEIGHT / cls.BASE_HEIGHT)
        return int(size * scale_factor)
    
    @classmethod
    def get_scaled_button_dimensions(cls):
        """Get scaled button dimensions"""
        return (
            cls.scale_width(cls.BUTTON_WIDTH),
            cls.scale_height(cls.BUTTON_HEIGHT)
        )
    
    @classmethod
    def get_scaled_font_sizes(cls):
        """Get scaled font sizes"""
        return {
            'small': cls.scale_font(cls.FONT_SMALL),
            'medium': cls.scale_font(cls.FONT_MEDIUM),
            'large': cls.scale_font(cls.FONT_LARGE)
        } 