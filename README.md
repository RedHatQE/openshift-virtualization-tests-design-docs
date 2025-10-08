# openshift-virtualizatio-tests-stps
This repository is used to manager openshift-virtualization-tests software test plans (STPs) allowing enhanced SIG improvement and collaboration

# Openshift Virtualization Quality Engineering Artifacts and Software Test Planning (STP) Repository

This repository is used to manage and track Quality Engineering (QE) artifacts for Openshift Virtualization enhancements, ensuring that features meet defined quality standards and user requirements before release.

## WHY

The purpose of this repository and the associated process is to ensure the **quality and reliability** of the software. By centralizing these artifacts, we ensure clear visibility of test coverage, required resources, and risks.

This process is mandatory for formal QE sign-off and feature acceptance, as **automation must be merged for GA**.

## Glossary

| Term | Definition | Citation |
| :--- | :--- | :--- |
| **STP** | **Software Test Plan**: Provides the overall roadmap for testing, detailing scope, approach, resources, and schedule. | |
| **STD** | **Software Test Description**: Provides the specific instructions for executing individual tests. | |
| **VEP** | **Virtualization Enhancement Proposal**. | |
| **NFR** | **Non-Functional Requirements**: Aspects of testing covering performance, security, monitoring, usability, etc.. | |
| **EF** | **Enhancement Freeze**. | |
| **CF** | **Code Freeze**. | |

## Process Flow: VEP to QE Sign-off

The QE process is initiated upon feature definition, usually correlating with an approved VEP.

1.  **Feature Review (Pre-STP)**: The QE owner reviews VEPs (Openshift Virtualization and OCP) and requirements to **understand the value** for RH customers. This stage confirms that requirements are **testable and unambiguous** and that acceptance criteria are clearly defined. Non-functional requirements (NFRs) like Downtime, Connectivity, Performance, Security, Monitoring (metrics/alerts), Portability, and Documentation must be covered.
2.  **STP Creation**: The QE owner writes the STP, detailing the scope of testing (functional and non-functional requirements), the overall Test Strategy (including types like Functional, Regression, Upgrade, and Compatibility testing), Test Environment requirements, and Risk Management. The STP must include a clear plan to address risks, including calling out an explicit **list of functionalities that cannot be tested**.
3.  **STD Creation**: Once the developer begins actual development, the QE owner writes the STD. STDs must create test cases **with the customer's perspective in mind**. Each step in the test case must be a test and **verify one thing**, and each step must include the expected results.
4.  **Tiering and Automation**: QE works with the Development team to define coverage for **Tier 1 and Tier 2 tests**. Automation is crucial, and tests must be running as part of one of the **release checklist jobs**.
5.  **Sign-off**: Upon meeting all **Exit Criteria** (high-priority defects resolved, test coverage achieved, test automation merged), the QE owner reviews documentation and formally signs off the feature. Jira tasks are used to **block the epic** until sign-off is complete.

## Artifacts and Templates

This repository hosts the templates for the core QE deliverable:

**Software Test Plan (STP) Template**: Outlines the scope, approach, resources, and schedule for all testing activities.
  *   **Entry Criteria**: Requirements/design approved, environment set up, test cases reviewed.
  *   **Exit Criteria**: All high-priority defects resolved, automation merged, acceptance criteria met.

## Responsibilities

### QE Owner

The QE Owner is responsible for the overall quality assurance process for a feature, which includes:

*   Writing the STP and STD.
*   Reviewing the design and technology to identify potential testing challenges.
*   Ensuring the plan addresses non-functional requirements (NFRs).
*   Managing risk, including adding an explicit list of untestable aspects to the STP.
*   Making sure tests are running as part of one of the **release checklist jobs**.
*   Performing the final **Sign off the feature as QE**.

### Stakeholders (SIGs/Approvers)

All relevant stakeholders, including SIG representatives, must be aware of and agree to the test plan.

*   Stakeholders must **approve** the STP.
*   Stakeholders must be aware of and **agree to take the risk** associated with any explicit list of functionalities that **cannot be tested**.
*   SIGs are responsible for coordinating reviews and approvals of VEPs and STPs.

## Deadlines and Check-ins

Deadlines are governed by the Openshift Virtualization release cycle, focusing on:

The QE process is governed by Openshift Virtualization and KubeVirt release milestones, focusing on test planning completion and automation delivery.

1.  **VEP Planning / Feature Review:**
    *   At the **beginning of every release cycle**, each SIG prioritizes VEPs and decides which ones are being tracked for the upcoming release. This centralized prioritization focuses community efforts on associated pull requests.
    *   QE involvement starts immediately with the **feature review**, ensuring the requirements are reviewed. The review includes verifying that requirements are **testable and unambiguous** and that the value of the feature for RH customers is understood.

2.  **Enhancement Freeze (EF):**
    *   The Software Test Plan (STP) must be written, reviewed, and approved by stakeholders. Testing cannot begin until the requirements and design documents are approved and stable, and test cases are reviewed.

3.  **Code Freeze (CF):**
    *   QE sign-off requires that **test automation must be merged for GA**. The Exit Criteria for testing requires that test automation is merged.
    *   Features that do not land in the release branch prior to CF will need to file for an exception.

> [!NOTE]
> QE sign-off is contingent on automation being merged. Features not landing in the release branch prior to CF will need to file for an exception.


## **Common Questions**

This section addresses frequently asked questions regarding VEP ownership, approvals, and managing delays, which impact the QE process and feature readiness.

| Question                                                                      | Answer                                                                                                                                                                                                                                                                                                             | 
|:------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Do PRs need to be approved by STP approvers?**                              | No, the approval of Pull Requests (PRs) is the **whole SIG's responsibility** for their code. The approver should be aware of the STP and approve based on its content, and a defined process exists to ensure this occurs.                                                                                        |
| **What to do in case all PRs didn't make it on time?**                        | The author of the STP needs to **file for an exception**. The outcome will be determined individually by maintainers based on the context of the delay.                                                                                                                                                            |
| **How to raise attention for my STP?**                                        | The QE has bi-weekly **recurring meetings**. The STP owner is encouraged to join the meeting and introduce the STP to the community to raise awareness.                                                                                                                                                            |
| **What if the feature is relates to more than one SIG?**                      | While features can relate to **multiple SIGs**, a single SIG must always own it. STP owners should reach out to other SIGs that are relevant for the feature and make sure that they also review the STP.                                                                                                          |
