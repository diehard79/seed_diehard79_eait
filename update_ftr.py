"""Fetch the eAIT forecast and publish fTR to the Pine Seeds repo.

Run from the root of this repo clone:
    set EAIT_API_KEY=...        (never commit the key; this repo is public)
    python update_ftr.py [--prev-date YYYY-MM-DD] [--no-push]

The API is called only if the cached response is not already for the previous
trading date. A CSV row is appended only if target_session is not present.
"""
import argparse, json, os, subprocess, sys, urllib.request
from datetime import date, timedelta
from pathlib import Path

URL = "http://127.0.0.1:8811/v1/forecast/latest"
ROOT = Path(__file__).parent
CACHE = ROOT / ".eait_cache.json"          # git-ignored
CSV = ROOT / "data" / "NIFTY_FTR.csv"


def prev_weekday(d):
    d -= timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def git(*args):
    subprocess.run(["git", "-c", "http.sslBackend=schannel", *args], cwd=ROOT, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prev-date")
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    prev = a.prev_date or prev_weekday(date.today()).isoformat()

    cached = json.loads(CACHE.read_text()) if CACHE.exists() else None
    if cached and cached.get("asof_date") == prev:
        print(f"Cache current (asof {prev}); API not called.")
        data = cached
    else:
        key = os.environ.get("EAIT_API_KEY") or sys.exit("Set EAIT_API_KEY first.")
        req = urllib.request.Request(URL, headers={"X-API-Key": key})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.load(r)
        CACHE.write_text(json.dumps(data))
        print(f"API called; asof_date={data['asof_date']}")
        if data["asof_date"] != prev:
            print(f"WARNING: asof_date {data['asof_date']} != expected {prev}")

    day = data["target_session"].replace("-", "") + "T"
    v = f"{data['ftr']:.2f}"
    lines = CSV.read_text().splitlines() if CSV.exists() else []
    if any(l.startswith(day) for l in lines):
        print(f"{day} already in {CSV.name}; nothing to push.")
        return
    lines.append(f"{day},{v},{v},{v},{v},0")
    CSV.write_text("\n".join(lines) + "\n")
    print(f"Appended {day} fTR={v}")
    if not a.no_push:
        git("add", "data/NIFTY_FTR.csv")
        git("commit", "-m", f"fTR {data['target_session']}")
        git("push", "origin", "main")


if __name__ == "__main__":
    main()
