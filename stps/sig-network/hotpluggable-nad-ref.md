# Openshift-virtualization-tests Test plan

## **Live Update NetworkAttachmentDefinition Reference  - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** https://github.com/kubevirt/enhancements/blob/main/veps/sig-network/hotpluggable-nad-ref.md
- **Feature Tracking:** https://issues.redhat.com/browse/VIRTSTRAT-560
- **Epic Tracking:** https://redhat.atlassian.net/browse/CNV-72329
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: 4.22
- **QE Owner(s):** Asia Khromov (@azhivovk)
- **Owning SIG:** sig-network
- **Participating SIGs:** sig-network

**Document Conventions (if applicable):**
- NAD = NetworkAttachmentDefinition, a Multus secondary network definition

### **Feature Overview**

This feature enables VM owners to change the secondary network of a running VM without rebooting and without any change in the guest interfaces. When the user updates the network reference in the VM configuration, the VM is reconnected to the new network (e.g. a different VLAN) while the guest OS sees no interface change.

The supported scope is bridge binding on live-migratable VMs.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:* Change the secondary network of a running VM without requiring a restart and without any change in the guest interfaces.

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* VM owners can re-assign new networks (e.g. a different VLAN) to VMs without reboot and without any change to the guest interface, avoiding workload impact.
  - *List the customer use cases identified:*
    - As a VM owner, I want to re-assign my VM to a different VLAN without rebooting so that my VM connects to the new network without requiring a restart. Note: guest network configuration (e.g. IP) may need to be adjusted manually after the reassignment.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* Core flow is testable (see III. Test Scenarios & Traceability).

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - The VM remains running (not rebooted) after changing the secondary network (e.g. VLAN change)
    - The VM establishes connectivity on the new secondary network (new VLAN)
    - The VM no longer has connectivity on the previous secondary network (previous VLAN)
    - The guest interface and its (IP) configuration is preserved during the transition
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Documentation: update required.
    - Monitoring/Observability: no new metrics or alerts required. The existing VM network interface info metric is validated to confirm it reflects the updated network attachment after the swap (see P1 testing goal and Section III scenario).
    - UI: no new UI components introduced, but existing VM network display is validated by the UI team (see Usability Testing in Section II.2).
  - *Note any NFRs not covered and why:*
    - Performance: no new performance requirements introduced.
    - Security: no new RBAC or authentication changes.
    - Scalability: the feature has scale implications — large-scale NAD reference updates are throttled by the cluster's migration parallelism limits. This is not tested (see Out of Scope, Section II.1). Documentation should reflect this limitation.

#### **2. Known Limitations**

- **Non-migratable VMs:** Changing the secondary network on non-migratable VMs is not supported; the VM will not reconnect to the new network without a restart.
  - *Sign-off:* Ronen Sde-Or, 04/2026

- **Binding support:** Secondary network reassignment is supported for bridge binding only; other binding types are not in scope for this feature.
  - *Sign-off:* Ronen Sde-Or, 04/2026

- **Guest network config:** Feature does not change guest-side configuration; guest may need separate reconfiguration for new network (e.g. IP).
  - *Sign-off:* Ronen Sde-Or, 04/2026

- **Single-node clusters (SNO):** Cannot be supported because migration is not possible.
  - *Sign-off:* Ronen Sde-Or, 04/2026

- **Migrating between CNI types:** Not supported; only same-CNI-type reassignment is allowed.
  - *Sign-off:* Ronen Sde-Or, 04/2026

- **Changing network binding/plugin:** Not supported.
  - *Sign-off:* Ronen Sde-Or, 04/2026

- **Seamless network connectivity until action is completed:** Not guaranteed by design. After the NAD update completes, connectivity is expected to be preserved without guest intervention, except when the new network requires explicit guest-side reconfiguration (e.g. IP change).
  - *Sign-off:* Ronen Sde-Or, 04/2026

- **Limiting migration retries on failure:** Not supported.
  - *Sign-off:* Ronen Sde-Or, 04/2026


#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Reconnection is done via live migration.
    - Guest interface configuration is preserved by design.
    - If migration fails, the VM remains on the original network; no rollback needed.

- [x] **Technology Challenges**
  - *List identified challenges:* The feature relies on live migration, which is not supported on all cluster topologies (e.g. single-node clusters), limiting the environments in which this feature can be tested.
  - *Impact on testing approach:* Tests must run on multi-node clusters where live migration is available.

- [x] **API Extensions**
  - *List new or modified APIs:* No new APIs introduced by this feature.
  - *Testing impact:* N/A

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Tests require a multi-node cluster with live migration available (minimum 2 worker nodes). SNO is excluded — the feature does not support it (see Known Limitations, Section I.2).
  - *Impact on test design:* All test scenarios must run on multi-node clusters; SNO environments are not valid test targets.

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify that a running VM with bridge binding on a Linux bridge CNI secondary network can be reconnected to a different secondary network without rebooting, has connectivity on the new network, and is no longer reachable on the previous network.
- **[P1]** Verify that a running VM connected to a localnet secondary network can be reconnected to a different localnet network without rebooting and has connectivity on the new network.
- **[P1]** Verify that when NAD references for multiple bridge binding on Linux bridge CNI secondary network interfaces on the same running VM are updated at once, all interfaces establish connectivity on their respective new networks.
- **[P1]** Verify that attempting to change the secondary network VLAN on a non-migratable VM with bridge binding on a Linux bridge CNI secondary network does not succeed, and the VM remains on the original network.
- **[P1]** Verify that a running VM with bridge binding on a Linux bridge CNI secondary network has its network interface monitoring data updated to reflect the new network attachment after reassignment.

**Out of Scope (Testing Scope Exclusions)**

- **Large-scale concurrent NAD reference updates**
  - *Rationale:* Changing NADs on many VMs simultaneously is throttled by the cluster's migration parallelism limits and may take extended time to stabilize. No scale requirements are defined for this feature, and testing at scale is not feasible within the current lab capacity. Feature documentation should reflect this limitation.
  - *PM/Lead Agreement:* Ronen Sde-Or, 04/2026

**Test Limitations**

None — reviewed and confirmed that no test limitations apply for this release.

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Validate NAD reference update on running VMs with bridge binding; verify connectivity on new network and absence of connectivity on previous network.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All new test scenarios will be automated and integrated into the standard CI lane.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Existing secondary network and live migration test suites will run as regression to confirm no impact.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Not applicable; no new performance requirements introduced for this feature.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* Not applicable; no new scale requirements introduced for this feature.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization
  - *Details:* Not applicable; no new RBAC or authentication changes introduced.

- [x] **Usability Testing** — Validates user experience and accessibility requirements
  - Does the feature require a UI? If so, ensure the UI aligns with the requirements (UI/UX consistency, accessibility)
  - Does the feature expose CLI commands? If so, validate usability and that needed information is available (e.g. status conditions, clear output)
  - Does the feature trigger backend operations that should be reported to the admin? If so, validate that the user receives clear feedback about the operation and its outcome (e.g. status conditions, events, or notifications indicating success or failure)
  - *Details:* QE UI team will validate that the VM network display reflects the updated network name after the swap, and that the previously assigned IP is preserved in the display. [CNV-85095](https://redhat.atlassian.net/browse/CNV-85095)

- [x] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* No new metrics or alerts are introduced. The existing VM network interface info metric will be validated to confirm it correctly reflects the updated network attachment after the swap completes (see P1 testing goal and Section III scenario). [CNV-85094](https://redhat.atlassian.net/browse/CNV-85094)

**Integration & Compatibility**

- [ ] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - Does the feature maintain backward compatibility with previous API versions and configurations?
  - *Details:* Not applicable; no new API versions or configurations introduced.

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Not applicable. Once the swap completes, the VM is indistinguishable from one always on the new network; covered by existing upgrade tests.

- [ ] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* Not applicable; no blocking external dependencies identified.

- [ ] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* Not applicable; no impact on other features or teams identified.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* Not applicable; the required secondary network configurations (Linux bridge, localnet) are not supported on cloud platforms.

#### **3. Test Environment**

- **Cluster Topology:** 3-master/3-worker cluster (minimum 2 workers), multi-NIC nodes

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization version 4.22

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled or ARM

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Network:** OVN-Kubernetes, IPv4, IPv6, secondary bridge network, localnet

- **Required Operators:** NMState Operator (for bridge interface configuration)

- **Platform:** Bare metal, PSI

- **Special Configurations:** N/A

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** N/A

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** None identified.
  - **Mitigation:** N/A
  - *Estimated impact on schedule:* N/A

**Test Coverage**

- **Risk:** None identified.
  - **Mitigation:** All intentional coverage exclusions are documented in Out of Scope (Section II.1).
  - *Areas with reduced coverage:* N/A

**Test Environment**

- **Risk:** None.
  - **Mitigation:** Cluster topology requirements are documented in Section II.3.
  - *Missing resources or infrastructure:* None

**Untestable Aspects**

- **Risk:** None — all components are testable.
  - **Mitigation:** Connection continuity during the swap is a non-goal by design and is documented in Known Limitations (Section I.2).
  - *Alternative validation approach:* N/A

**Resource Constraints**

- **Risk:** No special resource requirements.
  - **Mitigation:** New tests will run on network existing lanes.
  - *Current capacity gaps:* None

**Dependencies**

- **Risk:** No blocking external dependencies identified.
  - **Mitigation:** N/A
  - *Dependent teams or components:* None

---

### **III. Test Scenarios & Traceability**

- **[VIRTSTRAT-560]** — As a VM owner, I want to change my VM's VLAN without rebooting so that my workload remains available during network reconfiguration.
  - *Test Scenario:* [Tier 2] Verify that a running VM with bridge binding on a Linux bridge CNI secondary network remains running after a VLAN change, establishes connectivity on the new VLAN, is no longer reachable on the previous VLAN, and the guest interface and its configuration are preserved throughout the transition without guest-side intervention.
  - *Priority:* P0

- **[VIRTSTRAT-560]** — As a VM owner, I want to re-assign my VM connected to a localnet secondary network to a different network without rebooting.
  - *Test Scenario:* [Tier 2] Verify that a running VM connected to a localnet secondary network can be reconnected to a different localnet network (e.g. different VLAN) without rebooting and has connectivity on the new network.
  - *Priority:* P1

- **[VIRTSTRAT-560]** — As a VM owner, I want to update multiple secondary networks on the same running VM and have connectivity on all of them.
  - *Test Scenario:* [Tier 2] Verify that when NAD references for multiple bridge binding on Linux bridge CNI secondary network interfaces on the same running VM are updated at once, all interfaces establish connectivity on their respective new networks.
  - *Priority:* P1

- **[VIRTSTRAT-560]** — As a cluster admin, I want to know that changing the secondary network on a non-migratable VM does not silently succeed.
  - *Test Scenario:* [Tier 2] Verify that when a VLAN change is applied to a non-migratable VM with bridge binding on a Linux bridge CNI secondary network, the VM remains connected to the original network.
  - *Priority:* P1

- **[VIRTSTRAT-560]** — As a VM owner, I want monitoring data to accurately reflect my VM's current network attachment after a secondary network reassignment.
  - *Test Scenario:* [Tier 2] Verify that the VM network interface monitoring data is updated to reflect the new network attachment after a secondary network reassignment completes.
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Leading Dev: Ananya Banerjee (@frenzyfriday)
  - QE Architect: Ruth Netser (@rnetser)
* **Approvers:**
  - QE Architect: Ruth Netser (@rnetser)
  - Principal Developer: Edward Haas (@EdDev)
  - Product Manager/Owner: Ronen Sde-Or (@ronensdeor)
