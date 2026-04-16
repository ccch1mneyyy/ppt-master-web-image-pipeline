# PPT Master Web Image Pipeline

[English](./README.md) | 中文

`ppt-master-web-image-pipeline` 是 [PPT Master](https://github.com/ccch1mneyyy/ppt-master) 的配套 Codex 技能，专门解决一个常见痛点：**有网页端 AI 生图会员，但没有 API key**。

它能把 PPT Master 的 Step 5（图片生成）阶段对接到你已经登录的网页生图工具上——Gemini、Nano Banana、ChatGPT、Grok、豆包都支持。不需要 API，直接复用浏览器会话。

## 它做什么

- 从 `design_spec.md` 提取待生成的图片清单
- 生成提示词文档和任务清单（`image_prompts.md` + `web_generation_manifest.json`）
- 复用已登录的浏览器会话来生成和抓取图片
- 清理水印、角标、截图边框等杂质
- 校验图片并回写生成状态

## 仓库结构

```text
ppt-master-web-image-pipeline/
├── SKILL.md              # 技能主入口
├── agents/               # Agent 配置
├── references/           # 工作流参考文档
│   ├── ppt-master-bridge.md
│   ├── web-providers.md
│   └── capture-and-watermarks.md
└── scripts/              # 辅助脚本
    ├── extract_image_resource_list.py
    ├── build_ppt_image_prompts.py
    ├── update_design_spec_status.py
    ├── verify_ppt_images.py
    └── postprocess_web_image.py
```

## 安装

把 `ppt-master-web-image-pipeline/` 文件夹复制到 Codex 的 skills 目录下：

```text
~/.codex/skills/
```

Windows 用户一般在这里：

```text
C:/Users/<你的用户名>/.codex/skills/
```

然后重启 Codex 让它重新加载技能。

## 依赖

内置 Python 脚本依赖 Pillow：

```bash
pip install -r requirements.txt
```

## 使用流程

1. 准备一个 PPT Master 项目（包含 `design_spec.md` 和 `images/` 目录）
2. 用技能提取待生成的图片资源
3. 生成提示词和任务清单
4. 复用已登录的浏览器会话进行网页生图
5. 校验生成结果，回写项目状态

## 注意事项

- 这是 PPT Master Step 5 的配套技能，不会替代主流程的 Strategist 或 Executor
- 需要精确标签或矢量图的图表类素材，建议回到 PPT Master Executor 或手动制作 SVG，不适合用网页生图硬做

## 文档索引

- [`技能介绍.md`](./技能介绍.md)：详细的中文介绍
- [`ppt-master-web-image-pipeline/SKILL.md`](./ppt-master-web-image-pipeline/SKILL.md)：技能主入口
- [`ppt-master-web-image-pipeline/references/`](./ppt-master-web-image-pipeline/references/)：工作流参考文档
- [`ppt-master-web-image-pipeline/scripts/`](./ppt-master-web-image-pipeline/scripts/)：辅助脚本
