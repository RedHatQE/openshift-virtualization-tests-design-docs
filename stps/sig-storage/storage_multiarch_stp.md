# Openshift-virtualization-tests Test plan

## **CDI support for heterogeneous multi-arch clusters - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster)
- **Feature Tracking:** [VIRTSTRAT-494](https://issues.redhat.com/browse/VIRTSTRAT-494)
- **Epic Tracking:** [CNV-73892](https://issues.redhat.com/browse/CNV-73892)
- **QE Owner(s):** Yan Du
- **Owning SIG:** sig-storage
- **Participating SIGs:** sig-iuo, sig-infra, sig-storage, sig-virt, sig-network, sig-ui
-
**Document Conventions:**
- **CDI**: Containerized Data Importer - responsible for importing VM disk images into Kubernetes
- **DIC**: DataImportCron - automates periodic import of VM images
- **SSP**: Scheduling, Scale and Performance Operator - manages VM templates and common resources
- **HCO**: Hyperconverged Cluster Operator - orchestrates OpenShift Virtualization deployment
- **IUO**: Integration/Update Operator - handles feature gate management and upgrades
- **VEP**: Virtualization Enhancement Proposal - design document for new features
- **Pull Method**: Mechanism for importing images (Pod-based or Node-based)

### **Feature Overview**

This feature enables CDI to support heterogeneous multi-architecture clusters, allowing VM disk images to be imported and matched to the correct architecture (e.g., AMD64, ARM64) in mixed-architecture environments.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - CDI must support importing multi-architecture images with architecture matching
    - Support for both Pod-based and Node-based pull methods
    - DataSource can reference another DataSource for image inheritance
    - VM scheduling must respect architecture constraints

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:*
    - Enables customers to run heterogeneous workloads (AMD64 and ARM64 VMs) on the same cluster
  - *List the customer use cases identified:*


- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* None

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - Multi-arch images are successfully imported with correct architecture matching
    - Pod-based pull method correctly selects architecture-specific image layers
    - Node-based pull method schedules import pods on correct architecture nodes
    - DataSource chaining (DataSource → DataSource) works correctly
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Portability: AWS platform support (ARM64 workers available)
    - Documentation: User guide updates for multi-arch feature enablement
  - *Note any NFRs not covered and why:*
    - Security: No additional security requirements beyond existing CDI security model
    - Performance baseline testing: Deferred to future performance-focused testing cycles

#### **2. Known Limitations**

The following topics will not be tested or supported:

- The feature is limited to AWS platform due to ARM64 worker availability
- Performance testing is out of scope for this test plan

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Met with the team through the design, architecture, and implementation details

- [x] **Technology Challenges**
  - *List identified challenges:*
    - AWS multi-arch cluster duration is 12hr
  - *Impact on testing approach:*
    - Requires multi-arch cluster setup (AMD64 + ARM64 workers)
    - MultiArch Feature Gate is enabled

- [x] **API Extensions**
  - *List new or modified APIs:*
    - `dv.spec.registry.platform.architecture` field for specifying target architecture
    - `datasource.spec.source.dataSource.namespace` (string) - Pointer DataSource namespace
    - `datasource.spec.source.dataSource.name` (string) - Pointer DataSource name
  - *Testing impact:*
    - New APIs required validation tests in CDI

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:*
    - Heterogeneous cluster: 3 AMD64 control-plane, 2 AMD64 workers, 1-2 ARM64 workers
    - AWS platform (ARM64 instances available)
  - *Impact on test design:*
    - Tests must verify VM scheduling to correct architecture nodes

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

**Functional Goals**:

- **[P0]** Verify multi-arch image matching architecture with pull method Pod
  - Import succeeds when using `dv.spec.source.registry.pullMethod: pod` with `dv.spec.source.registry.platform.architecture: arm64`
  - Correct architecture-specific image layers are pulled from multi-arch registry

- **[P0]** Verify multi-arch image matching architecture with pull method Node
  - Import succeeds when using `dv.spec.source.registry.pullMethod: node` with correct architecture
  - Import pod is scheduled on node matching the target architecture

- **[P0]** Validate DataSource pointing to another DataSource
  - DataSource chaining works correctly (DataSource → DataSource reference)
  - Architecture information is preserved through DataSource chain

- **[P1]** Verify multi-arch image import fails gracefully with absent architecture
  - Import fails with clear error when requesting architecture not present in multi-arch image
  - For pull method Pod: import fails with appropriate error message
  - For pull method Node: import pod gets "Unschedulable" condition when no matching nodes exist

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- [x] **Performance Testing**
  - *Rationale:* Out of scope for this test plan; performance testing will be addressed in dedicated performance testing cycles
  - *PM/Lead Agreement:* [ ] Name/Date

- [x] **Security Testing**
  - *Rationale:* Feature does not introduce new security attack vectors; uses existing security model
  - *PM/Lead Agreement:* [ ] Name/Date

- [x] **Usability testing**
  - *Rationale:* UI testing should be done by UI team as part of their standard testing
  - *PM/Lead Agreement:* [ ] Name/Date

- [x] **Backward Compatibility Testing (VM creation with architecture-specific DataSources)**
  - *Rationale:* VM creation using architecture-specific DataSources and legacy DataSource backward compatibility is covered by SSP test plan
  - *PM/Lead Agreement:* [ ] Name/Date

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Validates that CDI correctly imports multi-arch images with proper architecture matching for both Pod and Node pull methods. Verifies DataSource chaining functionality and error handling for missing architectures.

- [x] **Automation Testing** — Confirms tests are expected to be automated
  - *Details:* All test scenarios will be automated and tests will run on multi-arch cluster environments.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Verify that new API changes do not break existing single-architecture import workflows.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Not applicable - explicitly out of scope for this test plan

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* Not applicable - no specific scale requirements defined for this feature

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Not applicable - feature does not introduce new security requirements

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* Not applicable - UI testing covered by UI team

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:*

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - Does the feature maintain backward compatibility with previous API versions and configurations?
  - *Details:* Testing limited to AWS platform (ARM64 workers available).

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Validate VMs migrated and updated successfully after upgrade

- [x] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:*
    - CDI must support architecture-specific registry imports (required for testing)
    - Feature gate `enableMultiArchBootImageImport` must be available and functional

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:*
    - **IUO**: HCO node architecture tracking (`status.nodeInfo`), feature gate activation/propagation, new metrics & alerts, upgrade flows
    - **SSP**: Template creation & utilization, new SSP API (`enableMultipleArchitectures`, `cluster` fields), architecture-specific DataSource generation
    - **Storage**: CDI-importer architecture selection, legacy `DataSource` backward compatibility, new CDI `platform` API
    - **Virt**: VM scheduling to correct architecture nodes, VM migration between same-arch nodes only, upgrade compatibility

**Infrastructure**

- [x] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* Testing is limited to AWS clusters due to ARM64 worker availability. Other cloud platforms are not in scope for initial testing.

#### **3. Test Environment**

- **Cluster Topology:** Multi-arch cluster (3 AMD64 control-plane, 2 AMD64 workers, 1-2 ARM64 workers)

- **OCP & OpenShift Virtualization Version(s):** OCP 4.22 with OpenShift Virtualization 4.22

- **CPU Virtualization:** VT-x (Intel AMD64) and ARM64 virtualization enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** ARM64 worker nodes (AWS ARM64 instances)

- **Storage:** io2-csi storage class (AWS EBS io2 CSI driver)

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** N/A

- **Platform:** AWS (ARM64 workers available)

- **Special Configurations:** Feature gate `enableMultiArchBootImageImport` enabled

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard (multi-arch cluster required)

- **CI/CD:** N/A

- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged** (VEP [dic-on-heterogeneous-cluster](https://github.com/kubevirt/enhancements/tree/main/veps/sig-storage/dic-on-heterogeneous-cluster))
- [x] CDI support for arch-specific registry imports is implemented
- [x] Test environment can be **set up and configured** (multi-arch cluster on AWS)
- [x] Feature gate `enableMultiArchBootImageImport` can be enabled

#### **5. Risks**

**Timeline/Schedule**

- [ ] **Risk:** N/A
  - **Mitigation:** No timeline risks identified at this time
  - *Estimated impact on schedule:* None

**Test Coverage**

- [ ] **Risk:** N/A
  - **Mitigation:** All functional requirements have corresponding test scenarios
  - *Areas with reduced coverage:* None

**Test Environment**

- [x] **Risk:**  N/A
  - **Mitigation:** N/A
  - *Missing resources or infrastructure:*  N/A

**Untestable Aspects**

- [ ] **Risk:** N/A
  - **Mitigation:** N/A
  - *Alternative validation approach:* N/A

**Resource Constraints**

- [ ] **Risk:** N/A
  - **Mitigation:**  N/A
  - *Current capacity gaps:*  N/A

**Dependencies**

- [x] **Risk:**  N/A
  - **Mitigation:**  N/A
  - *Dependent teams or components:*  N/A
**Other**

- [ ] **Risk:** N/A
  - **Mitigation:**  N/A

---

### **III. Test Scenarios & Traceability**

- **[TBD]** — Pull multi-arch image matching architecture with pull method Pod
  - *Test Scenario:* [Tier 1] Verify the import succeeded with dv.spec.source.registry.pullMethod: pod and dv.spec.source.registry.platform.architecture: arm64
  - *Priority:* P0

- **[TBD]** — Pull failed when multi-arch image with absent architecture with pull method Pod
  - *Test Scenario:* [Tier 1] Verify the import failed with dv.spec.source.registry.pullMethod: pod and dv.spec.source.registry.platform.architecture: absent (architecture not in image)
  - *Priority:* P1

- **[TBD]** — Node selector for multi-arch image architecture with pull method Node
  - *Test Scenario:* [Tier 1] Verify the import pod has "Unschedulable" condition with dv.spec.source.registry.pullMethod: node and dv.spec.source.registry.platform.architecture: absent (no matching nodes)
  - *Priority:* P1

- **[TBD]** — DataSource pointing to another DataSource
  - *Test Scenario:* [Tier 1] Verify the import succeeded when DataSource references another DataSource
  - *Priority:* P0

- **[TBD]** — Cross-architecture VM cloning
  - *Test Scenario:* [Tier 2] Attempt cross-arch clone, verify appropriate error message
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - [Name / @github-username]
  - [Name / @github-username]
* **Approvers:**
  - [Name / @github-username]
  - [Name / @github-username]
