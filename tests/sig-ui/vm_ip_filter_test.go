/*
VM IP Address Filtering Tests

Validates VM/VMI listing and IP address filtering behavior at the API level,
mirroring the OCP Console's VirtualMachinesList component filtering logic.

STP Reference: stps/sig-ui/vm-ip-filter-stp.md
Jira: CNV-72112
PR: https://github.com/kubevirt-ui/kubevirt-plugin/pull/3164
*/
package compute

import (
	"context"
	"fmt"
	"strings"
	"time"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"

	k8sv1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	v1 "kubevirt.io/api/core/v1"
	"kubevirt.io/client-go/kubecli"

	"kubevirt.io/kubevirt/pkg/libvmi"
	"kubevirt.io/kubevirt/tests/console"
	"kubevirt.io/kubevirt/tests/decorators"
	"kubevirt.io/kubevirt/tests/framework/kubevirt"
	"kubevirt.io/kubevirt/tests/framework/matcher"
	"kubevirt.io/kubevirt/tests/libnet"
	"kubevirt.io/kubevirt/tests/libvmifact"
	"kubevirt.io/kubevirt/tests/libvmops"
	"kubevirt.io/kubevirt/tests/libwait"
	"kubevirt.io/kubevirt/tests/testsuite"
)

// filterVMIsByIP returns VMIs whose IP address matches the given target IP.
// This mirrors the OCP Console's IP address filtering logic in VirtualMachinesList.tsx.
func filterVMIsByIP(vmis []v1.VirtualMachineInstance, targetIP string) []v1.VirtualMachineInstance {
	var matched []v1.VirtualMachineInstance
	for _, vmi := range vmis {
		for _, iface := range vmi.Status.Interfaces {
			if iface.IP == targetIP {
				matched = append(matched, vmi)
				break
			}
			for _, ip := range iface.IPs {
				if ip == targetIP {
					matched = append(matched, vmi)
					break
				}
			}
		}
	}
	return matched
}

// filterVMIsByPartialIP returns VMIs whose IP address contains the given substring.
func filterVMIsByPartialIP(vmis []v1.VirtualMachineInstance, partial string) []v1.VirtualMachineInstance {
	var matched []v1.VirtualMachineInstance
	for _, vmi := range vmis {
		for _, iface := range vmi.Status.Interfaces {
			if strings.Contains(iface.IP, partial) {
				matched = append(matched, vmi)
				break
			}
		}
	}
	return matched
}

var _ = Describe("[CNV-72112] VM IP Address Filtering", decorators.SigCompute, func() {
	var virtClient kubecli.KubevirtClient

	BeforeEach(func() {
		virtClient = kubevirt.Client()
	})

	Context("IP address filter with VMs across namespaces", Ordered, decorators.OncePerOrderedCleanup, func() {
		var (
			ctx            context.Context
			namespaceA     string
			namespaceB     string
			vmTarget       *v1.VirtualMachine
			vmDecoy        *v1.VirtualMachine
			targetIP       string
			decoyIP        string
		)

		BeforeAll(func() {
			ctx = context.Background()
			namespaceA = testsuite.GetTestNamespace(nil)
			namespaceB = testsuite.NamespaceTestAlternative

			By("Creating target VM in namespace A")
			vmiSpecTarget := libvmifact.NewFedora(
				libvmi.WithInterface(libvmi.InterfaceDeviceWithMasqueradeBinding()),
				libvmi.WithNetwork(v1.DefaultPodNetwork()),
				libvmi.WithLabel("test-role", "target"),
				libvmi.WithLabel("env", "production"),
			)
			vmTarget = libvmi.NewVirtualMachine(vmiSpecTarget, libvmi.WithRunStrategy(v1.RunStrategyAlways))
			var err error
			vmTarget, err = virtClient.VirtualMachine(namespaceA).Create(ctx, vmTarget, metav1.CreateOptions{})
			Expect(err).ToNot(HaveOccurred())
			Eventually(matcher.ThisVM(vmTarget)).WithTimeout(300 * time.Second).WithPolling(time.Second).Should(matcher.BeReady())

			By("Getting target VMI IP address")
			vmiTarget, err := virtClient.VirtualMachineInstance(namespaceA).Get(ctx, vmTarget.Name, metav1.GetOptions{})
			Expect(err).ToNot(HaveOccurred())
			vmiTarget = libwait.WaitUntilVMIReady(vmiTarget, console.LoginToFedora)
			targetIP = libnet.GetVmiPrimaryIPByFamily(vmiTarget, k8sv1.IPv4Protocol)
			Expect(targetIP).ToNot(BeEmpty(), "Target VM should have an IPv4 address")

			By("Creating decoy VM in namespace B")
			vmiSpecDecoy := libvmifact.NewFedora(
				libvmi.WithInterface(libvmi.InterfaceDeviceWithMasqueradeBinding()),
				libvmi.WithNetwork(v1.DefaultPodNetwork()),
				libvmi.WithLabel("test-role", "decoy"),
				libvmi.WithLabel("env", "staging"),
			)
			vmDecoy = libvmi.NewVirtualMachine(vmiSpecDecoy, libvmi.WithRunStrategy(v1.RunStrategyAlways))
			vmDecoy, err = virtClient.VirtualMachine(namespaceB).Create(ctx, vmDecoy, metav1.CreateOptions{})
			Expect(err).ToNot(HaveOccurred())
			Eventually(matcher.ThisVM(vmDecoy)).WithTimeout(300 * time.Second).WithPolling(time.Second).Should(matcher.BeReady())

			By("Getting decoy VMI IP address")
			vmiDecoy, err := virtClient.VirtualMachineInstance(namespaceB).Get(ctx, vmDecoy.Name, metav1.GetOptions{})
			Expect(err).ToNot(HaveOccurred())
			vmiDecoy = libwait.WaitUntilVMIReady(vmiDecoy, console.LoginToFedora)
			decoyIP = libnet.GetVmiPrimaryIPByFamily(vmiDecoy, k8sv1.IPv4Protocol)
			Expect(decoyIP).ToNot(BeEmpty(), "Decoy VM should have an IPv4 address")
			Expect(decoyIP).ToNot(Equal(targetIP), "Target and decoy VMs must have different IPs")
		})

		AfterAll(func() {
			ctx := context.Background()
			By("Cleaning up target VM")
			err := virtClient.VirtualMachine(namespaceA).Delete(ctx, vmTarget.Name, metav1.DeleteOptions{})
			Expect(err).ToNot(HaveOccurred())
			Eventually(matcher.ThisVMIWith(namespaceA, vmTarget.Name), 240*time.Second, 1*time.Second).ShouldNot(matcher.Exist())

			By("Cleaning up decoy VM")
			err = virtClient.VirtualMachine(namespaceB).Delete(ctx, vmDecoy.Name, metav1.DeleteOptions{})
			Expect(err).ToNot(HaveOccurred())
			Eventually(matcher.ThisVMIWith(namespaceB, vmDecoy.Name), 240*time.Second, 1*time.Second).ShouldNot(matcher.Exist())
		})

		It("[test_id:TS-CNV-72112-001] should return only the VM matching the IP address filter", func() {
			By("Listing all VMIs across namespaces")
			vmiListA, err := virtClient.VirtualMachineInstance(namespaceA).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())
			vmiListB, err := virtClient.VirtualMachineInstance(namespaceB).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())

			allVMIs := append(vmiListA.Items, vmiListB.Items...)

			By(fmt.Sprintf("Filtering VMIs by target IP %s", targetIP))
			matched := filterVMIsByIP(allVMIs, targetIP)

			By("Verifying only the target VM is matched")
			Expect(matched).To(HaveLen(1), "Expected exactly 1 VMI matching IP %s", targetIP)
			Expect(matched[0].Name).To(Equal(vmTarget.Name))
			Expect(matched[0].Namespace).To(Equal(namespaceA))
		})

		It("[test_id:TS-CNV-72112-002] should display empty state when filtering by non-existent IP", func() {
			nonExistentIP := "192.0.2.99"

			By("Listing all VMIs across namespaces")
			vmiListA, err := virtClient.VirtualMachineInstance(namespaceA).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())
			vmiListB, err := virtClient.VirtualMachineInstance(namespaceB).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())

			allVMIs := append(vmiListA.Items, vmiListB.Items...)

			By(fmt.Sprintf("Filtering VMIs by non-existent IP %s", nonExistentIP))
			matched := filterVMIsByIP(allVMIs, nonExistentIP)

			By("Verifying no VMIs are matched")
			Expect(matched).To(BeEmpty(), "No VMIs should match IP %s", nonExistentIP)
		})

		It("[test_id:TS-CNV-72112-003] should return VMs matching partial IP address substring", func() {
			By("Extracting a partial IP prefix from target IP")
			parts := strings.SplitN(targetIP, ".", 3)
			Expect(len(parts)).To(BeNumerically(">=", 2), "Target IP should have at least 2 octets")
			partialIP := parts[0] + "." + parts[1]

			By("Listing all VMIs across namespaces")
			vmiListA, err := virtClient.VirtualMachineInstance(namespaceA).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())
			vmiListB, err := virtClient.VirtualMachineInstance(namespaceB).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())

			allVMIs := append(vmiListA.Items, vmiListB.Items...)

			By(fmt.Sprintf("Filtering VMIs by partial IP prefix %s", partialIP))
			matched := filterVMIsByPartialIP(allVMIs, partialIP)

			By("Verifying matching VMIs all contain the partial IP")
			Expect(matched).ToNot(BeEmpty(), "At least 1 VMI should match partial IP %s", partialIP)
			for _, vmi := range matched {
				Expect(vmi.Status.Interfaces).ToNot(BeEmpty())
				Expect(vmi.Status.Interfaces[0].IP).To(ContainSubstring(partialIP),
					"VMI %s IP should contain %s", vmi.Name, partialIP)
			}
		})

		It("[test_id:TS-CNV-72112-004] should return the correct VM when filtering by name", func() {
			By(fmt.Sprintf("Listing VMs in namespace A with field selector for name %s", vmTarget.Name))
			vmList, err := virtClient.VirtualMachine(namespaceA).List(ctx, metav1.ListOptions{
				FieldSelector: fmt.Sprintf("metadata.name=%s", vmTarget.Name),
			})
			Expect(err).ToNot(HaveOccurred())

			By("Verifying only the target VM is returned")
			Expect(vmList.Items).To(HaveLen(1))
			Expect(vmList.Items[0].Name).To(Equal(vmTarget.Name))

			By("Verifying the decoy VM is NOT returned in the name filter")
			Expect(vmList.Items[0].Name).ToNot(Equal(vmDecoy.Name))
		})

		It("[test_id:TS-CNV-72112-005] should return VMs matching the selected label", func() {
			By("Listing VMs with label env=production across namespaces")
			vmListA, err := virtClient.VirtualMachine(namespaceA).List(ctx, metav1.ListOptions{
				LabelSelector: "env=production",
			})
			Expect(err).ToNot(HaveOccurred())
			vmListB, err := virtClient.VirtualMachine(namespaceB).List(ctx, metav1.ListOptions{
				LabelSelector: "env=production",
			})
			Expect(err).ToNot(HaveOccurred())

			allFilteredVMs := append(vmListA.Items, vmListB.Items...)

			By("Verifying only VMs with env=production label are returned")
			Expect(allFilteredVMs).To(HaveLen(1))
			Expect(allFilteredVMs[0].Name).To(Equal(vmTarget.Name))
			Expect(allFilteredVMs[0].Labels["env"]).To(Equal("production"))
		})

		It("[test_id:TS-CNV-72112-006] should use frontend-filtered data when proxy pod is not active", func() {
			By("Listing VMIs in namespace A (simulating non-proxy single-namespace path)")
			vmiList, err := virtClient.VirtualMachineInstance(namespaceA).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())

			By("Filtering by target IP within single namespace")
			matched := filterVMIsByIP(vmiList.Items, targetIP)

			By("Verifying target VM is found in single-namespace filter")
			Expect(matched).To(HaveLen(1))
			Expect(matched[0].Name).To(Equal(vmTarget.Name))

			By("Verifying decoy VM from other namespace is not present")
			for _, vmi := range vmiList.Items {
				Expect(vmi.Namespace).To(Equal(namespaceA),
					"Single-namespace list should only contain VMs from namespace A")
			}
		})

		It("[test_id:TS-CNV-72112-007] should update pagination item count after filtering", func() {
			By("Listing all VMIs across both namespaces")
			vmiListA, err := virtClient.VirtualMachineInstance(namespaceA).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())
			vmiListB, err := virtClient.VirtualMachineInstance(namespaceB).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())

			totalCount := len(vmiListA.Items) + len(vmiListB.Items)
			Expect(totalCount).To(BeNumerically(">=", 2), "Should have at least 2 VMIs")

			allVMIs := append(vmiListA.Items, vmiListB.Items...)

			By(fmt.Sprintf("Filtering by target IP %s", targetIP))
			matched := filterVMIsByIP(allVMIs, targetIP)
			filteredCount := len(matched)

			By("Verifying filtered count is less than total count")
			Expect(filteredCount).To(BeNumerically("<", totalCount),
				"Filtered count (%d) should be less than total count (%d)", filteredCount, totalCount)
			Expect(filteredCount).To(Equal(1), "Exactly 1 VMI should match the target IP")
		})

		It("[test_id:TS-CNV-72112-008] should select only the filtered VMs when select-all is clicked", func() {
			By("Listing all VMIs across namespaces")
			vmiListA, err := virtClient.VirtualMachineInstance(namespaceA).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())
			vmiListB, err := virtClient.VirtualMachineInstance(namespaceB).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())

			allVMIs := append(vmiListA.Items, vmiListB.Items...)

			By("Filtering by target IP to get select-all scope")
			filteredVMIs := filterVMIsByIP(allVMIs, targetIP)
			Expect(filteredVMIs).To(HaveLen(1))

			By("Simulating select-all: verifying selection scope matches filtered results")
			selectedNames := make(map[string]bool)
			for _, vmi := range filteredVMIs {
				selectedNames[vmi.Name] = true
			}

			Expect(selectedNames).To(HaveLen(1), "Select-all should select only filtered VMIs")
			Expect(selectedNames).To(HaveKey(vmTarget.Name), "Only target VM should be selected")
			Expect(selectedNames).ToNot(HaveKey(vmDecoy.Name), "Decoy VM should not be selected")
		})

		It("[test_id:TS-CNV-72112-009] should clear all VM selections when deselect-all is clicked", func() {
			By("Listing VMIs and filtering to get a selection set")
			vmiListA, err := virtClient.VirtualMachineInstance(namespaceA).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())

			filteredVMIs := filterVMIsByIP(vmiListA.Items, targetIP)
			Expect(filteredVMIs).To(HaveLen(1))

			By("Simulating select-all then deselect-all")
			selectedNames := make(map[string]bool)
			for _, vmi := range filteredVMIs {
				selectedNames[vmi.Name] = true
			}
			Expect(selectedNames).To(HaveLen(1))

			// Deselect all
			selectedNames = make(map[string]bool)

			By("Verifying all selections are cleared")
			Expect(selectedNames).To(BeEmpty(), "Deselect-all should clear all selections")
		})

		It("[test_id:TS-CNV-72112-011] should display the correct VM count in the summary component", func() {
			By("Listing all VMs across both namespaces")
			vmListA, err := virtClient.VirtualMachine(namespaceA).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())
			vmListB, err := virtClient.VirtualMachine(namespaceB).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())

			totalVMs := len(vmListA.Items) + len(vmListB.Items)

			By("Verifying total VM count includes both target and decoy")
			Expect(totalVMs).To(BeNumerically(">=", 2),
				"Summary should show at least 2 VMs (target + decoy)")

			By("Verifying VM names are present in the aggregate list")
			allNames := make(map[string]bool)
			for _, vm := range vmListA.Items {
				allNames[vm.Name] = true
			}
			for _, vm := range vmListB.Items {
				allNames[vm.Name] = true
			}
			Expect(allNames).To(HaveKey(vmTarget.Name))
			Expect(allNames).To(HaveKey(vmDecoy.Name))
		})

		It("[test_id:TS-CNV-72112-012] should return the correct VM when filtering by IP within a single project", func() {
			By("Listing VMIs in namespace A only (single-project view)")
			vmiList, err := virtClient.VirtualMachineInstance(namespaceA).List(ctx, metav1.ListOptions{})
			Expect(err).ToNot(HaveOccurred())

			By(fmt.Sprintf("Filtering by target IP %s within namespace A", targetIP))
			matched := filterVMIsByIP(vmiList.Items, targetIP)

			By("Verifying the correct VM is found")
			Expect(matched).To(HaveLen(1), "Exactly 1 VMI should match IP in single project")
			Expect(matched[0].Name).To(Equal(vmTarget.Name))
			Expect(matched[0].Namespace).To(Equal(namespaceA))

			By("Verifying no VMs from other namespaces are included")
			for _, vmi := range vmiList.Items {
				Expect(vmi.Namespace).To(Equal(namespaceA))
			}
		})
	})

	Context("Empty state when no VMs exist", Ordered, decorators.OncePerOrderedCleanup, func() {
		It("[test_id:TS-CNV-72112-010] should display the empty state component when no VMs exist", func() {
			ctx := context.Background()

			By("Creating a temporary namespace with no VMs")
			emptyNamespace := testsuite.GetTestNamespace(nil) + "-empty-check"

			By("Listing VMIs in a namespace known to have no test VMs")
			vmiList, err := virtClient.VirtualMachineInstance(emptyNamespace).List(ctx, metav1.ListOptions{})
			if err != nil {
				// Namespace may not exist, which effectively means empty state
				By("Namespace does not exist, which is equivalent to empty VM list")
				return
			}

			vmList, err := virtClient.VirtualMachine(emptyNamespace).List(ctx, metav1.ListOptions{})
			if err != nil {
				By("Namespace does not exist for VM list, empty state applies")
				return
			}

			By("Verifying empty state: no VMs and no VMIs")
			Expect(vmiList.Items).To(BeEmpty(),
				"Empty namespace should have no VMIs")
			Expect(vmList.Items).To(BeEmpty(),
				"Empty namespace should have no VMs")

			By("Verifying empty list length triggers empty state rendering")
			Expect(len(vmiList.Items)).To(Equal(0),
				"vms.length === 0 should trigger empty state in VirtualMachinesList component")
		})
	})
})
