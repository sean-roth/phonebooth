# Palette — SOPs Nobody Reads

## The colors

| Role | Hex | Usage |
|------|-----|-------|
| Primary ink | `#1f3a2e` | Forest Green | Headlines, body text, primary graphic elements, the wordmark |
| Background | `#f4ede0` | Warm Cream | Page background, large surfaces |
| Accent | `#3a1f2e` | Dark Aubergine | Link color, CTA emphasis, section dividers, key callouts |
| Utility | `#6b5d4a` | Warm Gray | Captions, footers, fine print, section labels, secondary text |

**Coolors reference:** https://coolors.co/1f3a2e-f4ede0-3a1f2e-6b5d4a

## Accessibility (verified)

- Forest Green on Cream: ~10:1 contrast (exceeds WCAG AAA)
- Aubergine on Cream: ~10:1 contrast (exceeds WCAG AAA)
- Warm Gray on Cream: ~5.48:1 contrast (passes WCAG AA for body text, AAA for large text)

The contrast in this palette comes primarily from lightness differences, not hue differences. This makes the palette robust for all color vision types, including red-green colorblindness.

## How it was chosen

The palette is the product of an explicit set of decisions, each documented so future revisions know what they're changing:

1. **Restraint over decoration.** Most brands in adjacent categories (compliance, training, SaaS) use bright palettes with multiple competing colors. This palette uses few colors with discipline. The brand's personality comes from the consistency of its small set, not from accumulation.

2. **Editorial register, not corporate or jobsite.** The colors are calibrated to feel like a serious nonfiction publisher — Phaidon, NYRB Classics — rather than a software vendor or a safety company. Deep, considered, paper-adjacent.

3. **Forest green as primary.** Cool-leaning, desaturated, dark. Carries weight without performing it. Distinct from the safety industry's hi-vis yellow-orange palette and from tech's default blue. Has a long association with serious publishing, archival work, and considered craft.

4. **Cream as background.** Warm off-white that softens the green and gives the page a paper-like feel. Not pure white, which reads as digital and clinical. Not yellow enough to feel rustic or vintage.

5. **Aubergine accent, not bronze.** Initial palette explored bronze (`#8b6f3a`) as accent, but bronze sat in the same yellow-brown family as the cream and lacked contrast — the eye absorbed bronze into the background rather than reading it as a distinct accent. Aubergine sits in a different color family (purple-leaning, cool), giving it clear separation from both the green and the cream. The dark aubergine also avoids any Christmas-red association.

6. **Warm gray for utility.** A separate utility color for secondary text prevents fine print from competing with the primary content. The gray harmonizes with both the green and the cream — warm enough to belong, neutral enough to recede.

## Usage rules

**Forest green is the dominant color.** Used for type, primary graphics, the wordmark. Most of the visual weight on any page comes from green-on-cream.

**Cream is the background everywhere.** Use as the page background for all surfaces. Avoid pure white. Avoid alternate backgrounds (gray, light blue, etc.) for sections — the cream should be unbroken throughout the brand.

**Aubergine is sparing.** Should appear no more than two or three times per page. Reserve for links, primary CTAs, section dividers, or critical emphasis. If aubergine starts to feel decorative rather than functional, it's being overused.

**Warm gray is structural, not expressive.** Use for utility text only. Don't use gray for headlines or important body copy — that's the green's job.

**Color should never be the only signal for meaning.** Links must be underlined (or otherwise distinguished) in addition to being colored aubergine, so colorblind readers can identify them.

## Known watch-points

- **The landscaping risk.** Forest green is heavily used by landscaping and outdoor brands. The brand mitigates this through context — editorial typography, conceptual imagery, copy about training and procedures. If the landscaping read keeps coming up in feedback during real implementation, revisit. For now: known risk, not changing course.

- **Body text in green.** Setting body text in forest green (rather than near-black) is a stylistic choice that gives the page a unified feel but can be more fatiguing for long reading. If readers report difficulty, consider shifting body text to a very dark near-black while keeping headlines and graphic elements green.

- **Future tonal variations.** The palette as committed has no mid-tone green — no "light forest" for hover states, soft backgrounds, or subtle borders. If a real design need surfaces during implementation, a light forest green (something like `#a8b8a4` or `#9caf99`) is the natural extension. Add deliberately when needed, not preemptively.

## What's not in the palette

- No pure white. Backgrounds are cream.
- No pure black. Primary ink is forest green; accent is aubergine. Black is reserved for cases where extreme emphasis is required and the other colors can't carry it.
- No bright or saturated colors. The palette stays in dark, restrained tones throughout.
- No red. Red signals warning, alarm, or sale — none of which fit the brand.
- No blue. Blue signals corporate, institutional, or tech-vendor — also wrong for the brand's positioning.

## Application notes for the designer

Once typography is committed, the palette will be tested in real implementation:

- Homepage hero, full sections, and footer
- Module player interface
- Email signature
- Invoice and proposal templates
- Any future printed materials

The relationships between colors should remain stable across all surfaces. The discipline is that every surface feels like it came from the same place.

Adjustments are allowed — small shifts in saturation or lightness during real rendering — but the *relationships* (green dominant, cream background, aubergine sparing accent, warm gray utility) should not change.
