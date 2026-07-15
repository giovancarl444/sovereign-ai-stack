# GUMROAD PRODUCT DRAFT — "Sovereign AI Stack" kit
# Elliot creates this on gumroad.com (free account), pastes this copy, sets price,
# then replaces the placeholder link in README.md / docs/index.html / POST_COPY.md.
# DO NOT put secrets here. The kit = files already in this repo's /kit folder + the README list.

## Product title
Sovereign AI Stack — run a self-hosted autonomous agent on free Oracle ARM

## Tagline
The free launcher gets you a node. This kit gets you the whole machine — and it launches itself.

## Price suggestion
$29 one-time (low friction, first blood). Optional $9/mo "Squad OS" tier later for updates + private Discord.

## Description (paste into Gumroad)
You got the free launcher working. Now own the full stack an autonomous agent operator actually runs:

✅ Patient launch watcher — a cron that probes Oracle every 20–30 min and catches the first free A1.Flex host while you sleep. Telegram ping the moment it lands.
✅ Multi-region fallback — auto-builds a second launch surface when your home region is starved >24h, so you're never stuck.
✅ Holographic memory — the durable, entity-resolved agent memory system (the thing this agent runs on). Stop losing context between sessions.
✅ Godmode squad topology — the multi-agent router + model registry that runs on the box. LangGraph + AutoGen + OpenHands wired.
✅ Troubleshooting bible — every OCI error we decoded, with the exact fix. The 429 storm, the ghost ADs, the 401 region lockouts.

Zero capital required. Oracle Always Free ARM. The constraint was never cost — it was capacity and the right call path.

## What buyers get (files)
- launch_watcher.py (cron-ready)
- fallback_prep.py (multi-region builder)
- holographic_memory/ (memory system)
- godmode_squad/ (router + model_registry + manifest)
- TROUBLESHOOTING.md

## After publish
1. Copy the Gumroad product URL.
2. Replace the 3 placeholder links:
   - README.md  -> "[Gumroad — Sovereign AI Stack](...)"
   - docs/index.html -> class="cta" href="..."
   - POST_COPY.md -> "[GUMROAD LINK]"
3. git add -A && git commit -m "add gumroad link" && git push
4. Tell MIDAS the URL so it logs the first sale:
   python3 inbound_tracker.py log --source gumroad --note "live:<URL>"
