from ..pipeline import OReillyBookPipeline
from ..repairs.isbn978_4_87311_758_4.document import apply_document_repairs
from ..repairs.isbn978_4_87311_758_4.index import (
    apply_known_index_repairs,
    split_known_pending_index_terms,
)
from ..repairs.isbn978_4_87311_758_4.markdown import apply_markdown_repairs
from ..repairs.isbn978_4_87311_758_4.toc import repair_toc_entries
from ..specs.isbn978_4_87311_758_4 import SPEC

PIPELINE = OReillyBookPipeline(
    spec=SPEC,
    index_source="docling-tables",
    document_repairs=(apply_document_repairs,),
    markdown_repairs=(apply_markdown_repairs,),
    toc_repairs=(repair_toc_entries,),
    index_repairs=(apply_known_index_repairs,),
    pending_index_term_splitter=split_known_pending_index_terms,
)
