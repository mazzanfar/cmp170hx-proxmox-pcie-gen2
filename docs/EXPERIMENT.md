# Experiment record

## Observed sequence

1. With the GPU assigned to VFIO, the guest initialized the 64 GiB memory unlock successfully.
2. Earlier changes advertised Gen2 capability and set the target to Gen2, while the physical link stayed Gen1 ×4. Several later host-side retrains did not change this.
3. Diagnostics showed GSP initialization changed MISC from `e0b42d00` to `e0b40d00` and CFG from `80084c00` to `800c4c00`.
4. The experiment reapplied four register settings at the successful end of `kgspInitRm_IMPL`. Subsequent opt-in readbacks showed those values persisted. Persistence of these values alone did not establish Gen2.
5. A host watcher observed the GPU's physical target-speed field transition from 1 to 2 during guest initialization. The root port was already targeting Gen2.
6. The watcher requested one root-port retrain at that transition. Its next successful poll, approximately 104 ms after the request, observed Gen2 ×4 at both ends. Polling does not measure the exact link-training duration.
7. Three transfer rounds passed; a later full VM stop/start also retained Gen2.

## Sanitized event excerpt

These are transcribed values with device addresses and absolute timestamps omitted, not an unedited raw log.

```text
Before guest initialization:
GPU  CAP=00456102 STA=1041 LC2=0001 gen=1 width=4 training=0
ROOT CAP=037a3903 STA=3041 LC2=0002 gen=1 width=4 training=0

GPU target transition observed: Gen1 -> Gen2
One physical root-port retrain requested
Next successful observation (~104 ms after request):
GPU  CAP=00456102 STA=1042 LC2=0002 gen=2 width=4 training=0
ROOT CAP=037a3903 STA=3042 LC2=0002 gen=2 width=4 training=0
```

The preconfigured root target was part of the successful setup. The successful watcher did not itself write either endpoint's target-speed field.

## Important negative findings

- Gen2 capability and target fields did not prove an active Gen2 link.
- Post-initialization retraining failed in earlier attempts. The timed attempt succeeded; this suggests a timing dependency but does not establish the exact hardware mechanism.
- An attempted write of zero to OPT_GEN23 (`0x82057c`) still read back one; the eventual successful Gen2 run did not require that readback to become zero.
- The diagnostic string `PCIe retrain done` existed even when mid-boot retraining was skipped. We used physical link status and transfer measurements as evidence.
- Builds called “no-Gen2 control” and “prefix17” still contained the same late-write source. They were not clean controls for the absence of every Gen2 modification.
- An earlier candidate caused a hung NVIDIA-SMI and loss of guest SSH access. Recovery required restoring modules/initramfs and stopping/starting the VM.

## Boundaries

This is one card and one platform, not a statistical reliability result. Three final round-trip comparisons validate the transferred buffers, not every individual repeated copy or all 64 GiB of VRAM. Earlier memory-unlock stress tests were run before the final PCIe changes and do not qualify this driver revision for long-term use. No inference speed improvement has been measured after the Gen2 change.

## Using the packaged tools

On the guest, with an existing CUDA-enabled PyTorch environment and inference stopped:

```bash
python3 tools/bandwidth.py
```

On the Proxmox host, first identify your own stopped VM, its GPU PCI address and the GPU's immediate root port. The watcher accepts full domain-qualified PCI addresses and verifies product ID, topology, VFIO binding and VM assignment. Replace each placeholder below; do not copy another machine's addresses.

```bash
python3 tools/edge_watch.py --vmid VM_ID --gpu GPU_BDF --root-port ROOT_PORT_BDF
```

That invocation is read-only and does not start the VM. If its prerequisites pass and you have reviewed the source and recovery plan, adding `--execute` starts the VM and permits at most one timed root-port retrain. It does not install a driver, prepare target-speed registers, stop a VM, or create a persistent service. Resource-mapped or multi-function shorthand assignments are rejected by this version.

If the initial physical link is already Gen2 ×4, it reports that and leaves the VM stopped. An ordinary VM start can then be evaluated separately, as in the reported retention test. Always verify guest driver initialization and physical link status after a start; an early host link observation is not proof that the guest subsequently initialized correctly.
