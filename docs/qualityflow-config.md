# QualityFlow configuration in this repository

This repository keeps its QualityFlow configuration in `.qualityflow/` and in
`stps/sig-<sig>/.qualityflow/`. The rules are not restated here — they live in the
QualityFlow repository:

- [Repo config layers](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/config/README.md#repo-config-layers-qualityflow)
  — where a `.qualityflow/` directory is read from, the precedence between layers, and
  how files merge.
- [Configuration reference](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/config/README.md)
  — every file and key a project or a layer may set, including `tier*.yaml`,
  `code_generation_config.yaml` and `components.yaml`.
- [Config schema](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/config/_schema.yaml)
  — the machine-readable allowlists the loader enforces.
- [Editor schema](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/schemas/qualityflow.schema.json)
  — referenced by the first line of each `project.yaml` here.
- [Scaffolding](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/onboard.py)
  — `onboard.py --scaffold-repo <checkout> --project-id <id>` writes a starter layer.

What this repository adds to that picture: `/stp-builder`'s target is the `stps/` tree, so
these layers apply to STP and STD work; test-code generation is configured by the test
suite's own `.qualityflow/`. For what each tier means in CNV, see
[testing-tiers.md](testing-tiers.md).

One prerequisite is not yet met, and until it is these layers are not read: QualityFlow
locates a repository's checkout through that repository's `local_path_env` in the central
`config/projects/cnv/repositories.yaml`, and `design_docs_repo` declares none. Setting
`DESIGN_DOCS_REPO_PATH` by hand does not help, because the missing key is what names the
variable.
