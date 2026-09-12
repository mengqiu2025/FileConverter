from pathlib import Path

from app.core.errors import SameFormatError


def build_output_path(source, target_ext, output_dir=None, overwrite=False):
    source = Path(source)
    target_ext = target_ext.lower().lstrip(".")
    if source.suffix.lower() == f".{target_ext}":
        raise SameFormatError(
            f"源格式与目标格式相同，无需转换: {source.name}"
        )

    if output_dir is None:
        output_dir = source.parent / "converted"
    output_dir = Path(output_dir)

    candidate = output_dir / f"{source.stem}.{target_ext}"
    if overwrite or not candidate.exists():
        return candidate

    counter = 1
    while True:
        candidate = output_dir / f"{source.stem}_{counter}.{target_ext}"
        if not candidate.exists():
            return candidate
        counter += 1
