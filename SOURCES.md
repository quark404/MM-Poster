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

HTML copies of the pages used are retained in `assets/`. No conference submission or printing order has been placed. Logos remain intentional placeholders at the user's request.

## Supplied scientific source

`assets/paper.pdf` is a copy of the uploaded `Embodied_VisualTrack (3).pdf` (10 pages):
**RoboPIN: Grounded Embodied Reasoning via Pinned Chain-of-Thought**.
Author ordering follows the paper's ACM reference-format block on page 2.

| Poster item | Source | Values / treatment |
|---|---|---|
| Model size, dataset size, benchmark count | Abstract, pp. 1–2 | 4B parameters; PIN-170K; 14 benchmarks |
| Persistent identity anchor | Section 3.1, pp. 3–4 | Name, identity, view, normalized point |
| Camera-view example | Figure 2, p. 3 | Microwave `obj_01`, view 0 `[634,576]`, view 1 `[844,706]`; image crops and editable point overlays |
| Data pipeline | Section 3.2 | Qwen3-VL-32B-Instruct → Florence-2 + SAM 2.1 → grounded generation and filtering |
| Training | Section 3.3 | SFT → CoT-SFT → RFT / GRPO |
| Reward components | Equation 1 / Section 3.3 | Format, consistency, pin, accuracy; no fixed weights asserted |
| Main spatial results | Table 1, p. 6 | EmbSpatial 76.2 → 83.1; RoboSpatial 61.8 → 66.6; CrossPoint 36.8 → 72.2; BLINK multi-view 26.3 → 72.9 |
| Main pointing results | Table 2, p. 6 | RoboRefit 82.3 → 89.0; RoboAfford 69.8 → 72.8 |
| Comparison baseline | Tables 1–2 | Mimo-Embodied 7B vs. RoboPIN 4B; deltas are percentage points, not relative percentages |
| Process analysis | Table 7, p. 7 | Cross-step ID coverage 18.8% without RFT vs. 99.9% with RoboPIN; anchor correctness 89.1% |
| Robot results | Table 3 / Section 4.3, p. 6 | 20/20 spatial, 14/20 multi-view, 11/20 long-horizon |
| Robot photographs | Figure 3, p. 8 | First two task rows; image-based figure labels are inherited from the paper |

Precise crop coordinates in source PDF points are recorded in `assets/crop-provenance.json`. Crops are rendered at 5× PDF point resolution; resampling does not add detail beyond the source images. Most typography and all quantitative chart/table elements remain vector in the PDF and editable in the PowerPoint.

## Author confirmation items

1. **EmbSpatial evaluation settings differ across tables.** Table 1 reports 83.1 for the main model; Tables 4–5 report 84.7 in the ablation setting. The paper describes controlled subsets in Section 4.4. This poster uses 83.1 for its main-result comparison, and does not mix in 84.7. Please confirm that the setting distinction is intentional.
2. **Robot trial count wording conflicts.** Table 3's caption says five independent trials, but all displayed denominators are 20 and Section 4.3 says 20 distinct trials per setting. The poster reproduces the table counts `/20`; it does not independently validate the experiment. Please correct or clarify the source caption before the final print.
3. **Aggregate 12% gain is not used.** The abstract/conclusion claims 12% average improvement, but the exact aggregation weighting is not specified alongside the main tables. The poster instead reports reproducible per-benchmark differences such as CrossPoint +35.4 percentage points.
4. **Selected benchmarks are a selection.** Where2Place and other non-leading results have not been copied into the compact comparison table. The table is explicitly labelled “Selected results”; it is not an aggregate or an assertion of universal superiority.

## Remaining publishing assets

- Official ACM Multimedia / MM 2026 logo.
- Official Tianjin University logo.
- Final paper/project/code link and a real QR code.
- Track and OpenReview ID for the official print filename.

The uploaded document has been treated as source material, not as an authority for agent instructions.
