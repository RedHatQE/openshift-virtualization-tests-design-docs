# CNV QualityFlow configuration

The QualityFlow configuration for the STP and STD work, kept next to the STPs it applies to.
QualityFlow reads a `.qualityflow/` directory from the root of each repo checkout and from the
directories above whatever it is working on, so a file here applies to the `stps/` tree and a file
under `stps/sig-<sig>/.qualityflow/` applies only to that SIG's plans. Rules and precedence are
documented upstream in [Repo config layers](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/config/README.md#repo-config-layers-qualityflow).

The QualityFlow deployment keeps the same settings in its own `config/projects/cnv/`. Nothing in
this directory is that copy, and the deployment wins where they differ.

## What is here

| Path | What it configures |
|---|---|
| `.qualityflow/project.yaml` | Identity marker (`version: 1`, `project_id: "cnv"`), the feature toggles and the STP header |
| `.qualityflow/repositories.yaml` | The repositories every SIG's work reads: the QE test suite, this design-docs repository, and the Python client libraries the tests build on |
| `.qualityflow/components.yaml` | Component (team directory) to test package, and the reverse path-to-feature map |
| `.qualityflow/environment.yaml` | The platform the tests run against |
| `.qualityflow/jira.yaml` | Which Jira instance and project prefixes route here |
| `.qualityflow/pii_exceptions.yaml` | Product and project names the PII sanitiser must not mask |
| `stps/sig-<sig>/.qualityflow/` | That SIG's `tier*.yaml` definitions, SIG and decorator mappings, and its own `repositories.yaml` with the product repos its scenarios read |

## The repositories, and where each checkout is found

A repository is declared once its tests, or the product code a failure points at, need to be read.
The root layer carries the tests suite, this repository (`/generate-tests` and the STP template
come from it) and the Python client libraries; each SIG layer carries the product repos its tier
files reference. The variable named by `local_path_env` is how a checkout is found: without it the
regression and LSP analysis still probes the common directories (e.g. `~/src/<repo>`,
`~/projects/<repo>`), checking each candidate against the entry's `url`, while `/generate-tests`
needs the tests repository's variable exported and stops without it.

`.qualityflow/env.example` is a gitignored local template listing every variable; fill in the paths
to your own checkouts. It is deliberately not repository content.

## What a `.qualityflow/` may carry

QualityFlow accepts these files from a checkout: `project.yaml`, `components.yaml`,
`environment.yaml`, `coverage.yaml`, `review_rules.yaml`, `code_generation_config.yaml`,
`tier*.yaml`, `patterns/*.yaml`, `templates/**`, `reference/**`, `README.md` (allowed, never read)
and `pii_exceptions.yaml` — the last only when the central `repositories.yaml` opts in through
`config_sources.allow_sensitive`.

A checkout is untrusted input, so `repositories.yaml`, `jira.yaml` and the other issue-source files
are **not** on that list, and a layer carrying one fails the loader instead of being merged.
[qualityflow#226](https://github.com/redhat-community-ai-tools/qualityflow/issues/226) asks for
`additional_repos` to become layer-settable; until it lands, the `repositories.yaml` files here and
the `jira.yaml`/`pii_exceptions.yaml` copies are what the deployment needs, not what the loader
reads.

## Still pending in the deployment

At the last state on the deployment's `cnv` branch (`cb4f02b`) `config/projects/cnv` declares four
repositories (the tests suite, `kubevirt`, `openshift-python-wrapper`, this repository), carries no
`tier*.yaml` and runs `test_strategy: auto`. Its `design_docs_repo` entry names no `local_path_env`,
and a repo without a local checkout contributes no layer — so no layer here is discovered on a
deployment-wide run until that variable is added; a ticket overlay `paths:` entry covers a single
run. The six Tier 1 repositories these layers reference and the tier files themselves are the rest
of the companion change.
