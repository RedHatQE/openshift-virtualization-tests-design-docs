# Openshift-virtualization-tests Test plan

## **VM IP Address Filtering in OCP Console Across All Projects - Quality Engineering Plan**

### **Metadata & Tracking**

| Field | Details |
|:------|:--------|
| **Enhancement(s)** | N/A (Bug fix - no VEP) |
| **Feature in Jira** | [CNV-72112](https://issues.redhat.com/browse/CNV-72112) |
| **Jira Tracking** | Closed Loop: [CNV-72112](https://issues.redhat.com/browse/CNV-72112), Bug: [CNV-70478](https://issues.redhat.com/browse/CNV-70478), Related: [CNV-66469](https://issues.redhat.com/browse/CNV-66469) |
| **QE Owner(s)** | Guohua Ouyang |
| **Owning SIG** | sig-ui |
| **Participating SIGs** | None |
| **Current Status** | Verified (Fix in CNV v4.18.26, PR merged 2025-11-07) |

**Document Conventions (if applicable):** N/A

### **Feature Overview**

This bug fix addresses the inability to search or filter VMs by IP address in the OpenShift Console when "All Projects" is selected. The root cause was in the kubevirt-plugin's VirtualMachinesList component, where the IP address filtering logic used the unfiltered VM list instead of the frontend-filtered data when the proxy pod was active. The fix ensures that the `matchedVMS` variable filters from `filteredData` (VMs with applied frontend filters) rather than the raw `vms` list, aligning the behavior with the 4.19 codebase. This fix is critical for customers who need to locate specific VMs by IP address across multiple projects in production environments.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value, technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

| Check | Done | Details/Notes | Comments |
|:------|:-----|:--------------|:---------|
| **Review Requirements** | [x] | Reviewed the relevant requirements. | Bug report clearly describes the filtering failure when "All Projects" is selected. Reproduction steps are well-defined. |
| **Understand Value** | [x] | Confirmed clear user stories and understood. Understand the difference between U/S and D/S requirements. **What is the value of the feature for RH customers**. | Customers managing large multi-project environments rely on IP address filtering to locate specific VMs quickly. Without this fix, operators must manually browse through all VMs across projects. |
| **Customer Use Cases** | [x] | Ensured requirements contain relevant **customer use cases**. | Multiple customer cases reported (CNV-66469 and related support cases). Customers with VMs across multiple namespaces need IP-based search in the "All Projects" view. |
| **Testability** | [x] | Confirmed requirements are **testable and unambiguous**. | Testable by creating VMs in multiple projects, selecting "All Projects" in the console, and filtering by IP address. Results should show only the matching VM. |
| **Acceptance Criteria** | [x] | Ensured acceptance criteria are **defined clearly** (clear user stories; D/S requirements clearly defined in Jira). | (1) IP address filter returns the correct VM when searching across all projects. (2) Name and label filters continue to work correctly. (3) Pagination reflects filtered results accurately. |
| **Non-Functional Requirements (NFRs)** | [x] | Confirmed coverage for NFRs, including Performance, Security, Usability, Downtime, Connectivity, Monitoring (alerts/metrics), Scalability, Portability (e.g., cloud support), and Docs. | No performance impact expected. The fix changes the data source for filtering from `vms` to `filteredData`, which is a subset. Usability is the primary NFR: the filter must return accurate results. |

#### **2. Technology and Design Review**

| Check | Done | Details/Notes | Comments |
|:------|:-----|:--------------|:---------|
| **Developer Handoff/QE Kickoff** | [x] | A meeting where Dev/Arch walked QE through the design, architecture, and implementation details. **Critical for identifying untestable aspects early.** | Fix developed by Adam Viktora. The core change is in `VirtualMachinesList.tsx`: `matchedVMS` now filters from `filteredData` instead of raw `vms`. PR reviewed and approved by upalatucci. |
| **Technology Challenges** | [x] | Identified potential testing challenges related to the underlying technology. | (1) The bug only manifests when the proxy pod is active (`isProxyPodAlive === true`), which requires a specific cluster configuration with proxy-based filtering enabled. (2) The issue was not reproducible in standard QE lab environments, suggesting it may require specific network/proxy configurations. |
| **Test Environment Needs** | [x] | Determined necessary **test environment setups and tools**. | Requires an OCP cluster with OpenShift Virtualization, VMs deployed across multiple namespaces with assigned IP addresses, and proxy pod functionality enabled. Playwright test framework is used for UI testing. |
| **API Extensions** | [x] | Reviewed new or modified APIs and their impact on testing. | No API changes. The fix is entirely within the frontend React component (`VirtualMachinesList.tsx`). The `useListPageFilter` hook return values are renamed but functionality is unchanged. |
| **Topology Considerations** | [x] | Evaluated multi-cluster, network topology, and architectural impacts. | Single-cluster topology. The bug affects the "All Projects" view, which is a cross-namespace operation. No multi-cluster or network topology considerations. |

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

This test plan covers the bug fix for VM IP address filtering in the OpenShift Console kubevirt-plugin. The fix corrects the data source used when filtering VMs by IP address across all projects when the proxy pod is active. Testing will validate that the IP address filter returns correct results, that other filters (name, label) continue to work, and that the pagination, selection, and empty state behaviors are correct with the updated filtering logic.

**Testing Goals**

- **P0:** Verify IP address filtering returns the correct VM when "All Projects" is selected and the proxy pod is active
- **P0:** Verify that existing name and label filters continue to function correctly
- **P1:** Verify pagination reflects the filtered VM count accurately
- **P1:** Verify VM selection (select all / deselect all) operates on the filtered results
- **P1:** Verify empty state is displayed correctly when no VMs exist
- **P2:** Verify filter behavior when proxy pod is not active (fallback path)

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item | Rationale | PM/ Lead Agreement |
|:-------------------|:----------|:-------------------|
| Backend API filtering logic | The fix is entirely in the frontend component; backend filtering is unchanged | Out of scope for this fix |
| Proxy pod lifecycle management | Proxy pod startup, health checks, and failure modes are separate concerns | Covered by separate infrastructure testing |
| VM IP address assignment | IP address assignment is handled by the network layer, not the console plugin | Covered by networking QE |
| Non-IP filter types not affected by the fix | Status, node, and other filters were not modified in this PR | No regression expected; covered by existing tests |
| Version 4.19+ behavior | IP address filter was removed from the VM list in 4.19 and later versions | Not applicable to current fix scope |

#### **2. Test Strategy**

| Item | Description | Applicable (Y/N or N/A) | Comments |
|:-----|:------------|:------------------------|:---------|
| Functional Testing | Validates that the feature works according to specified requirements and user stories | Y | Core testing of IP address filtering across all projects with proxy pod active. Verify correct VMs are returned and no false matches occur. |
| Automation Testing | Ensures test cases are automated for continuous integration and regression coverage | Y | Playwright-based UI tests. Existing test at `playwright/tests/tier1/vm-actions.spec.ts` line 98 covers this scenario. |
| Performance Testing | Validates feature performance meets requirements (latency, throughput, resource usage) | N/A | The fix changes the filter source from `vms` to `filteredData` (a subset). No performance degradation expected. |
| Security Testing | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning | N/A | No security changes. RBAC for cross-namespace VM listing is handled by the OCP console framework. |
| Usability Testing | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | Y | This is a UI fix. Verify that the filter input field, results display, and "no results" state are consistent with expected UX. |
| Compatibility Testing | Ensures feature works across supported platforms, versions, and configurations | Y | Verify fix works on OCP 4.18 with CNV v4.18.26+. The fix is specific to the release-4.18 branch. |
| Regression Testing | Verifies that new changes do not break existing functionality | Y | Verify name/label filters still work. Verify pagination. Verify select-all behavior. Verify empty state detection. Verify VirtualMachineListSummary component receives correct data. |
| Upgrade Testing | Validates upgrade paths from previous versions, data migration, and configuration preservation | N/A | Frontend-only fix with no persistent state changes. No upgrade path concerns. |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations | N/A | No API changes. Frontend-only fix. |
| Dependencies | Dependent on deliverables from other components/products? Identify what is tested by which team. | Y | Depends on the proxy pod being functional for the proxy-based filtering code path. Depends on VMI data providing IP address information. |
| Cross Integrations | Does the feature affect other features/require testing by other components? Identify what is tested by which team. | N | The fix is isolated to the VirtualMachinesList component filtering logic. No cross-component impact. |
| Monitoring | Does the feature require metrics and/or alerts? | N | No new metrics or alerts required. |
| Cloud Testing | Does the feature require multi-cloud platform testing? Consider cloud-specific features. | N/A | Console UI behavior is platform-independent. |

#### **3. Test Environment**

| Environment Component | Configuration | Specification Examples |
|:----------------------|:--------------|:-----------------------|
| **Cluster Topology** | Multi-node OCP cluster with at least 2 worker nodes | 3-node cluster: 1 control plane + 2 workers |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.18 with CNV v4.18.26+ | OCP 4.18, CNV 4.18.26 |
| **CPU Virtualization** | Standard x86_64 with hardware virtualization | Intel VT-x or AMD-V enabled |
| **Compute Resources** | Sufficient resources to run VMs across multiple namespaces | 16 GB RAM per worker node minimum |
| **Special Hardware** | N/A | No special hardware required |
| **Storage** | Standard storage for VM disks | OCS/ODF or any CSI-based storage |
| **Network** | Standard cluster networking with VM IP address visibility | OVN-Kubernetes with secondary network for VM IPs |
| **Required Operators** | OpenShift Virtualization operator | HyperConverged CR deployed |
| **Platform** | Any supported OCP platform | Bare metal, IPI, or cloud-provider |
| **Special Configurations** | Multiple namespaces with VMs; proxy pod filtering enabled | At least 3 namespaces with running VMs having assigned IP addresses |

#### **3.1. Testing Tools & Frameworks**

| Category | Tools/Frameworks |
|:---------|:-----------------|
| **Test Framework** | Playwright (UI tests, Tier 1), pytest (Tier 2 / Python) |
| **CI/CD** | OpenShift CI (Prow), Polarion for test case tracking |
| **Other Tools** | Browser DevTools for frontend debugging |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] PR [kubevirt-ui/kubevirt-plugin#3164](https://github.com/kubevirt-ui/kubevirt-plugin/pull/3164) is merged and included in the target CNV build
- [ ] At least 3 namespaces with running VMs having assigned IP addresses are available
- [ ] Proxy pod filtering is enabled and functional in the test environment
- [ ] OCP console with kubevirt-plugin v4.18.26+ is accessible

#### **5. Risks**

| Risk Category | Specific Risk for This Feature | Mitigation Strategy | Status |
|:--------------|:-------------------------------|:--------------------|:-------|
| Timeline/Schedule | Fix is already merged and verified; no timeline risk | Test development can begin immediately against available builds | [x] |
| Test Coverage | The bug was not reproducible in standard QE lab environments, suggesting environment-specific conditions | Document exact proxy pod configuration required; test with both proxy-active and proxy-inactive code paths | [ ] |
| Test Environment | Proxy pod filtering may require specific network or cluster configurations that are not standard in CI | Work with lab team to ensure proxy pod functionality is available; use environment flags to enable/disable proxy path | [ ] |
| Untestable Aspects | The exact customer environment conditions that triggered the bug may not be fully replicable | Focus on testing the code fix logic (filtered data source) rather than reproducing exact customer conditions | [x] |
| Resource Constraints | UI testing with Playwright requires browser automation infrastructure | Use existing Playwright CI infrastructure in the kubevirt-ui repository | [ ] |
| Dependencies | Proxy pod availability is required for testing the primary bug fix code path | Include proxy pod health verification as a test precondition; also test the non-proxy fallback path | [ ] |
| Other | IP address filter is removed in 4.19+; this fix is 4.18-only | Clearly scope tests to the 4.18 branch; no forward-port needed | [x] |

#### **6. Known Limitations**

- The fix is specific to the release-4.18 branch of kubevirt-plugin. In version 4.19 and later, the IP address filter was removed from the VM list entirely, making this fix not applicable to newer versions.
- The bug was reported as not reproducible in standard QE lab and developer environments. The fix was verified on build v4.18.24-24, but the exact customer environment conditions that triggered the original bug may not be fully replicable.
- The fix only addresses the proxy pod code path. When the proxy pod is not active (`isProxyPodAlive === false`), the filtering already uses `filteredData` correctly.
- The fix includes refactoring changes (variable renaming, code alignment with 4.19) beyond the core bug fix, which broadens the surface area for potential regression.

---

### **III. Test Scenarios & Traceability**

This section links requirements to test coverage, enabling reviewers to verify all requirements are tested.

#### **1. Requirements-to-Tests Mapping**

| Requirement ID | Requirement Summary | Test Scenario(s) | Tier | Priority |
|:---------------|:--------------------|:-----------------|:-----|:---------|
| CNV-72112 | IP address filter returns correct VM across all projects when proxy pod is active | Verify IP filter matches correct VM in all-projects view with proxy active | Tier 1 | P0 |
| | IP address filter returns no results for non-existent IP address | Verify IP filter returns empty results for unassigned IP | Tier 1 | P1 |
| | IP address filter works with partial IP address match | Verify partial IP address filtering behavior | Tier 1 | P1 |
| | Name filter continues to work correctly after fix | Verify name-based VM filtering in all-projects view | Tier 1 | P0 |
| | Label filter continues to work correctly after fix | Verify label-based VM filtering in all-projects view | Tier 1 | P1 |
| CNV-70478 | Filtered VM list uses frontend-filtered data when proxy fails | Verify fallback to filteredData when proxy pod filtering fails | Tier 1 | P1 |
| | Pagination reflects filtered VM count accurately | Verify pagination item count matches filtered results | Tier 1 | P1 |
| | Select-all operates on filtered VM list | Verify select-all selects only filtered VMs | Tier 1 | P2 |
| | Deselect-all clears selection correctly | Verify deselect-all clears all selected VMs | Tier 1 | P2 |
| | Empty state displayed when no VMs exist in any project | Verify empty state renders when vms list is empty | Tier 1 | P1 |
| | VirtualMachineListSummary receives correct VM data | Verify summary component shows correct VM count | Tier 1 | P2 |
| CNV-66469 | IP filter works in single-project view | Verify IP filter returns correct VM within a single project | Tier 1 | P1 |
| | Filter by IP across multiple projects with VMs in different namespaces | Verify cross-namespace IP search returns correct VM from target namespace | Tier 2 | P0 |
| | End-to-end VM lifecycle with IP filtering verification | Verify VM create, IP assignment, filter by IP, delete workflow | Tier 2 | P1 |
| | Bulk action on filtered VMs across projects | Verify bulk operations work correctly on IP-filtered VM results | Tier 2 | P2 |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

- **Reviewers:**
  - TBD / @tbd
  - TBD / @tbd
- **Approvers:**
  - TBD / @tbd
  - TBD / @tbd
