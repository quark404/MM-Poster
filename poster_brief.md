# Poster brief

- Paper: supplied RoboPIN PDF at `assets/paper.pdf`; venue ACM Multimedia 2026.
- Physical requirement: A0 portrait, 841 × 1189 mm.
- Latest direction: faithfully reconstruct the latest user-supplied RoboPIN AI visual mockup, including Rio art, gradients, rounded cards, icons, typography and proportions. The earlier SDO poster only supplied the initial section logic; it is superseded as the visual target.
- Layout: header → paired Motivation / Key Insight → full-width Method → paired Experimental / Qualitative Results → closing statement.
- Motivation: cross-step reference drift and reasoning–answer misalignment, amplified by cross-view changes.
- Main insight: identity-bound anchors bind name, ID, view and point throughout reasoning.
- Visual evidence: source Figures 1, 2, 3 and 4; two source camera views with the same identity.
- Quantitative evidence: 68.0 spatial, 67.9 pointing, 75.0 robot; cross-step ID coverage 18.8% → 99.9%.
- Branding: light Rio header art, original conference and TJU logos, navy text, teal-to-green rounded headers, pale blue/mint callouts and bottom waves.
- Outstanding: real QR, Track/OpenReview ID and source-paper robot-caption trial-count clarification.
- Execution: local tested renderer with Paper2Poster skill guidance; external API-based PosterAgent unexecuted.


## Latest module refinement

The user subsequently requested several iterations and better information density. Three actual variants (clean, balanced, mechanism) supersede strict mockup imitation as the immediate objective. Keep the five-panel story, source data and no-number-caption preference. Select V3 as the working main version after visual review; retain V1/V2 for user comparison. See `design/variants/README.md`.
