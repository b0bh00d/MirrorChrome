#-------------------------------------------------------------------------#
# MirrorChrome                                                by Bob Hood #
# https://github.com/b0bh00d/MirrorChrome                                 #
#-------------------------------------------------------------------------#

import os
import re
import sys
import time
import pyautogui
import subprocess

try:
    import winreg
    import win32gui

    from pywinauto import Application
except ImportError:
    print("I'm sorry, but this script only runs on Windows.")
    sys.exit(1)

try:
    # "One does want a hint of color" - Albert, "The Birdcage"
    import colorama
    fore_colors = { 'BLACK'       : colorama.Fore.BLACK,
                    'LITEBLACK'   : colorama.Fore.LIGHTBLACK_EX,
                    'RED'         : colorama.Fore.RED,
                    'LITERED'     : colorama.Fore.LIGHTRED_EX,
                    'GREEN'       : colorama.Fore.GREEN,
                    'LITEGREEN'   : colorama.Fore.LIGHTGREEN_EX,
                    'YELLOW'      : colorama.Fore.YELLOW,
                    'LITEYELLOW'  : colorama.Fore.LIGHTYELLOW_EX,
                    'BLUE'        : colorama.Fore.BLUE,
                    'LITEBLUE'    : colorama.Fore.LIGHTBLUE_EX,
                    'MAGENTA'     : colorama.Fore.MAGENTA,
                    'LITEMAGENTA' : colorama.Fore.LIGHTMAGENTA_EX,
                    'CYAN'        : colorama.Fore.CYAN,
                    'LITECYAN'    : colorama.Fore.LIGHTCYAN_EX,
                    'WHITE'       : colorama.Fore.WHITE,
                    'LITEWHITE'   : colorama.Fore.LIGHTWHITE_EX,
                    'RESET'       : colorama.Fore.RESET }
    back_colors = { 'BLACK'       : colorama.Back.BLACK,
                    'LITEBLACK'   : colorama.Back.LIGHTBLACK_EX,
                    'RED'         : colorama.Back.RED,
                    'LITERED'     : colorama.Back.LIGHTRED_EX,
                    'GREEN'       : colorama.Back.GREEN,
                    'LITEGREEN'   : colorama.Back.LIGHTGREEN_EX,
                    'YELLOW'      : colorama.Back.YELLOW,
                    'LITEYELLOW'  : colorama.Back.LIGHTYELLOW_EX,
                    'BLUE'        : colorama.Back.BLUE,
                    'LITEBLUE'    : colorama.Back.LIGHTBLUE_EX,
                    'MAGENTA'     : colorama.Back.MAGENTA,
                    'LITEMAGENTA' : colorama.Back.LIGHTMAGENTA_EX,
                    'CYAN'        : colorama.Back.CYAN,
                    'LITECYAN'    : colorama.Back.LIGHTCYAN_EX,
                    'WHITE'       : colorama.Back.WHITE,
                    'LITEWHITE'   : colorama.Back.LIGHTWHITE_EX,
                    'RESET'       : colorama.Back.RESET }
    styl_colors = { 'DIM'         : colorama.Style.DIM,
                    'NORMAL'      : colorama.Style.NORMAL,
                    'BRIGHT'      : colorama.Style.BRIGHT,
                    'RESET_ALL'   : colorama.Style.RESET_ALL }
    have_color = True
except ImportError:
    fore_colors = { 'BLACK' : '', 'RED' : '', 'GREEN' : '', 'YELLOW' : '', 'BLUE' : '' , 'MAGENTA' : '', 'CYAN' : '', 'WHITE' : '', 'RESET' : '' }
    back_colors = { 'BLACK' : '', 'RED' : '', 'GREEN' : '', 'YELLOW' : '', 'BLUE' : '' , 'MAGENTA' : '', 'CYAN' : '', 'WHITE' : '', 'RESET' : '' }
    styl_colors = { 'DIM' : '', 'NORMAL' : '', 'BRIGHT' : '', 'RESET_ALL' : '' }
    have_color = False

class WindowMgr:
    """
    Encapsulates some calls to the winapi for window management
    """

    def __init__ (self):
        self._handle = None

    def find_window(self, class_name, window_name=None) -> None:
        """
        Find a window by its class_name
        """
        self._handle = win32gui.FindWindow(class_name, window_name)
        if self._handle is None:
            raise Exception("Could not find window")

    def _wildcard_callback(self, hwnd, wildcard) -> None:
        """
        Pass to win32gui.EnumWindows() to check all the opened windows
        """
        if win32gui.IsWindowVisible( hwnd ):
            if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
                self._handle = hwnd

    def find_window_wildcard(self, wildcard) -> None:
        """
        Find a window whose title matches the wildcard regex
        """
        self._handle = None
        win32gui.EnumWindows(self._wildcard_callback, wildcard)
        if self._handle is None:
            raise Exception("Could not find window")

    def _substr_callback(self, hwnd, substr) -> None:
        """
        Pass to win32gui.EnumWindows() to check all the opened windows
        """
        if win32gui.IsWindowVisible( hwnd ):
            if substr in str(win32gui.GetWindowText(hwnd)):
                self._handle = hwnd

    def find_window_substr(self, substr) -> None:
        """
        Find a window whose title contains the provided substring
        """
        self._handle = None
        win32gui.EnumWindows(self._substr_callback, substr)
        if self._handle is None:
            raise Exception("Could not find window")

    def set_foreground(self) -> None:
        """
        Give the window focus for input
        """
        if self._handle is None:
            raise Exception("Invalid window handle")
        win32gui.SetForegroundWindow(self._handle)

def find_firefox() -> str | None:
    """
    Automatically locate the Firefox executable based on registry entries
    """
    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    try:
        key = winreg.OpenKey(reg, r'Software\Classes\Applications\firefox.exe\shell\open\command')
        value = winreg.QueryValueEx(key, "")
    except Exception:
        print(f"{fore_colors['RED']}ERROR{fore_colors['RESET']}: Firefox does not appear to be installed.  Sorry.")
        return None

    # "C:\Program Files\Mozilla Firefox\firefox.exe" -osint -url "%1"
    result = re.search(r'^"(.+?)"', value[0])
    if not result:
        print(f"{fore_colors['RED']}ERROR{fore_colors['RESET']}: Firefox does not appear to be installed.  Sorry.")
        return None

    print(f"{fore_colors['GREEN']}INFO{fore_colors['RESET']}: Found Firefox: {fore_colors['YELLOW']}{result.group(1)}{fore_colors['RESET']}")
    return result.group(1)

def find_chrome() -> WindowMgr:
    """
    Use the WindowMgr class to locate the open Chrome window
    """
    # def winEnumHandler( hwnd, ctx ):
    #     if win32gui.IsWindowVisible( hwnd ):
    #         print ( hex( hwnd ), win32gui.GetWindowText( hwnd ) )

    # win32gui.EnumWindows( winEnumHandler, None )
    # sys.exit(0)

    w = WindowMgr()
    try:
        w.find_window_substr("- Google Chrome")
    except Exception:
        print(f"{fore_colors['RED']}ERROR{fore_colors['RESET']}: Coud not locate a window with 'Google Chrome' in its title.")
        graceful_abort(1)

    return w

def connect_to_chrome(hwnd):
    """
    Create a connection to the open Chrome window using the provided
    Windows HANDLE.
    """
    app = Application(backend='uia')
    try:
        # app.connect(title_re=".*Google Chrome^")
        # app.connect(path=chrome_path)
        app.connect(handle=hwnd)
    except Exception:
        print(f"{fore_colors['RED']}ERROR{fore_colors['RESET']}: More than one potential Chrome window was found.")
        graceful_abort(1)

    dlg = app.top_window()
    return dlg

def open_in_firefox(url: str, firefox: str):
    """
    Open the provided URL in a Firefox tab (opens a new Firefox window if one
    isn't already open).
    """
    subprocess.check_call([firefox, '-url', url])

def print_steps() -> None:
    print("""
Steps to follow:
    1. Ensure that Chrome is open and positioned on the first tab you wish to mirror in Firefox.
          1a. If you have multiple Chrome windows open, close them as you complete each run.
    2. Place a "dead" tab (one without a value in the address bar) where you want the script to stop.
    3. If Firefox is already open (recommended), new tabs will be appended to your current tab list.
          3a. If it is not, it will be opened when the first tab is mirrored.

Press Enter to begin (or Ctrl-C to cancel)...""")

def elide(value: str, max: int, tail: str = '') -> str:
    """
    Clip a string value to a maximum length and append the provided tail value
    """
    if len(value) > max:
        return f"{value[:(max - len(tail))]}{tail}"
    return value

def graceful_abort(code: int):
    """
    Abort as gracefully as possible
    """

    # hold the terminate window open if we are running under pyinstaller
    if bundled():
        print('Press Enter to exit...')
        input()

    sys.exit(code)

def bundled() -> bool:
    """
    Are we running under a pyinstaller bundle?
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def main() -> int:
    global have_color

    if have_color:
        colorama.init()

    columns, _ = os.get_terminal_size()

    firefox_path = find_firefox()
    if firefox_path is not None:
        chrome = find_chrome()
        print_steps()

        try:
            input()
        except KeyboardInterrupt:
            print('Cancel requested.')
            graceful_abort(0)

        # See this ...
        # https://stackoverflow.com/questions/63648053/pywintypes-error-0-setforegroundwindow-no-error-message-is-available
        # ... for why this ...
        pyautogui.press("alt")
        # ... is necessary.

        chrome.set_foreground()

        dlg = connect_to_chrome(chrome._handle)

        element_name="Address and search bar"
        msg_prefix = 'Mirroring '
        elide_max = columns - len(msg_prefix)

        while True:
            # https://stackoverflow.com/questions/52675506/get-chrome-tab-url-in-python
            url = dlg.child_window(title=element_name, control_type="Edit").get_value()
            if len(url) == 0:
                break

            print(f"{msg_prefix}{fore_colors['CYAN']}{elide(url, elide_max, '...')}{fore_colors['RESET']}")

            open_in_firefox(url, firefox_path)

            # "Time is what keeps everything from happening at once." - Ray Cummings, "The Girl in the Golden Atom"
            time.sleep(1)

            pyautogui.press("alt")
            chrome.set_foreground()
            pyautogui.hotkey('ctrl', 'tab')

        print('\nDone!')
    else:
        return 1

    return 0

if __name__ == "__main__":
    result = main()

    # hold the terminate window open if we are running under pyinstaller
    if bundled():
        print('Press Enter to exit...')
        input()

    sys.exit(result)
