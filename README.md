# Docling Pipelines

This uv project manages configured PDF-to-Markdown conversion pipelines with
Docling. Reusable conversion helpers live separately from source-specific
pipeline configuration and repair hooks.

## O'Reilly Japan pipelines

The currently configured pipelines convert these O'Reilly Japan PDFs. PDF files
are not included in this repository. Place legally obtained PDFs under `pdf/`
with these exact filenames:

```text
pdf/ISBN978-4-87311-758-4.pdf
pdf/ISBN978-4-87311-836-9.pdf
pdf/ISBN978-4-87311-906-9.pdf
```

The `pdf/` directory is ignored by Git except for its README. These pipelines
use hard-coded physical page ranges for reproducible section output.

## Usage

```bash
uv run docling-books-758-4 --help
uv run docling-books-758-4 --pages 1-2
uv run docling-books-758-4 --section chapter-01
uv run docling-books-758-4 --all-sections
```

Equivalent book-specific commands are available for the other configured books:

```bash
uv run docling-books-836-9 --section chapter-01
uv run docling-books-906-9 --section stage-01
```

Generic pipeline orchestration, Markdown polish, and shared models live under
`src/docling_pipelines/`. O'Reilly-specific PDF paths, section boundaries,
output roots, pipeline choices, and repair hooks live under
`src/docling_pipelines/oreilly/`. Low-level Docling conversion helpers live
under `src/docling_pdf2md/`.

For the current O'Reilly pipelines, generated section Markdown is written to
`books/<isbn>/`, including extracted images under `books/<isbn>/images/`. Ad
hoc page-range output is written under `output/<isbn>/ranges/`. These generated
outputs are ignored by Git.

For a custom output path:

```bash
uv run docling-books-758-4 --pages 21-40 --output output/978-4-87311-758-4/ranges/chapter-01-test.md
uv run docling-books-758-4 --section chapter-01 --output books/978-4-87311-758-4/03-chapter-01.md
```

OCR is disabled by default because these PDFs already contain extractable
embedded text. Use `--ocr` only for comparison or investigation.
