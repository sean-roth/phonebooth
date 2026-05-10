---
name: sops-brand
description: Brand guardrails for any SOPs Nobody Reads-branded content. Use whenever producing customer-facing copy, marketing materials, proposals, or any communication that carries the SOPs Nobody Reads name. Triggers include drafting postcards, website copy, LinkedIn posts, email templates, proposals, business card text, voicemail scripts, cold call scripts, social media bios, blog posts, conference one-pagers, or anything else where the SOPs Nobody Reads brand is visible.
---

# SOPs Nobody Reads — Brand Skill

The gate for any branded content. The marketing folder in this repo is the canonical source; this skill is the entry point that enforces consistency. When in doubt, read the linked source docs.

## The brand thesis

*A serious instructional-design product for small trade contractors who need their crews trained and their training documented — sold by a person who isn't pretending to be a safety expert, with proof-of-completion that holds up if anyone asks.*

This is the test. Every creative decision passes or fails by this sentence.

## Voice rules

- **Direct, not sales-bro.** Honest about what the call/email/postcard is. Don't manufacture rapport. Don't pretend to know the prospect.
- **Plain over clever.** First version is usually too clever. Third version is usually too formal. Fifth version is usually right. Aim for boring; cleverness will show up on its own.
- **Concrete over abstract.** "LOTO, fall protection, hazcom" beats "safety training." "About a week per topic" beats "fast." Specifics build credibility; abstractions erode it.
- **Trade-owner reading level.** The audience is a 40-something contractor with a high school diploma and 20 years of running crews. He's not stupid; he hates being talked down to or talked over. Write the way a thoughtful peer would talk to him.
- **No fake urgency.** No "limited time," no "this quarter only," no "act now." The triggers are real (GC prequal, insurance pressure, OSHA risk) and don't need manufactured pressure on top.

## Banned words and phrases

These get flagged. The list is not exhaustive — add to it as new offenders surface in real copy.

- *Solutions* (and any variant: "safety solutions," "training solutions")
- *Leverage* (as a verb)
- *Synergy* / *synergistic*
- *AI-powered* / *AI-driven* / *intelligent*
- *Robust*
- *Seamless*
- *Cutting-edge*
- *World-class*
- *Best-in-class*
- *Game-changing*
- *Revolutionary*
- *Empower* / *empowering*
- *Unlock* (as in "unlock potential")
- *Journey* (as in "safety journey" or "learning journey")
- *Ecosystem*
- *Platform* (use "app" or name the actual thing)

If a phrase pattern-matches to LinkedIn corporate-speak, it's probably banned even if it's not on this list. Sean's call.

## The slogan deployment matrix

Two slogan variants are in A/B test. Use the right one for the surface.

| Surface | Variant | Reasoning |
|---|---|---|
| Postcard front | "training with receipts" | Stopping-power; visual scan |
| Site header | "training with receipts" | Distinctive brand impression |
| Business cards | "training with receipts" | Visual, single-impression |
| LinkedIn banner | "training with receipts" | Scroll-past-able; needs to snag |
| T-shirt / booth signage | "training with receipts" | Across-the-room legibility |
| Email signature | "training that gets done" | Read repeatedly; plainness wears better |
| Cold call value statement | "training that gets done" | Verbal; needs to parse without re-reading |
| Voicemail | "training that gets done" | Verbal; same logic |

Decision date for picking one variant (week 3 of dialing): not yet. Until then, use the matrix.

Full rationale in `docs/marketing/brand-and-messaging.md`.

## Positioning rules

**You are not a safety expert.** The CSP, the insurance carrier's risk consultant, OSHA's regulations — those are the safety authorities. SOPs Nobody Reads is the *conversion layer*: it takes existing procedures and turns them into training that gets completed and documented.

When producing copy:

- Don't make claims about safety best practices.
- Don't write OSHA opinions or interpretations.
- Don't offer specific safety advice for any trade.
- Don't suggest the brand is a substitute for safety expertise.
- *Do* claim instructional design expertise, training completion improvements, audit trail integrity, and the conversion-layer thesis.
- *Do* redirect safety questions to the appropriate authority (their CSP, their insurance carrier, OSHA directly).

This is also the safer legal position. The brand doesn't carry safety content liability because the brand doesn't produce safety content — it converts the client's safety content.

## Visual brand

See `docs/marketing/design-kit.md` for the working visual identity. Summary:

- Clean B2B product aesthetic. Serious, not playful.
- Muted professional palette. **Avoid hi-vis orange, safety yellow, "construction red."** Those are exactly the cliches the brand differentiates against.
- Sans-serif typography for working drafts. No construction-themed fonts, no decorative type, no condensed industrial styles.
- No stock photos of crews in hard hats. No clipart. No mascots.
- The brand should look like a serious software product, not a contractor flyer.

If producing visual content, run it past the design kit before generating.

## Pre-publish checklist

Before producing any branded copy, run through:

1. **Does this fit the brand thesis?** If you can't map the copy back to the one-sentence thesis, rewrite.
2. **Am I claiming safety expertise?** If the copy makes a safety claim, a safety interpretation, or a safety recommendation, redirect to the appropriate authority instead.
3. **Did I use any banned words or sales-bro phrases?** Scan the copy. Remove or replace.

If the output is visual:

4. **Does the visual treatment respect the design kit?** No hi-vis, no hard hats, no construction cliches.

These four are the floor. If a piece fails any of them, it's not ready.

## Validated examples

*Reserved for copy that has demonstrably converted — a postcard that drove inbound, a LinkedIn post that pulled qualified responses, a call script segment that produced a discovery booking. Empty for now. Add as reality provides data.*

## When the brand should evolve

The brand is not yet validated by paying customers. Once 3+ paying clients exist and patterns emerge in what they responded to, the brand may sharpen or shift. Until then, don't change brand fundamentals — deploy what's here and gather data.

Signals that justify revisiting brand fundamentals:

- Multiple clients independently describing the value proposition differently than the brand thesis
- A slogan variant consistently outperforming the other across 6+ weeks of A/B data
- A consistent objection pattern in calls that the current positioning fails to address
- A new product surface (e.g., direct-to-broker offering) that needs distinct treatment

Absent these signals, the brand stays consistent and the work goes into deployment quality.

## Canonical sources

When the skill is ambiguous or a question isn't covered, read these in order:

- `docs/marketing/README.md` — marketing operating plan, layer structure
- `docs/marketing/brand-and-messaging.md` — full brand and slogan reasoning
- `docs/marketing/design-kit.md` — visual identity working notes
- `docs/marketing/direct-mail.md` — postcard production specifics
- `docs/sales/cold-call-script.md` — call language and structure
- `docs/sales/pricing.md` — pricing language and tier framing

If a question can't be resolved from these sources, ask Sean before producing copy.
