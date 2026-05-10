from dataclasses import dataclass

from ..models import ConversionConfig
from ..pipeline import BookPipeline
from .markdown import polish_markdown


@dataclass(frozen=True)
class LambdaNoteBookPipeline(BookPipeline):
    def render_markdown(
        self,
        document: object,
        markdown: str,
        page_range: tuple[int, int] | None,
        section_key: str | None,
        config: ConversionConfig,
    ) -> str:
        return polish_markdown(markdown)
