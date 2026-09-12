import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.core.converters.archive import convert_archive


SEVENZIP = (
    Path(__file__).resolve().parents[1]
    / "downd-tools"
    / "sevenzip-full"
    / "7z.exe"
)


@unittest.skipUnless(SEVENZIP.exists(), "7z.exe is not available")
class ArchiveConverterTests(unittest.TestCase):
    def test_zip_to_7z(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            payload = tmp / "payload"
            payload.mkdir()
            (payload / "hello.txt").write_text("hello", encoding="utf-8")
            source = tmp / "input.zip"
            output = tmp / "converted" / "input.7z"
            shutil.make_archive(str(tmp / "input"), "zip", root_dir=tmp, base_dir="payload")

            convert_archive(source, output, sevenzip=SEVENZIP, quality={})

            self.assertTrue(output.exists())
            listing = subprocess.run(
                [str(SEVENZIP), "l", str(output)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            ).stdout
            self.assertIn("hello.txt", listing)

    def test_7z_to_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            payload = tmp / "payload"
            payload.mkdir()
            (payload / "hello.txt").write_text("hello", encoding="utf-8")
            source = tmp / "input.7z"
            output = tmp / "converted" / "input.zip"
            subprocess.run(
                [str(SEVENZIP), "a", str(source), str(payload / "hello.txt")],
                check=True,
                capture_output=True,
            )

            convert_archive(source, output, sevenzip=SEVENZIP, quality={})

            self.assertTrue(output.exists())
            with zipfile.ZipFile(output) as archive:
                self.assertIn("hello.txt", archive.namelist())


if __name__ == "__main__":
    unittest.main()
