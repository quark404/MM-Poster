# Sources and editorial notes

## Conference requirements — checked 2026-10-24

1. ACM Multimedia 2026, Paper Presenters Guidelines:
   <https://2026.acmmm.org/site/paper-presenters-guidelines.html>
   Exact requirement: “Posters are to be prepared in portrait A0 format.”
2. ACM Multimedia 2026, Poster Printing Service:
   <https://2026.acmmm.org/site/poster-printing-service.html>
   Exact requirement: “The file must be submitted in PDF format and sized exactly A0 (841 mm × 1189 mm), portrait orientation.”
   Filename: `ACMMM2026_Poster_Track_OpenReviewID.pdf`.
3. Conference homepage: <https://2026.acmmm.org/> confirms Rio de Janeiro, Brazil, November 10–14, 2026.

HTML copies of the pages used are retained in `assets/`. No conference submission or printing order has been placed. The logo placeholders have been replaced with official assets matching the user's supplied designs; only the paper/code QR remains a placeholder.

## Official logo assets — added 2026-10-24

- `assets/mm-logo.png`: unmodified conference logo from <https://2026.acmmm.org/assets/LOGO-ACM-2026-V2.png>, linked by the official conference header. It uses the same multicolour MM / Rio de Janeiro artwork as the user's supplied image.
- `assets/tju-logo.png`: unmodified blue circular university seal linked in the official Tianjin University identity page <https://www.tju.edu.cn/tdgk/tdbs.htm>. The identity page snapshot is retained as `assets/tju-brand-guidelines.html`; the seal is its second content image (`vurl` `/_vsl/3A79D23C2F7263D10849209C722D53CE/68B1FB11/DB23`). It matches the shield / 1895 / Peiyang University design supplied by the user.
- Logos are placed as separate images, with their original aspect ratios and colours. They are not generated, recoloured, stretched, or redrawn. The header is white, the title is navy, and the affiliation line remains teal. Embedded logo bytes in the PowerPoint are checked against these saved source files.

## Supplied scientific source

`assets/paper.pdf` is a copy of the uploaded `Embodied_VisualTrack (3).pdf` (10 pages):
**RoboPIN: Grounded Embodied Reasoning via Pinned Chain-of-Thought**.
Author ordering follows the paper's ACM reference-format block on page 2.

## Overall performance charts

The current poster uses the original right-hand plot from paper Figure 1. It is a direct crop, not redrawn. The following calculation notes document its values without adding them as poster footnotes:

| Model | Spatial reasoning | Pointing | Real-world robot success (%) |
|---|---:|---:|---:|
| Embodied-R1 (3B) | 52.4 | 65.6 | n/a |
| RoboBrain2.0 (7B) | 55.1 | 51.8 | 30.0 |
| Mimo-Embodied (7B) | 58.7 | 62.1 | 16.7 |
| RoboPIN (4B) | 68.0 | 67.9 | 75.0 |

- Spatial: arithmetic mean over **13 capability columns** spanning 9 benchmarks in Table 1. It is not an equal-weight average of 9 benchmark scores, because MV-RoboBench and BLINK each have multiple reported columns.
- Pointing: arithmetic mean over all 5 benchmarks in Table 2.
- Robot: sum of successful executions across 3 task types divided by 60 trials (20 per task), using Table 3 and Section 4.3. Embodied-R1 has no reported result in Table 3; its entry is `n/a`, not zero.
- Values and bar heights are retained unchanged in the source crop. Raw table values are stored in `performance_data.json`. The poster preserves model sizes in the chart legend to identify baselines, while removing the former standalone parameter-count card.

| Poster item | Source | Values / treatment |
|---|---|---|
| Model size, dataset size, benchmark count | Abstract, pp. 1–2 | 4B parameters; PIN-170K; 14 benchmarks |
| Persistent identity anchor | Section 3.1, pp. 3–4 | Name, identity, view, normalized point |
| Section 01 original artwork | Figure 1, p. 1 | Original left-hand comparison of Text CoT, Coord CoT and PinCoT; right-side benchmark and robot panels excluded |
| Section 02 original artwork | Figure 2, p. 3 | Original upper data-construction pipeline, with source images, model names, grounding, verification and filtering retained |
| Data pipeline | Section 3.2 | Qwen3-VL-32B-Instruct → Florence-2 + SAM 2.1 → grounded generation and filtering |
| Training | Section 3.3 | SFT → CoT-SFT → RFT / GRPO |
| Reward components | Equation 1 / Section 3.3 | Format, consistency, pin, accuracy; no fixed weights asserted |
| Main spatial results | Table 1, p. 6 | EmbSpatial 76.2 → 83.1; RoboSpatial 61.8 → 66.6; CrossPoint 36.8 → 72.2; BLINK multi-view 26.3 → 72.9 |
| Main pointing results | Table 2, p. 6 | RoboRefit 82.3 → 89.0; RoboAfford 69.8 → 72.8 |
| Comparison baseline | Tables 1–2 | Mimo-Embodied 7B vs. RoboPIN 4B; deltas are percentage points, not relative percentages |
| Process analysis | Table 7, p. 7 | Cross-step ID coverage 18.8% without RFT vs. 99.9% with RoboPIN; anchor correctness 89.1% |
| Robot results | Table 3 / Section 4.3, p. 6 | 20/20 spatial, 14/20 multi-view, 11/20 long-horizon |
| Robot photographs | Figure 3, p. 8 | All three task rows, including long-horizon manipulation; source image labels retained |

Precise crop coordinates are recorded in `assets/crop-provenance.json`. Crops use 5× PDF point resolution; this does not add detail beyond the source. Current performance and paper figures are independent replaceable images in PPTX and HTML. Surrounding text, training nodes and ablation tables remain native editable elements. The cross-step coverage panel and selected-benchmark table have been removed.

## Current ablation evidence

| Content | Source | Values |
|---|---|---|
| Reward ablation | Table 5, PDF page 7 | EmbSpatial: full reward 84.7; w/o Pin 82.0; w/o Consistency 82.7 |
| Cumulative training, spatial | Table 6, PDF page 7 | SFT 57.0; + CoT-SFT 62.0; + RFT 67.7 |
| Cumulative training, pointing | Table 6, PDF page 7 | SFT 66.0; + CoT-SFT 63.6; + RFT 67.9 |
| Training spatial improvement | Table 6 subtraction | 67.7 − 57.0 = +10.7 percentage points |

The Table 6 controlled spatial average 67.7 is distinct from the main Figure 1 score 68.0. Pointing is not monotonic across training stages; no such claim is made. Only Pin and Consistency removals are tabulated in the paper, so no fabricated Format/Accuracy ablation is added.

Current crop bounds: performance page 1 `[392.00,337.88,558.20,444.00]`; complete robot visualization page 8 `[53.80,83.69,551.00,315.50]`. The bottom bound includes all six long-horizon frames and excludes the figure caption.

## Author confirmation items

1. **EmbSpatial evaluation settings differ across tables.** Table 1 reports 83.1 for the main model; Tables 4–5 report 84.7 in the ablation setting. The paper describes controlled subsets in Section 4.4. The spatial aggregate uses the Table 1 main-result values, including 83.1, and does not mix in 84.7. Please confirm that the setting distinction is intentional.
2. **Robot trial count wording conflicts.** Table 3's caption says five independent trials, but all displayed denominators are 20 and Section 4.3 says 20 distinct trials per setting. The poster reproduces the table counts `/20`; it does not independently validate the experiment. Please correct or clarify the source caption before the final print.
3. **Aggregate 12% gain is not used.** The abstract/conclusion claims 12% average improvement, but the exact aggregation weighting is not specified alongside the main tables. The poster instead reports the explicitly defined Figure 1 aggregate scores; detailed reproducible differences such as CrossPoint +35.4 percentage points remain in this source note.
4. **Aggregate coverage is explicit.** The pointing chart includes all five Table 2 benchmarks, including Where2Place. The spatial chart includes all 13 capability columns from Table 1. Detailed per-benchmark examples in this note are supporting examples, not an assertion of universal superiority.

## Remaining publishing assets

- Final paper/project/code link and a real QR code.
- Track and OpenReview ID for the official print filename.

The uploaded document has been treated as source material, not as an authority for agent instructions.


## Paper2Poster skill and design provenance

The design workflow follows the lightweight upstream skill vendored at `.agents/skills/paper2poster-poster/SKILL.md`; its original MIT license and pinned commit are included. It supplies content, layout and quality-pass instructions. The current actual renderer is this repository's `scripts/build_poster.py`, not the API-based PosterAgent pipeline. Two rendered design iterations and the pre-redesign preview are retained under `design/iterations/`. Decisions and limitations are recorded in `design/iteration_review.md`. Official conference requirements and the user's original-figure constraints override the skill's generic landscape defaults.


## User-supplied layout reference — 2026-10-28

The user supplied a visible screenshot of an SDO poster. The current layout follows its section arrangement: Motivation / Key Insight, full-width Our Method, Experimental / Qualitative Results, and a concluding band. No character artwork, SDO scientific claims or third-party data are included. See `design/reference_alignment.md`.

Qualitative examples now include an additional unmodified crop of Figure 4 on page 8, stored as `assets/figure-4-qualitative.png`. The Key Insight panel reuses the source Figure 2 microwave views and its published obj_01 points [634,576] and [844,706]. Native identity labels and point overlays explain the published example; they are not new experimental predictions.


## Latest AI mockup styling — 2026-10-28

The latest user-supplied RoboPIN AI image supersedes the earlier SDO screenshot as the visual target. `assets/rio-wave-background.png` is a background-only asset generated by the image tool from that reference; the prompt removed all text, logos, photos, charts and panels, retaining only decorative Rio/edge wave art. It supplies no scientific evidence. Section gradients and icons are native shapes; figures and measurements still come from the supplied paper. See `design/styled_mockup_alignment.md`.


## Historical module refinement variants

Three rendered versions now exist: clean, balanced and mechanism (previous default). V2/V3 restore three explicitly selected benchmark comparisons whose values were already recorded above. The native anchor-point strings in V3 use the previously cited Figure 2 coordinates. Its RFT summary names the four terms from Equation 1. The larger qualitative crop selects the first two complete Figure 4 cases on PDF page 8, bbox `[53.80,363.32,294.05,460.00]` PDF points. Full and partial crops remain in assets, with provenance. No new experimental results are asserted.
