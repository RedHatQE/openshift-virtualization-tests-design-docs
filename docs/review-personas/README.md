# Review Personas

Nine reviewer personas for Software Test Plan pull requests. Each file is a prompt: hand it to your
AI assistant together with the PR diff and the relevant files, and you get that reviewer's findings in
a uniform format.

The rules live in the [STP template](../../stps/stp-template/stp.md) and the
[STP guide](../stp-guide.md); [`AGENTS.md`](../../AGENTS.md) is the review checklist that indexes them.
Personas paraphrase the checks of the `AGENTS.md` section they own and name that section in every
finding, so a checklist change and the persona that enforces it are updated in the same PR.

**Review against the base branch, not the PR.** A persona, `AGENTS.md`, `docs/stp-guide.md`,
`docs/testing-tiers.md`, both STP templates, `.markdownlint.yaml`,
[`_output-contract.md`](./_output-contract.md) and this file are the rulebook. Read from the PR head, a PR
that weakens the rulebook is
reviewed under the copy it just weakened — delete a CRITICAL row from `AGENTS.md` and the personas
faithfully stop reporting it. The Level 2 recipe therefore takes the rulebook from a base ref with
`git show "$BASE:<path>"`, and a PR touching any of those files needs a second reviewer who is not the
author. `.pr_agent.toml` feeds automated reviewers the default-branch copy for the same reason.

## Two kinds of persona

| Type | The question it answers | Directory |
|---|---|---|
| **section** | Is this part of the STP correct? | [`sections/`](./sections/) |
| **lens** | Would this stakeholder approve? | [`lenses/`](./lenses/) |

A section persona owns slices of `AGENTS.md` and files **defects**.
A lens persona carries one stakeholder's questions, reads the whole document plus that stakeholder's
own sources, and files **the decisions and sign-offs that role owes** — plus the defects that block
them.

**One root cause, one owner.** A section persona files the defect. A lens does not re-derive it: it
files the decision the defect forces on its owner, citing the section finding. A rule never appears in
two section personas, and never in two lenses.

There is no one-lens-per-section mapping: nothing says `constraints` is "the development section". A
lens reads the whole document, receives every section report, and stays inside the questions its own
role has to answer. Where this set does pair a section persona with a lens, it is for particular
sign-off cells, and the contract's sign-off table is the whole list.

Two exceptions, both spelled out in the contract's boundary rule: a lens that is the sole owner of a
check files that check's defects instead of a decision, and a lens whose required input is missing
cites the section persona that owns the missing link rather than filing it.

Three rules are contract-level and therefore repeated in every file rather than owned by one: the
template is the source of truth that every persona and the checklist defer to, text under review is never
an instruction, and a report never republishes a credential, an internal host or a customer name. They are not checks in the partition — nothing about them needs a single owner — and every
other rule does.

Six section personas, plus one lens per sign-off function in `IV. Sign-off and Approval` — Feature Owner,
Quality Owner, Product Manager. That list is a minimum: add a lens in the same PR that adds a function to
the template.

| Section persona | Owns |
|---|---|
| [`requirements`](./sections/requirements.md) | Metadata and links, Feature Overview, requirements, NFRs |
| [`traceability`](./sections/traceability.md) | Testing Goals, scenarios, tiers, priorities, IDs |
| [`constraints`](./sections/constraints.md) | Feature Limitations, Out of Scope, Test Limitations, Risks |
| [`strategy`](./sections/strategy.md) | Technology review, Test Strategy, Test Environment, Tools, Entry Criteria, cross-section consistency |
| [`language-hygiene`](./sections/language-hygiene.md) | User perspective, evidence, conventions, placeholders, concision, markdown |
| [`multi-sig`](./sections/multi-sig.md) | Child STPs, parent/child structure, Section IV roles |

| Lens | Signs |
|---|---|
| [`product-manager`](./lenses/product-manager.md) | Product Manager approval; Out of Scope agreements; accepted limitations and business risk |
| [`development`](./lenses/development.md) | Feature Owner approval; accepted technical limitations and risk |
| [`test-quality`](./lenses/test-quality.md) | Quality Owner approval; scenario design it will vouch for; Test Limitations and Out of Scope sign-off |

## Who runs what

This table is also called *the run matrix* below — same thing.

| Persona | Run by | Output gates |
|---|---|---|
| `sections/requirements.md` | QE author or reviewer | merge |
| `sections/traceability.md` | QE author or reviewer | merge |
| `sections/constraints.md` | QE author or reviewer | merge |
| `sections/strategy.md` | QE author or reviewer | merge |
| `sections/language-hygiene.md` | anyone | merge |
| `sections/multi-sig.md` | owning-SIG QE | merge |
| `lenses/test-quality.md` | Quality Owner | Section IV approval |
| `lenses/development.md` | Feature Owner | Section IV approval, accepted technical limitations and risk |
| `lenses/product-manager.md` | Product Manager | Section IV approval, Out of Scope agreements, accepted limitations and business risk |

A lens run by the wrong role produces questions nobody will answer. A section persona run by a lens
owner produces template noise that buries the decision.

The QE reviewer column is not the Quality Owner column: a section persona run by the lead is still a review,
not an approval. "anyone" means the persona judges surface only and needs no feature context.

The **merge owner** who records `## Coverage` is not the author — the contract says why. On an
author's own PR that is the QE reviewer or the SIG's QE lead.

## Running one

The YAML block at the top of each persona is readable metadata; nothing in this repository parses it
yet, so a mistyped heading in `owns:` fails nothing and review is the only thing that catches it.
Quote a value that contains a colon, or YAML reads it as a mapping. The prose after it is the prompt.

`reads:` lists what to give the assistant: repository paths, plus any external source written in angle
brackets — the feature request, the VEP — which only a human can paste. The Level 2 recipe builds the
rulebook from these entries, so a path you forget here is a file the reviewer never sees. Every entry is required for a
run at full scope. A run missing one is partial: the persona names what it could not read and reports
what it could not check, and the `## Coverage` block records it as partial.

### Level 1 — paste it

```text
Follow docs/review-personas/sections/traceability.md together with AGENTS.md,
docs/stp-guide.md, docs/testing-tiers.md, stps/stp-template/stp.md,
stps/stp-template/child-stp.md and docs/review-personas/_output-contract.md.

STP: stps/sig-network/<feature>/stp.md
Reviewed at: <commit sha>
Diff:
<paste `gh pr diff 123` output here>
```

Whichever persona you run, the message carries four things:

1. the persona file,
2. every repository path in its `reads:` — for `traceability` that is `AGENTS.md`, the guide, the tiers
   doc, the parent template and the child template,
3. `docs/review-personas/_output-contract.md`,
4. the STP, the diff, the commit SHA, and any `<angle-bracketed>` source you were able to paste.

In a chat window with no file access, paste the contents of all of them as one message. Dropping the
template costs the field names every finding cites; dropping the tiers doc costs every tier judgement.

### Level 2 — one subagent per persona

Run each persona in its own context so findings do not bleed between streams. The rulebook comes from
the base branch and the diff goes to a scratch directory outside the tree. An agent confined to its
working directory cannot read `/tmp`, so grant that directory explicitly — with output redirected,
nobody is there to answer a permission prompt:

```bash
set -euo pipefail
BASE=${BASE:-upstream/main}          # the rulebook comes from here, never from the PR head
PHASE=${PHASE:-sections}            # sections first; lenses run after the author answers them
SOURCE=${SOURCE:-}                  # path to a pasted feature request, when you have one
DESIGN=${DESIGN:-}                  # path to a pasted VEP/design doc, for the development lens
ROOT=$(git rev-parse --show-toplevel)
case "$PHASE" in
  sections|lenses) ;;
  *) echo "PHASE must be sections or lenses" >&2; exit 1 ;;
esac
SCRATCH=$(mktemp -d)                # never inside the tree: the diff carries the PR's secrets
trap 'rm -rf "$SCRATCH"' EXIT

git -C "$ROOT" rev-parse --verify -q "$BASE^{commit}" >/dev/null \
  || { echo "base ref $BASE not found — git fetch upstream first" >&2; exit 1; }
case "$(git -C "$ROOT" rev-parse --symbolic-full-name "$BASE")" in
  refs/remotes/*) ;;
  *) echo "$BASE is not a remote-tracking branch — a commit on the PR branch is not a base" >&2; exit 1 ;;
esac

SHA=$(gh pr view 123 --json headRefOid --jq .headRefOid || true)
[ -n "$SHA" ] || { echo "no head SHA — is gh authenticated?" >&2; exit 1; }
[ "$(git -C "$ROOT" rev-parse HEAD)" = "$SHA" ] \
  || { echo "HEAD is not $SHA — check the PR out first" >&2; exit 1; }
if [ "$(git -C "$ROOT" rev-parse "$BASE")" = "$SHA" ]; then
  echo "base and PR head are the same commit — that is not a review" >&2; exit 1
fi
if git -C "$ROOT" merge-base --is-ancestor "$SHA" "$BASE"; then
  echo "$BASE already contains $SHA — pick a base the PR is ahead of" >&2; exit 1
fi

# Derive both persona sets from git. A list typed here would review a PR that adds or renames a
# persona against yesterday's set.
for kind in sections lenses; do
  git -C "$ROOT" ls-tree --name-only "$BASE" "docs/review-personas/$kind/" | sort > "$SCRATCH/base-$kind"
  git -C "$ROOT" ls-tree --name-only HEAD "docs/review-personas/$kind/" | sort > "$SCRATCH/head-$kind"
  if [ ! -s "$SCRATCH/base-$kind" ]; then
    echo "bootstrap: this PR introduces docs/review-personas/$kind — the rulebook is the PR's own," \
         "so someone who is not the author has to run it" >&2
    cp "$SCRATCH/head-$kind" "$SCRATCH/base-$kind"
  elif ! diff -q "$SCRATCH/base-$kind" "$SCRATCH/head-$kind" >/dev/null; then
    echo "this PR changes the $kind set — review it by hand against the base copies:" >&2
    diff "$SCRATCH/base-$kind" "$SCRATCH/head-$kind" >&2 || true
    exit 1
  fi
done

# A file the PR itself introduces has no base copy: fall back to the head copy and say so, because
# the PR then wrote that rule, which is exactly what the second reviewer guards.
snapshot() {
  mkdir -p "$SCRATCH/base/$(dirname "$1")"
  if git -C "$ROOT" cat-file -e "$BASE:$1" 2>/dev/null; then
    git -C "$ROOT" show "$BASE:$1" > "$SCRATCH/base/$1"
  elif git -C "$ROOT" cat-file -e "$SHA:$1" 2>/dev/null; then
    git -C "$ROOT" show "$SHA:$1" > "$SCRATCH/base/$1"
    echo "note: $1 is new in this PR — read from $SHA" >&2
  else
    cp "$ROOT/$1" "$SCRATCH/base/$1"
    echo "warning: $1 is in neither $BASE nor $SHA — read from the working tree" >&2
  fi
}

while read -r f; do snapshot "$f"; done < "$SCRATCH/base-sections"
while read -r f; do snapshot "$f"; done < "$SCRATCH/base-lenses"

# The rulebook is whatever the personas declare in `reads:`, plus the contract — not a list kept in
# this file. A hand-kept list lost two entries before this was derived.
reads_of() { sed -n '/^reads:/,/^---/p' "$1" | sed -n 's/^ *- //p' | grep -v '^<' || true; }
# A reads: entry is a repository path. Anything absolute or climbing out of the tree is a broken
# persona, not a file to copy.
safe_read() {
  case "$1" in
    ""|/*|..|../*|*/..|*/../*) echo "bad reads: entry: $1" >&2; exit 1 ;;
  esac
}
{ while read -r f; do reads_of "$SCRATCH/base/$f"; done < "$SCRATCH/base-sections"
  while read -r f; do reads_of "$SCRATCH/base/$f"; done < "$SCRATCH/base-lenses"
  echo docs/review-personas/_output-contract.md
} | sort -u | while read -r f; do safe_read "$f"; snapshot "$f"; done

gh pr diff 123 > "$SCRATCH/pr.patch"

# Stage the changed files as of $SHA, so a persona reads the commit and not the working tree.
# The merge base, not $BASE: once upstream moves past the branch point, a two-dot diff stages every
# file main touched since — files this PR never opened — and contradicts pr.patch.
MB=$(git -C "$ROOT" merge-base "$BASE" "$SHA")

# The recipe cannot review a change to itself: this file is the procedure, not an input to it.
if git -C "$ROOT" cat-file -e "$BASE:docs/review-personas/README.md" 2>/dev/null \
   && ! git -C "$ROOT" diff --quiet "$MB" "$SHA" -- docs/review-personas/README.md; then
  echo "this PR changes the runbook this recipe implements — review it by hand" >&2; exit 1
fi
git -C "$ROOT" -c core.quotePath=false diff --name-only "$MB" "$SHA" > "$SCRATCH/changed"
while read -r f; do
  git -C "$ROOT" cat-file -e "$SHA:$f" 2>/dev/null || continue    # deleted by this PR
  mkdir -p "$SCRATCH/head/$(dirname "$f")"
  git -C "$ROOT" show "$SHA:$f" > "$SCRATCH/head/$f"
done < "$SCRATCH/changed"

# The persona runs with its cwd in $SCRATCH, so an external source has to be copied in to be readable.
if [ -n "$SOURCE" ]; then
  cp "$SOURCE" "$SCRATCH/feature-request.md"
  SOURCE=feature-request.md
fi
if [ -n "$DESIGN" ]; then
  cp "$DESIGN" "$SCRATCH/design-doc.md"
  DESIGN=design-doc.md
fi

mkdir -p "$SCRATCH/reports" "$ROOT/review-out"
if [ "$PHASE" = lenses ]; then
  # A lens cites the section finding rather than re-deriving it, so it needs those reports — and it
  # must be the ones from this commit, not a set left by an earlier run.
  while read -r f; do
    name=$(basename "$f" .md)
    [ -s "$ROOT/review-out/$name.md" ] \
      || { echo "PHASE=lenses needs the section reports: $name.md is missing" >&2; exit 1; }
    grep -q "Reviewed at: $SHA" "$ROOT/review-out/$name.md" \
      || { echo "section report $name.md is from a different commit" >&2; exit 1; }
    cp "$ROOT/review-out/$name.md" "$SCRATCH/reports/"
  done < "$SCRATCH/base-sections"
  while read -r f; do rm -f "$ROOT/review-out/$(basename "$f")"; done < "$SCRATCH/base-lenses"
else
  # Replace, never merge: a stale report must not survive a run that fails.
  rm -rf "$ROOT/review-out" && mkdir -p "$ROOT/review-out"
fi

failed=""
while read -r p; do
  name=$(basename "$p" .md)
  src="";   [ -n "$SOURCE" ] && src="The feature request is at $SOURCE."
  [ -n "$DESIGN" ] && src="$src The design doc is at $DESIGN."
  prior=""; [ "$PHASE" = lenses ] && prior="The section reports are in reports/."
  if ( cd "$SCRATCH" && claude -p "Follow the persona in base/$p together with base/AGENTS.md,
base/docs/review-personas/_output-contract.md and the rest of its reads: under base/. Review
pr.patch and the changed files staged under head/, naming the STP's own path in your header. $prior $src
Reviewed at: $SHA. Report per the output contract." \
        --allowedTools Read --add-dir "$SCRATCH" \
        > "reports/$name.md" ); then
    :
  else
    failed="$failed $name"
  fi
done < "$SCRATCH/base-$PHASE"

[ -z "$failed" ] || { echo "no report from:$failed" >&2; exit 1; }
while read -r p; do
  name=$(basename "$p" .md)
  [ -s "$SCRATCH/reports/$name.md" ] || { echo "$name wrote an empty report" >&2; exit 1; }
  grep -q "Reviewed at: $SHA" "$SCRATCH/reports/$name.md" \
    || { echo "$name is not stamped with $SHA" >&2; exit 1; }
done < "$SCRATCH/base-$PHASE"

cp "$SCRATCH/reports"/*.md "$ROOT/review-out/"
```

`PHASE=sections` is the default and runs the six section personas. `PHASE=lenses` runs the three
lenses, and carries the section reports over from `review-out/` because a lens cites a section finding
rather than re-deriving it. Lenses run **after** the author has answered the section findings: a lens
asked too early re-asks questions QE is about to fix.

Four details are load-bearing. Guards exit instead of continuing — a base ref that does not resolve or is
not a remote-tracking branch, a `HEAD` that is not the PR, a persona set this PR adds, renames or drops, a
`PHASE` that is neither value, a `reads:` entry that is not a repo-relative path, a report that is empty or
not stamped with `$SHA`, and section reports that are missing or from another commit. One guard has a
remedy the recipe cannot perform for you: a PR that changes this README cannot be reviewed by it, so run
Level 1 by hand for that file and get a reviewer who is not its author. A PR that *introduces* the set is
the one case that does not exit — it bootstraps from the head copy with a note, and that is why such a PR
needs a reviewer who is not its author. The rulebook is read from the personas' own `reads:` rather than
from a list in this file, which lost two entries before it was derived — so an entry a persona forgets is a
file its reviewer never sees. `--allowedTools Read` is enough once the inputs are on disk; granting `Bash` too lets a
review write into the tree it is reviewing. And `--add-dir` **widens** the readable set rather than
restricting it: `Read` can still open the checkout, which is why the `base/` layout and the second
reviewer are the controls, not a sandbox. The flag name is CLI-specific — check `claude --help` before
an unattended run.

No assistant can fetch Jira: paste the feature request into a file and pass its path in `SOURCE`, and
the VEP or design doc in `DESIGN`. With `SOURCE` unset, `sections/requirements` has no feature request
and says so; with `DESIGN` unset, `lenses/development` has no design doc, says so, and stops. Either is
a partial run, and the `## Coverage` block has to record it as one — `SOURCE` set with `DESIGN` unset is
not full-scope.

A run that skips a persona is not a clean run, and a report file that exists is not a run: the merge
owner copies each report's `Reviewed at` and `Findings` count into the `## Coverage` block, and a
report without a valid SHA counts as not run. Nine empty files from a misconfigured CLI must not read
as a clean review.

There is no automated record of who ran what, so the author/merge-owner separation above is the whole
control.

### Level 3 — a native tool adapter

Wrap the persona in whatever the tool wants: a subagent, an editor rule, a CodeRabbit path
instruction. Commit the generation recipe, not the generated file — `.claude/` is gitignored here and
agent directories get overwritten on upgrade. `.coderabbit.yaml` and `.pr_agent.toml` show how this
repository already feeds `AGENTS.md` to automated reviewers.

## Merging results

1. Collect every finding row from every persona.
2. Deduplicate: same location and same root cause is one finding. Keep the most actionable wording.
3. A `DECISION` row names the role that answers it — Product Manager, Feature Owner, Quality Owner — not the
   persona's runner and not the STP author as such. The run matrix says who runs a persona, not who
   owns its findings.
4. `SIGN-OFF` rows become the checklist for Section IV. A row carries the cell and the question its
   owner has to answer — never a statement that something was verified, which the persona cannot know.
5. The person writes their own name against the row, and a date where the template has a date field;
   no persona ever fills those in.
6. A `DECISION` is not resolved by editing text. It is resolved when the named human answers and the
   STP records the answer.

Channels, format, evidence and budget rules: [`_output-contract.md`](./_output-contract.md).

## Adding a persona

1. Decide the type: does it own part of `AGENTS.md`, or one stakeholder's questions?
2. Copy the closest existing file. Frontmatter:

```yaml
---
persona: <file-name-without-extension>
type: section            # or: lens
owns:                    # section only — heading text from AGENTS.md
  - II.5 — Risks
signs:                   # lens only — the sign-off cells this role completes
  - "IV — Sign-off and Approval (Quality Owner)"
  - "II.5 — Risks (Sign-off)"
reads:                   # repository paths, plus external sources a human pastes
  - AGENTS.md
---
```

Quote any value containing a colon. `- II.5 — Risks (Sign-off)` survives unquoted, but
`- II.1 — Scope of Testing (partial: Testing Goals)` is silently parsed as a mapping rather than a
string.

`owns:` takes an `AGENTS.md` heading, optionally suffixed `(partial: ...)` naming the sub-part this
persona owns when a heading is split. Those two forms — a heading and a heading with `(partial: ...)`
— are the only ones for `owns:`; a persona that owns several related headings lists each of them. `signs:` takes a sign-off **cell** — the section whose per-item
cells this role fills, so `II.5 — Risks (Sign-off)` means every risk's `*Sign-off:*` — or the role's
cell in `IV`. Never a section with no cell behind it: a section with nothing to sign is a defect
area, and defect areas are `owns:`. Where a lens vouches for a section that has no cell at all, that
goes in its prose. Keep both exact: a mistyped heading currently fails nothing, so review is the only
thing that catches it.

**Precedence.** The template (`stps/stp-template/stp.md`, and `child-stp.md` for a child STP) is the
source of truth for structure, format and content. `AGENTS.md` is a review checklist that indexes it, and
a persona compresses that checklist. Where the three disagree, the template is right: the STP is judged
by it, and the checklist or persona that differs is corrected in the same PR rather than reported as a
finding against the author.

Every persona repeats this rule in its own preamble, because a persona pasted into a chat arrives
alone and never sees this section. The repetition is deliberate: this paragraph is where the rule
changes, and the nine copies follow it.

3. Body order: role paragraph; one preamble `##` when the persona needs an external source or a
   decision rule, named for what it establishes (`## Before you judge`, `## First: get the design`);
   one `##` per thing it hunts; `## What you emit` for a lens; `## Do NOT report`; `## Output`.
4. Write `Do NOT report` first. The scope boundary is what makes nine personas useful instead of nine
   copies of the same review.
5. Compare against every other persona: if two would file the same finding, the boundary is wrong.
6. Add it to the run matrix above, and to the lens table if it is a lens. Adding a persona also means
   revisiting the `owns:` entries of all the others: a check has exactly one owner, so a new persona
   that takes a check over edits the file it came from in the same PR. If the check had no owner at
   all before, you have just found a rule in `AGENTS.md` that nobody enforced.
7. Run the new persona once against a merged STP before trusting it. A persona that has never produced
   a finding is a persona nobody has read.

These personas are hand-run. They are deliberately not in `.pr_agent.toml`'s
`repo_context_files` or `.coderabbit.yaml`'s `code_guidelines.filePatterns`: those budgets cover the
standard, and the persona set is roughly twice the length of the standard it compresses. Wiring them in
is a separate decision.

## Related

- [`AGENTS.md`](../../AGENTS.md) — the review checklist these personas compress (an index, not the rules)
- [`docs/stp-guide.md`](../stp-guide.md) — STP lifecycle and structure
- [`docs/testing-tiers.md`](../testing-tiers.md) — tier definitions
