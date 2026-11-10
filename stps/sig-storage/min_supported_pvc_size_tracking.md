# Openshift-virtualization-tests Test plan

## **Track PVCs Inflated to Storage Profile Minimum Supported Size - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [CDI PR #4281](https://github.com/kubevirt/containerized-data-importer/pull/4281)
- **Feature Tracking:** [CNV-97015](https://redhat.atlassian.net/browse/CNV-97015)
- **Epic Tracking:** [CNV-99388](https://redhat.atlassian.net/browse/CNV-99388)
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: 5.1
- **QE Owner(s):** Ahmad Hafe (@Ahmad-Hafe, ahafe@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage

**Document Conventions:**

- **Size inflation:** CDI raises an undersized request to the storage-profile minimum after filesystem overhead. Labels are set only when that minimum step increases the size.
- **Inflation labels:** PVC labels for the original requested size (raw bytes) and the bump source (`datavolume` or `external`), set together only when size inflation applies.
- **Direct PVC opt-in:** Label on a PVC created without a DataVolume that allows CDI to apply the storage-profile minimum.
- **MinimumPVCSizeApplied event:** Existing DataVolume event CDI emits when size inflation occurs (visible on the DataVolume; short-lived).

### **Feature Overview**

Some cloud storage classes enforce a minimum volume size. CDI already inflates undersized requests to that minimum so create and clone can succeed. The only signal today is the short-lived `MinimumPVCSizeApplied` DataVolume event, which expires and does not cover PVCs created without a DataVolume.

This feature does not change sizing rules. When inflation happens, the PVC is labeled with the original request and the bump source so administrators can identify volumes bumped above the requested size and compare requested versus effective capacity across the cluster. Alerts and dashboards for unexpected over-provisioning from minimum-supported-size inflation are not covered here; observability can extend that later. This STP covers GA in CNV 5.1.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - [CNV-97015](https://redhat.atlassian.net/browse/CNV-97015) — Inflated PVCs must record the original requested size and whether the bump came from a DataVolume or a direct/external PVC
    - [CNV-97015](https://redhat.atlassian.net/browse/CNV-97015) — Filesystem-overhead-only growth must not be recorded as size inflation
    - [CNV-97015](https://redhat.atlassian.net/browse/CNV-97015) — Non-inflated volumes must not receive inflation labels
    - [CNV-97015](https://redhat.atlassian.net/browse/CNV-97015) — Existing size-inflation behavior and the `MinimumPVCSizeApplied` DataVolume event remain unchanged

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Administrators can inventory inflated volumes and recover the original request without relying on expired events.
  - *List the customer use cases identified:*
    - As a cluster administrator, I want inflated PVCs to keep a durable record of the original request and bump source, so that I can audit size inflation across the cluster.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None for the label contract. Jira still mentions annotation/metric wording; this STP asserts PVC inflation labels. Metrics/alerts/dashboards remain Out of Scope.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - Below-minimum DataVolume (request still below the minimum after filesystem overhead, or block mode) succeeds; PVC equals the storage-profile minimum; both inflation labels present; original-size label equals the DataVolume request in bytes; source `datavolume`; a `MinimumPVCSizeApplied` event appears on the DataVolume
    - Below-minimum opted-in direct PVC becomes Bound; PVC equals the storage-profile minimum; both inflation labels present; source `external`
    - Filesystem-overhead-only growth sets no inflation labels
    - Direct PVC below minimum without opt-in keeps the original request and sets no inflation labels
    - Opted-in PVC at or above the minimum is not inflated and sets no inflation labels
    - Below-minimum PVC-source clone succeeds with both inflation labels and source `datavolume`; original-size label matches the destination request
    - Below-minimum snapshot-source clone succeeds with both inflation labels and source `datavolume`
  - *Note any gaps or missing criteria:* None. Metrics/alerts, docs, UI, performance, and scale are Out of Scope.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Observability:** Inflation labels are the durable record; Tier 2 asserts presence, absence, and values on the PVC
  - *Note any NFRs not covered and why:*
    - **Monitoring:** Metrics and alerts are Out of Scope (observability may extend later)
    - **Documentation:** Out of Scope for this Tier 2 plan
    - **UI:** No console workflow; customer value is API/label audit — PM/UX not requesting console coverage (Out of Scope)
    - **Performance:** No new performance targets (Out of Scope)
    - **Security:** No new RBAC or security surface
    - **Scalability:** No new cluster-level scale requirements; create/clone still use existing PVC paths (Out of Scope for dedicated scale scenarios)

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- **No backfill on upgrade** — Labels apply only to newly inflated PVCs.
  - *Sign-off:* Pending

- **Non-DV clone populator PVCs skip minimum inflation** — Clone PVCs created without a DataVolume do not receive storage-profile minimum inflation or inflation labels. DataVolume controller clones remain in scope.
  - *Sign-off:* Pending

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Reviewed with CDI development. Labels apply only when CDI inflates the request to the storage-profile minimum. Per [CDI PR #4281 discussion](https://github.com/kubevirt/containerized-data-importer/pull/4281#issuecomment-6248168500), unit tests are preferred for this change; e2e adds little unless multiple components are involved. This STP covers Tier 2 create/clone paths in openshift-virtualization-tests and does not duplicate that unit-test coverage. No untestable in-scope aspects.

- [x] **Technology Challenges**
  - *List identified challenges:* Need a StorageClass whose StorageProfile has a usable minimum; snapshot-source clone needs a below-minimum restore size.
  - *Impact on testing approach:* Pick any StorageClass with a real storage-profile minimum; gate the snapshot scenario when VolumeSnapshot support is missing.

- [x] **API Extensions**
  - *List new or modified APIs:* No new APIs. Two additive PVC labels (see Document Conventions). Existing `MinimumPVCSizeApplied` DataVolume event unchanged.
  - *Testing impact:* Assert label presence/absence and values.

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* No special cluster or network topology. Any standard OpenShift Virtualization cluster is sufficient when a StorageClass provides a usable storage-profile minimum (VolumeSnapshot support only for the snapshot-clone scenario).
  - *Impact on test design:* None.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify a below-minimum DataVolume (request still below the minimum after filesystem overhead, or block mode) finishes inflated with both inflation labels, source `datavolume`, original-size matching the request in bytes, and a `MinimumPVCSizeApplied` event on the DataVolume
- **[P0]** Verify a below-minimum opted-in direct PVC finishes Bound inflated with both inflation labels and source `external`
- **[P0]** Verify filesystem-overhead-only growth sets no inflation labels
- **[P0]** Verify a below-minimum direct PVC without opt-in keeps the original request and sets no inflation labels
- **[P0]** Verify an opted-in PVC at or above the storage-profile minimum is not inflated and sets no inflation labels
- **[P1]** Verify a below-minimum PVC-source clone finishes inflated with both inflation labels and source `datavolume`
- **[P1]** Verify a below-minimum snapshot-source clone finishes inflated with both inflation labels and source `datavolume`

**Existing Coverage (not duplicated here)**

- **CDI lower-level honesty coverage** — Owned by CDI development. This STP covers Tier 2 create/clone paths in openshift-virtualization-tests and does not re-test that layer.
- **Direct PVC opt-in / `external` source contract** — Proven by the opted-in, missing-opt-in, and at/above-minimum scenarios in Section III; dedicated DataImportCron / image-upload / backend-storage product paths are not duplicated.

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- **Metrics, alerts, and PromQL / dashboard validation**
  - *Rationale:* This STP covers PVC inflation labels only; observability may extend alerts/dashboards later
  - *PM/Lead Agreement:* Pending

- **Documentation / release-note validation**
  - *Rationale:* Outside this Tier 2 automation plan
  - *PM/Lead Agreement:* Pending

- **UI testing**
  - *Rationale:* No console workflow in this delivery; customer value is API/label audit
  - *PM/Lead Agreement:* Pending

- **Full cloud provisioner matrix**
  - *Rationale:* Behavior depends on a StorageProfile minimum, not on a specific cloud provider; one StorageClass with a usable minimum proves the label contract
  - *PM/Lead Agreement:* Pending

- **Performance benchmarking**
  - *Rationale:* No performance targets for inflation labels
  - *PM/Lead Agreement:* Pending

- **Dedicated scale / load scenarios**
  - *Rationale:* No new cluster-level scale requirements; create/clone use existing PVC paths
  - *PM/Lead Agreement:* Pending

**Test Limitations**

- **CDI build with inflation labels required** — Tier 2 execution cannot start until inflation labels are in the CNV build under test
  - *Sign-off:* Pending

- **Snapshot-source scenario needs VolumeSnapshot support** — Gate TS-07 when the cluster has no VolumeSnapshot-capable storage
  - *Sign-off:* Pending

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Scenarios cover below-minimum DataVolume create (labels, original-size bytes, `MinimumPVCSizeApplied` event), opted-in direct PVC inflate, filesystem-overhead-only (no labels), missing opt-in (no labels), at/above-minimum (no labels), PVC-source clone inflate, and snapshot-source clone inflate.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All Section III scenarios automated in openshift-virtualization-tests; run in existing sig-storage CI lanes.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Existing sig-storage DataVolume create/clone and related CDI sizing suites in openshift-virtualization-tests keep running on the feature cluster. Regression coverage is not listed in Section III.

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* N/A — Tier 2 label-contract checks need a StorageClass with a usable storage-profile minimum; not proposed for the self-validation package.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A — no performance targets; see Out of Scope.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* N/A — no dedicated scale scenarios; see Out of Scope.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* N/A — no new RBAC roles, security boundaries, or authentication changes.

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* N/A — no UI; customer value is API/label audit (Out of Scope).

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* N/A — no new metrics or alerts in this STP; scenarios assert PVC inflation labels only (Out of Scope).

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Validate on a StorageClass whose StorageProfile has a usable minimum; snapshot-source clone requires VolumeSnapshot support. Behavior is not cloud-provider-specific.

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* N/A — no backfill on upgrade (Known Limitation); upgrade path evaluated and excluded.

- [x] **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* Blocked on [CDI PR #4281](https://github.com/kubevirt/containerized-data-importer/pull/4281) merge and image promotion into the CNV build under test.

- [ ] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* No. sig-storage owns Tier 2 label coverage. Metrics/alerts remain Out of Scope for observability later.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* N/A — not cloud-provider-specific; full cloud matrix is Out of Scope.

#### **3. Test Environment**

- **Cluster Topology:** Single-node or multi-node; no multi-node requirement

- **OCP & OpenShift Virtualization Version(s):** OCP 5.0+ / CNV 5.0+ with a CDI build that includes inflation labels

- **CPU Virtualization:** Standard

- **Compute Resources:** Standard

- **Special Hardware:** N/A

- **Storage:** `ocs-storagecluster-ceph-rbd-virtualization` (or equivalent) whose StorageProfile has a usable minimum PVC size above the test request; snapshot-source clone needs restore size below that minimum and a VolumeSnapshot-capable StorageClass / VolumeSnapshotClass

- **Network:** Standard (OVN-Kubernetes)

- **Required Operators:** OpenShift Virtualization / CDI

- **Platform:** Bare metal or PSI (virtualized); record the platform used with results

- **Special Configurations:** Distinguish minimum inflation from filesystem-overhead-only growth; direct PVC opt-in label required for non-DataVolume inflate; WaitForFirstConsumer where required

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** N/A — existing sig-storage lanes

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged** ([CNV-97015](https://redhat.atlassian.net/browse/CNV-97015), [CDI PR #4281](https://github.com/kubevirt/containerized-data-importer/pull/4281))
- [ ] CDI inflation labels are available in the CNV build under test
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] StorageClass with a usable storage-profile minimum is available (VolumeSnapshot-capable for the snapshot-clone scenario)
- [ ] Sign-offs on Known Limitations, Out of Scope, Test Limitations, and Risks are filled (not Pending)

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Testing is blocked until inflation labels land in a CNV test build; late CDI delivery compresses Tier 2 automation before release readiness
  - **Mitigation:** Gate entry criteria on the CDI build; implement tests against development builds when available
  - *Estimated impact on schedule:* P0 execution blocked until CDI image promotion; later delivery compresses automation before GA
  - *Sign-off:* Pending

**Test Coverage**

**Test Environment**

- **Risk:** CI may lack a StorageClass whose StorageProfile has a usable minimum, or VolumeSnapshot support for the snapshot-clone scenario
  - **Mitigation:** Use `ocs-storagecluster-ceph-rbd-virtualization` (or equivalent) with a real storage-profile minimum; gate the snapshot scenario when VolumeSnapshot support is missing
  - *Missing or unavailable environments:* Environment-dependent StorageClass / VolumeSnapshot capability
  - *Sign-off:* Pending

**Untestable Aspects**

**Resource Constraints**

**Dependencies**

- **Risk:** Feature depends on [CDI PR #4281](https://github.com/kubevirt/containerized-data-importer/pull/4281) merge and image promotion into the CNV build under test
  - **Mitigation:** Keep entry criteria gated on that CDI build; do not start Tier 2 automation against a build without inflation labels
  - *Dependent teams or components:* CDI / OpenShift Virtualization image promotion
  - *Sign-off:* Pending

---

### **III. Test Scenarios & Traceability**

#### **1. Requirements-to-Tests Mapping**

- **[CNV-97015]** — As a cluster administrator, I want a below-minimum DataVolume to finish inflated with source `datavolume`, so that I can audit silently inflated volumes
  - *Test Scenario:* **TS-01**: [Tier 2] Create a below-minimum DataVolume whose request remains below the minimum after filesystem overhead (or use block mode); PVC request equals the storage-profile minimum; both inflation labels are present with source `datavolume`; original-size label equals the submitted DataVolume request in bytes; a `MinimumPVCSizeApplied` event appears on the DataVolume
  - *Priority:* P0

- **[CNV-97015]** — As a cluster administrator, I want a below-minimum opted-in direct PVC to finish Bound inflated with source `external`, so that non-DataVolume inflation is auditable
  - *Test Scenario:* **TS-02**: [Tier 2] Create a below-minimum opted-in direct PVC; PVC becomes Bound at the minimum; both inflation labels are present with source `external`
  - *Priority:* P0

- **[CNV-97015]** — As a storage operator, I want filesystem-overhead-only growth to leave PVCs unlabeled, so that overhead adjustments are not reported as size inflation
  - *Test Scenario:* **TS-03**: [Tier 2] Create a filesystem PVC whose size grows only by filesystem overhead; no inflation labels are set
  - *Priority:* P0

- **[CNV-97015]** — As a storage operator, I want a below-minimum direct PVC without opt-in to keep its original request unlabeled, so that non-opted-in volumes are not reported as inflated
  - *Test Scenario:* **TS-04**: [Tier 2] Create a below-minimum direct PVC without opt-in; original request is retained and no inflation labels are set
  - *Priority:* P0

- **[CNV-97015]** — As a storage operator, I want an opted-in PVC at or above the minimum to stay unlabeled, so that non-inflated volumes are not reported as inflated
  - *Test Scenario:* **TS-05**: [Tier 2] Create an opted-in PVC at or above the storage-profile minimum; PVC is not inflated and no inflation labels are set
  - *Priority:* P0

- **[CNV-97015]** — As a cluster administrator, I want a below-minimum PVC-source clone to carry inflation labels with source `datavolume`, so that clone destinations are auditable
  - *Test Scenario:* **TS-06**: [Tier 2] Create a below-minimum PVC-source clone DataVolume; destination succeeds; both inflation labels present with source `datavolume`; original-size label matches the destination request
  - *Priority:* P1

- **[CNV-97015]** — As a cluster administrator, I want a below-minimum snapshot-source clone to carry inflation labels with source `datavolume`, so that snapshot restores are auditable
  - *Test Scenario:* **TS-07**: [Tier 2] Create a below-minimum snapshot-source clone whose restore size is below the destination minimum; destination succeeds; both inflation labels present with source `datavolume`
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Development: Alexander Wels (@awels)
  - sig-storage QE: Jenia Peimer (@jpeimer), Jose Manuel Castano (@josemacassan), kgoldbla (@kgoldbla), Dalia Frank (@dalia-frank), Ahmad Hafe (@Ahmad-Hafe), Kate Shvaika (@kshvaika), Emanuele Prella (@ema-aka-young), Adam Cinko (@acinko-rh), ShellyKas13 (@ShellyKas13)
  - QE Lead: Ruth Netser (@rnetser)
* **Approvers:**
  - QE Lead: Ruth Netser (@rnetser)
  - Dev Lead: Alexander Wels (@awels)
  - Product Manager: Peter Lauterbach (@pelauter)
