#!/usr/bin/env python3
"""
sovereign-ai-stack :: inbound_tracker.py
Dead-simple inbound tracker. No external service. Counts clicks/signals via a
local JSONL log and prints a real dashboard. Wire the landing-page CTA to hit
the /track endpoint (or just have MIDAS log manually when Elliot reports inbound).

This is the zero-capital version: a local log + a daily digest. When volume
warrants, swap the storage for Airtable/Sheets (skill exists) without changing
the report shape.

CLI:
  python3 inbound_tracker.py log --source github --note "star"
  python3 inbound_tracker.py log --source gumroad --note "sale:$29"
  python3 inbound_tracker.py log --source x --note "@user DM'd"
  python3 inbound_tracker.py report
"""
import json, os, sys, datetime

LOG = os.path.join(os.path.dirname(__file__), "inbound.jsonl")

def log(source, note=""):
    rec = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
           "source": source, "note": note}
    with open(LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print("logged:", rec)

def report():
    if not os.path.exists(LOG):
        print("No inbound yet.")
        return
    rows = [json.loads(l) for l in open(LOG) if l.strip()]
    by_src = {}
    revenue = 0.0
    for r in rows:
        by_src[r["source"]] = by_src.get(r["source"], 0) + 1
        if r["source"] == "gumroad":
            import re
            m = re.search(r"\$?([0-9]+(?:\.[0-9]+)?)", r.get("note", ""))
            if m:
                revenue += float(m.group(1))
    print("=== SOVEREIGN AI STACK — INBOUND DASHBOARD ===")
    print(f"Total signals : {len(rows)}")
    print(f"Est. revenue  : ${revenue:.2f}")
    print("By source:")
    for k, v in sorted(by_src.items(), key=lambda x: -x[1]):
        print(f"  {k:10} {v}")
    print("\nRecent:")
    for r in rows[-8:]:
        print(f"  {r['ts']}  {r['source']:8}  {r['note']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: inbound_tracker.py [log --source X --note Y | report]")
        sys.exit(1)
    if sys.argv[1] == "log":
        src = ""
        note = ""
        for i, a in enumerate(sys.argv[2:]):
            if a == "--source": src = sys.argv[2:][i+1]
            if a == "--note": note = sys.argv[2:][i+1]
        log(src, note)
    elif sys.argv[1] == "report":
        report()
    else:
        print("unknown command:", sys.argv[1]); sys.exit(1)
