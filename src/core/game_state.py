import os
import json
import pygame
from src.config import Config

class GameState:
    """
    Manages the global state of the application, 
    including user progress and settings.
    """
    def __init__(self):
        self.current_game = None
        self.user_progress = self._load_progress()
        self.settings = self._load_settings()
        
    def _load_progress(self):
        """Load user progress from file or create default if not exists"""
        progress_path = os.path.join(Config.SAVE_DIRECTORY, "user_progress.json")
        
        if os.path.exists(progress_path):
            try:
                with open(progress_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading progress: {e}")
                return self._create_default_progress()
        else:
            return self._create_default_progress()
    
    def _create_default_progress(self):
        """Create default progress structure"""
        progress = {
            "games_completed": {},
            "accuracy_stats": {},
            "last_played": ""
        }
        
        # Initialize stats for all games
        for game in Config.IMPLEMENTED_GAMES + Config.COMING_SOON_GAMES:
            progress["games_completed"][game] = False
            progress["accuracy_stats"][game] = 0
            
        return progress
    
    def _load_settings(self):
        """Load application settings from file or create defaults"""
        settings_path = os.path.join(Config.SAVE_DIRECTORY, "settings.json")
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self._create_default_settings()
        else:
            return self._create_default_settings()
    
    def _create_default_settings(self):
        """Create default settings structure"""
        return {
            "volume": 0.7,
            "fullscreen": False,
            "show_tooltips": True,
            "default_brush_size": 1,  # Medium
            "default_brush_color": 0   # Black
        }
    
    def save_progress(self):
        """Save current progress to file"""
        progress_path = os.path.join(Config.SAVE_DIRECTORY, "user_progress.json")
        
        # Ensure directory exists
        os.makedirs(Config.SAVE_DIRECTORY, exist_ok=True)
        
        try:
            with open(progress_path, 'w') as f:
                json.dump(self.user_progress, f, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def save_settings(self):
        """Save current settings to file"""
        settings_path = os.path.join(Config.SAVE_DIRECTORY, "settings.json")
        
        # Ensure directory exists
        os.makedirs(Config.SAVE_DIRECTORY, exist_ok=True)
        
        try:
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def update_progress(self, game_name, completed=False, accuracy=None):
        """Update progress for a specific game"""
        if game_name in self.user_progress["games_completed"]:
            self.user_progress["games_completed"][game_name] = completed
            
        if accuracy is not None and game_name in self.user_progress["accuracy_stats"]:
            self.user_progress["accuracy_stats"][game_name] = accuracy
            
        self.user_progress["last_played"] = game_name
        self.save_progress()
            
    def set_current_game(self, game_name):
        """Set the currently active game"""
        self.current_game = game_name 