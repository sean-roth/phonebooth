# 10 — Legal Compliance: Recording Consent

## Why this exists

Illinois is an all-party consent state under 720 ILCS 5/14-2. Recording a private phone conversation without the consent of every party on the call is a felony eavesdropping offense, with criminal penalties (potential imprisonment) and civil liability (compensatory and punitive damages plus legal fees).

This spec was added late — after the Twilio recording infrastructure was already designed. The original Phase 1 design assumed recording was a build detail. It is not. It is the central legal question of the whole system, and it's fortunate the question came up before the first call was placed.

The good news: businesses record customer calls in Illinois every day. The mechanism is **implied consent through advance notification**. The standard pattern: announce that the call is being recorded, and continued participation by the other party constitutes consent. This is what every "this call may be recorded for quality assurance purposes" automated message is doing, legally.

The complication for phonebooth: AI transcription specifically has been subject to recent litigation in Illinois federal courts (2025), with plaintiffs arguing that AI analysis of recorded calls is a separate harm from recording alone. The safest practice — as advised by Illinois recording-law specialists — is to disclose both recording and AI transcription up front and get explicit verbal acknowledgment.

## The legal foundation

This spec is operational guidance, not legal advice. Sean is responsible for confirming this with a licensed Illinois attorney before placing the first call. The relevant statute is 720 ILCS 5/14-2. The relevant case shaping current interpretation is People v. Clark / People v. Melongo (Ill. 2014), which struck down the prior version of the statute on First Amendment grounds and led to the 2014 amended version that now governs.

The Engineer should not make compliance decisions. This document specifies what the system does; whether that's legally sufficient for Sean's specific use is a question for Sean and his attorney.

## The disclosure pattern

The first words spoken on every call must include three elements:

1. Identification — who Sean is and where he's calling from
2. Recording disclosure — the call is being recorded
3. AI transcription disclosure — the recording will be transcribed and analyzed by AI for training purposes

A workable script:

> "Hi, this is Sean Roth calling. Quick note before we start — I record my calls and have an AI transcribe them so I can review my conversations and improve. Is that okay with you?"

This serves multiple purposes:

- Satisfies the all-party consent requirement (explicit ask)
- Discloses AI specifically (covers the 2025 litigation territory)
- Gives the lead an out — if they say no, hang up, no harm done
- Models honesty as a sales posture (you're already not pretending; the rest of the call is easier)

Length matters. The disclosure must come before any other substantive conversation, but should not feel like a TSA security warning. Aim for under 15 seconds of clean delivery.

## The three response paths

When Sean delivers the disclosure, the lead does one of three things:

**Path A — Affirmative consent:** "Sure, that's fine" or "yeah, no problem." Recording continues. Call proceeds normally.

**Path B — Refusal:** "No, I'd rather not." Sean stops the recording, thanks them, ends the call. Marks the lead with disposition `declined_recording`.

**Path C — Hang up at disclosure:** the lead hangs up before answering. Sean marks the lead with disposition `declined_recording` (treats "no answer" of the consent question as refusal — the safest interpretation).

There is no Path D where you keep recording and hope they didn't mean it. There is no Path E where you record but don't tell anyone. The cost of getting this wrong is criminal liability and civil damages.

## What needs to change in the dashboard

### Cockpit page: visible disclosure script at top

The cockpit's lead-info section (per spec 03) must include the disclosure script as a prominent, persistent element. Not in the lead's brief. Not in a sidebar. At the top of the call screen, large enough to read while the phone is ringing.

```html
<section class="recording-disclosure" role="alert">
    <h3>READ BEFORE RECORDING</h3>
    <p class="disclosure-script">
        "Hi, this is Sean Roth calling. Quick note before we start — I record
        my calls and have an AI transcribe them so I can review my conversations
        and improve. Is that okay with you?"
    </p>
    <p class="disclosure-instructions">
        Wait for an affirmative answer before continuing the call.
        If they decline or hang up, end the call and mark disposition
        as "declined recording."
    </p>
</section>
```

This element renders even before the dialer. It is not collapsible. It is not configurable. The disclosure is the cost of using the system.

### New disposition: declined_recording

Update the disposition enum (spec 03) to include `declined_recording`. This is distinct from `not_interested` because:

- It's about the recording question, not the offer
- It's not a sales rejection
- The pattern in the data (how often this happens) is itself useful information

Disposition options become:

- `voicemail` — Voicemail left
- `no_answer` — No answer / disconnected
- `declined_recording` — Declined recording (NEW)
- `not_interested` — Not interested
- `interested` — Interested, follow up
- `discovery_booked` — Discovery call booked
- `disqualified` — Disqualified
- `wrong_number` — Wrong number
- `bad_number` — Bad number / dead line

### Pain points field rules

The pain_points-required logic (per spec 03) extends to skip on `declined_recording` along with the other no-conversation cases. You can't capture pain points if the call ended at hello.

Updated rule: pain_points required UNLESS disposition is one of: `voicemail`, `no_answer`, `wrong_number`, `bad_number`, `declined_recording`.

### Logging and events

Add a new event type: `consent_declined`. Recorded when Sean marks a call with `declined_recording` disposition. The events table thus captures the rate at which the disclosure script is failing.

Useful query for Phase 2 review:

```php
$declineRate = Event::where('event_type', 'consent_declined')->count() /
               Event::where('event_type', 'call_initiated')->count();
```

If the rate is high (say >20%), the disclosure script needs revision. The script is a hypothesis; the data tells you whether the hypothesis is right.

## What needs to change in the call flow

### Sean's behavioral protocol

Before clicking Call: read the disclosure script silently, get the words queued in your mouth.

After the lead answers: deliver the disclosure first. Do not introduce the offer, the brief, the value prop, or anything else before the disclosure. The disclosure is the gate.

Wait for a verbal response. Silence is not consent. A grunt is not consent. "Okay" is consent.

If they say yes: now you're calling. Continue.
If they say no, ask why, or sound uncertain: stop. "No problem, I appreciate you taking the call. Have a good one." End the call. Mark `declined_recording`.

If they hang up during or right after disclosure: that's a refusal. Mark `declined_recording`.

### Twilio configuration consideration

The spec 04 design has Twilio recording start automatically when the call connects (`record-from-answer-dual`). That means the disclosure itself gets recorded — including a refusal.

This is actually fine and arguably better:

- If the lead consents, the recording captures the consent itself (legal protection for Sean)
- If the lead refuses, the recording captures the refusal (Sean has documented evidence he stopped)
- Sean must immediately end the call after a refusal so no further conversation is recorded

The alternative (delay recording until consent is given) is technically more complex (Twilio's `<Dial>` doesn't easily support "start recording mid-call"), and provides less legal protection. Recommend keeping `record-from-answer-dual` and accepting that refusals are also captured.

**Important caveat:** Sean should consult his attorney on whether recording the refusal itself is acceptable in Illinois. The conservative interpretation is that you stop recording the moment consent is denied and discard everything captured before that point. The phonebooth dashboard could implement a "delete recording" action on calls marked `declined_recording`, hard-deleting the audio file and the Twilio recording.

This is the strongest legal posture and probably the right default.

### Recommended: auto-delete on declined_recording

When a call is saved with disposition `declined_recording`:

1. Delete `storage/app/recordings/{call_id}.mp3` if it exists
2. Issue a delete request to Twilio's API to remove the recording from their servers
3. Set `recording_url` and `recording_local_path` to null in the calls table
4. Record a `recording_deleted` event with the reason

```php
// In CallController::update() after save:
if ($call->disposition === 'declined_recording') {
    $this->deleteRecording($call);
    $events->record('recording_deleted', 'call', $call->id, [
        'reason' => 'declined_recording',
    ]);
}
```

Twilio API for deletion: `DELETE /2010-04-01/Accounts/{AccountSid}/Recordings/{RecordingSid}.json` with basic auth. (Verify endpoint format against current Twilio docs per spec 08 pattern.)

The Engineer should implement this even though Sean must verify legal sufficiency with an attorney.

## What needs to change in the spec set

The following specs need updates after this one is committed:

- **spec 03** — add `declined_recording` to disposition enum, update pain_points rule, add disclosure section to cockpit view, document the auto-delete behavior in CallController::update
- **spec 04** — add a note that the recording captures the disclosure itself, link to this spec
- **spec 05** — add note that processing won't run if recording was deleted
- **spec 07** — add `consent_declined` and `recording_deleted` event types
- **spec 02** — no schema changes needed (disposition is a string column, enum is enforced in validation)

These can be done as part of the next pass, or before build, or by the Engineer during build (with a commit that updates the relevant spec). Recommend before build.

## What this does NOT solve

This spec covers Illinois recording compliance for outbound business-to-business calls. It does NOT cover:

- **Multi-state calls.** If Sean dials a number in Indiana (one-party consent state), Illinois law still applies because Sean is in Illinois. But if Sean later moves to Chicago and dials a California number, California's all-party consent law applies. The disclosure pattern works for all states.
- **Inbound calls.** Phase 1 is outbound only. If Sean ever takes inbound business calls, the disclosure pattern needs to be adapted (typically a pre-call message or recorded greeting).
- **Calls to numbers that turn out to be personal cells.** Some small business owners use their personal mobile as the business line. The disclosure protects against this — you disclose, they consent or don't.
- **TCPA compliance.** Federal TCPA rules govern unsolicited business-to-business calling separately from recording laws. Sean should research TCPA requirements for cold calling before scaling. Phase 1 volume (~10 calls/day) is below most TCPA thresholds but the rules still apply.
- **GDPR / CCPA / state-specific privacy laws.** If you're storing transcripts of calls with people in California, CCPA applies. Phase 1's local-only storage on the OptiPlex is the conservative approach.
- **Do Not Call Registry.** Federal DNC rules apply to unsolicited sales calls. Business-to-business calls have some exemptions but Sean should verify before scaling.

## What Sean should do before Monday

1. **Read this document.**
2. **Talk to a licensed Illinois attorney about cold-calling compliance.** This is non-optional. The cost of a 30-minute consult is far less than the cost of a felony charge.
3. **Practice the disclosure script out loud.** It needs to feel natural. If it feels like a Miranda warning, leads will react accordingly.
4. **Decide on the auto-delete policy.** The spec recommends auto-delete on `declined_recording`. Sean should confirm with the attorney whether to keep the disclosure-and-refusal portion or delete entirely.
5. **Add the disclosure to the cockpit page during build step 3.** It is not a Phase 2 feature.

## Revising the success criteria

The "success looks like Monday at 9 AM" narrative in spec 00 needs an addendum:

> Sean clicks Call. The phone rings. Someone picks up. Before Sean introduces himself or his offer, he reads the disclosure script. The lead says "sure, go ahead." Sean continues with the call.
>
> Some calls will end at the disclosure. That data — how often, in what kinds of businesses, with what timing — is itself valuable. The disclosure is not friction; it's the system working.

## A note on emotional load

Reading the disclosure on every call is psychologically harder than it sounds. The first 5-10 calls, Sean will rush it, mumble it, or try to get through it like a TSA agent. This will increase decline rates. As Sean gets comfortable, the delivery will smooth out.

Don't let early decline rates discourage you. The first week is calibration of the script and delivery, not a referendum on the business idea.

If decline rates remain above 30% after a week, the script needs revision — try a friendlier opener, or a shorter disclosure, or invert the order ("I'm working on a project where I record my calls — happy to skip that if you'd prefer").

This is itself a Phase 2 design conversation worth having after field testing.
