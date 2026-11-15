# CNV QualityFlow project config — reference copies

The generic parts of the CNV QualityFlow configuration, kept here so a team member can read
them without access to the QualityFlow deployment. They are **copies for reference**, not a
live config: QualityFlow reads the real ones from its own `config/projects/cnv/`, never from
this repository. Rules and file semantics are documented upstream in
[Repo config layers](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/config/README.md#repo-config-layers-qualityflow).

| File | What it defines |
|---|---|
| `project.yaml` | Identity, feature toggles, the STP header QualityFlow writes |
| `repositories.yaml` | Which repositories QualityFlow may consult, and the environment variable each checkout is found through |
| `components.yaml` | Component (team directory) to test package, and the reverse path to feature name |
| `environment.yaml` | The platform the tests run against |
| `jira.yaml` | Which Jira instance and project prefixes route here |
| `pii_exceptions.yaml` | Product and project names the PII sanitiser must not mask |
| `tier1.yaml`, `tier2.yaml`, `tier3.yaml` | The three tier definitions: language, framework, reference tests, Tier 3 markers |
| `code_generation_config.storage-example.yaml` | The storage specialisation one team needed before per-directory layers existed; kept as an example of the keys, not as the default |

## No credentials, no local paths

`repositories.yaml` names the environment variable each checkout comes from and never carries a
path: whoever runs QualityFlow exports those variables themselves. Nothing here holds a token —
a GitHub token, a Jira credential or a password does not belong in this repository, and none of
the files above require one.

| Variable | Repository |
|---|---|
| `SOURCE_REPO_PATH` | `RedHatQE/openshift-virtualization-tests` |
| `OPENSHIFT_VIRTUALIZATION_TESTS_DESIGN_DOCS_REPO_PATH` | `RedHatQE/openshift-virtualization-tests-design-docs` |
| `KUBEVIRT_REPO_PATH` | `kubevirt/kubevirt` |
| `KUBEVIRT_ENHANCEMENTS_REPO_PATH` | `kubevirt/enhancements` |
| `OPENSHIFT_PYTHON_WRAPPER_REPO_PATH` | `RedHatQE/openshift-python-wrapper` |
| `CDI_REPO_PATH` | `kubevirt/containerized-data-importer` |
| `KUBEVIRT_VELERO_PLUGIN_REPO_PATH` | `kubevirt/kubevirt-velero-plugin` |
| `KUBEVIRT_MIGRATION_OPERATOR_REPO_PATH` | `kubevirt/kubevirt-migration-operator` |
| `VM_FILE_RESTORE_OPERATOR_REPO_PATH` | `kubevirt/vm-file-restore-operator` |

## What a per-directory layer may also carry

The layers in `.qualityflow/` and `stps/sig-<sig>/.qualityflow/` are restricted to the files
QualityFlow accepts from a checkout: `project.yaml`, `components.yaml`, `environment.yaml`,
`coverage.yaml`, `review_rules.yaml`, `code_generation_config.yaml`, `tier*.yaml`,
`patterns/*.yaml`, `templates/**` and `reference/**`.

`repositories.yaml` and `jira.yaml` are **not** in that list on purpose: a checkout is
untrusted input, and those two decide where code comes from, where generated code goes, and
which Jira endpoint is contacted. They exist only in the central config — hence the copies
here, which you read but never install as a layer.
