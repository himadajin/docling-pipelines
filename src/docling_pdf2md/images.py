from pathlib import Path
import os

from .models import ImageExportConfig, ImageExportResult


def image_export_prefix(
    page_range: tuple[int, int] | None,
    section_key: str | None,
) -> str:
    if section_key:
        return section_key
    if page_range:
        start, end = page_range
        return f"range-p{start:03d}-p{end:03d}"
    return "full"


def image_relative_path(image_path: Path, output_markdown: Path) -> Path:
    output_parent = output_markdown.parent or Path(".")
    return Path(os.path.relpath(image_path, start=output_parent))


def remove_stale_images(output_dir: Path, prefix: str) -> None:
    if not output_dir.exists():
        return

    for path in output_dir.glob(f"{prefix}_p*.png"):
        if path.is_file():
            path.unlink()


def first_picture_page_no(picture: object) -> int | None:
    provenance = getattr(picture, "prov", None)
    if not provenance:
        return None

    return getattr(provenance[0], "page_no", None)


def save_document_images(
    document: object,
    output_markdown: Path,
    page_range: tuple[int, int] | None,
    section_key: str | None,
    config: ImageExportConfig,
) -> ImageExportResult:
    if not config.enabled:
        return ImageExportResult(enabled=False, output_dir=config.output_dir)

    pictures = list(getattr(document, "pictures", []))
    output_dir = config.output_dir
    prefix = image_export_prefix(page_range, section_key)

    output_dir.mkdir(parents=True, exist_ok=True)
    remove_stale_images(output_dir, prefix)

    page_counts: dict[int, int] = {}
    saved_count = 0

    for picture in pictures:
        page_no = first_picture_page_no(picture)
        if page_no is None:
            continue

        image = picture.get_image(document)
        if image is None:
            continue

        page_counts[page_no] = page_counts.get(page_no, 0) + 1
        filename = f"{prefix}_p{page_no:03d}_{page_counts[page_no]:03d}.png"
        image_path = output_dir / filename
        image.save(image_path)

        image_ref = getattr(picture, "image", None)
        if image_ref is not None:
            image_ref.uri = image_relative_path(image_path, output_markdown)
        saved_count += 1

    return ImageExportResult(
        enabled=True,
        output_dir=output_dir,
        saved_count=saved_count,
    )
