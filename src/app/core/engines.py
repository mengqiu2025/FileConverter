import shutil
from pathlib import Path

from app.core.errors import EngineNotFoundError


ENGINE_SPECS = {
    "ffmpeg": {
        "names": ("ffmpeg.exe", "ffmpeg"),
        "bundled": ("tools", "ffmpeg", "bin"),
    },
    "sevenzip": {
        "names": ("7z.exe", "7za.exe", "7z"),
        "bundled": ("tools", "sevenzip"),
    },
    "libreoffice": {
        "names": ("soffice.exe", "soffice"),
        "bundled": ("tools", "libreoffice", "program"),
    },
}


class EngineManager:
    def __init__(self, app_dir, manual_paths=None):
        self.app_dir = Path(app_dir)
        self.manual_paths = manual_paths or {}

    def resolve(self, engine_name):
        spec = ENGINE_SPECS[engine_name]

        manual = self.manual_paths.get(engine_name)
        if manual:
            manual = Path(manual)
            if manual.is_file():
                return manual
            raise EngineNotFoundError(f"手动指定的引擎不存在: {manual}")

        bundled_dir = self.app_dir.joinpath(*spec["bundled"])
        for name in spec["names"]:
            bundled = bundled_dir / name
            if bundled.is_file():
                return bundled

        for name in spec["names"]:
            found = shutil.which(name)
            if found:
                return Path(found)

        raise EngineNotFoundError(f"找不到外部引擎: {engine_name}")
