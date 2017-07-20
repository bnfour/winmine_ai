# constant values file
# window titles
WINMINE_APP_TITLE = "Minesweeper"
GAME_LOST = "Game Lost"
GAME_WON = "Game Won"
# cell statuses that are not numbers
UNKNOWN = -1
FLAGGED = -2
# cell size in pixels
CELL_SIZE = 18
# left top right down game field offsets from entire window screenshot
WINDOW_BORDERS = (38, 80, -37, -40)
# mouse buttons constants
MOUSE1 = 1
MOUSE2 = 2
# used for comparing float fail chances
DELTA = 0.001
# delays in seconds
TINY_SLEEP_TIME = 0.01
WAIT_FOR_RESULTS_TIME = 0.4
# winapi constants
WM_KEYDOWN = 0x0100
VK_RETURN = 0x0d
GW_ENABLEDPOPUP = 6
# field recognition settings
# amount to crop from each side to get central pixels 
CROP = 7
# red color
FLAG_RED = (255, 0, 0)
# found empirically
COLOR_DISTANCE_THRESHOLD = 20
# sampled from a few test pictures, first one is color specific for number 1 and so on up to 8
CELL_COLORS = ((64, 80, 190), (29, 104, 2), (174, 5, 7), (1, 2, 128),
               (130, 1, 2), (7, 121, 120), (175, 5, 6), (174, 4, 7))
# also found empirically
VALUE_THRESHOLD = 10 / 255
