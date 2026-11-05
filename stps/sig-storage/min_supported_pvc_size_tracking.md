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
  - GA: 5.1
- **QE Owner(s):** Ahmad Hafe (ahafe@redhat.com)
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-storage

**Document Conventions (if applicable):** N/A

### **Feature Overview**

Some storage backends enforce a minimum volume size. When a user requests less than that minimum, CDI grows the request so provisioning can succeed. Until now the only signal was a short-lived DataVolume event, which expires and cannot be aggregated across the cluster.

This feature records the originally requested size on every PVC that was enlarged for that minimum, and whether the bump came from a DataVolume or a directly created PVC. Those labels are visible to OpenShift monitoring, so administrators can find inflated volumes and compare requested versus effective capacity. Sizing behavior itself is unchanged; this work only makes the bump observable. Packaged dashboards and alerts are tracked separately under CNV-100289.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - When CDI grows a volume to the storage profile minimum, the PVC must retain the originally requested size in a durable form
    - The record must show whether the bump came from a DataVolume or a directly created PVC
    - Volumes not grown for the storage-profile minimum must not get that record (including filesystem-overhead-only growth)
    - Existing minimum-size growth and the DataVolume event continue to work

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:*
    - Administrators can audit silent over-provisioning caused by storage minimums without relying on ephemeral events
  - *List the customer use cases identified:*
    - As a cluster admin, I want a durable mark on PVCs enlarged to a storage minimum so I can audit capacity use
    - As a cluster admin, I want to distinguish DataVolume-driven bumps from directly created PVC bumps
    - As a storage operator, I want filesystem-overhead-only growth excluded so audits do not false-positive

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:*
    - Jira story text still says annotation and metric; CDI PR #4281 ships PVC labels for kube-state-metrics. Tests target those labels. Dashboard packaging is CNV-100289 (out of scope here).

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - DataVolume below the storage profile minimum → PVC grown to minimum with original requested size record (DataVolume source) matching the original request
    - Directly created PVC below the minimum (storage-profile application path) → same record with external source
    - Filesystem-overhead-only growth → no original requested size record
    - Request already at or above the minimum → no original requested size record
  - *Note any gaps or missing criteria:* Dashboard follow-up is CNV-100289, not this STP

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - **Monitoring / Observability:** Original requested size and bump source must be queryable via the OpenShift monitoring stack
    - **Documentation:** Release note / docs should describe how to identify inflated PVCs
  - *Note any NFRs not covered and why:*
    - **UI:** No console changes; UI testing not required for this delivery
    - **Performance:** No new performance targets
    - **Security:** No new RBAC or auth surface
    - **Scalability:** No new scale requirements beyond existing PVC / monitoring cardinality

#### **2. Known Limitations**

- **Observability uses PVC labels (not a dedicated CDI metric or duplicate annotation), per CDI PR #4281**
  - *Sign-off:* Ahmad Hafe / 2026-11-05

- **No packaged dashboard or alert rules in this delivery (CNV-100289)**
  - *Sign-off:* Ahmad Hafe / 2026-11-05

- **Clone sizing does not use this minimum-supported-size inflation path (per upstream PR discussion); clone labeling is out of scope unless Dev changes that before merge**
  - *Sign-off:* Ahmad Hafe / 2026-11-05 — confirm with Dev at kickoff

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Reviewed CDI PR #4281 against CNV-97015: bump behavior unchanged; durable labels added when minimum-supported-size inflation occurs
    - Cover DataVolume controller path and external PVC (storage-profile application) path
    - Filesystem-overhead-only adjustments must not set the labels
    - Confirm fixture approach for storage-profile minimum before automation lands

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Need a storage profile with a known minimum larger than the test request
    - Separate minimum-size inflation from filesystem-overhead inflation in fixtures
  - *Impact on testing approach:*
    - Positive cases for DataVolume and external PVC; negative cases for no-bump and filesystem-overhead-only

- [x] **API Extensions**
  - *List new or modified APIs:*
    - No new CRDs; additive PVC labels when minimum-supported-size inflation occurs
  - *Testing impact:*
    - Assert label presence/absence and values after create flows; optional monitoring check for P1

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Standard single-cluster topology is sufficient
  - *Impact on test design:* No special topology required

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify a DataVolume below the storage profile minimum grows the PVC to that minimum and records the original requested size with DataVolume source
- **[P0]** Verify a directly created PVC enlarged for the minimum records the original requested size with external source
- **[P0]** Verify filesystem-overhead-only growth does not add the original requested size record
- **[P0]** Verify requests at or above the minimum do not receive the original requested size record
- **[P1]** Verify original versus effective size is visible through cluster monitoring after a successful minimum-size inflation

**Out of Scope (Testing Scope Exclusions)**

- **Packaged dashboards and alert rules**
  - *Rationale:* Follow-up story CNV-100289; this STP validates the durable PVC record and basic monitoring visibility
  - *PM/Lead Agreement:* Pending — confirm name/date on review

- **Mandatory cloud provisioner matrix (AWS io2, GCP sp-balanced, HPE XP, Hitachi HSPC)**
  - *Rationale:* Behavior is driven by storage-profile minimum; exercised with controlled profiles in standard storage CI
  - *PM/Lead Agreement:* Pending — confirm name/date on review

- **Clone-based labeling for this feature**
  - *Rationale:* Upstream states clone sizing skips this minimum-size inflation path
  - *PM/Lead Agreement:* Pending Dev confirmation at kickoff

**Test Limitations**

- **CDI PR #4281 is still open; cluster execution needs a build that includes the labels**
  - *Sign-off:* Ahmad Hafe / 2026-11-05

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing**
  - *Details:*
    - DataVolume below minimum → size + labels
    - External PVC below minimum → size + labels
    - Filesystem-overhead-only and at/above minimum → labels absent

- [x] **Automation Testing**
  - *Details:*
    - New automated tests under `tests/storage/` (working name: `test_pvc_size_bump_labels.py`) after CDI lands
    - Tracked by QE task CNV-100288

- [x] **Regression Testing**
  - *Details:*
    - Existing sig-storage CDI / DataVolume suites continue on feature clusters
    - Confirm the existing DataVolume size-bump event still appears when inflation occurs
    - Regression suites are not listed in Section III

- [ ] **Self-Validation Testing**
  - *Details:* Not initially — needs storage-profile fixtures; revisit after automation stabilizes

**Non-Functional**

- [ ] **Performance Testing**
  - *Details:* N/A — labeling does not change provisioning performance targets

- [ ] **Scale Testing**
  - *Details:* N/A — no new scale requirements in this delivery

- [ ] **Security Testing**
  - *Details:* N/A — no new RBAC or auth surface

- [ ] **Usability Testing**
  - *Details:* N/A — no UI work

- [x] **Monitoring**
  - *Details:*
    - P1: original requested size queryable next to effective storage request
    - Alerts/dashboards: CNV-100289 (out of scope)

**Integration & Compatibility**

- [x] **Compatibility Testing**
  - *Details:* Validate with storage classes / profiles that define a minimum; DataVolume and external PVC paths

- [ ] **Upgrade Testing**
  - *Details:* Labels apply at create/render time for new inflated PVCs after upgrade. No backfill of older PVCs expected.

- [x] **Dependencies**
  - *Details:* Blocked on CDI PR #4281 merge / downstream image with the label implementation

- [ ] **Cross Integrations**
  - *Details:* N/A — observability for storage provisioning; no other SIG ownership this cycle

**Infrastructure**

- [ ] **Cloud Testing**
  - *Details:* No dedicated multi-cloud scenarios (see Out of Scope)

#### **3. Test Environment**

- **Cluster Topology:** standard 3-master/3-worker (or equivalent CNV storage CI)

- **OCP & OpenShift Virtualization Version(s):** OCP / CNV build that includes CDI with PR #4281 (target CNV 5.1)

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** Storage class with a storage profile minimum larger than the test request (e.g. ocs-storagecluster-ceph-rbd-virtualization plus profile configuration as needed)

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** OpenShift Virtualization (CDI); cluster monitoring for the P1 scenario

- **Platform:** PSI / bare metal / supported cloud CI used by sig-storage

- **Special Configurations:** Ability to create PVCs with storage-profile application enabled for the external path

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** Standard

- **Other Tools:** N/A (cluster monitoring for P1 only)

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **reviewed** (CNV-97015 + CDI PR #4281)
- [ ] CDI implementation with inflation tracking labels is **available in a testable build**
- [ ] Test environment can be **set up** with a minimum-bearing storage profile (see Section II.3)
- [ ] Label keys/values confirmed stable with Dev (no further rename expected)

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** CDI PR #4281 is still open; automation cannot pass against a real cluster until a consumable build exists
  - **Mitigation:** Keep STP and stubs aligned to the PR contract; implement automation after merge
  - *Estimated impact on schedule:* Slip if PR misses the CNV 5.1 window
  - *Sign-off:* Ahmad Hafe / 2026-11-05

**Test Coverage**

- **Risk:** Vendor-specific storage-profile quirks not covered by the full cloud matrix
  - **Mitigation:** Controlled storage-profile fixtures; follow up if field bugs implicate a provisioner
  - *Areas with reduced coverage:* Exhaustive AWS/GCP/HPE/Hitachi environments
  - *Sign-off:* Ahmad Hafe / 2026-11-05

**Test Environment**

- **Risk:** Lab/CI may lack a ready-made storage profile with a usable minimum
  - **Mitigation:** Configure or select a profile with a known minimum in test setup
  - *Missing or unavailable environments:* None if profile configuration is allowed
  - *Sign-off:* Ahmad Hafe / 2026-11-05

**Untestable Aspects**

- **Risk:** Packaged dashboard correctness cannot be validated here
  - **Mitigation:** Track under CNV-100289; validate PVC labels (and P1 monitoring) here
  - *Reason untestable and mitigation approach:* Dashboard is a separate deliverable
  - *Sign-off:* Ahmad Hafe / 2026-11-05

**Resource Constraints**

- **Risk:** None beyond normal sig-storage capacity for this slice
  - **Mitigation:** Single QE owner with standard SIG review
  - *Missing resources or infrastructure:* None
  - *Sign-off:* Ahmad Hafe / 2026-11-05

**Dependencies**

- **Risk:** Blocked on CDI merge / image promotion
  - **Mitigation:** Coordinate with CDI Dev (story owner Ady Cohen)
  - *Third-party services or blockers:* kubevirt/containerized-data-importer#4281
  - *Sign-off:* Ahmad Hafe / 2026-11-05

---

### **III. Test Scenarios & Traceability**

- **[CNV-97015]** — As a cluster admin, I want a durable record of the original volume request when a DataVolume is raised to the storage profile minimum
  - *Test Scenario:* [Tier 1] Create a DataVolume below the profile minimum; verify the PVC capacity equals the minimum and the original requested size record is present with DataVolume source and matches the original request
  - *Priority:* P0

- **[CNV-97015]** — As a cluster admin, I want directly created PVCs raised to the minimum to record the original request with an external source
  - *Test Scenario:* [Tier 1] Create a PVC below the profile minimum on the direct path; verify the original requested size record is present with external source and matches the original request
  - *Priority:* P0

- **[CNV-97015]** — As a storage operator, I want filesystem-overhead-only growth excluded from the inflation record
  - *Test Scenario:* [Tier 1] Provision a volume that grows only for filesystem overhead; verify the original requested size record is absent
  - *Priority:* P0

- **[CNV-97015]** — As a cluster admin, I want volumes that already meet the minimum to remain unmarked by this feature
  - *Test Scenario:* [Tier 1] Request a size at or above the profile minimum; verify the PVC is not grown for minimum size and the original requested size record is absent
  - *Priority:* P0

- **[CNV-97015]** — As a cluster admin, I want to compare original versus effective size through cluster monitoring
  - *Test Scenario:* [Tier 2] After a successful minimum-size inflation, verify monitoring shows the original requested size alongside the effective PVC storage request (effective greater than original)
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE: Ahmad Hafe (@Ahmad-Hafe)
  - QE: Kate Shvaika (@kshvaika)
  - Development: CDI reviewers on PR #4281 (e.g. @akalenyu, @awels)
  - SIG Storage: Jenia Peimer (@jpeimer)
* **Approvers:**
  - QE Lead: Jenia Peimer (@jpeimer)
  - Dev Lead: Adam Litke (@aglitke)
  - Product Manager: (confirm on review)
