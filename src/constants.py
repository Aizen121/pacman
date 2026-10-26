

FONT = "assets/Press_Start_2P/PressStart2P-Regular.ttf"
LOGO = "assets/pacman_logo.png"
FULLSCREEN = True  # False: a window of 90 % of the screen instead
# DEFAULT = [] (default config)
TILE = 50  # largest cell size in pixels; big mazes get smaller cells
TOP, RIGHT, BOTTOM, LEFT = 1, 2, 4, 8
WALL_COLOR = (45, 75, 255)  # arcade neon blue
WALL = 3  # wall thickness for the largest cells
MAZE_LEFT = 300  # the HUD uses the screen left of this x
MARGIN = 25  # free space around the maze, in pixels
LOGO_COLOR = (255, 253, 208)  # the "42" cells
PACMAN_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 253, 208)
BG_COLOR = (8, 8, 28)  # night blue
PACGUM_COLOR = (255, 184, 174)  # arcade peach
HIGHLIGHT_COLOR = (255, 200, 40)  # amber, like the logo
DIM_COLOR = (130, 130, 170)  # hints
# Mouth openings of the Pac-Man frames, in degrees: closed, half, wide open
MOUTH_ANGLES = (0, 45, 90)
# Direction of the mouth, in degrees (the screen y axis points down)
FACING_ANGLES = {"right": 0, "down": 90, "left": 180, "up": 270}
# Body color of each ghost, as in the arcade game
GHOST_COLORS = {"blinky": (255, 0, 0), "pinky": (255, 184, 255),
                "inky": (0, 255, 255), "clyde": (255, 184, 82)}
EYE_COLOR = (255, 255, 255)
PUPIL_COLOR = (33, 33, 222)
# Edible ghosts are blue, and flash white in their last seconds
FRIGHT_COLOR = (33, 33, 255)
FLASH_COLOR = (255, 255, 255)
FLASH_TIME = 2.0  # seconds of flashing before a ghost is dangerous again
