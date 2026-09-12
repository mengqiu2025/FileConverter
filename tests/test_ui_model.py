import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.core.config import DEFAULT_CONFIG
from app.core.ui_model import build_file_item


class BuildFileItemTests(unittest.TestCase):
    def test_image_gets_default_png_target_and_is_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "photo.jpg"
            item = build_file_item(path, DEFAULT_CONFIG)

            self.assertEqual(item.category, "image")
            self.assertEqual(item.target_ext, "png")
            self.assertTrue(item.available)
            self.assertIn("png", item.supported_targets)

    def test_docx_default_pdf_is_unavailable_without_libreoffice(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            item = build_file_item(path, DEFAULT_CONFIG, libreoffice_available=False)

            self.assertEqual(item.category, "document")
            self.assertEqual(item.target_ext, "pdf")
            self.assertFalse(item.available)
            self.assertIn("需要可选文档引擎", item.reason)

    def test_docx_default_pdf_is_available_with_libreoffice(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            item = build_file_item(path, DEFAULT_CONFIG, libreoffice_available=True)

            self.assertEqual(item.target_ext, "pdf")
            self.assertTrue(item.available)
            self.assertEqual(item.reason, "")


if __name__ == "__main__":
    unittest.main()
