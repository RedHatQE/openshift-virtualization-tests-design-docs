"""
VM IP Address Filtering E2E Tests - CNV-72112

Validates VM IP address filtering behavior across namespaces at the API level,
mirroring the OCP Console's VirtualMachinesList component filtering logic.

STP Reference: stps/sig-ui/vm-ip-filter-stp.md
Jira: CNV-72112
"""

import logging

import pytest
from ocp_resources.virtual_machine import VirtualMachine

from utilities.constants import IPV4_STR
from utilities.network import get_ip_from_vm_or_virt_handler_pod
from utilities.virt import VirtualMachineForTests, fedora_vm_body, running_vm

from conftest import get_vmis_matching_ip

LOGGER = logging.getLogger(__name__)

pytestmark = [
    pytest.mark.tier2,
    pytest.mark.ipv4,
]


@pytest.mark.usefixtures(
    "test_namespaces_scope_class",
    "vms_across_namespaces_scope_class",
)
class TestCrossNamespaceIPFilter:
    """
    Tests for cross-namespace VM IP address filtering.

    Validates that VMs can be discovered by IP address across multiple
    namespaces, mirroring the OCP Console's "All Projects" IP filter
    behavior at the API level.

    Markers:
        - tier2
        - ipv4

    Preconditions:
        - OpenShift cluster with OCP 4.18+ and OVN-Kubernetes
        - OpenShift Virtualization CNV v4.18.26+
        - 3 test namespaces with running VMs having assigned IP addresses
    """

    @pytest.mark.polarion("CNV-72112")
    @pytest.mark.jira("CNV-72112")
    def test_ts_cnv72112_013_cross_namespace_ip_search(
        self,
        admin_client,
        vms_across_namespaces_scope_class,
        target_vm_ip_scope_class,
    ):
        """
        Test TS-CNV-72112-013: Verify cross-namespace IP search returns correct VM.

        Preconditions:
            - 3 namespaces created with 1 VM each
            - All VMs running with unique IP addresses
            - Target VM IP address recorded

        Steps:
            1. List all VMIs across all namespaces (mirrors "All Projects" view)
            2. Filter VMIs by the target VM's IP address
            3. Verify exactly one VMI matches
            4. Verify the matched VMI belongs to the target VM
            5. Verify the matched VMI is in the correct namespace

        Expected:
            - Exactly one VMI matches the target IP address
            - The matched VMI is the target VM (vm-search-target)
            - The matched VMI is in the target namespace (e2e-ip-filter-alpha)
            - Decoy VMs in other namespaces are not returned
        """
        target_vm = vms_across_namespaces_scope_class[0]
        target_ip = target_vm_ip_scope_class
        decoy_vms = vms_across_namespaces_scope_class[1:]

        LOGGER.info(
            f"Searching for VM by IP {target_ip} across all namespaces"
        )

        matched_vmis = get_vmis_matching_ip(
            admin_client=admin_client, target_ip=target_ip
        )

        assert len(matched_vmis) == 1, (
            f"Expected exactly 1 VMI matching IP {target_ip}, "
            f"got {len(matched_vmis)}: "
            f"{[vmi.name for vmi in matched_vmis]}"
        )

        matched_vmi = matched_vmis[0]
        assert matched_vmi.name == target_vm.vmi.name, (
            f"Expected matched VMI to be {target_vm.vmi.name}, "
            f"got {matched_vmi.name}"
        )
        assert matched_vmi.namespace == target_vm.namespace, (
            f"Expected matched VMI namespace to be {target_vm.namespace}, "
            f"got {matched_vmi.namespace}"
        )

        LOGGER.info(
            f"Verifying decoy VMs are not returned in IP filter results"
        )
        matched_names = {vmi.name for vmi in matched_vmis}
        for decoy in decoy_vms:
            assert decoy.vmi.name not in matched_names, (
                f"Decoy VM {decoy.vmi.name} should not appear in "
                f"IP filter results for {target_ip}"
            )

        LOGGER.info(
            f"Cross-namespace IP search successful: found {target_vm.name} "
            f"in namespace {target_vm.namespace}"
        )


class TestVMLifecycleIPFilter:
    """
    Tests for VM lifecycle with IP address filtering.

    Validates that the IP filter reflects real-time cluster state across
    VM creation and deletion, ensuring no stale results appear.

    Markers:
        - tier2
        - ipv4

    Preconditions:
        - OpenShift cluster with OCP 4.18+ and OVN-Kubernetes
        - OpenShift Virtualization CNV v4.18.26+
    """

    @pytest.mark.polarion("CNV-72112")
    @pytest.mark.jira("CNV-72112")
    def test_ts_cnv72112_014_vm_lifecycle_ip_filter(
        self,
        admin_client,
        unprivileged_client,
        namespace,
    ):
        """
        Test TS-CNV-72112-014: Verify IP filter across VM create and delete lifecycle.

        Preconditions:
            - Test namespace available

        Steps:
            1. Create a Fedora VM in the test namespace
            2. Wait for VM to start and obtain an IP address
            3. Record the assigned IP address
            4. List all VMIs and filter by the assigned IP
            5. Verify the VM is found in the filter results
            6. Delete the VM (exit context manager)
            7. List all VMIs and filter by the same IP again
            8. Verify the VM no longer appears in filter results

        Expected:
            - Newly created VM is discoverable by IP after startup
            - Deleted VM does not appear in IP filter results
            - No stale data remains after VM deletion
        """
        vm_name = "vm-lifecycle-filter-test"

        LOGGER.info(f"Creating VM {vm_name} for lifecycle IP filter test")

        with VirtualMachineForTests(
            name=vm_name,
            namespace=namespace.name,
            client=unprivileged_client,
            body=fedora_vm_body(name=vm_name),
            run_strategy=VirtualMachine.RunStrategy.ALWAYS,
        ) as vm:
            running_vm(vm=vm)

            vm_ip = get_ip_from_vm_or_virt_handler_pod(
                family=IPV4_STR, vm=vm
            )
            assert vm_ip, f"VM {vm.name} has no IPv4 address assigned"
            vm_ip_str = str(vm_ip)

            LOGGER.info(
                f"VM {vm_name} running with IP {vm_ip_str}, "
                f"verifying IP filter finds it"
            )

            matched_vmis = get_vmis_matching_ip(
                admin_client=admin_client, target_ip=vm_ip_str
            )
            assert len(matched_vmis) >= 1, (
                f"VM {vm_name} with IP {vm_ip_str} not found in VMI listing"
            )
            assert any(
                vmi.name == vm.vmi.name for vmi in matched_vmis
            ), (
                f"VM {vm_name} (VMI: {vm.vmi.name}) not in matched results: "
                f"{[vmi.name for vmi in matched_vmis]}"
            )

            LOGGER.info(
                f"VM {vm_name} found by IP {vm_ip_str}. "
                f"Now deleting VM to verify removal from filter."
            )

        LOGGER.info(
            f"VM {vm_name} deleted. Verifying IP {vm_ip_str} no longer "
            f"returns results."
        )

        matched_after_delete = get_vmis_matching_ip(
            admin_client=admin_client, target_ip=vm_ip_str
        )
        vm_still_present = any(
            vmi.name == vm_name or vmi.namespace == namespace.name
            for vmi in matched_after_delete
        )
        assert not vm_still_present, (
            f"Deleted VM {vm_name} still appears in IP filter results "
            f"for {vm_ip_str}. Stale data detected."
        )

        LOGGER.info(
            f"VM lifecycle IP filter test passed: VM {vm_name} "
            f"correctly removed from filter results after deletion"
        )


@pytest.mark.usefixtures(
    "test_namespaces_scope_class",
    "vms_across_namespaces_scope_class",
)
class TestBulkActionIPFilter:
    """
    Tests for bulk actions on IP-filtered VM results.

    Validates that operations (stop/start) applied to VMs identified
    through IP filtering affect only the targeted VMs, not other VMs
    in the cluster.

    Markers:
        - tier2
        - ipv4

    Preconditions:
        - OpenShift cluster with OCP 4.18+ and OVN-Kubernetes
        - OpenShift Virtualization CNV v4.18.26+
        - 3 test namespaces with running VMs having assigned IP addresses
    """

    @pytest.mark.polarion("CNV-72112")
    @pytest.mark.jira("CNV-72112")
    def test_ts_cnv72112_015_bulk_stop_filtered_vms(
        self,
        admin_client,
        vms_across_namespaces_scope_class,
        target_vm_ip_scope_class,
    ):
        """
        Test TS-CNV-72112-015: Verify bulk stop affects only IP-filtered VMs.

        Preconditions:
            - 3 VMs running across 3 namespaces
            - Target VM IP address recorded

        Steps:
            1. Filter VMIs by the target VM's IP address
            2. Verify exactly one VM matches the filter
            3. Stop the matched VM (simulating bulk stop on filtered results)
            4. Verify the target VM is stopped
            5. Verify all decoy VMs remain running
            6. Restart the target VM to restore state

        Expected:
            - Only the VM matching the IP filter is stopped
            - Decoy VMs in other namespaces remain running and unaffected
            - After restart, the target VM returns to Running state
        """
        target_vm = vms_across_namespaces_scope_class[0]
        decoy_vms = vms_across_namespaces_scope_class[1:]
        target_ip = target_vm_ip_scope_class

        LOGGER.info(
            f"Filtering VMs by IP {target_ip} for bulk stop operation"
        )

        matched_vmis = get_vmis_matching_ip(
            admin_client=admin_client, target_ip=target_ip
        )
        assert len(matched_vmis) == 1, (
            f"Expected 1 VMI matching IP {target_ip} for bulk operation, "
            f"got {len(matched_vmis)}"
        )

        LOGGER.info(
            f"Stopping target VM {target_vm.name} "
            f"(simulating bulk stop on filtered results)"
        )
        target_vm.stop(wait=True)

        LOGGER.info("Verifying target VM is stopped")
        assert not target_vm.ready, (
            f"Target VM {target_vm.name} should be stopped but is still ready"
        )

        LOGGER.info("Verifying decoy VMs remain running")
        for decoy in decoy_vms:
            assert decoy.ready, (
                f"Decoy VM {decoy.name} in namespace {decoy.namespace} "
                f"should still be running but is not ready. "
                f"Bulk stop incorrectly affected non-filtered VM."
            )

        LOGGER.info(
            f"Restarting target VM {target_vm.name} to restore test state"
        )
        target_vm.start(wait=True)
        target_vm.vmi.wait_until_running()

        LOGGER.info(
            f"Bulk action test passed: only target VM {target_vm.name} "
            f"was stopped, {len(decoy_vms)} decoy VMs remained running"
        )
