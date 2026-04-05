# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Assisted-by: Claude <noreply@anthropic.com>

## Repository Overview

This is a Quality Engineering (QE) documentation repository for OpenShift Virtualization. It contains:

- Software Test Plans (STPs) for features and enhancements
- Testing tier documentation and guidelines
- QE process documentation and templates
- All content is Markdown documentation

## Development Commands

### Prerequisites

```bash
pip install pre-commit
pre-commit install
```

### Linting

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run on specific files
pre-commit run --files README.md docs/stp-guide.md

# Run only markdownlint
pre-commit run markdownlint --all-files
```

## Project Structure

```text
/
├── docs/                    # Core documentation
│   ├── stp-guide.md        # Guide to Software Test Plans
│   └── testing-tiers.md    # Testing tier definitions
├── stps/                    # Software Test Plans by SIG
│   ├── sig-infra/          # Infrastructure SIG STPs
│   ├── sig-iuo/            # Instance Updates & Operators SIG STPs
│   ├── sig-network/        # Network SIG STPs
│   ├── sig-storage/        # Storage SIG STPs
│   ├── sig-virt/           # Virtualization SIG STPs
│   └── stp-template/       # STP template for new features
│       └── stp.md
└── .github/
    └── PULL_REQUEST_TEMPLATE.md
```

## Markdown Linting Rules

The repository uses markdownlint-cli with custom configuration in `.markdownlint.yaml`:

**Disabled Rules (flexibility for documentation):**
- MD010: Hard tabs allowed (for code examples)
- MD013: Line length unrestricted
- MD022: Flexible spacing around headings
- MD024: Multiple headings with same content allowed
- MD025: Multiple top-level headings allowed
- MD032: Flexible spacing around lists
- MD033: Inline HTML allowed (for complex tables)
- MD034: Bare URLs allowed
- MD036: Emphasis used as heading allowed
- MD041: First line doesn't need to be H1
- MD047: Flexible file endings
- MD049: Flexible emphasis style
- MD050: Flexible strong style
- MD060: Flexible table column alignment

**Enforced Rules:**
- MD040: Code blocks must specify language
- MD045: Images must have alt text
- MD051: Link fragments must be valid

See `.markdownlint.yaml` for complete configuration with detailed comments.

## Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:

- **markdownlint** - Markdown file linting
- **check-merge-conflict** - Prevent merge conflicts
- **trailing-whitespace** - Remove trailing whitespace
- **end-of-file-fixer** - Ensure files end with newline
- **detect-private-key** - Prevent committing secrets
- **mixed-line-ending** - Consistent line endings
- **gitleaks** - Secret scanning

## Contributing Guidelines

### Creating New STPs

1. Copy template from `/stps/stp-template/stp.md`
2. Place in appropriate SIG directory under `/stps/sig-*/`
3. Follow structure defined in `/docs/stp-guide.md`
4. Include testing tier coverage per `/docs/testing-tiers.md`

### Pull Requests

- PRs should reference VEP (Virtualization Enhancement Proposal) issue
- Follow the pull request template in `.github/PULL_REQUEST_TEMPLATE.md`
- Ensure pre-commit hooks pass before submitting
- Get stakeholder approval for STPs before testing begins

### STP Requirements

STPs must include:
- Feature scope and objectives
- Entry criteria
- Test strategy (Tier 1 functional + Tier 2 end-to-end)
- Environment and dependencies
- Risk analysis and mitigation
- Automation must be merged before GA

## Testing Tiers

- **Unit Tests**: Developer-owned, isolated component tests
- **Tier 1 (Functional)**: Feature-level tests covering individual capabilities
- **Tier 2 (End-to-End)**: Full integration tests covering complete workflows

See `/docs/testing-tiers.md` for detailed definitions and examples.

## AI Review Standards

For comprehensive STP review rules, patterns, and quality standards used by AI review tools
and human reviewers, see [AGENTS.md](AGENTS.md).

CodeRabbit is configured via [.coderabbit.yaml](.coderabbit.yaml) and uses AGENTS.md as its review guide.

AGENTS.md covers:
- Section-by-section review checklist
- Common rejection reasons per section
- Content quality rules (DO / DON'T)
- Constraint category distinctions (Limitations vs. Out of Scope vs. Risks)
- Review severity levels
