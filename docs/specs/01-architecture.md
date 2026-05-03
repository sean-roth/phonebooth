# 01 — Architecture

## Purpose of this document

System overview for Phase 1. What the parts are, how they fit, what's in scope vs deferred.

## What this is

A self-hosted Laravel dashboard that combines lead management, browser-based softphone, automatic call recording, dual-channel transcription, and Claude Desktop coaching feedback for cold calling Chicago small businesses.

Phase 1 = Sean alone, calling 10 leads/day, learning the work.

## Constraints shaping this design

- **Runway is exhausted.** Every dollar matters. No subscription costs that punish bad days.
- **Sean is one person.** No multi-user concerns, no auth, no tenancy.
- **Building is regulation.** The system exists partly to give Sean something to make while processing the emotional weight of the work.
- **Phase 1 is throwaway.** The plan is to rebuild after a week of field testing. Don't optimize for permanence.
- **Self-hosted on existing OptiPlex 9020.** No cloud costs, no deployment story.
- **Local network only.** No public exposure except the ngrok tunnel for Twilio webhooks.
- **Illinois recording compliance is non-optional.** All-party consent state — see spec 10.

## Stack

- **Laravel** — backend, dashboard, request handling, view rendering
- **SQLite** — local single-file database (leads, calls, events)
- **Twilio** — telephony (Voice JS SDK in browser, recording infrastructure)
- **faster-whisper** — local Python subprocess for transcription
- **ffmpeg** — channel splitting (stereo → two mono files for speaker attribution)
- **Claude Desktop with filesystem MCP** — coaching feedback (uses Sean's existing subscription)
- **ngrok** — public tunnel for Twilio webhook delivery to localhost

No Anthropic API. No PostgreSQL. No queue worker. No Redis. No Docker.

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
│   ┌─────────────────┐                    │ webhook              │
│   │ Cockpit form    │                    │                      │
│   │ (disclosure +   │                    ▼                      │
│   │  dialer +       │             ┌──────────────┐              │
│   │  post-call)     │◄────────────┤ ngrok tunnel │              │
│   └────────┬────────┘             └──────┬───────┘              │
│            │ HTTP                        │                      │
└────────────┼────────────────────────────┼──────────────────────┘
             ▼                            ▼
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
│   ┌──────────────────────┐    ┌──────────────────────┐          │
│   │ SQLite               │    │ Process Call pipeline│          │
│   │ - leads              │    │                      │          │
│   │ - calls              │    │ 1. Download from     │          │
│   │ - events             │    │    Twilio (basic auth)│         │
│   │                      │    │ 2. Split stereo      │          │
│   │ - transcript col is  │    │    via ffmpeg        │          │
│   │   a cache; canonical │    │ 3. Whisper x2 passes │          │
│   │   is the markdown    │    │ 4. Merge segments    │          │
│   │   file               │    │    with SEAN/LEAD    │          │
│   └──────────────────────┘    │    labels            │          │
│                                │ 5. Write transcript  │          │
│                                │    markdown file     │          │
│                                └────────┬─────────────┘          │
│                                         │                        │
│                                         ▼                        │
│   ┌────────────────────────────────────────────────────┐        │
│   │ Filesystem                                         │        │
│   │ storage/app/recordings/{call_id}.mp3 (stereo)      │        │
│   │ storage/app/recordings/{call_id}_left.mp3 (Sean)   │        │
│   │ storage/app/recordings/{call_id}_right.mp3 (lead)  │        │
│   │ storage/app/coaching/transcripts/{call_id}.md      │        │
│   │ storage/app/coaching/feedback/{call_id}.md ◄─┐    │        │
│   └────────────────────────────────────────────────┼────┘        │
│                                                    │             │
└────────────────────────────────────────────────────┼─────────────┘
                                                     │
                                                     │ filesystem MCP
                                                     │
┌────────────────────────────────────────────────────┼─────────────┐
│                                                    │             │
│   Claude Desktop (Sean's subscription)             │             │
│                                                    │             │
│   "Phonebooth Coaching" Project                    │             │
│   - Jeb Blount skill in project knowledge          │             │
│   - Workflow note as system prompt                 │             │
│                                                    │             │
│   Sean: "Coach my unprocessed calls"               │             │
│       │                                            │             │
│       ▼                                            │             │
│   Reads transcripts/{call_id}.md ◄─────────────────┤ filesystem  │
│   Generates coaching markdown                      │ MCP         │
│   Writes feedback/{call_id}.md ────────────────────┘             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

The dashboard and Claude Desktop are loosely coupled via the filesystem. The dashboard knows nothing about Claude Desktop; Claude Desktop just sees a folder of transcripts to read and writes feedback alongside.

## Why these choices

**Why local Whisper instead of cloud transcription?**
Cost. faster-whisper on the OptiPlex CPU produces decent quality at $0/call. Cloud transcription (AssemblyAI, Deepgram) would be $0.0025-0.01/minute. At 1100 minutes/month that's $3-11. Not terrible, but: Whisper local is genuinely free, runs offline, doesn't add another vendor relationship, and the OptiPlex is sitting there idle anyway.

**Why dual-channel transcription with separate passes?**
Twilio's `record-from-answer-dual` produces stereo audio (left = Sean, right = lead). Mixing to mono before transcription throws away speaker attribution. Without attribution, coaching feedback can only describe the call abstractly — it can't say "you opened weakly" because it doesn't know who opened. Splitting and processing each channel separately preserves the entire point of stereo recording. See spec 05.

**Why Claude Desktop instead of Claude API for coaching?**
Cost (subscription is fixed, API is per-call). Simplicity (no API integration, no key management, no token counting). Better experience (interactive coaching with follow-up questions, pattern recognition across calls). The original mental model from early conversations was MCP-everything; the API drift was caught and corrected. See spec 09.

**Why SQLite instead of Postgres?**
Single user. Single machine. No connection management. No service to keep running. Backup is `cp database/database.sqlite somewhere`. Phase 2's Twenty CRM may push toward Postgres; cross that bridge then.

**Why Laravel instead of Rails / Django / Express?**
Sean knows it. SOPs Nobody Reads is also Laravel. Switching costs are real and Phase 1 isn't the place.

**Why ngrok instead of cloudflared / serveo / lt?**
ngrok is the most stable in Sean's experience. Free tier rotates URLs but works. Paid tier $8/mo for static URL is acceptable insurance. cloudflared is fine alternative — engineer's choice during build.

**Why is the disclosure script mandatory at the top of the cockpit page?**
Illinois is an all-party consent state. Recording without consent is a felony. The disclosure converts implied consent (continued participation after notification) into legal protection. See spec 10. This is not a UX decision; it's a legal one.

## What's in Phase 1

- Lead management (CSV import, manual brief editing)
- Browser softphone (Twilio Voice JS SDK)
- Recording disclosure + consent workflow (spec 10)
- Automatic call recording with auto-delete on declined consent
- Local Whisper transcription with dual-channel speaker attribution
- Transcript files written for Claude Desktop consumption
- Call detail pages displaying transcript and coaching (read from filesystem)
- Audio playback via Laravel-side proxy (Twilio basic auth requirement)
- Application logs (three named channels) and events table for debugging
- One coaching framework (Jeb Blount) loaded by Sean into Claude Desktop

## What's deferred to Phase 2+

Worth listing because the urge to add these now needs to be resisted:

- **Twenty CRM integration** — Phase 1's leads table is enough for one person; Twenty is the proper system but its setup eats a day
- **Pre-call brief auto-generation** — spec 06 brief is template-driven; auto-generation needs Phase 2
- **Multiple coaching frameworks** — Jeb Blount only for Phase 1; add SPIN, Sandler, etc. as Project knowledge variants in Phase 2
- **Cost tracking dashboard** — Twilio is the only meaningful cost in Phase 1, visible in Twilio's console
- **Audit hash chain** — events table is the substrate; cryptographic chaining is Phase 2
- **Pretty UI** — Tailwind defaults for Phase 1; design pass later
- **Apollo / Google Maps API integration for lead generation** — manual sourcing for Phase 0/1
- **Territory tab with neighborhood context** — Phase 2
- **Pain-points pattern recognition automation** — Sean can ask Claude Desktop to find patterns manually for now
- **Speaker diarization beyond channel splitting** — current approach handles the 95% case
- **Real-time transcription** — out
- **Auto-coaching trigger when transcript appears** — Phase 2 (would require a watcher process)
- **Queue-based async processing** — synchronous is fine for one user
- **User accounts / auth** — Phase 2 if ever needed
- **Pre-call message played to lead announcing recording** — Sean reads disclosure himself in Phase 1; automated TwiML pre-message is a Phase 2 option
- **Multi-state legal compliance** — Phase 1 is Illinois only

## Cost expectations

At Phase 1 volume (10 calls/day, 5 min average, ~22 work days/month):

- **Twilio:** ~$5-25/month
  - Number rental: $1.15/month
  - Outbound minutes: ~1,100 × $0.014 = $15.40
  - Recording: ~1,100 × $0.0025 = $2.75
  - Recording storage: ~$0.50
- **faster-whisper local:** $0
- **Claude Desktop coaching:** $0 incremental (existing subscription)
- **ngrok:** $0 (free tier) or $8/month (static URL)
- **Hosting:** $0 (OptiPlex sitting at home)

**Total: $5-25/month at moderate volume; ~$1.15 on a zero-call week.** Pay-as-you-go shape is intentional.

## Operational model

Sean runs the dashboard locally. ngrok tunnels his localhost to a public HTTPS URL. Twilio webhook config points at the ngrok URL. When Sean restarts the OptiPlex or ngrok, the URL changes (free tier) — he updates `.env` and the Twilio TwiML App config.

The OptiPlex is otherwise running Sean's other projects (Clara, SOPs Nobody Reads), so it's already on. Phonebooth is just another Laravel app on it.

For coaching: Sean opens Claude Desktop separately, navigates to the Phonebooth Coaching project, asks Claude to coach unprocessed calls. Claude reads transcripts via filesystem MCP, generates coaching, writes feedback files. Dashboard reads them at display time.

## What this architecture optimizes for

In priority order:

1. **Cost stability under variable activity.** Bad days cost ~$1.15. Good days cost more proportionally. No subscriptions to feel guilty about.
2. **Legal compliance.** Spec 10's disclosure-and-delete pattern protects Sean from criminal/civil liability.
3. **Coaching quality.** Dual-channel attribution + interactive Claude Desktop = useful feedback, not generic platitudes.
4. **Debuggability when something breaks.** Three log channels + events table = answers in 30 seconds.
5. **Throwability.** SQLite, local files, no service dependencies. Sean can rebuild from scratch in a weekend if the design is wrong.

## What this architecture explicitly does NOT optimize for

- Scale (single user, single machine — Phase 2 problem if ever)
- Polish (Tailwind defaults are fine)
- Permanence (assume rebuild after field testing)
- Speed of pipeline (2-3 minutes for transcription is fine when batch-coaching at end of session)
- Real-time anything (post-call workflow throughout)
- Mobile (cockpit is laptop-only; no responsive design)
- Vendor independence (Twilio lock-in is acceptable; switching cost is one component)

## A note on the design conversation

This system was designed across multiple Designer Claude conversations with several architectural revisions:

1. Original: dashboard hits Anthropic API for coaching (rejected for cost/complexity)
2. Revised: dashboard writes transcripts, Claude Desktop reads via MCP and writes feedback (current design)
3. Late catch: dual-channel mixing to mono was discarding speaker attribution (fixed in spec 05)
4. Late catch: Illinois all-party consent law requires disclosure-and-consent workflow (added in spec 10)

The repo's commit history shows the evolution. Specs 04 and 05 contain memory-derived API details that need verification (see spec 08).

This is a Phase 1 system that knows it's Phase 1. The next conversation that picks it up should be open to throwing pieces away.
