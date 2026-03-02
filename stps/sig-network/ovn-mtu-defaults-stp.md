# Openshift-virtualization-tests Test plan

## **Document Better MTU Defaults for OVN Kubernetes (Closed Loop) - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                           |
|:-----------------------|:------------------------------------------------------------------|
| **Enhancement(s)**     | N/A (Documentation correctness fix -- no design enhancement)     |
| **Feature in Jira**    | [CNV-68270](https://issues.redhat.com/browse/CNV-68270)          |
| **Jira Tracking**      | Bug: [CNV-46504](https://issues.redhat.com/browse/CNV-46504), Closed Loop: [CNV-68270](https://issues.redhat.com/browse/CNV-68270), Validation: [CNV-68331](https://issues.redhat.com/browse/CNV-68331), Duplicate: [OCPBUGS-57322](https://issues.redhat.com/browse/OCPBUGS-57322), Epic: [CNV-69598](https://issues.redhat.com/browse/CNV-69598) |
| **QE Owner(s)**        | TBD                                                               |
| **Owning SIG**         | sig-network                                                       |
| **Participating SIGs** | sig-documentation                                                 |
| **Current Status**     | Draft                                                             |

**Document Conventions (if applicable):** N/A

### **Feature Overview**

This closed-loop item addresses documentation inconsistencies in OVN-Kubernetes secondary network MTU configuration examples shipped with OpenShift Virtualization. Two specific problems were identified in the original bug [CNV-46504](https://issues.redhat.com/browse/CNV-46504):

1. **Layer 2 overlay topology example** specified MTU 1300, but the correct default maximum for layer 2 overlays is 1400 (computed by the Cluster Network Operator as underlay MTU minus overlay overhead). The documentation PR updated this value from 1300 to 1400.
2. **Localnet topology example** omitted the MTU field entirely, causing OVN-Kubernetes to default to 1400 when 1500 is the appropriate value for localnet topologies where the physical network supports standard Ethernet MTU.

The fix was implemented via documentation PR [openshift/openshift-docs#98221](https://github.com/openshift/openshift-docs/pull/98221) (main branch) and cherry-picked to enterprise branches 4.15 through 4.20. A prior related fix for [OCPBUGS-57322](https://issues.redhat.com/browse/OCPBUGS-57322) was merged via PR [openshift/openshift-docs#96102](https://github.com/openshift/openshift-docs/pull/96102), which also corrected MTU default descriptions in the OVN-K network plugin JSON configuration table and the localnet NAD CLI module.

The testing scope for this closed-loop item focuses on validating that the documented MTU values are functionally correct, that VMs using OVN-Kubernetes secondary networks with the documented MTU settings achieve expected connectivity and throughput, and that the default MTU computation by the Cluster Network Operator produces the values stated in the documentation.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                           | Comments |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [ ]  | Reviewed the relevant requirements.                                                                                                                                                     | Original bug CNV-46504 and OCPBUGS-57322 documented incorrect MTU defaults. Closed-loop CNV-68270 tracks validation that the documentation fix was applied and is accurate. |
| **Understand Value**                   | [ ]  | Confirmed clear user stories and understood.  <br/>Understand the difference between U/S and D/S requirements<br/> **What is the value of the feature for RH customers**.               | Customers copy-paste documentation examples verbatim. Incorrect MTU values cause suboptimal network performance (layer 2: reduced throughput due to unnecessarily low MTU) or silent misconfiguration (localnet: MTU mismatch with physical network causing packet drops or fragmentation). |
| **Customer Use Cases**                 | [ ]  | Ensured requirements contain relevant **customer use cases**.                                                                                                                           | Customer-reported issue: users deploying OVN-Kubernetes secondary networks for VM connectivity following documentation examples experienced unexpected MTU values. The fix ensures documentation examples produce correct, optimal MTU settings. |
| **Testability**                        | [ ]  | Confirmed requirements are **testable and unambiguous**.                                                                                                                                | Testable by creating NADs with documented MTU values and verifying that VMs connected via these NADs can transmit packets at the expected MTU without fragmentation. Also verifiable by checking the CNO-computed default MTU matches documented values. |
| **Acceptance Criteria**                | [ ]  | Ensured acceptance criteria are **defined clearly** (clear user stories; D/S requirements clearly defined in Jira).                                                                     | AC1: Layer 2 overlay NAD example uses MTU 1400 (or omits MTU to use CNO default). AC2: Localnet NAD example specifies MTU 1500 explicitly. AC3: VMs using these configurations achieve expected end-to-end MTU. |
| **Non-Functional Requirements (NFRs)** | [ ]  | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs. | Performance: MTU directly affects network throughput; validated via MTU path discovery tests. Documentation: the fix itself is a documentation change. No security, scalability, or monitoring impacts. |

#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                                           | Comments |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [ ]  | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.** | PR reviewer confirmed the change is correct. The localnet MTU 1500 fix was already applied in a previous documentation update. QE kickoff is documentation-focused. |
| **Technology Challenges**        | [ ]  | Identified potential testing challenges related to the underlying technology.                                                                            | MTU behavior depends on the cluster's underlay network MTU. Default MTU computation by the CNO subtracts overlay overhead (e.g., Geneve encapsulation = 100 bytes) from the underlay MTU. Testing must account for environments where the underlay MTU is not the standard 1500 (e.g., jumbo frames at 9000). |
| **Test Environment Needs**       | [ ]  | Determined necessary **test environment setups and tools**.                                                                                              | Requires OCP cluster with OVN-Kubernetes as the CNI plugin, at least one worker node, ability to create layer 2 overlay and localnet NetworkAttachmentDefinitions, and VMs with network tools (ping, ip link) for MTU verification. |
| **API Extensions**               | [ ]  | Reviewed new or modified APIs and their impact on testing.                                                                                               | No API changes. The fix modifies documentation examples only. The NAD spec `mtu` field and OVN-Kubernetes CNI behavior are unchanged. |
| **Topology Considerations**      | [ ]  | Evaluated multi-cluster, network topology, and architectural impacts.                                                                                    | Localnet topology requires a physical network bridge mapped to the OVN localnet; layer 2 overlay is a pure overlay requiring no physical network changes. Both topologies must be validated. |

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

Testing validates that the corrected MTU documentation values produce functionally correct network configurations for VMs connected to OVN-Kubernetes secondary networks. Specifically:

- Layer 2 overlay NADs with MTU 1400 (the corrected value) allow VMs to communicate at the expected MTU
- Localnet NADs with MTU 1500 (the corrected value) allow VMs to communicate at standard Ethernet MTU
- The CNO default MTU computation (when MTU is omitted from a layer 2 overlay NAD) produces a value consistent with the documented behavior
- VMs using the documented NAD examples achieve end-to-end connectivity without unexpected fragmentation or packet drops

**Testing Goals**

- **P0:** Verify that a layer 2 overlay NAD with MTU 1400 allows VM-to-VM communication at MTU 1400
- **P0:** Verify that a localnet NAD with MTU 1500 allows VM connectivity at standard Ethernet MTU
- **P1:** Verify that omitting the MTU field from a layer 2 overlay NAD results in the CNO computing an appropriate default MTU
- **P1:** Verify that the previously incorrect MTU 1300 value for layer 2 overlays is no longer present in shipped documentation
- **P1:** Verify that localnet NAD examples explicitly include MTU 1500 in shipped documentation
- **P2:** Verify MTU path discovery (PMTUD) works correctly for VMs on secondary networks with the documented MTU values

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item | Rationale | PM/ Lead Agreement |
|:-------------------|:----------|:-------------------|
| OVN-Kubernetes CNI plugin code changes | No code changes were made; this is a documentation-only fix | [ ] Name/Date |
| Primary network MTU testing | The fix applies only to secondary network (NAD) MTU documentation | [ ] Name/Date |
| Non-OVN-Kubernetes CNI plugins | The fix is specific to OVN-Kubernetes secondary networks | [ ] Name/Date |
| Jumbo frame (MTU > 1500) configurations | Jumbo frames require non-default underlay configuration outside the scope of the documented examples | [ ] Name/Date |
| SR-IOV or macvtap secondary networks | The fix targets only OVN-Kubernetes layer 2 overlay and localnet topologies | [ ] Name/Date |

#### **2. Test Strategy**

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:---------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y | Validate that NADs created with the documented MTU values produce correct network behavior for VMs |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y | Automated via Ginkgo (tier 1) for functional NAD/MTU validation and pytest (tier 2) for end-to-end VM connectivity workflows |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | Y | MTU directly affects throughput; verify no unexpected performance degradation with corrected values compared to previous incorrect values |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N/A | No security-relevant changes; documentation fix only |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | N/A | No UI changes; documentation clarity improvement |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | Y | Fix cherry-picked to OCP 4.15 through 4.20; verify MTU behavior is consistent across supported versions |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | Y | Verify that changing the layer 2 example MTU from 1300 to 1400 does not break existing deployments that used MTU 1300 (i.e., MTU 1300 still works, just is not the recommended default) |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | N/A | Documentation change only; no runtime state affected by upgrades |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | Y | Existing NADs with MTU 1300 should continue to function; the documentation change does not invalidate previously deployed configurations |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | Y | Depends on OVN-Kubernetes CNI plugin for MTU enforcement and the Cluster Network Operator for default MTU computation |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | N/A | Documentation-only change; no cross-component integration impact |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | N/A | No monitoring changes |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | N/A | MTU behavior is consistent across platforms; no cloud-specific considerations for secondary network MTU |

#### **3. Test Environment**

| Environment Component                         | Configuration | Specification Examples |
|:----------------------------------------------|:--------------|:-----------------------|
| **Cluster Topology**                          | Single or multi-node cluster with at least 1 worker node | 3-node cluster (1 control plane + 2 workers) |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.15+ with OpenShift Virtualization 4.15+ (fix cherry-picked to 4.15-4.20) | OCP 4.18, CNV 4.18 |
| **CPU Virtualization**                        | Standard virtualization-enabled nodes | Intel VT-x or AMD-V enabled |
| **Compute Resources**                         | Sufficient resources for running 2+ VMs concurrently for connectivity testing | 8 GB RAM per worker node minimum |
| **Special Hardware**                          | N/A | N/A |
| **Storage**                                   | Standard storage for VM root disks | OCS/ODF or local storage |
| **Network**                                   | OVN-Kubernetes as primary CNI; ability to create layer 2 overlay and localnet NADs; standard underlay MTU (1500) | OVN-Kubernetes with Geneve tunneling; localnet bridge mapped to physical interface |
| **Required Operators**                        | OpenShift Virtualization operator, OVN-Kubernetes CNI (default in OCP) | HyperConverged CR deployed |
| **Platform**                                  | Bare metal or virtualized (nested virtualization supported) | Bare metal preferred for accurate MTU testing |
| **Special Configurations**                    | Localnet bridge configuration on worker nodes for localnet topology tests | Bridge mapped to physical NIC for localnet; no special config for layer 2 overlay |

#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks |
|:-------------------|:-----------------|
| **Test Framework** | Ginkgo v2 + Gomega (Tier 1), pytest (Tier 2) |
| **CI/CD**          | Prow (upstream), Jenkins (downstream) |
| **Other Tools**    | oc CLI, virtctl, ping, ip link show, tracepath (for PMTUD) |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] Documentation PRs [openshift/openshift-docs#98221](https://github.com/openshift/openshift-docs/pull/98221) and [openshift/openshift-docs#96102](https://github.com/openshift/openshift-docs/pull/96102) are merged
- [ ] OVN-Kubernetes CNI is deployed and operational on the cluster
- [ ] Localnet bridge is configured on worker nodes for localnet topology tests
- [ ] At least 2 VMs can be provisioned on the cluster for connectivity testing

#### **5. Risks**

| Risk Category        | Specific Risk for This Feature | Mitigation Strategy | Status |
|:---------------------|:-------------------------------|:--------------------|:-------|
| Timeline/Schedule    | Low risk; documentation PRs are already merged across all target branches | N/A -- fix is complete | [ ] |
| Test Coverage        | MTU behavior varies with underlay network configuration; tests may not cover all underlay MTU scenarios | Document expected underlay MTU in test prerequisites; parameterize tests for standard (1500) underlay MTU | [ ] |
| Test Environment     | Localnet topology requires physical bridge configuration on worker nodes, which may not be available in all CI environments | Provide localnet bridge setup automation in test fixtures; fall back to layer 2 overlay-only testing if localnet is unavailable | [ ] |
| Untestable Aspects   | CNO default MTU computation is internal and may vary by cluster configuration | Validate indirectly by checking the MTU on the VM interface when no explicit MTU is set in the NAD | [ ] |
| Resource Constraints | N/A | N/A | [ ] |
| Dependencies         | OVN-Kubernetes CNI version must support the `mtu` field in NAD spec | Use OCP 4.15+ where OVN-K MTU support is stable | [ ] |
| Other                | Enterprise-4.14 cherry-pick of PR #98221 failed due to merge conflict; 4.14 documentation may still contain incorrect MTU value | Verify documentation content on OCP 4.14 separately; file follow-up if manual cherry-pick is needed | [ ] |

#### **6. Known Limitations**

- The CNO default MTU computation depends on the underlay network MTU and overlay overhead (e.g., Geneve encapsulation). The documented default of 1400 for layer 2 overlays assumes a standard 1500 underlay MTU. Clusters with non-standard underlay MTU (e.g., jumbo frames) will have different computed defaults.
- The localnet MTU of 1500 assumes the physical network connected to the localnet bridge supports standard Ethernet MTU. Environments with lower physical MTU will require adjusting the NAD MTU field accordingly.
- The documentation fix for enterprise-4.14 failed to cherry-pick automatically due to a merge conflict. The 4.14 branch may still contain the incorrect MTU 1300 value.
- Testing MTU at the application layer (e.g., large file transfers) may show different effective MTU due to TCP MSS clamping and IP/TCP header overhead.

---

### **III. Test Scenarios & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are tested.

#### **1. Requirements-to-Tests Mapping**

| Requirement ID | Requirement Summary | Test Scenario(s) | Tier | Priority |
|:---------------|:--------------------|:-----------------|:-----|:---------|
| CNV-46504-AC1 | Layer 2 overlay NAD example uses MTU 1400 instead of incorrect MTU 1300 | Verify VM-to-VM connectivity over layer 2 overlay NAD with MTU 1400; confirm packets of size 1400 are transmitted without fragmentation | Tier 1 (Functional) | P0 |
| | | Verify end-to-end workflow: create layer 2 overlay NAD with MTU 1400, attach two VMs, validate bidirectional connectivity at MTU 1400 using ping with packet size matching MTU minus headers | Tier 2 (End-to-End) | P0 |
| CNV-46504-AC2 | Localnet NAD example specifies MTU 1500 explicitly | Verify VM connectivity over localnet NAD with explicit MTU 1500; confirm packets of size 1500 are transmitted without fragmentation | Tier 1 (Functional) | P0 |
| | | Verify end-to-end workflow: create localnet NAD with MTU 1500, attach VM, validate connectivity to external network at standard Ethernet MTU | Tier 2 (End-to-End) | P0 |
| CNV-46504-DEF | CNO computes correct default MTU when MTU is omitted from layer 2 overlay NAD | Verify that omitting the MTU field from a layer 2 overlay NAD results in a VM interface MTU equal to the CNO-computed default (underlay MTU minus overlay overhead) | Tier 1 (Functional) | P1 |
| | | Verify end-to-end: create layer 2 overlay NAD without explicit MTU, attach VM, confirm interface MTU matches expected CNO default, validate connectivity at computed MTU | Tier 2 (End-to-End) | P1 |
| CNV-68270-REG1 | Previously documented MTU 1300 still functions (backward compatibility) | Verify that a layer 2 overlay NAD with MTU 1300 still produces a functional network; VMs can communicate at MTU 1300 | Tier 1 (Functional) | P1 |
| | | Verify end-to-end backward compatibility: deploy NAD with MTU 1300 (old documentation value), attach VMs, confirm connectivity works but throughput is suboptimal compared to MTU 1400 | Tier 2 (End-to-End) | P2 |
| CNV-68270-REG2 | Localnet NAD without explicit MTU defaults to 1400 (not 1500) | Verify that omitting the MTU field from a localnet NAD results in a default MTU of 1400, confirming that explicit MTU 1500 specification is necessary for standard Ethernet MTU | Tier 1 (Functional) | P1 |
| CNV-68270-MTU1 | MTU enforcement on layer 2 overlay secondary network | Verify that packets exceeding the configured MTU on a layer 2 overlay NAD are either fragmented or dropped (depending on DF bit), confirming MTU enforcement | Tier 1 (Functional) | P1 |
| | | Verify PMTUD (Path MTU Discovery) works correctly: send packets with DF bit set exceeding configured MTU, confirm ICMP "need to fragment" response | Tier 2 (End-to-End) | P2 |
| CNV-68270-MTU2 | MTU enforcement on localnet secondary network | Verify that packets exceeding the configured MTU on a localnet NAD are either fragmented or dropped, confirming MTU enforcement | Tier 1 (Functional) | P1 |
| CNV-68270-DOC1 | Documentation correctness: layer 2 overlay example contains MTU 1400 | Verify that the shipped documentation for creating a layer 2 NAD via CLI specifies MTU 1400 (not 1300) in the example YAML | Tier 2 (End-to-End) | P1 |
| CNV-68270-DOC2 | Documentation correctness: localnet example contains explicit MTU 1500 | Verify that the shipped documentation for creating a localnet NAD via CLI specifies MTU 1500 explicitly in the example YAML | Tier 2 (End-to-End) | P1 |
| CNV-68270-MULTI | Multiple VMs on same secondary network with corrected MTU | Verify that three or more VMs attached to the same layer 2 overlay NAD with MTU 1400 can all communicate with each other at the configured MTU | Tier 2 (End-to-End) | P2 |
| CNV-68270-COMPAT | Cross-version documentation consistency | Verify that the MTU correction is present in documentation for OCP versions 4.15, 4.16, 4.17, 4.18, 4.19, and 4.20 (cherry-pick PRs #98538-#98543 merged) | Tier 2 (End-to-End) | P2 |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

- **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
- **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]
