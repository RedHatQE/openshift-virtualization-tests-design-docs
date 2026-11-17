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
[`qualityflow/`](../qualityflow/README.md), which marks what is a copy and where each checkout
variable comes from; the parity with the deployment is below.

## What the CNV project config already provides

The CNV project config (`config/projects/cnv` in the QualityFlow deployment) is the layer that
carries the shared settings: identity and toggles, the `component_package_map`, the platform and
Jira routing, the PII allowlist, `scenario_tiers` (the Section III labels) and its repository list.
At the last state on its branch (`cnv`, `cb4f02b`, 2026-10-05) it runs `test_strategy: auto` and
carries no `tier*.yaml`, so the tier files this repository's layers add have no tier mode to
match until the deployment gains them; the layers here add per-SIG descriptions, reference tests,
`default_package` and the SIG mapping only.

That config declares four repositories: the QE tests repo, `kubevirt`, `openshift-python-wrapper`
and this design-docs repo. Three of them name a checkout variable there (`SOURCE_REPO_PATH`,
`KUBEVIRT_REPO_PATH`, `OPENSHIFT_PYTHON_WRAPPER_REPO_PATH`): the tests repo needs its own exported
for `/generate-tests`, and for the other two an unset variable falls back to the common-directory
probe. The design-docs repository names no checkout variable at all — and a repo without a local
checkout contributes no layer (`config/README.md`) — so a deployment-wide run discovers the layers
in this repository only once that variable is added; a ticket overlay `paths:` entry covers a
single run. The copy shows the entry the deployment needs. The variable each repository uses, and
the checkout it belongs to, are mapped in
[`qualityflow/README.md`](../qualityflow/README.md#the-repositories-and-where-each-checkout-is-found)
(the names alone are in `env.example`).

On top of that, six repositories these layers reference are undeclared centrally and have to be
added to `config/projects/cnv/repositories.yaml` together with that design-docs variable:
`containerized-data-importer`, `hyperconverged-cluster-operator`, `kubernetes-nmstate`,
`sriov-network-operator`, `ssp-operator` and `common-instancetypes`. Third, the three tier files
(or `test_strategy: tier`) — at `cb4f02b` the project runs `auto` and carries none, so nothing
centrally supplies the `language`, `framework` or Tier 3 `markers` that these layers leave out.

The copy here declares the deployment's four, those six, and four more that no Tier 1 section
references yet (`enhancements`, `kubevirt-velero-plugin`, `kubevirt-migration-operator`,
`vm-file-restore-operator`) — fourteen entries in all. It therefore leads the deployment by ten,
and by four even after that companion change lands. Five further context repositories are kept
there as comments.

For what each tier means in CNV, see [testing-tiers.md](testing-tiers.md).
