# Rivals Smurf Tracker

A little project I wrote in a day to allow users to keep track of their marvel rivals smurf accounts.

Written in Python and using Textual TUI

# Why Use This

Why not? Honestly you can do the same thing with notepad or excel or even a piece of paper. But its a fun little project that allows you to see your accounts and filter them based on Competitive Rank matching. If youve ever wondered "Was it account a or account b that was gold" to play with your friend who just started, just type in the search bar your friends rank and it will show you all the accounts you have that can queue with them. Plus its pretty simplistic, no need for an internet connection and everything is saved locally to your pc using sqlite3 database files.

# Technology Used

Uses python 3.12, textual, and sqlite3 It runs completely in the terminal and supports both mouse clicks and keyboard.

# How to use

There are 2 ways to use this program. If you are a programmer or at least know your way around python, you can use [uv](https://docs.astral.sh/uv/) to install all the dependancies and run the python file. Or if you just want an exe to run you can download the .exe file in releases.

To get started with `uv` please install it [here](<[uv](https://docs.astral.sh/uv/getting-started/installation/)>)

Then clone this repo. and in the root directory type

```bash
uv sync
```

This will setup the dependancies and a venv for the project.

Then run

```bash
uv run ./rivals_viewer.py
```

in your terminal of choice (windows terminal, or alacritty recommended) and it will create a db file for you and start the TUI

You can also generate your own .exe file for portable use by installing [pyinstaller](https://pyinstaller.org/en/stable/) and running the following in your terminal once you have initialized the project with `uv`

```bash
uv run pyinstaller --noconfirm --onefile --hidden-import=textual.widgets._tab --console --name rivals_viewer .\rivals_viewer.py
```

This will create a `build`, `dist`, and `rivals_viewer.spec` folder and files. Open up the `dist` folder and double click the `rivals_viewer.exe` to run it.

---

If you don't care for setting it up, download the .exe from the releases page. It was created using the same steps as above.

# Feedback and Help

I just did this for a small group of friends who have smurfs to play with other friends in lower ranks. I literally wrote most of this in 2 hours and I'm sure theres issues, bugs, and better ways to do this. If you want to help make a PR and ill approve it if I think it helps.

I also plan on updating and adding some features "soon".

# FAQ

If you cant see all the buttons, resize the window until i get scrolling working on the application.
