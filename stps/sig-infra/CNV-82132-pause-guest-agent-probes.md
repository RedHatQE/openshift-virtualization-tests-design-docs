# Openshift-virtualization-tests Test plan

## **Annotation-Based GuestAgentPing Probe Pausing (VEP 207) - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP 207 -- Manual GuestAgentPing probe control](https://github.com/kubevirt/enhancements/pull/208)
- **Feature Tracking:** [VIRTSTRAT-563 -- Ability to ignore Liveness/Readiness probes during VM maintenance](https://redhat.atlassian.net/browse/VIRTSTRAT-563)
- **Epic Tracking:** [CNV-82132 -- GA: Implement pause probe functionality](https://redhat.atlassian.net/browse/CNV-82132)
- **Implementation PR:** [kubevirt/kubevirt#17664 -- virt-launcher annotation handling + unit tests](https://github.com/kubevirt/kubevirt/pull/17664)
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: 4.23/5.0
- **QE Owner(s):** Geetika Kapoor(@geetikakay)
- **Owning SIG:** sig-infra
- **Participating SIGs:** N/A

### **Feature Overview**

OpenShift Virtualization 4.23/5.0 introduces annotation-based GuestAgentPing probe pausing, designed per VEP 207. This feature is GA in 4.23/5.0 and this STP covers the GA phase. VM administrators can temporarily pause GuestAgentPing-based liveness and readiness probes on running VirtualMachineInstances by setting the `kubevirt.io/pause-guest-agent-probes` annotation. While paused, GuestAgentPing reports success, so the VM is not restarted and its readiness does not drop solely because the guest agent is down. Removing the annotation (or setting it to a non-true value) resumes normal probe behavior. The annotation is independent of existing GuestAgentPing suppression during live migration and user VM pause (those paths still apply when the annotation is not set).

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
  - All four acceptance criteria are covered by test scenarios that validate the expected behavior: enabling and disabling GuestAgentPing probe pausing through annotation changes, ensuring other probe types remain unaffected, verifying that annotation-based pausing works independently of existing GuestAgentPing suppression mechanisms and confirming that the annotation and its behavior are preserved during live migration.

- [x] **Acceptance Criteria**
  - Derived from VEP 207 goals:
    - Manual pause/unpause of GuestAgentPing probes via VMI annotations without requiring a virt-launcher pod restart
    - Annotation-based pause operates independently of existing probe suppression mechanisms (live migration, VM pause)
    - Non-GuestAgentPing probes (TCP, HTTP, Exec) are unaffected
    - Annotation removal resumes normal probe behavior

- [x] **Non-Functional Requirements (NFRs)**
  - **UI:** No UI changes (no-ui, no-ux labels). Annotation-based manual control only; no customer-facing UI testing planned unless PM/UX identifies value.
  - **Monitoring:** No new metrics or alerts required. Once virt-launcher applies the pause,  `GuestAgentPingFailed` events are not emitted, so existing dashboards may show gaps during maintenance windows. No API field, condition or metric reports the pause state.
  - **Observability:** While probes are paused, `GuestAgentPingFailed` events are not emitted (temporary gap in guest-agent connectivity signals). Operators should treat paused probes as an intentional blind spot during planned maintenance. Monitoring team awareness covered in Cross Integrations (II.2).
  - **Documentation:** Documentation changes are merged.
  - **Performance:** Per-VMI annotation lookup with negligible performance impact (see #17664). No latency or throughput requirements.
  - **Security:** Standard VMI annotation governed by existing Kubernetes RBAC. No new permission model or security boundary; users with VMI patch permissions can set or remove the annotation.
  - **Scalability:** No new per-VMI scale requirements -- annotation operates independently on each VMI. Maintenance workflows that combine probe pause with live migration (CNV-82392) inherit existing cluster-level live migration parallelism limits; cluster admins should plan maintenance windows accounting for live migration concurrency when migrating paused VMIs.

#### **2. Known Limitations**

The following are confirmed product constraints accepted before testing begins.

- **Annotation is never auto-applied**
  - KubeVirt does not set `kubevirt.io/pause-guest-agent-probes` during snapshots, migrations, or other internal operations. The user or external tooling must set it.
  - *Sign-off:* Ronen / Karel / 2026-Sep-03

- **Coexistence with live-migration probe suppression (#17235)**
  - During live migration, GuestAgentPing errors can still be suppressed by a separate mechanism ([kubevirt/kubevirt#17235](https://github.com/kubevirt/kubevirt/pull/17235)), independent of this annotation. Operators who need probes paused through maintenance that includes migration must still set the pause annotation on the VMI (migration-only suppression ends when migration completes).
  - *Sign-off:* Ronen / Karel / 2026-Sep-03

- **Guest-exec and access credentials are not suppressed**
  - The annotation does not suppress guest-exec. Access credential injection and other guest-agent operations still require a reachable qemu-guest-agent. Probe pause does not block them when the agent is connected; stopping the agent for maintenance makes them unavailable for the same reasons as without the annotation.
  - *Sign-off:* Ronen / Karel / 2026-Sep-03

- **GuestAgentPing probes only (no HTTP, TCP, or Exec pause)**
  - VEP 207 limits pause scope to GuestAgentPing probes. HTTP, TCP, and Exec liveness/readiness probes are unaffected by the annotation and continue to run normally.
  - *Sign-off:* Ronen / Karel / 2026-Sep-03

- **Manual pause only (no automatic scheduling or expiry)**
  - The annotation is manual-only. The product does not automatically pause probes on a schedule or time out pause after a maintenance window.
  - *Sign-off:* Ronen / Karel / 2026-Sep-03

- **Per-VMI annotation (no batch or selector API)**
  - Pause is controlled per VMI via annotation patch. There is no KubeVirt API to pause probes for multiple VMIs via label selector, CronJob, or similar bulk mechanism.
  - *Sign-off:* Ronen / Karel / 2026-Sep-03

- **No upstream Kubernetes probe suspension (KEP 5002)**
  - Probe pause is implemented via the KubeVirt annotation only. Upstream Kubernetes probe suspension ([KEP 5002](https://github.com/kubernetes/enhancements/issues/5002)) is not part of this product behavior.
  - *Sign-off:* Ronen / Karel / 2026-Sep-03

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - `GuestAgentPingFailed` events are suppressed during pause -- monitoring gap identified.

- [x] **Technology Challenges** (implementation detail: [kubevirt/kubevirt#17664](https://github.com/kubevirt/kubevirt/pull/17664), [VEP 207](https://github.com/kubevirt/enhancements/pull/208))
  - **Annotation change vs. next probe (VEP 207):** A VMI patch does not guarantee the very next kubelet GuestAgentPing cycle sees pause already active on virt-launcher. *Observable consequence:* Brief window where behavior may still reflect the prior state; after pause is active, liveness/readiness must not fail the VMI solely because the guest agent is down. *Test approach:* pause, stop the agent and hold the VMI Running past the liveness failure window with no `GuestAgentPingFailed`.
  - **Coexistence with other probe suppression (VEP acceptance):** Annotation pause must not break existing suppression during live migration or user-initiated VM pause. Annotation skip and migration/VM-pause error suppression are independent: if the annotation is set, GuestAgentPing does not run; if it is not set, migration and healthy-paused-domain suppression still apply. *Observable consequence:* VMI stays Running when pause applies on the migration target with a dead agent; VM pause without annotation still suppresses probe kills. *Test approach:* migration target scenario; existing VM pause probe suppression tests (without the annotation); combined annotation + VM pause as a Tier 2 scenario.
  - **Pause on migration target (CNV-82392):** After live migrate, pause may not be effective on the target pod until virt-launcher has applied the annotation from the VMI. *Observable consequence:* Without waiting for pause to be active, tests could false-pass while migration-only suppression still applies. *Test approach:* wait for virt-launcher log confirmation of the pause on the target, then hold Running through the probe kill window; unpause with the agent still stopped proves the annotation drove survival.
  - **Monitoring blind spot during pause:** Paused GuestAgentPing probes report success and do not emit `GuestAgentPingFailed` even when the agent is unhealthy. *Observable consequence:* Event stream gap during maintenance; events resume after unpause when probes run again. *Test approach:* check no events while paused and events after unpause.

- [x] **Test Environment Needs**
  - Guest agent (qemu-guest-agent) must be installed and running in test VM images. Live migration tests need **>=2 schedulable nodes** for VM workloads; Tier 1 migration scenarios use containerdisk and need no RWX storage. RWX (or equivalent live-migratable shared storage) applies only when testing migration of **PVC-backed** VMIs (Tier 2).

- [x] **API Extensions**
  - New annotation `kubevirt.io/pause-guest-agent-probes` on VMI. Setting it to a true value pauses GuestAgentPing probes. Removing the annotation or setting a non-true value resumes normal probe behavior. No new CRDs, API endpoints, or feature gates introduced.

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
- **P1:** Verify that non-GuestAgentPing probes are unaffected by the annotation
- **P1:** Verify that the pause annotation remains effective on the migration target so probes stay paused after live migration
- **P1:** Verify that probe pause coexists with live migration probe suppression (annotation effective on migration target; independent of #17235-only suppression)
- **P1:** Verify that access credential injection is not blocked by probe pause when the guest agent is connected (annotation does not suppress guest-exec)
- **P1:** Verify that with the guest agent stopped, access credential injection does not complete and reflects agent unavailability while probe pause is active (probe pause does not mask guest-exec dependency)
- **P1:** Verify that GuestAgentPingFailed events are suppressed during probe pause
- **P1:** Verify a complete maintenance workflow (pause, stop agent, restart agent, unpause), ending in a healthy VM after unpause
- **P1:** Verify a complete maintenance workflow on a live-migrated VM, ensuring probes stay paused through migration and return to service on the target node
- **P2:** Verify annotation pause remains effective through a VM Pause/Unpause cycle on the same VMI (stacked workflow)
- **P2:** Verify annotation value handling (boolean and invalid values)
- **P2:** Verify annotation persistence and snapshot coexistence
- **P2:** Verify that probes are paused when the annotation is present at VMI creation
- **P2:** Verify that probe pause functionality is available with default cluster configuration (no feature gate)

**Out of Scope (Testing Scope Exclusions)**

QE intentionally does not test the following in this cycle (product may support related behavior elsewhere or the mechanism is OS-agnostic).

- **Standalone validation of live migration probe suppression (kubevirt/kubevirt#17235)**
  - *Rationale:* Separate feature and upstream test coverage; this STP only verifies annotation propagation on the migration target and coexistence
  - *PM/Lead Agreement:* Ronen / Karel / 2026-Sep-03

- **Windows guest OS update scenarios**
  - *Rationale:* OS-specific maintenance validation deferred; annotation mechanism is OS-agnostic and covered on Linux guest images in Tier 1/2
  - *PM/Lead Agreement:* Ronen / Karel / 2026-Sep-03

**Test Limitations**

- **Sub-probe-cycle timing (annotation patch vs. GuestAgentPing)**
  - *Rationale:* E2e cannot force kubelet to run GuestAgentPing in a specific window relative to a VMI annotation patch. Kubernetes API patches cannot toggle fast enough to hit the sub-probe-cycle window between virt-launcher applying the annotation and kubelet's next GuestAgentPing; repeated e2e toggles would not create a deterministic race reproducer. Coverage is outcome-based (VMI phase, Ready, events, long pause holds) and supplemented by kubevirt/kubevirt#17664 unit tests -- not a deterministic interleaving test.
  - *Sign-off:* Ronen / Karel / 2026-Sep-03

- **Probe-pause state observability in cluster tests**
  - *Rationale:* No VMI condition or API field reports annotation-driven probe pause. Tier 1 tests confirm pause reached virt-launcher via a log substring until a supported observability signal exists (see Section I Monitoring NFR).
  - *Sign-off:* Ronen / Karel / 2026-Sep-03

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** -- Validates that the feature works according to specified requirements and user stories
  - *Details:* Tier 1 tests verify core probe pause/resume lifecycle, readiness probe pausing, probe type isolation, annotation value handling, event suppression. Access credential injection with a connected guest agent is Tier 2 downstream. All Tier 1 tests in Go/Ginkgo.
- [x] **Automation Testing** -- Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All tests automated. Tier 1 tests in Go/Ginkgo; Tier 2 tests in Python/pytest cover end-to-end maintenance and migration workflows.
- [x] **Regression Testing** -- Verifies that new changes do not break existing functionality
  - *Details:* Regression analysis identified 9 impacted features. Existing tests for these areas are re-run on the feature build:
    - **Liveness probes:** existing GuestAgentPing liveness probe tests
    - **Readiness probes:** existing GuestAgentPing readiness probe tests
    - **Event generation:** existing `GuestAgentPingFailed` event checks in probe tests
    - **Live migration suppression:** existing live migration tests with GuestAgentPing liveness probes
    - **VMI reconciliation:** existing VMI lifecycle tests
    - **Access credential injection:** existing access credentials tests
    - **VM pause:** existing VM pause/unpause tests
    - **Exec probes:** existing exec probe tests
    - **Snapshots:** existing VM snapshot tests
- [ ] **Self-Validation Testing** -- Should any of the new tests be included in the self-validation test package?
  - *Details:* N/A. The feature is a manual annotation toggle, not a core operational scenario. Self-validation tests target always-on product health checks. Probe pausing is user-initiated and situational.

**Non-Functional**

- [ ] **Performance Testing** -- Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* N/A. Per-VMI annotation with negligible performance impact. No latency or throughput requirements.
- [ ] **Scale Testing** -- Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* N/A for dedicated scale testing. Annotation operates per-VMI with no new aggregate scaling concern. Live migration scenarios (CNV-82392) inherit existing cluster-level migration parallelism limits; no additional scale validation beyond functional coverage is planned.
- [ ] **Security Testing** -- Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* N/A. Annotation is a standard VMI annotation governed by existing Kubernetes RBAC. No new permission model or security boundary introduced.
- [ ] **Usability Testing** -- Validates user experience and accessibility requirements
  - *Details:* N/A. Feature has no UI (no-ui, no-ux labels). Annotation-based interface documented in upstream user guide (kubevirt/user-guide#990).
- [ ] **Monitoring** -- Does the feature require metrics and/or alerts?
  - *Details:* N/A. No new metrics or alerts introduced. Note: GuestAgentPingFailed events are suppressed during probe pause, which may affect existing monitoring dashboards.

**Integration & Compatibility**

- [x] **Compatibility Testing** -- Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Annotation accepts strconv.ParseBool values for input flexibility. No feature gate required, ensuring compatibility with default cluster configurations.
- [ ] **Upgrade Testing** -- Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Upgrade path evaluated: annotation is standard VMI metadata in etcd and survives upgrades like any Kubernetes annotation. No dedicated feature-specific upgrade test in this STP; standard product upgrade testing applies. Pause effectiveness across virt-handler/virt-launcher reconciles is covered implicitly by the pause scenarios (pause held 45-60+ seconds).
- [x] **Dependencies** -- Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* None identified. Implementation PR (kubevirt/kubevirt#17664) is merged. No team delivery dependencies.
- [x] **Cross Integrations** -- Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* Monitoring teams should be aware that GuestAgentPingFailed events are suppressed during probe pause. Snapshot and user VM pause use separate probe-suppression behavior; coexistence with annotation pause is covered by P2 Tier 2 scenarios.

**Infrastructure**

- [ ] **Cloud Testing** -- Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* N/A. Feature is platform-agnostic with no cloud-specific dependencies.

#### **3. Test Environment**

- **Cluster Topology:** Any supported single-cluster deployment where VM workloads can be scheduled. Non-migration Tier 1 scenarios run on a single schedulable node. Live migration scenarios (Tier 1 and Tier 2) require **at least two schedulable nodes** that can run VMIs on different hosts; control-plane/worker layout is not prescribed.
- **OCP & OpenShift Virtualization Version(s):** OCP 4.23+ / OpenShift Virtualization 4.23 (CNV 4.23.0) and OCP 5.0+ / OpenShift Virtualization 5.0 (CNV 5.0.0)
- **CPU Virtualization:** Standard (no nested virtualization or special CPU features required)
- **Compute Resources:** Standard (sufficient for 2+ concurrent VMIs with guest agents running)
- **Special Hardware:** None required
- **Storage:** Tier 1 live migration scenarios use **containerdisk**-backed Fedora VMIs and do **not** require shared or RWX volumes. Use a storage class with **ReadWriteMany** access (and volume mode suitable for live-migratable PVCs, e.g. block RWX on ODF) only for scenarios that **live-migrate PVC-backed** VMIs (Tier 2 downstream / product workflows).
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

- [x] **Timeline/Schedule**
  - Mitigation: No schedule risks identified. The feature implementation is merged; Tier 2 automation is developed in parallel with the STP.

- [x] **Test Coverage**
  - Risk: Sub-probe-cycle timing between VMI annotation patch and the next GuestAgentPing is non-deterministic and cannot be forced from e2e.
  - Mitigation: Pause scenarios hold the VMI long enough that a failure to apply pause would surface as liveness or readiness failure; the migration scenario confirms the pause on the target before checking survival.
  - *Areas with reduced coverage:* Exact interleaving of a single probe with an in-flight annotation patch.
  - *PM/DEV Sign-off:* Ronen / Karel / 2026-Sep-03

- [x] **Test Environment**
  - Risk: Guest agent availability and behavior may vary across OS images and versions.
  - Mitigation: Use standard Fedora images with known qemu-guest-agent versions for consistent test results.
  - *Missing or unavailable environments:* None. Standard Fedora images with guest agent are available.
  - *PM/DEV Sign-off:* Ronen / Karel / 2026-Sep-03

- [x] **Untestable Aspects**
  - Risk: Sub-probe-cycle timing between annotation patch and GuestAgentPing cannot be forced from a test.
  - Mitigation: The migration scenario waits for virt-launcher log confirmation that pause is active on the target, then checks the VMI stays Running; removing pause with the agent still stopped proves probes resumed. Implementation concurrency is covered by unit tests in #17664 and design review.
  - *Reason untestable and mitigation approach:* Kubelet probe schedule cannot be interleaved with API patch from e2e. Observable VMI phase, Ready, and events validate the operator-visible result.
  - *PM/DEV Sign-off:* Ronen / Karel / 2026-Sep-03

- [x] **Resource Constraints**
  - Mitigation: No resource constraints identified. Feature testing uses standard test infrastructure with no additional staffing or hardware requirements.

- [x] **Dependencies**
  - Mitigation: No dependencies. Implementation PR (kubevirt/kubevirt#17664) is merged with no pending team delivery dependencies.

- [x] **Other**
  - Risk: Monitoring dashboards relying on GuestAgentPingFailed events may need updates to account for event suppression during probe pause.
  - Mitigation: Document event suppression behavior. Monitoring team awareness covered in Cross Integrations (II.2).
  - *PM/DEV Sign-off:* Ronen / Karel / 2026-Sep-03

---

### **III. Test Scenarios & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are tested.

#### **1. Requirements-to-Tests Mapping**

- **[CNV-82132]** -- As a VM admin, I want to pause GuestAgentPing liveness probes on a running VMI so the VM survives planned guest agent downtime
  - *Test Scenario:* Verify that with the annotation set and the guest agent stopped the VMI stays Running past the liveness failure window, and is failed once the annotation is removed
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P0

- **[CNV-82132]** -- As a VM admin, I want to perform a complete maintenance workflow with probes paused throughout
  - *Test Scenario:* Verify happy-path maintenance return to service with probes paused for the maintenance window, then normal probe behavior after unpause (guest agent restarted and `AgentConnected`, VMI `Running` with GuestAgentPing readiness/liveness probes healthy, no `GuestAgentPingFailed` during the paused window, virt-launcher pod UID unchanged across the cycle).
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P1

- **[CNV-82132]** -- As a VM admin, I want GuestAgentPing readiness probes paused so the VMI stays Ready while the agent is down
  - *Test Scenario:* Verify VMI remains Ready with paused readiness probes
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1

- **[CNV-82132]** -- As a VM admin, I want non-GuestAgentPing probes (exec, TCP, HTTP) unaffected by the annotation
  - *Test Scenario:* Verify exec probe fires normally with pause annotation set
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1

- **[CNV-82392]** -- As a VM admin, I want the pause annotation to propagate during live migration so probes remain paused on the target node
  - *Test Scenario:* Verify that with the annotation set and the guest agent stopped, the VMI stays Running on the target node past the liveness failure window after migration, and is failed once the annotation is removed
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1

- **[CNV-82392]** -- As a VM admin, I want to perform maintenance on a migrated VM with probes remaining paused throughout
  - *Test Scenario:* Verify end-to-end maintenance on a live-migrated workload: probes stay paused through migration and maintenance, then normal probe behavior after unpause on the target node (guest agent restarted and `AgentConnected`, VMI `Running` with GuestAgentPing readiness/liveness probes healthy, no `GuestAgentPingFailed` during the paused window).
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P1

- **[CNV-82132]** -- As a VM admin, I want GuestAgentPingFailed events suppressed while probes are paused so monitoring dashboards are not polluted
  - *Test Scenario:* Verify no GuestAgentPingFailed events during probe pause
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P1

- **[CNV-82132]** -- As a VM admin, I want the annotation honored when it is present at VMI creation, not only when patched onto a running VMI
  - *Test Scenario:* Verify a VMI created with the annotation already set has guest-agent probes paused before GuestAgentPing liveness can fail the VMI
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2

- **[CNV-82132]** -- As a VM admin, I want access credential injection to continue working while probes are paused and the guest agent is connected
  - *Test Scenario:* With `kubevirt.io/pause-guest-agent-probes=true` and the VMI reporting guest agent connected, inject an SSH public key via access credentials and assert injection completes (credential present in the guest, e.g. via guest-exec or successful SSH authentication).
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P1

- **[CNV-82132]** -- As a VM admin, I want access credential injection to reflect guest agent unavailability when the agent is stopped (independent of probe pause)
  - *Test Scenario:* With `kubevirt.io/pause-guest-agent-probes=true`, stop qemu-guest-agent in the guest and assert access credential injection does not complete within the test timeout; assert the VMI reports guest agent not connected (or equivalent agent-unavailable signal). Probe pause must not cause injection to succeed while the agent is down.
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P1

- **[CNV-82132]** -- As a VM admin, I want the annotation to accept standard boolean values and treat invalid values as false (probes resume)
  - *Test Scenario:* Verify annotation accepts standard boolean values and treats invalid values as false (probes not paused)
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2

- **[CNV-82132]** -- As a VM admin, I want probe pausing available without enabling a feature gate
  - *Test Scenario:* Verify probe pause works with default cluster configuration and no feature gate enabled
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2

- **[CNV-82132]** -- As a VM admin, I want the annotation to persist and probes to remain paused across multiple reconciliation cycles
  - *Test Scenario:* With `kubevirt.io/pause-guest-agent-probes` unchanged and the guest agent stopped, hold the VMI for 45-60+ seconds; pass when no `GuestAgentPingFailed` events are emitted and the VMI remains Running throughout the window
  - *Tier:* Tier 1 (Functional)
  - *Priority:* P2

- **[CNV-82132]** -- As a VM admin, I want snapshot operations to use their own probe suppression independently of this annotation
  - *Test Scenario:* Verify VM snapshot completes successfully and VMI remains Running with probe pause annotation set
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P2 (valid edge case)

- **[CNV-82132]** -- As a VM admin, I want the annotation-based pause to coexist with VM pause/unpause probe suppression
  - *Test Scenario:* Verify annotation pause remains effective through a VM Pause/Unpause cycle (annotation pause independent of user VM pause probe suppression).
  - *Tier:* Tier 2 (End-to-End)
  - *Priority:* P2

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
