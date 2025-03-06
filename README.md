<p align="center">
  <a href="https://rclone.org/">
    <img width="40%" alt="Reactor" src="https://github.com/user-attachments/assets/fbc5458a-a33e-403e-b3da-a4513be12172">
  </a>
</p>

# MirrorChrome
### Automates mirroring of tabs from Chrome to Firefox

## What is does

This is a Python script that automates the task of duplicating open tabs from a Chrome browser window to a Firefox browser window.  This script relies heavily on Windows-only packages, so only works on Microsoft Windows.

## Why it exists

Primarily, it exists to allow you to migrate your browser life out of Chrome and to Firefox.  However, you could also think of the process as "backing up" your tabs (or a selection of them) to another browser if your Chrome environment is volatile.

## How it works

The script will provide you with instructions when you run it.  Simply, have one or more Chrome windows open on your Windows desktop, and be sure Firefox is installed (and recommended to be open somewhere).

Since the script runs without user interaction, you need to let it know when to stop mirroring tabs.  This is accomplished by placing a "dead" (or "marker") tab someplace that contains no value in its address bar.  This will signal to the script that it has reached the end of the tab march, and will cause it to exit.  So, for example, if you want to export _all_ tabs in a paricular Chrome window, open a new tab the end of the line, and then go back and select the first tab in the list.  Alternately, you can position the "marker" tab anywhere you like, and select any starting tab you like (as long as it preceeds the "marker" tab) to export only subsets of your open tabs.

## How to use it

### For the tehnically inclined...
1. Clone this repo.
2. From the parent folder, execute `python -m venv MirrorChrome` to create a virtual environment in the same folder.
3. Change into the MirrorChrome/ folder and activate the virtual environment with `Scripts\activate`.
4. Install the requirements using `pip install -r requirements.txt`.
5. Run the script with `python mirror.py`.
6. Follow instructions.

### For the technically challenged...
1. Download the MirrorChrome.exe execuatble available as a Release (look over there -->).
2. Make sure your Chrome window(s) is open with the tabs you want to mirror.
3. Run the executable.
4. Follow instructions.

## Watch it work

This video, captured during development, demonstrates the script mirroring random tabs from Chrome to Firefox.

https://github.com/user-attachments/assets/8e463349-071c-4f08-9b54-1f1989705f7e

The interface has changed somewhat since then, but the functionality remains the same.

## Quaeso, opera mea fruere.
