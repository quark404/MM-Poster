# Reasoning-first Method

The user identified that the earlier Method showed only data construction and approved splitting it into a concrete PinCoT explanation followed by data construction/training.

## A. How PinCoT Reasons

The upper section reconstructs the lower half of the supplied paper's Figure 2, using its exact camera-view crops and published entity, coordinates and answer. Four stages show observation, anchor introduction, identity reuse and grounded answer. The CoT explanation is a concise paraphrase, not a verbatim transcript and not a new experiment.

| Poster element | Paper evidence |
|---|---|
| Two views and camera-rotation question | Figure 2 lower, PDF p. 3 |
| Microwave with obj_01; view 0 point [634,576] | First full tag in the example |
| Same obj_01 in view 1 at [844,706] | Second full tag in the example; rendered compactly on the poster |
| x-coordinate increases from 634 to 844; shift right | Source example's explanatory CoT |
| Camera movement left | Source `<answer> movement left </answer>` |
| Introduce once, then reuse ID | Section 3.1, PDF pp. 3–4 |

The source says “For this task” when relating apparent object motion to camera motion. The poster retains this qualification as “In this example”; it does not assert a universal geometric rule.

A complete source crop is retained at `assets/figure-2-reasoning-example.png` for checking. The two source photographs in the current slide appear only in Method; all surrounding text, colored ID mentions and arrows are editable. One complete XML tag is shown to establish the representation, and the remaining steps reuse its ID.

## B. Data Construction & Training

The original Figure 2 upper pipeline remains a distinct image below Part A. It describes generation of PIN-170K supervision, not inference-time calls by RoboPIN. Training is summarized separately to its right: SFT (embodied knowledge), CoT-SFT (PinCoT traces), RFT / GRPO (process and answer alignment), grounded in Section 3.3.

## Key Insight and space allocation

Key Insight now explains the conceptual contrast between ambiguous implicit references and persistent IDs, without repeating the worked example's photos. The “a cup / it / the target” chain is a pedagogical schematic, not a measured baseline failure.

Method grows from 234 to 314 mm high. The motivation figure and result figures are reduced proportionally to retain all previous scientific evidence. Three robot rows and both reward/training ablations remain intact. Source image aspect ratios, A0 dimensions, editable example text and no-number-caption preferences are validated.

[Method detail](../output/detail-method.png) · [Full preview](../output/RoboPIN_HTML_preview.png)
