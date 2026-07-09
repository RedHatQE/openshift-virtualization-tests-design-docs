# Openshift-virtualization-tests Test plan

## **Annotation-Based GuestAgentPing Probe Pausing (VEP 207) - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP 207 -- Manual GuestAgentPing probe control](https://github.com/kubevirt/enhancements/pull/208)
- **Feature Tracking:** [VIRTSTRAT-563 -- Ability to ignore Liveness/Readiness probes during VM maintenance](https://redhat.atlassian.net/browse/VIRTSTRAT-563)
- **Epic Tracking:** [CNV-82132 -- GA: Implement pause probe functionality](https://redhat.atlassian.net/browse/CNV-82132)
- **Implementation PR:** [kubevirt/kubevirt#17664 -- virt-launcher annotation handling + unit tests](https://github.com/kubevirt/kubevirt/pull/17664)
- **Upstream e2e PR:** [kubevirt/kubevirt#19076 -- GuestAgent probe pause e2e, test_id CNV82132-001/-002/-003/-004](https://github.com/kubevirt/kubevirt/pull/19076)
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

OpenShift Virtualization 4.23/5.0 introduces annotation-based GuestAgentPing probe pausing, designed per VEP 207. This feature is GA in 4.23/5.0 and this STP covers the GA phase. VM administrators can temporarily pause GuestAgentPing-based liveness and readiness probes on running VirtualMachineInstances by setting the `kubevirt.io/pause-guest-agent-probes` annotation. While paused, GuestAgentPing reports success, so kubelet liveness does not fail the virt-launcher compute container and readiness does not drop solely because the guest agent is down. Removing the annotation (or setting it to a non-true ParseBool value) resumes normal probe behavior. The annotation is independent of existing GuestAgentPing suppression during live migration and user VM pause (those paths still apply when the annotation is not set).

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value, technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - VEP 207 ([kubevirt/enhancements#208](https://github.com/kubevirt/enhancements/pull/208)) defines clear scope: GuestAgentPing probes only, annotation-based manual control.

- [x] **Understand Value and Customer Use Cases**
  - User stories:
    - As a VM owner, I want to pause GuestAgentPing probes on a running VM during maintenance (e.g., guest OS update, driver installation), so that liveness does not fail the VMI while the guest agent is temporarily unavailable.
    - As a VM admin, I want to set or remove the pause annotation on the VMIs I am maintaining, so that planned agent downtime does not trigger unwanted liveness failures or readiness transitions on those workloads.

- [x] **Testability**
  - All four acceptance criteria are directly testable: annotation set/remove behavior, probe type isolation, suppression independence and migration propagation.

- [x] **Acceptance Criteria**
  - Derived from VEP 207 goals:
    - Manual pause/unpause of GuestAgentPing probes via VMI annotations without requiring a virt-launcher pod restart
    - Annotation-based pause operates independently of existing probe suppression mechanisms (live migration, VM pause)
    - Non-GuestAgentPing probes (TCP, HTTP, Exec) are unaffected
    - Annotation removal resumes normal probe behavior

- [x] **Non-Functional Requirements (NFRs)**
  - **UI:** No UI changes (no-ui, no-ux labels). Annotation-based manual control only; no customer-facing UI testing planned unless PM/UX identifies value.
  - **Monitoring:** No new metrics or alerts required. `GuestAgentPingFailed` events are not emitted while probes are paused — existing dashboards may show gaps during maintenance windows. No API surface reports pause state, so e2e confirms it from a virt-launcher log line (see II.5 Test Maintenance); a VMI condition or metric would remove that coupling.
  - **Observability:** While probes are paused, `GuestAgentPingFailed` events are not emitted (temporary gap in guest-agent connectivity signals). Operators should treat paused probes as an intentional blind spot during planned maintenance. *Validated by:* CNV82132-001. Monitoring team awareness covered in Cross Integrations (II.2).
  - **Documentation:** Documentation changes are merged.
  - **Performance:** Per-VMI annotation lookup with negligible performance impact (see #17664). No latency or throughput requirements.
  - **Security:** Standard VMI annotation governed by existing Kubernetes RBAC. No new permission model or security boundary; users with VMI patch permissions can set or remove the annotation.
  - **Scalability:** No new per-VMI scale requirements — annotation operates independently on each VMI. Maintenance workflows that combine probe pause with live migration (CNV-82392) inherit existing cluster-level live migration parallelism limits; cluster admins should plan maintenance windows accounting for live migration concurrency when migrating paused VMIs.

#### **2. Known Limitations**

- The annotation is never auto-applied by KubeVirt (snapshots, migrations, or other internal operations). The user or external tooling must set it.
- During live migration, GuestAgentPing errors can still be suppressed by a separate mechanism (kubevirt/kubevirt#17235), independent of this annotation. Operators who need probes paused through maintenance that includes migration must still set `kubevirt.io/pause-guest-agent-probes` on the VMI (migration-only suppression ends when migration completes).
- The annotation does not suppress guest-exec. Access credential injection and other guest-agent operations still require a reachable qemu-guest-agent. Probe pause does not block them when the agent is connected; stopping the agent for maintenance makes them unavailable for the same reasons as without the annotation.

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - `GuestAgentPingFailed` events are suppressed during pause — monitoring gap identified.

- [x] **Technology Challenges** (implementation detail: [kubevirt/kubevirt#17664](https://github.com/kubevirt/kubevirt/pull/17664), [VEP 207](https://github.com/kubevirt/enhancements/pull/208))
  - **Annotation change vs. next probe (VEP 207):** A VMI patch does not guarantee the very next kubelet GuestAgentPing cycle sees pause already active on virt-launcher. *Observable consequence:* Brief window where behavior may still reflect the prior state; after pause is active, liveness/readiness must not fail the VMI solely because the guest agent is down. *Exercised by:* CNV82132-001 (pause, stop agent, hold Running 45s+, no `GuestAgentPingFailed`); implicit hold across reconciles in CNV82132-002, -004.
  - **Coexistence with other probe suppression (VEP acceptance):** Annotation pause must not break existing suppression during live migration or user-initiated VM pause. Annotation skip and migration/VM-pause error suppression are independent: if the annotation is set, GuestAgentPing does not run; if it is not set, migration and healthy-paused-domain suppression still apply. *Observable consequence:* VMI stays Running when pause applies on the migration target with a dead agent; VM pause without annotation still suppresses probe kills. *Exercised by:* CNV82132-004; existing `guest_agent.go` user-paused VMI test (VM pause only). Combined annotation + VM pause: Tier 2 mapping row (downstream).
  - **Pause on migration target (CNV-82392):** After live migrate, pause may not be effective on the target pod until virt-launcher has applied the annotation from the VMI. *Observable consequence:* Without waiting for pause to be active, tests could false-pass while migration-only suppression still applies. *Exercised by:* CNV82132-004 waits for virt-launcher log confirmation (see II.5 Test Maintenance), then holds Running through the probe kill window; unpause with dead agent proves the annotation drove survival.
  - **Monitoring blind spot during pause:** Paused GuestAgentPing probes report success and do not emit `GuestAgentPingFailed` even when the agent is unhealthy. *Observable consequence:* Event stream gap during maintenance; events resume after unpause when probes run again. *Exercised by:* CNV82132-001 (`ExpectNoEvent` while paused, `ExpectEvent` after unpause); mapping row for event suppression.

- [x] **Test Environment Needs**
  - Guest agent (qemu-guest-agent) must be installed and running in test VM images. Live migration tests need **≥2 schedulable nodes** for VM workloads; Tier 1 CNV82132-004 uses containerdisk and needs no RWX storage. RWX (or equivalent live-migratable shared storage) applies only when testing migration of **PVC-backed** VMIs (Tier 2).

- [x] **API Extensions**
  - New annotation `kubevirt.io/pause-guest-agent-probes` on VMI. Accepts standard boolean values via `strconv.ParseBool` (e.g. `"true"`, `"1"`, `"TRUE"` pause; `"false"`, `"0"`, missing, or non-bool values do not pause). Setting it to a true value pauses GuestAgentPing probes. Removing the annotation or setting a non-true value resumes normal probe behavior. No new CRDs, API endpoints, or feature gates introduced.

- [x] **Topology Considerations**
  - Single-cluster topology sufficient. At least two schedulable workload nodes required only for live migration scenarios. No multi-cluster or special network topology requirements.

---

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

This test plan covers the annotation-based GuestAgentPing probe pausing feature introduced by VEP 207. Testing validates that VM administrators can temporarily pause GuestAgentPing-based liveness and readiness probes on running VirtualMachineInstances by setting the `kubevirt.io/pause-guest-agent-probes` annotation. While set, GuestAgentPing reports success, so liveness does not fail the VMI and readiness does not drop solely because the guest agent is down. Removing the annotation resumes normal probe behavior. Testing also covers probe type isolation (non-GuestAgentPing probes unaffected), annotation propagation during live migration, coexistence with existing probe suppression, event suppression during pause, and that probe pause does not block access credential injection when the guest agent is connected (agent-down maintenance is a separate condition).

**Testing Goals**

- **P0:** Verify that pausing GuestAgentPing liveness probes prevents the VMI from being failed while the guest agent is down
- **P0:** Verify that removing the pause annotation resumes normal probe behavior
- **P1:** Verify that GuestAgentPing readiness probes are also paused by the annotation
- **P1:** Verify that non-GuestAgentPing probes are unaffected by the annotation (*observable:* exec/TCP/HTTP probes still run; only GuestAgentPing liveness/readiness behavior changes). *Exercised by:* CNV82132-003 (exec); TCP/HTTP are kubelet probes on the compute container and never use the GuestAgentPing pause path
- **P1:** Verify that the pause annotation propagates correctly during live migration
- **P1:** Verify that probe pause coexists with live migration probe suppression (annotation effective on migration target; independent of #17235-only suppression)
- **P1 (regression):** Verify that user VM Pause probe suppression is unchanged when the pause annotation is not used
- **P2:** Verify annotation pause remains effective through a VM Pause/Unpause cycle on the same VMI (stacked workflow)
- **P1:** Verify that access credential injection is not blocked by probe pause when the guest agent is connected (annotation does not suppress guest-exec)
- **P1:** Verify that GuestAgentPingFailed events are suppressed during probe pause
- **P2:** Verify annotation value handling (boolean and invalid values)
- **P2:** Verify annotation persistence and snapshot coexistence (Tier 2 / documented gaps where upstream does not cover)

**Out of Scope (Testing Scope Exclusions)**

> **PM/DEV Sign-off:** Ronen / Karel

- [x] HTTP, TCP, and Exec probe pausing -- VEP 207 explicitly limits pause scope to GuestAgentPing probes only; isolation (those probes still run) is in scope via CNV82132-003 and the P1 goal above
- [x] Automatic probe scheduling or timeout -- VEP 207 defines annotation as manual-only with no automatic expiry
- [x] Standalone validation of live migration probe suppression (kubevirt/kubevirt#17235) -- separate feature and test coverage; this STP only verifies annotation propagation on the migration target and coexistence (CNV82132-004)
- [x] Upstream Kubernetes probe suspension (KEP 5002) -- upstream proposal not yet implemented in Kubernetes
- [x] Windows guest OS update scenarios -- OS-specific validation deferred (annotation mechanism is OS-agnostic)
- [x] Batch annotation of multiple VMIs (CronJob / label selector) -- not a product API; per-VMI annotation only
- [x] Concurrent annotation toggling as a race reproducer -- Kubernetes API patches cannot toggle fast enough to hit the sub-probe-cycle window between virt-launcher applying the annotation and kubelet's next GuestAgentPing; repeated e2e toggles would not create a deterministic race

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** -- Validates that the feature works according to specified requirements and user stories
  - *Details:* Tier 1 tests verify core probe pause/resume lifecycle, readiness probe pausing, probe type isolation, annotation value handling, event suppression and integration point isolation. All Tier 1 tests in Go/Ginkgo.
- [x] **Automation Testing** -- Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All tests automated. Tier 1 upstream e2e lives in kubevirt/kubevirt#19076 -- `tests/compute/guest_agent_probe_pause.go` (CNV82132-001, -002, -004) plus CNV82132-003 in `tests/compute/guest_agent.go`. kubevirt/kubevirt#17664 carries the implementation and its unit tests; the single e2e spec it added is superseded and removed by #19076. Downstream Tier 2 tests in Python/pytest cover end-to-end maintenance and migration workflows.
- [x] **Regression Testing** -- Verifies that new changes do not break existing functionality
  - *Details:* Regression analysis identified 9 impacted features; upstream mapping (kubevirt/kubevirt#19076 / `guest_agent.go`):
    - **Liveness probes:** CNV82132-001 (pause holds Running); 9299 (unpaused agent stop fails VMI).
    - **Readiness probes:** CNV82132-002 (Ready while paused); 6741 (unpaused readiness drop/recover).
    - **Event generation:** CNV82132-001 (`ExpectNoEvent` / `ExpectEvent` for `GuestAgentPingFailed`); 9299 (unpaused failure emits event).
    - **Live migration suppression:** CNV82132-004 (pause on target after migrate); migration suite guest-agent-ping liveness (no annotation).
    - **VMI reconciliation:** Implicit in CNV82132-001, -002, -004 (45–60+ s pause hold while virt-handler reconciles).
    - **Access credential injection:** No upstream e2e with annotation + connected agent (mapping gap).
    - **VM pause:** `guest_agent.go` user-paused VMI (API Pause without annotation); stacked annotation + VM Pause — Tier 2 downstream.
    - **Exec probes:** CNV82132-003 (exec liveness still fails with pause annotation).
    - **Snapshots:** No upstream e2e with pause annotation (Tier 2 downstream).
- [x] **Self-Validation Testing** -- Should any of the new tests be included in the self-validation test package?
  - *Details:* N/A. The feature is a manual annotation toggle, not a core operational scenario. Self-validation tests target always-on product health checks. Probe pausing is user-initiated and situational.

**Non-Functional**

- [x] **Performance Testing** -- Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A. Per-VMI annotation with negligible performance impact. No latency or throughput requirements.
- [x] **Scale Testing** -- Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* N/A for dedicated scale testing. Annotation operates per-VMI with no new aggregate scaling concern. Live migration scenarios (CNV-82392) inherit existing cluster-level migration parallelism limits; no additional scale validation beyond functional coverage is planned.
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
  - *Details:* N/A. Annotation is standard VMI metadata in etcd and survives upgrades like any Kubernetes annotation. Pause effectiveness across virt-handler/virt-launcher restarts is covered implicitly by CNV82132-001, -002, and -004 (pause held 45–60+ seconds while the VMI is reconciled). No feature-specific upgrade test in this STP; standard product upgrade testing applies.
- [x] **Dependencies** -- Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* None identified. Implementation PR (kubevirt/kubevirt#17664) is merged. No team delivery dependencies.
- [x] **Cross Integrations** -- Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* Monitoring teams should be aware that GuestAgentPingFailed events are suppressed during probe pause (CNV82132-001). Snapshot and user VM pause use separate probe-suppression behavior; coexistence with annotation pause is a P2 Tier 2 scenario, not validated upstream in #19076.

**Infrastructure**

- [x] **Cloud Testing** -- Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* N/A. Feature is platform-agnostic with no cloud-specific dependencies.

#### **3. Test Environment**

- **Cluster Topology:** Any supported single-cluster deployment where VM workloads can be scheduled. Non-migration Tier 1 (CNV82132-001, -002, -003) runs on a single schedulable node. Live migration (CNV82132-004, Tier 2 migrated-maintenance) requires **at least two schedulable nodes** that can run VMIs on different hosts (upstream enforces `decorators.RequiresTwoSchedulableNodes`); control-plane/worker layout is not prescribed.
- **OCP & OpenShift Virtualization Version(s):** OCP 4.23+ / OpenShift Virtualization 4.23 (CNV 4.23.0) and OCP 5.0+ / OpenShift Virtualization 5.0 (CNV 5.0.0)
- **CPU Virtualization:** Standard (no nested virtualization or special CPU features required)
- **Compute Resources:** Standard (sufficient for 2+ concurrent VMIs with guest agents running)
- **Special Hardware:** None required
- **Storage:** Tier 1 upstream migration coverage (CNV82132-004) uses **containerdisk**-backed Fedora VMIs and does **not** require shared or RWX volumes. Use a storage class with **ReadWriteMany** access (and volume mode suitable for live-migratable PVCs, e.g. block RWX on ODF) only for scenarios that **live-migrate PVC-backed** VMIs (Tier 2 downstream / product workflows).
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
  - Risk: Sub-probe-cycle timing between VMI annotation patch and the next GuestAgentPing is non-deterministic and cannot be forced from e2e.
  - Mitigation: CNV82132-001, -002, and -004 hold pause long enough that a failure to apply pause would surface as liveness or readiness failure; CNV82132-004 uses log-confirmed pause on the migration target before asserting survival.
  - *Areas with reduced coverage:* Exact interleaving of a single probe with an in-flight annotation patch.
  - *PM/DEV Sign-off:* Ronen / Karel

- [x] **Test Environment**
  - Risk: Guest agent availability and behavior may vary across OS images and versions.
  - Mitigation: Use standard Fedora images with known qemu-guest-agent versions for consistent test results.
  - *Missing or unavailable environments:* None. Standard Fedora images with guest agent are available.
  - *PM/DEV Sign-off:* Ronen / Karel

- [x] **Untestable Aspects**
  - Risk: Sub-probe-cycle timing between annotation patch and GuestAgentPing cannot be forced from a test.
  - Mitigation: CNV82132-004 waits for virt-launcher log confirmation that pause is active on the migration target (II.5 Test Maintenance), then asserts VMI stays Running; removing pause with dead agent proves probes resumed. Outcome-based coverage in CNV82132-001/-002/-004; implementation concurrency is covered in #17664 unit tests and design review.
  - *Reason untestable and mitigation approach:* Kubelet probe schedule cannot be interleaved with API patch from e2e. Observable VMI phase, Ready, and events validate the operator-visible result.
  - *PM/DEV Sign-off:* Ronen / Karel

- [x] **Test Maintenance**
  - Risk: Tier 1 e2e depends on a virt-launcher log line to confirm pause reached the pod before post-migration assertions. A log wording change in #17664 breaks CNV82132-001, -002, and -004 without necessarily indicating a product regression.
  - Mitigation: Log substring is a single constant in `tests/compute/guest_agent_probe_pause.go`; failure messages point maintainers to update the test if launcher logging changes. Follow-up: VMI condition or metric for pause state (see §I Monitoring NFR).
  - *PM/DEV Sign-off:* Ronen / Karel

- [x] **Resource Constraints**
  - Mitigation: No resource constraints identified. Feature testing uses standard test infrastructure with no additional staffing or hardware requirements.

- [x] **Dependencies**
  - Mitigation: No dependencies. Implementation PR (kubevirt/kubevirt#17664) is merged with no pending team delivery dependencies.

- [x] **Other**
  - Risk: Monitoring dashboards relying on GuestAgentPingFailed events may need updates to account for event suppression during probe pause.
  - Mitigation: Document event suppression behavior. Monitoring team awareness covered in Cross Integrations (II.2).
  - *PM/DEV Sign-off:* Ronen / Karel

---

### **III. Test Scenarios & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are tested.

#### **1. Requirements-to-Tests Mapping**

- **[CNV-82132]** -- As a VM admin, I want to pause GuestAgentPing liveness probes on a running VMI so the VM survives planned guest agent downtime
  - *Test Scenario:* Verify VMI stays Running after guest agent stop with pause annotation
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P0
  - *Test ID:* CNV82132-001
  - *Upstream coverage:* kubevirt/kubevirt#19076 -- full (VMI held Running with agent stopped while paused)
  - *Coverage gap:* No assertion that the virt-launcher pod is not restarted across pause/resume, against the "without Pod restart" acceptance criterion
  - *Gap resolution:* upstream
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want to perform a complete maintenance workflow with probes paused throughout
  - *Test Scenario:* Verify happy-path maintenance return to service with probes paused for the maintenance window, then normal probe behavior after unpause.
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P1
  - *Covered upstream (kubevirt):* CNV82132-001 in `tests/compute/guest_agent_probe_pause.go` -- pause annotation, stop guest agent while paused, VMI stays Running with no `GuestAgentPingFailed`; remove annotation while the agent is still stopped and assert liveness failure and events resume. CNV82132-002 covers readiness stability while paused with a dead agent. Neither restarts the guest agent or asserts a healthy VM after unpause. Credential injection is not exercised while the agent is stopped (expected unavailable until the agent is restored).
  - *Pending (Tier 2 downstream):* End-to-end workflow: set pause on a running workload, stop guest agent for maintenance, confirm VM stays up with probes suppressed, restart guest agent and confirm `AgentConnected`, remove pause (or set annotation to `false`), then assert VMI `Running`, readiness/liveness GuestAgentPing probes healthy, and no erroneous `GuestAgentPingFailed` during the paused window.
  - *Downstream required:* yes


- **[CNV-82132]** -- As a VM admin, I want to resume normal probe behavior by removing the annotation
  - *Test Scenario:* Verify probes resume and VMI is failed after annotation removal with the guest agent still stopped
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P0
  - *Test ID:* CNV82132-001 (second half -- annotation removed on the running VMI, agent still stopped)
  - *Upstream coverage:* kubevirt/kubevirt#19076 -- full (VMI terminates and GuestAgentPingFailed events resume after removal)
  - *Coverage gap:* Resume by setting the annotation to `"false"` rather than removing it is not exercised at e2e (`ParseBool` treats both as unpaused)
  - *Gap resolution:* upstream
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want GuestAgentPing readiness probes paused so the VMI stays Ready while the agent is down
  - *Test Scenario:* Verify VMI remains Ready with paused readiness probes
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1
  - *Test ID:* CNV82132-002
  - *Upstream coverage:* kubevirt/kubevirt#19076 -- full (VMI holds the Ready condition for the paused window with the agent stopped)
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want non-GuestAgentPing probes (exec, TCP, HTTP) unaffected by the annotation
  - *Test Scenario:* Verify exec probe fires normally with pause annotation set
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1
  - *Test ID:* CNV82132-003 (in `tests/compute/guest_agent.go`)
  - *Upstream coverage:* kubevirt/kubevirt#19076 -- full (CNV82132-003: exec liveness still fails with the annotation set; pause only short-circuits GuestAgentPing in virt-launcher — HTTP and TCP stay normal kubelet probes on the compute container and never use that path)
  - *Downstream required:* no


- **[CNV-82392]** -- As a VM admin, I want the pause annotation to propagate during live migration so probes remain paused on the target node
  - *Test Scenario:* Verify VMI is never failed during or after live migration with pause annotation set
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1
  - *Test ID:* CNV82132-004
  - *Upstream coverage:* kubevirt/kubevirt#19076 -- full (pause confirmed on the target launcher, then VMI held Running for one full initialDelay + failureThreshold x period window plus margin)
  - *Downstream required:* no


- **[CNV-82392]** -- As a VM admin, I want to perform maintenance on a migrated VM with probes remaining paused throughout
  - *Test Scenario:* Verify end-to-end maintenance on a live-migrated workload: probes stay paused through migration and maintenance, then normal probe behavior after unpause on the target node.
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P1
  - *Covered upstream (kubevirt):* CNV82132-004 in `tests/compute/guest_agent_probe_pause.go` (kubevirt/kubevirt#19076) -- pause annotation, stop guest agent, live migrate, confirm pause propagates on the target virt-launcher, VMI stays Running through the probe kill window; unpause with agent still stopped and assert liveness failure. Uses containerdisk Fedora VMI only; does not restart the guest agent or assert a healthy VM after maintenance on the target.
  - *Pending (Tier 2 downstream):* Product QE workflow on a migrated VM (e.g. PVC-backed VM where required): pause probes, migrate, perform maintenance on the target (guest agent down), confirm VM stays up with probes suppressed on the target, restart guest agent on the target, remove pause, then assert `Running`, `AgentConnected`, and GuestAgentPing readiness/liveness healthy with no spurious `GuestAgentPingFailed` during the paused window.
  - *Downstream required:* yes


- **[CNV-82132]** -- As a VM admin, I want the annotation-based pause and live migration probe suppression to work independently
  - *Test Scenario:* Verify annotation pause and live migration probe behavior operate independently
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1
  - *Test ID:* CNV82132-004 (resume-on-target control step)
  - *Upstream coverage:* kubevirt/kubevirt#19076 -- partial (resuming probes on the target fails the VMI, showing migration-time suppression had already ended and the survival was attributable to the annotation)
  - *Coverage gap:* Pausing or unpausing while a migration is in flight is not covered
  - *Gap resolution:* upstream
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want GuestAgentPingFailed events suppressed while probes are paused so monitoring dashboards are not polluted
  - *Test Scenario:* Verify no GuestAgentPingFailed events during probe pause
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1
  - *Test ID:* CNV82132-001
  - *Upstream coverage:* kubevirt/kubevirt#19076 -- full (events cleared after pause, `ExpectNoEvent` while paused, `ExpectEvent` after resume)
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want the annotation honored when it is present at VMI creation, not only when patched onto a running VMI
  - *Test Scenario:* Verify a VMI created with the annotation already set has guest-agent probes paused before GuestAgentPing liveness can fail the VMI
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2
  - *Test ID:* CNV82132-003 (incidental -- the exec-probe spec sets the annotation via `libvmi.WithAnnotation` at create time)
  - *Upstream coverage:* kubevirt/kubevirt#19076 -- partial (the create-time path is exercised, but the assertion is about the exec probe firing, not about GuestAgentPing being paused)
  - *Coverage gap:* No spec asserts GuestAgentPing suppression for a VMI that carried the annotation from creation
  - *Gap resolution:* upstream
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want access credential injection to continue working while probes are paused and the guest agent is connected
  - *Test Scenario:* Verify SSH key injection succeeds with pause annotation set while qemu-guest-agent is connected; expect injection to fail or be deferred while the agent is stopped for maintenance (independent of probe pause)
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1
  - *Upstream coverage:* none -- not in analyzed PR(s)
  - *Coverage gap:* No e2e asserts credential injection with annotation set and agent connected; maintenance workflows that stop the agent are out of scope for this requirement (agent unavailable independent of probe pause)
  - *Gap resolution:* upstream
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want the annotation to accept standard boolean values and treat invalid values as false (probes resume)
  - *Test Scenario:* Verify annotation accepts standard boolean values and treats invalid values as false (probes not paused)
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2
  - *Upstream coverage:* kubevirt/kubevirt#17664 -- full via upstream unit tests (boolean and invalid annotation values). Cluster e2e uses `"true"` and annotation removal for pause/unpause; no dedicated e2e per ParseBool variant.
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want probe pausing available without enabling a feature gate
  - *Test Scenario:* Verify probe pause works with default cluster configuration and no feature gate enabled
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2
  - *Test ID:* CNV82132-001, -002, -003, -004
  - *Upstream coverage:* kubevirt/kubevirt#19076 -- full (all four specs run against default cluster configuration with no feature gate)
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want the annotation to persist and probes to remain paused across multiple reconciliation cycles
  - *Test Scenario:* Verify probes remain paused across repeated virt-handler reconciliation with no annotation change
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2
  - *Upstream coverage:* kubevirt/kubevirt#19076 -- full (implicit in CNV82132-001, -002, and -004; pause held 45–60+ seconds while virt-handler reconciles the VMI; failure to persist pause would cause immediate liveness failure)
  - *Downstream required:* no


- **[CNV-82132]** -- As a VM admin, I want snapshot operations to use their own probe suppression independently of this annotation
  - *Test Scenario:* Verify VM snapshot completes successfully and VMI remains Running with probe pause annotation set
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P2 (valid edge case)
  - *Upstream coverage:* none -- not in analyzed PR(s)
  - *Downstream required:* yes


- **[CNV-82132]** -- As a VM admin, I want the annotation-based pause to coexist with VM pause/unpause probe suppression
  - *Test Scenario:* Verify annotation pause remains effective through a VM Pause/Unpause cycle (annotation pause independent of user VM pause probe suppression).
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P2
  - *Covered upstream (kubevirt):* CNV82132-001 (annotation only); `guest_agent.go` user-paused VMI test (VM Pause only). No spec uses both on one VMI (kubevirt/kubevirt#19076).
  - *Pending (Tier 2 downstream):* On a running VMI with GuestAgentPing liveness, set `kubevirt.io/pause-guest-agent-probes=true`, Pause then Unpause via API; assert VMI stays Running and annotation pause still suppresses probes (e.g. stop guest agent after unpause while annotation remains set, VMI survives); remove annotation and verify normal probe behavior with a healthy guest agent.
  - *Gap resolution:* downstream (Tier 2); optional future upstream e2e
  - *Downstream required:* yes


---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE (sig-infra): Roni Kishner (@RoniKishner)
  - Development: Karel Simon (@ksimon1)
  - QE Architect (OCP-V): Ruth Netser (@rnetser)
* **Approvers:**
  - QE Lead / QE Architect (OCP-V): Ruth Netser (@rnetser)
  - Dev Lead: Karel Simon (@ksimon1)
  - Product Manager: Ronen Sde-Or (@ronensdeor)
