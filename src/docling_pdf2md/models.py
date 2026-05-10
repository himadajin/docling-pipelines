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
