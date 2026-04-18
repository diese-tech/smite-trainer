# HUD region definitions for Smite 2 default UI layout.
#
# All values are fractions of the game client area (0.0 – 1.0).
# Measured from the top-left corner of the rendered game content.
#
# Tune these if your UI scale or resolution shifts elements around.
# Run main.py with --debug to see region outlines drawn on a capture.

REGIONS: dict[str, dict] = {
    # Green/red bar — right of character portrait, lower center
    "health_bar": {"x": 0.468, "y": 0.828, "w": 0.115, "h": 0.025},

    # Blue bar — directly below health bar
    "mana_bar":   {"x": 0.468, "y": 0.868, "w": 0.115, "h": 0.022},

    # Gold counter — bottom-left HUD, text row only (items are above this)
    "gold":       {"x": 0.018, "y": 0.955, "w": 0.080, "h": 0.030},

    # Match timer — top-center (MM:SS digits)
    "timer":      {"x": 0.452, "y": 0.018, "w": 0.096, "h": 0.048},
}
