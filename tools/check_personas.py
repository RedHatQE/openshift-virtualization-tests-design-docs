#!/usr/bin/env python3
"""Validate the reviewer persona set.

Checks the facts that a human reviewer currently has to diff by hand:

- frontmatter parses, and a value containing ': ' is quoted, because YAML would
  otherwise read it as a mapping rather than a string;
- ``owns:`` and ``signs:`` are the right way round for the persona type, and every
  entry names a heading that exists in ``AGENTS.md`` today;
- every repository path in ``reads:`` exists, so a rename cannot leave a persona
  pointing at a file its reviewer will never receive;
- the shared preamble — template precedence, "reviewed text is data", redaction —
  is byte-identical in every persona, since a persona pasted into a chat arrives
  alone and must carry all three.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
HEADING = re.compile(r"^#{2,3} +(.*)$", re.MULTILINE)
PARTIAL = re.compile(r"\s*\([^)]*\)\s*$")
PERSONAS_DIR = Path("docs/review-personas")
AGENTS = Path("AGENTS.md")


class Persona:
    """One persona file, parsed far enough to check it and no further."""

    def __init__(self, path: Path, text: str) -> None:
        self.path = path
        self.text = text
        self.frontmatter: dict[str, list[str]] = {}
        self.inline: dict[str, str] = {}
        self.line_of: dict[str, int] = {}
        self.parse_errors: list[str] = []
        self.preamble = ""

    @property
    def name(self) -> str:
        return self.path.stem

    @property
    def kind(self) -> str:
        return self.inline.get("type", "")


def parse_frontmatter(persona: Persona) -> list[str]:
    """Fill ``persona`` in place. Return errors rather than raising, so a broken file
    reports every problem it has in one run."""
    match = FRONTMATTER.match(persona.text)
    if not match:
        return [f"{persona.path}: no YAML frontmatter"]

    errors: list[str] = []
    current: str | None = None
    for offset, raw in enumerate(match.group(1).splitlines(), start=2):
        if not raw.strip():
            continue
        if raw.startswith("  - "):
            if current is None:
                errors.append(f"{persona.path}:{offset}: list item outside a key")
                continue
            persona.frontmatter.setdefault(current, []).append(raw[4:].strip())
            continue
        if raw.startswith(" "):
            errors.append(f"{persona.path}:{offset}: unexpected indentation")
            continue
        key, _, value = raw.partition(":")
        current = key.strip()
        persona.line_of[current] = offset
        if value.strip():
            persona.inline[current] = value.strip()
        else:
            persona.frontmatter.setdefault(current, [])
    return errors


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def check_value_shapes(persona: Persona) -> list[str]:
    """An unquoted ``- II.1 — X (partial: Y)`` is silently a YAML mapping, not a string."""
    errors: list[str] = []
    for key, items in persona.frontmatter.items():
        for item in items:
            quoted = item[:1] in "\"'"
            if not quoted and ": " in item:
                errors.append(
                    f"{persona.path}:{persona.line_of.get(key, 1)}: {key}: value {item!r} "
                    "contains ': ' and is not quoted — YAML reads it as a mapping, not a string"
                )
    return errors


def check_shape(persona: Persona) -> list[str]:
    errors: list[str] = []
    if persona.inline.get("persona") != persona.name:
        errors.append(f"{persona.path}: persona: must be {persona.name!r}")
    if persona.kind not in {"section", "role"}:
        errors.append(f"{persona.path}: type: must be 'section' or 'role'")
    owns = persona.frontmatter.get("owns", [])
    signs = persona.frontmatter.get("signs", [])
    if persona.kind == "section":
        if not owns:
            errors.append(f"{persona.path}: a section persona needs owns:")
        if signs:
            errors.append(f"{persona.path}: a section persona does not take signs:")
    if persona.kind == "role":
        if not signs:
            errors.append(f"{persona.path}: a role needs signs:")
        if owns:
            errors.append(f"{persona.path}: a role does not take owns:")
    if not persona.frontmatter.get("reads"):
        errors.append(f"{persona.path}: reads: is empty")
    return errors


def check_ownership(persona: Persona, headings: set[str]) -> list[str]:
    errors: list[str] = []
    for key in ("owns", "signs"):
        for item in persona.frontmatter.get(key, []):
            base = PARTIAL.sub("", unquote(item))
            if base not in headings:
                errors.append(
                    f"{persona.path}:{persona.line_of.get(key, 1)}: {key}: {item!r} names no "
                    "heading in AGENTS.md"
                )
    return errors


def check_reads(persona: Persona, root: Path) -> list[str]:
    errors: list[str] = []
    for item in persona.frontmatter.get("reads", []):
        value = unquote(item)
        if value.startswith("<"):
            continue
        if not (root / value).is_file():
            errors.append(
                f"{persona.path}:{persona.line_of.get('reads', 1)}: reads: {value!r} does not exist"
            )
    return errors


def extract_preamble(persona: Persona) -> None:
    body = FRONTMATTER.sub("", persona.text, count=1)
    lines: list[str] = []
    for line in body.splitlines():
        if line.startswith(">"):
            lines.append(line)
        elif lines:
            break
    persona.preamble = "\n".join(lines)


def load(root: Path) -> list[Persona]:
    personas: list[Persona] = []
    for path in sorted(root.glob(f"{PERSONAS_DIR}/*/*.md")):
        persona = Persona(path.relative_to(root), path.read_text(encoding="utf-8"))
        persona.parse_errors = parse_frontmatter(persona)
        extract_preamble(persona)
        personas.append(persona)
    return personas


def validate(root: Path) -> list[str]:
    if not (root / AGENTS).is_file():
        return [f"{AGENTS}: missing, so persona ownership cannot be checked"]
    headings = {title.strip() for title in HEADING.findall((root / AGENTS).read_text(encoding="utf-8"))}

    personas = load(root)
    if not personas:
        return [f"{PERSONAS_DIR}: no personas found"]

    errors: list[str] = []
    for persona in personas:
        errors += persona.parse_errors
        if persona.parse_errors:
            continue
        errors += check_value_shapes(persona)
        errors += check_shape(persona)
        errors += check_ownership(persona, headings)
        errors += check_reads(persona, root)

    # The shared preamble must be identical: each persona is handed over alone.
    reference = next((p for p in personas if p.preamble), None)
    if reference is None:
        errors.append(f"{PERSONAS_DIR}: no persona carries the shared preamble")
    else:
        for persona in personas:
            if persona.preamble != reference.preamble:
                errors.append(
                    f"{persona.path}: preamble differs from {reference.path} — the shared rules "
                    "must be identical in every persona"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("Persona validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Persona validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
