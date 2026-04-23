#!/usr/bin/env python3
"""
Verify a Meowcoin bootstrap.dat by walking its block framing.

Checks that every frame begins with the mainnet magic bytes `MEWC`
(0x4d455743), that sizes are sane, and that the file has no trailing
garbage. Does NOT validate proof-of-work — that is meowcoind's job when
it imports the file.

Usage:
    python verify_bootstrap.py <path/to/bootstrap.dat>
"""
import os
import struct
import sys
import time

MAGIC_MAINNET = bytes.fromhex("4d455743")  # "MEWC"
MAX_BLOCK_SIZE = 64 * 1024 * 1024  # 64 MiB — Meowcoin APEX allows 16 MB, keep headroom


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    total = os.path.getsize(path)
    print(f"Verifying {path} ({total/1e9:.3f} GB)")

    count = 0
    min_sz = 1 << 30
    max_sz = 0
    sum_sz = 0
    t0 = time.time()
    with open(path, "rb") as f:
        while True:
            pos = f.tell()
            hdr = f.read(8)
            if len(hdr) < 8:
                break
            magic = hdr[:4]
            size = struct.unpack("<I", hdr[4:])[0]
            if magic != MAGIC_MAINNET:
                print(f"ERROR: bad magic {magic.hex()} at offset {pos}")
                sys.exit(1)
            if size == 0 or size > MAX_BLOCK_SIZE:
                print(f"ERROR: implausible block size {size} at offset {pos}")
                sys.exit(1)
            f.seek(size, 1)
            count += 1
            min_sz = min(min_sz, size)
            max_sz = max(max_sz, size)
            sum_sz += size
            if count % 100000 == 0:
                pct = pos * 100 / total
                print(f"  ... {count} blocks, {pct:.1f}%")
        end_off = f.tell()

    elapsed = time.time() - t0
    print(f"\nOK: {count} blocks verified in {elapsed:.1f}s")
    print(f"  min block: {min_sz} B")
    print(f"  max block: {max_sz} B  ({max_sz/1024/1024:.2f} MiB)")
    print(f"  avg block: {sum_sz//count} B")
    if end_off != total:
        tail = total - end_off
        print(f"WARN: {tail} trailing bytes beyond last block")
        sys.exit(1)


if __name__ == "__main__":
    main()
