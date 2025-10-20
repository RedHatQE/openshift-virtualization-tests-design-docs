# Software Test Plan (STP) Guide

## What is an STP?

A **Software Test Plan (STP)** is a comprehensive document that serves as the overall roadmap for testing a feature or enhancement. It details the scope, approach, resources, and schedule for all testing activities.

The STP is a **mandatory deliverable** for formal QE sign-off and feature acceptance in OpenShift Virtualization.

## Why Do We Need STPs?

### Quality Assurance
- Ensures **systematic coverage** of all requirements (functional and non-functional)
- Provides **clear visibility** of test coverage, required resources, and identified risks
- Documents **untestable aspects** upfront with stakeholder agreement

### Process Alignment
- Aligns QE activities with the OpenShift Virtualization release cycle
- Ensures **automation is merged for GA** (mandatory exit criteria)
- Creates a shared understanding between Dev, QE, and Product Management

### Risk Management
- Explicitly identifies what **can** and **cannot** be tested
- Requires stakeholder sign-off on untestable functionalities
- Documents mitigation strategies for identified risks

## STP Structure

The STP template includes the following main sections:

### I. Motivation and Requirements Review

**Purpose:** Ensure QE understands the feature value and testability before planning begins.

**Key Activities:**
- Review feature requirements (KubeVirt and OCP enhancements)
- Confirm requirements are **testable and unambiguous**
- Verify acceptance criteria are clearly defined
- Ensure Non-Functional Requirements (NFRs) are covered:
  - Performance
  - Security
  - Usability
  - Monitoring (metrics/alerts)
  - Scalability
  - Portability

**Critical Checkpoint:** Developer Handoff/QE Kickoff meeting where Dev/Arch walks QE through design and architecture.

### II. Software Test Plan (STP)

#### 1. Introduction and Scope
- **Purpose:** High-level overview of testing approach
- **Scope of Testing:** What will be tested (functional and non-functional)
- **Document Conventions:** Acronyms and definitions

#### 2. Test Objectives
Primary goals:
- Verify software meets all requirements
- Identify and report defects
- Ensure software performs as expected
- Assess overall quality and release readiness

#### 3. Motivation
QE perspective on testing priorities:
- **User Stories:** Key scenarios driving test priorities
- **Testing Goals:** Specific, measurable objectives (coverage targets, performance SLAs, etc.)
- **Non-Goals:** Explicitly document what's **out of scope** with stakeholder sign-off

#### 4. Test Strategy
**Types of Testing:**
- Functional Testing
- Automation Testing
- Performance Testing
- Security Testing
- Usability Testing
- Compatibility Testing
- Regression Testing
- Upgrade Testing
- Backward Compatibility Testing

**Potential Areas:**
- Dependencies on other components
- Monitoring requirements (metrics/alerts)
- Cross-integration impacts
- UI requirements

#### 5. Test Environment
Virtualization-specific requirements:
- Cluster topology (bare metal, SNO, compact cluster, etc.)
- OCP & OpenShift Virtualization versions
- Hardware requirements (CPU virtualization, compute resources, special hardware)
- Storage configuration (ODF, LSO, CSI drivers)
- Network configuration (CNI, secondary networks, network plugins)
- Required operators
- Platform (bare metal, AWS, Azure, GCP, etc.)
- Special configurations (disconnected, proxy, FIPS)

#### 6. Entry and Exit Criteria

**Entry Criteria:**
- Requirements and design documents approved and stable
- Test environment set up and configured
- Test cases reviewed and approved

**Exit Criteria:**
- All high-priority defects are resolved and verified
- Test coverage goals achieved
- **Test automation merged** (required for GA sign-off)
- All planned test cycles are completed
- Test summary report approved
- Acceptance criteria met

#### 7. Risk Management
Document risks and mitigation strategies:
- Timeline/Schedule Risk
- Insufficient test coverage
- Unstable test environment
- **Untestable aspects** (must be explicitly documented with stakeholder agreement)
- Resource constraints
- Integration concerns

#### 8. Limitations
- Known limitations or trade-offs
- Constraints or edge cases are not covered

### III. Test Case Descriptions & Traceability

**Purpose:** Link strategic plan to tactical test cases.

**Key Components:**
1. **Test Case Repository:** Links to Jira, Polarion, or test management system
2. **Traceability Matrix:** Maps requirements to high-level test scenarios
3. **Test Scenario Descriptions:** Brief descriptions of key scenarios
4. **Traceability Maintenance:** Process for keeping traceability current

### IV. Sign-off and Approval

**Final Sign-off Checklist:**
- Tier 1 / Tier 2 tests defined
- **Automation merged** (mandatory for GA)
- Tests running in release checklist jobs
- Documentation reviewed
- Feature sign-off by QE

**Approvers:**
- QE Lead
- Product Manager
- Development Lead

## STP Lifecycle

### 1. Feature Review (Pre-STP)
- QE owner reviews feature requirements and enhancements
- Confirms testability and value for customers
- Developer Handoff/QE Kickoff meeting

### 2. STP Creation
- QE owner writes the STP
- Documents scope, strategy, environment, risks
- Includes an explicit list of untestable aspects

### 3. STP Review and Approval
- Stakeholders review the STP
- All parties agree to risk associated with untestable aspects
- STP approved before test execution begins

### 4. Test Execution
- Implement test cases based on STP
- Track progress against entry/exit criteria
- Update traceability matrix

### 5. Sign-off
- Verify all exit criteria met
- Automation merged and running in CI
- QE formally signs off the feature

## Release Cycle Integration

### Enhancement Freeze (EF)
- STP must be written, reviewed, and approved
- Testing cannot begin until requirements/design approved

### Code Freeze (CF)
- **Test automation must be merged for GA**
- Features not landing prior to CF need an exception

## Best Practices

### Early Engagement
- Start QE review immediately when the feature is defined
- Attend Developer Handoff/QE Kickoff meeting
- Identify untestable aspects early

### Clear Communication
- Document assumptions and dependencies explicitly
- Use traceability matrix to prove coverage
- Get stakeholder sign-off on non-goals

### Comprehensive Coverage
- Address both functional and non-functional requirements
- Plan for different test environments and configurations
- Include upgrade and backward compatibility testing

### Automation First
- Plan automation strategy upfront
- Identify which tests will be automated
- Ensure automation is merged before GA

### Risk Transparency
- Document all risks, including untestable aspects
- Get explicit stakeholder agreement on risk acceptance
- Propose mitigation strategies

## Common Pitfalls to Avoid

1. **Late STP Creation:** STP must be approved before testing begins
2. **Unclear Scope:** Non-goals must be explicitly documented with stakeholder sign-off
3. **Missing NFRs:** Don't forget performance, security, monitoring requirements
4. **No Traceability:** Must map requirements to test scenarios
5. **Automation Delays:** Automation must be merged for GA - plan early
6. **Untested Assumptions:** All untestable aspects must be explicitly documented

## External Resources

- [KubeVirt VEPs](https://github.com/kubevirt/enhancements/tree/main/veps)
- [OCP Enhancements](https://github.com/openshift/enhancements/tree/master/enhancements)
