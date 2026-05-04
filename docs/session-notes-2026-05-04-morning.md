# Session Notes: 2026-05-04 (Sunday morning)

## What Got Done

### DNS Issue Resolved
- Sean's laptop couldn't resolve `phonebooth.vfxbuddy.com` Saturday night
- Root cause: NordVPN's DNS server (103.86.96.100) hadn't propagated the new CNAME yet
- Overnight propagation fixed it — `nslookup` now returns Cloudflare IPs even with NordVPN running
- **Direct HTTPS access from laptop is working** — no more SSH port forward needed

### Voice Quality Troubleshooting
- Sean is using a **Logitech G335** gaming headset (decent quality)
- Initial audio sounded "distant" — fixed by:
  - **Disabling Windows audio enhancements** (was over-processing voice)
  - Repositioning the boom mic 1 inch from corner of mouth
- Static issue from cranking Microphone Boost too high — fixed by:
  - Setting Microphone Boost back to **0 dB**
  - Raising Microphone Volume slider to 100 instead
- Final result: clear, telephony-quality audio. PSTN bandwidth ceiling (3.4kHz) is fundamental — chasing studio quality on phone calls is a trap.

### Phase 1 Scope Reaffirmed
- Sean considered buying multiple Twilio numbers for major cities
- Engineer pushed back: scope creep before field testing dilutes learning signal
- Sean confirmed Phase 1 stays Chicago-only with single 312 number
- Customer profiles + multi-city expansion deferred to Phase 2 (post-field-test data)

### Twilio Account Upgrade
- Upgraded from trial to paid (added $20 minimum)
- Trial credit forfeited (expected)
- Existing 312 number, TwiML App, API keys all carried over unchanged

### Anti-Spam Registrations

| Registration | Status |
|---|---|
| Free Caller Registry | ✓ Submitted (5 min, instant) |
| Trust Hub Customer Profile | ✓ Submitted, in review |
| Trust Hub CNAM Trust Product | ✓ Submitted ("Sean Roth" 9-char display name) |
| SHAKEN/STIR | ✓ **APPROVED — immediate effect** |

### "Scam Likely" — Resolved
- SHAKEN/STIR Level A attestation now active on all outbound calls from 312 number
- T-Mobile dropped the spam flag immediately upon test call
- Carriers see calls as cryptographically signed and verified
- CNAM display name will populate once Customer Profile vets through (1-3 business days)

## Current System State

### Live Infrastructure
- **Tunnel:** cloudflared running, https://phonebooth.vfxbuddy.com active
- **Laravel:** running on joi at port 8000
- **Twilio:** paid account, 312 number with TwiML App + SHAKEN/STIR
- **Direct laptop access:** Chrome → `https://phonebooth.vfxbuddy.com/leads` (NordVPN OK)

### Spec Correction Pending
- Spec 04's `codecPreferences` was corrected to `Device.Codec` yesterday
- Actual SDK exports it on `Call.Codec`, not `Device.Codec`
- Code is correct (commit `c3cfa10`), but spec 04 still says `Device.Codec`
- **TODO:** Fix spec 04 to reflect `Call.Codec.Opus` and `Call.Codec.PCMU`

## What's Left Before Monday

1. **Build 10-lead CSV** per spec 06 (specialty trades + independent retailers in Chicago)
2. **Import the CSV** at `/leads`
3. **Write briefs** for the first 3-5 leads (research their websites, note pain signals)
4. **Place a final test call** end-to-end (own cell or a friend) to confirm the post-call form save flow works
5. **Sleep**

## Decisions Confirmed This Session

- **Phase 1 = Chicago only** (no multi-city expansion until field testing produces data)
- **CNAM display name = "Sean Roth"** (real human name beats branded business name for cold calls)
- **Headset = Logitech G335** with enhancements off, boost at 0, volume at 100
- **Mic position = 1 inch from corner of mouth** on the boom
- **Audio quality = "good enough"** — phone calls are inherently bandwidth-limited

## Risk Notes

- CNAM won't be live by Monday morning (1-3 day vetting + carrier propagation)
- This is fine — SHAKEN/STIR is doing the heavy lifting on spam labeling
- Free Caller Registry adds belt-and-suspenders coverage with major US carriers
