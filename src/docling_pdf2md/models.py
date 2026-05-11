from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MarkdownExportConfig:
    escape_html: bool = True
    escape_underscores: bool = True


@dataclass(frozen=True)
class ImageExportConfig:
    enabled: bool = True
    output_dir: Path = Path("images")
    images_scale: float = 2.0


@dataclass(frozen=True)
class ImageExportResult:
    enabled: bool
    output_dir: Path
    saved_count: int = 0


@dataclass(frozen=True)
class ConversionProfile:
    docling_convert_seconds: float
    document_transform_seconds: float
    image_save_seconds: float
    markdown_export_seconds: float
    markdown_render_seconds: float
    markdown_write_seconds: float

    @property
    def measured_seconds(self) -> float:
        return (
            self.docling_convert_seconds
            + self.document_transform_seconds
            + self.image_save_seconds
            + self.markdown_export_seconds
            + self.markdown_render_seconds
            + self.markdown_write_seconds
        )
