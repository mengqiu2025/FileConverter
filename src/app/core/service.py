from pathlib import Path

from app.core.config import load_config
from app.core.converters.archive import convert_archive
from app.core.converters.document import convert_document
from app.core.converters.image import convert_image
from app.core.converters.media import convert_media
from app.core.converters.pdf import convert_pdf
from app.core.engines import EngineManager
from app.core.paths import build_output_path
from app.core.routes import classify_file


class ConverterService:
    def __init__(self, app_dir, config_path=None):
        self.app_dir = Path(app_dir)
        self.config_path = Path(config_path) if config_path else self.app_dir / "config.json"
        self.config = load_config(self.config_path)
        self.engine_manager = EngineManager(
            self.app_dir,
            manual_paths=self.config.get("engines", {}),
        )

    def convert(self, source, target_ext, output_dir=None, overwrite=False):
        source = Path(source)
        target_ext = target_ext.lower().lstrip(".")
        category = classify_file(source)

        output_dir = self._resolve_output_dir(output_dir)
        output = build_output_path(source, target_ext, output_dir=output_dir, overwrite=overwrite)
        output.parent.mkdir(parents=True, exist_ok=True)

        if category == "image":
            convert_image(source, output, self.config["quality"]["image"])
        elif category == "document":
            if source.suffix.lower().lstrip(".") == "pdf":
                convert_pdf(source, output)
            else:
                convert_document(source, output)
        elif category in {"audio", "video"}:
            ffmpeg = self.engine_manager.resolve("ffmpeg")
            convert_media(source, output, ffmpeg, self.config["quality"][category])
        elif category == "archive":
            sevenzip = self.engine_manager.resolve("sevenzip")
            temp_dir = self.app_dir / self.config["temp"]["dir"]
            convert_archive(
                source,
                output,
                sevenzip,
                self.config["quality"]["archive"],
                temp_dir=temp_dir,
            )
        else:
            raise ValueError(f"无法处理该文件类别: {category}")

        return output

    def _resolve_output_dir(self, output_dir):
        if output_dir is not None:
            return output_dir
        output = self.config.get("output", {})
        if output.get("mode") == "custom" and output.get("custom_dir"):
            return Path(output["custom_dir"])
        return None
