# Future Ideas — Capture Only

Ideas worth keeping but not building. One-line entries. Add as they come up.

Don't expand any of these into full specs until they earn it through manual exposure to the problem they solve.

---

## Lead generation

- **Mid-market operational intelligence skill.** When scaling up to $5M–$25M trade contractors, mine Glassdoor + Indeed + LinkedIn for training-gap and turnover signals (e.g., line-worker reviews saying "no one trained me, had to figure it out"). Different data sources, different parsing, different trigger logic than the Google Maps lead-intelligence feature. Keep separate. (Captured 2026-05-05.)

- **Consumer-facing local business signal skill.** For restaurants/gyms/retail with active social. Mine Instagram comments, TikTok replies, tagged posts for operational complaints. Same logic as Google reviews but earlier in the customer frustration arc. Not a SOPs Nobody Reads target customer; deferred. (Captured 2026-05-05.)

## Phonebooth phase 2 — observed needs from real dialing

These surfaced during the first week of manual cold calling. Capture them now; build when the manual workflow becomes the bottleneck.

- **Workflow acceleration, not parallel dialing.** The reputational risk of parallel-dialing-with-drops is real. The actual pain is dead time on rings, wrong numbers, and slow lead-to-lead transitions on a single line. The right intervention is: auto-advance to next lead after hangup, dead-number detection before the call rings at the destination, one-button "send demo" action post-call. NOT 4-line parallel dialing. (Captured 2026-05-12.)

- **502 recovery in active-call mode.** Current behavior: on 502, UI resets and the form being edited is lost. Correct for audit-trail mode (compliance product), wrong for active-call mode (cold call cockpit). Need separate recovery semantics for the two modes. Phase 2 must distinguish "active call note-taking" from "audit-trail entry" with different durability and recovery rules. (Captured 2026-05-12.)

- **In-call timer between dials.** Self-imposed countdown (5 min → 3 min → 1 min as muscle builds) creates bounded pre-call discomfort, which is tolerable in a way unbounded discomfort isn't. Currently using an external timer. In-app timer with configurable interval would be tighter UX. Optionally: timer auto-decreases over weeks as completion rates improve. (Captured 2026-05-12.)

- **Script in sidebar with inline note-tagging.** Tab-switching to read the script during a call has real cognitive cost. Embedding the script in a sidebar of the active-call view removes the friction. Bonus: let the user tag specific lines of the script during the call with one click — "felt off," "got a bad reaction," "they paused here." Notes attach to the script line for afternoon review. (Captured 2026-05-12.)

- **Gatekeeper-vs-owner pickup field.** Current call logging doesn't distinguish "owner picked up" from "gatekeeper picked up" from "voicemail" from "dead line." All four are different outcomes with different next-steps. Need a quick-tag field in the call log so this data can be analyzed across time windows (does early MT actually mean owner pickup, or just earlier gatekeeper?). (Captured 2026-05-12.)

- **Minimum viable inbound layer (WEEKEND PROJECT).** Phone is the main channel for this audience. Trade owners call back, text back, leave voicemails. Currently the 312 number is outbound-only and any inbound is lost. Scope: (1) inbound call logging — caller ID + timestamp + voicemail captured to phonebooth dashboard, (2) inbound SMS capture — texts received to the 312 number show up in phonebooth, (3) email notification when any inbound arrives. NOT in scope this weekend: real-time call forwarding to cell, unified messaging inbox UI, auto-reply on inbound SMS, transcription. Twilio webhooks + database writes. ~6–10 hours focused work. (Captured 2026-05-14 after Victor's dropped call exposed the gap.)

## Sales workflow ideas

- **Post-call demo-send automation.** After a call ends in "send me info" or "not interested but interested in demo," one-button action sends the LOTO demo email with their name pre-filled, logs the send in phonebooth, and queues a follow-up reminder. Currently doing this manually; will become a chore by call 50. (Captured 2026-05-12.)

- **Calendar booking inside phonebooth.** When a discovery call gets booked during a cold call, embedding the Calendly equivalent into phonebooth (or just a direct API integration with Calendly) eliminates the tab-switch and lets the booking happen during the call instead of after. (Captured 2026-05-12.)

- **Almost-bail tracking.** Log a separate "almost didn't dial but did" event. This is the actual training data of week 1-2 — the muscle being built is button-pressing through resistance, not call quality. Track it explicitly to see the curve flatten over weeks. (Captured 2026-05-12.)

## Sequencing rule

None of these get built before:

1. The manual workflow has exposed the actual shape of the problem (most are already there)
2. Manual workflow is genuinely the bottleneck (will become true around call 50-100)
3. The cold-calling muscle is established enough that building doesn't become avoidance

Most of phase 2 probably activates around end of week 3 or start of week 4. Not before.

**Exception:** the minimum viable inbound layer is a weekend project, not part of phase 2. It's narrow enough to scope tight, and it unblocks the next 50 calls. Don't let it expand into the larger phase 2 redesign.
