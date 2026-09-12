import subprocess
from pathlib import Path

from app.core.errors import ConverterError


def convert_media(source, output, ffmpeg, quality):
    source = Path(source)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    target_ext = output.suffix.lower().lstrip(".")
    args = [str(ffmpeg), "-hide_banner", "-loglevel", "error", "-y", "-i", str(source)]
    args.extend(_target_args(target_ext, quality))
    args.append(str(output))

    completed = subprocess.run(args, capture_output=True, text=True)
    if completed.returncode != 0:
        raise ConverterError(completed.stderr.strip() or "FFmpeg 转换失败")


def _target_args(target_ext, quality):
    if target_ext == "mp3":
        return ["-vn", "-codec:a", "libmp3lame", "-b:a", str(quality.get("mp3_bitrate", "320k"))]
    if target_ext == "wav":
        return ["-vn", "-codec:a", "pcm_s16le"]
    if target_ext == "flac":
        return ["-vn", "-codec:a", "flac"]
    if target_ext in {"aac", "m4a"}:
        return ["-vn", "-codec:a", "aac", "-b:a", str(quality.get("aac_bitrate", "256k"))]
    if target_ext in {"ogg", "opus"}:
        return ["-vn", "-codec:a", "libopus", "-b:a", str(quality.get("opus_bitrate", "192k"))]

    if target_ext == "mp4":
        return [
            "-codec:v",
            "libx264",
            "-crf",
            str(quality.get("h264_crf", 23)),
            "-preset",
            str(quality.get("h264_preset", "medium")),
            "-codec:a",
            "aac",
            "-b:a",
            str(quality.get("audio_bitrate", "192k")),
        ]
    if target_ext == "mkv":
        return [
            "-codec:v",
            "libx264",
            "-crf",
            str(quality.get("h264_crf", 23)),
            "-preset",
            str(quality.get("h264_preset", "medium")),
            "-codec:a",
            "aac",
            "-b:a",
            str(quality.get("audio_bitrate", "192k")),
        ]
    if target_ext == "webm":
        return [
            "-codec:v",
            "libvpx-vp9",
            "-crf",
            str(quality.get("webm_crf", 32)),
            "-b:v",
            "0",
            "-codec:a",
            "libopus",
            "-b:a",
            str(quality.get("webm_opus_bitrate", "128k")),
        ]

    raise ValueError(f"暂不支持媒体转换到 .{target_ext}")
