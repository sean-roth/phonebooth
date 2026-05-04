# Session Notes: 2026-05-04 (late Saturday / early Sunday)

## What Happened This Session

### Twilio Setup — Complete
- Account created and upgraded
- Phone number purchased: **+1 312 757 7434** (got a 312 after all)
- API Key created (Standard type)
- TwiML App "Phonebooth" configured:
  - Voice URL: `https://phonebooth.vfxbuddy.com/api/twilio/voice` (POST)
  - Status Callback: `https://phonebooth.vfxbuddy.com/webhooks/twilio/status` (POST)
- Phone number configured to use the Phonebooth TwiML App
- All 6 env vars populated in `.env`

### First Test Call — Successful
- Called Sean's cell (+1 719 321 8817) from the cockpit
- Call connected, audio worked both directions
- Post-call form functional

### Bug Found and Fixed: Codec Enum
- `Device.Codec.Opus` is undefined in Voice JS SDK 2.18
- The codec enum lives on `Call.Codec`, not `Device.Codec`
- Fixed: `import { Device, Call } from '@twilio/voice-sdk'` and `Call.Codec.Opus`
- Committed and pushed: `c3cfa10`
- **Note:** The earlier spec 04 correction used `Device.Codec` — this was wrong. The spec should say `Call.Codec`. Update spec 04 next session.

### Two Issues Found During Testing

#### 1. Voice Quality
- Audio quality was mediocre on the test call
- Likely causes to investigate:
  - Opus codec may not be negotiating (falling back to PCMU)
  - SSH port forward adds latency (localhost:8000 → joi → Twilio)
  - Laptop built-in mic/speakers vs headset
- **Fix path:** Get HTTPS tunnel working directly from laptop browser (fix DNS resolution issue) to eliminate the SSH hop. Use headset Monday.

#### 2. "Scam Likely" on Android
- New Twilio number flagged as spam by T-Mobile/Android
- **Not fixable before Monday.** Requires:
  - SHAKEN/STIR registration (Trust Hub → needs EIN + Twilio vetting)
  - CNAM registration (Trust Hub → needs Business Profile → 24-48hr propagation)
  - Branded Calling (beta, T-Mobile/Verizon only)
- **Immediate action:** Register at https://freecallerregistry.com tonight (free, instant submission)
- **EIN needed:** SOPs Nobody Reads EIN for Trust Hub Business Profile
- **Accept for Monday:** Calls will connect; opener handles the "who is this" moment

### DNS Issue — Unresolved
- `phonebooth.vfxbuddy.com` resolves correctly from joi (verified via curl)
- Sean's Windows laptop cannot resolve it — `nslookup` fails, even against 1.1.1.1
- Laptop DNS server is 103.86.96.100 (ISP resolver, may have slow propagation)
- **Workaround in use:** SSH port forward (`ssh -L 8000:localhost:8000 sean@10.0.0.1 -p 2222`)
- **To investigate tomorrow:**
  - Check if laptop can resolve `vfxbuddy.com` (root domain) — if not, broader DNS issue
  - Try `ipconfig /flushdns` on Windows
  - Try setting laptop DNS to 8.8.8.8 or 1.1.1.1 manually
  - Check if the nameserver change at Namecheap fully propagated
  - Test from phone browser (different network/DNS)

## Current System State

### Running
- **cloudflared tunnel:** running, connected to Cloudflare edge (Denver/KC)
- **Laravel:** `php artisan serve --host=0.0.0.0 --port=8000`
- **Access:** `http://localhost:8000` via SSH port forward from laptop

### To Start the System
```bash
# Terminal 1: tunnel (for Twilio webhooks)
cloudflared tunnel run phonebooth

# Terminal 2: Laravel
cd /home/sean/phonebooth && php artisan serve --host=0.0.0.0 --port=8000

# Laptop: SSH port forward (until DNS issue resolved)
ssh -L 8000:localhost:8000 sean@10.0.0.1 -p 2222
# Then open http://localhost:8000/leads in Chrome
```

### Database
- 4 CSV-imported leads (fake Chicago numbers)
- 1 lead updated to Sean's real cell for testing ("Test Call - Sean Cell")
- 2 call records from testing
- Event log has call_initiated + twilio_call_connected entries

## TODO for Tomorrow (Sunday)

### Must Do Before Monday
1. **Import real leads** — build 10-lead CSV per spec 06, import it, write briefs
2. **Fix DNS or accept SSH workaround** — try flushing DNS, changing laptop DNS server
3. **Test full call cycle** — call → hang up → fill form → Save and Next → verify lead status transitions
4. **Register at freecallerregistry.com** — +1 312 757 7434

### Should Do When Possible
5. **Fix spec 04** — update codecPreferences from `Device.Codec` to `Call.Codec`
6. **Start Trust Hub** — Business Profile with EIN for SHAKEN/STIR + CNAM
7. **Claude Desktop coaching setup** — per spec 09, configure filesystem MCP
8. **Headset test** — verify audio quality with proper headset vs laptop speakers

### Can Wait
9. **Set up cloudflared as systemd service** — so tunnel survives reboots
10. **Voice quality investigation** — check if Opus is negotiating, test without SSH hop
