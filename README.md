# Meowcoin Bootstrap

Skip the slow first sync. Drop this file into your Meowcoin folder and you're caught up in an hour or two instead of a week.

**Covers:** mainnet up to block 1,884,606 (April 22, 2026)

---

## How to use it

1. **Download** `bootstrap.dat.xz` from [Releases](../../releases/latest).

2. **Unzip it.** On Windows, open it with [7-Zip](https://www.7-zip.org/). On Mac/Linux: `xz -d bootstrap.dat.xz`. You'll end up with `bootstrap.dat` (~3 GB).

3. **Close Meowcoin Core** if it's running.

4. **Move `bootstrap.dat`** into your Meowcoin data folder:

   - **Windows:** `%APPDATA%\Meowcoin`
   - **Mac:** `~/Library/Application Support/Meowcoin`
   - **Linux:** `~/.meowcoin`

5. **Open Meowcoin Core.** It finds the file automatically and starts importing. First start will show "Reindexing blocks on disk…" — let it run. Takes 30–90 min.

6. When it's done, **delete `bootstrap.dat`** to free up space. You won't need it again.

That's it.

---

## Want to make sure the file isn't corrupted?

Check the SHA256. `bootstrap.dat.xz.sha256` is next to the file on the Releases page.

- **Windows:** `Get-FileHash bootstrap.dat.xz` in PowerShell
- **Mac/Linux:** `sha256sum -c bootstrap.dat.xz.sha256`

If the hash matches, you're good.

---

## For node operators: making your own

If you run a synced node and want to publish a fresh snapshot:

```
meowcoin-cli stop
python make_bootstrap.py <datadir>/blocks bootstrap.dat
xz -9 -T 0 bootstrap.dat
```

The script handles the XOR-obfuscation that Meowcoin Core 30.x applies to `blk*.dat` files — no RPC needed, just reads disk.

---

MIT licensed. Bootstrap data is public blockchain, share freely.
