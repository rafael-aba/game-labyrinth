# pygame values
LENGTH = 512
RESOLUTION = (LENGTH,LENGTH)
ORIGIN = (0,0)

# color values
RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
BLACK = (0,0,0)
WHITE = (255,255,255)
LIGHT_GREEN = (90,238,90)
DARK_GREEN = (1,50,32)

# hero values
IDLE = 0
WALK = 1

UP = -1
DOWN = 1
RIGHT = 2
LEFT = -2

# maze values
WALL = (0,0,0,255)
FLOOR = (255,255,255,255)
ENTRANCE = (*RED,255)
EXIT = (*BLUE,255)

# maze generator values
URL = "https://mazegenerator.net/"
SHAPE_DROPDOWN = "ShapeDropDownList"
GENERATE_BUTTON = "GenerateButton"
MAZE_IMG = "MazeDisplay"

# game difficulty values
EASY = 0
NORMAL = 1
HARD = 2
RANKING = 3

# game states
LOADING = 0
MENU = 1
RUNNING = 2
WIN = 3
LOSE = 4