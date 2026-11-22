"""
Start Lights Out.

    python main.py

This starts a small web server on your computer and opens the game in
your browser. Press Ctrl+C in the terminal to stop it.
"""

import threading
import webbrowser

from app import app

HOST = "127.0.0.1"
PORT = 5000
BROWSER_DELAY_SECONDS = 1.0


def open_browser():
    webbrowser.open(f"http://{HOST}:{PORT}/")


if __name__ == "__main__":
    print(f"Lights Out is running at http://{HOST}:{PORT}/  (Ctrl+C to stop)")
    threading.Timer(BROWSER_DELAY_SECONDS, open_browser).start()
    app.run(host=HOST, port=PORT, debug=False)
