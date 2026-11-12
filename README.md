# eAIT TradingView Bridge (seed_diehard79_eait)

This is a bridge to share data between eAIT and TradingView PineScript.

## Data Files:
1. data/NIFTY_FTR.csv : NIFTY fTR data is in Close (symbol NIFTY_FTR; Pine: `request.seed("seed_diehard79_eait", "NIFTY_FTR", close)`)

## Details:
`seed_crypto_santiment` is someone else's repo, so you can't push to it. `request.seed()` reads from a public GitHub repo that you own and that follows TradingView's Pine Seeds layout. You push your data to that repo, and TradingView picks it up on a schedule. This works from memory of the Pine Seeds docs, so check the field names against the current docs.

**1. Create the repo** on GitHub, public, named `seed_<github_user>_<name>` (for example `seed_sihas_eait`). Use this layout:

```
seed_sihas_eait/
├─ data/EAIT_FTR.csv
└─ symbol_info/seed_sihas_eait.json
```

**2. Add the symbol info** in `symbol_info/seed_sihas_eait.json`:

```json
{
  "symbol": ["EAIT_FTR"],
  "description": ["eAIT fTR forecast"],
  "currency": ["INR"],
  "session-regular": ["0000-2359"],
  "timezone": ["Asia/Kolkata"],
  "pricescale": [100],
  "minmove": [1]
}
```

**3. Format the CSV.** There is no header row, only daily data, and the columns are `date,open,high,low,close,volume`. Put the value you need in `close`, and use `target_session` as the date so the value lines up with the bar it applies to:

```
20261112T,301.67,301.67,301.67,301.67,0
```

**4. Register the repo.** Submit it through TradingView's Pine Seeds form, which is a one-time step. Their bot then pulls updates roughly every 30 minutes.

**5. Read it in Pine**, replacing the manual input:

```pine
float fTR = request.seed("seed_sihas_eait", "EAIT_FTR", close)
```

**6. Update the repo.** Extend `update_ftr.py` to append a row and push. Run it from a clone of the seed repo:

```python
import subprocess, csv
row = [data["target_session"].replace("-", "") + "T", *([data["ftr"]] * 4), 0]
path = "data/EAIT_FTR.csv"
existing = open(path).read() if os.path.exists(path) else ""
if not existing.startswith(row[0]) and row[0] not in existing:
    with open(path, "a", newline="") as f:
        csv.writer(f).writerow(row)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"fTR {data['target_session']}"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
```

The duplicate check keeps your "don't act if already current" logic, so the repo only changes when there is a new session.

**Caveats**
- The repo has to be public, so don't commit your API key. Keep it in an environment variable, as the script does now.
- You can't preview a seed locally. Expect a delay of up to about 30 minutes before the data shows in TradingView.
- If you want other fields such as `fCloseHT` or `H4`, add each as its own symbol and CSV, or pack them into the `open`, `high`, `low` and `close` columns.


Referene:
https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/#requestseed
