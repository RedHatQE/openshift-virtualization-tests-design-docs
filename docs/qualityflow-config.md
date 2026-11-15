# QualityFlow configuration for STP and STD work

QualityFlow reads the `.qualityflow/` directory of every directory between a run's target and
the checkout root and merges them, deepest last
([qualityflow#199](https://github.com/redhat-community-ai-tools/qualityflow/pull/199)).
`/stp-builder`'s target is this repository's `stps/` tree, so the layers here configure STP and
STD work: how a scenario is classified into a tier and what a test for it should look like.
Test-code generation is configured by the test suite's own `.qualityflow/`, not here.

Only configuration lives in those directories — `.qualityflow/` at the repository root and
`stps/sig-<sig>/.qualityflow/` per SIG. This page is the documentation for both.

## Not active yet

QualityFlow locates a repository's checkout through that repository's `local_path_env` in the
central `config/projects/cnv/repositories.yaml`. `design_docs_repo` declares none, so this
checkout is never found and no layer here is read. Setting `DESIGN_DOCS_REPO_PATH` by hand does
not help: the missing key is what names the variable. One line activates everything:

```yaml
design_docs_repo:
  # ... name, org, full_name, url, default_branch
  local_path_env: "DESIGN_DOCS_REPO_PATH"
```

## Precedence

Lowest to highest: the central `config/projects/cnv/`, the root layer, then
`stps/sig-<sig>/.qualityflow/`. A layer found deeper in the tree outranks one above it, and the
root layer outranks the central config but not a SIG's.

A target inside one SIG directory gets shared-then-SIG settings; a target elsewhere under
`stps/` (such as `stps/stp-template/`) gets the root layer only.

## Merge rules

Mappings merge recursively and scalars replace. Lists replace, except lists whose items all
carry an `id` or `name` key, and a list may opt into `{merge: append|replace, value: [...]}`.
`null` unsets a key, which is how a SIG records "none": `reference_tests: null` means this SIG
has no exemplar, whereas omitting the key would inherit whatever a lower layer carries.

A SIG layer therefore states only its deltas — a `description` and `reference_tests` per tier —
and inherits `enabled`, `tier`, `language`, `framework` and the rest from the root layer.

## Tiers

The root layer defines all three tiers and enables only Tier 2. Tier 1 tests are Go/Ginkgo in
`kubevirt/kubevirt`, and a Go generation target resolves to the Python test suite rather than
the product. Tier 3 is off because nothing a layer can set makes a generated test carry
`@pytest.mark.tier3`, and an unmarked test is stamped `tier2` by the test suite's `conftest.py`,
so a generated Tier 3 test would run in the tier2 lane.

Both remain valid STP labels: `tier-classifier` is handed every `tier*.yaml` to build the list
of available tiers, not only the enabled ones. What each tier means is defined in
[testing-tiers.md](testing-tiers.md); a Tier 1 or Tier 3 scenario produces no stub and no test,
and `stub-generator`'s "no matching language config" warning for it is expected.

## What a layer may contain

A checkout is untrusted input, so a layer holds only the files listed in QualityFlow's
`config/_schema.yaml` under `config_layers`, and in each only the keys its own validation spec
allows. Every layer needs `project.yaml` with `version: 1` and the `project_id` it configures,
and symlinks are refused. In `project.yaml` a layer may not set `display_name`, `review_sla`,
`model_policy`, `stakeholders` or `pr_autofix`, and may not turn off the four review toggles the
central config has enabled. `display_name` in a `tier*.yaml` is allowlisted, and the root tier
files set it. `OWNERS` is not an allowed layer file.

## Adding a SIG

Create `stps/sig-<sig>/.qualityflow/` with `project.yaml` — `version: 1`, `project_id: "cnv"`,
`sig_mappings`, and `decorator_mappings` keyed by the SIG a scenario carries and naming the
decorator its upstream Go tests use (`sig-iuo: "SigOperator"`, `sig-virt: "SigCompute"`) — plus
`tier1.yaml`, `tier2.yaml` and `tier3.yaml` carrying that SIG's `description` and
`reference_tests` only.

## Checking a change

```bash
# from a QualityFlow checkout that carries config/projects/cnv/
uv run python config/validate.py --repo /path/to/openshift-virtualization-tests-design-docs
```

`--repo` checks each layer on its own — identity marker, file and key allowlists, toggle
ratchet — and does not validate a merged result; merging happens in `layers.resolve()` during
real runs. Against a plain clone of the public QualityFlow repository it prints
`(project 'cnv' is not in .../config/projects: checked against the schema only)` and checks the
key allowlist against the schema alone.
