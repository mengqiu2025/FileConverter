import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PIL import Image
from docx import Document

from app.core.config import load_config, save_config
from app.core.job_queue import JobQueue
from app.core.service import ConverterService


class SlowService:
    def convert(self, source, target_ext):
        time.sleep(0.5)
        return Path(source)


def make_service(tmp):
    config_path = Path(tmp) / "config.json"
    save_config(load_config(config_path), config_path)
    return ConverterService(Path(tmp), config_path)


class JobQueueTests(unittest.TestCase):
    def test_runs_jobs_sequentially_and_marks_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            service = make_service(tmp)
            sources = []
            for index in range(2):
                source = tmp / f"input_{index}.png"
                Image.new("RGB", (2, 2), color=(index * 10, 0, 0)).save(source)
                sources.append(source)

            queue = JobQueue(service, max_workers=1)
            for source in sources:
                queue.enqueue(source, "jpg")
            jobs = queue.run()

            self.assertEqual([job.status for job in jobs], ["success", "success"])
            self.assertTrue(all(job.output.exists() for job in jobs))

    def test_marks_failed_jobs_and_keeps_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "input.docx"
            document = Document()
            document.add_paragraph("HELLO")
            document.save(source)
            service = make_service(tmp)

            queue = JobQueue(service, max_workers=1)
            queue.enqueue(source, "pdf")
            jobs = queue.run()

            self.assertEqual(jobs[0].status, "failed")
            self.assertTrue(jobs[0].error)

    def test_cancel_marks_pending_job_as_cancelled(self):
        queue = JobQueue(SlowService(), max_workers=1)
        queue.enqueue(Path("a.png"), "jpg")
        queue.enqueue(Path("b.png"), "jpg")
        queue.cancel()
        jobs = queue.run()

        self.assertEqual(jobs[0].status, "cancelled")
        self.assertEqual(jobs[1].status, "cancelled")


if __name__ == "__main__":
    unittest.main()
