import sys
from pathlib import Path

from tkinterdnd2 import TkinterDnD

from app.ui.main_window import ConverterApp


def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def main():
    root = TkinterDnD.Tk()
    ConverterApp(root, app_dir())
    root.mainloop()


if __name__ == "__main__":
    main()
