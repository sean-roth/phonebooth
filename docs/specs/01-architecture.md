# 01 — Architecture

## Purpose of this document

System overview for Phase 1.

## What this is

A self-hosted Laravel dashboard that combines lead management, a browser-based softphone, and post-call note capture for cold calling Chicago small businesses.

Discovery calls (which happen separately in Google Meet) are coached via Claude Desktop reading Google Meet transcripts. The dashboard does not handle discovery calls directly.

Phase 1 = Sean alone, calling 10 leads/day, learning the work.

**Note: this spec was substantially simplified by spec 11 (recording pivot).** Earlier drafts had recording, transcription, dual-channel splitting, AI-generated coaching for cold calls, and an Illinois consent compliance layer. All removed.

## Constraints shaping this design

- **Runway is exhausted.** Every dollar matters.
- **Sean is one person.** No multi-user concerns.
- **Building is regulation.** The system gives Sean something to make while processing the emotional weight of the work.
- **Phase 1 is throwaway.** Plan to rebuild after a week of field testing.
- **Self-hosted on existing OptiPlex 9020.** No cloud costs.
- **Local network only.** No public exposure except ngrok for Twilio webhooks.
- **Cold calls are not recorded.** Per spec 11.

## Stack

- **Laravel** — backend, dashboard, request handling
- **SQLite** — local single-file database
- **Twilio** — telephony (Voice JS SDK in browser, no recording)
- **Google Meet** — discovery call hosting + recording (handled outside phonebooth)
- **Claude Desktop with filesystem MCP** — discovery-call coaching feedback (uses Sean's existing subscription)
- **ngrok** — public tunnel for Twilio webhook delivery to localhost

No Anthropic API. No Whisper. No ffmpeg. No Python. No PostgreSQL. No queue worker. No Redis. No Docker.

## Data flow

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Browser (cockpit page on localhost:8000)                      │
│                                                                 │
│   ┌─────────────────┐   WebRTC   ┌──────────────┐              │
│   │ Voice JS SDK    │◄──────────►│   Twilio     │              │
│   │ (audio in/out)  │             │  (telephony) │              │
│   └─────────────────┘             └──────┬───────┘              │
│                                          │                      │
│   ┌─────────────────┐                    │ status webhook       │
│   │ Cockpit form    │                    │                      │
│   │ (dialer +       │                    ▼                      │
│   │  post-call)     │◄────────────┌──────────────┐              │
│   └────────┬────────┘             │ ngrok tunnel │              │
│            │ HTTP                 └──────────────┘              │
└────────────┼─────────────────────────────────────────────────────┘
             ▼
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   Laravel dashboard                                              │
│                                                                  │
│   ┌──────────────────┐                                          │
│   │ LeadController   │                                          │
│   │ CallController   │                                          │
│   │ TwilioWebhook... │                                          │
│   └────────┬─────────┘                                          │
│            │                                                     │
│            ▼                                                     │
│   ┌──────────────────────┐                                      │
│   │ SQLite               │                                      │
│   │ - leads              │                                      │
│   │ - calls              │  ← lead_id + Twilio CallSid +        │
│   │ - events             │    duration + Sean's observations    │
│   └──────────────────────┘                                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

Discovery call workflow (separate from dashboard):

┌────────────────────────────────────────────────────┐
│   Google Meet                                      │
│   - Sean schedules with lead                       │
│   - Recording indicator notifies all participants  │
│   - Workspace exports transcript                   │
└────────────────┬───────────────────────────────────┘
                 │
                 │  Sean saves transcript to:
                 ▼
┌────────────────────────────────────────────────────┐
│   storage/app/coaching/discoveries/{filename}.md   │
└────────────────┬───────────────────────────────────┘
                 │
                 │  Sean opens Claude Desktop, asks for coaching
                 ▼
┌────────────────────────────────────────────────────┐
│   Claude Desktop "Phonebooth Coaching" Project     │
│   - Reads transcript via filesystem MCP            │
│   - Reads framework skill (SPIN, Sandler, etc.)    │
│   - Generates coaching markdown                    │
│   - Writes to feedback/{filename}.md               │
└────────────────────────────────────────────────────┘
```

The dashboard handles cold-call top-of-funnel; Google Meet + Claude Desktop handle the discovery-call coaching loop. They're loosely coupled — Sean is the only thing tying them together.

## Why these choices

**Why no recording for cold calls?**
Per spec 11: cold calls are 30-90 seconds with low coaching signal, and Illinois' all-party consent law requires a disclosure script that adds friction and decline-rate risk. Removing recording removes both the disclosure burden and the legal exposure.

**Why coach discovery calls instead?**
Discovery calls are 30-minute conversations about pain points, qualification, and value framing — much richer coaching data. Google Meet handles the consent question natively (recording indicator visible to all participants), so the legal posture is clean.

**Why Claude Desktop instead of Claude API for coaching?**
Cost (subscription is fixed, API is per-call). Simplicity (no API integration, no key management). Better experience (interactive coaching with follow-up questions, pattern recognition across calls).

**Why SQLite instead of Postgres?**
Single user. Single machine. No connection management. Backup is `cp database/database.sqlite somewhere`.

**Why Laravel instead of Rails / Django / Express?**
Sean knows it. SOPs Nobody Reads is also Laravel. Switching costs are real.

**Why ngrok?**
Most stable in Sean's experience. Free tier rotates URLs but works. Paid tier $8/mo for static URL is acceptable insurance.

## What's in Phase 1

- Lead management (CSV import, manual brief editing)
- Browser softphone (Twilio Voice JS SDK)
- Post-call form capturing Sean's own observations (disposition, pain points, notes)
- Application logs (three named channels) and events table for debugging
- Manual discovery-call coaching workflow via Google Meet + Claude Desktop

## What's deferred to Phase 2+

- **Twenty CRM integration** — Phase 1's leads table is enough for one person
- **Pre-call brief auto-generation** — manual for Phase 1
- **Multiple coaching frameworks** — Sean swaps project knowledge in Claude Desktop manually
- **Cost tracking dashboard** — Twilio is the only meaningful cost, visible in their console
- **Audit hash chain** — events table is the substrate; cryptographic chaining is Phase 2
- **Pretty UI** — Tailwind defaults for Phase 1
- **Apollo / Google Maps API integration for lead generation** — manual sourcing
- **Territory tab with neighborhood context** — Phase 2
- **Pain-points pattern recognition automation** — Sean asks Claude Desktop manually
- **Real-time transcription** — out
- **Discovery call records as separate DB entity** — Phase 1 tracks via lead status updates
- **Auto-import of Google Meet transcripts** — Sean does it manually for Phase 1
- **Cold-call recording reintroduction** — possible if field testing shows it would have been valuable
- **User accounts / auth** — Phase 2 if ever needed

## Cost expectations

At Phase 1 volume (10 calls/day, 5 min average, ~22 work days/month):

- **Twilio:** ~$5-17/month (number + outbound minutes only; no recording)
  - Number rental: $1.15/month
  - Outbound minutes: ~1,100 × $0.014 = $15.40
- **Anthropic API:** $0
- **Claude Desktop:** $0 incremental (existing subscription)
- **Google Workspace:** $0 incremental (existing — needed for Meet recording transcripts)
- **ngrok:** $0 (free tier) or $8/month (static URL)
- **Hosting:** $0 (OptiPlex)

**Total: $5-17/month at moderate volume; ~$1.15 on a zero-call week.**

## Operational model

Sean runs the dashboard locally. ngrok tunnels his localhost to a public HTTPS URL. Twilio webhook config points at the ngrok URL. The OptiPlex is otherwise running Sean's other projects (Clara, SOPs Nobody Reads), so it's already on.

For coaching: Sean opens Claude Desktop separately, navigates to the Phonebooth Coaching project, asks Claude to coach the latest discovery call. Claude reads the transcript via filesystem MCP, generates coaching, writes feedback files.

## What this architecture optimizes for

In priority order:

1. **Cost stability under variable activity.** Bad days cost ~$1.15.
2. **Simplicity.** Fewer moving parts, less to debug, less to learn how to operate.
3. **Coaching quality where it matters.** Discovery calls are the substantive conversations; cold calls are the booking mechanism.
4. **Debuggability.** Three log channels + events table.
5. **Throwability.** SQLite, local files, no service dependencies.

## What this architecture explicitly does NOT optimize for

- Scale (single user, single machine)
- Polish (Tailwind defaults are fine)
- Permanence (assume rebuild after field testing)
- Real-time anything (post-call workflow throughout)
- Mobile (cockpit is laptop-only)
- Vendor independence (Twilio + Google Meet + Claude Desktop lock-in is acceptable)
- AI coaching of cold calls (deliberately out — see spec 11)

## A note on the design history

This system went through several architectural revisions:

1. **Original:** dashboard hits Anthropic API for coaching (rejected for cost/complexity)
2. **Pivot 1:** dashboard writes transcripts; Claude Desktop reads via MCP (current coaching mechanism)
3. **Catch:** dual-channel mixing to mono was discarding speaker attribution (fixed)
4. **Catch:** Illinois all-party consent law required disclosure-and-consent workflow (added then removed)
5. **Final pivot:** stop recording cold calls entirely; coach discovery calls only (spec 11, current architecture)

The repo's commit history shows the evolution. This is a Phase 1 system that knows it's Phase 1. The next conversation should be open to throwing pieces away.
