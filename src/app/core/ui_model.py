from dataclasses import dataclass, field
from pathlib import Path

from app.core.routes import classify_file, get_default_target, get_supported_targets


@dataclass
class FileItem:
    path: Path
    category: str
    target_ext: str
    supported_targets: list[str]
    available: bool = True
    reason: str = ""
    status: str = "pending"
    error: str | None = None


def build_file_item(path, config, libreoffice_available=False):
    path = Path(path)
    category = classify_file(path)
    source_ext = path.suffix.lower().lstrip(".")
    default_target = get_default_target(category, config["defaults"])
    targets = get_supported_targets(
        source_ext,
        lib=("fitz", "docx", "PIL"),
        libreoffice_available=libreoffice_available,
    )
    available = default_target in targets
    reason = "" if available else "需要可选文档引擎"
    return FileItem(
        path=path,
        category=category,
        target_ext=default_target,
        supported_targets=targets,
        available=available,
        reason=reason,
    )
