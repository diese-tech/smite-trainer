# HUD region definitions for Smite 2 default UI layout.
#
# All values are fractions of the game client area (0.0 – 1.0).
# Measured from the top-left corner of the rendered game content.
#
# Tune these if your UI scale or resolution shifts elements around.
# Run main.py with --debug to see region outlines drawn on a capture.

REGIONS: dict[str, dict] = {
    # Green/red bar — lower center of screen
    "health_bar": {"x": 0.432, "y": 0.795, "w": 0.136, "h": 0.028},

    # Blue bar — just below health bar
    "mana_bar":   {"x": 0.432, "y": 0.830, "w": 0.136, "h": 0.018},

    # Gold counter — bottom-left HUD (yellow digits)
    "gold":       {"x": 0.018, "y": 0.878, "w": 0.085, "h": 0.058},

    # Match timer — top-center (MM:SS digits)
    "timer":      {"x": 0.452, "y": 0.018, "w": 0.096, "h": 0.048},
}
