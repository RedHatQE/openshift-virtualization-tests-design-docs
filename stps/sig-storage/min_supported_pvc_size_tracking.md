# Openshift-virtualization-tests Test plan

## **Track PVCs Inflated to Storage Profile Minimum Supported Size - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [CDI PR #4281](https://github.com/kubevirt/containerized-data-importer/pull/4281)
- **Feature Tracking:** [CNV-97015](https://redhat.atlassian.net/browse/CNV-97015)
- **Epic Tracking:** [CNV-99388](https://redhat.atlassian.net/browse/CNV-99388)
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: CNV v5.1.0
- **QE Owner(s):** Ahmad Hafe (@Ahmad-Hafe, ahafe@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage

**Document Conventions:**

- **Size inflation:** CDI raises an undersized request to the storage-profile minimum supported size after filesystem overhead. This STP still verifies that behavior and the existing `MinimumPVCSizeApplied` DataVolume event; it does not treat labels as present only when inflation happens.
- **Size-tracking labels:** Two PVC labels set by CDI on covered create paths:
  - `cdi.kubevirt.io/originalRequestedSizeBytes` — the user's originally requested storage size in raw bytes (before filesystem overhead and the minimum supported size). Present on every DataVolume-created PVC and on webhook-rendered opted-in direct PVCs.
  - `cdi.kubevirt.io/fsOverheadBytes` — filesystem overhead added to the request, in bytes (`0` for Block). Set **only** when CDI's overhead and minimum sizing produced the final PVC size. Absent when the PVC was sized another way (legacy `spec.pvc`, clone sized from its source, or a webhook PVC restoring from a VolumeSnapshot). Dashboards that see both labels derive the pre-minimum size as `originalRequestedSizeBytes + fsOverheadBytes`, and the minimum-bump delta as `final - (originalRequestedSizeBytes + fsOverheadBytes)`.
- **Direct PVC opt-in:** Any PVC labeled `cdi.kubevirt.io/applyStorageProfile: "true"` so CDI applies storage-profile rendering (including the minimum supported size) to PVCs created without a DataVolume. See [CDI PVC mutating webhook usage](https://github.com/kubevirt/containerized-data-importer/blob/main/doc/pvc-mutating-webhook-rendering.md#usage).
- **MinimumPVCSizeApplied event:** Existing DataVolume event CDI emits when size inflation occurs (visible on the DataVolume; short-lived).
- **Label ownership:** Size-tracking labels are CDI-owned. They are never copied from the DataVolume or from an existing PVC. Temporary clone PVCs may keep the labels (filterable by name).

### **Feature Overview**

Some storage providers enforce a minimum volume size. Those known by CDI have this information in the storage profile. CDI already inflates undersized requests to that minimum so create and clone can succeed. The only durable signal today for the original request is missing: the short-lived `MinimumPVCSizeApplied` DataVolume event expires and does not cover PVCs created without a DataVolume.

This feature does not change sizing rules. CDI stamps every covered PVC with the original requested size and, when CDI sizing produced the final size, the filesystem overhead in bytes. Namespace administrators can identify volumes whose effective capacity differs from the request and compare requested versus effective capacity across the namespace. Dashboards can separate filesystem-overhead growth from minimum-supported-size inflation using the two labels. Alerts and dashboards themselves are not covered here; observability can extend that later. This STP covers GA in CNV 5.1.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - [CNV-97015](https://redhat.atlassian.net/browse/CNV-97015) — Covered PVCs must record the original requested size in bytes on every DataVolume-created and opted-in direct PVC path
    - [CNV-97015](https://redhat.atlassian.net/browse/CNV-97015) — When CDI sizing produced the final size, the PVC must also record filesystem overhead in bytes (`0` for Block)
    - [CNV-97015](https://redhat.atlassian.net/browse/CNV-97015) — Size-tracking labels must not be copied from the DataVolume or from an existing PVC
    - [CNV-97015](https://redhat.atlassian.net/browse/CNV-97015) — Existing size-inflation behavior and the `MinimumPVCSizeApplied` DataVolume event remain unchanged
    - [CNV-97015](https://redhat.atlassian.net/browse/CNV-97015) — Direct PVCs without `cdi.kubevirt.io/applyStorageProfile: "true"` keep the original request and do not receive size-tracking labels

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Namespace administrators can track requested versus effective PVC size without relying on expired events, and dashboards can separate filesystem overhead from minimum-size inflation.
  - *List the customer use cases identified:*
    - As a namespace administrator, I want every covered PVC to keep a durable record of the original request and filesystem overhead, so that I can audit size changes across the namespace.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None for the label contract. Jira may still mention annotation/metric wording; this STP asserts PVC size-tracking labels. Metrics/alerts/dashboards remain Out of Scope.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - Below-minimum DataVolume (request still below the minimum supported size after filesystem overhead, or block mode) succeeds; PVC equals the storage-profile minimum supported size; both size-tracking labels present; `originalRequestedSizeBytes` equals the DataVolume request in bytes; `fsOverheadBytes` matches mode (non-zero for filesystem with overhead, `0` for Block); a `MinimumPVCSizeApplied` event appears on the DataVolume
    - Below-minimum opted-in direct PVC (labeled `cdi.kubevirt.io/applyStorageProfile: "true"`) becomes Bound; PVC equals the storage-profile minimum supported size; both size-tracking labels present with `originalRequestedSizeBytes` equal to the submitted request
    - Filesystem-overhead-only growth (final size not raised to the minimum) still sets both size-tracking labels; `originalRequestedSizeBytes` matches the request; `fsOverheadBytes` reflects the overhead; PVC size equals request plus overhead
    - Direct PVC below minimum without opt-in keeps the original request and sets no size-tracking labels
    - Opted-in PVC at or above the minimum supported size is not raised further; both size-tracking labels are still present
    - PVC-source clone DataVolume succeeds; `originalRequestedSizeBytes` matches the destination request; `fsOverheadBytes` is absent when the clone was sized from its source (not by CDI's overhead+minimum pipeline)
    - Opted-in direct PVC restoring from a VolumeSnapshot (below the storage-profile minimum) succeeds; `originalRequestedSizeBytes` matches the restore request; `fsOverheadBytes` is absent; the PVC is **not** raised to the storage-profile minimum (webhook `RenderPvc` skips minimum inflation for VolumeSnapshot restores)
  - *Note any gaps or missing criteria:* None. Metrics/alerts, docs, UI, performance, and scale are Out of Scope.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Observability:** Size-tracking labels are the durable record; Tier 2 asserts presence, absence, and values on the PVC
  - *Note any NFRs not covered and why:*
    - **Monitoring:** Metrics and alerts are Out of Scope (observability team owns metrics/alert testing; may extend later)
    - **Documentation:** Out of Scope for this Tier 2 plan
    - **UI:** No console workflow; customer value is API/label audit — PM/UX not requesting console coverage (Out of Scope)
    - **Performance:** No new performance targets (Out of Scope)
    - **Security:** No new RBAC or security surface
    - **Scalability:** No new cluster-level scale requirements; create/clone still use existing PVC paths (Out of Scope for dedicated scale scenarios)

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- **No backfill on upgrade** — Labels apply only to newly created covered PVCs.
  - *Sign-off:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-11

- **Non-DV clone populator PVCs skip minimum inflation** — Clone PVCs created without a DataVolume do not receive storage-profile minimum supported size inflation unless the PVC carries `cdi.kubevirt.io/applyStorageProfile: "true"`. DataVolume controller clones remain in scope for the original-size label.
  - *Sign-off:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-11

- **Webhook VolumeSnapshot restores skip minimum inflation and `fsOverheadBytes`** — For a direct PVC with `applyStorageProfile` whose data source is a VolumeSnapshot, CDI does not raise the request to the storage-profile minimum and does not set `fsOverheadBytes`. `originalRequestedSizeBytes` is still set. (A DataVolume with `Source.Snapshot` can still be sized by the DV controller; that path is not TS-07.)
  - *Sign-off:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-23

- **Clone sized from source may omit `fsOverheadBytes`** — When clone size comes from the source (not CDI's overhead+minimum pipeline), only `originalRequestedSizeBytes` is required; absence of `fsOverheadBytes` is expected.
  - *Sign-off:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-23

- **Later PVC expansion is not a minimum bump** — If a labeled PVC is expanded later, `final - (original + fsOverhead)` grows even though that growth is not a storage-profile minimum bump. Dashboards must account for this; this STP does not assert expansion behavior.
  - *Sign-off:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-23

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:* Reviewed with CDI development. Per the later [CDI PR #4281](https://github.com/kubevirt/containerized-data-importer/pull/4281) direction, CDI always stamps `originalRequestedSizeBytes` on covered PVCs and records `fsOverheadBytes` when CDI sizing produced the final size. There is no bump-source label. Unit tests are preferred for controller honesty when they keep an honest environment; e2e adds little unless multiple components are involved. This STP covers Tier 2 create/clone paths in openshift-virtualization-tests and does not equate that coverage with unit tests or claim CDI Tier 1 is unit-test coverage. No untestable in-scope aspects.

- [x] **Technology Challenges**
  - *List identified challenges:* Need a StorageClass whose StorageProfile has a usable minimum supported PVC size (tests may set that minimum on the StorageProfile); TS-07 needs VolumeSnapshot support, `applyStorageProfile` on the restore PVC, and a restore request below that minimum so the skipped minimum bump is visible.
  - *Impact on testing approach:* Configure or select a StorageClass and set the StorageProfile minimum supported size in the test as needed; gate TS-07 when VolumeSnapshot support is missing.

- [x] **API Extensions**
  - *List new or modified APIs:* No new APIs. Two additive PVC labels (see Document Conventions). Existing `MinimumPVCSizeApplied` DataVolume event unchanged.
  - *Testing impact:* Assert label presence/absence and values; derive minimum-bump delta as `final - (originalRequestedSizeBytes + fsOverheadBytes)` when needed.

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* No special cluster or network topology. Any standard OpenShift Virtualization cluster is sufficient when a StorageClass provides a usable storage-profile minimum supported size (VolumeSnapshot support only for the snapshot-clone scenario).
  - *Impact on test design:* None.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify a below-minimum DataVolume (request still below the minimum supported size after filesystem overhead, or block mode) finishes inflated with both size-tracking labels, `originalRequestedSizeBytes` matching the request in bytes, correct `fsOverheadBytes`, and a `MinimumPVCSizeApplied` event on the DataVolume
- **[P0]** Verify a below-minimum opted-in direct PVC (applyStorageProfile) finishes Bound inflated with both size-tracking labels
- **[P0]** Verify filesystem-overhead-only growth still sets both size-tracking labels with correct original and overhead values, without raising to the minimum
- **[P0]** Verify a below-minimum direct PVC without opt-in keeps the original request and sets no size-tracking labels
- **[P0]** Verify an opted-in PVC at or above the storage-profile minimum supported size is not raised further and still receives both size-tracking labels
- **[P1]** Verify a PVC-source clone finishes with `originalRequestedSizeBytes` matching the destination request and without `fsOverheadBytes` when sized from its source
- **[P1]** Verify an opted-in direct PVC restoring from a VolumeSnapshot keeps `originalRequestedSizeBytes`, has no `fsOverheadBytes`, and is not raised to the storage-profile minimum

**Existing Coverage (not duplicated here)**

- **CDI lower-level honesty coverage** — Owned by CDI development (unit-test honesty preferred per Developer Handoff). This STP covers Tier 2 create/clone paths in openshift-virtualization-tests and does not re-test that layer or claim CDI Tier 1 equals unit tests.
- **Direct PVC opt-in contract** — Proven by the opted-in, missing-opt-in, and at/above-minimum scenarios in Section III; dedicated DataImportCron / image-upload / backend-storage product paths are not duplicated.

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- **Metrics, alerts, and PromQL / dashboard validation**
  - *Rationale:* This STP covers PVC size-tracking labels only; observability team owns metrics/alert testing and may extend alerts/dashboards later
  - *PM/Lead Agreement:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-11

- **Documentation / release-note validation**
  - *Rationale:* Outside this Tier 2 automation plan
  - *PM/Lead Agreement:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-11

- **UI testing**
  - *Rationale:* No console workflow in this delivery; customer value is API/label audit
  - *PM/Lead Agreement:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-11

- **Full cloud provisioner matrix**
  - *Rationale:* Behavior depends on a StorageProfile minimum supported size, not on a specific cloud provider; one StorageClass with a usable minimum proves the label contract
  - *PM/Lead Agreement:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-11

- **Performance benchmarking**
  - *Rationale:* No performance targets for size-tracking labels
  - *PM/Lead Agreement:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-11

- **Dedicated scale / load scenarios**
  - *Rationale:* No new cluster-level scale requirements; create/clone use existing PVC paths
  - *PM/Lead Agreement:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-11

**Test Limitations**

- **CNV build with size labels required** — CDI #4281 is merged upstream; Tier 2 execution still cannot start until those labels are in the CNV build under test
  - *Sign-off:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-23

- **TS-07 needs VolumeSnapshot support** — Gate the opted-in VolumeSnapshot restore scenario when the cluster has no VolumeSnapshot-capable storage
  - *Sign-off:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-11

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Scenarios cover below-minimum DataVolume create (both labels, `MinimumPVCSizeApplied` event), opted-in direct PVC inflate, filesystem-overhead-only (both labels), missing opt-in (no labels), at/above-minimum (both labels, no further raise), PVC-source clone (original label; no `fsOverheadBytes` when sized from source), and opted-in VolumeSnapshot restore PVC (original label; no `fsOverheadBytes`; no minimum inflation).

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All Section III scenarios automated in openshift-virtualization-tests; run in existing sig-storage CI lanes.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Existing sig-storage DataVolume create/clone and related CDI sizing suites in openshift-virtualization-tests keep running on the feature cluster. Regression coverage is not listed in Section III.

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* N/A — Tier 2 label-contract checks need a StorageClass with a usable storage-profile minimum supported size; not proposed for the self-validation package.

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
  - *Details:* N/A — no new metrics or alerts in this STP; scenarios assert PVC size-tracking labels only (Out of Scope for observability).

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Validate on a StorageClass whose StorageProfile has a usable minimum supported PVC size (tests may set that minimum); TS-07 requires VolumeSnapshot support. Behavior is not cloud-provider-specific.

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* N/A — no backfill on upgrade (Known Limitation); upgrade path evaluated and excluded.

- [x] **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* [CDI PR #4281](https://github.com/kubevirt/containerized-data-importer/pull/4281) is merged. Tier 2 still waits on a CNV build that includes that CDI change.

- [ ] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* No. sig-storage owns Tier 2 label coverage. Metrics/alerts remain Out of Scope for the observability team.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* N/A — not required for this feature; not cloud-provider-specific. Automation runs against any StorageClass whose StorageProfile has a usable minimum PVC size.

#### **3. Test Environment**

- **Cluster Topology:** Single-node or multi-node; no multi-node requirement

- **OCP & OpenShift Virtualization Version(s):** OpenShift (OCP) 4.22 and later / OpenShift Virtualization (CNV) 5.1 with a CDI build that includes size-tracking labels

- **CPU Virtualization:** Standard

- **Compute Resources:** Standard

- **Special Hardware:** N/A

- **Storage:** `ocs-storagecluster-ceph-rbd-virtualization` (or equivalent) whose StorageProfile has a usable minimum supported PVC size above the test request (tests may set that minimum on the StorageProfile); TS-07 needs a VolumeSnapshot-capable StorageClass / VolumeSnapshotClass and a restore request below that minimum on an opted-in direct PVC

- **Network:** Standard (OVN-Kubernetes)

- **Required Operators:** OpenShift Virtualization / CDI

- **Platform:** Bare metal or PSI (virtualized); record the platform used with results. Not tied to AWS/Azure/GCP as automation targets.

- **Special Configurations:** Distinguish minimum supported size inflation from filesystem-overhead-only growth using the two size-tracking labels; direct PVC opt-in (`cdi.kubevirt.io/applyStorageProfile: "true"`) required for non-DataVolume rendering; WaitForFirstConsumer where required

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** N/A — standard suite tooling

- **CI/CD:** N/A — existing sig-storage lanes

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged** ([CDI PR #4281](https://github.com/kubevirt/containerized-data-importer/pull/4281) merged 2026-11-23; feature tracking [CNV-97015](https://redhat.atlassian.net/browse/CNV-97015))
- [ ] A CNV / OpenShift Virtualization build that includes the merged CDI size labels (`originalRequestedSizeBytes`, `fsOverheadBytes`) is **available** for the test cluster
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] StorageClass with a usable storage-profile minimum supported size is available (VolumeSnapshot-capable for TS-07); tests may set the minimum on the StorageProfile
- [ ] Test cases reviewed and approved

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Testing is blocked until the merged CDI size labels land in a CNV test build; late image promotion compresses Tier 2 automation before release readiness
  - **Mitigation:** Gate entry criteria on a CNV build that includes CDI #4281; implement tests against development builds when available
  - *Estimated impact on schedule:* P0 execution blocked until CNV image promotion; later delivery compresses automation before GA
  - *Sign-off:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-23

**Test Coverage**

- **Mitigation:** No risk identified — P0 create inflate and label-presence paths plus P1 clone paths cover the label contract for openshift-virtualization-tests Tier 2 scope.

**Test Environment**

- **Risk:** CI may lack a StorageClass whose StorageProfile has a usable minimum supported size, or VolumeSnapshot support for the snapshot-clone scenario
  - **Mitigation:** Use `ocs-storagecluster-ceph-rbd-virtualization` (or equivalent) and set the StorageProfile minimum supported size in the test when needed; gate the snapshot scenario when VolumeSnapshot support is missing
  - *Missing resources or infrastructure:* Environment-dependent StorageClass / VolumeSnapshot capability
  - *Sign-off:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-11

**Untestable Aspects**

- **Mitigation:** No risk identified — in-scope P0 paths are testable through create/clone APIs; snapshot-clone is gated as a Test Limitation when VolumeSnapshot support is absent.

**Resource Constraints**

- **Mitigation:** No risk identified — no additional QE headcount or dedicated hardware beyond the standard sig-storage lanes is required for this STP.

**Dependencies**

- **Risk:** Feature still depends on image promotion of merged [CDI PR #4281](https://github.com/kubevirt/containerized-data-importer/pull/4281) into the CNV build under test
  - **Mitigation:** Keep entry criteria gated on that CNV build; do not start Tier 2 automation against a build without the size labels
  - *Dependent teams or components:* OpenShift Virtualization / CDI image promotion
  - *Sign-off:* Arnon Gilboa (@arnongilboa), Ady Cohen (@AdyCohen1)/2026-11-23

---

### **III. Test Scenarios & Traceability**

#### **1. Requirements-to-Tests Mapping**

- **[CNV-97015]** — As a namespace administrator, I want a below-minimum DataVolume to finish inflated with both size-tracking labels, so that I can audit silently inflated volumes
  - *Test Scenario:* **TS-01**: [Tier 2] Create a below-minimum DataVolume whose request remains below the minimum supported size after filesystem overhead (or use block mode); PVC request equals the storage-profile minimum supported size; both size-tracking labels are present; `originalRequestedSizeBytes` equals the submitted DataVolume storage request expressed in bytes; `fsOverheadBytes` matches mode; a `MinimumPVCSizeApplied` event appears on the DataVolume
  - *Priority:* P0

- **[CNV-97015]** — As a namespace administrator, I want a below-minimum opted-in direct PVC to finish Bound inflated with both size-tracking labels, so that non-DataVolume inflation is auditable
  - *Test Scenario:* **TS-02**: [Tier 2] Create a below-minimum direct PVC labeled `cdi.kubevirt.io/applyStorageProfile: "true"`; PVC becomes Bound at the minimum supported size; both size-tracking labels are present; `originalRequestedSizeBytes` equals the submitted request
  - *Priority:* P0

- **[CNV-97015]** — As a namespace administrator, I want filesystem-overhead-only growth to still record original request and overhead, so that overhead is distinguishable from minimum-size inflation
  - *Test Scenario:* **TS-03**: [Tier 2] Create a filesystem PVC whose size grows only by filesystem overhead (final size not raised to the minimum); both size-tracking labels are set; `originalRequestedSizeBytes` matches the request; `fsOverheadBytes` reflects the overhead; PVC size equals request plus overhead
  - *Priority:* P0

- **[CNV-97015]** — As a namespace administrator, I want a below-minimum direct PVC without opt-in to keep its original request unlabeled, so that non-opted-in volumes are not reported as CDI-sized
  - *Test Scenario:* **TS-04**: [Tier 2] Create a below-minimum direct PVC without `cdi.kubevirt.io/applyStorageProfile: "true"`; original request is retained and no size-tracking labels are set
  - *Priority:* P0

- **[CNV-97015]** — As a namespace administrator, I want an opted-in PVC at or above the minimum to keep size-tracking labels without further raise, so that non-inflated volumes remain auditable
  - *Test Scenario:* **TS-05**: [Tier 2] Create an opted-in PVC (`cdi.kubevirt.io/applyStorageProfile: "true"`) at or above the storage-profile minimum supported size; PVC is not raised further; both size-tracking labels are present
  - *Priority:* P0

- **[CNV-97015]** — As a namespace administrator, I want a PVC-source clone to record the destination request without a false overhead label, so that clones sized from source stay auditable
  - *Test Scenario:* **TS-06**: [Tier 2] Create a PVC-source clone DataVolume; destination succeeds; `originalRequestedSizeBytes` matches the destination request; `fsOverheadBytes` is absent when the clone was sized from its source
  - *Priority:* P1

- **[CNV-97015]** — As a namespace administrator, I want an opted-in VolumeSnapshot restore PVC to record the restore request without minimum inflation or an overhead label, so that snapshot restores are not misreported as CDI-sized bumps
  - *Test Scenario:* **TS-07**: [Tier 2] Create a direct PVC labeled `cdi.kubevirt.io/applyStorageProfile: "true"` that restores from a VolumeSnapshot with a request below the storage-profile minimum supported size; PVC succeeds; `originalRequestedSizeBytes` matches the restore request; `fsOverheadBytes` is absent; the PVC is not raised to the minimum supported size
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE: Jenia Peimer (@jpeimer), Jose Manuel Castano (@josemacassan), Dalia Frank (@dalia-frank), Ahmad Hafe (@Ahmad-Hafe), Kate Shvaika (@kshvaika), Emanuele Prella (@ema-aka-young), Adam Cinko (@acinko-rh)
  - QE Lead: Ruth Netser (@rnetser)
* **Approvers:**
  - QE Lead: Ruth Netser (@rnetser)
  - Dev Lead: Alexander Wels (@awels)
  - Product Manager: Peter Lauterbach (@pelauter)
