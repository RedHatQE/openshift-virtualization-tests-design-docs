# Openshift-virtualization-tests Test plan

## **Track PVCs Inflated to Storage Profile Minimum Supported Size - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** https://github.com/kubevirt/containerized-data-importer/pull/4281
- **Feature Tracking:** https://redhat.atlassian.net/browse/CNV-97015
- **Epic Tracking:** https://redhat.atlassian.net/browse/CNV-99388
- **QE Tracking:** https://redhat.atlassian.net/browse/CNV-100288
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: TBD (target with CDI PR #4281 merge / CNV release containing that build)
- **QE Owner(s):** Ahmad Hafe (ahafe@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage

**Document Conventions (if applicable):**

- **Minimum-supported-size inflation** — CDI enlarges a volume request up to the storage profile's configured minimum when the user asks for less than that minimum
- **Filesystem-overhead inflation** — a separate size adjustment for filesystem overhead; it must not be treated as minimum-supported-size inflation
- **Original requested size record** — durable labels on the resulting PVC that preserve the size the user originally requested and identify what triggered the bump (`datavolume` vs `external`)

### **Feature Overview**

Some storage backends advertise a minimum usable volume size. When a user requests a smaller DataVolume or PVC, CDI silently grows the request to that minimum so provisioning succeeds. Historically the only signal was a short-lived event on the DataVolume, which expires and cannot be aggregated cluster-wide.

This feature adds a durable record on every PVC whose size was raised for that minimum: the originally requested size (in bytes) and whether the bump came from a DataVolume path or a directly created PVC path. Those labels are visible to kube-state-metrics on OpenShift, so administrators can identify inflated volumes and quantify requested-versus-effective capacity. The size-growth behavior itself is unchanged; this work only makes it observable.

**STP scope note:** Dashboard/alert packaging that consumes the labels is tracked separately ([CNV-100289](https://redhat.atlassian.net/browse/CNV-100289)) and is out of scope for this STP. Upstream PR #4281 ships **labels** (not a custom CDI Prometheus metric and not a duplicate human-readable annotation).

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - When CDI raises a volume request to the storage profile minimum, the resulting PVC must retain the originally requested size in a durable, queryable form
    - The record must indicate whether the bump was triggered via a DataVolume or via a directly created (external) PVC path
    - Volumes that were not enlarged for the storage-profile minimum must not receive that record (including volumes only adjusted for filesystem overhead)
    - Existing minimum-size growth behavior and the existing DataVolume event remain available; this feature does not change sizing math

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:*
    - Cluster administrators can find PVCs that are larger than what users asked for because of backend minimums
    - Operators can quantify aggregate over-provisioning caused by minimum-supported-size enforcement and build alerts/dashboards later
  - *List the customer use cases identified:*
    - As a cluster admin, I want a durable mark on PVCs enlarged to a storage minimum so I can audit unexpected capacity use
    - As a cluster admin, I want to distinguish DataVolume-driven bumps from directly created PVC bumps when reviewing inflated capacity
    - As a VM owner, I want provisioning that is smaller than the backend minimum to keep working while still leaving an auditable trail of my original request

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:*
    - Parent acceptance criteria still mention a shipping "annotation" and a dedicated "metric that displays the per pvc original size". Upstream settled on **PVC labels** consumed via kube-state-metrics joins — not a CDI-owned metric series. QE validates the labels on the PVC; PromQL/dashboard validation is deferred to CNV-100289 unless product clarifies otherwise after PR merge.
    - Clone sizing currently skips this minimum-size inflation path per upstream discussion on PR #4281; clone is treated as out of scope / non-applicable unless implementation changes before merge.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - When a DataVolume requests storage below the storage profile minimum, the created PVC is grown to the minimum and carries labels for the original requested size (bytes) and source `datavolume`
    - When a directly created PVC (with storage-profile application enabled) is grown for the same reason, it carries the original-size label and source `external`
    - PVCs not enlarged for the storage-profile minimum do not receive those labels
    - Filesystem-overhead-only size growth does not set those labels
    - Follow-up dashboard work is tracked separately (CNV-100289), not gated by this STP
  - *Note any gaps or missing criteria:*
    - Reconcile Jira wording (annotation/metric) with merged upstream labels once PR #4281 lands; update this STP if the final API differs

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Observability / Monitoring:** Durable PVC labels suitable for kube-state-metrics / PromQL joins; no new CDI-owned metric required in the current PR design
    - **Documentation:** Release note describing the new labels when size is raised to the profile minimum
  - *Note any NFRs not covered and why:*
    - **UI:** Not applicable — no console changes in this feature
    - **Performance:** Not applicable — labeling adds negligible overhead versus existing size rendering
    - **Security / RBAC:** Not applicable — uses existing PVC visibility; no new privileged APIs
    - **Scalability:** Not applicable — per-PVC labels scale with existing PVC count
    - **Dashboard packaging:** Deferred to CNV-100289

#### **2. Known Limitations**

- **Clone workflows do not participate in this minimum-size inflation labeling path** (clone sizing skips this inflation per upstream PR discussion).
  - *Sign-off:* Pending Dev confirmation at QE kickoff after PR #4281 finalization — Ahmad Hafe / TBD

- **Dashboard and alert content that visualizes exact delta / storage class aggregates are follow-up work (CNV-100289), not part of this delivery.**
  - *Sign-off:* Ahmad Hafe / 2026-11-05 (aligned with QE task split CNV-100288 vs CNV-100289)

- **Jira parent text still says annotation + CDI metric; implementation under review uses labels only.**
  - *Sign-off:* Pending product/dev alignment when PR merges — Ahmad Hafe / TBD

#### **3. Technology and Design Review**

- [ ] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Planned after CDI PR #4281 implementation settles (controller + webhook paths, shared rendering helper)
    - Confirm final label keys/values, whether populator PVCs without DataVolume are covered when storage-profile application is enabled, and that clone remains excluded
    - Confirm filesystem-overhead path does not set the new labels (parity with existing event logic)

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Need a storage class / storage profile with a known minimum larger than the test request
    - Two code paths (DataVolume controller rendering vs PVC mutating webhook for external PVCs)
    - Distinguishing minimum-supported-size inflation from filesystem-overhead inflation
  - *Impact on testing approach:*
    - Prefer storage classes that already expose a minimum in the storage profile (or temporarily annotate a profile in a controlled test setup where allowed)
    - Separate positive cases for DataVolume vs external PVC; explicit negative cases for no-bump and filesystem-overhead-only

- [x] **API Extensions**
  - *List new or modified APIs:*
    - No new CRDs — additive PVC labels when inflation occurs
    - Existing storage profile minimum annotation remains the trigger for sizing
  - *Testing impact:*
    - Assert presence/absence and values of the new PVC labels after create/import flows
    - No API version migration testing required

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*
    - Storage class backed by a storage profile that defines a minimum supported PVC size
    - Ability to create DataVolumes and standalone PVCs (including with storage-profile application enabled for the webhook path)

- [x] **Topology Considerations**
  - *Describe topology requirements:* Standard single-cluster topology is sufficient
  - *Impact on test design:* No multi-cluster or special network topology required

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify that a DataVolume requesting less than the storage profile minimum produces a PVC grown to that minimum and labeled with the original requested size and DataVolume source
- **[P0]** Verify that a directly created PVC enlarged via the storage-profile application path is labeled with the original requested size and external source
- **[P0]** Verify that PVCs not enlarged for the storage-profile minimum do not receive the new labels
- **[P0]** Verify that filesystem-overhead-only growth does not set the minimum-supported-size tracking labels
- **[P1]** Verify label values are usable for capacity comparison (original request in bytes matches what the user asked for before the bump)

**Out of Scope (Testing Scope Exclusions)**

- Building or validating the administrator dashboard / alerts that consume the labels ([CNV-100289](https://redhat.atlassian.net/browse/CNV-100289))
  - *Rationale:* Split into a follow-up story; this STP covers durable labeling on inflated PVCs only
  - *PM/Lead Agreement:* Pending — aligned with Jira task split; confirm at kickoff
- Clone-based provisioning labeling for this feature
  - *Rationale:* Upstream states clone sizing skips this minimum-size inflation path
  - *PM/Lead Agreement:* Pending Dev sign-off after PR finalization
- Changing or re-validating the historical DataVolume "minimum size applied" event beyond ensuring it still fires when inflation occurs (optional smoke only if cheap)

**Test Limitations**

- End-to-end PromQL / kube-state-metrics scrape validation may be limited in standard functional jobs; primary assertions are on PVC object labels. Full metrics pipeline checks belong with CNV-100289 or observability coverage if required later.
  - *Sign-off:* Ahmad Hafe / 2026-11-05

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:*
    - DataVolume below minimum → PVC size + labels
    - External PVC with storage-profile application below minimum → PVC size + labels
    - Request already at/above minimum → no tracking labels
    - Filesystem-overhead-only growth → no tracking labels

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:*
    - New automated tests under `tests/storage/` (working name: `test_pvc_size_bump_labels.py`) in openshift-virtualization-tests
    - Reuse existing helper to read storage profile minimum supported size

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:*
    - Minimum-supported-size growth still occurs (PVC effective size is the minimum)
    - Existing CDI create/import flows continue to succeed on profiles with and without a minimum

**Non-Functional**

- [ ] **Performance Testing**
  - *Details:* N/A — labeling does not change provisioning performance characteristics

- [ ] **Scale Testing**
  - *Details:* N/A for this delivery; aggregate capacity views are dashboard follow-up

- [ ] **Security Testing**
  - *Details:* N/A — no new authz surface

- [ ] **Usability Testing**
  - *Details:* N/A — admin observability via labels/metrics consumers

- [x] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* Labels are designed for kube-state-metrics consumption. This STP validates label presence/values on PVCs. Dedicated metric/dashboard acceptance is CNV-100289.

**Integration & Compatibility**

- [x] **Compatibility Testing**
  - *Details:* Run against at least one storage class whose storage profile defines a minimum (cloud or lab provisioner that already carries the minimum annotation). Skip/select via existing storage markers/helpers when a profile has no minimum.

- [x] **Upgrade Testing**
  - *Details:* After upgrade to a build containing the feature, newly inflated PVCs receive labels. Pre-existing inflated PVCs created before the feature are not required to be backfilled (confirm at Dev kickoff; treat as limitation if confirmed).

- [x] **Dependencies**
  - *Details:* Blocked on CDI PR https://github.com/kubevirt/containerized-data-importer/pull/4281 merge (or equivalent downstream build). QE implementation should start when Dev implementation is closed / label contract is stable.

- [x] **Cross Integrations**
  - *Details:* Observability consumers (kube-state-metrics allowlists already include PVC labels on OpenShift). No required testing by other SIGs for this STP.

**Infrastructure**

- [x] **Cloud Testing**
  - *Details:* Prefer environments where storage profiles already publish a minimum (e.g. certain AWS/GCP/HPE/Hitachi profiles cited in the feature). Not every cloud SC is required if one representative minimum-bearing SC is available.

#### **3. Test Environment**

- **Cluster Topology:** standard 3-master/3-worker (or equivalent CNV QE lab)

- **OCP & OpenShift Virtualization Version(s):** Target CNV release that includes CDI with PR #4281

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** At least one storage class with storage profile `minimumSupportedPvcSize` set and larger than the test request size; plus a class/profile without a minimum for negative coverage where practical

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** OpenShift Virtualization (CDI)

- **Platform:** PSI / cloud labs that expose a minimum-bearing storage profile

- **Special Configurations:** Ability to create PVCs with storage-profile application enabled for the external path

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** openshift-virtualization-tests (pytest)

- **CI/CD:** Standard storage tier jobs

- **Other Tools:** `oc`/`kubectl` for PVC inspection; optional Prometheus only if observability follow-up is pulled into scope

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved** (this STP reviewed)
- [ ] CDI implementation of PVC inflation tracking labels is **complete and merged** (or available in a testable downstream build) — https://github.com/kubevirt/containerized-data-importer/pull/4281
- [ ] Final label keys/values and source strings are **confirmed** with Dev (no further rename expected)
- [ ] Test environment can be **set up** with a minimum-bearing storage profile (see Section II.3)

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** PR #4281 is still open and may refactor shared controller/webhook rendering before merge
  - **Mitigation:** Keep STP scenarios behavior-focused; regenerate STD/tests only after Dev closes implementation details. Do not automate against a moving label contract.
  - *Estimated impact on schedule:* Medium — start automation after merge or after Dev freeze on label API
  - *Sign-off:* Ahmad Hafe / 2026-11-05

**Test Coverage**

- **Risk:** Parent Jira still mentions annotation + dedicated metric; tests written against labels may need rename if product reverts
  - **Mitigation:** Trace scenarios to CNV-97015 / CNV-100288; update STP + STD when AC text is reconciled
  - *Areas with reduced coverage:* PromQL/dashboard (explicitly deferred)
  - *Sign-off:* Ahmad Hafe / 2026-11-05

**Test Environment**

- **Risk:** Lab storage classes may lack a usable minimum supported size
  - **Mitigation:** Select cloud/lab SCs known to carry the profile minimum; document environment prerequisite; fail fast with clear precondition messaging in automation
  - *Missing resources or infrastructure:* None if a minimum-bearing SC is available
  - *Sign-off:* Ahmad Hafe / 2026-11-05

**Untestable Aspects**

- **Risk:** Full cluster-wide inflated-capacity dashboards not validated here
  - **Mitigation:** Covered by CNV-100289 follow-up
  - *Alternative validation approach:* PVC label assertions + manual KSM spot-check if needed
  - *Sign-off:* Ahmad Hafe / 2026-11-05

**Resource Constraints**

- **Risk:** N/A
  - **Mitigation:** Scope is a small set of storage functional tests
  - *Current capacity gaps:* None
  - *Sign-off:* Ahmad Hafe / 2026-11-05

**Dependencies**

- **Risk:** Blocked on upstream CDI merge / downstream CDI image
  - **Mitigation:** Track PR #4281; begin STD placeholders now, implement after merge
  - *Dependent teams or components:* CDI / virt storage Dev
  - *Sign-off:* Ahmad Hafe / 2026-11-05

**Other**

- **Risk:** Planned clone test may be invalid if clone never inflates via this path
  - **Mitigation:** Do not automate clone labeling unless Dev confirms the path applies; keep clone out of scope (see limitations)
  - *Sign-off:* Ahmad Hafe / 2026-11-05

---

### **III. Test Scenarios & Traceability**

- **[CNV-97015]** — As a cluster admin, I want PVCs created from undersized DataVolumes to record the originally requested size when grown to the storage minimum
  - *Test Scenario:* [Tier 2] Create a DataVolume requesting less than the storage profile minimum; verify the PVC capacity is the minimum and the PVC carries original-size and DataVolume-source tracking labels whose original-size value matches the request
  - *Priority:* P0
  - *Planned automation:* `test_pvc_labels_when_size_bumped_via_datavolume`

- **[CNV-97015]** — As a cluster admin, I want directly created PVCs that are grown for the storage minimum to record the original request with an external source
  - *Test Scenario:* [Tier 2] Create a PVC below the storage profile minimum with storage-profile application enabled; verify growth and original-size + external-source tracking labels
  - *Priority:* P0
  - *Planned automation:* `test_pvc_labels_with_external_pvc`

- **[CNV-97015]** — As a cluster admin, I want PVCs that were not grown for the storage minimum to remain unmarked by this feature
  - *Test Scenario:* [Tier 2] [NEGATIVE] Create a DataVolume/PVC at or above the storage profile minimum (or on a profile without a minimum); verify the minimum-supported-size tracking labels are absent
  - *Priority:* P0

- **[CNV-97015]** — As a cluster admin, I want filesystem-overhead size adjustments not to be mistaken for minimum-supported-size inflation
  - *Test Scenario:* [Tier 2] [NEGATIVE] Trigger filesystem-overhead-only size growth without minimum-supported-size inflation; verify the minimum-supported-size tracking labels are absent
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect: Ruth Netser (@rnetser)
  - QE Members (OCP-V storage): (add storage QE peers on PR)
  - Developer: Ady Cohen (@AdyCohen1) / storage reviewers on CDI PR #4281
* **Approvers:**
  - QE Architect: Ruth Netser (@rnetser)
  - QE Lead (storage): (confirm on PR)
