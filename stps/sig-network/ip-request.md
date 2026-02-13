# Software Test plan

## **IP addresses specification on a VM - Quality Engineering Plan**

### **Metadata & Tracking**

| Field                  | Details                                                                                                                                                  |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Enhancement(s)**     | [OCP](https://github.com/openshift/enhancements/pull/1793) and [OCP-V](https://docs.google.com/document/d/1M5YMM6w-Cimuqxd_hUdB-FcuBxrsmDSJNTjQJ-UcDDA/) |
| **Feature in Jira**    | https://issues.redhat.com/browse/CNV-67524                                                                                                               |
| **Jira Tracking**      | https://issues.redhat.com/browse/CNV-70089                                                                                                               |
| **QE Owner(s)**        | Yoss Segev (ysegev@redhat.com)                                                                                                                           |
| **Owning SIG**         | sig-network                                                                                                                                              |
| **Participating SIGs** | sig-network                                                                                                                                              |
| **Current Status**     | QE Review Complete                                                                                                                                       |

**Document Conventions:**
- UDN: User Defined Network (OVN-K based network type).
- CUDN/UDN resource: A CRD used to define a UDN, at the cluster level (CUDN) or project level (UDN).
- KCS: [Knowledge Centered Support](https://access.redhat.com/articles/7031392).
- MTV: [Migration Toolkit for Virtualization](https://docs.redhat.com/en/documentation/migration_toolkit_for_virtualization/2.10)

### **Feature Overview**

Customers migrating to OpenShift Virtualization from traditional virtualization platforms often rely on third-party
systems for network management, including established workflows for provisioning and allocating IP addresses to
virtual machines.

The feature allows a third party IPAM solution to specify on a VM the IP address it should use.
Specifically focused on the primary pod network in a (L2) UDN network type.

---

### **I. Motivation and Requirements Review (QE Review Guidelines)**

#### **1. Requirement & User Story Review Checklist**

| Check                                  | Done | Details/Notes                                                                                                                                       | Comments                                                                                       |
|:---------------------------------------|:-----|:----------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------|
| **Review Requirements**                | [x]  | Provide the ability for 3rd party integrators to specify an IP address on the VM primary (pod) network.                                             |                                                                                                |
| **Understand Value**                   | [x]  | Assists new customers coming from other virtualization solutions to integrate their existing IPAM solutions into OCP-V.                             |                                                                                                |
| **Customer Use Cases**                 | [x]  | Allow users to propagate a specific IP address to the guest during the VM definition, in order to integrate OCP-V with a third-party IPAM provider. | Propagation may be implemented through cloud-init, DHCP (default), console or any other means. |
| **Testability**                        | [x]  | The use cases are testable through the provided API and existing coverage of dependent features.                                                    |                                                                                                |
| **Acceptance Criteria**                | [x]  | Ability to request a specific IP through the VM definition and documentation in the form of a KCS is well defined.                                  |                                                                                                |
| **Non-Functional Requirements (NFRs)** | [x]  | Documentation (in the form of a KCS) is explicitly required. Implications on scale are mainly dependent on supporting features.                     |                                                                                                |

#### **2. Technology and Design Review**

| Check                            | Done | Details/Notes                                                                                                                                                                                                                         | Comments |
|:---------------------------------|:-----|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------|
| **Developer Handoff/QE Kickoff** | [x]  | Performed through meetings and design review.                                                                                                                                                                                         |          |
| **Technology Challenges**        | [x]  | No special challenges, however it involves a multi component orchestration. From a user-facing perspective, the input API and result verification is simple. Uses the same API as VM migration from an external provider through MTV. |          |
| **Test Environment Needs**       | [x]  | Default OCP-V deployment, on any environment (Bare Metal, Cloud).                                                                                                                                                                     |          |
| **API Extensions**               | [x]  | The new capability is exposed through a dedicated annotation on the VM resource.                                                                                                                                                      |          |
| **Topology Considerations**      | [x]  | The explicit IP address specification is limited to primary UDN. No known limitations when considering different topologies.                                                                                                          |          |


### **II. Software Test Plan (STP)**

#### **1. Scope of Testing**

Tests are aimed to cover the ability to define at VM definition its primary pod network IP address.
The functionality is limited to UDN.

**Testing Goals**

- **[P0]** Verify IP address definition through cloud-init is reaching the guest OS.
- **[P0]** Confirm east-west connectivity in the cluster.
- **[P0]** Confirm north-south connectivity from/to the cluster.
- **[P1]** Verify IP persists over power cycle.
- **[P1]** Verify seamless connectivity is preserved over migration.
- **[P2]** Verify IP address definition through the default DHCP is reaching the guest OS.

**Out of Scope (Testing Scope Exclusions)**

| Out-of-Scope Item                | Rationale                                                                                                                                                           | PM/ Lead Agreement                |
|:---------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------|
| Non UDN primary pod network      | The feature is currently limited to UDN only network types.                                                                                                         | [x] ronen@redhat.com (12/2025)    |
| Secondary networks (of any kind) | The feature is currently limited to the primary UDN network.                                                                                                        | [x] ronen@redhat.com (12/2025)    |
| IPv6 support                     | IPv6 support is not yet planned for the primary pod network (of any type). Current limitation on UDN networks is mainly due to test coverage.                       | [x] ronen@redhat.com (01/2026)    |
| UI support                       | The feature is intended for 3rd party integration tools and has no formal user oriented exposure.                                                                   | [x] ronen@redhat.com (12/2025)    |
| Observability                    | There are no requirements or needs to have this feature covered by metrics or telemetry at this stage.                                                              | [x] ronen@redhat.com (01/2026)    |
| Core OCP network functionality   | The functionality is based on OCP network OVN-K & ipam-extensions pod level solutions, the OCP-V layered product assumes the core functionality is already covered. | [x] phoracek@redhat.com (12/2025) |

#### **2. Test Strategy**

<!-- The following test strategy considerations must be reviewed and addressed. Mark "Y" if applicable,
"N/A" if not applicable (with justification in Comments). Empty cells indicate incomplete review. -->

| Item                           | Description                                                                                                                                                  | Applicable (Y/N or N/A) | Comments                                                                                                                                                      |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Functional Testing             | Validates that the feature works according to specified requirements and user stories                                                                        | Y                       |                                                                                                                                                               |
| Automation Testing             | Ensures test cases are automated for continuous integration and regression coverage                                                                          | Y                       |                                                                                                                                                               |
| Performance Testing            | Validates feature performance meets requirements (latency, throughput, resource usage)                                                                       | N                       | Required by the core functionality (OCP), not planned to be included in OCP-V coverage.                                                                       |
| Security Testing               | Verifies security requirements, RBAC, authentication, authorization, and vulnerability scanning                                                              | N/A                     | There are no known security risks. If there are any, the core functionality is expected to cover them.                                                        |
| Usability Testing              | Validates user experience, UI/UX consistency, and accessibility requirements. Does the feature require UI? If so, ensure the UI aligns with the requirements | N                       | API only, annotation style, no UI. Aimed for machine integration, not human interface.                                                                        |
| Compatibility Testing          | Ensures feature works across supported platforms, versions, and configurations                                                                               | Y                       | Primary UDN only, dependent on OCP Network with OVN-K network provider that uses IPAM Claim.                                                                  |
| Regression Testing             | Verifies that new changes do not break existing functionality                                                                                                | Y                       | Core OCP-V functionality covered (power cycle and migration); other features are considered nice-to-have.                                                     |
| Upgrade Testing                | Validates upgrade paths from previous versions, data migration, and configuration preservation                                                               | Y                       | Upgrade to future versions should confirm basic functionality is preserved.                                                                                   |
| Backward Compatibility Testing | Ensures feature maintains compatibility with previous API versions and configurations                                                                        | N                       | There is no known impact on existing functionality.                                                                                                           |
| Dependencies                   | Dependent on deliverables from other components/products? Identify what is tested by which team.                                                             | Y                       | Core functionality of the feature is dependent on OCP Network coverage. This is a hard assumption.                                                            |
| Cross Integrations             | Does the feature affect other features/require testing by other components? Identify what is tested by which team.                                           | N                       | The feature uses sticky IP addresses (IPAM Claim) which is a default on OCP-V with UDN. Therefore, the IP address chosen can depend on that feature coverage. |
| Monitoring                     | Does the feature require metrics and/or alerts?                                                                                                              | N                       | Observability has been agreed to be out-of-scope at this stage. No major need has been identified at this stage.                                              |
| Cloud Testing                  | Does the feature require multi-cloud platform testing? Consider cloud-specific features.                                                                     | Y                       | The feature should be agnostic to the platform used, therefore, running the same tests on the cloud should be applicable.                                     |

#### **3. Test Environment**

<!-- **Note:** "N/A" means explicitly not applicable. Cannot leave empty cells. -->

| Environment Component                         | Configuration | Specification Examples                                         |
|:----------------------------------------------|:--------------|:---------------------------------------------------------------|
| **Cluster Topology**                          |               | Should be agnostic to the cluster topology.                    |
| **OCP & OpenShift Virtualization Version(s)** |               | OCP 4.21 (and up) with OpenShift Virtualization 4.21 (and up). |
| **CPU Virtualization**                        | N/A           | Agnostic.                                                      |
| **Compute Resources**                         | N/A           | Agnostic.                                                      |
| **Special Hardware**                          | N/A           | Agnostic.                                                      |
| **Storage**                                   | N/A           | Agnostic.                                                      |
| **Network**                                   | Primary UDN   | OVN-Kubernetes, should be available with IPv4.                 |
| **Required Operators**                        | N/A           | OVN-K (default)                                                |
| **Platform**                                  | N/A           | Agnostic.                                                      |
| **Special Configurations**                    | N/A           | No special configuration expected.                             |

#### **3.1. Testing Tools & Frameworks**

| Category           | Tools/Frameworks |
|:-------------------|:-----------------|
| **Test Framework** | -                |
| **CI/CD**          | -                |
| **Other Tools**    | -                |

#### **4. Entry Criteria**

The following conditions must be met before testing can begin:

- [x] Requirements and design documents are **approved and merged**
- [x] Test environment can be **set up and configured** (see Section II.3 - Test Environment)

#### **5. Risks**

<!-- Document specific risks for this feature. If a risk category is not applicable, mark as "N/A" with
justification in mitigation strategy.

**Note:** Empty "Specific Risk" cells mean this must be filled. "N/A" means explicitly not applicable
with justification. -->

| Risk Category        | Specific Risk for This Feature                                                    | Mitigation Strategy                                                                            | Status          |
|:---------------------|:----------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------|:----------------|
| Timeline/Schedule    | Post code-freeze, finalization of STP, STD and implementation delayed.            | Engage all team members to assist, use Dev assistance, use existing UDN tests as the baseline. | [ in-progress ] |
| Test Coverage        | Single stack IPv6 is delayed with follow up Z stream releases.                    | Add GA limitations notes.                                                                      | [ planned ]     |
| Test Environment     | N/A                                                                               | No known risks.                                                                                | [x]             |
| Untestable Aspects   | Scale                                                                             | Under OCP Network responsibility.                                                              | [x]             |
| Resource Constraints | N/A                                                                               | No known risks.                                                                                | [x]             |
| Dependencies         | Functionality implemented by OCP Network team with sig-network SDN wg assistance. | Issues are dependent on the larger OCP Network release (and fix) flow.                         | [x]             |

#### **6. Known Limitations**

- Single-stack IPv6 is not planned for coverage at the initial GA.
- Except for specific core features, like power-cycle and live-migration, cross regression functionality is not planned.
- Coverage on special architectures (e.g. ARM64) is not planned, although the feature is considered agnostic.
- Primary UDN coverage assumes classic Guest OS (Fedora-based), with cloud-init and/or dynamic (DHCP) IPv4 support.
- Special guest OS, e.g. Windows, is expected to work with cloud-init and/or dynamic (DHCP) IPv4. However, no explicit tests are planned to cover them.

---

### **III. Test Scenarios & Traceability**

| Requirement ID   | Requirement Summary                                                                                                                  | Test Scenario(s)                                                                            | Tier   | Priority |
|:-----------------|:-------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------|:-------|:---------|
| CNV-67524 (epic) | As an integration tool, I can define a VM with an explicit IPv4 address (through cloud-init) on the UDN primary pod network.         | Verify VM is created with the specified IP address, which enables east-west communication   | Tier 2 | P0       |
|                  | As a integration tool, I can define a VM with an explicit IPv4 address (through cloud-init) on the UDN primary pod network.          | Verify VM is created with the specified IP address, which enables north-south communication | Tier 2 | P0       |
|                  | As an admin, I can live-migrate a VM with an explicit IPv4 address.                                                                  | Verify IP and connectivity is preserved over live-migration.                                | Tier 2 | P0       |
|                  | As a user, I can stop a VM with an explicit IPv4 address and start it afterward.                                                     | Verify IP is preserved over power-lifecycle.                                                | Tier 2 | P0       |
|                  | As an admin, I can upgrade a cluster that has a VM with an explicit IPv4 address.                                                    | Verify IP is preserved over upgrade.                                                        | Tier 2 | P1       |
|                  | As an integration tool, I can define a VM with an explicit IPv4 address (through the default DHCPv4) on the UDN primary pod network. | Verify VM is created with the specified IP address, which enables east-west communication   | Tier 2 | P2       |

---

### **IV. Sign-off and Approval**

This Software Test Plan requires approval from the following stakeholders:

* **Reviewers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - Development Representative (OCP-V): [Orel Misan](@orelmisan)
  - QE Members (OCP-V): [Yossi Segev](@yossisegev), [Anat Wax](@Anatw), [Asia Zhivov Khromov](@azhivovk), [Sergei Volkov](@yossservolkov)
* **Approvers:**
  - QE Architect (OCP-V): [Ruth Netser](@rnetser)
  - Product Manager/Owner: [Ronen Sde-Or](ronen@redhat.com), [Petr Horacek](@phoracek)
