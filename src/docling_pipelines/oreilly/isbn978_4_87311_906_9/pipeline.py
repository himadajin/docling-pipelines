from ...pipeline import BookPipeline
from ..repairs.isbn978_4_87311_906_9.index import apply_known_index_repairs
from ..repairs.isbn978_4_87311_906_9.toc import repair_toc_entries
from ..specs.isbn978_4_87311_906_9 import SPEC

PIPELINE = BookPipeline(
    spec=SPEC,
    index_source="pdf-layout",
    toc_repairs=(repair_toc_entries,),
    index_repairs=(apply_known_index_repairs,),
)
