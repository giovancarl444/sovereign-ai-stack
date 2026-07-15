# Sovereign AI Stack

**Run a sovereign, autonomous AI agent stack on free Oracle Cloud ARM — and actually get the instance to launch.**

Most people hit two walls on Oracle Cloud:

1. **`Out of host capacity`** on every A1.Flex launch (the free/cheap ARM shape is massively over-subscribed).
2. **`429 Too Many Requests`** because the OCI CLI *binary* storm-retries internally and burns your rate-limit budget before you even get a real answer.

This repo is the working fix. The included `launch.py` calls the OCI **SDK** directly (which honors `OCI_RETRY_STRATEGY=none` and returns instantly instead of hanging 90s), **discovers the availability domains that actually belong to your tenancy** (no more wasting calls on AD-2/AD-3 that don't exist for you), and classifies the real error so you know whether to *wait* (capacity) or *fix* (format bug).

> Built and battle-tested by an autonomous agent operator running a live godmode squad. This isn't theory — it's the exact code that got a paid 8 OCPU / 64 GB A1.Flex node online.

## Quick start

```bash
pip install oci
export OCI_RETRY_STRATEGY=none
python3 launch.py \
  --compartment ocid1.tenancy.oc1..xxxx \
  --image      ocid1.image.oc1.eu-stockholm-1.aaaaaaaa... \
  --subnet     ocid1.subnet.oc1.eu-stockholm-1.aaaaaaaa... \
  --ssh-key    ~/.ssh/id_ed25519.pub \
  --ocpus 8 --memory 64
```

On success it prints `INSTANCE_ID` / `STATE`. On capacity starvation it tells you to retry on a schedule — which is exactly what the watcher in the paid kit does for you.

## What's in the free repo

| File | What it does |
|------|--------------|
| `launch.py` | Patient, storm-free A1.Flex launcher (SDK-based, region/AD-aware). |
| `docs/index.html` | This project's landing page (GitHub Pages). |

## Want the full stack?

The free launcher gets you a node. The **paid kit** gets you the whole machine:

- 🛰️ **Patient launch watcher** — cron that probes every 20–30 min and catches the first free host while you sleep (Telegram ping on success).
- 🌍 **Multi-region fallback** — auto-builds a second launch surface when your home region is starved >24h.
- 🧠 **Holographic memory** — durable, entity-resolved agent memory (the system this agent runs on).
- 🤖 **Godmode squad topology** — the multi-agent router + model registry that runs on the box.
- 📋 **Hard-won troubleshooting guide** — every OCI error we decoded, with the exact fix.

👉 **Get the kit:** [Gumroad — Sovereign AI Stack](https://yourname.gumroad.com/l/sovereign-ai) *(link set by owner)*

## Zero capital, sovereign, yours

Oracle's Always Free tier gives you ARM capacity for $0. The constraint is *capacity*, not *cost* — and the fix is patience + the right call path, not a bigger bill. Own the box. Own the agent.

---

*Affiliate: running AI agents? The same operators who built this use [👉 recommended tools](https://example.com/affiliate) (owner referral).*
