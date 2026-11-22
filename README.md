# Lights Out

A 5x5 Lights Out puzzle game made with Python and Flask. Clicking a window flips it and the windows above, below, left and right of it. The goal is to turn every light off.

## Libraries used

- [Flask](https://flask.palletsprojects.com/) - runs the web page (installed with pip)
- `random` - makes random puzzles (built into Python)
- `time` - the timer (built into Python)
- `unittest` - the tests (built into Python)

## How to run

You need Python 3 installed.

1. Install Flask:

   ```
   pip install flask
   ```

2. Start the game:

   ```
   python app.py
   ```

3. Open <http://127.0.0.1:5000> in your browser. Press `Ctrl+C` in the terminal to stop it.

To run the tests:

```
python -m unittest
```

On macOS and Linux you may need to type `python3` instead of `python`, and `pip3` instead of `pip`.

## Files

- `logic.py` - the game rules: `toggle`, `is_solved`, `generate_board`
- `app.py` - the web server
- `templates/` - the game page and the instructions pop-up
- `static/` - the CSS and images
- `test_logic.py` - the tests
