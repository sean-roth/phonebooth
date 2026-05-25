# Image Prompts — SOPs Nobody Reads

Generation-ready prompts for every image referenced in the homepage and segment pages. These are designed for Seedream 4.5 on Replicate but should work with similar adjustments on Nano Banana 2 or other capable models.

## Prompt anatomy

Each prompt has six required elements:

1. **Stylistic reference** — anchors the editorial illustration tradition
2. **Subject description** — concrete description of what's in the frame
3. **Composition** — viewing angle, spatial relationships, where elements sit
4. **Palette** — brand hex values or close color descriptions
5. **Anti-instructions** — what to exclude (photorealism, texture, decoration)
6. **Tonal close** — restates the intended feeling

The prompts here vary slightly in length depending on subject complexity, but all six elements appear in every prompt.

## Visual vocabulary across pages

A consistent grammar runs through the imagery so the brand reads as one system:

- **Scene 1 of each segment page** shows a state of disorder, tangle, drift, or unresolved condition — the problem before the training
- **Scene 2 of each segment page** shows a rectangular shape (representing a screen, tablet, page, or document) with structured marks — the training intervention
- **Scene 3 of each segment page** shows a resolved or coherent state — the same elements from Scene 1 now in order

This pattern is intentional. The visitor reads imagery left-to-right or top-to-bottom and absorbs the brand's value proposition without needing to read the captions. The recurring "rectangular form with structured marks" in Scene 2 of every segment page becomes a visual signature for *the training itself.*

## The brand palette in prompts

The brand uses four colors. When prompts reference colors, they should use these specific values or close descriptive equivalents:

- Forest green: `#1f3a2e` — described as *deep forest green* or *cool dark green*
- Cream: `#f4ede0` — described as *warm cream* or *off-white*
- Aubergine: `#3a1f2e` — described as *dark aubergine* or *deep purple-brown*
- Warm gray: `#6b5d4a` — described as *muted warm gray* (for fine details if needed)

Seedream interprets hex values reasonably well but sometimes drifts. The descriptive equivalents are backup.

## Generation workflow

When producing these images for the build:

1. Run the prompt as written
2. Generate 2-4 variants per prompt (Seedream can produce variation through seed changes)
3. Curate against the brand criteria: reductive composition, no decoration, palette adherence, single conceptual idea
4. Reject the majority. Expect 1 in 4 or 1 in 5 to be brand-coherent on first generation.
5. Refine prompts based on what the model is and isn't honoring. Some Seedream tendencies (slight painterly quality, decorative flourishes) need explicit anti-instructions.

The discipline of rejection is what creates a consistent visual library rather than a stream of AI outputs.

---

# Homepage Images

The homepage has four image slots: hero, section 2 (the materials exist), section 3 (the real question), and section 4 (what the work is). Each should establish the brand's tone independently and form a small visual progression down the page.

## Hero image

**Slot:** Top of homepage, above the headline *Custom training, made for how the work actually happens.*

**Conceptual job:** Establish the brand's tone before any reading begins. Should feel considered, calm, slightly weighted with craft. Not literal training imagery; abstract enough to set mood without illustrating the offering.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A single thread, deep forest green, crossing a warm cream background from left to right. Near the center of the composition, the thread passes through itself in a small, carefully tied knot — the kind a sailor or weaver would make to join two ends together with intention. The thread is rendered in flat graphic shape, no shading or gradient. A soft dark aubergine shadow falls beneath the knot, suggesting depth and weight without realism. Restricted palette of three colors only: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). No photorealism. No texture or grain. No painterly brushwork. No decorative elements. The image should feel like a New Yorker spot illustration about something carefully connected — considered, archival, quiet. Editorial restraint throughout.

**Notes:** This is the most important image in the brand. The thread-and-knot motif carries the deeper essence — transmission of knowledge as something that must be deliberately tied together. If the first generation doesn't land, prioritize iteration here.

## Section 2 image — "The materials exist. They go unused."

**Slot:** Adjacent to or below the section 2 copy about procedures that get ignored.

**Conceptual job:** Convey *transmission attempted but not received.* Documents exist, knowledge exists, but the bridge between document and reader has failed.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. Two flat rectangular shapes on a warm cream background, representing pages or documents. The shape on the left contains a tight grid of small forest green marks — abstract suggestions of text, not readable letters. The shape on the right is empty, the same color as the background, almost invisible. Between the two rectangles, a thin dark aubergine line attempts to connect them but breaks partway across — the line is present but incomplete. Restricted palette of three colors only: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes, no texture, no painterly brushwork, no realism. The image should feel like a New Yorker spot illustration about something that should have been transmitted but wasn't. Considered, restrained, slightly melancholy.

**Notes:** The *broken line* is the load-bearing element. If Seedream produces a fully connected line, the image misses the point. May require explicit prompt iteration to get the "incomplete connection" right.

## Section 3 image — "The real question is whether the crew actually knows."

**Slot:** Adjacent to or below the section 3 copy about comprehension as the real question.

**Conceptual job:** Suggest *interior structure made visible.* The image should evoke understanding the inside of a thing, not just its surface.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A single object rendered in cross-section view on a warm cream background — the object is abstract, not a specific tool or device, but shows its interior structure. Outer shell rendered in deep forest green. Interior cavities and components shown as dark aubergine outlines, revealing how the object is constructed. The cross-section should feel like a page from a vintage technical manual or field guide. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no shading, no texture, no painterly brushwork, no realism. The image should feel like a New Yorker spot illustration about understanding the inside of a thing — considered, archival, slightly diagrammatic.

**Notes:** The object can be ambiguous — it doesn't need to be a specific recognizable thing. Slight ambiguity is preferable because the brand serves multiple segments and the image shouldn't lock into one trade's vocabulary.

## Section 4 image — "What the work is."

**Slot:** Adjacent to or below the section 4 copy about the practice's translation work.

**Conceptual job:** Show *transformation between two states.* Dense becoming organized, closed becoming open, raw becoming refined.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A horizontal composition split into two halves on a warm cream background. The left half shows a dense, chaotic block of forest green marks — small shapes clustered tightly together with no clear order, suggesting unorganized information. The right half shows the same number of marks but now arranged in a clean constellation pattern, with breathing room between them and a subtle structure connecting them — the same content, transformed into legibility. Between the two halves, a thin dark aubergine arrow or line indicates the direction of transformation. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism. The image should feel like a New Yorker spot illustration about something being reorganized. Considered, archival, intentional.

**Notes:** This is the most explicitly *brand-defining* image because it visualizes what SOPs Nobody Reads actually does (transformation, not addition). The before-and-after composition should be clearly readable in one glance.

---

# Contractor Page Images

The contractor page's three scenes show the journey from *new hire confused, best worker burdened* through *training accessed on tablet* to *better questions, work proceeding.*

## Contractor Scene 1

**Conceptual job:** Show *questions piling up with no clear path through.* The new hire's confusion as a visual state.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A tangled thread or line, deep forest green, knotted and confused on a warm cream background. The tangle is dense in the upper portion and trails off without resolution toward the bottom edge of the frame. The thread crosses itself multiple times in irregular knots. A faint dark aubergine shadow suggests slight depth. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism. The image should feel like a New Yorker spot illustration about confusion without resolution. Restrained, slightly melancholy.

## Contractor Scene 2

**Conceptual job:** Show *the training as ordered, accessible structure.* The tablet/training as the intervention.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A single clean rectangular shape on a warm cream background, representing a tablet or screen viewed straight on. The rectangle is filled with structured forest green marks arranged in a clear sequence — small shapes in tidy rows, suggesting organized procedure steps without being readable text. A few elements are highlighted in dark aubergine to suggest important details. The rectangle has subtle dark aubergine borders or corners. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism, no actual readable text. The image should feel like a New Yorker spot illustration about organized information. Considered, restrained, useful.

## Contractor Scene 3

**Conceptual job:** Show *resolution and order.* The tangle from Scene 1 now coherent and intentional.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A thread, deep forest green, traveling cleanly across a warm cream background from left to right. At one point along its path, the thread passes through itself in a single deliberate knot — clearly tied with intention, the kind a master craftsman would make. Beyond the knot, the thread continues smoothly toward the right edge. A soft dark aubergine shadow falls beneath the knot. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism. The image should feel like a New Yorker spot illustration about connection made deliberate. Calm, resolved, intentional.

**Notes on the contractor page set:** The three scenes form a clear narrative — tangle, intervention, resolution. The same green thread appears in Scene 1 and Scene 3, evolving from chaos to order. This is the most narratively explicit segment page in terms of imagery and serves as the visual template for the others.

---

# Property Manager Page Images

The property manager page's three scenes show *the maintenance worker approaching a tenant's door,* *reviewing the procedure and the protocol,* and *leaving the unit better than found.*

## Property Manager Scene 1

**Conceptual job:** Suggest *the moment of arrival at someone's home.* Anticipation, the boundary between outside and inside, the weight of being about to enter a private space.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A single flat rectangular shape on a warm cream background, rendered in deep forest green, representing a closed apartment door viewed straight on. The door has subtle dark aubergine details suggesting a doorknob and a small contact point — a knock-mark or a doorbell shape — at the right height. A faint dark aubergine shadow falls to one side, suggesting the door is solid and present in space. The composition is centered, with generous breathing room around the door. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism. The image should feel like a New Yorker spot illustration about a threshold — the moment before entering. Considered, restrained, slightly weighted with anticipation.

## Property Manager Scene 2

**Conceptual job:** Show *the procedure and the interaction protocol displayed in parallel.* Two streams of training, both accessible at once.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A single rectangular shape on a warm cream background, representing a phone or tablet held in viewing position. The rectangle is divided into two parallel vertical columns. The left column contains structured forest green marks in tidy rows, suggesting the technical procedure steps. The right column contains a different set of marks — same color, slightly different rhythm and grouping, suggesting the human interaction protocol. The two columns are clearly distinct but harmoniously aligned. Subtle dark aubergine borders or corners on the rectangle. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism, no readable text. The image should feel like a New Yorker spot illustration about two kinds of preparation happening at once. Considered, useful, dignified.

**Notes:** The two-column structure visualizes the brand's claim that the training covers *both* the technical and the interpersonal. The image is doing real conceptual work here, not just decoration.

## Property Manager Scene 3

**Conceptual job:** Show *the threshold crossed cleanly.* The door from Scene 1 now open, the work complete, the unit left in better shape than found.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. The same flat rectangular shape from the previous door scene, now rendered slightly differently — the door is open, revealing a clean dark aubergine threshold or interior edge beneath. The door itself remains in deep forest green. A subtle indication of light or space beyond the threshold. The composition retains the centered, generous spacing of the closed-door version. A faint dark aubergine shadow falls to one side. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism. The image should feel like a New Yorker spot illustration about a threshold cleanly crossed — calm, resolved, dignified. The work was done well.

**Notes on the property manager page set:** The before/after of the same door (closed in Scene 1, open in Scene 3) creates a satisfying visual rhyme that mirrors the textual narrative. Scene 2 sits between as the moment of preparation.

---

# Warehouse Page Images

The warehouse page's three scenes show *the small error easily missed,* *the new worker reviewing the items side by side,* and *the line corrected, errors caught before they ship.*

## Warehouse Scene 1

**Conceptual job:** Show *a small error in an otherwise orderly system.* The kind of mistake that's easy to miss because it looks almost right.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A horizontal sequence of small forest green marks arranged in a clean line on a warm cream background — small squares or circles in tidy progression, suggesting items moving through a process. One mark in the middle of the sequence is subtly different — slightly tilted, or in a slightly off shade of dark aubergine instead of green, or slightly larger. The difference is small enough to be easily missed at a glance. The composition is clean and horizontal. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism. The image should feel like a New Yorker spot illustration about a small wrong note in an otherwise correct pattern. Restrained, attentive, slightly disquieting.

**Notes:** The *subtlety of the error* is the key. If the wrong mark is too obvious, the image fails. If it's too subtle to detect, also fails. Iterate until the error is clearly present but easily missed.

## Warehouse Scene 2

**Conceptual job:** Show *the two confusable items displayed side by side.* The training as the moment of clarification.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A rectangular shape on a warm cream background representing a phone or tablet screen. The rectangle contains two small forest green shapes side by side, each one rendered with slightly different proportions or markings — clearly distinct when shown together, but similar enough that they could be confused individually. Subtle dark aubergine labels or markers below each shape. The composition is clean, didactic, almost like a diagram in a reference book. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism, no readable text. The image should feel like a New Yorker spot illustration about distinguishing two similar things. Considered, useful, clarifying.

## Warehouse Scene 3

**Conceptual job:** Show *the line corrected.* The sequence from Scene 1 now consistent, the small error from earlier resolved.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A horizontal sequence of small forest green marks arranged in a clean line on a warm cream background, identical in spacing and rhythm to the earlier wrong-mark scene — but now every mark is consistent and correctly aligned. The previously off mark in the middle is now matching the rest. A subtle indication that the correction was made deliberately — perhaps a small dark aubergine highlight near the formerly wrong mark, suggesting awareness and attention. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism. The image should feel like a New Yorker spot illustration about a pattern restored. Calm, intentional, accurate.

**Notes on the warehouse page set:** The before/after of the same horizontal sequence (one wrong mark in Scene 1, all correct in Scene 3) creates the same visual rhyme as the property manager page's door imagery. The pattern of "show the problem, show the intervention, show the resolution as a visual echo of the problem" is consistent across segment pages.

---

# Manufacturer Page Images

The manufacturer page's three scenes show *the procedure degrading across generations,* *the canonical version captured in writing,* and *the standard restored.*

## Manufacturer Scene 1

**Conceptual job:** Show *a pattern degrading across iterations.* Knowledge passed informally from one person to the next, losing precision at each step.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A vertical sequence of small forest green marks on a warm cream background — perhaps four or five iterations of the same simple shape stacked from top to bottom. Each iteration is slightly less precise than the one above it: small distortions, slight asymmetries, edges becoming less crisp as the sequence descends. The progression is subtle but unmistakable when viewed as a whole — the same shape, slowly losing fidelity. A faint dark aubergine indication of direction (a downward arrow or simple line) suggests the temporal progression. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism. The image should feel like a New Yorker spot illustration about something slowly degrading. Restrained, slightly mournful, attentive.

**Notes:** This is the most conceptually demanding image in the segment pages because it visualizes *drift* — a process happening across time. The degradation has to be visible but not exaggerated. Iterate to get the right level of subtle decay.

## Manufacturer Scene 2

**Conceptual job:** Show *the canonical version captured cleanly.* The procedure rendered correctly, available as a reference.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A single clean rectangular shape on a warm cream background, centered in the composition, representing a page or document. The rectangle contains a precise forest green shape — a clean, careful rendering of the same form that appeared distorted in the previous scene, now shown as it should be. The shape is rendered with confident, deliberate lines. Subtle dark aubergine markings around the rectangle suggest annotations or notation — small marginal indicators of correctness. The composition is calm, almost reverent. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism. The image should feel like a New Yorker spot illustration about something captured correctly — a master copy, an authoritative reference. Calm, careful, definitive.

## Manufacturer Scene 3

**Conceptual job:** Show *the standard restored across iterations.* The degrading sequence from Scene 1 now consistent and matching the canonical form.

**Prompt:**

> Editorial illustration in the tradition of Christoph Niemann. A vertical sequence of small forest green marks on a warm cream background, identical in spacing to the earlier degrading-sequence scene — but now every iteration is consistent and matches the canonical form from the previous scene. The shape is the same at the top of the sequence as at the bottom; no distortion accumulates. A subtle dark aubergine indicator of direction (a downward arrow or simple line) shows that this is still a temporal progression — but the progression no longer degrades. Restricted palette: deep forest green (#1f3a2e), warm cream (#f4ede0), dark aubergine (#3a1f2e). Flat graphic shapes only, no texture, no painterly brushwork, no realism. The image should feel like a New Yorker spot illustration about a pattern that holds. Calm, durable, stable.

**Notes on the manufacturer page set:** The before/after of the vertical sequence (degrading in Scene 1, stable in Scene 3) creates the segment's visual rhyme. The introduction of the canonical reference in Scene 2 is what makes the difference between the two states — the training as the *master copy* that prevents drift.

---

# Generation order recommendation

When producing these for the build, work in this order:

1. **Homepage hero first.** This is the single most important image. Iterate until it lands. The hero establishes the brand's visual signature; everything else should feel coherent with it.

2. **Section 4 image (the transformation).** This is the brand's most defining conceptual image. Getting it right confirms that Seedream can handle the brand-essential transformation imagery.

3. **Contractor Scene 1, 2, 3 as a set.** The contractor page is the most pressure-tested segment and the visual narrative is clearest. Use this set to establish the segment-page visual grammar.

4. **Property manager Scene 1, 2, 3.** The door imagery is distinctive and worth getting right; once these land, the segment-page system feels established.

5. **Homepage sections 2 and 3.** Less critical than the hero and section 4; can wait until the segment grammar is settled.

6. **Warehouse and manufacturer scenes.** Apply the established grammar to the remaining segments. By this point, the brand's visual vocabulary is locked in and these should generate with less iteration.

## Estimated generation cost

At current Seedream pricing on Replicate (~$0.05 per image), and assuming 4 generations per slot to get one keeper:

- 16 image slots × 4 generations = 64 total generations
- 64 × $0.05 = approximately $3.20 in compute

This is the cheapest part of the brand build by an order of magnitude. The expensive part is the curation discipline.

---

# What this document is not

This is not a static reference. As you generate images and learn what Seedream does well and where it drifts, the prompts should be refined. After producing the homepage hero, update this document with what you learned — what worked, what needed adjustment, what anti-instructions had to be added. The document is a working tool for the build, not a finished spec.
