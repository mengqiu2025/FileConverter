from pathlib import Path

from PIL import Image


def convert_image(source, output, quality):
    source = Path(source)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(source) as image:
        target_ext = output.suffix.lower().lstrip(".")
        image = _prepare_image(image, target_ext)

        save_kwargs = {}
        if target_ext in {"jpg", "jpeg"}:
            save_kwargs["quality"] = int(quality.get("jpeg_quality", 95))
            save_kwargs["optimize"] = True
        elif target_ext == "webp":
            save_kwargs["lossless"] = bool(quality.get("webp_lossless", True))
        elif target_ext == "tif" or target_ext == "tiff":
            compression = quality.get("tiff_compression")
            if compression:
                save_kwargs["compression"] = compression
        elif target_ext == "ico":
            size = int(quality.get("ico_size", 256))
            image.thumbnail((size, size))

        image.save(output, format=_pillow_format(target_ext), **save_kwargs)


def _prepare_image(image, target_ext):
    if target_ext in {"jpg", "jpeg"} and image.mode not in {"RGB", "L"}:
        background = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode == "RGBA":
            background.paste(image, mask=image.getchannel("A"))
        else:
            background.paste(image.convert("RGB"))
        return background
    return image


def _pillow_format(ext):
    if ext in {"jpg", "jpeg"}:
        return "JPEG"
    if ext == "tif":
        return "TIFF"
    if ext == "ico":
        return "ICO"
    return ext.upper()
