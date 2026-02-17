# Openshift-virtualization-tests Test plan

## **Live Update of NAD Reference on Running VM - Quality Engineering Plan**

### **Metadata & Tracking**

| Field | Details |
|:-----------------------|:------------------------------------------------------------------|
| **Enhancement(s)** | [VEP #140: Live Update NAD Reference](https://github.com/kubevirt/enhancements/blob/main/veps/sig-network/hotpluggable-nad-ref.md) |
| **Feature in Jira** | [CNV-72329](https://issues.redhat.com/browse/CNV-72329) |
| **Jira Tracking** | [CNV-72329](https://issues.redhat.com/browse/CNV-72329) |
| **QE Owner(s)** | TBD |
| **Owning SIG** | sig-network |
| **Participating SIGs** | sig-compute |
| **Current Status** | Draft |

**Document Conventions (if applicable):** N/A

### **Feature Overview**

This feature allows VM administrators to change the NetworkAttachmentDefinition (NAD) reference on a running VM's secondary network interface without requiring a VM restart. When the `LiveUpdateNADRef` feature gate is enabled, updating the `networkName` field in the VM spec triggers an automatic live migration, after which the VM is connected to the new network. Guest interface properties such as MAC address and interface name are preserved across the change.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

| Check | Done | Details/Notes | Comments |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements** | [ ] | Reviewed the relevant requirements. | VEP #140 defines clear scope: change NAD ref on running VM via live migration, gated by `LiveUpdateNADRef`. |
| **Understand Value** | [ ] | Confirmed clear user stories and understood.  <br/>Understand the difference between U/S and D/S requirements<br/> **What is the value of the feature for RH customers**. | Enables network reassignment (e.g., VLAN change) without VM downtime, preserving workload continuity. |
| **Customer Use Cases** | [ ] | Ensured requirements contain relevant **customer use cases**. | "As a VM admin, I want to swap the guest's uplink from one network to another without the VM noticing." |
| **Testability** | [ ] | Confirmed requirements are **testable and unambiguous**. | Testable via API patching and network connectivity checks. Upstream e2e test (`tests/network/nad_live_update.go`) covers 3 scenarios. |
| **Acceptance Criteria** | [ ] | Ensured acceptance criteria are **defined clearly** (clear user stories; D/S requirements clearly defined in Jira). | AC: NAD change triggers migration, post-migration connectivity on new NAD, feature gate controls availability. |
| **Non-Functional Requirements (NFRs)** | [ ] | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs. | No new scalability or performance constraints. Relies on existing migration infrastructure. |

#### **2. Technology and Design Review**

| Check | Done | Details/Notes | Comments |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [ ] | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.** | QE kickoff should be scheduled during feature design phase. PR #16412 is under review; kickoff should cover migration evaluator design and pod annotation dependency. |
| **Technology Challenges** | [ ] | Identified potential testing challenges related to the underlying technology. | Migration evaluator reads pod network-status annotations to detect NAD changes; stale annotations could cause incorrect decisions. NAD name normalization (namespace-qualified vs. unqualified) requires careful handling. |
| **Test Environment Needs** | [ ] | Determined necessary **test environment setups and tools**. | Requires 2+ schedulable worker nodes, two bridge-based NADs, shared storage for migration, `WorkloadUpdateMethods=LiveMigrate` and `VMRolloutStrategy=LiveUpdate`. |
| **API Extensions** | [ ] | Reviewed new or modified APIs and their impact on testing. | No new API fields. Existing `spec.networks[].multus.networkName` becomes live-updatable. New feature gate: `LiveUpdateNADRef` (Beta v1.8). |
| **Topology Considerations** | [ ] | Evaluated multi-cluster, network topology, and architectural impacts. | Feature requires live-migratable VMs; non-migratable VMs cannot use this feature. Both source and target nodes must have the target NAD's network infrastructure. |

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

Testing covers the ability to change the NAD reference on a running VM's secondary network interface without restart. This includes verifying that the NAD change triggers automatic live migration, that the VM connects to the new network after migration, and that the feature is properly controlled by the `LiveUpdateNADRef` feature gate.

**Testing Goals**

- **P0:** Verify that changing the NAD reference on a running VM results in the VM being connected to the new network without restart
- **P0:** Verify that the `LiveUpdateNADRef` feature gate controls whether NAD changes are applied live or require restart
- **P1:** Verify that the VM maintains its guest interface properties (MAC address, interface name) after the NAD change
- **P1:** Verify correct behavior when the target NAD does not exist (migration failure handling)
- **P1:** Verify that existing NIC hotplug/unplug operations are not affected when the feature gate is enabled
- **P2:** Verify that multiple sequential NAD changes each result in correct network connectivity
- **P2:** Verify that non-NAD network property changes still require restart when the feature gate is enabled

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item | Rationale | PM/ Lead Agreement |
|:-------------------|:----------|:-------------------|
| Migrating between CNI types | VEP #140 explicit non-goal | [ ] Name/Date |
| Changing the network binding/plugin | VEP #140 explicit non-goal | [ ] Name/Date |
| Seamless network connectivity during migration | Brief interruption is expected; VEP #140 explicit non-goal | [ ] Name/Date |
| NAD change on non-migratable VMs | Requires DNC changes not in scope; VEP #140 explicit non-goal | [ ] Name/Date |
| Guest network reconfiguration after NAD swap | User responsibility; VEP #140 explicit non-goal | [ ] Name/Date |
| In-place NAD swapping via DNC | Current design uses migration (Option 1); DNC changes not required | [ ] Name/Date |

#### **2. Test Strategy**

| Item | Description | Applicable (Y/N or N/A) | Comments |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:---------|
| Functional Testing | Validates that the feature works according to specified requirements and user stories | Y | NAD reference change workflow, feature gate behavior, connectivity verification, spec synchronization |
| Automation Testing | Ensures test cases are automated for continuous integration and regression coverage | Y | Upstream e2e tests in PR #16412 provide foundation; downstream tests in Ginkgo (tier 1) and pytest (tier 2) |
| Performance Testing | Validates feature performance meets requirements (latency, throughput, resource usage) | N/A | Migration performance covered by existing migration test suites; no new performance-sensitive code paths |
| Security Testing | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning | N/A | No new RBAC roles, API endpoints, or security boundaries |
| Usability Testing | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | N/A | Feature is API-driven; no UI changes |
| Compatibility Testing | Ensures feature works across supported platforms, versions, and configurations | Y | Verify coexistence with existing NIC hotplug/unplug and link state management operations |
| Regression Testing | Verifies that new changes do not break existing functionality | Y | Code changes affect VM controller sync, migration evaluator, and restart-required detection — all shared with existing network features |
| Upgrade Testing | Validates upgrade paths from previous versions, data migration, and configuration preservation | N/A | Feature is a one-time operation (patching a VM spec field) gated behind a new feature gate with no persistent state migration |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations | Y | Disabling the feature gate must restore previous behavior (NAD changes require restart) |
| Dependencies | Dependent on deliverables from other components/products? Identify what is tested by which team. | N/A | No team delivery dependencies; Multus CNI and bridge CNI are pre-existing platform infrastructure |
| Cross Integrations | Does the feature affect other features/require testing by other components? Identify what is tested by which team. | Y | Shares code paths with NIC hotplug/unplug and live migration; regression verification needed |
| Monitoring | Does the feature require metrics and/or alerts? | N/A | No new metrics or alerts; existing migration metrics apply |
| Cloud Testing | Does the feature require multi-cloud platform testing? Consider cloud-specific features. | N/A | Feature operates at the KubeVirt layer; no cloud-specific considerations |

#### **3. Test Environment**

| Environment Component | Configuration | Specification Examples |
|:----------------------------------------------|:--------------|:-----------------------|
| **Cluster Topology** | Multi-node cluster with at least 2 schedulable worker nodes | 3-node cluster (1 control plane + 2 workers) |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.22 with OpenShift Virtualization 4.22 | OCP 4.22, CNV 4.22 |
| **CPU Virtualization** | Standard virtualization-enabled nodes | Intel VT-x or AMD-V enabled |
| **Compute Resources** | Sufficient resources for live migration (source + target VM memory) | 16 GB RAM per worker node minimum |
| **Special Hardware** | N/A — no special hardware required | N/A |
| **Storage** | Shared storage for live migration (RWX PVCs or LiveMigrate-compatible storage) | OCS/ODF, NFS, or iSCSI with RWX support |
| **Network** | Multiple bridge-based NetworkAttachmentDefinitions on each worker node | Two bridge NADs with different bridges (e.g., br-1, br-2) |
| **Required Operators** | OpenShift Virtualization operator, Multus CNI (default in OCP) | HyperConverged CR |
| **Platform** | Bare metal or nested virtualization with migration support | Bare metal preferred |
| **Special Configurations** | `WorkloadUpdateMethods=LiveMigrate`, `VMRolloutStrategy=LiveUpdate`, feature gate `LiveUpdateNADRef` enabled | HyperConverged CR with LiveMigrate workload update strategy |

#### **3.1. Testing Tools & Frameworks**

| Category | Tools/Frameworks |
|:-------------------|:-----------------|
| **Test Framework** | |
| **CI/CD** | |
| **Other Tools** | |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] PR [kubevirt/kubevirt#16412](https://github.com/kubevirt/kubevirt/pull/16412) is merged and included in the target build
- [ ] `LiveUpdateNADRef` feature gate is available in KubeVirt configuration
- [ ] At least 2 bridge-based NetworkAttachmentDefinitions are deployed and functional on worker nodes

#### **5. Risks**

| Risk Category | Specific Risk for This Feature | Mitigation Strategy | Status |
|:---------------------|:-------------------------------|:--------------------|:-------|
| Timeline/Schedule | PR #16412 is still open with changes requested; merge timeline may affect test development | Begin test development using upstream e2e tests as reference | [ ] |
| Test Coverage | Pod annotation dependency in migration evaluator may produce edge cases not covered by upstream tests | Add dedicated test scenarios for NAD name normalization and annotation parsing | [ ] |
| Test Environment | N/A — standard multi-node cluster with bridge NADs | N/A | [ ] |
| Untestable Aspects | In-place NAD swapping via DNC (Option 2) is not implemented and cannot be tested | Document as known limitation | [ ] |
| Resource Constraints | N/A — uses standard test infrastructure | N/A | [ ] |
| Dependencies | N/A — no team delivery dependencies | N/A | [ ] |
| Other | NAD name comparison logic may have asymmetric behavior for namespace-qualified names (flagged in PR review) | Track resolution in PR review; add unit tests for namespace-qualified NAD name pairs | [ ] |

#### **6. Known Limitations**

- Only bridge binding type is supported for NAD reference live update. Other binding types (SR-IOV, macvtap, passt) are not supported.
- Non-migratable VMs cannot use this feature; a live migration is required to apply the NAD change.
- Brief network connectivity interruption occurs during live migration. Seamless connectivity is explicitly not a goal.
- Guest network configuration (IP address, routes) is not automatically updated after the NAD swap; the VM owner must handle guest-side reconfiguration if needed.
- In-place NAD swapping (without migration) is not supported, even on clusters with Dynamic Networks Controller.
- The feature does not limit migration retries due to a missing NAD. If the target NAD does not exist, migrations will continue to be attempted.

---

### **III. Test Scenarios & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are tested.

#### **1. Requirements-to-Tests Mapping**

| Requirement ID | Requirement Summary | Test Scenario(s) | Tier | Priority |
|:---------------|:--------------------|:-----------------|:-----|:---------|
| CNV-72329 | NAD reference can be changed on a running VM without restart | Verify NAD reference change triggers automatic live migration and VM connects to new network | Tier 1 | P0 |
| | NAD reference can be changed on a running VM without restart | Verify end-to-end NAD change workflow including connectivity on new network and loss of connectivity on old network | Tier 2 | P0 |
| | Feature gate controls whether NAD changes are applied live | Verify NAD reference change does NOT trigger migration when feature gate is disabled; RestartRequired condition is set | Tier 1 | P0 |
| | Feature gate controls whether NAD changes are applied live | Verify feature gate disabled behavior end-to-end: VM requires restart after NAD change | Tier 2 | P0 |
| | VM maintains guest interface properties after NAD change | Verify MAC address and interface name inside the guest are preserved after NAD swap and migration | Tier 2 | P1 |
| | VM connects to the correct network after NAD change | Verify post-migration network connectivity on new NAD via ping from peer VM | Tier 2 | P1 |
| | Non-existent NAD reference is handled gracefully | Verify migration failure when NAD reference is changed to a non-existent NAD | Tier 1 | P1 |
| | Non-existent NAD reference is handled gracefully | Verify end-to-end behavior with non-existent target NAD including VM state after failed migration | Tier 2 | P1 |
| | RestartRequired condition is not set for NAD-only changes | Verify that changing only the NAD reference does not add RestartRequired condition when feature gate is enabled | Tier 1 | P1 |
| | Non-NAD network property changes still require restart | Verify that changing non-networkName properties (e.g., network type) triggers RestartRequired even with feature gate enabled | Tier 1 | P1 |
| | Existing NIC hotplug operations are unaffected by feature gate | Verify bridge and SR-IOV interface hotplug/unplug continue to work correctly when feature gate is enabled | Tier 1 | P1 |
| | Existing NIC hotplug operations are unaffected by feature gate | Verify NIC hotplug followed by NAD change both complete correctly on the same VM | Tier 2 | P2 |
| | Multiple sequential NAD changes produce correct results | Verify multiple NAD reference changes in sequence each trigger migration and result in correct connectivity | Tier 2 | P2 |
| | Namespace-qualified NAD names are handled correctly | Verify NAD reference change works with namespace-qualified NAD names (e.g., `namespace/nad-name`) | Tier 1 | P2 |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
* **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]
