#!/usr/bin/env python3
"""Validate permanent STP move stubs."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path

MARKER = re.compile(r"<!--\s*STP-MOVED-TO:\s*([^\s]+)\s*-->")
MOVED_HEADING = re.compile(r"^#\s+MOVED\s*$", re.MULTILINE)
LINK = re.compile(r"\[[^\]]+\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)")
PREFIX = "https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/blob/main/"
HTML_TAG_START = re.compile(r"<\s*(/?)\s*([A-Za-z][\w:-]*)")
VOID_TAGS = {"area", "base", "br", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def without_fenced_blocks(text: str) -> str:
    lines: list[str] = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines():
        opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence is None and opening:
            marker = opening.group(1)
            fence = (marker[0], len(marker))
        elif fence is not None:
            closing = re.fullmatch(rf" {{0,3}}{re.escape(fence[0])}{{{fence[1]},}}\s*", line)
            if closing:
                fence = None
        else:
            lines.append(line)
    return "\n".join(lines)


def without_inline_code(text: str) -> str:
    return re.sub(r"`+[^`]*`+", "", text)


def html_tags(text: str) -> list[tuple[int, int, bool, str]]:
    tags = []
    index = 0
    while index < len(text):
        if text[index] == "<":
            tag, next_index = parse_html_tag(text, index)
            if tag:
                tags.append(tag)
                index = tag[1]
                continue
            index = max(index + 1, next_index)
            continue
        index += 1
    return tags


def parse_html_tag(text: str, start: int) -> tuple[tuple[int, int, bool, str] | None, int]:
    match = HTML_TAG_START.match(text, start)
    if not match:
        return None, start + 1
    end = match.end()
    if end < len(text) and not text[end].isspace() and text[end] not in "/>":
        return None, start + 1
    quote: str | None = None
    while end < len(text):
        char = text[end]
        if quote:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == ">":
            return (start, end + 1, bool(match.group(1)), match.group(2).lower()), end + 1
        elif char == "<":
            return None, end
        end += 1
    return None, len(text)


def without_html_tags(text: str) -> str:
    removals: list[tuple[int, int]] = []
    stack: list[tuple[int, int, str]] = []
    for start, end, closing, name in html_tags(text):
        if closing:
            if stack and stack[-1][2] == name:
                removals.append((stack.pop()[0], end))
            else:
                removals.append((start, end))
        elif name in VOID_TAGS or text[start:end].rstrip().endswith("/"):
            removals.append((start, end))
        else:
            stack.append((start, end, name))
    removals.extend((start, end) for start, end, _ in stack)
    return remove_ranges(text, sorted(removals))


def remove_ranges(text: str, ranges: list[tuple[int, int]]) -> str:
    merged: list[tuple[int, int]] = []
    for start, end in ranges:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    result: list[str] = []
    current = 0
    for start, end in merged:
        result.append(text[current:start])
        current = end
    result.append(text[current:])
    return "".join(result)


def visible_markdown(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return without_inline_code(without_html_tags(text))


def target_from_link(source: Path, destination: str, root: Path) -> str | None:
    destination = destination.split("#", 1)[0].strip().strip("<>")
    if destination.startswith(PREFIX):
        return destination[len(PREFIX) :]
    if destination.startswith(("http://", "https://")):
        return None
    try:
        resolved = (source.parent / destination).resolve()
        relative = resolved.relative_to((root / "stps").resolve())
        return (Path("stps") / relative).as_posix()
    except (OSError, RuntimeError, ValueError):
        return None


def validate(root: Path, base_ref: str | None = None) -> list[str]:
    errors = root_errors(root)
    if errors:
        return errors
    stubs: dict[Path, str] = {}
    stps = root / "stps"
    for source in sorted(stps.rglob("*.md")):
        source_errors, target = validate_source(source, root, stps.resolve())
        errors.extend(source_errors)
        if target:
            stubs[source.relative_to(root)] = target
    if base_ref is not None:
        errors.extend(validate_base_ref(root, base_ref, stubs))
    return errors


def root_errors(root: Path) -> list[str]:
    stps = root / "stps"
    if not stps.exists() or not stps.is_dir():
        return ["stps: directory is missing"]
    if stps.is_symlink():
        return ["stps: symlinked STP roots are not allowed"]
    try:
        stps.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError):
        return ["stps: STP root must remain inside the repository"]
    return []


def validate_source(source: Path, root: Path, stps_root: Path) -> tuple[list[str], str | None]:
    relative = source.relative_to(root)
    if source.is_symlink():
        return [f"{relative}: symlinked STP paths are not allowed"], None
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return [f"{relative}: cannot read file: {error}"], None
    content = without_fenced_blocks(text)
    marker_content = without_html_tags(without_inline_code(content))
    visible = visible_markdown(content)
    markers = MARKER.findall(marker_content)
    if not markers:
        return moved_heading_error(relative, visible), None
    if len(markers) != 1:
        return [f"{relative}: expected exactly one STP-MOVED-TO marker"], None
    target = markers[0]
    errors, destination = validate_target(relative, target, root, stps_root)
    if not MOVED_HEADING.search(visible):
        errors.append(f"{relative}: missing '# MOVED' heading")
    if target not in rendered_links(source, content, root):
        errors.append(f"{relative}: add a link directly to {target}")
    return errors, target if destination else None


def moved_heading_error(relative: Path, visible: str) -> list[str]:
    if MOVED_HEADING.search(visible):
        return [f"{relative}: # MOVED requires an STP-MOVED-TO marker"]
    return []


def validate_target(relative: Path, target: str, root: Path, stps_root: Path) -> tuple[list[str], Path | None]:
    errors: list[str] = []
    target_path = Path(target)
    if any(ord(char) < 32 for char in target):
        return [f"{relative}: target must not contain control characters"], None
    candidate = root / target_path
    if candidate.is_symlink():
        try:
            candidate.resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as error:
            return [f"{relative}: cannot resolve target {target}: {error}"], None
        return [f"{relative}: symlinked targets are not allowed: {target}"], None
    try:
        destination = candidate.resolve()
    except (OSError, RuntimeError, ValueError) as error:
        return [f"{relative}: cannot resolve target {target}: {error}"], None
    try:
        destination.relative_to(stps_root)
    except ValueError:
        return [f"{relative}: target must remain under stps/"], None
    if invalid_target_path(target_path, target):
        return [f"{relative}: target must be a normalized Markdown path under stps/"], None
    if not destination.is_file():
        errors.append(f"{relative}: target does not exist: {target}")
    if destination == (root / relative).resolve():
        errors.append(f"{relative}: target points to the stub itself")
    if destination.is_file():
        target_error = target_is_stub(destination)
        if target_error:
            errors.append(f"{relative}: {target_error}: {target}")
    return errors, destination if destination.is_file() else None


def invalid_target_path(target_path: Path, target: str) -> bool:
    return (
        target_path.is_absolute()
        or target_path.as_posix() != target
        or ".." in target_path.parts
        or not target.startswith("stps/")
        or target_path.suffix != ".md"
    )


def target_is_stub(destination: Path) -> str | None:
    try:
        text = destination.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return f"cannot read target {destination}: {error}"
    content = without_html_tags(without_inline_code(without_fenced_blocks(text)))
    if MARKER.search(content):
        return "target is another moved stub"
    return None


def rendered_links(source: Path, content: str, root: Path) -> list[str | None]:
    rendered = visible_markdown(content)
    links: list[str | None] = []
    for match in LINK.finditer(rendered):
        if escaped_link(rendered, match.start()):
            continue
        links.append(target_from_link(source, match.group(1) or match.group(2), root))
    return links


def escaped_link(text: str, start: int) -> bool:
    backslashes = 0
    index = start - 1
    while index >= 0 and text[index] == "\\":
        backslashes += 1
        index -= 1
    if backslashes % 2:
        return True
    if index >= 0 and text[index] == "!":
        bang_slashes = 0
        index -= 1
        while index >= 0 and text[index] == "\\":
            bang_slashes += 1
            index -= 1
        return bang_slashes % 2 == 0
    return False


def valid_status(status: str) -> bool:
    if not status or status[0] not in "ACDMRTXUB":
        return False
    if status[0] in "RC":
        score = status[1:]
        return not score or len(score) <= 3 and score.isascii() and score.isdigit() and 0 <= int(score) <= 100
    return len(status) == 1


def validate_base_ref(root: Path, base_ref: str, stubs: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    if not base_ref:
        return ["base ref must not be empty"]
    if any(ord(char) < 32 for char in base_ref):
        return ["base ref must not contain control characters"]
    if base_ref.startswith("-"):
        return ["base ref must not start with '-'"]
    try:
        subprocess.run(["git", "rev-parse", "--verify", f"{base_ref}^{{commit}}"], cwd=root, capture_output=True, text=True, check=True)
        result = subprocess.run(["git", "diff", "-z", "--name-status", "--find-renames", "--relative", f"{base_ref}...HEAD", "--", "stps"], cwd=root, capture_output=True, check=True)
    except (OSError, ValueError, UnicodeError, subprocess.CalledProcessError) as error:
        return [f"cannot inspect base ref {base_ref}: {error}"]
    raw = result.stdout
    if raw and not raw.endswith(b"\0"):
        return ["malformed git diff status stream: missing NUL terminator"]
    fields = raw.split(b"\0")
    if fields and fields[-1] == b"":
        fields.pop()
    index = 0
    while index < len(fields):
        if not fields[index]:
            errors.append("malformed git diff status record: empty status")
            break
        status = os.fsdecode(fields[index])
        if not valid_status(status):
            errors.append(f"malformed git diff status record: {status!r}")
            break
        path_count = 2 if status[0] in "RC" else 1
        path_start = index + 1
        path_end = path_start + path_count
        paths = fields[path_start:path_end]
        if len(paths) != path_count or any(not path for path in paths):
            errors.append(f"malformed git diff status record: {status!r}")
            break
        deleted = os.fsdecode(paths[0])
        index = path_end
        if (status.startswith("R") or status == "D") and deleted.endswith(".md") and Path(deleted) not in stubs:
            errors.append(f"{deleted!r}: moved/deleted STPs must leave a permanent stub")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--base-ref", help="also reject deleted STP paths in this diff")
    args = parser.parse_args()
    errors = validate(args.root.resolve(), args.base_ref)
    if errors:
        print("STP move validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("STP move validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
