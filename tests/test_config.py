import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.core.config import DEFAULT_CONFIG, load_config, save_config


class ConfigTests(unittest.TestCase):
    def test_load_returns_defaults_when_file_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            self.assertEqual(load_config(path), DEFAULT_CONFIG)

    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            config = load_config(path)
            config["execution"]["parallel"] = True
            config["output"]["custom_dir"] = "D:/out"
            save_config(config, path)

            loaded = load_config(path)
            self.assertTrue(loaded["execution"]["parallel"])
            self.assertEqual(loaded["output"]["custom_dir"], "D:/out")

    def test_saved_file_is_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            save_config(DEFAULT_CONFIG, path)
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            self.assertEqual(data["defaults"]["document"], "pdf")


if __name__ == "__main__":
    unittest.main()
