# Openshift-virtualization-tests Test plan

## Multi-Architecture Boot Image Import and DataSource Lifecycle - Quality Engineering Plan

### **Metadata & Tracking**

- **Enhancement(s):** [VEP: Heterogeneous Cluster Support](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster)
- **Feature Tracking:** [VIRTSTRAT-494 - Multiarch Support enablement for ARM](https://issues.redhat.com/browse/VIRTSTRAT-494)
- **Epic Tracking:**
  - [CNV-75960](https://issues.redhat.com/browse/CNV-75960) — Infra Multi-arch boot image import and DataSource lifecycle
- **Parent STP:** [HCO support for heterogeneous multi-arch clusters (#12)](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/pull/12)
- **QE Owner(s):** Geetika Kapoor (@geetikakay)
- **Owning SIG:** sig-infra
- **Participating SIGs:** sig-iuo, sig-storage

**Document Conventions (if applicable):**

- **Golden Image**: Pre-configured bootable OS volume used as template for VM creation
- **Heterogeneous cluster**: Cluster with worker nodes of different CPU architectures (primarily amd64 and arm64)
- **Architecture-specific golden image**: Golden image labeled with a specific architecture suffix (e.g. `rhel9-amd64`, `rhel9-arm64`)


### **Feature Overview**

This STP is an extension of the [parent STP (#12)](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/pull/12) covering **only** sig-infra-specific edge cases not already addressed by the parent or other SIG STPs.

The parent STP already covers: golden image provisioning lifecycle, architecture-specific boot source creation, cleanup on node removal, custom golden image annotations, feature gate toggle behavior, VM creation from templates and upgrade testing.

This STP adds coverage for: bootable volume re-import validation on existing clusters, storage resource label validation, architecture-incompatible image handling and backward compatibility on single-arch clusters.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- **Review Requirements**
  - *Key requirements reviewed:*
    - Bootable volume re-import behavior when enabling the feature on clusters with pre-existing volumes (documented expected behavior per [CNV-75084](https://issues.redhat.com/browse/CNV-75084))
    - Correct architecture labels on all storage resources (DataVolumes, VolumeSnapshots, PVCs)
    - Graceful failure with clear error messaging for architecture-incompatible VM creation
    - Backward compatibility on single-arch clusters when the feature is enabled
- **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:*
    - Extends parent STP coverage for edge cases around re-import behavior, label correctness and backward compatibility
  - *List the customer use cases identified:*
    - A cluster admin enables multi-arch support on an existing cluster with pre-existing bootable volumes and expects them to be re-imported with correct architecture-specific labels
    - A VM operator attempts to create a Windows VM on an ARM node and expects a clear error
    - A cluster admin enables the feature on a single-arch cluster and expects no regressions
- **Testability**
  - *Note any requirements that are unclear or untestable:*
    - All scenarios testable on heterogeneous AWS cluster or single-arch cluster
- **Acceptance Criteria**
  - *List the acceptance criteria:*
    - Bootable volumes are re-imported with correct architecture-specific labels when enabling the feature on a cluster with existing volumes (expected behavior)
    - Architecture labels are correct on all associated DataVolumes, VolumeSnapshots and PVCs
    - VM creation fails gracefully with a clear error when using an architecture-incompatible image
    - Single-arch clusters continue working unchanged — no duplicates, existing workflows unaffected

#### **2. Known Limitations**

- Bootable volume re-import on enable: When enabling multi-arch boot image import on a cluster with existing bootable volumes, those volumes are re-imported with architecture-specific labels. This is documented expected behavior per [CNV-75084](https://issues.redhat.com/browse/CNV-75084).
- Retention policy on disable: Disabling the feature does not automatically delete architecture-specific golden images. Cleanup depends on SSP retention policy. (Tested in parent STP.)
- Multi-arch cluster availability: Available only for 12-hour windows, limiting scope and duration of test runs.

#### **3. Technology and Design Review**

- **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Covered in parent STP and in team discussions
- **Technology Challenges**
  - *List identified challenges:*
    - Multi-arch cluster available only for 12-hour windows
    - Node removal simulated via nodePlacement where dynamic add/remove is not feasible
  - *Impact on testing approach:*
    - Tests limited to AWS platform
- **Test Environment Needs**
  - *See environment requirements in Section II.3*

---

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources and schedule.

#### **1. Scope of Testing**

**Testing Goals**

Edge cases specific to golden image lifecycle not covered by the parent STP:

- **[P0]** Bootable volumes are re-imported with correct architecture-specific labels when enabling the feature on a heterogeneous cluster with existing volumes
- **[P1]** Architecture labels are correct on all associated DataVolumes, VolumeSnapshots and PVCs for golden images
- **[P1]** Graceful failure with clear error message when creating a VM from an architecture-incompatible image (e.g. Windows on ARM)
- **[P1]** Post-deployment DataImportCron additions (e.g. Windows, Alpine) create architecture-specific images for all available node architectures
- **[P1]** Single-arch clusters continue working unchanged when the feature is enabled — no duplicate golden images, existing workflows unaffected

**Already Covered by Parent STP**

The following are explicitly handled in the [parent STP (#12)](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/pull/12) and are **not** retested in this STP:

- Golden image creation and labeling on heterogeneous clusters (sig-iuo P0)
- Custom golden image annotation handling and alerts (sig-iuo P0)
- VM creation from architecture-specific templates (sig-infra P0 in parent)
- Boot source cleanup on node removal (sig-infra P2 in parent)
- Feature gate disable behavior (sig-iuo P2 in parent)
- VM creation from legacy boot sources (sig-infra P0 in parent)
- Mixed architecture VM deployment (sig-virt P0 in parent)
- Upgrade testing (sig-iuo P1 in parent)

**Out of Scope (Testing Scope Exclusions)**

- **Performance, Monitoring, Scalability, Usability NFRs**
  - *Rationale:* Not in scope for functional validation
- **HCO nodeInfo architecture tracking**
  - *Rationale:* Covered in parent STP
- **VM scheduling to correct architecture nodes**
  - *Rationale:* Covered under [Virt Multi-arch STP (#19)](https://github.com/RedHatQE/openshift-virtualization-tests-design-docs/pull/19)

**Test Limitations**

- Tests limited to AWS, no bare metal clusters
- 12-hour ARM cluster availability window
- No Windows guest tested on ARM64

#### **2. Test Strategy**

**Functional**

- **Functional Testing** — Validates edge cases around re-import behavior, label correctness and error handling
  - *Details:* All scenarios automated in openshift-virtualization-tests repo
- **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage
  - *Details:* All test cases automated in openshift-virtualization-tests repo

**Non-Functional**

- **Performance Testing** — N/A, out of scope
- **Monitoring** — N/A, covered in parent STP

**Integration & Compatibility**

- **Backward Compatibility Testing** — Validates single-arch cluster behavior when feature is enabled
  - *Details:* Verify no duplicates and no regression on amd64-only clusters
- **Regression Testing** — N/A, covered by parent STP's per-SIG regression plan
- **Dependencies** — CDI operator for imports, SSP operator for golden image management

#### **3. Test Environment**

- **Cluster Topology:** Multi-arch heterogeneous cluster (3 amd64 control-plane, 2 amd64 workers, 2 arm64 workers). Single-arch cluster for backward compatibility testing.
- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22
- **Storage:** io2-csi storage class (AWS EBS io2 CSI driver)
- **Network:** OVN-Kubernetes
- **Required Operators:** SSP operator v4.22+, CDI operator v1.60+, HCO v4.22+
- **Platform:** AWS

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** pytest, openshift-virtualization-tests framework
- **CI/CD:** Existing CNV-QE pipeline with multi-arch cluster support
- **Other Tools:** oc CLI, jq, kubectl, virtctl

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Parent STP requirements and design documents are **approved and merged**
- [ ] Test environment with multi-arch cluster can be **set up and configured**
- [x] Multi-arch boot image import feature is **available in target release**

#### **5. Risks**

**Test Environment**

- **Risk:** 12-hour ARM64 cluster availability window limits test execution time.
  - **Mitigation:** Prioritize test execution. Ticket raised with Devops.
  - *Missing resources or infrastructure:* Longer cluster availability for full test runs.

---

### **III. Test Scenarios & Traceability**

Only scenarios **not covered by the parent STP** are included. Each scenario covers sig-infra-specific behavior which is not part of parent STP.

**sig-infra — Additive Functional Tests**

- **[CNV-75960](https://issues.redhat.com/browse/CNV-75960)** — As a cluster admin, I want bootable volumes to be re-imported with correct architecture labels when enabling multi-arch support on an existing cluster
  - *Test Scenario:* [Tier 2] Enable multi-arch boot image import on a heterogeneous cluster that already has existing bootable volumes. Verify volumes are re-imported with correct architecture-specific labels (documented expected behavior per [CNV-75084](https://issues.redhat.com/browse/CNV-75084)).
  - *Priority:* P0
- **[CNV-75960](https://issues.redhat.com/browse/CNV-75960)** — As a cluster admin, I want correct architecture labels on all storage resources
  - *Test Scenario:* [Tier 2] Verify architecture labels are correct on all associated DataVolumes, VolumeSnapshots and PVCs for golden images on a heterogeneous cluster.
  - *Priority:* P1
- **[CNV-75960](https://issues.redhat.com/browse/CNV-75960)** — As a cluster admin, I want post-deployment DataImportCron additions to create architecture-specific images
  - *Test Scenario:* [Tier 2] Add new DataImportCron (e.g. Windows, Alpine) on an existing multi-arch cluster. Verify architecture-specific images are created for all available node architectures.
  - *Priority:* P1
- **[CNV-75960](https://issues.redhat.com/browse/CNV-75960)** — As a VM operator, I want a clear error when creating a VM from an architecture-incompatible image
  - *Test Scenario:* [Tier 2] Attempt to create a Windows VM on an ARM node when only an x86 image is available. Verify graceful failure with a clear error message.
  - *Priority:* P1

**sig-infra — Backward Compatibility Tests**

- **[CNV-75960](https://issues.redhat.com/browse/CNV-75960)** — As a cluster admin, I want single-arch clusters to continue working unchanged when the feature is enabled
  - *Test Scenario:* [Tier 2] Enable multi-arch boot image import on a single-arch (amd64-only) cluster. Verify only amd64 golden images exist, no duplicates are created and existing workflows remain unaffected.
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

- **Reviewers:**
  - QE Members (sig-infra): @RoniKishner
  - QE Members (sig-iuo): @hmeir
  - QE Members (sig-network): @yossisegev
- **Approvers:**
  - QE Architect: @rnetser
