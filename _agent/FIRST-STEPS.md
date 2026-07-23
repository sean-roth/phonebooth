# FIRST STEPS — read this before touching anything

Written 2026-07-22, at the end of the build session that produced this folder.
It is the context the code cannot carry: why things are the way they are, what
was tried and abandoned, and what will quietly break if it gets "improved."

If you are a Claude picking this up cold: read this, then `README.md`, then
`skills/leads/SKILL.md`. That is enough to be useful in about five minutes.

---

## How this came to exist (the part that matters most)

Six months of outreach came first. Cold email underperformed. LinkedIn
underperformed. Cold calling worked. Three segments were tried in order —
trade contractors (bust), warehouses/distributors (mediocre, ~30 rejections),
property management (poor fit) — before landing on **small manufacturers**,
which is where the existing LOTO demo is finally native rather than a stretch.

Then the ICP was worked **by hand** for three batches — roughly 90 leads
sourced, curated, and reasoned about one at a time, with the keep/reject calls
argued out loud each time. Only after that was the judgment written down
(`docs/sales/lead-generation-guide.md`) and only then automated.

**That order is the lesson.** The agent is good because the ICP was validated
by hand first. Building this in January would have automated the wrong thing
beautifully. Do not automate judgment that has not yet been earned — for this
system, or for whatever comes next.

---

## Setup that actually works (three dead ends already removed)

1. **Places API (New) only.** Not the legacy Places API. The orchestrator calls
   `places.googleapis.com/v1/places:searchText`, which only works with the New
   API enabled. Legacy can no longer be enabled on new projects anyway.
2. **Billing must be attached** to the Cloud project even though usage stays
   inside the free allowance. Google will not serve place data otherwise.
3. **API key restrictions:** restrict to *Places API (New)*. Do **not** set an
   HTTP-referrer restriction — that is for browser keys and will block a
   server-side script. Leave application restrictions off, or use an IP
   restriction if the machine has a stable address.
4. **Google Sheets auth: use OAuth, not a service-account key.** A Workspace-
   backed Cloud org enforces `iam.disableServiceAccountKeyCreation` by default,
   so the standard service-account-JSON path is blocked. OAuth (Desktop app
   client ID + `gspread.oauth()`) is the working path, and is the better fit
   anyway: you authenticate as yourself, no key file on disk, no need to share
   the Sheet with a robot account. Do not "fix" this by lifting the org policy.
5. **Two different safety nets, both worth having.** A billing budget alert is
   a smoke alarm — it notifies, it does not stop anything. The actual hard stop
   is a **daily quota cap** on Places API (APIs & Services → Quotas). Set both.

The console is confusing on one point: enabling an API and creating a key are
separate pages, and every "get started" flow pushes you toward making a *new*
key. One key serves every API on the project. When in doubt, skip the console
and just curl `places:searchText` — the error text diagnoses the problem far
better than the dashboard does.

---

## Cost reality (supersedes the cost note in `orchestrator/README.md`)

Google bills per **SKU** — a billing line item, not an API. Places splits into
several, and **you are billed at the highest-tier SKU any requested field
belongs to.**

- The advertised "10K free calls per SKU" is the *Essentials* number. Pro gets
  5K, Enterprise 1K.
- Our field mask requests `nationalPhoneNumber`, `websiteUri`, `rating`,
  `userRatingCount`, and `regularOpeningHours` — all of which trigger **Text
  Search Enterprise** — plus `reviews`, which pushes it to **Enterprise +
  Atmosphere**. So the real free allowance is **1,000 searches/month**, not
  10,000.
- **Do not drop `reviews.text` to save money.** Dropping it moves you from
  Enterprise + Atmosphere down to Enterprise — *still the 1K bucket*, because
  the phone number alone triggers Enterprise, and there is no call list without
  phone numbers. You would lose the single best qualification signal (owner
  names, B2B-vs-consumer tells) for zero savings at this volume.

One `maps.search()` = one billable call returning up to 20 businesses. Six
slices a run, daily, is ~180 calls/month. Comfortably free. If you ever pass
1,000 searches in a month, the business has customers paying for it.

---

## Data hygiene (learned by getting it wrong)

- **Hand-recorded email addresses are unreliable.** Three out of three
  addresses collected by phone were wrong: a domain that did not exist, a
  domain belonging to an unrelated business, and one missing a single letter.
  Always verify a company's real domain from its own website before sending.
- **A wrong domain is worse than a bounce.** A bounce tells you. A valid domain
  belonging to someone else swallows the email silently.
- **Company names are not unique.** Two unrelated businesses shared a name in
  different states; the website found by name search was the wrong company.
  Match on name *and* phone/address before trusting a lookup.
- **Check a contact's role before treating them as the buyer.** A friendly
  "Client Success" contact at a distributor serves that company's *customers*,
  not its own staff — courteous, but not the training decision-maker. The buyer
  is the owner, plant manager, or ops lead.
- **A late follow-up does not need an apology.** If they asked for information,
  send it plainly; drawing attention to the delay is worse than the delay.

---

## Design principles (do not undo these)

- **Code orchestrates; the model judges one lead at a time.** Sourcing, dedup,
  scrubbing, and output are deterministic Python. Sonnet is called once per
  surviving lead and returns strict JSON. Letting a model chain the tool calls
  is where this class of system gets flaky and expensive.
- **Keep the tool surface tiny.** Two Maps tools, one Firecrawl tool. Thirty
  available tools makes any model pick wrong.
- **The dedup store is load-bearing, not a nice-to-have.** Repeated sweeps over
  the same corridors will drown in duplicates within weeks without it. Rejects
  are remembered too, so non-fit shops are never re-qualified.
- **The review pile stays short.** It is the human-judgment queue. If it grows,
  the prompt needs tightening — not the human's patience.
- **The agent never calls anyone.** It sources and filters. Full stop.
- **Every layer is earned by stress in the machine.** See `ROADMAP.md`. A CRM
  before the spreadsheet hurts is the build-instead-of-dial trap wearing a
  roadmap costume.

---

## Strategy context a future conversation should not re-derive

Full version in `strategy/sales-strategy.md`. The short list:

- **Calling is the channel.** Proven against email and LinkedIn.
- **50–200 employees is the band.** Big enough to have turnover and budget,
  small enough that the owner decides and there is no training department.
- **The demo is native to manufacturing.** OSHA 1910.147 (lockout/tagout) is a
  production-floor standard. This is *why* manufacturers, not a coincidence.
- **Plain language, no idioms.** Many owners speak English as a second
  language. "Full freight," "up to speed," "looks like your floor" all had to
  be cut. Short sentences survive a bad phone connection and an accent on
  either end.
- **Never apologize for being new.** "You'd be one of my first customers" is
  the *reason for the pilot price*, not a confession. Lead with the demo.
- **Say "onboarding" and "module," never "training."** Training implies Sean
  shows up to teach the staff. The product is slides a new hire clicks through
  on a device, with a trainer checking understanding afterward.
- **Calling infrastructure shapes strategy.** One Chicago number covers the
  whole Midwest coherently. Starlink jitter cannot be engineered away on this
  setup, so **real discovery calls go native cellular**, off the internet
  entirely. Cold dials can ride VoIP where a rough call is cheap.

---

## Known limits — what to watch on the first live runs

- **This pipeline is young.** The architecture is right; it has not been beaten
  on. Expect surprises in API response shapes, rate limits, and retries. Those
  are hardening, not redesign.
- **Sonnet is roughly 90% as precise as hand-curation.** Hand-picking caught
  subtleties like a company named "Residential" that is actually B2B, or a
  machinery dealer hiding among molders. At volume that is an acceptable trade:
  a wasted dial is cheap, and the call itself filters. Expect slightly noisier
  lists than the hand-built batches.
- **Corridors mine out.** When a slice returns mostly duplicates and sub-50
  shops, it is marked worked-out and the queue advances. Chicago then Detroit
  is months of runway; the wider Midwest is rows added to `sweep-matrix.md`.
- **Never source faster than one caller can dial.** Backlog is wasted compute.

---

## The prime directive, restated

This system exists so Sean spends more hours on the phone with Midwest
manufacturers. Every layer must remove friction from that. Nothing here is
finished work worth admiring — it is scaffolding around the only activity that
generates revenue, which is the call.

The next thing to build is whatever the calling reveals. Not before.
