import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.core.converters.media import convert_media


FFMPEG = shutil.which("ffmpeg")


@unittest.skipIf(FFMPEG is None, "ffmpeg is not available")
class MediaConverterTests(unittest.TestCase):
    def test_converts_wav_to_mp3(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp / "input.wav"
            output = tmp / "converted" / "input.mp3"
            _make_silent_wav(source, seconds=0.05)

            convert_media(
                source,
                output,
                ffmpeg=FFMPEG,
                quality={"mp3_bitrate": "320k"},
            )

            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 0)
            info = _probe(output)
            self.assertIn("Audio: mp3", info)


def _make_silent_wav(path, seconds=0.05, rate=8000):
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = bytearray(int(seconds * rate * 2))
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(bytes(frames))


def _probe(path):
    return subprocess.run(
        [FFMPEG, "-hide_banner", "-i", str(path)],
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        stderr=subprocess.STDOUT,
    ).stdout


if __name__ == "__main__":
    unittest.main()
