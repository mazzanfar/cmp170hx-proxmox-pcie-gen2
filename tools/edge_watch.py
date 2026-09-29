#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One-shot experimental retrain. Read-only preflight unless --execute is given."""
import argparse
import os
from pathlib import Path
import re
import struct
import subprocess
import time


def run(args, timeout=10):
    return subprocess.run(args, check=True, capture_output=True, text=True,
                          timeout=timeout).stdout.strip()


def decision(previous_target, gpu, root):
    """Pure transition decision, covered by offline tests."""
    for s in (gpu, root):
        if s['width'] != 4 or s['gen'] not in (1, 2):
            raise RuntimeError('Unexpected link generation/width; no retrain')
    if gpu['training'] or root['training']:
        return 'wait'
    if gpu['gen'] == root['gen'] == 2:
        return 'already-gen2'
    if previous_target == 1 and gpu['target'] == 2:
        if root['target'] != 2 or gpu['gen'] != root['gen']:
            raise RuntimeError('Inconsistent link state at transition; no retrain')
        return 'retrain'
    return 'wait'


class Device:
    def __init__(self, address):
        if not re.fullmatch(r'[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-1][0-9a-fA-F]\.[0-7]', address):
            raise ValueError('Use a full PCI address discovered on YOUR host')
        self.address = address.lower()
        self.path = Path('/sys/bus/pci/devices') / self.address
        self.fd = os.open(self.path / 'config', os.O_RDONLY)
        pointer = self.read(0x34, 1)
        seen = set()
        while pointer and pointer not in seen:
            if pointer < 0x40 or pointer > 0xfc or pointer % 4:
                break
            seen.add(pointer)
            if self.read(pointer, 1) == 0x10:
                self.cap = pointer
                return
            pointer = self.read(pointer + 1, 1)
        raise RuntimeError('PCI Express capability missing or malformed')

    def read(self, offset, size):
        data = os.pread(self.fd, size, offset)
        if len(data) != size or data == b'\xff' * size:
            raise RuntimeError('PCI configuration read failed')
        return int.from_bytes(data, 'little')

    def snapshot(self):
        sta = self.read(self.cap + 0x12, 2)
        return dict(gen=sta & 15, width=(sta >> 4) & 63,
                    training=bool(sta & 0x0800),
                    target=self.read(self.cap + 0x30, 2) & 15)


def topology(gpu, root):
    if gpu.path.resolve().parent != root.path.resolve():
        raise RuntimeError('Specified root port is not the immediate physical parent')
    if (gpu.path / 'vendor').read_text().strip() != '0x10de' or (gpu.path / 'device').read_text().strip() != '0x20c2':
        raise RuntimeError('This experiment is restricted to product 10de:20c2')
    if (gpu.path / 'driver').resolve().name != 'vfio-pci':
        raise RuntimeError('GPU must already be bound to vfio-pci')
    if ((root.read(root.cap + 2, 2) >> 4) & 15) != 4:
        raise RuntimeError('Parent is not a PCIe root port')
    if any((d.read(d.cap + 0x0c, 4) & 15) < 2 for d in (gpu, root)):
        raise RuntimeError('Both endpoints must advertise at least Gen2')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vmid', type=int, required=True)
    p.add_argument('--gpu', required=True)
    p.add_argument('--root-port', required=True)
    p.add_argument('--execute', action='store_true', help='Start stopped VM and permit at most ONE retrain')
    args = p.parse_args()
    if args.vmid <= 0:
        p.error('VM ID must be positive')
    gpu, root = Device(args.gpu), Device(args.root_port)
    topology(gpu, root)
    vm = str(args.vmid)
    if run(['qm', 'status', vm]) != 'status: stopped':
        raise RuntimeError('VM must be stopped before arming')
    # Verify this VM configuration actually assigns this GPU.
    config = run(['qm', 'config', vm])
    assignment = False
    for line in config.splitlines():
        if line.startswith('hostpci') and ':' in line:
            value = line.split(':', 1)[1].strip().split(',', 1)[0]
            if value in (gpu.address, gpu.address[5:]):
                assignment = True
    if not assignment:
        raise RuntimeError('VM GPU assignment not verified; resource mappings are not supported')
    g, r = gpu.snapshot(), root.snapshot()
    print('Physical baseline:', g, r, flush=True)
    state = decision(1, g, r)
    if state == 'already-gen2':
        print('Link already Gen2 x4. Nothing changed; VM remains stopped.')
        return
    if any(s['gen'] != 1 or s['training'] for s in (g, r)) or g['target'] != 1 or r['target'] != 2:
        raise RuntimeError('Expected settled Gen1 x4, GPU target 1, root target 2; nothing changed')
    if not args.execute:
        print('Preflight passed. No writes or VM start performed. Review source before --execute.')
        return
    start = subprocess.Popen(['qm', 'start', vm])
    deadline = time.monotonic() + 180
    previous_target = g['target']
    try:
        while time.monotonic() < deadline:
            if start.poll() not in (None, 0):
                raise RuntimeError('VM start failed; no retrain')
            g, r = gpu.snapshot(), root.snapshot()
            state = decision(previous_target, g, r)
            if state == 'already-gen2':
                print('Gen2 x4 already observed. No retrain issued.')
                return
            if state == 'retrain':
                topology(gpu, root)
                # No retries: an ambiguous command failure ends the experiment.
                print('Target transition observed. Requesting ONE root-port retrain.', flush=True)
                run(['setpci', '-s', root.address, 'CAP_EXP+10.w=0020:0020'], timeout=3)
                for _ in range(30):
                    time.sleep(0.1)
                    g, r = gpu.snapshot(), root.snapshot()
                    if all(s['gen'] == 2 and s['width'] == 4 and not s['training'] for s in (g, r)):
                        print('Gen2 x4 observed at both endpoints:', g, r)
                        print('Now check guest initialization, bandwidth/data and both kernel logs.')
                        return
                raise RuntimeError('One retrain attempted; Gen2 not verified. Do not automatically retry.')
            previous_target = g['target']
            time.sleep(0.005)
        raise RuntimeError('Target transition not observed before timeout. No retrain issued.')
    finally:
        print('VM left in its current state; this helper does not stop it.', flush=True)


if __name__ == '__main__':
    main()
