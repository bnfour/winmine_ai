# An artificial "intelligence" that plays windows minesweeper

![Screencap](http://i.imgur.com/zOaHhuO.gif)

Usage: `python winmine_exe.py [amount of games to play, 1 by default]`

How to stop ~~the machine uprising~~ this app's control of your cursor:
* **Caps lock:** no new games will be played if it is on
* **F2:** popping a new game dialog stops execution immediately 

Winrates of 100 games on standard difficulty levels:
* **Beginner:** 86%
* **Intermediate:** 61%
* **Advanced:** 9% (it is hard) 

Dependencies: [PIL](https://pypi.python.org/pypi/Pillow/4.2.1), [win32api, win32con, win32gui](https://pypi.python.org/pypi/pypiwin32/220).

Tested on english version of Windows 7, for different locale please change the `WINMINE_APP_TITLE`, `GAME_LOST` and `GAME_WON` strings in `winmine_const.py` to their equivalents.

Won't work on small screens and weak videocards (on a 1024×600 Atom netbook with integrated video even minesweeper is rendered with blurry upscaling that **really** messes up field recognition algorithm).