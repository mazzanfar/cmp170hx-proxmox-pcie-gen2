# CMP 170HX: Gen2 ×4 timing experiment under Proxmox

A single CMP 170HX passed through to a Linux guest negotiated PCIe Gen2 ×4 when **one host root-port retrain was timed to the physical GPU Target Link Speed transition from Gen1 to Gen2 during guest driver initialization**.

Measured median host-to-device bandwidth increased from **0.816 to 1.628 GB/s** and device-to-host from **0.839 to 1.673 GB/s** (decimal units). Three round-trip data comparisons passed. Both physical link endpoints reported 5 GT/s ×4. This is a community experiment, not a vendor-supported fix or a production-ready boot service.

## Tested configuration

| Component | Configuration |
|---|---|
| Server | Dell PowerEdge R730, dual Xeon E5-2695 v4 |
| Host | Proxmox VE 9.1.1; Linux 6.17.2-1-pve |
| Guest | Ubuntu 24.04.4; Linux 6.8.0-142-generic; Q35/SeaBIOS |
| GPU | NVIDIA CMP 170HX, generic PCI device ID `10de:20c2` |
| GPU memory | 8 GiB SKU, software-unlocked to 65,536 MiB |
| Physical link | Four lanes; no modification to enable sixteen lanes |
| Guest driver | NVIDIA open kernel modules 610.43.03, modified |
| Power limit | 150 W |
| Benchmark | PyTorch 2.7.1+cu128; pinned CPU buffers |

Device ID `10de:20c2` identifies a product type, not a particular card. No serial numbers, GPU UUIDs, real PCI addresses, network addresses or hostnames are included.

## Results

| Round | Host → GPU (GB/s) | GPU → host (GB/s) | Data comparison |
|---|---:|---:|---|
| 1 | 1.629 | 1.674 | PASS |
| 2 | 1.628 | 1.672 | PASS |
| 3 | 1.628 | 1.673 | PASS |
| Median | 1.628 | 1.673 | Three passes |

The earlier Gen1 baseline was 0.816 / 0.839 GB/s. Treat the comparison as approximately 2×, not a precision benchmark across controlled repeated sessions. This does not establish a 2× improvement in model inference.

The guest reported 65,536 MiB and a 150 W cap with successful NVIDIA-SMI queries. Filtered guest/host logs showed no matching Xid, GPU-loss, initialization-failure, AER or DPC errors during the reported checks. That is narrower than proving absence of all errors.

A subsequent **full VM stop/start** retained Gen2 ×4 without another retrain. A VM stop/start is not a physical GPU power cycle. Host reboot, AC power cycle and repeated recovery from a fresh Gen1 state remain unvalidated.

## Contents

- [Experiment and negative results](docs/EXPERIMENT.md)
- [Source provenance and patch preparation](docs/SOURCE.md)
- [Recovery and operational limits](docs/RECOVERY.md)
- [Sanitized evidence](evidence/results.json)
- [Transfer benchmark](tools/bandwidth.py)
- [One-shot host watcher](tools/edge_watch.py): adapted helper, simulated locally; this exact packaged revision has not been run on hardware.
- [Publication/privacy checklist](docs/PUBLICATION.md)

The guest patch is extracted from the supplied tested source snapshots. The host helper is reconstructed and generalized from the successful manual experiment. Neither component is an unattended installer. Read the source and recovery notes before reproducing the experiment.

## Attribution

The memory unlock and most PCIe register programming come from [amoghmunikote/cmpunlocker](https://github.com/amoghmunikote/cmpunlocker), pinned here to `6c442eeb6448b97c803e72b61da344a39e0a26ab`, on [NVIDIA open-gpu-kernel-modules 610.43.03](https://github.com/NVIDIA/open-gpu-kernel-modules/tree/610.43.03). This repository documents local adaptations and measurements; it does not claim authorship of the original unlock.

Related community reports: [cmpunlocker PR #35](https://github.com/amoghmunikote/cmpunlocker/pull/35), [cmp170hx-gen2](https://github.com/luannanxian/cmp170hx-gen2), and [Proxmox dual-GPU passthrough](https://github.com/anoane/01-proxmox-dual-gpu-passthrough). These are leads for comparison, not independently reproduced results on this system.

Repository contributions are distributed under GPL-2.0-only. Upstream NVIDIA material retains its original notices and licensing; see [NOTICE](NOTICE).
