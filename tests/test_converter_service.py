import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PIL import Image
from docx import Document

from app.core.config import load_config, save_config
from app.core.errors import SameFormatError
from app.core.service import ConverterService


SEVENZIP = (
    Path(__file__).resolve().parents[1]
    / "downd-tools"
    / "sevenzip-full"
    / "7z.exe"
)


class ConverterServiceTests(unittest.TestCase):
    def test_converts_image_through_service(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "input.png"
            Image.new("RGB", (3, 3), color=(255, 0, 0)).save(source)
            config_path = tmp / "config.json"
            save_config(load_config(config_path), config_path)
            service = ConverterService(tmp, config_path)

            output = service.convert(source, "jpg")

            self.assertTrue(output.exists())
            with Image.open(output) as image:
                self.assertEqual(image.format, "JPEG")

    def test_converts_document_through_service(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "input.docx"
            document = Document()
            document.add_paragraph("HELLO SERVICE")
            document.save(source)
            config_path = tmp / "config.json"
            save_config(load_config(config_path), config_path)
            service = ConverterService(tmp, config_path)

            output = service.convert(source, "txt")

            self.assertTrue(output.exists())
            self.assertIn("HELLO SERVICE", output.read_text(encoding="utf-8"))

    def test_rejects_same_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "input.png"
            Image.new("RGB", (2, 2)).save(source)
            config_path = tmp / "config.json"
            save_config(load_config(config_path), config_path)
            service = ConverterService(tmp, config_path)

            with self.assertRaises(SameFormatError):
                service.convert(source, "png")

    @unittest.skipUnless(SEVENZIP.exists(), "7z.exe is not available")
    def test_converts_archive_through_service(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            payload = tmp / "payload"
            payload.mkdir()
            (payload / "hello.txt").write_text("hello", encoding="utf-8")
            source = tmp / "input.zip"
            shutil.make_archive(str(tmp / "input"), "zip", root_dir=tmp, base_dir="payload")
            config_path = tmp / "config.json"
            config = load_config(config_path)
            config["engines"]["sevenzip"] = str(SEVENZIP)
            save_config(config, config_path)
            service = ConverterService(tmp, config_path)

            output = service.convert(source, "7z")

            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
