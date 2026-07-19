# Roadmap — each layer earned by stress in the machine

Governing rule: **every stage is unlocked by a bottleneck you can feel, not by
a date or a plan.** Each layer removes friction from the human work. If a stage
isn't solving a pain you're actively feeling, it's the build-instead-of-dial
trap wearing a roadmap costume. Skip it.

## Stage 1 — Lead agent → spreadsheet (NOW)
Scheduled script: sweep the Chicago-then-Detroit queue, source from Maps,
dedup, qualify with Sonnet, scrub dead numbers, append keepers to the Google
Sheet in tracker format. Ambiguous → short review pile.
- System of record: the spreadsheet. Nothing fancier.
- This is months of runway. Do not build past it until something below
  actually hurts.

## Stage 2 — CRM (Twenty), WHEN THE SPREADSHEET HURTS
Trigger: you're tracking multiple touches per lead and follow-ups start
slipping — you can feel the spreadsheet straining to hold the funnel's state.
- Twenty CRM on the local server (the 32GB box handles it).
- The lead agent feeds Twenty instead of the Sheet.
- Not a day before that pain is real. A CRM with nothing moving through it is
  just a nicer place to store leads you haven't called.

## Stage 3 — Follow-up layer, WHEN THE MIDDLE OF THE FUNNEL CLOGS
Trigger: dialing at volume; the bottleneck moved from "finding shops" to
"following up with the interested ones."
- Reminders / sequencing for warm leads.
- Email drafting off the existing templates (the Alice / Hong Thai format).
- On top of the CRM, not instead of it.

## Stage 4 — Proposal generation, WHEN YOU'RE CLOSING ENOUGH TO FEEL IT
Trigger: enough pilots closed to know what actually converts.
- Proposals from a repeatable template.

## Territory expansion — threaded through all stages
Chicago → Detroit → (only when those genuinely thin) Milwaukee, Grand Rapids,
Cleveland, Akron, Rockford, Fort Wayne, Toledo, Columbus, Cincinnati,
Indianapolis. Just rows added to the sweep matrix.

## Anti-goals (do NOT build these)
- A CRM before the spreadsheet hurts.
- Multi-channel outreach automation (email blasts, LinkedIn bots) — calling is
  the channel; six months proved it.
- A "full database" / warehouse — SQLite dedup is enough until thousands/week.
- Anything that sources faster than one caller can dial. Backlog is wasted
  compute.
