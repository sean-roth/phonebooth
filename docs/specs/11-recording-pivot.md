# 11 — Recording Architecture Pivot

## What changed

Phase 1 originally recorded all cold calls via Twilio, transcribed them locally with faster-whisper (dual-channel split for speaker attribution), and surfaced the transcripts to Claude Desktop for coaching feedback against the Jeb Blount framework.

That entire pipeline has been removed.

The new Phase 1 approach:

- **Cold calls are not recorded.** No Twilio recording. No Whisper. No transcription. No coaching feedback for cold calls.
- **Discovery calls are recorded — but in Google Meet, not phonebooth.** Google Meet's built-in recording surfaces a recording indicator to all participants, which constitutes notice + implied consent under Illinois law. The framing to the lead is mutual benefit: "we'll both have notes and a reference point as we work."
- **Coaching shifts to discovery calls only.** Sean exports the Google Meet transcript (or pastes it) into Claude Desktop. The Jeb Blount skill (or whatever framework) coaches against that transcript.

## Why this is better

**The data argument.** A 30-90 second cold call where Sean is trying to book a meeting has very little coaching signal. The interesting moments — pain discovery, qualification, objection handling, value framing — happen in discovery calls. Coaching cold calls is coaching the equivalent of an elevator pitch; coaching discovery calls is coaching actual sales conversations.

**The friction argument.** The disclosure script ("I record my calls and have an AI transcribe them...") was the first words of every cold call. That created a decline-rate risk and a psychological burden for Sean before he even introduced himself. Removing it means Sean can open with his actual pitch. Lower friction for him, less weirdness for the lead.

**The legal argument.** Illinois' all-party consent law was the reason the disclosure existed. Without recording, there's no consent obligation. Discovery calls in Google Meet have the recording indicator built into the platform UX — leads see it, the platform notifies them, that's the consent mechanism. Cleanly inside the law without Sean having to manage it.

**The memory argument.** Sean noted that on a recent important call (the "Thatcher call"), he wished he'd had a recording to refer back to. A 90-second cold call is easy to remember; a 30-minute discovery conversation about pain points and AI applications is not. Recording the calls that actually require recall is a better use of recording infrastructure than recording everything.

**The complexity argument.** Removing the recording pipeline removes ~40% of Phase 1's spec content: the Twilio recording config, the dual-channel splitting via ffmpeg, the Whisper subprocess management, the transcript file generation, the coaching folder structure, the disclosure UI, the auto-delete-on-decline logic, the recording deletion API call. The system Sean has to operate Monday morning becomes substantially smaller.

## What stays

- Lead management (CSV import, brief editing, status tracking)
- Browser softphone (Twilio Voice JS SDK) — calling still happens, just not recording
- Post-call form (disposition, pain points, notes) — Sean's own observations replace AI-generated transcripts for cold calls
- Events table + logging (debugging substrate)
- Claude Desktop coaching workflow — but applied to Google Meet transcripts of discovery calls, not cold-call audio

## What this changes in the specs

The following specs are affected:

- **Spec 02 (data model):** remove `recording_url`, `recording_local_path`, `transcript`, `processed_at`, `twilio_recording_sid` columns from the calls table. Remove `declined_recording` from disposition enum.
- **Spec 03 (routes/controllers):** remove `/calls/{call}/audio` route. Remove `/calls/{call}/process` route. Remove disclosure section from cockpit page. Remove auto-delete logic from CallController::update. Simplify call detail view (no transcript, no coaching display section).
- **Spec 04 (Twilio):** remove all recording configuration. Remove `record-from-answer-dual` from TwiML. Remove recording webhook handler. Keep only the dialer infrastructure.
- **Spec 05 (Whisper):** delete entirely. There is no transcription pipeline.
- **Spec 07 (logging):** remove `recording_downloaded`, `transcript_generated`, `consent_declined`, `recording_deleted` events. Keep call lifecycle events.
- **Spec 08 (verification checklist):** remove faster-whisper section, ffmpeg section, recording deletion API section.
- **Spec 09 (Claude Desktop coaching):** rewrite. Workflow now: Sean exports Google Meet transcript → pastes/saves to a designated folder → Claude Desktop reads via filesystem MCP → writes coaching feedback. No cold-call coaching.
- **Spec 10 (legal compliance):** delete entirely. No recording = no consent obligation in phonebooth itself. Discovery calls in Google Meet are governed by the platform's consent mechanism.
- **Spec 00 (build order):** remove Whisper installation step. Remove ffmpeg verification. Build is shorter.

## What's removed entirely

- `scripts/transcribe.py` (was never built; removed from spec 05)
- `app/Services/RecordingDownloader.php` (was never built)
- `app/Services/Transcriber.php` (was never built)
- `app/Services/ChannelSplitter.php` (was never built)
- `storage/app/recordings/` directory (no longer needed)
- `storage/app/coaching/transcripts/` directory (no longer needed for cold calls; may be used differently for discovery call transcripts)
- All faster-whisper Python dependencies
- All Twilio recording costs (~$3-5/month savings)

## What discovery-call coaching looks like

Sean has a discovery call booked with a lead. The discovery call happens in Google Meet (or Zoom — same pattern). Google Meet records the call (Sean enables recording at meeting start; the platform displays the recording indicator to all participants).

After the call:

1. Sean downloads the transcript from Google Meet (Workspace's native transcript feature, or a third-party tool if needed)
2. Sean saves it as `discovery-{lead-name}-{date}.md` in `storage/app/coaching/discoveries/` (new folder)
3. Sean opens Claude Desktop, the Phonebooth Coaching project
4. Asks: "Coach my latest discovery call"
5. Claude Desktop reads the transcript via filesystem MCP, generates coaching feedback, writes to `storage/app/coaching/feedback/discovery-{lead-name}-{date}.md`

This is functionally the same workflow as the original spec 09, just applied to a different (more valuable) input.

The discovery call coaching can also include:

- Pattern recognition across multiple discovery calls ("what objections keep coming up")
- Framework-specific analysis (Jeb Blount for cold calls; SPIN or Sandler for discovery calls — Sean can swap project knowledge)
- Pain points extraction (replacing the manual pain_points field, since Claude reads the full transcript)
- Action items / follow-up prompts

This is genuinely more powerful than the cold-call coaching ever would have been.

## What Sean still does Monday morning

Same as before, minus the disclosure ritual:

1. Open phonebooth, see ten leads
2. Click into the first one, read the brief
3. Put on headset
4. Click Call
5. Say "Hi, this is Sean Roth from..." and pitch
6. Hang up
7. Fill in disposition, pain points (his own observations), notes
8. Click Save and Next

If a discovery call gets booked: schedule it in Google Meet with the lead, attach the brief as context, and conduct it there.

## Discovery-call workflow integration

Phase 1 doesn't need a "discovery call" feature in the dashboard. The lead's status moves to `discovery_booked`. Sean schedules the Google Meet directly with the lead via email. The phonebooth dashboard is unaware of the meeting itself.

After the discovery call, Sean updates the lead's status (`discovery_completed` or similar) and saves the transcript-coaching pair as described above. Phase 2 might integrate Google Calendar / Meet directly, but Phase 1 stays simple.

## Cost change

| Component | Before | After |
|---|---|---|
| Twilio number | $1.15/mo | $1.15/mo |
| Twilio outbound minutes | $15.40/mo | $15.40/mo |
| Twilio recording per-minute | $2.75/mo | $0 |
| Twilio recording storage | $0.50/mo | $0 |
| Anthropic API | $0 | $0 |
| Claude Desktop | $0 incremental | $0 incremental |
| **Phase 1 total** | **~$20/mo** | **~$17/mo** |

Marginal savings, but the simplicity savings are larger — fewer moving parts, less to debug, less to verify, less for Sean to learn how to operate.

## Risk: what if cold-call coaching would have been useful?

Possible. Sean is making a bet here that the ten cold calls per day for a week will produce more learning through reflection than they would through AI coaching of low-signal recordings. That bet is reversible — the recording infrastructure can be added back if Phase 2 review concludes it would have helped.

What's not reversible is the cumulative legal exposure of recording without proper consent management, or the cumulative friction of the disclosure script eating the first 15 seconds of every call.

The conservative choice (record everything, transcribe everything, coach everything) is more complex *and* more legally risky *and* generates lower-value data than the simpler choice.

## What this skill chain looks like end-state

For the operator (Sean):

```
Cold call (phonebooth dashboard)
  ↓ no recording, just notes
Lead booked discovery call (status update in phonebooth)
  ↓ schedule Google Meet
Discovery call (Google Meet — recorded by platform)
  ↓ download transcript
Save to storage/app/coaching/discoveries/{filename}.md
  ↓
Claude Desktop reads via filesystem MCP, writes coaching feedback
  ↓
Sean reads coaching, refines for next discovery call
```

Phonebooth dashboard handles the cold-call top-of-funnel; Google Meet + Claude Desktop handle the discovery-call coaching loop.

## When this was decided

Sunday afternoon, before Phase 1 build began. Sean caught the friction problem during a metacognition pass and proposed the rework after some honest self-reflection about what was anxiety-driven versus design-driven thinking.

The rework was implemented before any code was written, so there's no technical debt — the specs simply describe a smaller system.
