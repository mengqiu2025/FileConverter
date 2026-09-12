import json
from copy import deepcopy
from pathlib import Path


DEFAULT_CONFIG = {
    "defaults": {
        "document": "pdf",
        "image": "png",
        "video": "mp4",
        "audio": "mp3",
        "archive": "zip",
    },
    "quality": {
        "image": {
            "jpeg_quality": 95,
            "webp_lossless": True,
            "tiff_compression": None,
            "ico_size": 256,
        },
        "audio": {
            "mp3_bitrate": "320k",
            "aac_bitrate": "256k",
            "opus_bitrate": "192k",
        },
        "video": {
            "h264_crf": 23,
            "h264_preset": "medium",
            "audio_bitrate": "192k",
            "webm_crf": 32,
            "webm_opus_bitrate": "128k",
        },
        "archive": {
            "zip_method": "deflate",
            "zip_level": 5,
            "sevenzip_method": "LZMA2",
            "sevenzip_level": 5,
        },
    },
    "output": {
        "mode": "converted",
        "custom_dir": None,
        "overwrite": False,
    },
    "execution": {
        "parallel": False,
        "max_workers": 0,
    },
    "engines": {
        "ffmpeg": None,
        "sevenzip": None,
        "libreoffice": None,
    },
    "logs": {
        "retention_days": 30,
    },
    "temp": {
        "dir": "temp",
        "auto_clean_on_exit": False,
    },
}


def load_config(path):
    path = Path(path)
    if not path.exists():
        return deepcopy(DEFAULT_CONFIG)

    with path.open("r", encoding="utf-8") as handle:
        stored = json.load(handle)
    return _merge_defaults(stored)


def save_config(config, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, ensure_ascii=False, indent=2)


def _merge_defaults(stored):
    merged = deepcopy(DEFAULT_CONFIG)
    for key, value in stored.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged
