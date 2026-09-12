import os
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.core.engines import EngineManager, EngineNotFoundError


class EngineManagerTests(unittest.TestCase):
    def test_prefers_bundled_tool_over_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            app_dir = Path(tmp)
            bundled = app_dir / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
            bundled.parent.mkdir(parents=True)
            bundled.touch()

            manager = EngineManager(app_dir)
            self.assertEqual(manager.resolve("ffmpeg"), bundled)

    def test_falls_back_to_system_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            fake = bin_dir / "ffmpeg.exe"
            fake.touch()

            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = str(bin_dir) + os.pathsep + old_path
            try:
                manager = EngineManager(Path(tmp) / "app")
                self.assertEqual(manager.resolve("ffmpeg"), fake)
            finally:
                os.environ["PATH"] = old_path

    def test_manual_path_overrides_everything(self):
        with tempfile.TemporaryDirectory() as tmp:
            app_dir = Path(tmp) / "app"
            manual = Path(tmp) / "custom" / "ffmpeg.exe"
            manual.parent.mkdir(parents=True)
            manual.touch()

            manager = EngineManager(app_dir, manual_paths={"ffmpeg": manual})
            self.assertEqual(manager.resolve("ffmpeg"), manual)

    def test_raises_when_engine_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            app_dir = Path(tmp) / "app"
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = ""
            try:
                manager = EngineManager(app_dir)
                with self.assertRaises(EngineNotFoundError):
                    manager.resolve("ffmpeg")
            finally:
                os.environ["PATH"] = old_path


if __name__ == "__main__":
    unittest.main()
