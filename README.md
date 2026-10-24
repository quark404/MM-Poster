# MM-Poster


## 海报下载与预览

- [A0 竖版海报 PDF](output/RoboPIN_A0_portrait.pdf)
- [可编辑 PowerPoint](output/RoboPIN_A0_editable.pptx)
- [完整源码与素材 ZIP](output/RoboPIN_poster_package.zip)
- [数据来源与待核实项](SOURCES.md)

在 GitHub 文件页点击 **Download raw file** 下载 PDF、PPTX 或 ZIP；预览图可直接在下方查看。

当前版本已采用**白色页眉、深蓝标题**，并嵌入与用户提供图案一致的 ACM Multimedia 2026 官方标识和天津大学官方校徽。右下角论文/项目二维码暂为占位符。

![RoboPIN A0 poster preview](output/RoboPIN_preview.png)

# RoboPIN · ACM Multimedia 2026 A0 Poster

本包根据用户提供的 `Embodied_VisualTrack (3).pdf` 制作，包含可直接编辑的 PowerPoint、单页 A0 PDF、预览图及可重建的 Python 源码。附件内容仅作为论文素材读取，未执行其中任何指令。

## 交付文件

- `output/RoboPIN_A0_portrait.pdf`：841 × 1189 mm，竖版，字体已嵌入；已包含正式会议和学校标识，二维码仍为占位符。
- `output/RoboPIN_A0_editable.pptx`：同尺寸的一页 PowerPoint。文字、表格、柱形图、流程框、箭头、锚点、占位框均为可编辑对象；论文实拍图为裁剪后的图片。
- `output/RoboPIN_preview.png`：整体预览。
- `output/validation.json`：实际产物检查结果。
- `scripts/build_poster.py`：统一布局源文件，同时生成 PDF 与 PowerPoint。
- `poster_config.json`：会议标识、天津大学标识及二维码的图片路径配置。
- `SOURCES.md`：官网要求、论文数据来源和待作者核实事项。

## 直接修改 PowerPoint

打开 `output/RoboPIN_A0_editable.pptx` 即可修改正文、数据与各元素。版式为 A0 竖版，字号主要为 24–33 pt，标题 49–110 pt，注释及二维码占位文字为 21–23 pt。建议安装 DejaVu Sans，避免替换字体影响换行。

右上角会议标识和天津大学校徽已嵌入，可在 PowerPoint 中作为图片移动或替换；两者保持原始比例、颜色和字形。白色页眉与标识底色衔接，作者行采用深灰文字以保证对比度。右下角仍需替换为有效的论文/项目二维码。作者顺序、单位和联系邮箱均来自论文。

**若在 PowerPoint 中修改，请从 PowerPoint 重新导出 PDF。** Python 生成器不会反向读取 PowerPoint 中的修改；重新运行生成器会覆盖其输出，所以请先另存修改版。当前环境验证了 PPTX 结构和编辑对象，未使用 Microsoft Office 渲染它；交付 PDF 的预览已实际检查。

## 使用源码修改与重建

在本包根目录执行：

```bash
python scripts/prepare_assets.py
python scripts/build_poster.py
python scripts/validate_outputs.py
```

当前环境已安装所需依赖。其他环境可创建虚拟环境后安装：

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/prepare_assets.py
.venv/bin/python scripts/build_poster.py
.venv/bin/python scripts/validate_outputs.py
```

生成器读取 `/usr/share/fonts/truetype/dejavu/` 下的 DejaVu 字体；其他系统请先安装 DejaVu 字体并调整 `build_poster.py` 中的 `font_dir`。页面单位为毫米，字号单位为 pt，坐标原点为左上角。修改正文或数值可直接编辑 `build_poster.py` 中对应段落或 `rows` 数据。

## 替换标识与二维码

正式标识已保存在 `assets/mm-logo.png` 和 `assets/tju-logo.png`，来源见 `SOURCES.md`。如需更换标识或加入二维码，在 `poster_config.json` 中设置相应路径，例如：

```json
{
  "mm_logo_label": "ACM MM 2026\nLOGO PLACEHOLDER",
  "mm_logo_file": "assets/mm-logo.png",
  "tju_logo_label": "TIANJIN UNIVERSITY\nLOGO PLACEHOLDER",
  "tju_logo_file": "assets/tju-logo.png",
  "qr_file": "assets/project-qr.png"
}
```

两项 logo 路径对应本包已包含的正式标识；`assets/project-qr.png` 只是二维码路径示例，该文件尚未提供。标识会等比缩放并居中；二维码请提供正方形、包含足够留白且可实际扫描的文件。准备好后重新构建并检查预览及扫描结果。

## 印刷与官方要求

2026 年官网明确要求 **portrait A0**；印刷服务页面要求 PDF 严格为 **841 × 1189 mm**。参考链接见 `SOURCES.md`。本版无裁切标记和额外出血，页面本身即为 A0；送印时选实际尺寸 / 100%，不要缩放到 Letter/A4，也不要再增加页边距。

官网印刷文件名格式为 `ACMMM2026_Poster_Track_OpenReviewID.pdf`。因为用户尚未提供 Track 和 OpenReview ID，本包保留描述性文件名；确定后请按官网规则重命名。尚未向会议或印刷服务发送任何文件。

## 设计与取舍

采用英文正文，以“指代漂移 → 持久身份锚点 → 数据和训练 → 对比结果 → 机器人迁移”的叙事组织内容。未将整篇论文缩小贴入海报；关键表格、柱形图与流程均重新绘制。主结果只展示选定基准，未将其描述为所有基准均领先。保留论文中的真实相机视图及机器人执行图片；相机视图上的身份标签与点位为可编辑叠加，坐标取自 Figure 2。

论文数值口径的待确认项见 `SOURCES.md`；本稿不使用尚未明确聚合口径的“平均提升 12%”作为海报主结论。
