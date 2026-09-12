import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.core.routes import (
    classify_file,
    get_default_target,
    get_supported_targets,
)


class ClassifyFileTests(unittest.TestCase):
    def test_classifies_document_extensions(self):
        self.assertEqual(classify_file(Path("report.docx")), "document")
        self.assertEqual(classify_file(Path("sheet.xlsx")), "document")
        self.assertEqual(classify_file(Path("book.pdf")), "document")
        self.assertEqual(classify_file(Path("note.txt")), "document")

    def test_classifies_media_and_archive_extensions(self):
        self.assertEqual(classify_file(Path("photo.jpg")), "image")
        self.assertEqual(classify_file(Path("sound.mp3")), "audio")
        self.assertEqual(classify_file(Path("movie.mp4")), "video")
        self.assertEqual(classify_file(Path("bundle.zip")), "archive")


class DefaultTargetTests(unittest.TestCase):
    def test_returns_agreed_default_targets(self):
        defaults = {
            "document": "pdf",
            "image": "png",
            "video": "mp4",
            "audio": "mp3",
            "archive": "zip",
        }
        for category, expected in defaults.items():
            with self.subTest(category=category):
                self.assertEqual(get_default_target(category, defaults), expected)


class SupportedTargetsTests(unittest.TestCase):
    def test_pdf_source_offers_docx_txt_and_images(self):
        targets = get_supported_targets("pdf", lib=("fitz", "docx", "PIL"))
        self.assertIn("docx", targets)
        self.assertIn("txt", targets)
        self.assertIn("png", targets)

    def test_image_source_offers_common_lossless_and_web_formats(self):
        targets = get_supported_targets("jpg", lib=("PIL",))
        for ext in ("png", "jpg", "bmp", "gif", "tif", "webp", "ico", "pdf"):
            self.assertIn(ext, targets)

    def test_docx_source_does_not_offer_pdf_without_libreoffice(self):
        targets = get_supported_targets("docx", lib=("docx",))
        self.assertNotIn("pdf", targets)

    def test_docx_source_offers_pdf_with_libreoffice(self):
        targets = get_supported_targets(
            "docx", lib=("docx",), libreoffice_available=True
        )
        self.assertIn("pdf", targets)


if __name__ == "__main__":
    unittest.main()
