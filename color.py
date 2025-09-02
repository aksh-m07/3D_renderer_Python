import random

print("Color module imported")

# Color constants
MIN_COLOR = 0
MAX_COLOR = 3

# Color definitions (R, G, B values)
COLORS = [
    (1.0, 0.0, 0.0),  # Red
    (0.0, 1.0, 0.0),  # Green  
    (0.0, 0.0, 1.0),  # Blue
    (1.0, 1.0, 0.0),  # Yellow
    (1.0, 0.0, 1.0),  # Magenta
    (0.0, 1.0, 1.0),  # Cyan
    (1.0, 1.0, 1.0),  # White
    (0.5, 0.5, 0.5),  # Gray
]

print(f"Color module loaded: {len(COLORS)} colors available")
print(f"Color range: {MIN_COLOR} to {MAX_COLOR}")
