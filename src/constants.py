

FONT = "assets/Press_Start_2P/PressStart2P-Regular.ttf"
LOGO = "assets/pacman_logo.png"
PACMAN = "assets/pacman.png"
# DEFAULT = [] (default config)
TILE = 50  # largest cell size in pixels; big mazes get smaller cells
TOP, RIGHT, BOTTOM, LEFT = 1, 2, 4, 8
WALL_COLOR = (255, 253, 208)
WALL = 3  # wall thickness for the largest cells
MAZE_LEFT = 300  # the HUD uses the screen left of this x
MARGIN = 25  # free space around the maze, in pixels
LOGO_COLOR = (25, 25, 166)
PACMAN_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 253, 208)
# Mouth openings of the Pac-Man frames, in degrees: closed, half, wide open
MOUTH_ANGLES = (0, 45, 90)
# Direction of the mouth, in degrees (the screen y axis points down)
FACING_ANGLES = {"right": 0, "down": 90, "left": 180, "up": 270}
# Body color of each ghost, as in the arcade game
GHOST_COLORS = {"blinky": (255, 0, 0), "pinky": (255, 184, 255),
                "inky": (0, 255, 255), "clyde": (255, 184, 82)}
EYE_COLOR = (255, 255, 255)
PUPIL_COLOR = (33, 33, 222)
