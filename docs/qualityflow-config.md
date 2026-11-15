# QualityFlow configuration in this repository

This repository keeps its QualityFlow layer configuration in `.qualityflow/` and
`stps/sig-<sig>/.qualityflow/`. The rules are not restated here — they live in the
QualityFlow repository:

- [Repo config layers](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/config/README.md#repo-config-layers-qualityflow)
  — where a `.qualityflow/` directory is read from, the precedence between layers, and how
  files merge.
- [Configuration reference](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/config/README.md)
  — every file and key a project or a layer may set.
- [Config schema](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/config/_schema.yaml)
  — the allowlists the loader enforces.
- [Editor schema](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/schemas/qualityflow.schema.json)
  — referenced by the first line of each `project.yaml` here.
- [Scaffolding](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/onboard.py)
  — `onboard.py --scaffold-repo <checkout> --project-id <id>` writes a starter layer.

## The generic config, readable from here

The generic parts of the CNV QualityFlow configuration are copied into
[`qualityflow/`](../qualityflow/README.md) — identity and toggles, the repository list with the
environment variable each checkout comes from, the component map, the platform, the Jira
routing, the PII allowlist and the three tier definitions. Nothing there holds a credential or a
local path; `env.example` lists the variables to export yourself. Those copies are for reading —
QualityFlow reads the live ones from its own `config/projects/cnv/`.

## What the CNV project config already provides

The CNV project config (`config/projects/cnv` in the QualityFlow deployment) is the layer
that carries the shared settings: tier mode, all three tier files (Tier 1 Go/Ginkgo with
`default_package`, Tier 2 and Tier 3 Python/pytest, Tier 3 with its `markers`), the
`component_package_map`, and the repository list. The layers here deliberately do not repeat
any of it — they add per-SIG descriptions, reference tests, `default_package` and the SIG
mapping only.

That config also declares the checkout locations, so a layer here is read once the variable
it names is set:

| Repository | Variable |
|---|---|
| `RedHatQE/openshift-virtualization-tests` | `SOURCE_REPO_PATH` |
| `RedHatQE/openshift-virtualization-tests-design-docs` | `OPENSHIFT_VIRTUALIZATION_TESTS_DESIGN_DOCS_REPO_PATH` |
| `kubevirt/kubevirt` | `KUBEVIRT_REPO_PATH` |
| `kubevirt/enhancements` | `KUBEVIRT_ENHANCEMENTS_REPO_PATH` |
| `RedHatQE/openshift-python-wrapper` | `OPENSHIFT_PYTHON_WRAPPER_REPO_PATH` |
| `kubevirt/containerized-data-importer` | `CDI_REPO_PATH` |
| `kubevirt/kubevirt-velero-plugin` | `KUBEVIRT_VELERO_PLUGIN_REPO_PATH` |
| `kubevirt/kubevirt-migration-operator` | `KUBEVIRT_MIGRATION_OPERATOR_REPO_PATH` |
| `kubevirt/vm-file-restore-operator` | `VM_FILE_RESTORE_OPERATOR_REPO_PATH` |

For what each tier means in CNV, see [testing-tiers.md](testing-tiers.md).
