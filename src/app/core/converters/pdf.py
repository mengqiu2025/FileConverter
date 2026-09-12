from pathlib import Path

import contextlib
import io
import warnings
import pymupdf as fitz

with contextlib.redirect_stderr(io.StringIO()), warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from pdf2docx import Converter


def convert_pdf(source, output):
    source = Path(source)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    target_ext = output.suffix.lower().lstrip(".")

    if target_ext in {"png", "jpg", "jpeg"}:
        _pdf_to_image(source, output, target_ext)
    elif target_ext == "docx":
        _pdf_to_docx(source, output)
    elif target_ext == "txt":
        _pdf_to_text(source, output)
    else:
        raise ValueError(f"暂不支持 PDF 转换到 .{target_ext}")


def _pdf_to_text(source, output):
    document = fitz.open(source)
    try:
        text = "\n".join(page.get_text() for page in document)
        output.write_text(text, encoding="utf-8")
    finally:
        document.close()


def _pdf_to_image(source, output, target_ext):
    document = fitz.open(source)
    try:
        page = document[0]
        pixmap = page.get_pixmap(dpi=150)
        pixmap.save(output)
    finally:
        document.close()


def _pdf_to_docx(source, output):
    converter = Converter(str(source))
    try:
        converter.convert(str(output))
    finally:
        converter.close()
