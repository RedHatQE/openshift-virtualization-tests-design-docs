# Openshift-virtualization-tests Test plan

## **Report virtio Version Per VM - Observability - Quality Engineering Plan**

### **Metadata & Tracking**

- **Enhancement(s):** [VEP #385: Guest Device Info Metrics](https://github.com/kubevirt/enhancements/blob/main/veps/sig-observability/385-guest-device-info/vep.md)
- **Feature Tracking:** [VIRTSTRAT-658](https://redhat.atlassian.net/browse/VIRTSTRAT-658)
- **Epic Tracking:** [CNV-97975](https://redhat.atlassian.net/browse/CNV-97975)
- **Feature Maturity:**
  - DP: N/A
  - TP: N/A
  - GA: 5.1 (CNV v5.1.0)
- **QE Owner(s):** Alex Barker (@albarker-rh)
- **Owning SIG:** sig-iuo (Install, Upgrade, Operators)
- **Participating SIGs:** sig-observability

**Document Conventions (if applicable):**

- **VMStatsCollector:** VEP #143's pipeline for collecting guest agent stats via virt-handler
- **Observability Controller:** kubevirt-observability-controller component that processes stats and emits Prometheus metrics

### **Feature Overview**

This feature enables fleet-wide visibility into VirtIO driver versions installed in Windows guest VMs.
Cluster administrators can query per-device driver information for every Windows VM through Prometheus
and identify which VMs need driver updates — without opening sessions to individual guest machines.
An alert notifies VM owners when any device is running a driver version older than the organization's
defined current versions. The definition of "current" is configurable at runtime by the cluster
administrator. Without a configuration, the feature is silent by default: no alerts fire,
and no action is required from administrators.

This is a GA feature for CNV v5.1.0 (GA: Feb 25, 2027, Feature Freeze: Nov 30, 2026).

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

This section documents the mandatory QE review process. The goal is to understand the feature's value,
technology, and testability before formal test planning.

#### **1. Requirement & User Story Review Checklist**

- [x] **Review Requirements**
  - *List the key D/S requirements reviewed:*
    - Windows VM VirtIO driver versions must be queryable from Prometheus per device per VM
    - An alert must fire when a Windows VM device has an outdated VirtIO driver version
    - Driver version reference data must be updatable at runtime via ConfigMap without rebuilding KubeVirt
    - Linux VMs must produce no device series and suffer no impact to other metrics
    - The feature must be silent by default (no ConfigMap = no alert)

- [x] **Understand Value and Customer Use Cases**
  - *Describe the feature's value to customers:* Checking Windows VM driver versions currently
    requires opening sessions to individual VMs, which is impractical at scale. This feature enables
    proactive driver management across VM fleets, preventing driver-related issues from being
    diagnosed reactively.
  - *List the customer use cases identified:*
    - As a Windows VM owner, I want to know from the host side whether my guest has the right VirtIO driver version
    - As a cluster admin, I want to see the VirtIO version installed in each Windows VM via a metric so I can identify VMs needing updates
    - As a VM owner, I want an alert if any of my VMs have a driver older than the one provided by virtio-win.iso
    - As a vendor distributing KubeVirt, I want to ship supported driver version definitions for out-of-box alerting

- [x] **Testability**
  - *Note any requirements that are unclear or untestable:* All requirements are testable.
    The metric and alert are verifiable through standard Prometheus queries. The ConfigMap
    behavior is testable through standard Kubernetes API operations. Windows guest agent
    availability requires Windows VM test infrastructure.

- [x] **Acceptance Criteria**
  - *List the acceptance criteria:*
    - An alert is created for every device of a Windows VM that has an outdated VirtIO driver version
    - VirtIO driver versions are reported when querying VMStats of a Windows VM
    - The `kubevirt_vmi_guest_device_driver_date_seconds` metric carries correct labels (driver_name, driver_version, device_id, guest_os_version_id)
    - The `kubevirt_guest_device_driver_latest_version_info` reference metric is populated from ConfigMap data
    - The recording rule `vmi:kubevirt_vmi_guest_device_driver_outdated:info` correctly identifies outdated drivers
    - Linux VMs produce no device series and do not affect existing metrics
  - *Note any gaps or missing criteria:* None

- [x] **Non-Functional Requirements (NFRs)**
  - *List applicable NFRs and their targets:*
    - Monitoring: New Prometheus metric, recording rule, and alert with runbook
    - Security: ConfigMap write requires admin namespace permission; metric does not introduce new exposure class beyond existing `kubevirt_vmi_guest_os_info`
    - Scalability: ~6-10 series per Windows VM (bounded by QEMU's vendor ID filter); ~6,000-10,000 series for 1,000 VMs; Linux VMs contribute zero series
    - Performance: `guest-get-devices` uses 30-minute cache TTL; minimal impact on stats poll
  - *Note any NFRs not covered and why:*
    - Usability: N/A — no direct UI component (labeled `no-ux`); future UI work tracked under CNV-92050
    - Portability: N/A — feature is platform-independent

#### **2. Known Limitations**

The limitations are documented to ensure alignment between development, QA, and product teams.
The following are confirmed product constraints accepted before testing begins.

- **Windows-only:** The `guest-get-devices` command is Windows-only. Linux ships VirtIO drivers in-kernel and does not expose per-device info through the guest agent. Linux VMs produce no device series.
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this limitation]

- **PCI devices only:** Only PCI devices are reported by the QEMU guest agent. Other device types (e.g., USB) are not surfaced.
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this limitation]

- **No in-guest driver updates:** KubeVirt does not manage in-guest software. The feature reports driver versions but does not update them.
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this limitation]

- **Existing VMs across upgrade:** VMs running during upgrade report no device data until live-migrated or restarted onto a new virt-launcher.
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this limitation]

- **No per-namespace/per-VM policy overrides:** Deferred; driver currency is a driver property, not a VM property.
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this limitation]

#### **3. Technology and Design Review**

- [x] **Developer Handoff/QE Kickoff**
  - *Key takeaways and concerns:*
    - Feature builds on VEP #143's VMStatsCollector pipeline
    - Three repos involved: kubevirt/kubevirt (data path), kubevirt/kubevirt-observability-controller (metrics/alerts), kubevirt/monitoring (runbook)
    - HCO enables VMStatsCollector via `kvExposedAlphaFGs` and adds `--enable-vmstats` to the observability controller deployment
    - ConfigMap `kubevirt-guest-device-drivers-config` is optional and typically distributor-supplied

- [x] **Technology Challenges**
  - *List identified challenges:*
    - Windows VM test infrastructure required for full end-to-end testing
    - Depends on CNV-93708 (VEP #143 VMStatsCollector) being available by default
  - *Impact on testing approach:* Tests requiring `guest-get-devices` response data need Windows VMs with QEMU guest agent installed and running

- [x] **API Extensions**
  - *List new or modified APIs:*
    - New metric: `kubevirt_vmi_guest_device_driver_date_seconds` (Gauge)
    - New metric: `kubevirt_guest_device_driver_latest_version_info` (Gauge, from ConfigMap)
    - New metric: `kubevirt_guest_device_driver_config_invalid` (Gauge, set to 1 on invalid ConfigMap)
    - New recording rule: `vmi:kubevirt_vmi_guest_device_driver_outdated:info`
    - New alert: `OutdatedGuestDeviceDrivers` (severity: warning, for: 1h)
    - New ConfigMap: `kubevirt-guest-device-drivers-config` (schema version: v1alpha1)
    - Modified: HCO feature gates and observability controller deployment args
  - *Testing impact:* Tests must validate each metric's labels and values, recording rule logic, alert firing conditions, ConfigMap CRUD lifecycle, and HCO configuration

- [x] **Test Environment Needs**
  - *See environment requirements in Section II.3 and testing tools in Section II.3.1*

- [x] **Topology Considerations**
  - *Describe topology requirements:* Feature is cluster-scoped and topology-independent. Observability controller runs alongside KubeVirt in its namespace.
  - *Impact on test design:* Standard cluster topology sufficient. No multi-cluster or special topology requirements.

### **II. Software Test Plan (STP)**

This STP serves as the **overall roadmap for testing**, detailing the scope, approach, resources, and schedule.

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Verify `kubevirt_vmi_guest_device_driver_date_seconds` metric is emitted per VirtIO device for Windows VMs with correct labels (driver_name, driver_version, device_id, guest_os_version_id)
- **[P0]** Verify `OutdatedGuestDeviceDrivers` alert fires when ConfigMap indicates a device's driver is outdated
- **[P0]** Verify no device series are produced for Linux VMs and existing VMStatsCollector metrics are unaffected
- **[P0]** Verify ConfigMap `kubevirt-guest-device-drivers-config` correctly populates `kubevirt_guest_device_driver_latest_version_info` reference metric
- **[P0]** Verify recording rule `vmi:kubevirt_vmi_guest_device_driver_outdated:info` correctly identifies outdated (VMI, device) pairs
- **[P1]** Verify `kubevirt_guest_device_driver_config_invalid` gauge is set to 1 when ConfigMap has unrecognized schema version, and previous valid mapping is retained
- **[P1]** Verify HCO enables VMStatsCollector feature gate and configures observability controller with correct flags (`--enable-vmstats`, `--vmstats-cert-path`, `--metrics-allowlist`)
- **[P1]** Verify alert does not fire when no ConfigMap is present (silent by default)
- **[P1]** Verify alert does not fire for devices not covered by the ConfigMap mapping
- **[P1]** Verify ConfigMap updates (apply/mutate/delete) are reflected in the reference metric
- **[P2]** Verify device data appears after live-migration or restart for VMs running during upgrade
- **[P1]** Verify no device metric series are produced for a Windows VM when the guest agent is not running, and existing VMStatsCollector metrics for that VM are unaffected
- **[P2]** Verify PromQL age-based queries work correctly (e.g., `time() - kubevirt_vmi_guest_device_driver_date_seconds > 365*24*3600`)

**Out of Scope (Testing Scope Exclusions)**

The following items are explicitly Out of Scope for this test cycle and represent intentional exclusions.

- **In-guest driver update operations**
  - *Rationale:* KubeVirt does not manage in-guest software; this feature is observability-only
  - *PM/Lead Agreement:* [Name/Date]

- **UI banner/notification for outdated drivers**
  - *Rationale:* UI work tracked separately under CNV-92050 / CNV-84458; this STP covers observability backend only
  - *PM/Lead Agreement:* [Name/Date]

- **Per-namespace or per-VM policy overrides for driver currency**
  - *Rationale:* Deferred per VEP #385 design; currency is a driver property, not a VM property
  - *PM/Lead Agreement:* [Name/Date]

- **Non-PCI device types (USB, etc.)**
  - *Rationale:* QEMU guest agent only reports PCI devices; this is a known platform limitation
  - *PM/Lead Agreement:* [Name/Date]

**Test Limitations**

- **Windows VM availability**
  - Windows VMs with QEMU guest agent are required for end-to-end device metric validation. ConfigMap and alert logic can be tested with Linux-only clusters and synthesized metric data.
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this limitation]

#### **2. Test Strategy**

**Functional**

- [x] **Functional Testing** — Validates that the feature works according to specified requirements and user stories
  - *Details:* Core functional testing covers: metric emission from Windows VM guest agent data, ConfigMap lifecycle (create/update/delete), recording rule evaluation, alert firing and resolution. Linux VM regression ensures no impact on existing metrics.

- [x] **Automation Testing** — Confirms test automation plan is in place for CI and regression coverage
  - *Details:* All Tier 2 tests automated. Tier 3 Windows VM tests automated in dedicated Windows CI lane.

- [x] **Regression Testing** — Verifies that new changes do not break existing functionality
  - *Details:* Verify existing VMStatsCollector metrics are unaffected by the new `guest-get-devices` category. Verify unsupported agent commands (Linux VMs) do not fail entire VMI stats responses.

- [ ] **Self-Validation Testing** — Should any of the new tests be included in the self-validation test package?
  - *Details:* Not applicable — observability feature does not affect core VM lifecycle operations.

**Non-Functional**

- [ ] **Performance Testing** — Validates feature performance meets requirements
  - *Details:* N/A for initial release. Response growth is ~1-2 KB per Windows VMI per poll (6-10 records of ~150 bytes). Cache TTL is 30 minutes for `guest-get-devices`.

- [ ] **Scale Testing** — Validates feature behavior under increased load
  - *Details:* N/A for initial release. Series cardinality bounded at ~6-10 per Windows VM. Scale impact documented in VEP.

- [ ] **Security Testing** — Verifies security requirements
  - *Details:* N/A — ConfigMap write requires admin namespace permission (existing Kubernetes RBAC). No new RBAC roles introduced beyond ClusterRole `list`/`watch` additions for the controller.

- [ ] **Usability Testing** — Validates user experience
  - *Details:* N/A — labeled `no-ux`. No UI component in this epic. Future UI tracked under CNV-92050.

- [x] **Monitoring** — Does the feature require metrics and/or alerts?
  - *Details:* Yes — this feature IS the monitoring/observability implementation. New metrics, recording rule, alert, and runbook (CNV-97834).

**Integration & Compatibility**

- [x] **Compatibility Testing** — Ensures feature works across supported platforms
  - *Details:* Feature depends on VEP #143 VMStatsCollector (CNV-93708) being available by default. Must verify backward compatibility: existing VMStatsCollector behavior unaffected.

- [x] **Upgrade Testing** — Validates upgrade paths
  - *Details:* VMs running during upgrade report no device data until live-migrated or restarted. Verify no regressions in existing metrics post-upgrade. HCO feature gate activation happens automatically on upgrade.

- [x] **Dependencies** — Blocked by deliverables from other components/products
  - *Details:* Blocked on CNV-93708 (VMStatsCollector/VEP #143) being available by default. Three repos involved: kubevirt/kubevirt, kubevirt/kubevirt-observability-controller, kubevirt/monitoring.

- [x] **Cross Integrations** — Does the feature affect other features or require testing by other teams?
  - *Details:* UI team (CNV-92050) depends on these metrics for banner/notification feature. Doc team (CNV-97845, CNV-97849) documents metrics, alert, and runbook.

**Infrastructure**

- [ ] **Cloud Testing** — Does the feature require multi-cloud platform testing?
  - *Details:* N/A — feature is platform-independent. Works on any platform supporting Windows VMs with guest agent.

#### **3. Test Environment**

- **Cluster Topology:** 3-master/3-worker bare-metal

- **OCP & OpenShift Virtualization Version(s):** OCP 4.20+ with OpenShift Virtualization 5.1 (CNV v5.1.0)

- **CPU Virtualization:** VT-x (Intel) or AMD-V enabled

- **Compute Resources:** Minimum per worker node: 8 vCPUs, 32GB RAM

- **Special Hardware:** N/A

- **Storage:** ocs-storagecluster-ceph-rbd-virtualization

- **Network:** OVN-Kubernetes, IPv4

- **Required Operators:** N/A

- **Platform:** Bare metal

- **Special Configurations:** Windows VM guest images with QEMU guest agent (virtio-win drivers installed)

#### **3.1. Testing Tools & Frameworks**

- **Test Framework:** Standard

- **CI/CD:** Windows CI lane for Tier 3 Windows VM tests

- **Other Tools:** `promtool` for recording rule and alert unit tests

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [ ] Requirements and design documents are **approved and merged** (VEP #385)
- [ ] Test environment can be **set up and configured** (see Section II.3 - Test Environment)
- [ ] VMStatsCollector (VEP #143 / CNV-93708) is available by default
- [ ] HCO changes merged: VMStatsCollector feature gate, observability controller deployment flags (CNV-98903)
- [ ] Observability controller changes merged: device metric, ConfigMap loader, recording rule, alert (CNV-95504, CNV-97832, CNV-97833)
- [ ] Windows VM images with QEMU guest agent available in test infrastructure

#### **5. Risks**

**Timeline/Schedule**

- **Risk:** Feature depends on CNV-93708 (VMStatsCollector/VEP #143) being available by default. If not ready by Feature Freeze (Nov 30, 2026), observability controller cannot collect device data.
  - **Mitigation:** CNV-97975 status is GREEN per latest update (Nov 16, 2026) — work is on track. Monitor CNV-93708 dependency closely.
  - *Estimated impact on schedule:* Could delay all end-to-end testing if VMStatsCollector is not available
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this risk]

**Test Coverage**

- **Risk:** Tier 3 Windows VM tests require Windows guest images with QEMU guest agent. If Windows images are unavailable, device metric validation is limited to unit tests and synthesized data.
  - **Mitigation:** ConfigMap, reference metric, recording rule, and alert logic can be tested with synthesized metric data on Linux-only clusters. Unit tests and promtool rule tests cover core logic without Windows VMs.
  - *Areas with reduced coverage:* End-to-end `guest-get-devices` → metric emission path
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this risk]

**Test Environment**

- **Risk:** N/A — standard cluster topology sufficient. No special hardware requirements beyond Windows guest images.
  - **Mitigation:** N/A
  - *Missing resources or infrastructure:* None
  - *Sign-off:* N/A

**Untestable Aspects**

- **Risk:** Behavior of `guest-get-devices` with very old QEMU guest agent versions (pre-5.2) cannot be tested in standard CI.
  - **Mitigation:** VEP #385 handles unsupported agent commands gracefully (empty payload + successful result). Unit tests cover this path.
  - *Alternative validation approach:* Unit test for unsupported command handling
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this risk]

**Resource Constraints**

- **Risk:** N/A — QE resource assigned (Alex Barker).
  - **Mitigation:** N/A
  - *Current capacity gaps:* None
  - *Sign-off:* N/A

**Dependencies**

- **Risk:** Three repos must deliver changes (kubevirt/kubevirt, kubevirt/kubevirt-observability-controller, kubevirt/monitoring). Late delivery from any repo delays testing.
  - **Mitigation:** Stories across repos are tracked under CNV-97975. Multiple stories already Closed (CNV-97834, CNV-98903, CNV-99456, CNV-95504, CNV-97833). CNV-97832 (ConfigMap loader) is Release Pending.
  - *Dependent teams or components:* kubevirt/kubevirt (data path), kubevirt/kubevirt-observability-controller (metrics/alerts), kubevirt/monitoring (runbook), HCO (feature gate enablement)
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this risk]

**Other**

- **Risk:** Invalid ConfigMap schema versions could cause unexpected behavior in production.
  - **Mitigation:** VEP #385 specifies that unrecognized schema versions are rejected and the previous valid mapping is retained. `kubevirt_guest_device_driver_config_invalid` gauge exposes this state.
  - *Sign-off:* [Name/Date — confirms awareness and acceptance of this risk]

---

### **III. Test Scenarios & Traceability**

- **[CNV-95504](https://redhat.atlassian.net/browse/CNV-95504)** — As a cluster admin, I want to see the VirtIO driver version per device for each Windows VM via a Prometheus metric
  - *Test Scenario:* [Tier 3] Verify `kubevirt_vmi_guest_device_driver_date_seconds` metric is emitted for each VirtIO device on a running Windows VM with guest agent, with correct labels (driver_name, driver_version, device_id, guest_os_version_id) and value (Unix epoch seconds from driver date)
  - *Priority:* P0

- **[CNV-95504](https://redhat.atlassian.net/browse/CNV-95504)** — As a cluster admin running Linux VMs, I want driver monitoring to have no impact on my existing metrics
  - *Test Scenario:* [Tier 2] Verify no device metric series are produced for Linux VMs and all existing VMStatsCollector metrics remain unaffected
  - *Priority:* P0

- **[CNV-97832](https://redhat.atlassian.net/browse/CNV-97832)** — As a cluster admin, I want to define which driver versions are current so the system can identify outdated drivers
  - *Test Scenario:* [Tier 2] Verify creating ConfigMap `kubevirt-guest-device-drivers-config` with valid v1alpha1 schema populates `kubevirt_guest_device_driver_latest_version_info` reference metric with correct labels (device_id, guest_os_version_id, driver_version, device_name)
  - *Priority:* P0

- **[CNV-97832](https://redhat.atlassian.net/browse/CNV-97832)** — As a cluster admin, I want changes to my driver version definitions to take effect without restarting components
  - *Test Scenario:* [Tier 2] Verify updating the ConfigMap reflects changes in the reference metric, and deleting the ConfigMap removes all reference metric series
  - *Priority:* P1

- **[CNV-97832](https://redhat.atlassian.net/browse/CNV-97832)** — As a cluster admin, I want the system to reject invalid driver version definitions and retain the last valid configuration
  - *Test Scenario:* [Tier 2] Verify applying a ConfigMap with an unrecognized schema version is rejected, the previous valid mapping is retained, and `kubevirt_guest_device_driver_config_invalid` gauge is set to 1
  - *Priority:* P1

- **[CNV-97833](https://redhat.atlassian.net/browse/CNV-97833)** — As a VM owner, I want to receive an alert when any of my VMs have outdated VirtIO drivers
  - *Test Scenario:* [Tier 3] Verify `OutdatedGuestDeviceDrivers` alert fires (severity: warning, for: 1h) when a Windows VM device's driver version does not match the ConfigMap reference for the VM's guest_os_version_id
  - *Priority:* P0

- **[CNV-97833](https://redhat.atlassian.net/browse/CNV-97833)** — As a cluster admin, I want the system to be silent by default when no driver version definitions are configured
  - *Test Scenario:* [Tier 2] Verify `OutdatedGuestDeviceDrivers` alert does not fire when no `kubevirt-guest-device-drivers-config` ConfigMap exists (silent by default)
  - *Priority:* P0

- **[CNV-97833](https://redhat.atlassian.net/browse/CNV-97833)** — As a cluster admin, I want alerts only for devices covered by my driver version definitions
  - *Test Scenario:* [Tier 2] Verify alert does not fire for devices not covered by the ConfigMap mapping, and VMs without `guest_os_version_id` are not alerted
  - *Priority:* P1

- **[CNV-97833](https://redhat.atlassian.net/browse/CNV-97833)** — As a cluster admin, I want to query which specific VMs and devices have outdated drivers
  - *Test Scenario:* [Tier 2] Verify recording rule `vmi:kubevirt_vmi_guest_device_driver_outdated:info` produces one series per outdated (VMI, device) pair and zero series for current or uncovered devices
  - *Priority:* P0

- **[CNV-98903](https://redhat.atlassian.net/browse/CNV-98903)** — As a cluster admin, I want the driver monitoring capabilities enabled automatically in my cluster
  - *Test Scenario:* [Tier 2] Verify HCO adds VMStatsCollector to KubeVirt CR feature gates, adds `--enable-vmstats` and `--vmstats-cert-path` flags to observability controller deployment, and mounts the monitoring client certificate secret
  - *Priority:* P1

- **[CNV-98903](https://redhat.atlassian.net/browse/CNV-98903)** — As a cluster admin, I want only the relevant driver metrics collected to minimize overhead
  - *Test Scenario:* [Tier 2] Verify HCO configures the `--metrics-allowlist` flag with the expected metric names (kubevirt_vmi_guest_device_driver_timestamp_seconds, kubevirt_guest_device_driver_latest_version_info, kubevirt_guest_device_driver_config_invalid)
  - *Priority:* P1

- **[CNV-95504](https://redhat.atlassian.net/browse/CNV-95504)** — As a cluster admin, I want driver monitoring to degrade gracefully when the guest agent is not running
  - *Test Scenario:* [Tier 3] Verify no device metric series are produced for a Windows VM when the guest agent is not running, and existing VMStatsCollector metrics for that VM are unaffected
  - *Priority:* P1

- **[CNV-97975](https://redhat.atlassian.net/browse/CNV-97975)** — As a cluster admin, I want driver data to appear for VMs that were running during a cluster upgrade
  - *Test Scenario:* [Tier 3] Verify that a Windows VM running during cluster upgrade reports device data after live-migration or restart onto a new virt-launcher
  - *Priority:* P2

- **[CNV-97975](https://redhat.atlassian.net/browse/CNV-97975)** — As a cluster admin, I want to query VMs with drivers older than a specified age threshold
  - *Test Scenario:* [Tier 2] Verify PromQL query `(time() - kubevirt_vmi_guest_device_driver_date_seconds) > threshold` correctly identifies VMs with drivers older than the specified threshold
  - *Priority:* P2

- **[CNV-97834](https://redhat.atlassian.net/browse/CNV-97834)** — As a cluster admin receiving an outdated driver alert, I want a runbook to guide me through resolution
  - *Test Scenario:* [Tier 2] Verify the `OutdatedGuestDeviceDrivers` alert includes a valid runbook URL pointing to the merged runbook in kubevirt/monitoring
  - *Priority:* P1

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE: Alex Barker / @albarker-rh
  - Development: Joao Vilaca / @jvilaca
  - Observability: Shirly Radco / @sradco
* **Approvers:**
  - QE Lead: Harel Meir / @hmeir
  - Dev Lead: Natalie Gavrilov / @ngavrilo
  - Product Manager: Martin Tessun / @mtessun
