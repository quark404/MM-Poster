# Layout brief

## Grid and hierarchy

A0 portrait, 841 × 1189 mm. Outer horizontal margin 30 mm. White background; navy title; one teal accent. Four full-width sections follow a single top-to-bottom reading order. Section headings use small unboxed indices and thin horizontal rules, avoiding repeated dashboard-style cards.

1. Header, y 15–179 mm: wordmark / full paper title left, official conference and TJU logos right, authors and venue beneath.
2. Main visual, y 197–493: original Figure 1 left crop, 484 mm wide at x 30, with the source aspect ratio preserved. A navy explanation panel at x 546 presents the persistent-anchor concept in two linked steps.
3. Method, y 516–775: original Figure 2 upper pipeline, 761 mm wide at x 40. Editable SFT → CoT-SFT → RFT strip beneath it.
4. Results, y 797–1005: three equal-width grouped charts. All share a 0–100 axis; baseline colours are muted blue-grey; RoboPIN alone uses saturated teal. The plotting area is 94 mm high. Model names, values and aggregation captions remain explicit.
5. Evidence and close, y 1020–1184: robot image left; per-task successes and cross-step identity coverage centre; labelled QR placeholder right; contact footer.

## Content budget

Keep the hero image obvious. Original figure labels supply the detailed comparisons; surrounding copy explains one concept rather than repeating every cell. Detailed per-benchmark tables move to `SOURCES.md` because the aggregate charts already provide the visual comparison requested by the user.

## Style configuration

`assets/poster.yaml` stores both supported upstream fields and a namespaced `robopin` block consumed by the local renderer. The local renderer controls exact coordinates and A0 dimensions. Upstream PosterAgent's automatic layout would require another proof before publication.
