# utility functions

import win32gui, win32api, win32con
from PIL import ImageGrab
from colorsys import rgb_to_hsv
from math import sqrt
from winmine_const import WINMINE_APP_TITLE, CELL_SIZE, WINDOW_BORDERS, \
                          UNKNOWN, FLAGGED, GW_ENABLEDPOPUP, CELL_COLORS, CROP, \
                          VALUE_THRESHOLD, FLAG_RED, COLOR_DISTANCE_THRESHOLD


# returns whether an element belongs to all sets provided
def in_all(element, list_of_sets):
    for s in list_of_sets:
        if element not in s:
            return False
    else:
        return True


# tries to find game window by its title
def find_minesweeper_window():
    window_handle = win32gui.FindWindow(None, WINMINE_APP_TITLE)
    if window_handle != 0:
        return window_handle
    else:
        raise RuntimeError(f"Unable to find window \"{WINMINE_APP_TITLE}\"")


# moves window to top-left corner of main monitor for predictable coordinates
def resize_window(handle):
    win32gui.MoveWindow(handle, 0, 0, 100, 100, True)


# brings window to top
def topwindow(handle):
    win32gui.SetForegroundWindow(handle)


# takes a screenshot of given rect
def get_window_picture(handle, rect):
    topwindow(handle)
    screenshot = ImageGrab.grab(rect)
    return screenshot


# crops full window rect by predefined offsets
def crop_rect(full_window_rect):
    return tuple(i + j for i, j in zip(full_window_rect, WINDOW_BORDERS))


# estimates field size in cells
def size_guess(picture):
    x, y = picture.size
    return ((x - 1) // CELL_SIZE, (y - 1) // CELL_SIZE)


# moves the mouse and sends click events
def mouse_click(x, y, button=1):
    if button == 1:
        up_event = win32con.MOUSEEVENTF_LEFTUP
        down_event = win32con.MOUSEEVENTF_LEFTDOWN
    elif button == 2:
        up_event = win32con.MOUSEEVENTF_RIGHTUP
        down_event = win32con.MOUSEEVENTF_RIGHTDOWN
    else:
        raise ValueError(f"Unknown mouse button {button}: 1 for left, 2 for right")

    w = win32api.GetSystemMetrics(0)
    h = win32api.GetSystemMetrics(1)

    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE,
                         int(x / w * 65535.0), int(y / h * 65535.0))
    win32api.mouse_event(down_event, x, y, 0, 0)
    win32api.mouse_event(up_event, x, y, 0, 0)


# converts field coordinates to on-screen coordinates
def resolve_field_coords(x, y, window_rect):
    left, top, *whatever = window_rect
    return tuple(int(i + CELL_SIZE * (j + 0.5)) for i, j in zip((left, top), (x, y)))


# click on cell given by its field coordinates
def field_click(x, y, window_rect, button=1):
    screen_x, screen_y = resolve_field_coords(x, y, window_rect)
    mouse_click(screen_x, screen_y, button)


def process_field_image(picture, field):
    w = len(field[0])
    h = len(field)

    for x in range(w):
        # for whatever reason, one column is one pixel wider than others
        # the following code compensates for that
        if w % 2 == 0:
            wide_x = (w // 2) - 1
        else:
            wide_x = w // 2

        if x < wide_x:
            left = CELL_SIZE * x
            right = left + CELL_SIZE
        elif x == wide_x:
            left = CELL_SIZE * x
            right = left + CELL_SIZE + 1
        else:
            left = CELL_SIZE * x + 1
            right = left + CELL_SIZE

        for y in range(h):
            # if cell is still unknown
            if field[y][x].content == UNKNOWN:
                # also for whatever esoteric reason, one row is one pixel taller
                wide_y = h // 2

                if y < wide_y:
                    top = CELL_SIZE * y
                    bottom = top + CELL_SIZE
                elif y == wide_y:
                    top = CELL_SIZE * y
                    bottom = top + CELL_SIZE + 1
                else:
                    top = CELL_SIZE * y + 1
                    bottom = top + CELL_SIZE
                # get a picture of a tested cell
                cell_to_test = picture.copy().crop((left, top, right, bottom))
                c_w, c_h = cell_to_test.size
                # check out its top left pixel
                r, g, b = cell_to_test.getpixel((0, 0))
                hue, sat, val = rgb_to_hsv(r / 255, g / 255, b / 255)
                # crop it more to get central pixels
                cell_to_test = cell_to_test.crop((CROP, CROP, c_w - CROP, c_h - CROP))
                c_w, c_h = cell_to_test.size
                # get a list of unique colors at cell's center
                uniq_colors = set(j for i, j in cell_to_test.getcolors(c_w * c_h))

                # if color is dark enough, cell is opened
                if val <= VALUE_THRESHOLD:
                    # trying to find its value by comparing color distance from sampled ones
                    # finds minimum distance from cartesian product of each sampled color and each unique color
                    # 99999 is just a large enough value for initialisation
                    g_mins = tuple(99999 for i in range(len(CELL_COLORS)))
                    # there is a possibility we got exactly same color as the sampled one
                    # speeds up this part significally
                    quick = False
                    for c in uniq_colors:
                        # the shortcut
                        if c in CELL_COLORS:
                            content_to_set = CELL_COLORS.index(c) + 1
                            field[y][x].set_content(content_to_set)
                            quick = True
                            break
                        # else update minimums vector
                        mins = tuple(distance(c, i) for i in CELL_COLORS)
                        g_mins = tuple(min(i, j) for i, j in zip(g_mins, mins))
                    if not quick:
                        # find the smallest value
                        # if it is smaller than threshold, set accroding value to cell
                        min_value = min(g_mins)
                        if min_value <= COLOR_DISTANCE_THRESHOLD:
                            min_index = g_mins.index(min_value)
                            field[y][x].set_content(min_index + 1)
                        # if the smallest is greater than the threshold, cell is completely free
                        else:
                            field[y][x].set_content(0)
                # if top left pixel is not black, cell is unopened:
                # either unknown or a flag
                else:
                    # so we search for remotely red pixel at cell's center
                    # if there are some, it's a flag
                    for c in uniq_colors:
                        if distance(c, FLAG_RED) <= COLOR_DISTANCE_THRESHOLD:
                            field[y][x].set_content(FLAGGED)
                            break


# return 2D array's contents in a flat list
def get_field_flat(field):
    ret = []
    for row in field:
        ret.extend(row)
    return ret


# checks for popup windows with handle as a parent
def check_for_other_window(handle):
    return win32gui.GetWindow(handle, GW_ENABLEDPOPUP)


# moves mouse away, so highlight on hover doesn't mess with image processing
def remove_mouse():
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, 65535, 65535 // 2)


# returns length of a difference between two colors as integer vectors
def distance(color1, color2):
    return sqrt(sum(i ** 2 for i in (j - k for j, k in zip(color1, color2))))
