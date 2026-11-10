# Openshift-virtualization-tests Test plan

## **ARM64 UEFI Secure Boot - Quality Engineering Plan**

> **Status: initial DP draft** — minimal scope for the v5.1.0 Developer Preview.
> To be expanded for TP (v5.3.0, [CNV-100819](https://redhat.atlassian.net/browse/CNV-100819)).

### **Metadata & Tracking**

- **Enhancement(s):** [kubevirt/enhancements#227](https://github.com/kubevirt/enhancements/issues/227)
- **Feature Tracking:** [CNV-81765](https://redhat.atlassian.net/browse/CNV-81765)
- **Epic Tracking:** [CNV-81765](https://redhat.atlassian.net/browse/CNV-81765) (DP),
  [CNV-100819](https://redhat.atlassian.net/browse/CNV-100819) (TP)
- **Feature Maturity:**
  - DP: v5.1.0
  - TP: v5.3.0
  - GA: TBD
- **QE Owner(s):** TBD
- **Owning SIG:** sig-virt
- **Participating SIGs:** sig-virt

**Document Conventions:**

- **UEFI Secure Boot** — firmware validates the boot chain (shim → grub/kernel) against
  enrolled keys; unsigned components fail to boot
- **uefi-vars device** — QEMU mechanism for aarch64 UEFI variable storage, replacing the
  x86_64 SMM-based approach
- **Firmware auto-selection** — libvirt selects firmware via JSON descriptors shipped by
  edk2-aarch64 instead of KubeVirt hardcoding loader paths

### **Feature Overview**

Enable UEFI Secure Boot for ARM64 (aarch64) guest VMs in OpenShift Virtualization, using the
same `secureBoot` API field as x86_64. On aarch64 the mechanism differs from x86_64: firmware
auto-selection plus the QEMU uefi-vars device, guarded by the `ARM64SecureBoot` feature gate.
Customers with security-compliance requirements can run signed boot chains on ARM64 VMs.

For DP (v5.1.0) the feature gate is **disabled by default**; the scope below validates
explicit opt-in only.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - Same `secureBoot` API field as x86_64 (portable VM definitions)
  - Requires the `ARM64SecureBoot` feature gate and a host stack with QEMU 10.0+,
    libvirt and edk2-aarch64 secure-boot firmware
  - Delivered as Alpha in kubevirt v1.10.0
    ([kubevirt/kubevirt#17135](https://github.com/kubevirt/kubevirt/pull/17135))

- [x] **Understand Value and Customer Use Cases**
  - Security-compliance workloads on ARM64 hardware require a signed boot chain
  - As a VM owner, I can set `secureBoot: true` on an ARM64 VM so only signed boot
    components load

- [x] **Testability**
  - All requirements observable via guest state (`mokutil --sb-state`, dmesg secure-boot
    messages) and VM lifecycle status; no untestable requirements identified

- [x] **Acceptance Criteria**
  - With the feature gate enabled, an ARM64 VM with `secureBoot: true` boots and Secure
    Boot is active inside the guest
  - Unsigned boot components fail to boot
  - With the gate disabled, `secureBoot: true` on ARM64 is rejected by the validating
    webhook
  - x86_64 Secure Boot behavior unchanged

- [x] **Non-Functional Requirements (NFRs)**
  - **Security:** firmware auto-selection must only pick secure-boot-enabled descriptors —
    covered by descriptor-selection unit tests upstream
  - Performance/Scale/Monitoring: N/A for DP

#### **2. Known Limitations**

- DP is upstream-only; downstream delivery (RHEL edk2-aarch64 firmware) lands with TP
  ([CNV-81779](https://redhat.atlassian.net/browse/CNV-81779))
  - *Sign-off:* TBD

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - Feature gate opt-in; libvirt firmware auto-selection via edk2-aarch64 JSON
    descriptors (90-edk2-aarch64-qemuvars-sb-enrolled.json); uefi-vars device for
    variable storage
  - e2e test exists upstream (`ARM64 EFI secure boot` context in
    tests/vmi_configuration_test.go) but has no CI lane yet
    ([CNV-81780](https://redhat.atlassian.net/browse/CNV-81780))

- [x] **Technology Challenges**
  - Requires ARM64 bare-metal workers with a CS10-based host stack
- [x] **API Extensions** — none; existing `secureBoot` field reused
- [x] **Test Environment Needs** — see Section II.3
- [x] **Topology Considerations** — single ARM64 worker sufficient for DP scenarios

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** With the `ARM64SecureBoot` gate enabled, an ARM64 VM with `secureBoot: true`
  boots successfully and the guest reports Secure Boot as active
- **[P0]** With the gate disabled, an ARM64 VM with `secureBoot: true` is rejected by the
  validating webhook with a clear message
- **[P1]** An ARM64 VM with `secureBoot: true` fails to boot an unsigned kernel
- **[P1]** x86_64 Secure Boot behavior is unchanged (regression)

**Out of Scope (Testing Scope Exclusions)**

- **TP/GA scope** (CI lane enablement, RHEL firmware, migration/upgrade coverage,
  default-on gate) — tracked by
  [CNV-100819](https://redhat.atlassian.net/browse/CNV-100819)
  - *Rationale:* DP validates explicit opt-in functionality only
  - *PM/Lead Agreement:* TBD
- **Confidential computing (SEV/SNP/TDX) on ARM64** — non-goal per VEP #227
  - *Rationale:* explicitly excluded by the enhancement
  - *PM/Lead Agreement:* TBD

**Test Limitations**

- No upstream CI lane exists for ARM64 Secure Boot yet — manual execution on ARM64
  hardware until [CNV-81780](https://redhat.atlassian.net/browse/CNV-81780) lands
  - *Sign-off:* TBD

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — positive boot, unsigned-boot failure, gate-disabled
  rejection, x86_64 regression
- [x] **Automation Testing** — upstream e2e exists
  (tests/vmi_configuration_test.go, `RequiresARM64SecureBoot` decorator); downstream
  automation deferred to TP
- [ ] **Regression Testing** — x86_64 Secure Boot e2e suite (existing coverage)

**Non-Functional**

- [ ] Performance/Scale/Monitoring — N/A for DP

**Integration & Compatibility**

- [x] **Compatibility Testing** — RHEL guests; CS10-based ARM64 host stack
- [ ] **Upgrade Testing** — deferred to TP

#### **3. Test Environment**

- **Cluster Topology:** ARM64 (aarch64) bare-metal worker(s)
- **OCP & OpenShift Virtualization Version(s):** OCP 4.20+ / OpenShift Virtualization 5.1
- **Special Hardware:** aarch64 workers with QEMU 10.0+, libvirt and edk2-aarch64
  secure-boot firmware (CS10 base repos provide it)
- **Required Operators:** OpenShift Virtualization
- **Special Configurations:** `ARM64SecureBoot` feature gate enabled in the
  kubevirt CR before running positive scenarios

#### **4. Entry Criteria**

- [x] Requirements and design documents approved and merged (VEP #227, PR #228)
- [ ] Test environment available with ARM64 workers and required host stack
- [ ] ARM64 Secure Boot e2e executed manually at least once upstream

#### **5. Risks**

**Test Environment**

- **Risk:** ARM64 bare-metal availability; no CI lane means manual-only execution
  - **Mitigation:** upstream e2e validated during development; lane tracked by CNV-81780
  - *Sign-off:* TBD

---

### **III. Test Scenarios & Traceability**

- **[CNV-81765](https://redhat.atlassian.net/browse/CNV-81765)** — As a VM owner, I can
  enable Secure Boot on an ARM64 VM
  - *Test Scenario:* [Tier 2] Enable `ARM64SecureBoot` gate; create ARM64 VM with
    `secureBoot: true` and a signed boot chain; verify VM reaches Running and the guest
    reports Secure Boot active (`mokutil --sb-state`)
  - *Priority:* P0

- **[CNV-81765](https://redhat.atlassian.net/browse/CNV-81765)** — As a VM owner, I get
  clear feedback when the feature is not enabled
  - *Test Scenario:* [Tier 2] With the gate disabled, create ARM64 VM with
    `secureBoot: true`; verify webhook rejection with a clear error message
  - *Priority:* P0

- **[CNV-81765](https://redhat.atlassian.net/browse/CNV-81765)** — Unsigned boot
  components must not load
  - *Test Scenario:* [Tier 2] ARM64 VM with `secureBoot: true` and an unsigned kernel;
    verify boot failure (guest stuck/refuses boot, no kernel panic of signed path)
  - *Priority:* P1

- **[CNV-81765](https://redhat.atlassian.net/browse/CNV-81765)** — x86_64 Secure Boot
  unchanged
  - *Test Scenario:* [Tier 1] Existing x86_64 Secure Boot e2e scenarios pass
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

* **Reviewers:** TBD (sig-virt QE)
* **Approvers:** TBD — QE Architect, Product Manager, Dev Lead (Lee Yarwood)
