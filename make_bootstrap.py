#!/usr/bin/env python3
"""
Generate Meowcoin bootstrap.dat from a fully-synced node's blk*.dat files.

Reads the XOR-obfuscation key from <datadir>/blocks/xor.dat, de-obfuscates
each blk*.dat, and concatenates the result into bootstrap.dat. Because each
block in a blk file is already framed with [magic 4B][size 4B LE][payload],
the concatenated de-XORed stream IS a valid bootstrap.dat.

Orphan/reorged blocks are passed through; meowcoind's -loadblock ignores them.

Usage:
    python make_bootstrap.py <blocks_dir> <output_path>
"""
import os
import sys
import struct
import time

MAGIC_MAINNET = bytes.fromhex("4d455743")  # "MEWC"
CHUNK = 8 * 1024 * 1024  # 8 MiB


def xor_stream(src, dst, key):
    klen = len(key)
    offset = 0
    while True:
        buf = src.read(CHUNK)
        if not buf:
            break
        out = bytearray(len(buf))
        for i, b in enumerate(buf):
            out[i] = b ^ key[(offset + i) % klen]
        dst.write(out)
        offset += len(buf)
    return offset


def scan_blocks(path, expected_magic):
    """Walk bootstrap.dat counting framed blocks. Returns (count, end_offset_of_last_valid).

    Tolerates zero padding (pre-allocated but unused space at end of hot blk
    file) and stops at the first bad magic after the last valid block. This
    end_offset is safe to truncate to.
    """
    count = 0
    last_valid_end = 0
    with open(path, "rb") as f:
        while True:
            pos = f.tell()
            hdr = f.read(8)
            if len(hdr) < 8:
                break
            magic = hdr[:4]
            size = struct.unpack("<I", hdr[4:])[0]
            if magic == expected_magic:
                f.seek(size, 1)
                count += 1
                last_valid_end = f.tell()
                continue
            if magic == b"\x00\x00\x00\x00":
                # Zero padding — skip ahead to next non-zero byte or EOF.
                remaining = f.read()
                nz = next((i for i, b in enumerate(remaining) if b != 0), -1)
                if nz < 0:
                    break
                f.seek(pos + nz)
                continue
            # Garbage (e.g., preallocated-but-uninitialized region in the
            # currently-open blk file). Stop here — output is valid up to
            # last_valid_end.
            break
    return count, last_valid_end


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)

    blocks_dir = sys.argv[1]
    out_path = sys.argv[2]

    xor_path = os.path.join(blocks_dir, "xor.dat")
    with open(xor_path, "rb") as f:
        key = f.read()
    print(f"XOR key ({len(key)}B): {key.hex()}")

    blk_files = sorted(
        fn for fn in os.listdir(blocks_dir)
        if fn.startswith("blk") and fn.endswith(".dat")
    )
    if not blk_files:
        print("No blk*.dat files found.", file=sys.stderr)
        sys.exit(1)
    print(f"Found {len(blk_files)} blk files")

    total_in = 0
    t0 = time.time()
    with open(out_path, "wb") as dst:
        for fn in blk_files:
            path = os.path.join(blocks_dir, fn)
            sz = os.path.getsize(path)
            with open(path, "rb") as src:
                written = xor_stream(src, dst, key)
            total_in += sz
            elapsed = time.time() - t0
            rate = total_in / elapsed / (1024 * 1024) if elapsed else 0
            print(f"  {fn}: {sz/1e6:8.1f} MB  (cum {total_in/1e9:.2f} GB, {rate:.1f} MB/s)")

    out_size = os.path.getsize(out_path)
    print(f"\nWrote {out_path}: {out_size/1e9:.3f} GB")

    print("\nScanning output to verify block framing...")
    t0 = time.time()
    count, end_off = scan_blocks(out_path, MAGIC_MAINNET)
    print(f"Verified {count} framed blocks in {time.time()-t0:.1f}s")

    if end_off < out_size:
        trim = out_size - end_off
        print(f"Trimming {trim} trailing bytes (preallocated/unused space)")
        with open(out_path, "r+b") as f:
            f.truncate(end_off)
        print(f"Final size: {end_off/1e9:.3f} GB")


if __name__ == "__main__":
    main()
