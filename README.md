# Meowcoin Bootstrap

A block-data snapshot that lets a fresh Meowcoin node skip most of the peer-to-peer download and sync the chain in a fraction of the time.

- **Chain:** Meowcoin mainnet
- **Height covered:** 1,884,606 (plus ~32 orphan-chain blocks — ignored on import)
- **Snapshot date:** 2026-04-22
- **File:** `bootstrap.dat` — 2.996 GB uncompressed, ~2 GB compressed (`bootstrap.dat.xz`)
- **Node version tested:** Meowcoin Core 30.2.0

The bootstrap is a plain concatenation of framed blocks (`[magic 4B][size 4B LE][block]...`). Any Meowcoin Core build can import it with `-loadblock`.

> Downloads are published as assets on the GitHub **Releases** page of this repo — not inside the repo tree (they are too large for git).

---

## Quick start — use the bootstrap

1. **Download** the latest `bootstrap.dat.xz` and `bootstrap.dat.xz.sha256` from [Releases](../../releases).

2. **Verify** the checksum:
   ```bash
   sha256sum -c bootstrap.dat.xz.sha256
   ```
   (Windows PowerShell: `Get-FileHash bootstrap.dat.xz -Algorithm SHA256`, compare to the `.sha256` file.)

3. **Decompress**:
   ```bash
   xz -dk bootstrap.dat.xz          # keeps the .xz too
   # or, if you want to save disk:
   xz -d  bootstrap.dat.xz
   ```
   On Windows, [7-Zip](https://www.7-zip.org/) opens `.xz` files too.

4. **Place** `bootstrap.dat` in your Meowcoin datadir, alongside `meowcoin.conf`:

   | Platform | Default datadir |
   |----------|-----------------|
   | Windows  | `%APPDATA%\Meowcoin\` |
   | Linux    | `~/.meowcoin/` |
   | macOS    | `~/Library/Application Support/Meowcoin/` |

5. **Stop** Meowcoin Core if it's running.

6. **Start** the node pointing it at the bootstrap:
   ```bash
   meowcoind -loadblock=/path/to/bootstrap.dat
   # or:
   meowcoin-qt -loadblock=C:\Users\you\AppData\Roaming\Meowcoin\bootstrap.dat
   ```

   The node reads the bootstrap, validates each block, writes them into its own `blocks/` and `chainstate/`, and then connects to peers to sync the remaining tip. Depending on your CPU/disk the bootstrap import takes 30–90 minutes on commodity hardware.

7. **(Optional) Delete `bootstrap.dat`** once the node has caught up — it is not used again.

### Gotchas

- **Do not delete the existing `blocks/` and `chainstate/` folders yourself.** The node will reuse them if they are already partially populated. If you want a truly fresh import, move your datadir aside first, then point a new datadir at the bootstrap.
- **Pruned nodes:** `-loadblock` still works with `prune=<N>` — the node imports, validates, and discards old blocks as it goes.
- **Assets must be enabled** (they are by default on mainnet). Asset-aware validation runs automatically during import.
- Import is **CPU-bound** (signature + PoW checks). An NVMe disk and all CPU cores help.

---

## Verify the bootstrap before importing

Optional but recommended. The verifier walks the block framing and confirms every frame is well-formed. It does not re-check proof-of-work — meowcoind does that during `-loadblock`.

```bash
python verify_bootstrap.py /path/to/bootstrap.dat
```

Expected output:
```
OK: 1884638 blocks verified in ~6s
  min block: 244 B
  max block: 1997720 B  (1.91 MiB)
  avg block: 1581 B
```

---

## Generate your own bootstrap from a synced node

If you run a fully-synced Meowcoin node and want to publish your own bootstrap (or just regenerate one for your private use), use `make_bootstrap.py`.

```bash
# stop the daemon first — blk*.dat must not be open for writing
meowcoin-cli stop

# generate
python make_bootstrap.py \
    ~/.meowcoin/blocks \
    ~/bootstrap.dat

# compress (level 6 is a good size/speed trade; -9 -e for maximum ratio)
xz -6 -T 0 bootstrap.dat
sha256sum bootstrap.dat.xz > bootstrap.dat.xz.sha256
```

### How it works

Meowcoin Core 30.x writes its raw block files (`blk*.dat`) XOR-obfuscated on disk — the 8-byte key is stored in `blocks/xor.dat`. The on-disk layout is otherwise identical to the bootstrap.dat format (`[magic][size][block]`).

`make_bootstrap.py`:
1. Reads the XOR key from `blocks/xor.dat`.
2. Reads each `blk*.dat` in order, XORs each byte with `key[file_offset % 8]` to recover plaintext.
3. Concatenates the de-obfuscated streams into `bootstrap.dat`.
4. Truncates trailing preallocated-but-unused space in the hot blk file.
5. Re-scans the output to verify every block is framed correctly.

No RPC calls are needed — the script works purely on files. Stopping the daemon first avoids reading a half-written `blk` file.

### Orphan blocks

`blk*.dat` contains every block the node ever received, including a small number that later got reorged out of the best chain. `make_bootstrap.py` preserves them. `meowcoind -loadblock` accepts orphans without complaint — they simply fail the "extends best chain" check and are skipped. The valid blocks still get imported.

---

## Files in this repo

| File | Purpose |
|------|---------|
| `README.md`          | You are here |
| `make_bootstrap.py`  | Generate `bootstrap.dat` from a synced node's `blocks/` directory |
| `verify_bootstrap.py`| Walk `bootstrap.dat` and confirm every block frame is well-formed |
| `LICENSE`            | MIT |

The compressed `bootstrap.dat.xz` itself and its `.sha256` live on the [Releases](../../releases) page.

---

## License

MIT. See [LICENSE](LICENSE).

The bootstrap.dat file is public blockchain data, freely redistributable.
