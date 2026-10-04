# Openshift-virtualization-tests Test plan

## **Annotation-Based GuestAgentPing Probe Pausing (VEP 207) - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP 207 -- Manual GuestAgentPing probe control](https://github.com/kubevirt/enhancements/pull/208)
- **Feature Tracking:** [VIRTSTRAT-563 -- Ability to ignore Liveness/Readiness probes during VM maintenance](https://redhat.atlassian.net/browse/VIRTSTRAT-563)
- **Epic Tracking:** [CNV-82132 -- GA: Implement pause probe functionality](https://redhat.atlassian.net/browse/CNV-82132)
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: 4.23/5.0
- **QE Owner(s):** Geetika Kapoor(@geetikakay)
- **Owning SIG:** sig-infra
- **Participating SIGs:** N/A

**Document Conventions (if applicable):**

- VMI = VirtualMachineInstance
- VEP = Virtualization Enhancement Proposal

### **Feature Overview**

OpenShift Virtualization 4.23/5.0 introduces annotation-based GuestAgentPing probe pausing, designed per VEP 207. This feature is GA in 4.23/5.0 and this STP covers the GA phase. VM administrators can temporarily pause GuestAgentPing-based liveness and readiness probes on running VirtualMachineInstances by setting the `kubevirt.io/pause-guest-agent-probes` annotation. While paused, guest agent probes report success, preventing unwanted VM restarts or readiness transitions during planned maintenance such as guest OS updates, driver installations, or agent upgrades. Removing the annotation resumes normal probe behavior. The feature operates independently of existing probe suppression mechanisms for live migration and VM pause.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value, technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - VEP 207 ([kubevirt/enhancements#208](https://github.com/kubevirt/enhancements/pull/208)) defines clear scope: GuestAgentPing probes only, annotation-based manual control.

- [x] **Understand Value and Customer Use Cases**
  - User stories:
    - As a VM owner, I want to pause GuestAgentPing probes on a running VM during maintenance (e.g., guest OS update, driver installation), so that the VM is not restarted by the liveness probe while the guest agent is temporarily unavailable.
    - As a cluster admin, I want to pause probes on selected VMIs (by label or namespace) during a scheduled maintenance window, so that planned agent downtime does not trigger unwanted restarts or readiness transitions across the affected workloads.

- [x] **Testability**
  - All four acceptance criteria are directly testable: annotation set/remove behavior, probe type isolation, suppression independence and migration propagation.

- [x] **Acceptance Criteria**
  - Derived from VEP 207 goals:
    - Manual pause/unpause of GuestAgentPing probes via VMI annotations without Pod restart
    - Annotation-based pause operates independently of existing probe suppression mechanisms (live migration, VM pause)
    - Non-GuestAgentPing probes (TCP, HTTP, Exec) are unaffected
    - Annotation removal resumes normal probe behavior

- [x] **Non-Functional Requirements (NFRs)**
  - **UI:** No UI changes (no-ui, no-ux labels). Annotation-based manual control only; no customer-facing UI testing planned unless PM/UX identifies value.
  - **Monitoring:** No new metrics or alerts required. GuestAgentPingFailed events are suppressed during probe pause — existing dashboards may show gaps during maintenance windows.
  - **Observability:** Probe pause suppresses GuestAgentPingFailed events and skips QemuAgentCommand, creating a temporary observability gap for guest-agent connectivity in event streams. Operators should treat paused probes as an intentional blind spot during planned maintenance. Monitoring team awareness covered in Cross Integrations (II.2).
  - **Documentation:** Documentation changes are merged.
  - **Performance:** Annotation check is an O(1) atomic.Bool read with negligible performance impact. No latency or throughput requirements.
  - **Security:** Standard VMI annotation governed by existing Kubernetes RBAC. No new permission model or security boundary; users with VMI patch permissions can set or remove the annotation.
  - **Scalability:** No new per-VMI scale requirements — annotation operates independently on each VMI. Maintenance workflows that combine probe pause with live migration (CNV-82392) inherit existing cluster-level live migration parallelism limits. Multi-VMI batch maintenance (P2 scenario) is bounded by operator tooling and API rate limits, not by KubeVirt-enforced aggregate limits; cluster admins should plan maintenance windows accounting for live migration concurrency when migrating paused VMIs.

#### **2. Known Limitations**

- No automatic triggering by KubeVirt-internal operations (e.g., snapshots, live migration). The annotation must be set by the user, either manually or through external tooling (e.g., shell scripts, CronJobs).
- Live migration probe suppression is handled separately (kubevirt/kubevirt#17235) and operates independently of this annotation.
- The annotation does not suppress guest-exec commands. Access credential injection continues to work while probes are paused.
- Windows guest OS update scenarios use the same annotation mechanism but OS-specific validation is not included in this test plan.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - GuestAgentPingFailed events are suppressed during pause — monitoring gap identified.

- [x] **Technology Challenges**
  - Thread safety: SyncVMI writes the pause state from one goroutine while GuestPing reads from another. Atomic.Bool ensures correctness, but timing between annotation change and probe evaluation creates a race window that is difficult to reproduce deterministically.
  - Three suppression paths coexist in GuestPing: annotation pause, live migration probe suppression and VM pause probe suppression. Interaction ordering across these paths must be verified.
  - Annotation propagation timing during live migration: SyncVirtualMachine gRPC delivers annotation state to the target virt-launcher, but there is a window between migration start and first SyncVMI where the annotation has not yet reached the target. This window is covered by the existing `isLiveMigrationInProgress()` suppression path, which suppresses probes independently of the annotation during the entire migration. The annotation must take effect before `isLiveMigrationInProgress()` returns false on the target.
  - GuestPing early-return skips QemuAgentCommand entirely (not error suppression), which also suppresses GuestAgentPingFailed Kubernetes events. Monitoring systems relying on these events will see gaps during probe pause.

- [x] **Test Environment Needs**
  - Multi-node cluster required for live migration scenarios (minimum 2 schedulable worker nodes). Guest agent must be installed and running in test VMs. Live migration scenarios require RWX block storage (e.g., ocs-storagecluster-ceph-rbd with accessModes: ReadWriteMany, volumeMode: Block).

- [x] **API Extensions**
  - New annotation `kubevirt.io/pause-guest-agent-probes` on VMI. Accepts standard boolean values (e.g., "true", "false"). Setting it to "true" pauses GuestAgentPing probes. Removing the annotation or setting it to "false" resumes normal probe behavior. No new CRDs, API endpoints, or feature gates introduced.

- [x] **Topology Considerations**
  - Single-cluster topology sufficient. Multi-node required for migration test scenarios only. No multi-cluster, external dependency, or network topology requirements.

---

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

This test plan covers the annotation-based GuestAgentPing probe pausing feature introduced by VEP 207. Testing validates that VM administrators can temporarily pause GuestAgentPing-based liveness and readiness probes on running VirtualMachineInstances by setting the `kubevirt.io/pause-guest-agent-probes` annotation. While set, guest agent probes report success, preventing unwanted VM restarts or readiness transitions during planned maintenance. Removing the annotation resumes normal probe behavior. Testing also covers probe type isolation (non-GuestAgentPing probes unaffected), annotation propagation during live migration, coexistence with existing probe suppression mechanisms, event suppression during pause, and access credential injection independence.

**Testing Goals**

- **P0:** Verify that pausing GuestAgentPing liveness probes prevents VM restarts during guest agent downtime
- **P0:** Verify that removing the pause annotation resumes normal probe behavior
- **P1:** Verify that GuestAgentPing readiness probes are also paused by the annotation
- **P1:** Verify that non-GuestAgentPing probes (exec, TCP, HTTP) are unaffected by the annotation
- **P1:** Verify that the pause annotation propagates correctly during live migration
- **P1:** Verify that probe pause coexists with existing migration and VM pause suppression mechanisms
- **P1:** Verify that access credential injection continues working while probes are paused
- **P1:** Verify that GuestAgentPingFailed events are suppressed during probe pause
- **P2:** Verify annotation value handling (boolean and invalid values)
- **P2:** Verify batch annotation of multiple VMIs using a scheduled job or patch command
- **P2:** Verify annotation persistence, snapshot independence, and concurrent safety

**Out of Scope (Testing Scope Exclusions)**

- [x] HTTP, TCP, and Exec probe pausing -- VEP 207 explicitly limits scope to GuestAgentPing probes only
- [x] Automatic probe scheduling or timeout -- VEP 207 defines annotation as manual-only with no automatic expiry
- [x] Live migration probe fix (kubevirt/kubevirt#17235) -- separate feature with independent implementation and test coverage
- [x] Upstream Kubernetes probe suspension (KEP 5002) -- upstream proposal not yet implemented in Kubernetes
- [x] Windows guest OS update scenarios -- same annotation mechanism applies but OS-specific validation deferred

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** -- Validates that the feature works according to specified requirements and user stories
  - *Details:* Tier 1 tests verify core probe pause/resume lifecycle, readiness probe pausing, probe type isolation, annotation value handling, event suppression and integration point isolation. All Tier 1 tests in Go/Ginkgo.
- [x] **Automation Testing** -- Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All tests automated. Upstream e2e test exists (kubevirt/kubevirt#17664). Downstream Tier 2 tests in Python/pytest cover end-to-end maintenance and migration workflows.
- [x] **Regression Testing** -- Verifies that new changes do not break existing functionality
  - *Details:* Regression analysis identified 9 impacted features: liveness probes, readiness probes, event generation, live migration suppression, SyncVMI reconciliation, access credential injection, VM pause, exec probes and snapshots. All have corresponding test scenarios.
- [x] **Self-Validation Testing** -- Should any of the new tests be included in the self-validation test package?
  - *Details:* N/A. The feature is a manual annotation toggle, not a core operational scenario. Self-validation tests target always-on product health checks. Probe pausing is user-initiated and situational.

**Non-Functional**

- [x] **Performance Testing** -- Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A. Annotation check is an O(1) atomic.Bool read with negligible performance impact. No latency or throughput requirements.
- [x] **Scale Testing** -- Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* N/A for dedicated scale testing. Annotation operates per-VMI with no new aggregate scaling concern. Multi-VMI batch annotation (P2) validates operator-scale maintenance workflows at modest VM counts. Live migration scenarios (CNV-82392) inherit existing cluster-level migration parallelism limits; no additional scale validation beyond functional coverage is planned.
- [x] **Security Testing** -- Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* N/A. Annotation is a standard VMI annotation governed by existing Kubernetes RBAC. No new permission model or security boundary introduced.
- [x] **Usability Testing** -- Validates user experience and accessibility requirements
  - *Details:* N/A. Feature has no UI (no-ui, no-ux labels). Annotation-based interface documented in upstream user guide (kubevirt/user-guide#990).
- [x] **Monitoring** -- Does the feature require metrics and/or alerts?
  - *Details:* N/A. No new metrics or alerts introduced. Note: GuestAgentPingFailed events are suppressed during probe pause, which may affect existing monitoring dashboards.

**Integration & Compatibility**

- [x] **Compatibility Testing** -- Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Annotation accepts strconv.ParseBool values for input flexibility. No feature gate required, ensuring compatibility with default cluster configurations.
- [x] **Upgrade Testing** -- Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* N/A. The annotation is standard VMI metadata persisted in etcd and survives upgrades like any Kubernetes annotation. The in-memory `guestAgentProbePaused` flag in virt-launcher is re-set by `syncGuestAgentProbePaused()` on every SyncVMI call, which virt-handler issues automatically after reconnect during rolling updates. No feature-specific upgrade logic, schema conversion, or manual re-sync is needed. Re-delivery after virt-handler restart is covered by standard product upgrade testing.
- [x] **Dependencies** -- Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* None identified. Implementation PR (kubevirt/kubevirt#17664) is merged. No team delivery dependencies.
- [x] **Cross Integrations** -- Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* Monitoring teams should be aware that GuestAgentPingFailed events are suppressed during probe pause. Snapshot feature (isPausedButHealthy suppression) operates independently and is not affected.

**Infrastructure**

- [x] **Cloud Testing** -- Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* N/A. Feature is platform-agnostic with no cloud-specific dependencies.

#### **3. Test Environment**

- **Cluster Topology:** Multi-node cluster with at least 2 schedulable worker nodes (e.g., 3 control-plane + 2 worker compact or standard topology)
- **OCP & OpenShift Virtualization Version(s):** OCP 4.23+ / OpenShift Virtualization 4.23 (CNV 4.23.0) and OCP 5.0+ / OpenShift Virtualization 5.0 (CNV 5.0.0)
- **CPU Virtualization:** Standard (no nested virtualization or special CPU features required)
- **Compute Resources:** Standard (sufficient for 2+ concurrent VMIs with guest agents running)
- **Special Hardware:** None required
- **Storage:** ocs-storagecluster-ceph-rbd (accessModes: ReadWriteMany, volumeMode: Block) for live migration scenarios
- **Network:** OVN-Kubernetes CNI (default); Multus optional, not required for this feature
- **Required Operators:** OpenShift Virtualization (kubevirt-hyperconverged), HyperConverged Cluster Operator (hco-operator)
- **Platform:** OpenShift Container Platform (bare metal or cloud provider)
- **Special Configurations:** Guest agent (qemu-guest-agent) must be installed and running in test VM images (Fedora or RHEL with guest agent package)

#### **3.1. Testing Tools & Frameworks**

N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [x] Implementation PR (kubevirt/kubevirt#17664) merged and included in target build
- [x] Guest agent VM images available with qemu-guest-agent package installed
- [x] Upstream documentation for annotation usage merged (kubevirt/user-guide#990)

#### **5. Risks**

- [x] **Test Coverage**
  - Risk: Race condition between annotation setting and probe execution is non-deterministic and may be difficult to reproduce reliably.
  - Mitigation: Concurrent toggling test scenario (P2) covers this. Upstream PR review explicitly identified the race window and the atomic.Bool mitigation.
  - *Areas with reduced coverage:* Exact race timing between SyncVMI annotation write and GuestPing read.
  - *Sign-off:* Geetika Kapoor / 2026-07-20

- [x] **Test Environment**
  - Risk: Guest agent availability and behavior may vary across OS images and versions.
  - Mitigation: Use standard Fedora images with known qemu-guest-agent versions for consistent test results.
  - *Missing or unavailable environments:* None. Standard Fedora images with guest agent are available.
  - *Sign-off:* Geetika Kapoor / 2026-07-20

- [x] **Untestable Aspects**
  - Risk: Exact timing of SyncVMI delivery during live migration is non-deterministic, making the annotation propagation window difficult to test precisely.
  - Mitigation: Test observable outcomes (probes remain paused after migration completes) rather than internal timing. The propagation window is covered by the existing `isLiveMigrationInProgress()` suppression path.
  - *Reason untestable and mitigation approach:* Internal SyncVMI delivery timing is not externally observable. Observable outcome testing validates the end result.
  - *Sign-off:* Geetika Kapoor / 2026-07-20

- [x] **Resource Constraints**
  - Mitigation: No resource constraints identified. Feature testing uses standard test infrastructure with no additional staffing or hardware requirements.

- [x] **Dependencies**
  - Mitigation: No dependencies. Implementation PR (kubevirt/kubevirt#17664) is merged with no pending team delivery dependencies.

- [x] **Other**
  - Risk: Monitoring dashboards relying on GuestAgentPingFailed events may need updates to account for event suppression during probe pause.
  - Mitigation: Document event suppression behavior. Monitoring team awareness covered in Cross Integrations (II.2).
  - *Sign-off:* Geetika Kapoor / 2026-07-20

---

### **III. Test Scenarios & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are tested.

#### **1. Requirements-to-Tests Mapping**

- **[CNV-82132]** -- As a VM admin, I want to pause GuestAgentPing liveness probes on a running VMI so the VM survives planned guest agent downtime
  - *Test Scenario:* Verify VMI survives guest agent stop with pause annotation
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P0
  - *Upstream coverage:* kubevirt/kubevirt#17664 -- full (should not kill the VMI when probes are paused by annotation)
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want to perform a complete maintenance workflow with probes paused throughout
  - *Test Scenario:* Verify full maintenance workflow: pause probes, stop agent, resume probes
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P1
  - *Downstream required:* yes


- **[CNV-82132]** -- As a VM admin, I want to resume normal probe behavior by removing the annotation
  - *Test Scenario:* Verify probes resume and VMI is restarted after annotation removal
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P0
  - *Upstream coverage:* kubevirt/kubevirt#17664 -- partial (should resume normal probe behavior when unpaused)
  - *Coverage gap:* Unit test only — no cluster e2e for resume after annotation removal on running VMI
  - *Gap resolution:* upstream
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want GuestAgentPing readiness probes also paused by the annotation so traffic routing remains stable during maintenance
  - *Test Scenario:* Verify VMI remains Ready with paused readiness probes
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1
  - *Upstream coverage:* kubevirt/kubevirt#17664 -- partial (should skip probe entirely when paused)
  - *Coverage gap:* Unit test covers GuestPing short-circuit but no e2e asserting VMI Ready condition with paused readiness probes
  - *Gap resolution:* upstream
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want non-GuestAgentPing probes (exec, TCP, HTTP) unaffected by the annotation
  - *Test Scenario:* Verify exec probe fires normally with pause annotation set
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1
  - *Upstream coverage:* none -- not in analyzed PR(s)
  - *Downstream required:* no


- **[CNV-82392]** -- As a VM admin, I want the pause annotation to propagate during live migration so probes remain paused on the target node
  - *Test Scenario:* Verify VMI is never restarted during or after live migration with pause annotation set
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1
  - *Upstream coverage:* none -- not in analyzed PR(s)
  - *Downstream required:* no


- **[CNV-82392]** -- As a VM admin, I want to perform maintenance on a migrated VM with probes remaining paused throughout
  - *Test Scenario:* Verify pause annotation persists through migration and maintenance
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P1
  - *Downstream required:* yes


- **[CNV-82132]** -- As a VM admin, I want the annotation-based pause and live migration probe suppression to work independently
  - *Test Scenario:* Verify annotation pause and live migration probe behavior operate independently
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1
  - *Upstream coverage:* none -- not in analyzed PR(s)
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want GuestAgentPingFailed events suppressed while probes are paused so monitoring dashboards are not polluted
  - *Test Scenario:* Verify no GuestAgentPingFailed events during probe pause
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1
  - *Upstream coverage:* kubevirt/kubevirt#17664 -- partial (should skip probe entirely when paused)
  - *Coverage gap:* Unit test confirms nil return from GuestPing but no test explicitly asserts absence of GuestAgentPingFailed events
  - *Gap resolution:* upstream
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want access credential injection to continue working while probes are paused
  - *Test Scenario:* Verify SSH key injection succeeds with pause annotation set
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1
  - *Upstream coverage:* none -- not in analyzed PR(s)
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want the annotation to accept standard boolean values and treat invalid values as false (probes resume)
  - *Test Scenario:* Verify annotation accepts boolean values and that invalid values resume normal probe behavior
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2
  - *Upstream coverage:* kubevirt/kubevirt#17664 -- partial (should parse annotation value correctly, DescribeTable 7 entries)
  - *Coverage gap:* Unit test covers ParseBool parsing but no cluster-level test verifies annotation values applied via Kubernetes API
  - *Gap resolution:* upstream
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want probe pausing available without enabling a feature gate
  - *Test Scenario:* Verify probe pause works with default cluster configuration and no feature gate enabled
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2
  - *Upstream coverage:* kubevirt/kubevirt#17664 -- full (should not kill the VMI when probes are paused by annotation)
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want the annotation to persist and probes to remain paused across multiple reconciliation cycles
  - *Test Scenario:* Verify probes remain paused after multiple SyncVMI reconciliation cycles with no annotation change
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2
  - *Upstream coverage:* none -- not in analyzed PR(s)
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want snapshot operations to use their own probe suppression independently of this annotation
  - *Test Scenario:* Verify VM snapshot completes successfully and VMI remains Running with probe pause annotation set
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2
  - *Upstream coverage:* none -- not in analyzed PR(s)
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want the annotation-based pause to coexist with VM pause/unpause probe suppression
  - *Test Scenario:* Verify annotation pause persists through VM pause/unpause cycle
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2
  - *Upstream coverage:* none -- not in analyzed PR(s)
  - *Downstream required:* no


- **[CNV-82132]** -- As a cluster admin, I want to pause probes across multiple VMIs during a scheduled maintenance window
  - *Test Scenario:* Verify batch annotation of multiple VMIs using a CronJob or patch command. Confirm all targeted VMIs have probes paused and removing the annotation resumes probes on all VMIs.
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P2
  - *Downstream required:* yes

- **[CNV-82132]** -- As a VM admin, I want annotation toggling under concurrent probe execution to be safe
  - *Test Scenario:* Verify VMI remains Running and virt-launcher pod does not restart when pause annotation is toggled repeatedly during active probes
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P2
  - *Downstream required:* yes


---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Karel Simon (@ksimon1)
  - Roni Kishner (@RoniKishner)
* **Approvers:**
  - Ruth Netser (@rnetser)
