from .converter import export_document_markdown
from .models import ImageExportConfig, MarkdownExportConfig


def export_markdown_for_range(
    document: object,
    markdown: MarkdownExportConfig,
    images: ImageExportConfig,
) -> str:
    return export_document_markdown(
        document,
        markdown,
        include_images=images.enabled,
    )
