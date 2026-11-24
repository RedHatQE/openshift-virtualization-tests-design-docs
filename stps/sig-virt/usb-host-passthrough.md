# Openshift-virtualization-tests Test plan

## **USB Host Passthrough - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [kubevirt/kubevirt#10015](https://github.com/kubevirt/kubevirt/pull/10015) (no VEP; design tracked in that change, the KubeVirt user guide [kubevirt/user-guide#718](https://github.com/kubevirt/user-guide/pull/718), and the OpenShift Virtualization documentation [openshift/openshift-docs#77072](https://github.com/openshift/openshift-docs/pull/77072))
- **Feature Tracking:** https://issues.redhat.com/browse/VIRTSTRAT-294 — support host-side USB device passthrough
- **Epic Tracking:** https://issues.redhat.com/browse/CNV-29334 — GA tracking epic for OpenShift Virtualization 4.17
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: 4.17
- **QE Owner(s):** Samuel Alberstein (@SamAlber)
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-virt

**Document Conventions:**

- USB host passthrough: A USB device plugged into a worker node is assigned to a virtual machine on that same node, so the guest uses the physical device.

### **Feature Overview**

USB host passthrough has been generally available since OpenShift Virtualization 4.17.

A cluster administrator can expose a USB device that is plugged into a worker node, and a workload owner can assign that device to a virtual machine on the same node. The guest then uses the physical hardware as if it were plugged into the virtual machine. Customers use this so a guest can use real USB hardware, such as USB storage.

This STP covers one USB mass-storage device: the guest reads back the data it wrote to the volume, and it can do that again after the virtual machine restarts. The read/write is done from a Linux guest. Windows guests are supported. The other exclusions are in Out of Scope.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value, technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - [VIRTSTRAT-294](https://issues.redhat.com/browse/VIRTSTRAT-294): pass a USB device that is connected to an OpenShift node through to a virtual machine. This STP proves that with one USB mass-storage device.

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* A guest needs to use a real USB device that is plugged into the worker.
  - *List the customer use cases identified:*
    1. As a workload owner, I want to pass USB devices that are plugged into the worker through to my virtual machine so the guest can use that hardware.

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* The two scenarios are testable on a worker with a dedicated USB mass-storage device. Pass criterion: the bytes the guest reads back equal the bytes it wrote.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    1. On the worker where one exposed USB mass-storage device is plugged in, a Linux guest assigned that device reads back the same data it wrote to the volume.
    2. After that Linux virtual machine restarts and the guest is reachable again, the guest reads back the same data it writes to that volume.
  - *Note any gaps or missing criteria:* None for the two scenarios. Live migration is not part of those scenarios (see Out of Scope). Rejecting a device the administrator has not exposed is already covered for other passed-through devices (see Existing coverage).

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Observability: The user-visible outcome is the guest read-back of the data it wrote.
    - Documentation: The customer documentation is published for OpenShift Virtualization ([openshift/openshift-docs#77072](https://github.com/openshift/openshift-docs/pull/77072)) and in the KubeVirt user guide ([kubevirt/user-guide#718](https://github.com/kubevirt/user-guide/pull/718)). The 4.17 general-availability note is [openshift/openshift-docs#81835](https://github.com/openshift/openshift-docs/pull/81835).
    - Scalability: No new scale target. The two scenarios use one device and one virtual machine.
  - *Note any NFRs not covered and why:*
    - Monitoring: No new metrics or alerts are required for this feature.
    - UI: The two scenarios use the command line. The OpenShift console can add a host device, and the devices it offers are PCI and mediated devices. A USB device is not in that list.
    - Performance: No performance target is defined for this cycle.
    - Security: No new security requirement. Rejecting a device the administrator has not exposed is already covered for other passed-through devices and is not retested here (see Existing coverage).

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- **The virtual machine runs on the worker where the USB device is plugged in.** The published documentation places the virtual machine on that same worker. The documentation does not mention live migration. The live-migration requirements say a virtual machine that uses a passed-through device, with GPUs given as the example, cannot be live migrated. A virtual machine with a passed-through USB device cannot be live migrated.
  - *Sign-off:* [Name/Date]

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - No separate kickoff. Behavior was taken from the published documentation and the existing functional tests.
    - Those functional tests use a simulated USB device. They do not use a physical storage device on a worker, and they are currently unreliable.
    - This plan checks a real storage device on a worker, used from the guest, including after restart.
    - Linux and Windows are given the device in the same way. These scenarios read and write the volume from a Linux guest.

- [x] **Technology Challenges**
  - *List identified challenges:* The scenarios need a dedicated USB mass-storage device. The worker and the guest cannot use the same USB device at the same time. Once the virtual machine is using it, the worker no longer has it. A keyboard or virtual media the worker is using must not be the device selected. The documentation's keyboard example is a device meant for the guest. The vendor and product must be read from the device that is plugged in.
  - *Impact on testing approach:* Tests run only on a worker that has a dedicated USB mass-storage device, and they use the vendor and product read from that device. Devices the worker still needs are not passed through.

- [x] **API Extensions**
  - *List new or modified APIs:* The cluster administrator exposes a USB device that is plugged into a worker, and the virtual machine owner assigns that exposed device to a virtual machine.
  - *Testing impact:* Making an exposed device available to virtual machines is already covered and is not repeated here. This STP checks the guest read and write of the storage volume, including after restart.

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* One worker with a USB mass-storage device plugged in. The virtual machine must run on that worker. A second worker is not required.
  - *Impact on test design:* The virtual machine is placed on the worker that has the device. The scenarios do not move the virtual machine, and they do not need a second worker.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

Tests validate that a guest can read and write one USB mass-storage device passed through from the worker it is plugged into, and that the guest can read and write that volume after the virtual machine restarts. The read and write is performed from a Linux guest. Both scenarios run on that worker only. A device plugged into a remote client, live migration, several devices, a device made available by another product, unplugging the device, attaching or removing the device on a running virtual machine, and attaching the device from the web console are not part of these scenarios (see Out of Scope). Rejecting a device the administrator has not exposed, and checks that use a simulated USB device, are existing coverage.

**Testing Goals**

- **[P0]** USB storage passthrough: On the worker where one USB mass-storage device is plugged in, verify a Linux guest reads back the data it wrote to that volume.
- **[P0]** USB storage after restart: On that same worker, verify the Linux guest reads back data it writes to that volume after the virtual machine restarts.

**Existing coverage (not Out of Scope)**

- **A virtual machine that requests a USB device the administrator has not exposed** is already covered by existing tests for other passed-through devices. That is the failure path for these goals. This STP does not add a USB-only copy.

- **A simulated USB device** is covered by existing functional tests for one device and for two identical devices. Those tests are unreliable, so this plan does not use them as the customer check. The customer check is reading and writing the physical storage volume.

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.
No verification activities will be performed for these items, and any related issues found will not be classified as defects for this release.

- **A USB device plugged into a remote client**
  - *Rationale:* The GA epic is specifically not client-side passthrough. This feature passes through a device that is plugged into the worker. It does not forward a device from the computer that is displaying the virtual machine.
  - *PM/Lead Agreement:* [Name/Date]

- **Successful live migration of a virtual machine that is using a passed-through USB device**
  - *Rationale:* The two scenarios do not migrate the virtual machine. The USB documentation does not mention live migration. Live-migration requirements exclude passed-through devices, with GPUs as the example. A virtual machine with a passed-through USB device cannot be live migrated.
  - *PM/Lead Agreement:* [Name/Date]

- **Several different USB devices exposed under one name, and choosing among identical devices on different workers**
  - *Rationale:* The published documentation allows both. This cycle covers one storage device on one worker. The other shapes need extra devices.
  - *PM/Lead Agreement:* [Name/Date]

- **A USB device made available by another product rather than by OpenShift Virtualization**
  - *Rationale:* The documentation covered here is what OpenShift Virtualization publishes. A device made available by another product is a different integration.
  - *PM/Lead Agreement:* [Name/Date]

- **Unplugging the USB device while a virtual machine is using it**
  - *Rationale:* Disruptive to the worker and outside the two customer scenarios.
  - *PM/Lead Agreement:* [Name/Date]

- **Attaching a node USB device to a virtual machine that is already running, and removing that assignment while the virtual machine is running**
  - *Rationale:* [VIRTSTRAT-294](https://issues.redhat.com/browse/VIRTSTRAT-294) lists hotplug and hot-unplug as not required for the first version.
  - *PM/Lead Agreement:* [Name/Date]

- **Attaching the USB device from the web console**
  - *Rationale:* The two scenarios use the command line. The RHEL web console can attach a host device on a RHEL machine. That is not this documentation. The OpenShift console can add a host device, and the devices it offers are PCI and mediated devices. A USB device is not in that list.
  - *PM/Lead Agreement:* [Name/Date]

**Test Limitations**

- **Guest read/write scenarios require a dedicated USB mass-storage device plugged into a worker.** They cannot run on a cluster that does not have that device. Vendor and product identifiers are read from the device that is plugged in.
  - *Sign-off:* [Name/Date]

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* A Linux guest reads and writes a USB mass-storage volume passed through from its worker. The same check is repeated after the virtual machine restarts.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage (all tests are expected to be automated)
  - *Details:* Section III scenarios will be automated in openshift-virtualization-tests. They run only in the lane that has the USB mass-storage device and are not part of the default or gating jobs.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* After automation merges, these scenarios remain the regression check for physical USB storage passthrough on clusters that have the device. Existing virtual USB tablet tests are a different feature and stay as they are.

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* N/A — the scenarios need a physical USB mass-storage device that self-validation clusters do not have.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements (latency, throughput, resource usage)
  - *Details:* Not in scope for functional USB passthrough validation.

- [ ] **Scale Testing** — Validates feature behavior under increased load and at production-like scale (e.g., large number of VMs, nodes, or concurrent operations)
  - *Details:* Scale testing is deferred. One device is used by one virtual machine. No scale-specific concerns identified.

- [ ] **Security Testing** — Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning
  - *Details:* N/A — rejecting a device the administrator has not exposed is already covered for other passed-through devices (see Existing coverage).

- [ ] **Usability Testing** — Validates user experience and accessibility requirements
  - *Details:* N/A — the two scenarios use the command line. The OpenShift console list of host devices does not offer a USB device.

- [ ] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* N/A — no specific metrics required for USB host passthrough.

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms, versions, and configurations
  - *Details:* OpenShift Virtualization 4.17 and later, on the worker that has the USB mass-storage device.
  - *Backward compatibility:* No known API changes affecting backward compatibility. The feature is already generally available.

- [ ] **Upgrade Testing** — Validates upgrade paths from previous versions, data migration, and configuration preservation
  - *Details:* Upgrade path evaluated; no USB-passthrough-specific upgrade concerns identified. Not in scope for this cycle.

- [ ] **Dependencies** — Blocked by deliverables from other components/products. Identify what we need from other teams before we can test.
  - *Details:* N/A — no outstanding deliverable from another team. The guest scenarios still need a USB mass-storage device plugged into a worker; that is a test-environment constraint, not a component dependency.

- [ ] **Cross Integrations** — Does the feature affect other features or require testing by other teams? Identify the impact we cause.
  - *Details:* N/A — no other SIG owns part of this feature.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing? Consider cloud-specific features.
  - *Details:* N/A — the worker must list the USB mass-storage device. A normal cloud worker does not. Bare metal is the usual way to plug the device into the worker. An OpenStack worker is usable only when that device is visible on the worker.

#### **3. Test Environment**

- **Cluster Topology:** One worker that lists the USB mass-storage device. Bare metal is the usual way to plug it in. An OpenStack worker is usable only when that device is visible on the worker.
- **OCP & OpenShift Virtualization Version(s):** OpenShift Virtualization 4.17 or later (GA)
- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled on the worker that runs the virtual machine
- **Compute Resources:** A worker that can run one Linux virtual machine
- **Special Hardware:** One dedicated USB mass-storage device plugged into that worker
- **Storage:** Any storage class that can host the Linux virtual machine disk (e.g., ocs-storagecluster-ceph-rbd-virtualization)
- **Network:** OVN-Kubernetes
- **Required Operators:** OpenShift Virtualization
- **Platform:** Any platform whose worker lists the USB device. Bare metal provides that directly.
- **Special Configurations:** The USB mass-storage device is exposed for virtual machine use before the scenarios start. The virtual machine is placed on the worker that has the device.

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard
- **CI/CD:** Tests use marker-based CI lane selection so they run only in the environment that has the USB mass-storage device. They are not part of default or gating jobs.
- **Other Tools:** N/A

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [x] USB host passthrough is available and functional in the target OpenShift Virtualization version (GA since 4.17)

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Guest scenarios cannot start until a worker with a dedicated USB mass-storage device is assigned.
  - **Mitigation:** Automate against the published documentation and run both scenarios when the device is available.
  - *Estimated impact on schedule:* Both scenarios wait on that worker. There is no other schedule dependency.
  - *Sign-off:* [Name/Date]

**Test Coverage**

- **Risk:** Existing functional tests that use a simulated USB device are unreliable, so they are not a reliable signal that passthrough still works.
  - **Mitigation:** The guest read and write on a physical storage device is the customer check. Do not treat those simulated tests as coverage for this plan.
  - *Areas with reduced coverage:* Simulated device checks, and a Windows guest. These scenarios read and write the volume from a Linux guest. A Windows guest uses its own support for the same device, and that is not covered.
  - *Sign-off:* [Name/Date]

**Test Environment**

- **Risk:** Selecting a USB device the worker is already using, such as its keyboard or virtual media, gives that device to the guest and the worker loses it.
  - **Mitigation:** Use only a dedicated mass-storage device. Record its vendor and product from the worker before exposing it.
  - *Missing resources or infrastructure:* Default and cloud clusters have no dedicated USB mass-storage device. The scenarios need a worker where that storage device is the one exposed to virtual machines.
  - *Sign-off:* [Name/Date]

**Untestable Aspects**

- **None** — the read/write scenarios are testable on a worker with a dedicated USB mass-storage device.

**Resource Constraints**

- **Risk:** Only one such device may be available, so scenarios that need two devices or two workers cannot be run in this cycle.
  - **Mitigation:** Limit this cycle to one device on one worker, as listed in Out of Scope.
  - *Current capacity gaps:* A second USB device, or a second worker with the same device.
  - *Sign-off:* [Name/Date]

**Dependencies**

- **None** — no external component delivery is outstanding. The feature is already generally available. The plugged-in device is an environment constraint, tracked under Test Environment and Resource Constraints.

---

### **III. Test Scenarios & Traceability**

- **[CNV-11032](https://issues.redhat.com/browse/CNV-11032)** — As a workload owner, I want a USB mass-storage device that is plugged into my worker passed through to my virtual machine so the guest can use it.
  - *Test Scenario:* [Tier 2] On the worker that has the exposed USB mass-storage device, start a Linux virtual machine that is assigned that device. From the guest, write data to the USB storage volume and read it back. The data read back equals the data written.
  - *Priority:* P0

- **[CNV-11033](https://issues.redhat.com/browse/CNV-11033)** — As a workload owner, I want that USB storage volume to keep working after I restart the virtual machine.
  - *Test Scenario:* [Tier 2] Restart the virtual machine from the previous scenario. After it is running and the guest is reachable, write data to the USB storage volume and read it back. The data read back equals the data written.
  - *Priority:* P0

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - QE Members (OCP-V): [Akriti Gupta](@akri3i), [Samuel Alberstein](@SamAlber)
  - Principal QE (OCP-V): [Denys Shchedrivyi](@dshchedr), [Vasiliy Sibirskiy](@vsibirsk)
  - Principal Developer (OCP-V): [Victor Toso](@victortoso)
  - Product Manager/Owner: [Martin Tessun](@mtessun)

* **Approvers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - Principal QE (OCP-V): [Denys Shchedrivyi](@dshchedr), [Vasiliy Sibirskiy](@vsibirsk)
  - Principal Developer (OCP-V): [Victor Toso](@victortoso)
  - Product Manager/Owner: [Martin Tessun](@mtessun)
