from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, Pattern

from ..paths import PROJECT_ROOT
from .catalog import ISBN978_4_908686_06_1, ISBN978_4_908686_16_0


JAPANESE_TEXT_CHARS = (
    r"\u3040-\u30ff"
    r"\u3400-\u4dbf"
    r"\u4e00-\u9fff"
    r"\uf900-\ufaff"
    r"\u2e80-\u2fff"
    r"々〆〤"
)


@dataclass(frozen=True)
class AuditIssue:
    name: str
    pattern: Pattern[str]
    description: str


@dataclass(frozen=True)
class AuditFinding:
    path: Path
    line_number: int
    issue: str
    text: str


AUDIT_ISSUES: tuple[AuditIssue, ...] = (
    AuditIssue(
        "watermark",
        re.compile(r"^\s*★(?:\s|$)|★\s"),
        "watermark/hash noise",
    ),
    AuditIssue(
        "running_header",
        re.compile(r"^##\s+\d+\s+第\s*\d+\s*章\b"),
        "page number running header",
    ),
    AuditIssue(
        "glyph",
        re.compile(r"glyph\[[^]]+\]"),
        "unrepaired glyph marker",
    ),
    AuditIssue(
        "cjk_radical",
        re.compile(r"[\u2e80-\u2fff]"),
        "Kangxi/CJK radical compatibility character",
    ),
    AuditIssue(
        "japanese_spacing",
        re.compile(rf"[{JAPANESE_TEXT_CHARS}] +[{JAPANESE_TEXT_CHARS}]"),
        "suspicious internal Japanese spacing",
    ),
    AuditIssue(
        "formula_not_decoded",
        re.compile(r"<!--\s*formula-not-decoded\s*-->"),
        "undecoded formula placeholder",
    ),
    AuditIssue(
        "command_heading",
        re.compile(r"^##\s+\$"),
        "command line misrecognized as heading",
    ),
    AuditIssue(
        "code_listing_heading",
        re.compile(r"^##\s+リスト\s+\d+(?:\.\d+)?\s*[:：]"),
        "code listing caption misrecognized as heading",
    ),
    AuditIssue(
        "figure_caption_heading",
        re.compile(r"^##\s+▲\s*図\s+\d+(?:\.\d+)?\b"),
        "figure caption misrecognized as heading",
    ),
    AuditIssue(
        "table_caption_heading",
        re.compile(r"^##\s+表\s+\d+(?:\.\d+)?\b"),
        "table caption misrecognized as heading",
    ),
)


DEFAULT_ROOTS = (
    PROJECT_ROOT / ISBN978_4_908686_06_1.output_root,
    PROJECT_ROOT / ISBN978_4_908686_16_0.output_root,
)


def markdown_files(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".md":
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
    return sorted(files)


def audit_markdown_file(path: Path) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for issue in AUDIT_ISSUES:
            if issue.pattern.search(line):
                findings.append(
                    AuditFinding(
                        path=path,
                        line_number=line_number,
                        issue=issue.name,
                        text=line.strip(),
                    )
                )
    return findings


def audit_paths(paths: Iterable[Path]) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for path in markdown_files(paths):
        findings.extend(audit_markdown_file(path))
    return findings


def issue_totals(findings: Iterable[AuditFinding]) -> dict[str, int]:
    totals = {issue.name: 0 for issue in AUDIT_ISSUES}
    for finding in findings:
        totals[finding.issue] += 1
    return totals


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def format_audit_report(findings: list[AuditFinding], sample_limit: int = 40) -> str:
    totals = issue_totals(findings)
    lines = ["Lambda Note Markdown audit", "", "Issue totals:"]
    for issue in AUDIT_ISSUES:
        lines.append(f"  {issue.name}: {totals[issue.name]}")

    if findings:
        lines.extend(["", f"Samples (first {min(sample_limit, len(findings))}):"])
        for finding in findings[:sample_limit]:
            lines.append(
                f"{display_path(finding.path)}:{finding.line_number}: "
                f"{finding.issue}: {finding.text}"
            )

    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit generated Lambda Note Markdown for known quality issues."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Markdown files or directories to audit. Defaults to both Lambda Note books.",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=40,
        help="Maximum number of finding samples to print.",
    )
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit with status 1 when any finding is detected.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths = tuple(args.paths) if args.paths else DEFAULT_ROOTS
    findings = audit_paths(path if path.is_absolute() else PROJECT_ROOT / path for path in paths)
    print(format_audit_report(findings, args.sample_limit))
    if args.fail_on_findings and findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
