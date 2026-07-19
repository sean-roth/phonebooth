# Sales strategy — context for strategy conversations

Start a new strategy chat by pointing it here. This is the standing context for
how SOPs Nobody Reads sells, what's been learned, and where things stand — so a
fresh conversation doesn't re-derive six months of hard-won judgment.

## The company, in a sentence
Turn a Midwest manufacturer's own procedures into onboarding a new hire works
through on a device (slides + a trainer checking understanding), sold as a
$3,500 pilot module. Founder: Sean, from Michigan, now in Colorado, building
this for the industrial heartland he is from.

## The funnel
Source (this agent) -> cold call -> discovery (4 questions) -> $3,500 pilot ->
build & deliver (~2 weeks) -> paid -> expand. The decision-maker call doctrine
(opener, two-gear discovery, the four questions) is `dm-call-script.md`; the
after-the-yes runbook is in `docs/` and Google Drive.

## What six months taught us (don't relearn these the hard way)
- Channel: calling beats cold email and LinkedIn for this segment. Email and
  LinkedIn were tried first and underperformed. Calling is the channel.
- Segment: manufacturers are the best fit — the LOTO demo (OSHA 1910.147) is
  native to a production floor. Warehouses were mediocre; property management
  was a poor fit (LOTO didn't translate, no in-house training pain).
- Size: 50–200 employees is the sweet spot — big enough to have turnover and
  budget, small enough that the owner/plant manager decides and there is no
  training department. Larger shops have in-house people who make training.
- Product language: say "onboarding"/"module," never "training" (implies Sean
  shows up to teach). Lead with the demo, never apologize for being new; frame
  "one of my first customers" as the reason for the pilot price.
- Voice: plain, short sentences and no idioms — many owners speak English as a
  second language. No costume words (AI, blockchain, SCORM, LMS, "compliance,"
  "platform," "solution").
- Data hygiene: hand-recorded emails are unreliable; verify a company's domain
  from its real website before sending. Match a contact's role before assuming
  they're the buyer.

## Calling infrastructure (constraints that shape strategy)
- One number for everything: cold dials AND discovery calls go out on the Mint
  cellular number. A single Chicago number reads as a coherent regional
  business across the whole Midwest, and native cellular keeps every call off
  the Starlink connection (bad jitter, can't be wired to the calling machine).
- At volume, watch the Mint line for "Spam Likely" labeling — that is the
  trigger for a VoIP + number-rotation layer, not before. Registering the
  number with the free caller registries (First Orion, TNS, Hiya) lowers the
  mislabeling risk in the meantime.

## Current state (update this as it changes)
- Territory: Chicago metro first, then Detroit. (See `skills/leads/sweep-matrix.md`.)
- System of record: the SNR-Cold-Call-Tracker Google Sheet. No CRM yet — by
  design (see `../ROADMAP.md`; CRM comes only when the spreadsheet hurts).
- Lead gen: transitioning from hand-built batches to the Sonnet agent in
  `skills/leads/`.

## Pointers
- Decision-maker call doctrine: `dm-call-script.md`
- Governing ICP & exclusions: `docs/sales/lead-generation-guide.md`
- Product/voice facts: "SOPs — Canonical Facts" (Google Drive)
- Call scripts, runbook: `docs/` + Google Drive
- Build order: `../ROADMAP.md`
