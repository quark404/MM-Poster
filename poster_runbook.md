# Runbook

## Current output

Default `source` layout generates HTML, PPTX and PDF with original performance artwork, all three robot execution rows, reward ablations and cumulative training-stage results. Archived earlier variants remain in `output/variants`; rebuild them from historical Git commits if needed. `--output-dir` selects the output folder for all current generation and validation scripts.

## Current visual target

The user's renewed SDO screenshot now governs typography and prose. Use plain white, flat coral section strips, centered Comic Neue Bold headings and Open Sans body copy with coral phrase emphasis. No anime art. The earlier Rio mockup is superseded. See `design/reference_typography.md` for source excerpts and decisions.

## What was actually run

The upstream lightweight skill is installed in `.agents/skills/paper2poster-poster/`; its original instruction, references, metadata, license and source commit are retained. The source paper already follows the upstream folder convention at `assets/paper.pdf`; the per-paper `assets/poster.yaml` sits alongside it.

Current deliverables use the local PDF/PPTX renderer after applying the skill's source-grounding, copy compression, layout and quality-pass workflow:

```bash
cd /workspace/MM-Poster
python scripts/prepare_assets.py
python scripts/build_poster.py
python scripts/validate_outputs.py
python scripts/render_html.py
```

This path requires no remote model credentials. The output is exactly A0 portrait. Native text, inline phrase colors, ablation tables and layout shapes are editable; performance and paper figures are original images. HTML embeds every font and picture and works offline. Chromium prints an additional HTML PDF.

## Optional full upstream PosterAgent execution — NOT RUN

The separate upstream checkout is `/workspace/Paper2Poster`. Its full requirements and model service were not installed or executed. Required OpenAI API credentials were absent when checked; values have not been requested or stored. The lightweight skill does not require them.

After provisioning the upstream dependencies (including LibreOffice / Poppler) and securely supplying model access, the documented CLI supports this exploratory command:

```bash
cd /workspace/Paper2Poster
python -m PosterAgent.new_pipeline \
  --poster_path=/workspace/MM-Poster/assets/paper.pdf \
  --poster_name=RoboPIN \
  --model_name_t=4o \
  --model_name_v=4o \
  --poster_width_inches=33 \
  --poster_height_inches=47 \
  --institution_logo_path=/workspace/MM-Poster/assets/tju-logo.png \
  --conference_logo_path=/workspace/MM-Poster/assets/mm-logo.png \
  --max_workers=2
```

**This command is unexecuted and is not an A0 print recipe.** Inspection of upstream `PosterAgent/new_pipeline.py` shows integer-only inch flags and an unconditional `scale_to_target_area()` call. Fractional A0 inches cannot be passed directly, and automatic area scaling can change the final physical size. Inspect and resize any upstream result to exactly 841 × 1189 mm, then render and verify it before use. The current local renderer avoids this issue by setting PDF and PPTX dimensions directly in millimetres. No upstream application code was modified.

Upstream YAML precedence also deserves attention: the current implementation reads the per-paper config first and then project-level defaults, so those later defaults may override it. If using the full pipeline, verify effective settings rather than assuming the per-paper file wins.

## Quality pass

- Inspect the complete poster at reduced scale for reading order and visual balance.
- Inspect the source figures and chart details at larger scale.
- Validate the actual one-page PDF dimensions and font embedding.
- Validate the original Figure 1 performance crop and all three Figure 3 robot rows by image identity and visual inspection.
- Compare editable ablation text with Tables 5 and 6; preserve the Point dip at CoT-SFT.
- Check logo and original-figure bytes in the PPTX.
- Render HTML offline in Chromium, check text bounds and image loading, print one A0 page and inspect its preview.
- Check native text collisions, all page bounds and PPTX archive integrity.
- Keep the QR placeholder visible until a real project link and QR are supplied.
- Microsoft Office rendering and a physical print proof remain separate from the checks run here.
