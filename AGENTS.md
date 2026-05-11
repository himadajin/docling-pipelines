# AGENTS.md

## Project

This is a `uv` Python project for configured PDF-to-Markdown conversion
pipelines with Docling.

Current O'Reilly Japan PDFs:

```text
pdf/ISBN978-4-87311-758-4.pdf
pdf/ISBN978-4-87311-836-9.pdf
pdf/ISBN978-4-87311-906-9.pdf
```

Current Lambda Note PDFs:

```text
pdf/ISBN978-4-908686-06-1.pdf
pdf/ISBN978-4-908686-16-0.pdf
```

Pipeline configuration can be specialized by source or book. Hard-coded physical
page ranges are acceptable when they improve reproducibility.

## Files

- `src/docling_pdf2md/`: reusable Docling PDF-to-Markdown conversion helpers
- `src/docling_pipelines/`: reusable pipeline orchestration, CLI parsing,
  models, and shared helpers
- `src/docling_pipelines/oreilly/`: O'Reilly-specific PDF paths, sections,
  output roots, pipelines, Markdown rendering, style transforms, and repair hooks
- `src/docling_pipelines/lambda_note/`: Lambda Note-specific PDF paths,
  sections, output roots, and pipelines
- `pdf/`: local input PDFs, ignored by Git except for `pdf/README.md`
- `books/<isbn>/`: current O'Reilly section-split Markdown output
- `output/<isbn>/ranges/`: current O'Reilly ad hoc page-range Markdown output

## Commands

Use `uv run` for all Python execution.

```bash
uv run docling-books-758-4 --help
uv run docling-books-758-4 --pages 1-2
uv run docling-books-758-4 --section chapter-01
uv run docling-books-758-4 --all-sections
uv run docling-lambdanote-06-1 --section chapter-01
uv run docling-lambdanote-16-0 --section chapter-01
uv run python -m compileall -q src tests
```

For a custom output path:

```bash
uv run docling-books-758-4 --pages 21-40 --output output/978-4-87311-758-4/ranges/chapter-01-test.md
uv run docling-books-758-4 --section chapter-01 --output books/978-4-87311-758-4/03-chapter-01.md
```

## OCR Policy

OCR is disabled by default.

Reason: these PDFs already contain extractable embedded text. Use OCR only for
comparison or investigation:

```bash
uv run docling-books-758-4 --pages 1-2 --ocr --output output/978-4-87311-758-4/ranges/smoke_ocr_enabled.md
```

The script prints `OCR: off` or `OCR: on` in its result summary.

## Table Mode Policy

Docling table structure mode defaults to `accurate`.

Use `--table-mode fast` or `--table-mode off` only for speed comparison or
targeted investigation. They can be much faster, but 758's TOC showed meaningful
Markdown quality regressions: `fast` dropped or merged TOC entries, and `off`
lost most TOC structure.

The script prints `Table mode: accurate`, `Table mode: fast`, or
`Table mode: off` in its result summary.

## Section Boundaries

Docling page ranges are 1-based and inclusive. Current physical page ranges are
defined in the O'Reilly pipeline modules under `src/docling_pipelines/oreilly/`.

## Verification

After changing CLI or conversion behavior, run:

```bash
uv run python -m compileall -q src tests
uv run docling-books-758-4 --help
uv run docling-books-758-4 --pages 1-2 --output output/978-4-87311-758-4/ranges/smoke.md
```

When validating section conversion:

```bash
uv run docling-books-758-4 --all-sections
wc -c books/*/*.md
wc -l books/*/*.md
```

When changing conversion scripts and regenerating `books/`, take a snapshot
after conversion as a backup. Store snapshots under:

```text
snapshots/<MM-DD-HHMM-{before|after}-short-label>/<generated-output-dir>
```

Use a short label that makes both the timing and change clear, for example
`snapshots/05-11-2103-after-cjk-radical-normalize/978-4-908686-06-1`.
Copy each regenerated output directory under the snapshot directory using the
same basename it has under `books/` or `output/`.

For a full OCR/no-OCR comparison, write OCR-enabled output to a separate
directory and use `diff -qr` rather than visual inspection.

## Editing Guidelines

- Keep reusable CLI parsing in `src/docling_pipelines/cli.py`.
- Keep Docling-specific conversion helpers in `src/docling_pdf2md/`.
- Keep O'Reilly-specific PDF paths, section definitions, output roots, pipeline
  choices, Markdown rendering, style transforms, and known repairs in
  `src/docling_pipelines/oreilly/`.
- Keep Lambda Note-specific PDF paths, section definitions, output roots, and
  pipeline choices in `src/docling_pipelines/lambda_note/`.
- Prefer small, reproducible changes and verify with a short page range before
  converting the full PDF.
- Do not make OCR the default unless a future diff shows missing content without
  OCR.
- Generated Markdown under `books/<isbn>/` is conversion output. Do not
  hand-edit it; update package code and regenerate Markdown instead.
- Generated Markdown under `output/` can be regenerated; avoid treating it as
  source code.
- PDFs under `pdf/` are local copyrighted inputs and must not be committed.
