#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""256 MiB pinned-buffer transfers; three final round-trip comparisons."""
import statistics
import subprocess
import time
import torch

SIZE = 256 * 1024 * 1024
COPIES = 32
ROUNDS = 3


def telemetry():
    print(subprocess.run(['nvidia-smi', '-i', '0',
        '--query-gpu=pcie.link.gen.current,pcie.link.width.current,temperature.gpu,temperature.memory,power.limit',
        '--format=csv'], capture_output=True, text=True, check=True,
        timeout=10).stdout.strip(), flush=True)


def measure(destination, source):
    for _ in range(2):
        destination.copy_(source, non_blocking=True)
    torch.cuda.synchronize()
    begin = time.perf_counter()
    for _ in range(COPIES):
        destination.copy_(source, non_blocking=True)
    torch.cuda.synchronize()
    return SIZE * COPIES / (time.perf_counter() - begin) / 1e9


def main():
    torch.set_num_threads(4)
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA unavailable')
    telemetry()
    host = torch.empty(SIZE, dtype=torch.uint8, pin_memory=True)
    returned = torch.empty_like(host, pin_memory=True)
    device = torch.empty(SIZE, dtype=torch.uint8, device='cuda:0')
    h2d, d2h = [], []
    for round_number in range(1, ROUNDS + 1):
        host.random_(0, 256)
        returned.zero_()
        h2d.append(measure(device, host))
        d2h.append(measure(returned, device))
        if not torch.equal(host, returned):
            raise RuntimeError(f'Data mismatch in round {round_number}')
        print(f'Round {round_number}: H2D {h2d[-1]:.3f}; D2H {d2h[-1]:.3f} GB/s; data PASS', flush=True)
        telemetry()
    print(f'Medians: H2D {statistics.median(h2d):.3f}; D2H {statistics.median(d2h):.3f} GB/s')
    print('PASS: all three final round-trip comparisons')


if __name__ == '__main__':
    main()
