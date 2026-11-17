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
- Ensures **automation is merged for GA**
- Creates a shared understanding between Dev, QE, and Product Management

### Risk Management
- Explicitly identifies what **can** and **cannot** be tested
- Requires stakeholder sign-off on untestable functionalities
- Documents mitigation strategies for identified risks

## STP Structure

**The template is the source of truth for the structure and format of an STP:**
[`stps/stp-template/stp.md`](../stps/stp-template/stp.md) (child STPs:
[`child-stp.md`](../stps/stp-template/child-stp.md)). It contains inline instructions for most fields.
This guide does not restate those instructions; it maps the template's parts and explains their purpose and the
process around them.
If this guide and the template ever disagree, the template wins and the guide must be fixed.

| Template part | Purpose |
|:--------------|:--------|
| Metadata & Tracking, Feature Overview | Identify the feature (links, maturity, owners) and explain it to a reader who has not seen it before |
| I. Motivation and Requirements Review | Requirements, customer value, testability, acceptance criteria, Feature Limitations and the outcome of the design review (Developer Handoff / QE Kickoff) |
| II.1 Scope of Testing | Testing Goals (with priority), Out of Scope, Test Limitations |
| II.2 Test Strategy | Which of the listed testing types apply and the high-level approach for each |
| II.3 / II.3.1 Environment, Tools | What the tests need to run; only new or non-standard tools |
| II.4 Entry Criteria | What must be true before testing starts |
| II.5 Risks | Uncertainties, grouped by the template's risk categories, each with mitigation and sign-off |
| III. Test Scenarios & Traceability | Each new scenario traced to a Jira requirement, with tier and priority |
| IV. Sign-off and Approval | Sign-off by at least one person per function (Feature Owner, Quality Owner, Product Manager) |

### Purpose of Each Part

The template says what to fill in. This section explains why each part exists and when it happens.

**Feature Overview and metadata.** Let a reader who has never seen the feature understand what it is,
why customers need it and which maturity phase this STP covers, and find the tracking links.

**I. Motivation and Requirements Review.** Happens before test planning. It makes sure the requirements are
understood, testable and unambiguous, that acceptance criteria are verifiable, and that the non-functional
requirements listed in the template are considered. Feature Limitations are recorded here as confirmed
product constraints. The critical checkpoint is the Developer Handoff / QE Kickoff meeting, where development
and architecture walk through the design. Its purpose is to find untestable aspects and ambiguous
requirements early, while they are cheap to fix.

**II.1 Scope of Testing.** States what testing is meant to achieve: verify that the feature meets its
requirements, find defects, and assess quality and release readiness. The scope must cover functional and
non-functional requirements and trace back to the user stories from Section I; the user stories drive the
testing priorities. Testing Goals are specific and measurable so that completion can be judged objectively.
Out of Scope and Test Limitations make the gap between what the product can do and what QE verifies visible.

**II.2 Test Strategy.** Decides which testing types apply and the high-level approach for each, including
dependencies on other components, monitoring, impact on other features and UI. Goals say *what* must be
verified; the strategy says *how* and with which types of testing.

**II.3 Test Environment and Tools.** States the virtualization-specific needs up front, so the environment can
be prepared in time; the template lists the fields to fill. Tools are listed only when they are new or
different from standard test infrastructure.

**II.4 Entry Criteria.** The conditions that must hold before test execution starts, such as approved
requirements and design and an environment that can be set up. Feature-specific conditions are added as needed.

**II.5 Risks.** Uncertainties that might affect testing, each with a mitigation, grouped by the template's
risk categories. See Constraint Categories below for how risks differ from limitations and Out of Scope.

**III. Test Scenarios & Traceability.** Links the plan to concrete tests: each requirement is traced to its
scenarios so that coverage can be verified. Scenarios stay brief; the test cases themselves live in the test
code or the test management system (for example Jira or Polarion), linked from here where one is used.
Traceability is kept current as tests are implemented, so that Section III is accurate at sign-off.

**IV. Sign-off and Approval.** Records who accepted the plan. Stakeholders approve the STP before test
implementation starts. Feature sign-off is a later milestone, given only when Tier 1 and Tier 2 tests are
defined (Tier 3 where applicable), automation is merged for GA, tests run in the release checklist jobs, and
the documentation is reviewed.

The sign-off functions are:

- **Feature Owner**: the person accountable for the feature from the moment the requirement arrives until GA.
  They don't necessarily do all the work, but they make sure the right work happens, in the right order, by the
  right people, with nothing falling between teams and phases.
- **Quality Owner**: the person accountable for the quality of the feature, both the processes that build quality
  in and the verification that confirms it. They define what "good" means (test strategy, coverage, acceptance
  criteria), design quality in from the start instead of inspecting it at the end, and give the authoritative
  assessment of whether the feature is fit to ship.
- **Product Manager**: the person accountable for defining what gets built and why. They own the product vision
  and roadmap, gather and prioritize requirements from customers, stakeholders and market signals, translate them
  into clear problem statements for the delivery teams, and represent the customer and the business throughout
  the development lifecycle, adjusting priorities and scope as new information emerges; they are the primary
  source of requirements flowing to Feature Owners.

### Multi-SIG Features and Child STPs

When a feature spans multiple SIGs, use a **feature directory** under the owning SIG.
The parent STP defines the overall scope, and each participating SIG contributes a child STP
that covers its specific test scope.

- Start from the child template: [`stps/stp-template/child-stp.md`](../stps/stp-template/child-stp.md)
- Place the child beside the parent, as `stps/<owning-sig>/<feature-name>/<sig-name>.md`

```text
stps/<owning-sig>/<feature-name>/
├── stp.md              ← parent STP
├── <sig-name>.md       ← child STP per participating SIG
└── ...
```

**Parent STP** — defines Feature Overview, requirements, acceptance criteria, and overall coordination.
**Child STPs** — define SIG-specific testing goals, scenarios, strategy, and risks. They reference
the parent for shared context and do NOT duplicate it. A child STP intentionally omits
Enhancement(s) and Feature Maturity. Its Feature Overview describes only the SIG's scope. Every other rule
applies to it unchanged.

Single-SIG features place the STP directly under `stps/<sig>/` without a feature directory.

## Constraint Categories

An STP keeps the following kinds of constraints apart. Never mix them.

| Category | Template location | Meaning | Example |
|:---------|:------------------|:--------|:--------|
| **Feature Limitations** | I.2 | Known product constraint: the product does not support it | "Feature only supports IPv4" |
| **Out of Scope** | II.1 | The product works, but QE decided not to test it | "Windows guests are not tested" |
| **Test Limitations** | II.1 | Constraint imposed on QE that prevents testing something QE wants to test | "No dual-stack cluster available" |
| **Risks** | II.5 | Uncertainty that might affect testing, with a mitigation | "Cluster may not be ready in time" |

Rule of thumb: Feature Limitations and Test Limitations are *known facts* (about the product and about what QE
can test), risks are *uncertainties*, Out of Scope is a *decision*.
Every entry that states a limitation, an exclusion or a risk is signed off; a risk category marked "N/A"
needs only a justification in the Mitigation field. The template shows where each sign-off goes.

## Priority and Tier

**Priority** (testing goals and scenarios):

- **P0** — blocks GA; must be complete before release
- **P1** — required for full feature coverage
- **P2** — nice-to-have; can be deferred if the timeline is constrained

**Tier** — see [Testing Tiers](./testing-tiers.md). Every scenario in Section III states its tier.

## Checklist Before Requesting Review

- Template HTML comments and example text removed; no `[placeholder]` text left
- Every acceptance criterion maps to a scenario in Section III, and every Testing Goal has a scenario
- Out of Scope, Feature Limitations, Test Limitations and Risks each carry the required sign-off (name/date)
- Test Strategy addresses every testing type listed in the template (checked, or unchecked with justification)

## Moving an STP

The canonical STP may move, but its historical paths must remain available as permanent stubs. When moving an STP:

1. Move the canonical STP to the new path.
2. Leave a stub at the old path.
3. Update every existing stub for that STP to point directly to the new canonical path.
4. Never delete historical stubs.
5. The pre-commit hooks validate the move stub before submitting the change.

The validator and its regression tests run as pre-commit-managed Python hooks in both local pre-commit and pre-commit.ci. They validate all existing moved-STP stubs; pre-commit does not inspect deleted paths that are no longer present in the working tree.

Use this format for every historical path:

```markdown
<!-- STP-MOVED-TO: stps/<sig>/<current-file>.md -->

# MOVED

This STP was moved to [the current STP](<relative-link-from-this-stub>.md).
```

The Markdown link is relative to the stub's directory. For a nested stub at `stps/sig-virt/feature/old.md` pointing to `stps/sig-virt/feature/current.md`, use `[the current STP](current.md)`. The target in `STP-MOVED-TO` must be the current canonical file, not another stub. The validator checks that targets exist and stubs are clearly marked.

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
- Track progress against testing goals
- Update traceability matrix

### 5. Sign-off
- Verify acceptance criteria were met
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
