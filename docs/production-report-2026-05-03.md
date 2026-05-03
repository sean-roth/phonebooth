# Production Report: Phase 1 Build

**Date:** 2026-05-03 (Saturday evening)
**Engineer:** Claude Code (Opus 4.6)
**Machine:** joi (OptiPlex 9020, Ubuntu 24.04, PHP 8.3.6, Node 20.19.5)

---

## What Was Built

A Laravel 13 cold-call dashboard with browser-based Twilio softphone, lead management, CSV import, post-call notes, and event logging. The full Phase 1 spec (12 docs) was implemented in a single session.

### Stack

- Laravel 13.7.0
- SQLite (single-file database)
- Twilio Voice JS SDK 2.18.2 (browser softphone via WebRTC)
- Twilio PHP SDK 8.11.x (token generation, TwiML, webhook verification)
- Tailwind CSS v4 (shipped with Laravel 13)
- Vite (asset bundling, cockpit.js as separate entrypoint)
- cloudflared (Cloudflare Tunnel for public HTTPS access)

### Files Created

- 4 controllers: LeadController, CallController, TwilioTokenController, TwilioWebhookController
- 3 models: Lead, Call, Event
- 1 service: EventLogger
- 1 middleware: VerifyTwilioSignature
- 6 Blade views: layouts/app, leads/index, leads/show, leads/partials/import-modal, calls/create (cockpit), calls/show
- 1 Blade component: status-badge
- 2 JS files: twilio-device.js (PhoneboothDevice wrapper), cockpit.js (cockpit page wiring)
- 3 migrations: leads, calls, events
- 1 seeder: LeadSeeder (5 Chicago test businesses)

### Routes (13 application routes)

```
GET   /                        → redirect to /leads
GET   /leads                   → lead list with status filter
POST  /leads/import            → CSV import
GET   /leads/{lead}            → lead detail + brief editor
PATCH /leads/{lead}            → update lead
GET   /leads/{lead}/call       → cockpit page
POST  /calls                   → create call record (JSON)
PATCH /calls/{call}            → save post-call form
GET   /calls/{call}            → call detail
POST  /webhooks/twilio/status  → Twilio status callback
GET   /api/twilio/token        → Twilio capability token
POST  /api/twilio/voice        → TwiML voice endpoint
```

---

## Spec Verification (Spec 08)

Before building, all Twilio API details from spec 08 were verified against live sources:

| Item | Status |
|------|--------|
| Voice JS SDK custom params propagate as POST form data | Confirmed (load-bearing assumption) |
| PHP SDK class names and namespaces | Confirmed (v8.11.4, source code verified on GitHub) |
| Status webhook sends CallSid, CallStatus, CallDuration | Confirmed (CallDuration only on 'completed') |
| @twilio/voice-sdk npm package current | v2.18.2, Node >= 12 |
| Twilio pricing ($1.15/mo number, $0.014/min outbound) | Confirmed |
| Trial account verified-numbers-only restriction | Confirmed ($20 upgrade to call any number) |
| Chicago 312 area code availability | May be exhausted; 773/872 as fallbacks |
| ngrok free tier | Now has interstitial page that breaks webhooks — switched to cloudflared |

### Spec Corrections Committed

6 bugs found in specs during verification and implementation, all committed back:

| Spec | Bug | Fix |
|------|-----|-----|
| 02 | Event model uses deprecated `$dates` property | Changed to `$casts['created_at' => 'datetime']` |
| 04 | `codecPreferences: ['opus', 'pcmu']` (strings) | Changed to `[Device.Codec.Opus, Device.Codec.PCMU]` |
| 04 | `voice()` missing EventLogger for `twilio_call_connected` | Added EventLogger injection and event recording |
| 04 | `enablePostCallForm()` missing `form.action` URL | Added `postCallForm.action = '/calls/' + currentCallId` |
| 08 | Assumes ngrok free tier works for webhooks | Added warning: interstitial page breaks non-browser clients |
| 03 | `CallController::update()` missing `last_call_date` update | Added (caught during planning, not in spec commit) |

---

## QA Passes Run

Four structured QA passes (per docs/skills/qa-passes/SKILL.md):

### 1. Consistency Pass
Checked disposition enum (8 values), lead status enum (8 values), event types (4), route paths (13), calls table columns (11), leads table columns (15) across all specs and code. **No disagreements found.**

### 2. Traceability Pass
Traced 12 specific requirements from specs to code. **11 passed, 1 partial fail** (error event missing from CSV import catch block — fixed).

### 3. Quality-Gate Pass
Traced 10 Monday-morning UX scenarios. Found **2 blockers + 4 friction issues:**

| Issue | Severity | Fix |
|-------|----------|-----|
| Double-click on Call button creates duplicate records | Blocker | Button disabled immediately on click |
| Lead status never updates after call (Save and Next loops) | Blocker | Auto-transition based on disposition |
| Validation errors lose form data | Friction | Added `old()`, `@error` directives, pending call detection |
| Error event missing from CSV import | Friction | Added EventLogger to catch block |

All four fixed and committed.

### 4. Dead-Code / Stale-Reference Pass
Searched all 14 patterns from handoff.md's warning list (recording, whisper, ffmpeg, disclosure, Anthropic API, removed columns, removed routes, removed directories). **Zero stale references found.** The recording pivot is clean.

---

## Infrastructure

### Cloudflare Tunnel

- **URL:** https://phonebooth.vfxbuddy.com
- **Tunnel ID:** 0dd8700e-7b2d-4337-bdf6-8e6ad962b272
- **Config:** ~/.cloudflared/config.yml
- **Credentials:** ~/.cloudflared/0dd8700e-7b2d-4337-bdf6-8e6ad962b272.json
- **Status:** Tested — returns 200 through Cloudflare edge (Denver/KC nodes)
- **Cost:** $0 (Cloudflare free plan + existing domain)

### Running the System

```bash
# Terminal 1: tunnel
cloudflared tunnel run phonebooth

# Terminal 2: Laravel
cd /home/sean/phonebooth && php artisan serve --host=0.0.0.0 --port=8000
```

Since the public URL is HTTPS, laptop browsers can access `https://phonebooth.vfxbuddy.com` directly — no SSH port forwarding needed for mic access (Chrome allows `getUserMedia()` on HTTPS origins).

### Environment

`.env` is configured with:
- `APP_NAME=Phonebooth`
- `DB_CONNECTION=sqlite`
- `TUNNEL_URL=https://phonebooth.vfxbuddy.com`
- 6 TWILIO_* placeholders (empty, pending account setup)

---

## What's Left Before Monday

### Sean's Tasks (Sunday afternoon)

1. **Twilio account:** Sign up → upgrade ($20) → buy 773 number (872 fallback)
2. **Twilio credentials:** Create API Key + Secret → create TwiML App with voice URL `https://phonebooth.vfxbuddy.com/api/twilio/voice`
3. **Fill `.env`:** TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_API_KEY_SID, TWILIO_API_KEY_SECRET, TWILIO_TWIML_APP_SID, TWILIO_PHONE_NUMBER
4. **Test call:** Verify own cell on Twilio (trial requirement) → place test call from cockpit → fill form → verify events table
5. **Import leads:** Build 10-lead CSV per spec 06 → import → write briefs for first few

### Claude Desktop Coaching Setup (optional, per spec 09)

- Configure filesystem MCP in claude_desktop_config.json pointing at `storage/app/coaching/`
- Create "Phonebooth Coaching" project
- Add Jeb Blount skill as project knowledge
- Test with a sample discovery transcript

---

## What's Deliberately Not Built

Per spec 11 (recording pivot) and spec 01 (architecture):

- No call recording, no Whisper transcription, no audio processing
- No Anthropic API integration
- No user auth
- No pagination or search on leads
- No pretty UI beyond Tailwind defaults
- Discovery call coaching is Claude Desktop + Google Meet (manual workflow, not dashboard)

Phase 1 is designed to be thrown away after a week of field testing.

---

## Commit History

```
474ca77 Fix 4 issues from QA passes
16ceb8a Build Phase 1 phonebooth dashboard
01b15ea Fix spec bugs found during build verification
```

---

## Risk Register

| Risk | Mitigation | Status |
|------|-----------|--------|
| Twilio trial can only call verified numbers | Verify own cell first; upgrade Sunday | Pending |
| 773 area code unavailable | Fall back to 872 | Pending |
| cloudflared tunnel goes down | Restart with `cloudflared tunnel run phonebooth` | Monitored |
| OptiPlex loses power | Stage 2 (Cloudflare Tunnel as service) per spec 12 | Accepted for Phase 1 |
| Cockpit UX doesn't work under stress | Field testing Monday will surface issues | By design |
