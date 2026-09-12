from pathlib import Path


DOCUMENT_EXTENSIONS = {
    "docx",
    "doc",
    "xlsx",
    "xls",
    "pptx",
    "ppt",
    "pdf",
    "txt",
    "md",
    "csv",
    "html",
    "htm",
}
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "gif", "tif", "tiff", "webp", "ico"}
AUDIO_EXTENSIONS = {"mp3", "wav", "flac", "aac", "m4a", "ogg", "opus"}
VIDEO_EXTENSIONS = {"mp4", "mkv", "mov", "avi", "webm", "m4v"}
ARCHIVE_EXTENSIONS = {"zip", "7z", "tar", "gz", "bz2", "xz", "rar"}


def classify_file(path):
    ext = Path(path).suffix.lower().lstrip(".")
    if ext in DOCUMENT_EXTENSIONS:
        return "document"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    if ext in VIDEO_EXTENSIONS:
        return "video"
    if ext in ARCHIVE_EXTENSIONS:
        return "archive"
    raise ValueError(f"不支持的文件格式: {ext or '无扩展名'}")


def get_default_target(category, defaults):
    return defaults[category]


def get_supported_targets(source_ext, lib=(), libreoffice_available=False):
    source_ext = source_ext.lower().lstrip(".")

    if source_ext == "pdf":
        targets = ["docx", "txt", "md", "png", "jpg"]
        return [target for target in targets if _is_pdf_target_available(target, lib)]

    if source_ext in IMAGE_EXTENSIONS:
        return ["png", "jpg", "bmp", "gif", "tif", "webp", "ico", "pdf"]

    if source_ext == "docx":
        targets = ["txt", "md", "html"]
        if libreoffice_available:
            targets.append("pdf")
        return targets

    if source_ext == "xlsx":
        targets = ["csv", "pdf"]
        if not libreoffice_available:
            targets = ["csv"]
        return targets

    if source_ext == "csv":
        return ["xlsx", "pdf"]

    if source_ext in {"txt", "md", "html", "htm"}:
        return ["pdf", "docx", "txt", "md", "html"]

    if source_ext in AUDIO_EXTENSIONS:
        return ["mp3", "wav", "flac", "aac", "m4a", "ogg", "opus"]

    if source_ext in VIDEO_EXTENSIONS:
        targets = ["mp4", "mkv", "webm", "mp3", "wav", "aac", "m4a"]
        return targets

    if source_ext in ARCHIVE_EXTENSIONS:
        return ["zip", "7z", "tar", "gz", "bz2", "xz"]

    raise ValueError(f"不支持的文件格式: {source_ext}")


def _is_pdf_target_available(target, lib):
    if target in {"png", "jpg"}:
        return "fitz" in lib
    if target == "docx":
        return "fitz" in lib and "docx" in lib
    if target in {"txt", "md"}:
        return "fitz" in lib
    return False
