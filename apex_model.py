
# APEX AI SOLUTIONS — REAL UNIT-ECONOMICS MODEL
def clients_per_spears(spears, c):
    return spears * c['spear_reply'] * c['reply_meeting'] * c['meeting_tripwire'] * c['tripwire_core']

base = dict(spear_reply=0.10, reply_meeting=0.70, meeting_tripwire=0.30, tripwire_core=0.25)
low  = dict(spear_reply=0.05, reply_meeting=0.50, meeting_tripwire=0.20, tripwire_core=0.15)
high = dict(spear_reply=0.15, reply_meeting=0.80, meeting_tripwire=0.40, tripwire_core=0.35)

MRR = 2997
ARR_C = MRR * 12
TARGET = 10_000_000
need = TARGET / ARR_C

print("=== 1. $10M / 36-MO REALITY ===")
print(f"Clients needed @ ${MRR}/mo = {need:.0f}")
for name, c in [("BASE", base), ("LOW", low), ("HIGH", high)]:
    per200 = clients_per_spears(200, c)
    spears = need / per200 * 200
    hrs = spears * 0.5
    print(f"  {name}: {per200:.2f} clients/200 spears | spears to target = {spears:,.0f} | research hrs = {hrs:,.0f}")

print("\n=== 2. SOLO THROUGHPUT ===")
for pd in [8, 15, 25]:
    peryr = pd * 240
    cy = clients_per_spears(peryr, base)
    print(f"  {pd} spears/day ({pd*0.5:.0f}h research/day): ~{cy:.0f} clients/yr -> {need/cy:.1f} yrs to $10M")

print("\n=== 3. 12-MO BASE P&L (build mo1-3, core from mo4) ===")
spears = [120,160,200,240,260,280,300,300,320,320,340,340]
cum=0; trip=0; core_mrr=0
for m in range(1,13):
    s=spears[m-1]
    audits=s*base['spear_reply']*base['reply_meeting']*base['meeting_tripwire']
    trip+=audits*497
    if m>=4:
        cum+=s*base['spear_reply']*base['reply_meeting']*base['meeting_tripwire']*base['tripwire_core']
    core_mrr=cum*MRR
arr=core_mrr*12
print(f"  Mo12: clients={cum:.1f} | core MRR=${core_mrr:,.0f} | ARR=${arr:,.0f} | tripYTD=${trip:,.0f}")

print("\n=== 4. 12-MO COST/PROFIT ===")
dev=6000*12; cs=4000*2*8; tools=500*12; opex=dev+cs+tools
print(f"  ARR(mo12)=${arr:,.0f}  OPEX=${opex:,.0f}  net~${arr-opex:,.0f} (+trip ${trip:,.0f} = ${(arr-opex+trip):,.0f})")
