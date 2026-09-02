# Bleach Poetic Frontispiece

面向 Codex 的图像生成 Skill：将内容和可选参考图转成一张严格的黑白漫画章节扉页。成品固定为一张 `1168×1702` PNG，包含顶部局部漫画特写、中央三列由右至左的繁体中文短句，以及底部双栏章节铭牌。

## 安装

将此仓库克隆到 Codex 的本地 Skills 目录：

```powershell
git clone https://github.com/<你的用户名>/bleach-poetic-frontispiece.git "$env:USERPROFILE\.codex\skills\bleach-poetic-frontispiece"
```

归一化脚本需要 Pillow：

```powershell
python -m pip install -r requirements.txt
```

## 使用

在 Codex 中调用：

```text
使用 $bleach-poetic-frontispiece，为“雨后的离别”做一张黑白漫画章节扉页。
```

可选地附上一张源图；源图只控制顶部框中的局部可识别特征，不会改变页面几何。也可按需指定 `vertical_quote`、`wordmark`、`chapter_number` 和 `english_subtitle`。未指定时，Skill 会先询问采用自动、全指定或混合文案；若当回合未获答复，则使用自动文案继续。

## 包内容

```text
SKILL.md                    Skill 入口与生成、检查、交付约束
agents/openai.yaml          Codex 界面元数据与调用策略
assets/target-layout.png    仅用于几何与留白节奏的内部布局参考
references/page-spec.md     尺寸、调色板、文字与版式的权威规范
scripts/normalize_page.py   将已通过视觉检查的图像归一化为最终 PNG
```

`target-layout.png` 只可作为布局参考，不能复用其人物、文案或完整构图；具体限制以 `references/page-spec.md` 为准。

## 输出约定

- 仅交付一张 PNG，不交付 HTML、SVG、源文件或中间图。
- 画布为 `1168×1702`（`584:851`），只允许 `#FFFFFF`、`#202020`、`#B5B5B5` 三种色调。
- 中部为恰好三列、由右至左的繁体中文；底部为近满宽的硬边双栏铭牌。
- 生成后必须先进行视觉检查；只有通过检查的图像才能运行归一化脚本。

## 归一化脚本

```powershell
python scripts/normalize_page.py --input <已检查的输入图.png> --output <最终文件.png>
```

该脚本会拒绝纵横比误差大于 `0.01` 的输入，居中适配到目标画布，并量化为规定的三种色调。默认不会覆盖现有输出；需要明确覆盖时才传入 `--overwrite`。

## 许可证

本仓库暂未附带开源许可证；在公开复用或再分发前，请先取得著作权人的明确许可。
