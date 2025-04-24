# CursorDraw

A comprehensive mouse cursor training application designed to improve users' drawing speed, accuracy, and control through engaging exercises and games.

## Phase 1 Implementation

This initial phase includes:
- Main menu system
- Core whiteboard functionality
- Whiteboard Playground game

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Pygame library

### Installation

1. Clone the repository:
```
git clone https://github.com/Omar7001-B/cursor-draw.git
cd cursor-draw
```

2. Install the required packages:
```
pip install -r requirements.txt
```

### Running the Application

From the project root directory, run:
```
python src/main.py
```

## Features

### Main Menu
- Access to all games and features
- Visual indicators for implemented vs. coming soon games

### Whiteboard Playground
- Free-drawing mode with smooth line interpolation
- Color selection (black, red, blue)
- Brush size options (small, medium, large)
- Eraser tool
- Canvas clearing with animation
- Image saving capability

## Project Structure

```
cursordraw/
├── src/
│   ├── main.py                # Application entry point
│   ├── config.py              # Global configuration
│   ├── core/
│   │   ├── whiteboard.py      # Reusable whiteboard component
│   │   ├── drawing_engine.py  # Drawing mechanics
│   │   ├── ui_manager.py      # UI components manager
│   │   └── game_state.py      # Game state management
│   ├── screens/
│   │   ├── main_menu.py       # Main menu screen
│   │   └── coming_soon.py     # Template for unimplemented games
│   ├── games/
│   │   └── playground.py      # Whiteboard Playground
│   └── assets/                # Font files, images, etc.
├── data/                      # User progress and saved drawings
├── tests/                     # Test files
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Future Development

Future phases will include:
- Draw Basic Shapes game
- Letter and Number Tracing games
- Sentence Tracing
- Whiteboard to Text conversion

## License

This project is licensed under the MIT License - see the LICENSE file for details. 