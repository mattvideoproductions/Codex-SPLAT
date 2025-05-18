# Physics Example

This repository contains a small physics based prototype using
[Pygame](https://www.pygame.org/) together with
[Pymunk](http://www.pymunk.org/). It started as a platformer skeleton but now
shows a single square that can be moved around with the keyboard or the mouse.
Feel free to extend it further.

## Requirements

- Python 3.8+
- Pygame
- Pymunk

Install the requirements using pip:

```bash
pip install -r requirements.txt
```

## Running the Game

Execute the game script using Python:

```bash
python game.py
```

When running the script a window will appear that can be resized or maximised.
A red square lives in a small physics environment and can be moved with the
**WASD** keys. You can also drag it with the left mouse button and release it to
fling the square across the screen. The square starts inside a boxed-in test
area so it has a floor and walls to collide with.
