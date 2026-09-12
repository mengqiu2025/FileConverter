import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PIL import Image
from tkinterdnd2 import TkinterDnD

from app.ui.main_window import ConverterApp


class GuiSmokeTests(unittest.TestCase):
    def test_window_creates_and_accepts_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "input.png"
            Image.new("RGB", (2, 2), color=(10, 20, 30)).save(source)

            root = TkinterDnD.Tk()
            root.withdraw()
            app = None
            try:
                app = ConverterApp(root, tmp)
                app._add_paths([source])
                self.assertEqual(len(app.items), 1)
                root.update_idletasks()
            finally:
                if app is not None:
                    for handler in app.logger.handlers:
                        handler.close()
                root.destroy()


if __name__ == "__main__":
    unittest.main()
