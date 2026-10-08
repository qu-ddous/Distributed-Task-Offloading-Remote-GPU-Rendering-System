"""
Client Desktop Application Entrypoint
"""
import io
import sys
from pathlib import Path

# Safe streams for windowed exe (console=False)
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# Ensure root repository directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from client.ui.main_window import App

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
