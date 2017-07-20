# main executable file

from winmine_classes import Cell
# import * is actually a bad practice
from winmine_util import *
import winmine_const as const
from winmine_ai import do_ai
from sys import exit, argv

from random import randint
from time import sleep
# variable to keep track of win count
wins = 0

# plays a single game
def play(handle, number):

    global wins
    # is caps is on, exit
    state = win32api.GetKeyState(win32con.VK_CAPITAL)
    if state:
        print("[i] CAPS on, exiting for the great justice")
        exit(0)

    # find game field borders on screen an take a picture of it
    window_rect = crop_rect(win32gui.GetWindowRect(handle))
    pic = get_window_picture(handle, window_rect)
    # guestimate field size, as each cell is 18×18 by default
    field_w, field_h = size_guess(pic)
    # initialize a completely unknown field
    field = [[Cell(i, j, const.UNKNOWN) for i in range(field_w)] for j in range(field_h)]
    for cell in get_field_flat(field):
        cell.set_parent(field)
    # first click is always safe, so click whereever but not at the border
    #  to maximize amount of cell opened
    first_x = randint(1, field_w - 2)
    first_y = randint(1, field_h - 2)
    field_click(first_x, first_y, window_rect, const.MOUSE1)
    sleep(const.WAIT_FOR_RESULTS_TIME)
    # AI begins here
    to_flag, to_open = 1, 1
    # while there are AI results and game is not won or lost
    #   (or another window is brought by user to stop the algorithm)
    while (to_flag or to_open) and not check_for_other_window(handle):
        # take another screenshot and process it
        pic = get_window_picture(handle, window_rect)
        process_field_image(pic, field)
        # run ai over an updated field
        to_flag, to_open = do_ai(field)
        # open and flag cells per AI output
        for cell in to_open:
            sleep(const.TINY_SLEEP_TIME)
            results = check_for_other_window(handle)
            if results:
                break
            x, y = cell.get_coords()
            field_click(x, y, window_rect, const.MOUSE1)
        for cell in to_flag:
            sleep(const.TINY_SLEEP_TIME)
            results = check_for_other_window(handle)
            if results:
                break
            x, y = cell.get_coords()
            field_click(x, y, window_rect, const.MOUSE2)
            field[y][x].set_content(const.FLAGGED)
    # check for win/loss/other popup window
    sleep(const.WAIT_FOR_RESULTS_TIME)
    results = check_for_other_window(handle)
    text = win32gui.GetWindowText(results)
    if text == const.GAME_LOST:
        print(f"[-] Game #{number} lost")
    elif text == const.GAME_WON:
        wins += 1
        print(f"[+] Game #{number} won")
    else:
        raise RuntimeError("Another window appeared")


# just sends "Enter" keypress to restart the game
def restart(results_window):
    win32api.PostMessage(results_window, const.WM_KEYDOWN, const.VK_RETURN, 0)


# warns about console usage
def wrong_usage():
    print("Usage: no arguments to play one game, positive integer to play multiple games in a row")
    exit(-1)


if __name__ == '__main__':

    times_to_play = 1

    if len(argv) > 1:
        try:
            times_to_play = int(argv[1])
        except ValueError:
            wrong_usage()
        if times_to_play <= 0:
            wrong_usage()

    handle = None
    try:
        handle = find_minesweeper_window()
    except RuntimeError as err:
        print(err)
        exit(-1)
    resize_window(handle)

    for i in range(times_to_play):
        try:
            play(handle, i)
            restart(check_for_other_window(handle))
            sleep(const.WAIT_FOR_RESULTS_TIME)
        except RuntimeError:
            print("[i] Unknown window appeared, exiting")
            exit(0)
    print(f"[i] Winrate: {wins}/{times_to_play}")
