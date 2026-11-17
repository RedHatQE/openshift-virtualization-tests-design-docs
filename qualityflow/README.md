# CNV QualityFlow project config — reference copies

The generic parts of the CNV QualityFlow configuration, kept here so a team member can read
them without access to the QualityFlow deployment. They are **copies for reference**, not a
live config: QualityFlow reads the real ones from its own `config/projects/cnv/`, never from
this repository. Rules and file semantics are documented upstream in
[Repo config layers](https://github.com/redhat-community-ai-tools/qualityflow/blob/main/config/README.md#repo-config-layers-qualityflow).

The copies can lead or lag `config/projects/cnv/`: an entry here is not proof that the deployment
declares it, and [docs/qualityflow-config.md](../docs/qualityflow-config.md) records which
repository declarations are still pending centrally. When the two disagree, the deployment wins.
The deployment's `design_docs_repo` entry names no checkout variable, and a repo without a local
checkout contributes no layer, so nothing in `.qualityflow/` here is read until that variable is
added centrally or a ticket overlay supplies the path through `paths:`.

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
path: whoever runs QualityFlow exports those variables themselves. No file here holds a credential:
a GitHub token, a Jira credential or a password does not belong in this repository. The one
credential variable any file names is the empty `GITHUB_PERSONAL_ACCESS_TOKEN` in `env.example`,
which the review cycle reads; the operator exports it outside git.

## The repositories, and where each checkout is found

A repository is declared once its tests, or the product code a failure points at, need to be
read. The variable is how that checkout is found: without it the regression and LSP analysis still
probes the common directories (e.g. `~/src/<repo>`, `~/projects/<repo>`), checking each candidate
against the entry's `url`, while `/generate-tests` needs the tests repository's variable exported
and stops without it. `OPENSHIFT_VIRTUALIZATION_TESTS_DESIGN_DOCS_REPO_PATH` is the exception in the
other direction — the deployment's `design_docs_repo` names no variable at all (see the note at the
top). `env.example` lists all of them.

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
| `HCO_REPO_PATH` | `kubevirt/hyperconverged-cluster-operator` |
| `SSP_OPERATOR_REPO_PATH` | `kubevirt/ssp-operator` |
| `COMMON_INSTANCETYPES_REPO_PATH` | `kubevirt/common-instancetypes` |
| `KUBERNETES_NMSTATE_REPO_PATH` | `nmstate/kubernetes-nmstate` |
| `SRIOV_NETWORK_OPERATOR_REPO_PATH` | `k8snetworkplumbingwg/sriov-network-operator` |

Five further context repositories are kept as comments in `repositories.yaml` because no `tier1`
in this repository points at them yet: `ovn-kubernetes`, `forklift`, `node-healthcheck-operator`,
`oadp-operator` and `virt-platform-autopilot`. Uncommenting one registers it — which is what lets
the repo-aware steps open a checkout at all — so activating an entry means three things: uncomment
it, verify its `default_branch` against GitHub, and add its variable to `env.example` and to the
table above.

## What a per-directory layer may also carry

The layers in `.qualityflow/` and `stps/sig-<sig>/.qualityflow/` are restricted to the files
QualityFlow accepts from a checkout: `project.yaml`, `components.yaml`, `environment.yaml`,
`coverage.yaml`, `review_rules.yaml`, `code_generation_config.yaml`, `tier*.yaml`,
`patterns/*.yaml`, `templates/**`, `reference/**`, `README.md` (allowed, never loaded) and
`pii_exceptions.yaml` — the last only when the central `repositories.yaml` lists it in
`config_sources.allow_sensitive`.

`repositories.yaml` and `jira.yaml` are **not** in that list on purpose: a checkout is
untrusted input, and those two decide where code comes from, where generated code goes, and
which Jira endpoint is contacted. `jira.yaml` is central-only. `repositories.yaml` lives in the
central config or in the operator's gitignored per-ticket overlay
`outputs/<JIRA>/repositories.overlay.yaml`, which is never reviewed and so should stay scoped to
one ticket — hence the copies here, which you read but never install as a layer.

A SIG layer can therefore point at upstream tests (`tier1.yaml` `reference_tests`) but cannot
declare the repository they live in. [qualityflow#226](https://github.com/redhat-community-ai-tools/qualityflow/issues/226)
asks for `additional_repos` — context repositories only, never the tests repo — to be
layer-settable.
