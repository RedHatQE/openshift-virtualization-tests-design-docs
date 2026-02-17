# Software Test plan

## **VM integration of BGP and EVPN with UDN - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                                                                                                                                                                         |
|:-----------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Enhancement(s)**     | [OVN-K](https://github.com/ovn-kubernetes/ovn-kubernetes/blob/master/docs/okeps/okep-5088-evpn.md) and [OCP](https://github.com/openshift/enhancements/blob/master/enhancements/network/ovn-kubernetes-evpn.md) |
| **Feature in Jira**    | https://issues.redhat.com/browse/OCPSTRAT-1744                                                                                                                                                                  |
| **Jira Tracking**      | https://issues.redhat.com/browse/CORENET-5633<br/>https://issues.redhat.com/browse/CNV-63123                                                                                                                    |
| **QE Owner(s)**        | Sergei Volkov (sevolkov@redhat.com)                                                                                                                                                                             |
| **Owning SIG**         | sig-network                                                                                                                                                                                                     |
| **Participating SIGs** | sig-network                                                                                                                                                                                                     |
| **Current Status**     | Draft                                                                                                                                                                                                           |

**Document Conventions:**
- UDN: User Defined Network (OVN-K based network type).
- CUDN/UDN resource: A CRD used to define a UDN, at the cluster level (CUDN) or project level (UDN).
- BGP: Border Gateway Protocol (Control Plane used to exchange routes).
- EVPN: Ethernet Virtual Private Network (The BGP extension allowing L2/L3 VPNs).
- VXLAN: Virtual Extensible LAN (Data Plane encapsulation protocol).
- VNI: VXLAN Network Identifier (24-bit segment ID used in VXLAN encapsulation).
- MAC-VRF: Layer 2 VPN (Virtual Switching/Bridging).
- IP-VRF: Layer 3 VPN (Virtual Routing).
- VTEP: VXLAN Tunnel Endpoint.
- Stretched L2: A broadcast domain extended between the OCP cluster and an external provider via VXLAN.

### **Feature Overview**

This feature allows VMs running in OpenShift Virtualization to seamlessly connect to networks outside the cluster —
as if they never moved. When customers migrate VMs from an existing virtualization platform into OpenShift, those
VMs often need to keep talking to workloads that haven't migrated yet. Today, that requires manual network
reconfiguration and risks downtime. With BGP/EVPN support, a migrated VM keeps its original IP address and MAC address,
stays on the same network segment as its former neighbors, and can communicate with them without any reconfiguration —
on the same subnet (Layer 2) or across different subnets (Layer 3). This is especially critical for phased migrations,
where only some workloads move to OpenShift at a time and the rest remain on the source platform. EVPN extends the VM's
network transparently across both environments, enabling live migration between OpenShift nodes without dropping connections.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                                                                                                                                                                                                                                                                                  | Comments |
|:---------------------------------------|:-----|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Review Requirements**                | [x]  | Enable BGP EVPN for UDNs to support L2 and L3 extension.                                                                                                                                                                                                                                                                                                                                                       |          |
| **Understand Value**                   | [x]  | Customers can migrate VMs from source virtualization platform to OpenShift UDN namespace while preserving their IP addresses and L2 connectivity (Stretched L2). VMs maintain Layer 3 routed access to different external subnets over the VPN, ensuring seamless communication with resources remaining in the source cluster.                                                                                |          |
| **Customer Use Cases**                 | [x]  | 1. A user migrates a VM from Source Provider to OpenShift over the stretched L2 EVPN network preserving source VM network configuration and maintains ongoing, continuous communication with the rest of the application that remains in the Source Provider.<br>2. UDN VM requires routed ingress and egress over an L3 VPN to communicate with external networks (different subnets) in the Source Provider. |          |
| **Testability**                        | [x]  | Testable via a software-based external VTEP emulation.                                                                                                                                                                                                                                                                                                                                                         |          |
| **Acceptance Criteria**                | [x]  | 1. Connectivity: UDN VMs can ping each other over EVPN and Source Provider endpoint on same subnet (stretched L2).<br/>2. Mobility: Connection survives UDN VM Live Migration within the same cluster/Source Provider. <br/>3. VMs can communicate over the L3 VPN (different subnets), and these established L3 connections survive UDN VM internal Live Migration.                                           |          |
| **Non-Functional Requirements (NFRs)** | [x]  | See section **II.2 - Test Environment**                                                                                                                                                                                                                                                                                                                                                                        |          |

#### **2. Known Limitations**

- Local Gateway Mode Only: EVPN is not supported on clusters using Shared Gateway Mode.
- Single-Stack IPv6 is not supported: due to upstream Linux Kernel limitations regarding IPv6-based VXLAN tunnels, the EVPN VTEP (Underlay) requires IPv4.
- Bare Metal Only: this feature is supported on neither public cloud platforms nor virtual environments.
- Secondary networks (of any kind): The feature is currently limited to the primary UDN network.

#### **3. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                                                                                      | Comments |
|:---------------------------------|:-----|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [x]  | Performed through meetings and design review.                                                                                                                                                      |          |
| **Technology Challenges**        | [x]  | Requires "Stretched L2" emulation. The test environment must simulate an external VTEP that connects the OCP UDN VNI to an external "host" IP.                                                     |          |
| **Test Environment Needs**       | [x]  | Default OCP-V Bare Metal deployment, OVN in Local Gateway Mode, Source Provider Cluster with support of EVPN.                                                                                      |          |
| **API Extensions**               | [x]  | The new capability to setup EVPN is exposed through a dedicated VTEP CRD, new API fields in CUDN/UDN and FRRConfiguration resources.                                                               |          |
| **Topology Considerations**      | [x]  | Requires a multi-node OCP topology where nodes peer with an external BGP router. Includes an External VTEP to extend the Stretched Layer 2 (MAC-VRF)/Layer 3 (IP-VRF) network outside the cluster. |          |

---

### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

**Testing Goals**

- **[P0]** Basic L2 Connectivity (East-West): Verify two UDN VMs connected to the same L2 EVPN network can communicate with each other.
- **[P0]** Stretched L2 Connectivity (East-West): Verify a UDN VM can communicate with the Source Provider on the same subnet via the EVPN fabric.
- **[P0]** UDN VM Live Migration (Internal): Verify that a UDN VM connected via EVPN L2 fabric can live-migrate between OCP nodes without losing connectivity to the Source Provider/another UDN VM.
- **[P0]** Source Provider Migration: Verify migration from Source Provider to OCP UDN namespace over VXLAN tunnel: network data is preserved (IP+MAC), connectivity is maintained after migration.
- **[P1]** L3 Routed Connectivity (North-South): Verify a UDN VM can communicate with the Source Provider on a different subnet via the EVPN L3 fabric (IP-VRF).
- **[P1]** L3 UDN VM Live Migration (Internal): Verify that a VM connected via L3 EVPN can live-migrate between OCP nodes without losing routed connectivity to the Source Provider/another UDN VM.
- **[P2]** UDN VM cold reboot: Verify that a UDN VM connected via EVPN retains connectivity to the Source Provider after a cold reboot.

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item                | Rationale                                                                                                                                              | PM/ Lead Agreement                |
|:---------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------|
| Observability                    | There are no requirements or needs to have this feature covered by metrics or telemetry at this stage.                                                 | [x] phoracek@redhat.com (02/2026) |
| EVPN Multihoming                 | The OCP-V layered product assumes the EVPN multihoming is already covered by OCP Network.                                                              | [x] phoracek@redhat.com (02/2026) |
| Core OCP network functionality   | The functionality is based on OCP network OVN-K pod level solutions, the OCP-V layered product assumes the core EVPN functionality is already covered. | [x] phoracek@redhat.com (02/2026) |

#### **2. Test Strategy**

<!-- The following test strategy considerations must be reviewed and addressed. Mark "Y" if applicable,
"N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review. -->

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments                                                                                                                                                                                                                                                                |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y                       |                                                                                                                                                                                                                                                                         |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       |                                                                                                                                                                                                                                                                         |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N                       | Not OCP-V scope. Tracker: https://issues.redhat.com/browse/PERFSCALE-4393                                                                                                                                                                                               |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N/A                     | There are no known security risks. If there are any, the core functionality is expected to cover them.                                                                                                                                                                  |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | N                       | General EVPN configuration is out of scope for OCP-V. While there are new API fields to define an EVPN-backed UDN, VMs simply consume these networks using standard, existing network attachments. This does not introduce any complex usability hurdles for VM users.  |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | Y                       |                                                                                                                                                                                                                                                                         |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | Y                       |                                                                                                                                                                                                                                                                         |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation for VMs attached to EVPN-enabled networks.                    | Y                       |                                                                                                                                                                                                                                                                         |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | N                       | There is no known impact on existing functionality.                                                                                                                                                                                                                     |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | Y                       | Core functionality of the feature is dependent on OCP Network coverage. This is a hard assumption.                                                                                                                                                                      |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | Y                       | **OCP CORENET**: core functionality of EVPN feature, corner cases; **OCP-V network**: migration from Source Provider to OCP, connectivity checks                                                                                                                        |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | N/A                     | No major need has been identified.                                                                                                                                                                                                                                      |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | N/A                     | Bare Metal environment is required.                                                                                                                                                                                                                                     |

#### **3. Test Environment**

<!-- **Note:** "N/A" means explicitly not applicable. Cannot leave empty cells. -->

| Environment Component                         | Configuration                           | Specification Examples                                                                                              |
|:----------------------------------------------|:----------------------------------------|:--------------------------------------------------------------------------------------------------------------------|
| **Cluster Topology**                          | Bare Metal                              | Bare metal OCP cluster with multi-worker nodes required.                                                            |
| **OCP & OpenShift Virtualization Version(s)** | OCP 4.22 and up                         | OCP 4.22 (and up). No special OCP-V version is required, but testing environment will use aligned version with OCP. |
| **CPU Virtualization**                        | N/A                                     | Agnostic.                                                                                                           |
| **Compute Resources**                         | N/A                                     | Agnostic.                                                                                                           |
| **Special Hardware**                          | N/A                                     | Agnostic.                                                                                                           |
| **Storage**                                   | N/A                                     | Agnostic.                                                                                                           |
| **Network**                                   | Primary UDN, OVN-K                      | Single stack IPv4 underlays. Local Gateway Mode is mandatory.                                                       |
| **Required Operators**                        | OVN-K (default)                         |                                                                                                                     |
| **Platform**                                  | N/A                                     | Agnostic.                                                                                                           |
| **Special Configurations**                    | Source Provider Virtualization Platform | Should be configured next to CNV QE bare metal infrastructure.                                                      |

#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks           |
|:-------------------|:---------------------------|
| **Test Framework** | -                          |
| **CI/CD**          | -                          |
| **Other Tools**    | EVPN aware external router |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment).

#### **5. Risks**

<!-- Document specific risks for this feature. If a risk category is not applicable, mark as "N/A" with
justification in mitigation strategy.

**Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable
with justification. -->

| Risk Category        | Specific Risk for This Feature                                              | Mitigation Strategy                                                                                                                                            | Status      |
|:---------------------|:----------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------|
| Timeline/Schedule    | Post code-freeze, finalization of STP, STD and implementation delayed.      | Engage all team members to assist, use Dev assistance, collaboration with the OCP CORENET team.                                                                | [x]         |
| Test Coverage        | Source Provider emulation limits testing Source Provider Migration scenario | Migration emulation: removing the external endpoint from the simulated provider and deploying a OCP VM utilizing the identical network configuration (IP/MAC). | [x]         |
| Test Environment     | Lack of Physical Source Provider environment.                               | Configure the emulated external provider endpoint to closely match real-world network behavior.                                                                | [ planned ] |
| Untestable Aspects   | Scale.                                                                      | Not under OCP-V responsibility.                                                                                                                                | [x]         |
| Resource Constraints | Lack of Physical Source Provider environment.                               | Configure the emulated external provider endpoint to closely match real-world network behavior.                                                                | [ planned ] |
| Dependencies         | Functionality implemented by OCP CORENET team.                              | Issues are dependent on the OCP Network release (and fix) flow.                                                                                                | [x]         |

---

### **III. Test Scenarios & Traceability**

| Requirement ID   | Requirement Summary                                                                                            | Test Scenario(s)                                                                                                                         | Tier   | Priority |
|:-----------------|:---------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------|:-------|:---------|
| CNV-63123 (epic) | As a user, I want my VMs on different nodes to communicate with each other over the EVPN fabric (East-West).   | Verify that two UDN VMs connected to the same EVPN network can communicate with each other across different OCP nodes.                   | Tier 2 | P0       |
|                  | As a user, I want my OCP VM to communicate with the Source Provider network on the same subnet (Stretched L2). | Verify a VM can communicate with the Source Provider on the same subnet via the EVPN fabric.                                             | Tier 2 | P0       |
|                  | As an admin, I want to live-migrate an EVPN-connected VM between OCP nodes without losing connectivity.        | Verify that a VM connected via EVPN can live-migrate between OCP nodes without losing connectivity to the Source Provider/another UDN VM | Tier 2 | P0       |
|                  | As an admin, I want to migrate a VM from the Source Provider to OCP keeping its network data.                  | Verify migration from Source Provider to OCP over VXLAN tunnel with preserving connectivity and VM network data.                         | Tier 2 | P0       |
|                  | As a user, I want my VM to reach external networks on different subnets over the L3 VPN.                       | Verify a UDN VM can communicate with an external provider on a different subnet via IP-VRF.                                              | Tier 2 | P1       |
|                  | As an admin, I want to live-migrate an L3 EVPN-connected VM between OCP nodes without dropping connections.    | Verify a UDN VM connected via L3 EVPN retains connectivity to a different external subnet/another UDN VM during live migration.          | Tier 2 | P1       |
|                  | As a user, I can stop and start an EVPN-connected UDN VM and immediately establish new connections.            | Verify that a UDN VM connected via EVPN retains connectivity to the Source Provider after a cold VM reboot (stop\start).                 | Tier 2 | P2       |
|                  | As an admin, I want to upgrade the cluster without losing EVPN VM connectivity.                                | Verify an existing connection is preserved, a new connection can be established after upgrade.                                           | Tier 2 | P2       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - Development Representative (OCP-V): [Miguel Duarte Barroso](@maiqueb)
  - QE Members (OCP): [Anurag Saxena](@anuragthehatter)
  - QE Members (OCP-V): [Yossi Segev](@yossisegev), [Anat Wax](@Anatw), [Asia Zhivov Khromov](@azhivovk)
* **Approvers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - Principal Developer (OCP-V): [Edward Haas](@EdDev)
  - Product Manager/Owner: [Petr Horacek](@phoracek)
