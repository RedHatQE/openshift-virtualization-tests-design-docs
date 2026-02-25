"""
Shared fixtures for CNV-72112 VM IP Address Filtering tests.

STP Reference: stps/sig-ui/vm-ip-filter-stp.md
Jira: CNV-72112
"""

import logging

import pytest
from ocp_resources.namespace import Namespace
from ocp_resources.virtual_machine import VirtualMachine
from ocp_resources.virtual_machine_instance import VirtualMachineInstance

from utilities.constants import IPV4_STR, TIMEOUT_2MIN
from utilities.network import get_ip_from_vm_or_virt_handler_pod
from utilities.virt import VirtualMachineForTests, fedora_vm_body, running_vm

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="class")
def test_namespaces_scope_class(admin_client):
    """Create multiple test namespaces for cross-namespace filtering tests."""
    ns_names = ["e2e-ip-filter-alpha", "e2e-ip-filter-beta", "e2e-ip-filter-gamma"]
    namespaces = []
    for name in ns_names:
        ns = Namespace(client=admin_client, name=name, teardown=True)
        ns.deploy()
        ns.wait_for_status(
            status=Namespace.Status.ACTIVE, timeout=TIMEOUT_2MIN
        )
        namespaces.append(ns)
    yield namespaces
    for ns in reversed(namespaces):
        ns.clean_up()


@pytest.fixture(scope="class")
def vms_across_namespaces_scope_class(
    unprivileged_client, test_namespaces_scope_class
):
    """Create VMs in multiple namespaces, all running with IP addresses assigned."""
    vms = []
    vm_names = ["vm-search-target", "vm-search-decoy-1", "vm-search-decoy-2"]
    for ns, vm_name in zip(test_namespaces_scope_class, vm_names):
        vm = VirtualMachineForTests(
            name=vm_name,
            namespace=ns.name,
            client=unprivileged_client,
            body=fedora_vm_body(name=vm_name),
            run_strategy=VirtualMachine.RunStrategy.ALWAYS,
        )
        vm.deploy()
        vms.append(vm)

    for vm in vms:
        running_vm(vm=vm)

    yield vms

    for vm in reversed(vms):
        vm.clean_up()


@pytest.fixture(scope="class")
def target_vm_ip_scope_class(vms_across_namespaces_scope_class):
    """Get the IPv4 address of the target (first) VM."""
    target_vm = vms_across_namespaces_scope_class[0]
    ip = get_ip_from_vm_or_virt_handler_pod(family=IPV4_STR, vm=target_vm)
    assert ip, f"Target VM {target_vm.name} has no IPv4 address assigned"
    return str(ip)


def get_vmis_matching_ip(admin_client, target_ip):
    """Return list of VMIs whose interfaces contain the target IP address.

    This mirrors the OCP Console IP address filtering behavior at the API level.
    """
    all_vmis = list(VirtualMachineInstance.get(client=admin_client))
    matched = []
    for vmi in all_vmis:
        interfaces = vmi.instance.status.interfaces or []
        for iface in interfaces:
            ip_addresses = iface.get("ipAddresses", [])
            if any(target_ip in addr for addr in ip_addresses):
                matched.append(vmi)
                break
    return matched
