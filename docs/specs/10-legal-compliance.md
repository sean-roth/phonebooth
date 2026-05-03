# 10 — REMOVED: Legal Compliance for Cold-Call Recording

## This spec is intentionally empty

Earlier drafts of this spec described Illinois recording-consent compliance for cold calls: a disclosure script displayed on the cockpit page, a `declined_recording` disposition, and auto-deletion of recordings when consent was refused.

That entire compliance pattern was removed by spec 11 (recording pivot).

## Why

The phonebooth dashboard no longer records cold calls. Without recording, there's no consent obligation in phonebooth itself.

Discovery calls happen in Google Meet, where the platform handles recording consent natively (Meet displays a recording indicator to all participants when recording is active, which constitutes legal notice + implied consent under Illinois law).

## What replaced it

For cold calls: nothing — the legal exposure is removed by removing the recording.

For discovery calls: rely on Google Meet's built-in recording indicator. The framing to the lead is mutual benefit: "we'll both have notes and a reference point as we work."

## Still recommended

Sean should still consult a licensed Illinois attorney about cold-calling compliance generally. Outbound cold calling has its own regulatory considerations — TCPA, Do Not Call Registry, state-specific telemarketing laws — that are separate from recording-consent law. The original spec's recommendation to consult an attorney before placing the first call still stands; the topic of the consultation has just narrowed.

The original spec content, including the disclosure script template and the auto-delete implementation guidance, can be recovered from git history if a future Phase 2 conversation reintroduces cold-call recording.
