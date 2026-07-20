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
