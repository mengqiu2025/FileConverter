import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pymupdf as fitz
from docx import Document
from PIL import Image

from app.core.converters.pdf import convert_pdf


def make_pdf(path, text="HELLO PDF"):
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    document.save(path)
    document.close()


class PdfConverterTests(unittest.TestCase):
    def test_pdf_to_txt_extracts_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "input.pdf"
            output = tmp / "converted" / "input.txt"
            make_pdf(source)

            convert_pdf(source, output)

            self.assertTrue(output.exists())
            self.assertIn("HELLO PDF", output.read_text(encoding="utf-8"))

    def test_pdf_to_png_creates_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "input.pdf"
            output = tmp / "converted" / "input.png"
            make_pdf(source)

            convert_pdf(source, output)

            self.assertTrue(output.exists())
            with Image.open(output) as image:
                self.assertEqual(image.format, "PNG")

    def test_pdf_to_docx_creates_editable_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "input.pdf"
            output = tmp / "converted" / "input.docx"
            make_pdf(source)

            convert_pdf(source, output)

            self.assertTrue(output.exists())
            document = Document(output)
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
            self.assertIn("HELLO PDF", text)


if __name__ == "__main__":
    unittest.main()
