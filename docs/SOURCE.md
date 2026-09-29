# Source provenance and preparation

The supplied patch is a delta against NVIDIA 610.43.03 after applying these cmpunlocker patches from commit `6c442eeb6448b97c803e72b61da344a39e0a26ab`, in order:

1. sec2-postbl-plm-ss-cfg.patch
2. booter-verify.patch
3. late-pma.patch
4. bar0-pramin-clamp.patch
5. ce-scrub-workarounds.patch
6. persistent-sw-state.patch
7. pcie-gen2.patch

Do **not** also apply `pcie-gen2-probe-retrain.patch`, `name-string.patch`, `bar1-resize-unlock.patch` or `cmp-sku-mask.patch` for this reconstruction. The upstream installer applies a broader set; do not use it blindly for this experiment.

Apply the seven upstream patches using their original `patch -p1` workflow in a fresh source tree, then apply `patches/0001-guest-init-timing.patch`. The upstream pcie-gen2 patch required fuzz 1 and a line offset on the GSP source during local reconstruction. The follow-up patch was checked with strict `git apply --check`, then the resulting two files were hash-compared with the supplied tested snapshots.

The patch includes the payload-size guard, omission of the `FEAT_OVR_ECC_PLM` write at `0x823800`, removal of the SM-reconfiguration block, diagnostic snapshots, and relocation of four late writes to the successful end of GSP initialization. The field semantics and minimal necessary subset have not been independently established.

Expected patched files:

```text
e209352a4830511c2a7fe4604ecddac2792b731d7fd17d2ada45d1b07d7d4576  src/nvidia/src/kernel/gpu/gsp/kernel_gsp.c
5033864e259e82f6778d04e25eaf0e986a12bd599a0ea3375227cfc5a6715037  src/nvidia/src/kernel/gpu/gsp/arch/turing/kernel_gsp_tu102.c
```

These are source hashes, not installed-binary hashes. No module binaries are supplied.

The final tested build also included an opt-in, default-off `cmp_gen2_readback` diagnostic in `nv.c`, logging register reads on successful device opens. That diagnostic is not included in this package. Accordingly this is a source reconstruction of the functional changes, not a byte-for-byte reconstruction of the final installed build. Original tested `nv.c` before that diagnostic had SHA256 `735bf7a12c222cf1a1940bceed777c22adbaab9b04cd973ef99154d4fe5d4dff`.

Build against your guest's exact kernel headers and matching NVIDIA userspace version. Compilation does not validate runtime behavior. This package deliberately has no privileged driver-installation script; preserve your existing working modules and initramfs before any installation. See RECOVERY.md.
