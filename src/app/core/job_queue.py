from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
import threading
import time


@dataclass
class Job:
    source: Path
    target_ext: str
    status: str = "pending"
    output: Path | None = None
    error: str | None = None
    id: int = field(default_factory=lambda: next(Job._counter))
    _counter = iter(range(1, 10**9))

    def __post_init__(self):
        self.source = Path(self.source)
        self.target_ext = self.target_ext.lower().lstrip(".")


class JobQueue:
    def __init__(self, service, max_workers=1, on_job_finished=None):
        self.service = service
        self.max_workers = max_workers
        self.jobs = []
        self.on_job_finished = on_job_finished
        self._cancel_event = threading.Event()
        self._pause_event = threading.Event()
        self._paused = False

    def enqueue(self, source, target_ext):
        job = Job(source=source, target_ext=target_ext)
        self.jobs.append(job)
        return job

    def run(self):
        if self.max_workers <= 1:
            for job in self.jobs:
                self._run_one(job)
                self._notify_finished(job)
            return self.jobs

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._run_one, job): job for job in self.jobs}
            for future in as_completed(futures):
                future.result()
                self._notify_finished(futures[future])
        return self.jobs

    def cancel(self):
        self._cancel_event.set()

    def pause(self):
        self._pause_event.set()
        self._paused = True

    def resume(self):
        self._pause_event.clear()
        self._paused = False

    def is_paused(self):
        return self._paused

    def _run_one(self, job):
        if self._cancel_event.is_set():
            job.status = "cancelled"
            return
        while self._pause_event.is_set() and not self._cancel_event.is_set():
            time.sleep(0.05)
        if self._cancel_event.is_set():
            job.status = "cancelled"
            return
        job.status = "running"
        try:
            job.output = self.service.convert(job.source, job.target_ext)
            job.status = "success"
        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)

    def _notify_finished(self, job):
        if self.on_job_finished:
            self.on_job_finished(job)
