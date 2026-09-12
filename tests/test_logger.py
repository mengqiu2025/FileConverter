import sys
import tempfile
import time
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.core.logger import cleanup_old_logs


class LoggerCleanupTests(unittest.TestCase):
    def test_deletes_logs_older_than_retention(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_dir = Path(tmp)
            old = log_dir / "converter-20200101.log"
            new = log_dir / "converter-20990101.log"
            old.write_text("old", encoding="utf-8")
            new.write_text("new", encoding="utf-8")
            old_time = time.time() - 31 * 24 * 3600
            new_time = time.time()
            import os

            os.utime(old, (old_time, old_time))
            os.utime(new, (new_time, new_time))

            cleanup_old_logs(log_dir, retention_days=30)

            self.assertFalse(old.exists())
            self.assertTrue(new.exists())


if __name__ == "__main__":
    unittest.main()
