import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PIL import Image

from app.core.converters.image import convert_image


class ImageConverterTests(unittest.TestCase):
    def test_converts_png_to_jpeg(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "input.png"
            output = tmp / "converted" / "input.jpg"
            Image.new("RGB", (4, 4), color=(255, 0, 0)).save(source)

            convert_image(source, output, {"jpeg_quality": 95})

            self.assertTrue(output.exists())
            with Image.open(output) as image:
                self.assertEqual(image.format, "JPEG")
                self.assertEqual(image.size, (4, 4))

    def test_converts_png_to_lossless_webp(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "input.png"
            output = tmp / "converted" / "input.webp"
            Image.new("RGBA", (3, 3), color=(1, 2, 3, 255)).save(source)

            convert_image(source, output, {"webp_lossless": True})

            self.assertTrue(output.exists())
            with Image.open(output) as image:
                self.assertEqual(image.format, "WEBP")


if __name__ == "__main__":
    unittest.main()
