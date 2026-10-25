# Poster copy

## Title block

RoboPIN: Grounded Embodied Reasoning via Pinned Chain-of-Thought

Yaoting Huang*, Yifu Yuan*†, Linqi Han, Chengwen Li, Shuoheng Zhang, Xianze Yao, Hongyao Tang, Yan Zheng, Jianye Hao†

Tianjin University · ACM Multimedia 2026 · Rio de Janeiro, Brazil · 10–14 November 2026

## 01 — Reason with a persistent visual anchor

One entity. One persistent ID.

a = (name, id, view, point)

- Introduce anchor: name, ID, view and point.
- Reuse identity across reasoning steps and viewpoints.
- Visual evidence stays traceable.

Visual: original paper Figure 1 left comparison.

## 02 — How RoboPIN learns to stay grounded

Visual: original Figure 2 upper pipeline, preserving semantic parsing, point grounding, reverse verification, generation and filtering.

Three-stage post-training:
- SFT: embodied knowledge.
- CoT-SFT: structured reasoning.
- RFT / GRPO: process alignment.

## 03 — Grounding improves embodied reasoning

Original aggregate scores from Figure 1 / Tables 1–3:

| Model | Spatial | Pointing | Robot |
|---|---:|---:|---:|
| Embodied-R1 (3B) | 52.4 | 65.6 | n/a |
| RoboBrain2.0 (7B) | 55.1 | 51.8 | 30.0 |
| Mimo-Embodied (7B) | 58.7 | 62.1 | 16.7 |
| RoboPIN (4B) | 68.0 | 67.9 | 75.0 |

All charts use a zero baseline and a 0–100 scale. Spatial is the arithmetic mean over 13 capability columns spanning 9 benchmarks; pointing over 5 benchmarks; robot success over 60 executions.

## 04 — Reliable execution and consistent entity tracking

Zero-shot xArm execution, Figure 3:
- Spatial: 20 / 20.
- Multi-view: 14 / 20.
- Long-horizon: 11 / 20.

Cross-step identity coverage: 18.8% without RFT → 99.9% with RoboPIN (Table 7).

Contact: quark404@tju.edu.cn · yuanyf@tju.edu.cn.

* Equal contribution. † Corresponding authors. Paper/code QR remains a labelled placeholder.
