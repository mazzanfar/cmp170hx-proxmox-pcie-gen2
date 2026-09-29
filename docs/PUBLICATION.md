# Publication and privacy

Publish this clean directory as a new repository; do not push the experimental workspace or its Git history. Suggested name: `cmp170hx-proxmox-pcie-gen2`.

Included: hardware product models, software versions, generic product PCI ID, source hashes, register values and sanitized measurements. Excluded: real device addresses, serials, GPU UUIDs, service tags, MAC addresses, IP addresses, hostnames, login names, SSH material, tokens, tunnel configuration, raw system dumps and original archive metadata.

Before publishing, inspect `git diff --cached` and `git ls-files`. Use your GitHub-provided no-reply email for commits if you do not want your email public. Posting from your personal account associates the research with that account by design. Publishing sanitized research does not require opening any server ports or granting access to the lab; it cannot guarantee zero security risk.

Suggested repository description:

> Single-system CMP 170HX Gen2 x4 timing experiment under Proxmox: sanitized evidence, source delta, benchmark and guarded one-shot retrain helper.

Suggested first release title: `Experimental Gen2 x4 case study`.

Suggested upstream issue text:

> We observed successful Gen2 x4 on a 20c2 CMP 170HX passed through to an Ubuntu guest on Proxmox. A single host root-port retrain triggered when the GPU's physical target-speed field changed from Gen1 to Gen2 during guest initialization succeeded, whereas earlier post-initialization retrains did not. Measured pinned-memory transfer medians increased from 0.816/0.839 to 1.628/1.673 GB/s, with three round-trip comparisons passing. One later VM stop/start retained Gen2. Host cold boot and repeated fresh Gen1 recovery remain untested. The repository documents the exact source provenance, non-clean controls, failure/recovery history and limits. We would welcome review of the timing mechanism and the minimal required patch set.

Add the repository URL before posting. This issue draft has not been submitted.
