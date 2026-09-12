import subprocess
import tempfile
from pathlib import Path

from app.core.errors import ConverterError


ARCHIVE_FORMATS = {
    "zip": "zip",
    "7z": "7z",
    "tar": "tar",
    "gz": "gzip",
    "bz2": "bzip2",
    "xz": "xz",
}


def convert_archive(source, output, sevenzip, quality, temp_dir=None):
    source = Path(source)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    target_ext = output.suffix.lower().lstrip(".")
    archive_type = ARCHIVE_FORMATS[target_ext]

    temp_root = Path(temp_dir) if temp_dir else None
    if temp_root:
        temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=temp_root) as tmp:
        extract_dir = Path(tmp) / "extract"
        extract_dir.mkdir()
        _run_7z([str(sevenzip), "x", str(source), f"-o{extract_dir}", "-y"])

        level = _level(target_ext, quality)
        items = [str(path) for path in sorted(extract_dir.iterdir())]
        _run_7z(
            [
                str(sevenzip),
                "a",
                f"-t{archive_type}",
                f"-mx={level}",
                "-y",
                "-bso0",
                "-bsp0",
                str(output),
                *items,
            ]
        )


def _level(target_ext, quality):
    if target_ext == "zip":
        return int(quality.get("zip_level", 5))
    if target_ext == "7z":
        return int(quality.get("sevenzip_level", 5))
    return int(quality.get("archive_level", 5))


def _run_7z(args):
    completed = subprocess.run(args, capture_output=True, text=True)
    if completed.returncode != 0:
        raise ConverterError(completed.stderr.strip() or completed.stdout.strip() or "7-Zip 转换失败")
