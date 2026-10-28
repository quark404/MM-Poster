# Poster copy — reference-aligned revision

## Motivation

1. Reference drift: textual references can switch between similar objects during multi-step reasoning.
2. Reasoning–answer misalignment: a correct intermediate analysis can still end on the wrong object, especially across views.

Visual: original Figure 1 left comparison.

## Key Insight: Persistent Identity

Same entity. Same ID. Different views.

Reasoning anchor = name + ID + view + point.

Introduce the anchor once; reuse its identity throughout the reasoning chain. Persistent IDs connect visual grounding, intermediate steps and the final answer.

Visual: the microwave view pair from Figure 2; `obj_01` in both views. Paper/code QR is a labelled placeholder.

## Our Method: RoboPIN / PinCoT

Original Figure 2 data-construction pipeline.

SFT: embodied knowledge → CoT-SFT: structured reasoning → RFT / GRPO: process alignment.

PinCoT binds visual evidence to persistent identities. PIN-170K supplies structured traces; process rewards supervise grounding and identity consistency.

## Experimental Results

| Model | Spatial | Pointing | Robot |
|---|---:|---:|---:|
| Embodied-R1 (3B) | 52.4 | 65.6 | n/a |
| RoboBrain2.0 (7B) | 55.1 | 51.8 | 30.0 |
| Mimo-Embodied (7B) | 58.7 | 62.1 | 16.7 |
| RoboPIN (4B) | 68.0 | 67.9 | 75.0 |

Spatial: 13-column mean / 9 benchmarks. Pointing: 5-benchmark mean. Robot: overall success over 60 executions. Source: Figure 1 / Tables 1–3.

Cross-step ID coverage: 18.8% without RFT → 99.9% with RoboPIN (Table 7).

## Qualitative Results

Original Figure 3 execution sequences and Figure 4 grounded reasoning examples.

Zero-shot xArm successes: spatial 20/20, multi-view 14/20, long-horizon 11/20 (Table 3).

## Closing statement

Persistent visual anchors make embodied reasoning traceable.

Title, author order, university, official logos and contact addresses continue to follow the supplied paper and verified branding.


## Latest V3 additions

- Anchor example: `obj_01 · view 0 · point [634,576]`; `obj_01 · view 1 · point [844,706]`.
- RFT rewards format, identity consistency, pin localization and final-answer correctness.
- Explicitly selected benchmark rows compare Mimo-Embodied 7B and RoboPIN 4B: CrossPoint 36.8 / 72.2, BLINK multi-view 26.3 / 72.9, EmbSpatial 76.2 / 83.1.
- Qualitative presentation uses two larger representative reasoning examples, not all three thumbnail rows.
