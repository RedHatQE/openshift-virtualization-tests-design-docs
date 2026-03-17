# Multiarch Support for ARM - Feature Overview

## What Is It

Multiarch support enables running ARM (aarch64) virtual machines alongside x86 (amd64) VMs
on a single OpenShift Virtualization cluster. The cluster has mixed-architecture worker nodes
and the platform automatically manages architecture-aware golden images, templates, and VM scheduling.

The feature is defined in VEP #48: [Golden Images Support For Heterogeneous Clusters](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster).

**Jira Tracking:**

- Feature: [VIRTSTRAT-494](https://issues.redhat.com/browse/VIRTSTRAT-494)
- QE Epic: [CNV-67900](https://issues.redhat.com/browse/CNV-67900)
- sig-infra: [CNV-76714](https://issues.redhat.com/browse/CNV-76714)
- sig-storage: [CNV-76732](https://issues.redhat.com/browse/CNV-76732)
- sig-virt: [CNV-26818](https://issues.redhat.com/browse/CNV-26818)
- sig-network: [CNV-76741](https://issues.redhat.com/browse/CNV-76741)
- UI: [CNV-62535](https://issues.redhat.com/browse/CNV-62535)

## Feature Gate Timeline

| Version | Feature Gate Default | Behavior |
|:--------|:---------------------|:---------|
| 4.22    | Disabled (opt-in)    | Users must explicitly enable `enableMultiArchBootImageImport` |
| 4.23+   | Enabled (opt-out)    | Multiarch golden images active by default |

## Architecture Flow

The feature maintains the existing golden image workflow while adding architecture awareness at each layer:

```text
HCO
 ├── Detects worker node architectures (status.nodeInfo.architecture)
 ├── Stores in status.nodeInfo.workloadsArchitectures
 ├── Filters DICT annotations to supported archs only
 └── Propagates to SSP CR
      │
      SSP
      ├── Reads enableMultipleArchitectures + cluster arch fields
      ├── Creates arch-specific DICs (one per supported arch)
      │    e.g., centos-stream9-image-cron-amd64
      │         centos-stream9-image-cron-arm64
      ├── Creates arch-specific VM templates
      │    with template.kubevirt.io/architecture label
      └── Creates pointer DataSources for backward compatibility
           │
           CDI
           ├── Each DIC imports arch-specific image from registry
           │    pullMethod==pod: uses platform.architecture field
           │    pullMethod==node: uses nodeAffinity to match arch
           ├── Creates arch-specific DataSources
           │    e.g., centos-stream9-amd64, centos-stream9-arm64
           └── Pointer DataSource (centos-stream9) → default arch DS
                │
                KubeVirt
                ├── VM spec.architecture targets specific arch
                ├── Scheduler places VM on matching arch node
                └── Migration only between same-arch nodes
```

## Team Responsibilities

### HCO (sig-iuo)

**What HCO does:**

1. **Detects cluster architecture composition**: Monitors worker and control-plane nodes via `status.nodeInfo.architecture` field. Worker nodes identified by `node-role.kubernetes.io/worker` label (or via `spec.workloads.nodePlacement`). Control-plane nodes identified by `node-role.kubernetes.io/control-plane` or `node-role.kubernetes.io/master` label.

2. **Manages the `enableMultiArchBootImageImport` feature gate**: When disabled, HCO behaves as before (no arch-specific resources). When enabled, activates the full multiarch pipeline.

3. **Filters DICT annotations**: At HCO image build time, predefined DICTs receive `ssp.kubevirt.io/dict.architectures` annotations as comma-separated values (e.g., `amd64,arm64`). During reconciliation, HCO removes unsupported architectures from these annotations based on current cluster capabilities.

4. **Propagates architecture info to SSP**: Sets `enableMultipleArchitectures`, `cluster.workloadArchitectures`, and `cluster.controlPlaneArchitectures` on the SSP CR.

5. **Tracks DICT deployment status**: For each DICT, HCO stores `originalSupportedArchitectures` (the pre-filter annotation) and conditions in `status.dataImportCronTemplates`. DICTs with no supported cluster architectures are excluded from SSP but tracked with `Deployed=False, Reason=UnsupportedArchitectures`.

6. **Manages 3 multiarch-related alerts and metrics** (see Alerts section below).

**Key HCO behavior details:**

- If the DICT has no `ssp.kubevirt.io/dict.architectures` annotation, it passes through without filtering (backward compatible).
- If a common (predefined) DICT is customized by the user but the image source is unchanged, HCO uses the original supported architectures rather than the user's annotation override.
- HCO dynamically updates architecture lists when nodes are added/removed from the cluster.

### SSP (sig-infra)

**What SSP does:**

1. **Creates arch-specific DataImportCron CRs**: For each supported architecture in the DICT annotation, SSP creates a separate DIC with:
   - Name suffixed with architecture: `<original-name>-<arch>` (e.g., `centos-stream9-image-cron-amd64`)
   - Label: `template.kubevirt.io/architecture: <arch>`
   - Label: `cdi.kubevirt.io/storage.import.datasource-name: <datasource-name>`
   - Field: `spec.template.spec.source.registry.platform.architecture: <arch>`

2. **Creates arch-specific VM templates**: Deploys templates corresponding to supported cluster architectures with correct labels for discovery. Templates reference arch-specific DataSources.

3. **Creates pointer DataSources for backward compatibility**: SSP creates an architecture-agnostic pointer DataSource with the original name (no suffix, no architecture label). Its `spec.source.dataSource` points to the default arch-specific DataSource. Default architecture is `controlPlaneArchitectures[0]`.

4. **Dynamically adjusts**: When cluster composition changes (nodes added/removed), SSP adds/removes DIC CRs and templates accordingly based on updated SSP CR fields from HCO.

5. **Removes legacy DICs**: When transitioning a template from non-annotated to annotated, SSP removes the old unsuffixed DIC and creates new suffixed ones.

### CDI (sig-storage)

**What CDI does:**

1. **Imports arch-specific images**: Each DIC triggers an import with architecture awareness:
   - **`pullMethod==pod`**: CDI-importer uses the `platform.architecture` field to request the correct arch-specific image from the container registry. Sets OS field to `linux` (the platform reflects the runtime environment, since VM images in KubeVirt may represent different guest operating systems).
   - **`pullMethod==node`**: CDI-controller creates a pod with an init container containing the required image. CRI performs the actual pull, matching the node's architecture. CDI-controller modifies the pod's `nodeSelector`/`nodeAffinity` to force scheduling on a node with `kubernetes.io/arch` label matching `spec.template.spec.source.registry.platform.architecture`. If no matching node exists, CDI reports failure in DIC conditions.

2. **Reconciles pointer DataSources**: When a DataSource has `spec.source.dataSource` populated (set by SSP), CDI copies the pointed-to DataSource's `status.source` into the pointer's `status.source`. This enables transparent resolution for consumers.

3. **Propagates labels**: CDI propagates `template.kubevirt.io/architecture` and `cdi.kubevirt.io/storage.import.datasource-name` labels from DIC to resulting DataSource CRs.

4. **Cloning modification**: CDI-cloner uses `status.source` (not `spec.source`) when populating VM PVCs, enabling proper resolution through pointer DataSources.

### KubeVirt (sig-virt)

**What KubeVirt does:**

1. **Schedules VMs to matching architecture nodes**: Uses `VirtualMachineInstanceSpec.Architecture` field to ensure VMs run only on nodes with matching `kubernetes.io/arch` label.

2. **Manages VM migration**: Live migration is only allowed between nodes of the same architecture. Cross-architecture migration is rejected.

3. **Manages `defaultCPUModel` per architecture**: Each architecture can have its own default CPU model configuration.

4. **Preserves architecture placement during upgrades**: VMs retain their architecture placement after cluster upgrade.

## API Changes Reference

### HCO API

| Field Path | Type | Description |
|:-----------|:-----|:------------|
| `spec.featureGates.enableMultiArchBootImageImport` | bool | Enables/disables multiarch golden image support (default: false in 4.22) |
| `status.nodeInfo.controlPlaneArchitectures` | []string | List of control-plane node architectures detected in the cluster |
| `status.nodeInfo.workloadsArchitectures` | []string | List of worker node architectures detected in the cluster |
| `status.dataImportCronTemplates[].status.originalSupportedArchitectures` | string | Preserves the original annotation value before filtering |
| `status.dataImportCronTemplates[].status.conditions` | []Condition | Includes deployment status with reasons like `UnsupportedArchitectures` |

### SSP API

| Field Path | Type | Description |
|:-----------|:-----|:------------|
| `spec.enableMultipleArchitectures` | bool | Activates arch-aware DIC and template creation |
| `spec.cluster.workloadArchitectures` | []string | Worker node architectures (set by HCO) |
| `spec.cluster.controlPlaneArchitectures` | []string | Control-plane node architectures (set by HCO) |

### CDI API

| Field Path | Type | Description |
|:-----------|:-----|:------------|
| `DataVolumeSourceRegistry.platform.architecture` | string | Target CPU architecture for image import |
| `DataSourceSource.dataSource.namespace` | string | Pointer DataSource: target namespace |
| `DataSourceSource.dataSource.name` | string | Pointer DataSource: target DataSource name |

### KubeVirt API

| Field Path | Type | Description |
|:-----------|:-----|:------------|
| `VirtualMachineInstanceSpec.Architecture` | string | Targets VM to specific CPU architecture |

## Annotations and Labels

| Key | Applied To | Values | Purpose |
|:----|:-----------|:-------|:--------|
| `ssp.kubevirt.io/dict.architectures` | DICT | Comma-separated archs (e.g., `amd64,arm64`) | Specifies supported architectures for this golden image |
| `template.kubevirt.io/architecture` | DIC, DataSource, VM Template | Single arch (e.g., `amd64`) | Identifies the target architecture of this resource |
| `cdi.kubevirt.io/storage.import.datasource-name` | DIC | DataSource name | Associates DIC with its target DataSource |
| `cdi.kubevirt.io/storage.bind.immediate.requested` | DICT | `true` | Requests immediate storage binding |

## Alerts and Metrics

| Alert | Fires When | Metric | Severity |
|:------|:-----------|:-------|:---------|
| `HCOGoldenImageWithNoSupportedArchitecture` | DICT annotated with architectures not present in the cluster | `kubevirt_hco_dataimportcrontemplate_with_supported_architectures` | Warning |
| `HCOMultiArchGoldenImagesDisabled` | Multi-arch cluster detected but FG is disabled (and nodePlacement does not restrict to single arch) | `kubevirt_hco_multi_arch_boot_images_enabled` | Warning |
| `HCOGoldenImageWithNoArchitectureAnnotation` | Custom DICT lacks `ssp.kubevirt.io/dict.architectures` annotation | `kubevirt_hco_dataimportcrontemplate_with_architecture_annotation` | Info |

Runbooks:

- [HCOGoldenImageWithNoSupportedArchitecture](https://kubevirt.io/monitoring/runbooks/HCOGoldenImageWithNoSupportedArchitecture)
- [HCOMultiArchGoldenImagesDisabled](https://kubevirt.io/monitoring/runbooks/HCOMultiArchGoldenImagesDisabled.html)
- [HCOGoldenImageWithNoArchitectureAnnotation](https://kubevirt.io/monitoring/runbooks/HCOGoldenImageWithNoArchitectureAnnotation)

## Resource Naming Convention

When multiarch is enabled, resources are created with architecture-specific suffixes:

| Resource Type | Naming Pattern | Example |
|:--------------|:---------------|:--------|
| DataImportCron | `<original-name>-<arch>` | `centos-stream9-image-cron-amd64` |
| DataSource (arch-specific) | `<original-name>-<arch>` | `centos-stream9-amd64` |
| DataSource (pointer/legacy) | `<original-name>` | `centos-stream9` (points to default arch DS) |
| VM Template | Labeled with `template.kubevirt.io/architecture` | `centos-stream9-server-small` with label `arm64` |

## Predefined vs Custom Golden Images

| Aspect | Predefined (built-in) | Custom (user-defined) |
|:-------|:----------------------|:----------------------|
| Annotation source | Set at HCO image build time | User must supply `ssp.kubevirt.io/dict.architectures` |
| Architecture validation | HCO filters to cluster-supported archs | HCO respects but does not validate values |
| Image override behavior | If user changes only the annotation (not the image source), HCO uses original arch list | User's annotation is used as-is |
| Missing annotation | All predefined DICTs have annotations | DICT passes through without arch filtering; `HCOGoldenImageWithNoArchitectureAnnotation` alert fires |

## Conditions for Multiarch Activation

Both conditions must be met for architecture-specific changes to apply:

1. `enableMultiArchBootImageImport` feature gate must be enabled
2. Cluster must NOT be a single-node cluster (SNO)

On single-node clusters, all architecture-related changes are skipped even if the FG is enabled.

## Backward Compatibility

The pointer DataSource mechanism ensures backward compatibility:

1. When multiarch is enabled, SSP creates arch-specific DataSources (e.g., `centos-stream9-amd64`, `centos-stream9-arm64`) via DICs
2. SSP also creates a pointer DataSource with the original name (e.g., `centos-stream9`) - no arch suffix, no architecture label
3. The pointer's `spec.source.dataSource` references the default arch-specific DataSource (default = `controlPlaneArchitectures[0]`)
4. CDI reconciles the pointer: copies `status.source` from the referenced DataSource into the pointer's `status.source`
5. Existing tools referencing the original name continue working transparently
6. CDI-cloner reads `status.source` instead of `spec.source` to properly resolve through pointers
7. DICTs without `ssp.kubevirt.io/dict.architectures` annotation are treated as legacy: SSP creates a single DIC without suffix (no new labels or platform fields)
8. When transitioning (annotation added to existing template): SSP removes the old unsuffixed DIC and creates new suffixed ones
9. For DataSources pointing to manually-created PVC/Snapshot (not managed by DIC): SSP assumes default architecture

## Pointer DataSource Example

```yaml
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataSource
metadata:
  name: centos-stream9
  namespace: kubevirt-os-images
spec:
  source:
    dataSource:
      name: centos-stream9-amd64
      namespace: kubevirt-os-images
status:
  conditions:
  - message: DataSource is ready to be consumed
    reason: Ready
    status: "True"
    type: Ready
  source:
    snapshot:
      name: centos-stream9-e065d9079064
      namespace: kubevirt-os-images
```

## Error Handling

| Condition | Behavior |
|:----------|:---------|
| DICT has only unsupported architectures | Excluded from SSP deployment; tracked in HCO status with `UnsupportedArchitectures` reason |
| No matching arch node for `pullMethod==node` | CDI reports failure in DIC conditions; import does not proceed |
| Unsupported image manifest for requested arch | CDI reports failure in DIC conditions |
| FG disabled on multi-arch cluster | Warning alert `HCOMultiArchGoldenImagesDisabled` fires (unless nodePlacement restricts to single arch) |
| Custom DICT missing arch annotation | Info alert `HCOGoldenImageWithNoArchitectureAnnotation` fires; DICT passes through without filtering |
| Node added with new architecture | HCO updates SSP CR; SSP creates new DICs and templates for the new arch |
| Node removed (last of its arch) | HCO updates SSP CR; SSP removes DICs and templates for that arch |
| Single-node cluster (SNO) | All architecture-related changes are skipped even if FG is enabled |
| Image not a manifest or lacks specified architecture | CDI reports failure in DIC conditions |

## Existing Upstream Test Coverage (HCO)

The HCO repo has 7 multiarch-specific functional tests in `tests/func-tests/golden_image_test.go`:

1. **Verify HCO status has worker architectures** - checks `status.nodeInfo.workloadsArchitectures`
2. **Verify SSP CR has architectures** - checks `MultiArchDICTAnnotation` contains only supported archs
3. **Verify user-defined DICT architecture filtering** - creates DICT with mixed supported/unsupported archs, verifies filtering
4. **Verify customized common DICT architecture handling** - modifies common DICT annotations, verifies behavior
5. **Verify DICT without annotation skips filtering** - creates DICT without arch annotation, verifies passthrough
6. **Verify DICT with no supported archs excluded** - creates DICT with only unsupported archs, verifies exclusion with `UnsupportedArchitectures` reason
7. **Verify common DICT with unchanged image uses original archs** - modifies annotation but not image, verifies original arch list used


## Implementation Dependencies

- SSP implementation depends on CDI API changes being released first
- HCO implementation depends on new CDI and SSP releases containing the API changes
- Implementation phases: CDI changes first, then SSP adoption, then HCO orchestration

## Known Bugs

- [CNV-68981](https://issues.redhat.com/browse/CNV-68981) - [UI] Architecture is incorrect for Fedora ARM and inconsistent on UI for other OS
- [CNV-68996](https://issues.redhat.com/browse/CNV-68996) - [Storage] Arch-specific DataSources (arm64) persist after removing arm64 nodes

## Test Environment

- **Platform**: AWS (ARM64 workers available)
- **Cluster**: 3 amd64 control-plane nodes, 2 amd64 worker nodes, 2 arm64 worker nodes
- **Storage**: io2-csi (AWS EBS io2 CSI driver)
- **Network**: OVN-Kubernetes (default)
- **Constraint**: MultiArch cluster available for 12 hours only
