# Current method: complete original paper figure

The user rejected the custom four-step redraw and explicitly requested the paper's complete Figure 2: data-construction pipeline on top, concrete reasoning example below. The user also requested restoring the preceding Key Insight and removing the QR placeholder entirely.

The current renderer embeds `assets/figure-2-full-method.png` as a single image. It is a direct crop of PDF page 3, `[53.80,84.48,551.48,282.00]` in PDF points, rendered at 5×. It preserves the full artwork, including source photos, XML tags, prose, arrows and answer. Only the numbered caption beneath the artwork is excluded. The image is placed 700 mm wide at its original aspect ratio. In PPT it is a replaceable picture, not editable internal shapes or rewritten text.

Key Insight restores the previous view pair and prose from commit `2e1b15c`, with source aspect ratios preserved. Its last bullet expands to use the space freed by removing the QR. There is no QR frame, QR placeholder or PAPER / CODE label. The prior four-step Method, A/B labels and concept-chain replacement are no longer used.

[Method detail](../output/detail-method.png) · [Full preview](../output/RoboPIN_HTML_preview.png)
