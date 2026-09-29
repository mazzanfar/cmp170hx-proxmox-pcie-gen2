# Recovery and operating limits

Before installing an experimental driver, save the working module directory, initramfs for the exact guest kernel, modprobe configuration and checksums outside the candidate source tree. Verify that you can reach the guest through the hypervisor console. Keep the original working driver as the rollback target; an older experimental directory is not automatically a clean control.

Keep inference stopped during link experiments. The host watcher touches the physical root port of one passed-through GPU. Check the physical topology yourself; never substitute a guessed address. No repeated retrain loop, hot-remove, bus reset or persistent Proxmox hook is included.

If the guest stops responding, use the hypervisor console. If necessary, stop the guest and temporarily detach GPU passthrough to boot and restore the backed-up modules and initramfs. Restore the exact previous configuration before attaching the card again. A VM restart may not reset every GPU state; a physical power cycle is a separate operation affecting the host and other guests.

For a failed watcher, read the output and current link state rather than running it repeatedly. It leaves the VM in its current state. A timeout is not a request to issue another retrain. Restore original root-port target settings only from a recorded original value and a separately reviewed procedure.

The packaged watcher refuses to prepare a root target. Its successful historical prerequisite was a root port already targeting Gen2, with GPU Gen1 ×4 and target Gen1 before VM start. Initial Gen2 retention is reported without changing the link. This does not qualify cold host boot or unattended operation.
