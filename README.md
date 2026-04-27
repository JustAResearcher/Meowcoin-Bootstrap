# Meowcoin Bootstrap

Skip the slow first sync. Drop this file into your Meowcoin folder and you're caught up in an hour or two instead of a week.

**Covers:** mainnet up to block 1,884,606 (April 22, 2026)

Works with **both** Meowcoin Core v3.0.6 (legacy) and v30.2.0+ (APEX).

---

## How to use it

1. **Download** `bootstrap.dat.xz` from [Releases](../../releases/latest).

2. **Unzip it.** On Windows, open it with [7-Zip](https://www.7-zip.org/). On Mac/Linux: `xz -d bootstrap.dat.xz`. You'll end up with `bootstrap.dat` (~3 GB).

3. **Close Meowcoin Core** if it's running. (Important — the file must be in place *before* you start the wallet.)

4. **Move `bootstrap.dat`** into your Meowcoin data folder:

   - **Windows:** `%APPDATA%\Meowcoin`
   - **Mac:** `~/Library/Application Support/Meowcoin`
   - **Linux:** `~/.meowcoin`

5. **Open Meowcoin Core.** It auto-detects the file and imports. Takes 30–90 min.

6. When it's done, the file gets renamed to `bootstrap.dat.old` automatically. Delete it to free up space.

---

## Troubleshooting (it's still syncing from peers!)

If after starting the wallet you see "Syncing Headers… X years behind," the bootstrap wasn't picked up. Check:

- **Did you decompress?** The wallet needs `bootstrap.dat`, not `bootstrap.dat.xz`. Open the .xz and extract.
- **Right folder?** The datadir is *not* the install folder. It's where `meowcoin.conf` and `wallets/` live (paths above).
- **Wallet was already running?** Auto-import only fires at startup. Close the wallet, place the file, then reopen.
- **Already imported?** Look for `bootstrap.dat.old` in the datadir — that means it ran successfully. Your block height should jump to ~1.88 M shortly after.
- **Manual fallback:** start with `meowcoind -loadblock=C:\path\to\bootstrap.dat` (or `meowcoin-qt` with the same flag).

---

## Verify the download (optional)

Match the SHA256 against `bootstrap.dat.xz.sha256` from the same Release.

- Windows: `Get-FileHash bootstrap.dat.xz` in PowerShell
- Mac/Linux: `sha256sum -c bootstrap.dat.xz.sha256`

---

## For node operators: making your own

If you run a fully-synced node and want to publish a fresh snapshot:

```
meowcoin-cli stop
python make_bootstrap.py <datadir>/blocks bootstrap.dat
xz -9 -T 0 bootstrap.dat
```

The script handles the XOR-obfuscation that Meowcoin Core 30.x applies to `blk*.dat`. The output is wire-format blocks — readable by both v3.x and v30.x wallets.

---

MIT licensed. Bootstrap data is public blockchain, share freely.
