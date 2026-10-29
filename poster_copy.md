# Poster copy — reference-aligned revision

## Motivation

1. Text-based references can drift between similar objects. Coordinate-only grounding lacks explicit identity tracking.
2. A model may correctly analyze object A, then silently point to object B. This reasoning-to-answer misalignment breaks reliable visual grounding.

Visual: original Figure 1 left comparison. Prose condensed from Introduction and Section 3.1; no numbered figure caption on the poster.

## Key Insight: Persistent Identity

From isolated grounding to persistent anchors

- Spatial references are usually isolated annotations, without explicit identity tracking during reasoning.
- PinCoT binds each entity to a name, ID, view and point. Later steps reuse the same ID.
- Our insight: visual anchors act as persistent reasoning variables, making each step traceable to visual evidence.

Visual: conceptual implicit-reference chain (a cup / it / the target) versus a persistent obj_01 chain. This is an explanatory schematic, not a new experiment. The source microwave views now appear only in Method. QR remains a placeholder.

## Our Method: RoboPIN / PinCoT

### A. How PinCoT Reasons

1. Observe: How did the camera rotate between the two views?
2. Introduce an anchor: `<obj name="microwave" id="obj_01" img_idx="0" point="[634,576]">`. Introduce the entity once with identity, view and point; then refer to it by obj_01.
3. Reuse identity: same obj_01, new view. View 0 [634,576]; view 1 [844,706]. Its x-coordinate increases from 634 to 844: the object appears to shift right.
4. Ground the answer: in this example, apparent object motion is opposite to camera motion. Answer: Movement left.

This is a condensed explanatory reconstruction of the supplied paper's Figure 2 lower example, not a newly generated model trace or a verbatim quotation. Only one full tag is displayed; the second view uses a compact coordinate line. The source's case-specific camera-motion explanation is preserved.

### B. Data Construction & Training

Visual: original Figure 2 upper data pipeline, ending in PIN-170K.

- SFT: Embodied knowledge.
- CoT-SFT: Learn PinCoT traces.
- RFT / GRPO: Align reasoning and answers.

## Experimental Results

| Model | Spatial | Pointing | Robot |
|---|---:|---:|---:|
| Embodied-R1 (3B) | 52.4 | 65.6 | n/a |
| RoboBrain2.0 (7B) | 55.1 | 51.8 | 30.0 |
| Mimo-Embodied (7B) | 58.7 | 62.1 | 16.7 |
| RoboPIN (4B) | 68.0 | 67.9 | 75.0 |

Spatial: 13-column mean / 9 benchmarks. Pointing: 5-benchmark mean. Robot: overall success over 60 executions. Source: Figure 1 / Tables 1–3.

The performance chart is the original paper image. Supporting aggregation details above are documentation only.

### Ablation studies

Reward design (EmbSpatial): full reward 84.7; without Pin 82.0; without Consistency 82.7.

| Cumulative stage | Spatial | Point |
|---|---:|---:|
| SFT | 57.0 | 66.0 |
| + CoT-SFT | 62.0 | 63.6 |
| + RFT | 67.7 | 67.9 |

Spatial reasoning: +10.7 points from SFT to RFT.

Sources: Tables 5 and 6. The controlled ablation setting is separate from the main performance plot. Source references do not appear as numbered poster captions.

## Qualitative Results

All three original Figure 3 execution rows and Figure 4 grounded reasoning examples.

Zero-shot xArm successes: spatial 20/20, multi-view 14/20, long-horizon 11/20 (Table 3).

## Closing statement

Persistent Visual Anchors · Consistent Reasoning · Grounded Answers

Title, author order, university, official logos and contact addresses continue to follow the supplied paper and verified branding.
