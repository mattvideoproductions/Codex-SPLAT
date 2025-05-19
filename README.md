# Physics Example

This repository contains a small physics based prototype using
[Pygame](https://www.pygame.org/) together with
[Pymunk](http://www.pymunk.org/). It started as a platformer skeleton but now
shows a single circle that can be moved around with the keyboard or the mouse.
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
A red circle lives in a small physics environment and can be moved with the
**WASD** keys. You can also drag it with the left mouse button and release it to
fling the circle across the screen.

## Level Files

Level geometry is loaded from JSON (or YAML) files in the `levels/` directory.
Each level file is an array of segments. Every segment requires two endpoints
`a` and `b` and can optionally specify `friction`:

```json
[
  {"a": [0, 40], "b": [2000, 40]},
  {"a": [0, 40], "b": [0, 1200]},
  {"a": [2000, 40], "b": [2000, 1200]},
  {"a": [0, 1200], "b": [2000, 1200], "friction": 1.5}
]
```

Segments are created in the physics space exactly as specified. Create a new
file following this format and place it inside `levels/` to experiment with your
own playgrounds.
