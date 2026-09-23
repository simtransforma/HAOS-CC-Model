#!/usr/bin/env python3
"""Read-only structural size scanner for multi-stack source trees."""

import argparse
import json
import os
import sys
from pathlib import Path


CODE_EXTENSIONS = frozenset(
    {
        ".bash", ".c", ".cc", ".clj", ".cljs", ".cmd", ".cpp", ".cs", ".css", ".cxx",
        ".dart", ".ex", ".exs", ".erl", ".fs", ".fsx", ".go", ".groovy",
        ".h", ".hh", ".hpp", ".hrl", ".htm", ".html", ".java", ".js", ".jsx", ".kt",
        ".kts", ".less", ".lua", ".m", ".mjs", ".mm", ".php", ".ps1", ".psd1",
        ".psm1", ".py", ".pyi", ".r", ".rb", ".rs", ".sass", ".scala", ".scss", ".sh",
        ".sol", ".sql", ".svelte", ".swift", ".tf", ".tfvars", ".ts", ".tsx", ".vue", ".zsh",
    }
)

IGNORED_DIRECTORIES = frozenset(
    {
        ".cache", ".git", ".gradle", ".idea", ".mypy_cache", ".next",
        ".nuxt", ".parcel-cache", ".pytest_cache", ".ruff_cache",
        ".svelte-kit", ".terraform", ".tox", ".venv", ".yarn",
        "__pycache__", "artifacts", "bower_components", "build", "cache",
        "caches", "coverage", "deps", "dist", "env", "generated", "gen",
        "node_modules", "obj", "out", "target", "temp", "tmp", "vendor",
        "vendors", "venv",
    }
)

IGNORED_FILE_NAMES = frozenset(
    {
        "bun.lock", "bun.lockb", "cargo.lock", "composer.lock", "gemfile.lock",
        "package-lock.json", "pipfile.lock", "pnpm-lock.yaml", "poetry.lock",
        "uv.lock", "yarn.lock",
    }
)

GENERATED_NAME_MARKERS = (
    ".designer.",
    ".g.",
    ".generated.",
    ".pb.",
    "-generated.",
    "_generated.",
    "_pb2.py",
    "_pb2_grpc.py",
)

NOTICE = (
    "File size is a triage signal only; exceeding the line limit does not prove "
    "technical debt or justify refactoring."
)


def positive_integer(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def stable_key(value):
    text = str(value)
    return (text.casefold(), text)


def is_link_or_junction(path):
    if path.is_symlink():
        return True
    is_junction = getattr(os.path, "isjunction", None)
    return bool(is_junction and is_junction(path))


def is_ignored_file(path):
    name = path.name.casefold()
    if name in IGNORED_FILE_NAMES or path.suffix.casefold() == ".lock":
        return True
    if ".min." in name or "-min." in name:
        return True
    return any(marker in name for marker in GENERATED_NAME_MARKERS)


def count_lines(path):
    total = 0
    non_empty = 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            total += 1
            if line.strip():
                non_empty += 1
    return total, non_empty


def discover_source_files(root, excluded_paths=None, on_error=None):
    excluded = {Path(item).resolve() for item in (excluded_paths or ())}
    discovered = []

    def record_error(error):
        if on_error is not None:
            on_error(error)

    for current, directories, filenames in os.walk(
        root, topdown=True, followlinks=False, onerror=record_error
    ):
        current_path = Path(current)
        directories[:] = sorted(
            (
                name
                for name in directories
                if name.casefold() not in IGNORED_DIRECTORIES
                and not is_link_or_junction(current_path / name)
            ),
            key=stable_key,
        )
        for filename in sorted(filenames, key=stable_key):
            path = current_path / filename
            if path.suffix.casefold() not in CODE_EXTENSIONS:
                continue
            if is_link_or_junction(path) or is_ignored_file(path):
                continue
            if path.resolve() in excluded:
                continue
            discovered.append(path)

    return sorted(discovered, key=lambda path: stable_key(path.relative_to(root).as_posix()))


def scan_project(root, max_lines=350, excluded_paths=None):
    root = Path(root).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root must be a directory")

    traversal_errors = []
    unreadable_files = 0
    scanned_files = 0
    aggregate_total = 0
    aggregate_non_empty = 0
    candidates = []

    for path in discover_source_files(root, excluded_paths, traversal_errors.append):
        try:
            total_lines, non_empty_lines = count_lines(path)
        except OSError:
            unreadable_files += 1
            continue

        scanned_files += 1
        aggregate_total += total_lines
        aggregate_non_empty += non_empty_lines
        if total_lines > max_lines:
            candidates.append(
                {
                    "candidate": True,
                    "non_empty_lines": non_empty_lines,
                    "path": path.relative_to(root).as_posix(),
                    "total_lines": total_lines,
                }
            )

    return {
        "candidates": candidates,
        "max_lines": max_lines,
        "notice": NOTICE,
        "root": root.as_posix(),
        "summary": {
            "candidate_count": len(candidates),
            "non_empty_lines": aggregate_non_empty,
            "scanned_files": scanned_files,
            "skipped_unreadable": unreadable_files + len(traversal_errors),
            "total_lines": aggregate_total,
        },
    }


def render_json(report):
    return json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def escape_markdown(value):
    return str(value).replace("|", "\\|")


def render_markdown(report):
    summary = report["summary"]
    lines = [
        "# Structural Risk Scan",
        "",
        f"- Root: `{escape_markdown(report['root'])}`",
        f"- Maximum lines: {report['max_lines']}",
        f"- Scanned files: {summary['scanned_files']}",
        f"- Total lines: {summary['total_lines']}",
        f"- Non-empty lines: {summary['non_empty_lines']}",
        f"- Candidates: {summary['candidate_count']}",
        f"- Skipped unreadable: {summary['skipped_unreadable']}",
        "",
        f"> {report['notice']}",
        "",
    ]
    if report["candidates"]:
        lines.extend(
            [
                "| Candidate | Total lines | Non-empty lines | Path |",
                "|---|---:|---:|---|",
            ]
        )
        for item in report["candidates"]:
            candidate_path = escape_markdown(item["path"])
            lines.append(
                f"| yes | {item['total_lines']} | {item['non_empty_lines']} | "
                f"`{candidate_path}` |"
            )
    else:
        lines.append("No files exceeded the configured line limit.")
    return "\n".join(lines) + "\n"


def build_parser():
    parser = argparse.ArgumentParser(
        description="Find large source files without changing the scanned project."
    )
    parser.add_argument("root", help="source tree root")
    parser.add_argument("--max-lines", type=positive_integer, default=350)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", help="new report file; existing files are not overwritten")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    output_path = Path(args.output).expanduser().resolve() if args.output else None
    try:
        if output_path is not None and output_path.exists():
            raise ValueError("output file already exists")
        report = scan_project(
            args.root,
            max_lines=args.max_lines,
            excluded_paths=(() if output_path is None else (output_path,)),
        )
        rendered = render_json(report) if args.format == "json" else render_markdown(report)
        if output_path is None:
            sys.stdout.write(rendered)
        else:
            with output_path.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
