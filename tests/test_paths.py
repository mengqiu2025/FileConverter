import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.core.errors import SameFormatError
from app.core.paths import build_output_path


class BuildOutputPathTests(unittest.TestCase):
    def test_outputs_to_converted_directory_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "report.docx"
            expected = Path(tmp) / "converted" / "report.pdf"
            self.assertEqual(build_output_path(source, "pdf"), expected)

    def test_normalizes_target_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "image.jpg"
            expected = Path(tmp) / "converted" / "image.png"
            self.assertEqual(build_output_path(source, ".PNG"), expected)

    def test_auto_renames_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "report.docx"
            converted = Path(tmp) / "converted"
            converted.mkdir()
            (converted / "report.pdf").write_text("existing", encoding="utf-8")
            self.assertEqual(
                build_output_path(source, "pdf"),
                converted / "report_1.pdf",
            )

    def test_skips_already_taken_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "report.docx"
            converted = Path(tmp) / "converted"
            converted.mkdir()
            for name in ("report.pdf", "report_1.pdf"):
                (converted / name).write_text("existing", encoding="utf-8")
            self.assertEqual(
                build_output_path(source, "pdf"),
                converted / "report_2.pdf",
            )

    def test_rejects_same_format_conversion(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "report.docx"
            with self.assertRaises(SameFormatError):
                build_output_path(source, "docx")

    def test_allows_custom_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "report.docx"
            out = Path(tmp) / "output"
            self.assertEqual(build_output_path(source, "pdf", output_dir=out), out / "report.pdf")


if __name__ == "__main__":
    unittest.main()
