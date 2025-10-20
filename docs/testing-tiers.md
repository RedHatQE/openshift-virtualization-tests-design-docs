# Testing Tiers Guide

## Overview

OpenShift Virtualization uses a tiered testing strategy to ensure comprehensive coverage while optimizing test execution time and resource usage. Understanding the differences between **Unit Tests**, **Tier 1 (Functional Tests)**, and **Tier 2 (End-to-End Tests)** is critical for effective test planning and implementation.

## Testing Pyramid

```text
        /\
       /  \      Tier 2 (E2E)
      /____\     - Fewest tests, full system
     /      \
    / Tier 1 \   Tier 1 (Functional)
   /__________\  - More tests, feature integration
  /            \
 /  Unit Tests  \ Unit Tests
/________________\ - Most tests, isolated components
```

## Unit Tests

### What Are Unit Tests?

**Unit tests** validate individual components, functions, or methods in isolation, without dependencies on external systems, databases, or network services.

### Characteristics

- **Scope:** Single function, method, or small component
- **Dependencies:** None - uses mocks, stubs, or fakes

### Purpose

- Verify individual units of code work correctly
- Catch regressions early in development
- Enable fast feedback loops for developers
- Serve as living documentation of component behavior
- Enable safe refactoring

### When to Use Unit Tests

- Testing business logic
- Validating data structures and models
- Testing utility functions
- Verifying error handling
- Testing parsing and validation logic

### Best Practices

- **Isolated:** No external dependencies
- **Deterministic:** Same input always produces same output
- **Focused:** Test one thing per test
- **Maintainable:** Clear test names and structure

## Tier 1 - Functional Tests

### What Are Tier 1 Tests?

**Tier 1 tests** verify core functionality of individual features or components within an OpenShift Virtualization cluster. They test one feature at a time with minimal cross-feature dependencies.

**Note:** Tier 1 refers to downstream testing in the OpenShift Virtualization product context.

### Characteristics

- **Scope:** Single feature or component functionality
- **Dependencies:** Requires OpenShift cluster with OpenShift Virtualization installed (for downstream testing)
- **Environment:** Test cluster (can be minimal configuration)

### Purpose

- Verify the feature works as designed
- Test API contracts and interfaces
- Validate basic user workflows
- Ensure core functionality doesn't have regression
- Block broken code from merging

### Test Scope for Tier 1

**Functional Areas Covered - Examples:**
- VM lifecycle (create, start, stop, delete)
- Storage operations (DataVolumes, PVCs)
- Network configuration (basic networking, NADs)
- VM migration (single migration)
- Snapshots (create, restore a single snapshot)
- Hot-plug operations (single device)
- Basic API validation

**What's NOT in Tier 1:**
- Multi-feature integration scenarios
- Complex end-to-end user workflows and user stories
- Performance and scale testing
- Upgrade scenarios
- Disaster recovery scenarios

## Tier 2 - End-to-End (E2E) Tests

### What Are Tier 2 Tests?

**Tier 2 tests** validate complete user workflows and multi-feature integrations across the entire OpenShift Virtualization stack. They simulate real-world scenarios from a user's perspective.

**Important:** Tier 2 tests are strictly **user-scenario focused**. They validate what end users experience and interact with, not internal system behavior, implementation details, or diagnostic information that users don't directly consume.

### Characteristics

- **Scope:** Complete user workflows, multi-feature integrations
- **Environment:** Production-like test environment

### Purpose

- Validate complete user journeys from end-to-end
- Test feature interactions and integration points as experienced by users
- Verify system works as a cohesive whole from the user's perspective
- Simulate real production user scenarios
- Catch integration issues that would impact user workflows
- Validate upgrade and migration paths from the user experience standpoint

**Key Principle:** Tests should only verify observable user outcomes, not internal system state or logs.

### Test Scope for Tier 2

**End-to-End Scenarios - Examples:**
- Complete application deployment workflows
- Multi-VM interactions and communication
- Storage lifecycle (provision → attach → snapshot → restore)
- Live migration with workload validation
- Upgrade paths and version compatibility
- Disaster recovery scenarios
- Multi-network configurations
- Performance under realistic load
- Security and RBAC workflows

**Integration Points Tested Examples:**
- VM ↔ Storage
- VM ↔ Network
- VM ↔ Migration
- Storage ↔ Snapshots
- Multiple VMs ↔ Networks
- Operator ↔ All components

### Tier 2 Test Requirements

**What Tier 2 Tests:**
- **Production-like environment** required
- **Must test real user workflows**
- **Must validate feature integrations**
- **Cover upgrade scenarios**

**What Tier 2 Does NOT Test:**
- Internal debug logs validation and analysis (not user-facing). Note: Tests may verify user-observable Kubernetes Events as these are part of the user-facing API but should not parse internal pod logs.
- Internal component implementation details (not observable by users)
- Code-level unit behaviors (internal to the system)
- Low-level API internals that are not exposed to users
- Developer debugging workflows (not part of the user experience)
- Kubernetes and OpenShift features (underlying platform, not virtualization features)
- System metrics that users don't directly interact with
- Internal error messages or stack traces are not shown to users

## Comparison Matrix

| Aspect                  | Unit Tests             | Tier 1 (Functional)                  | Tier 2 (E2E)                  |
|:------------------------|:-----------------------|:-------------------------------------|:------------------------------|
| **Scope**               | Single function/method | Single feature                       | Complete workflows            |
| **Dependencies**        | None (mocked)          | OpenShift + OpenShift Virtualization | Full production-like setup    |
| **Isolation**           | Complete               | Feature-level                        | System-level integration      |

## Resources

- [STP Guide](./stp-guide.md)
- [STP Template](../stps/stp-template/stp.md)
- [OpenShift Virtualization Test Repository](https://github.com/kubevirt/kubevirt/tree/main/tests)
