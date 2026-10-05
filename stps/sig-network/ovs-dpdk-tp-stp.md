# Openshift-virtualization-tests Test plan

## **OVS-DPDK Network Binding In Virtual Machines - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):**
  - Scope defined by [CNV-88618](https://redhat.atlassian.net/browse/CNV-88618)
  - Utilizing the backing DRA driver [VEP 183](https://github.com/kubevirt/enhancements/blob/main/veps/sig-network/183-dra-network/vep.md)
- **Feature Tracking:** https://issues.redhat.com/browse/VIRTSTRAT-639
- **Epic Tracking:** https://redhat.atlassian.net/browse/CNV-88618
- **Feature Maturity:**
  - DP: N/A
  - TP: 5.1
  - GA: 5.2
- **QE Owner(s):** Yossi Segev (ysegev@redhat.com)
- **Owning SIG:** sig-network
- **Participating SIGs:** sig-network

**Document Conventions:**

- OVS-DPDK: High-performance virtual networking binding used as the concrete test implementation for this STP. Architecture and driver behavior: [VEP 183](https://github.com/kubevirt/enhancements/blob/main/veps/sig-network/183-dra-network/vep.md) and the [OVS-DPDK DRA driver documentation](https://github.com/k8snetworkplumbingwg/dra-driver-ovsdpdk/).
- DRA: Dynamic Resource Allocation — see [VEP 183](https://github.com/kubevirt/enhancements/blob/main/veps/sig-network/183-dra-network/vep.md) for design details
- RC: ResourceClaim — a Kubernetes object requesting specific devices for a single workload instance
- RCT: ResourceClaimTemplate — a Kubernetes object that generates a per-VM ResourceClaim, required for live migration of VMs with DRA-backed devices
- ODC: OvsDpdkConfig — the CRD used to configure the OVS-DPDK DRA driver ([definition](https://github.com/k8snetworkplumbingwg/dra-driver-ovsdpdk/#ovsdpdkconfig-cluster-scoped))
- ODRP: OvsDpdkResourcePolicy — a CRD that map each OVS-DPDK bridge (as DRA-allocatable resource) on a node ([definition](https://github.com/k8snetworkplumbingwg/dra-driver-ovsdpdk/#ovsdpdkresourcepolicy-namespaced))
- Also note that when not explicitly mentioned otherwise, the term "network plugin" refers to the OVS-DPDK network binding plugin.

### **Feature Overview**

Performance-intensive VM workloads need higher network throughput and lower latency than typical virtual attachments provide. This STP covers the Tech Preview (OCP 5.1) introduction of OVS-DPDK network binding for OpenShift Virtualization VMs: VM owners can attach a high-throughput, low-latency interface and live-migrate VMs that use the supported ResourceClaimTemplate-backed configuration. Implementation follows [VEP 183](https://github.com/kubevirt/enhancements/blob/main/veps/sig-network/183-dra-network/vep.md).

> **Note on TP testing scope:** Although this feature ships as Tech Preview in OCP 5.1, QE is providing full test coverage as an exceptional commitment to the target customer. This is not the standard TP testing approach.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - VM users can connect their VMs to the network through a high-throughput, low-latency interface.
    - VM users can live-migrate a VM that uses a high-throughput, low-latency interface.
    - A cluster admin can deploy and enable the components required to make this capability available.

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* VM owners can attach a high-performance network interface to workloads that need it; cluster admins can deploy and enable the capability on supported bare-metal environments.
  - *List the customer use cases identified:*
    - As a VM owner, I want to run a DPDK application in my VM by using OVS-DPDK network binding, to gain high-throughput and low-latency.
    - As a VM owner, I want to live-migrate an OVS-DPDK based VM.
    - As a cluster admin, I want to enable DPDK network acceleration.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* Core flows are testable. The OVS-DPDK DRA driver setup is applied at cluster deployment time (day-0; see CNV-96151 for the CI lane implementation tracking issue), so it will be eventually validated by the dedicated tests.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    1. A VM with OVS DPDK network binding plugin starts successfully and has connectivity through the assigned device.
    2. A VM with OVS DPDK network binding plugin can be live-migrated (limited to binding using ResourceClaimTemplate); an active connection established before migration is maintained and restored after migration completes, and the VM is reachable on the destination node.
    3. VMs with OVS-DPDK network devices on a bridge configured with a non-default MTU can exchange traffic using the full jumbo-frame payload size, with no fragmentation.
    4. A VM with two OVS-DPDK network interfaces (several requests in the same ResourceClaim, not multiple devices on a single request), starts successfully and has connectivity through both interfaces.
    5. Two VMs requesting the same device (same OVS-DPDK device class), each using different ports (separate ResourceClaims), can be co-scheduled on the same node and exchange traffic with each other.
    - *Note any gaps or missing criteria:* None for TP scope.

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Security: No new RBAC or authentication changes introduced; existing Kubernetes DRA access controls and webhook validations apply.
    - Scalability: No new scale requirements for TP phase. Device scheduling and claim allocation follow the [existing DRA scalability model](https://github.com/kubevirt/enhancements/blob/main/veps/sig-compute/10-dra-devices/vep.md#scalability) (metadata/API load and local device metadata reads). Live migration of RCT-backed OVS-DPDK attachments still depends on platform-wide limits that already apply to OpenShift Virtualization (for example, cluster-wide concurrent live-migration caps) and on per-node OVS-DPDK device availability on the migration destination. Those inherited constraints are acknowledged; this feature does not introduce new scale targets beyond them. TP functional tests use single-VM (low-count) migration on the bare-metal test cluster, not max cluster parallelism.
    - Monitoring/Observability: No new metrics or alerts required for TP phase.
    - UI: Feature is API-driven; no new UI components required. UI team confirmed no testing needed for TP.
    - Performance: No performance requirements defined for TP phase; performance validation is deferred to GA, and is anyway owned by the dedicated performance team and is outside this team's scope.
    - Documentation: Tracked in https://redhat.atlassian.net/browse/CNV-98307
  - *Note any NFRs not covered and why:*
    - Portability (cloud): OVS-DPDK requires bare-metal, which we currently don't have with cloud platform support; therefore - cloud platform testing is not applicable.

#### **2. Known Limitations**

- **Hot-plug/hot-unplug:** Adding or removing DRA-backed network interfaces on a running VM is not supported.
  - *Sign-off:* Ronen Sde-Or / 2026-Sep-06

- **ResourceClaim live migration:** Live migration is only supported for VMs whose backing driver devices were allocated via ResourceClaimTemplate. VMs using direct ResourceClaim-backed devices cannot be live-migrated, as ResourceClaim is a node-specific resource.
  - *Sign-off:* Ronen Sde-Or / 2026-Sep-06

- **Mixed network sources:** Mixing DRA and Multus-based network sources on the same VM is not supported.
  - *Sign-off:* Ronen Sde-Or / 2026-Sep-06

- **Multiple devices per request (`count > 1`):** Requesting more than one device from a single `devices.requests` entry (DRA `count > 1` / consumable-capacity style allocation) via a ResourceClaim or ResourceClaimTemplate has not been validated and is not a supported configuration. This does not apply to AC #4 / [TG-7]: multiple named requests in one claim (each with default count 1), which the [OVS-DPDK DRA driver](https://github.com/k8snetworkplumbingwg/dra-driver-ovsdpdk) documents as supported.
  - *Sign-off:* Ronen Sde-Or / 2026-Sep-06

- **Interface link-state management:** Setting the interface link-state via the VM spec is not supported for OVS-DPDK network devices.
  - *Sign-off:* Ronen Sde-Or / 2026-Sep-17

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - DRA replaces the traditional device-plugin approach: users describe the network device they need using Kubernetes resource claim objects (ResourceClaim or ResourceClaimTemplate), and the Kubernetes scheduler allocates devices with full awareness of device constraints and placement requirements.
    - Once the DRA driver provisions the device, a network binding plugin configures the VM's network interface. KubeVirt orchestrates between the DRA driver and the binding plugin.
    - A feature gate gates all new API surface; disabling the gate rejects any DRA network source at admission time.
    - Rollback from an enabled feature gate requires removing all VMs using DRA network devices before disabling the gate.

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Testing requires a functional external OVS-DPDK DRA driver. Setting up OVS-DPDK as a DRA driver involves significant infrastructure configuration (hugepages, OVS configuration, DPDK-capable NICs or software equivalent).
    - The OVS-DPDK DRA driver setup is applied at cluster deployment time (day-0). This approach was selected to ensure environment consistency across test runs; see CNV-96151 for the CI lane implementation tracking issue.
    - The feature requires Kubernetes 1.36+ for exposing device metadata from the DRA driver to the containers that need it, and accessing it (as detailed in https://kubernetes.io/docs/concepts/resource-management/dynamic-resource-allocation/dra-observability/#device-metadata). OCP 5.1, which is based on Kubernetes 1.37, meets this version requirement.
  - *Impact on testing approach:* Tests require a dedicated environment with the OVS-DPDK DRA driver deployed and validated before test execution. A standard shared CI lane is not suitable without driver setup; a dedicated CI lane is needed.

- [x] **API Extensions**
  - *List new or modified APIs:* A new DRA network source type is added to the VM network configuration API. Users reference their DRA resource claims from the VM spec using the new source type. A feature gate controls availability of this new source type.
  - *Testing impact:* Test scenarios cover both valid DRA network configurations and invalid ones (except for cases that are designed to be rejected by admission webhooks, which are covered in unit-tests). Existing tests for Multus-based networks are unaffected.

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* All tests run on a bare-metal cluster (3-master/3-worker) with DPDK-capable physical NICs and IOMMU enabled on worker nodes. OVS-DPDK requires real hardware and cannot run on a virtualized cluster. Multi-node topology is required for live migration scenarios.
  - *Impact on test design:* All scenarios run on the bare-metal cluster. Live migration scenarios require at least two worker nodes, which the 3-worker topology satisfies.

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0] [TG-1]** Verify that a VM with an OVS-DPDK network attachment starts successfully and has network connectivity through that interface.
  - *Setup:* Device allocated via ResourceClaimTemplate; VM uses the OVS-DPDK network binding plugin.
- **[P0] [TG-14]** Verify that two VMs with OVS-DPDK network attachments can communicate and exchange traffic with each other (e.g. using a PMD application such as testpmd between guests).
  - *Setup:* Two VMs each with an OVS-DPDK attachment; L2 reachability per test harness (see test case for topology).
- **[P0] [TG-2]** Verify that a VM with an OVS-DPDK network attachment can be live-migrated between nodes; an active connection established before migration is maintained or re-established within normal migration bounds after migration completes, and the VM is reachable on the destination node.
  - *Setup:* Backing device allocated via ResourceClaimTemplate (required for live migration in this release).
- **[P1] [TG-3]** Verify that a VM with an OVS-DPDK network attachment starts successfully and has network connectivity through that interface when the device is allocated without a per-VM claim template.
  - *Setup:* Direct ResourceClaim (not ResourceClaimTemplate); network binding plugin as in the test scenario.
- **[P1] [TG-4]** Verify that a VM with two OVS-DPDK network interfaces starts successfully and traffic flows independently on each interface.
  - *Setup:* Each interface backed by a separate ResourceClaimTemplate-generated claim.
- **[P1] [TG-5]** Verify that after the OVS-DPDK DRA driver is restarted, existing VMs with OVS-DPDK network attachments remain reachable and newly created VMs can start and achieve connectivity.
  - *Rationale:* Ensures persistency across driver restart for running workloads and new VM creation.
- **[P1] [TG-13]** Verify that when OVS is restarted, VMs with OVS-DPDK network attachments remain reachable.
  - *Rationale:* Validates recovery of VM networking after OVS restart on the node.
- **[P1] [TG-6]** Verify that two VMs with OVS-DPDK network attachments can exchange traffic at full jumbo-frame payload size with no fragmentation.
  - *Setup:* OVS bridge configured with a non-default MTU as specified in the test scenario.
- **[P1] [TG-7]** Verify that a VM with two OVS-DPDK network interfaces starts successfully and has connectivity through both interfaces when both interfaces are provisioned from a single device claim.
  - *Setup:* One ResourceClaim with two named `devices.requests` entries (one device per request; not `count > 1` on a single request).
- **[P1] [TG-8]** Verify that two VMs with OVS-DPDK network attachments on the same node can exchange traffic with each other.
  - *Setup:* Each VM uses its own ResourceClaim against the same OVS-DPDK device class; scheduling places both VMs on one node.
- **[P2] [TG-9]** Verify that a VM with an OVS-DPDK network attachment can be live-migrated with connectivity preserved after the OVS-DPDK DRA driver has been restarted on both source and destination nodes.
  - *Setup:* ResourceClaimTemplate-backed allocation; driver restart on source and destination before migration.
- **[P2] [TG-10]** Verify that two VMs on different nodes, each with an OVS-DPDK network attachment, start successfully and can exchange traffic over their respective interfaces.
  - *Setup:* Separate ResourceClaim per VM; same device class on each node.
- **[P2] [TG-11]** Verify that a VM with an OVS-DPDK network attachment remains running after an OCP minor-version upgrade and network connectivity can be re-established after the upgrade completes.
  - *Setup:* ResourceClaimTemplate-backed OVS-DPDK network attachment.
- **[P2] [TG-12]** Verify that a VM with an OVS-DPDK network device retains network connectivity after a guest reboot.

**Out of Scope (Testing Scope Exclusions)**

- **Performance benchmarking of OVS-DPDK throughput and latency**
  - *Rationale:* No performance requirements are defined for the TP phase; performance validation is deferred to GA, and is anyway owned by the dedicated performance team and is outside this team's scope.
  - *PM/Lead Agreement:* Ronen Sde-Or / 2026-Sep-06

- **Scheduling of non-DRA NUMA-aware plugin for OVS-DPDK resources**
  - *Rationale:* Exposing OVS-DPDK resources via the legacy device binding plugin for NUMA-aware pod/VM scheduling is a separate mechanism from DRA. It requires bare-metal with dual-NUMA nodes. This STP covers DRA-based device consumption only.
  - *PM/Lead Agreement:* Ronen Sde-Or / 2026-Sep-06

- **Live migration failure path - the destination node cannot allocate the OVS-DPDK device required by the ResourceClaimTemplate**
  - *Rationale:* The nodes configuration is set on deployment time and not changed on day-2, and is similar on all nodes. This STP covers scenarios under the assumption of fixed, similar nodes configurations.
  - *PM/Lead Agreement:* Ronen Sde-Or / 2026-Sep-08

**Test Limitations**

- **DPDK applications inside VMs:** Running DPDK workloads inside a VM (vfio passthrough of the vhost-user device) requires vIOMMU and hugepages, hence testing is limited to QE bare-metal clusters.
  - *Sign-off:* Ronen Sde-Or / 2026-Sep-06

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Validate VM creation with OVS-DPDK network devices (via RC and RCT), connectivity establishment, and live migration with RCT-backed devices.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* All new test scenarios will be automated. A dedicated CI lane is required due to OVS-DPDK hardware and driver setup requirements; the standard shared lane cannot be used without driver setup (see Section II.3.1).

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Existing secondary network and live migration test suites run as regression to confirm no impact from the new DRA network source type. Enabling the feature gate must not affect existing VMs using Multus-based networks (i.e. nodes that can now host OVS DPDK VMs, can also continue hosting multus VMs, or in other words - VMs without DPDK network can run on the same node as DPDK VMs).

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* Not applicable. DRA network device tests require a dedicated OVS-DPDK driver setup and special hardware; they are not suitable for the self-validation package.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Not applicable for TP phase; no performance requirements defined. Deferred to GA.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale
  - *Details:* Not applicable for TP phase; no dedicated scale test plan. Inherited platform limits (including cluster-wide live-migration parallelism) and per-node OVS-DPDK device capacity can constrain scheduling and migration in production; this STP does not add scale scenarios to validate those limits.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* Not applicable; no new RBAC or authentication changes introduced. Webhook admission validation for invalid DRA network configurations is covered by unit tests in the KubeVirt codebase (see [CNV-97357](https://redhat.atlassian.net/browse/CNV-97357)).

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* Not applicable. Feature is API-driven; no new UI components or CLI commands introduced. UI team confirmed no testing required for TP phase.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* Not applicable for TP phase; no new metrics or alerts introduced.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* Existing Multus-based VM tests run as regression (when feature-gate enabled) to confirm no impact from OVS-DPDK network workloads on the same cluster and nodes.

- [x] **Upgrade Testing** — Validates upgrade paths from previous versions (starting from 5.1), data migration, and configuration preservation
  - *Details:* Validate that a VM with an RCT-backed network device remains functional after an OCP minor-version upgrade with connectivity re-established after the upgrade (see P2 testing goal).

- [x] **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* Testing depends on a stable external OVS-DPDK DRA driver being available for QE use. Network binding plugin must be registered and functional before test execution begins. OVS must function properly as the base for OVS DPDK. Track driver and binding plugin readiness against the CNV-88618 epic.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* The integration is with the DRA device, the coverage suggested in this STP will cover that (by the network team). The live migration flow is affected and will also be covered by the network tests; any regressions in VM scheduling or migration with DRA devices must be caught during testing.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* Not applicable. OVS-DPDK requires bare-metal, and the cloud platforms that we use are currently not available on bare-metal.

#### **3. Test Environment**

**Environment — Bare-metal cluster (all tests)**

- **Cluster Topology:** 3-master/3-worker bare-metal cluster (either HA or compact); multi-node worker topology required for live migration scenarios
- **OCP & OpenShift Virtualization Version(s):** OCP 5.1 with OpenShift Virtualization 5.1 (assures Kubernetes server version ≥ 1.36)
- **CPU:** Hardware virtualization enabled (VT-x / AMD-V); IOMMU enabled (VT-d / AMD-Vi) on all worker nodes
- **Compute Resources:** Minimum per worker node: 32 physical CPUs, 64 GB RAM; hugepages configured for OVS-DPDK
- **Special Hardware:** DPDK-capable physical NICs on worker nodes; dual-NUMA node topology available on workers
- **Storage:** ocs-storagecluster-ceph-rbd-virtualization (ReadWriteMany access mode, Block volume mode — required for live-migration scenarios)
- **Network:** OVN-Kubernetes; OVS-DPDK configured as a DRA network device on worker nodes
- **Required Operators:** N/A
- **Platform:** Bare-metal
- **Special Configurations:** OVS-DPDK DRA driver deployed and configured on worker nodes at cluster provisioning time (day-0; see CNV-96151); `NetworkDevicesWithDRA` feature gate enabled; network binding plugin registered in the HyperConverged CR.
- **Not suitable for:** Cloud platforms (OVS-DPDK requires bare-metal hardware, and we currently don't have cloud-platform bare-metal clusters).

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** Dedicated CI lane required — OVS-DPDK DRA driver setup cannot be assumed in standard shared lanes

- **Other Tools:** OVS-DPDK DRA driver (external dependency)

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged**
- [ ] OCP 5.1 version confirmed (which necessarily assures Kubernetes server version ≥ 1.36)
- [ ] Test environment is **set up and configured** with OVS-DPDK DRA driver deployed and functional (see Section II.3)
- [ ] Network binding plugin is registered for the OVS-DPDK device type in the HCO CR

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** The OVS-DPDK DRA driver and test environment setup are complex and require cross-team coordination.
  - **Mitigation:** The setup approach (day-0) has been decided; CI lane implementation is tracked under [CNV-96151](https://redhat.atlassian.net/browse/CNV-96151).
  - *Estimated impact on schedule:* The [setup coverage](https://redhat.atlassian.net/browse/CNV-96151) is part of the epic, thus planned to be obtained within the OCP 5.1 time frame.
  - *Sign-off:* Ronen Sde-Or / 2026-Sep-06

**Test Coverage**

- **Risk:** Testing is scoped to OVS-DPDK as the only concrete DRA network driver for this release. Other DRA network drivers, if introduced in future releases, will require separate test coverage.
  - **Mitigation:** Design test assertions against user-observable outcomes (connectivity, migration success) rather than OVS-DPDK-specific internals, so tests remain applicable to future drivers.
  - *Sign-off:* Ronen Sde-Or / 2026-Sep-06

**Test Environment**

- **Risk:** The bare-metal cluster requires DPDK-capable physical NICs, IOMMU, and hugepages configuration. Environment provisioning is complex and depends on infrastructure team support and hardware availability.
  - **Mitigation:** Environment setup is treated as a day-0 activity tracked under CNV-96151. Hardware requirements are documented explicitly so provisioning can start early.
  - *Missing resources or infrastructure:* Bare-metal cluster with DPDK-capable NICs required; tracked under [CNV-96151](https://redhat.atlassian.net/browse/CNV-96151) to be provided by DevOps.
  - *Sign-off:* Ronen Sde-Or / 2026-Sep-06

**Resource Constraints**

- **Risk:** Setting up and maintaining the OVS-DPDK DRA driver configuration on the bare-metal cluster requires cross-team expertise spanning OVS-DPDK and KubeVirt DRA. Insufficient expertise within QE may slow environment setup and test development.
  - **Mitigation:** Coordinate with the DevOps team for environment setup assistance during the initial test development phase. Document the setup procedure (ODC/ODRP configuration, driver deployment) to reduce ongoing dependency.
  - *Current capacity gaps:* OVS-DPDK DRA driver operational expertise within QE.
  - *Sign-off:* Ronen Sde-Or / 2026-Sep-06

**Dependencies**

- **Risk:** Test execution depends on a stable and functional external OVS-DPDK DRA driver being available for QE use. If the driver, and the OVS start scripts, are not ready or stable, all DRA network device test scenarios are blocked.
  - **Mitigation:** Track driver readiness against the CNV-88618 epic; do not begin test execution until the driver is confirmed stable for QE use. Coordinate with the DRA driver team for early access to a test build.
  - *Dependent teams or components:* OVS-DPDK DRA driver team; network binding plugin team; KubeVirt DRA core team.
  - *Sign-off:* Ronen Sde-Or / 2026-Sep-06

---

### **III. Test Scenarios & Traceability**

| Requirement ID   | Requirement Summary                                                                                                                                                        | Test Scenario(s)                                                                                                                                                                                                                                                                                               | Tier | Priority |
|:-----------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----|:---------|
| CNV-88618 (epic) | As a VM owner, I want to attach an OVS-DPDK network interface to my VM so it can exchange traffic over a high-throughput, low-latency connection.                          | [TG-1] Verify that a VM with an OVS-DPDK network attachment starts successfully and has network connectivity through that interface. *Setup:* device allocated via ResourceClaimTemplate (see Section II.1 [TG-1]). | Tier 1 | P0 |
|                  | As a VM owner, I want two VMs with OVS-DPDK network interfaces to exchange traffic with each other.                                                                        | [TG-14] Verify that two VMs with OVS-DPDK network attachments can communicate and exchange traffic with each other (e.g. using a PMD application such as testpmd between guests). | Tier 1 | P0 |
|                  | As a VM owner, I want to live-migrate my VM that uses an OVS-DPDK network interface so I can perform node maintenance and remain reachable on the destination node.        | [TG-2] Verify that a VM with an OVS-DPDK network attachment can be live-migrated between nodes; an active connection established before migration is maintained or re-established within normal migration bounds after migration completes, and the VM is reachable on the destination node. *Setup:* ResourceClaimTemplate-backed allocation (see Section II.1 [TG-2]). | Tier 2 | P0 |
|                  | As a VM owner, I want to attach an OVS-DPDK network interface to my VM so it can exchange traffic over a high-throughput, low-latency connection.                          | [TG-3] Verify that a VM with an OVS-DPDK network attachment starts successfully and has network connectivity through that interface. *Setup:* device allocated via a direct ResourceClaim, not a per-VM ResourceClaimTemplate (see Section II.1 [TG-3]). | Tier 1 | P1 |
| AC #3            | As a VM owner, I want jumbo-frame traffic to traverse my OVS-DPDK interface without fragmentation.                                                                         | [TG-6] Verify that two VMs with OVS-DPDK network attachments can exchange traffic at full jumbo-frame payload size with no fragmentation. *Setup:* OVS bridge with non-default MTU (see Section II.1 [TG-6]). | Tier 1 | P1 |
|                  | As a VM owner, I want two independent OVS-DPDK network interfaces on my VM so traffic can flow on each interface separately.                                               | [TG-4] Verify that a VM with two OVS-DPDK network interfaces starts successfully and traffic flows independently on each interface. *Setup:* each interface backed by a separate ResourceClaimTemplate-generated claim (see Section II.1 [TG-4]). | Tier 1 | P1 |
| AC #4            | As a VM owner, I want two OVS-DPDK network interfaces on my VM and connectivity through both connections.                                                                  | [TG-7] Verify that a VM with two OVS-DPDK network interfaces starts successfully and has connectivity through both interfaces. *Setup:* one ResourceClaim with two named `devices.requests` entries (one device per request; not `count > 1` on a single request) (see Section II.1 [TG-7]). | Tier 1 | P1 |
| AC #5            | As a VM owner, I want two VMs on the same node with OVS-DPDK interfaces to exchange traffic with each other.                                                            | [TG-8] Verify that two VMs with OVS-DPDK network attachments on the same node can exchange traffic with each other. *Setup:* each VM uses its own ResourceClaim against the same OVS-DPDK device class; both VMs scheduled on one node (see Section II.1 [TG-8]). | Tier 1 | P1 |
|                  | As a VM owner, I want my VM to remain reachable on its OVS-DPDK interface after the OVS-DPDK network driver is restarted.                                                  | [TG-5] Verify that after the OVS-DPDK DRA driver is restarted, existing VMs with OVS-DPDK network attachments remain reachable. | Tier 2 | P1 |
|                  | As a VM owner, I want to create a new VM with an OVS-DPDK interface and reach the network after the network driver was restarted.                                          | [TG-5] Verify that after the OVS-DPDK DRA driver is restarted, newly created VMs can start and achieve connectivity. | Tier 2 | P1 |
|                  | As a VM owner, I want my VM to remain reachable on its OVS-DPDK interface after OVS is restarted on the node. | [TG-13] Verify that when OVS is restarted, VMs with OVS-DPDK network attachments remain reachable. | Tier 2 | P1 |
|                  | As a VM owner, I want my VM with an OVS-DPDK interface to keep running and regain network connectivity after a cluster upgrade.                                            | [TG-11] Verify that a VM with an OVS-DPDK network attachment remains running after an OCP minor-version upgrade and network connectivity can be re-established after the upgrade completes. *Setup:* ResourceClaimTemplate-backed attachment (see Section II.1 [TG-11]). | Tier 2 | P2 |
|                  | As a VM owner, I want to live-migrate my VM with an OVS-DPDK interface after the network driver was restarted on the source and destination nodes.                         | [TG-9] Verify that a VM with an OVS-DPDK network attachment can be live-migrated with connectivity preserved after the OVS-DPDK DRA driver has been restarted on both source and destination nodes. *Setup:* ResourceClaimTemplate-backed allocation; driver restart on both nodes before migration (see Section II.1 [TG-9]). | Tier 2 | P2 |
|                  | As a VM owner, I want two VMs on different nodes, each with an OVS-DPDK interface, to exchange traffic with each other.                                                    | [TG-10] Verify that two VMs on different nodes, each with an OVS-DPDK network attachment, start successfully and can exchange traffic over their respective interfaces. *Setup:* separate ResourceClaim per VM; same device class on each node (see Section II.1 [TG-10]). | Tier 2 | P2 |
|                  | As a VM owner, I want my OVS-DPDK network interface to remain usable after I reboot the guest.                                                                             | [TG-12] Verify that a VM with an OVS-DPDK network device retains network connectivity after a guest reboot. | Tier 2 | P2 |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Development: Nir Dothan (@nirdothan), Ananya Banerjee (@frenzyfriday), Bruno Gomes (@brunogomes011), Maxime Coquelin (@mcoqueli), Adrian Moreno (@amorenoz)
  - QE: Asia Khromov (@azhivovk), Yossi Segev (@yossisegev)
* **Approvers:**
  - QE Lead: Ruth Netser (@rnetser)
  - Dev Lead: Orel Misan (@orelmisan)
  - Product Manager: Ronen Sde-Or (@ronensdeor)
