> ## ARCHIVED 2026-08-13 — reference only. This document no longer governs.
>
> **Where v0 scope lives now:** `sean-roth/snr-app` — `docs/DECISION-2026-08-13-adrs.md`
> (Sean's rulings) and `docs/TECH-PROPOSAL.md` ADR-8 (build order). Those arrive on
> `main` via snr-app PRs #7 and #2; until they merge, read them on their branches.
>
> **Why archived rather than corrected.** Sean, 2026-08-13: *as we build, the plans must
> meet reality, and that rarely looks the same later.* This document is not wrong for
> having aged. It was wrong for still being cited as governing while it aged — both
> `snr-app/KICKOFF.md` and `snr-app/ARCHITECTURE.md` routed v0 scope through it. Keeping
> the thinking and removing the authority is the honest split.
>
> **What had gone stale.** The "Behind the curtain (do not build)" list below was written
> on 2026-07-20. On 2026-07-22 Sean ruled that SNR is "an app with a lot of service,"
> resolving scope per the **dual rule**: build client-facing surfaces **plus whatever makes
> the service fast**; every other layer waits until it is needed. Read plainly against that
> ruling, the list below forbids the entire v0 Runner — including the gate console, which
> is the single highest-evidence requirement in the record (four publish-before-review
> failures, escalating). That contradiction is why this file needed a ruling rather than
> an edit.
>
> **What carried forward, still true.** The Wizard-of-Oz principle. The interview as the
> one real build. Ownership as a feature — they can always leave whole. One shared,
> one-place-steerable chrome. Metering API spend per delivered module from day one so
> pricing is set on data. The exit test: run LOTO through the container as client zero.
>
> Left otherwise unedited below, deliberately. An archive that gets tidied stops being
> evidence of what was thought at the time.

---

# App v0 scope — the container, not the product

STATUS: DRAFT (2026-07-20). This gates the founding-customer offer. Live sales
doctrine (`dm-call-script.md` v1.1, $3,500 pilot) is unchanged until the exit
criteria at the bottom pass.

## Principle
The standards and prompts are the product; the app is the container. v0 builds
ONLY what a client touches. Everything else is Sean behind the curtain running
the existing Claude Code pipeline. Wizard-of-Oz rule: if the client never sees
it, do not build it.

## What the client touches (build these)
1. **Intake.** A page to drop documents (PDF / docx / photos of the binder)
   and name the module they want first. Nothing clever — a dropbox and a form.
2. **The interview.** The one real build in v0, because it is the product's
   soul and the one thing that cannot stay Sean at scale. An AI-driven
   interview the owner and the senior operator each sit with. Encodes the
   interview doctrine: it drives the conversation, stays on the work, casts
   from the Q3 who-barrel, and produces a transcript that becomes a frozen,
   citable source under the Durability Standard.
3. **Review.** Client views the draft module in the existing player and
   leaves feedback. Alpha-grade is fine: a feedback box per module. Their
   feedback is part of the alpha's price.
4. **Delivery.** A hosted course URL on shared chrome + a download button
   (plain HTML zip; SCORM via the existing scorm-builder). Ownership is a
   feature: they can always leave whole — their documents, their training.

## Behind the curtain (do not build)
Source qualification, script writing, slide decomposition, image generation,
QA passes, packaging — the existing skills, run by Sean. Also NOT in v0:
accounts, billing automation (invoice by hand), dashboards, template
libraries, analytics, self-serve onboarding.

## Pulls forward
The one-place-steerable chrome (2026-07-20 principle: a course steers
course-wide from one place). Hosted courses on ONE shared chrome means a bug
fix or a client-wide style change lands once, not per module. Do it as part
of delivery, not after — it is the same property the app needs anyway.

## Cost discipline
Images are the marginal cost. Meter API spend per delivered module from day
one (Replicate + Anthropic, logged per module) so beta pricing is set on
data, not vibes.

## Exit criteria (v0 is done when)
A founding customer can go intake → interview → draft → feedback → delivered
without Sean writing code mid-client. Sean's hands on the content are
allowed; Sean's hands on the machinery are not. First test: run LOTO through
the container as client zero.
