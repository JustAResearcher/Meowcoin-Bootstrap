# Meowcoin bootstrap — April 22, 2026

Snapshot of the Meowcoin mainnet chain up to block **1,884,606**. Use this to skip the slow initial sync on a new node.

> ⚠️ **Requires Meowcoin Core v30.2.0 or later (APEX).** The legacy v3.x wallet will not accept these blocks.

## Files

- `bootstrap.dat.xz` — 1.24 GB compressed (3 GB uncompressed)
- `bootstrap.dat.xz.sha256` — checksum

## Use it

1. Download and unzip `bootstrap.dat.xz`.
2. Close Meowcoin Core.
3. Move `bootstrap.dat` into your Meowcoin folder (`%APPDATA%\Meowcoin` on Windows, `~/.meowcoin` on Linux, `~/Library/Application Support/Meowcoin` on Mac).
4. Open Meowcoin Core. It imports automatically.
5. When done, delete the file.

Full instructions in the [README](https://github.com/JustAResearcher/Meowcoin-Bootstrap#readme).
