# Universal AI URL Workflow

一个面向 Alfred 5 的 Python Workflow，用来把输入内容或剪贴板内容拼成目标站点 URL，并分发到一个或多个 AI 站点打开。

这个仓库负责 Alfred 入口、Prompt 模板、URL 组装和多站点打开。

Chrome 端的自动注入能力不在本仓库内实现，而是依赖：

- `github.com:penwyp/universal-ai-url-prompt`

该项目负责浏览器侧自动识别 URL 中的 prompt 参数，并注入到对应站点输入框中。因此，这个 workflow 与 Chrome 自动注入需要配套使用。

## 功能概览

- 支持单站点打开
- 支持多站点同时打开
- 支持从剪贴板读取内容
- 支持预设 Prompt 模板前缀
- 支持通过 Alfred 变量覆盖默认站点 URL

当前内置站点：

- Gemini
- ChatGPT
- Kimi
- DeepSeek
- Claude

## 使用方式

安装 `.alfredworkflow` 后，在 Alfred 中输入工作流关键词，再跟上你的问题或文本内容。

默认行为：

- 直接输入内容时，使用你的输入作为 prompt
- 只输入关键词时，会展示剪贴板入口和模板前缀入口
- 选择某个平台后，打开对应站点
- 选择“同时打开 ...”后，会一次打开所有已启用的平台

示例：

```text
ai 解释一下这段 SQL 的执行计划
ai bug java.lang.NullPointerException at ...
ai doc 帮我整理成一份技术方案
```

其中：

- `bug`、`doc` 这类前缀来自 `workflow/config/templates.json`
- 如果只输入 `ai bug`，且剪贴板有内容，则会自动使用剪贴板内容拼接模板

## Prompt 模板修改方式

Prompt 模板定义在：

- `workflow/config/templates.json`

格式示例：

```json
{
  "bug": {
    "title": "异常与故障排查",
    "prompt": "作为SRE与开发专家，请分析以下报错或异常，给出可能的原因分析、排查思路和修复方案：\n\n"
  }
}
```

说明：

- `bug` 是 Alfred 中输入的前缀
- `title` 是候选项展示名称
- `prompt` 是最终拼接到用户输入或剪贴板前面的固定提示词

修改后重新执行：

```bash
make
```

## 站点修改方式

站点有两种修改方式，分别适合“改默认配置”和“改本机安装后的行为”。

### 方式 1：修改仓库内默认站点配置

默认站点定义在：

- `workflow/config/platforms.json`

示例：

```json
{
  "chatgpt": {
    "name": "ChatGPT",
    "url": "https://chatgpt.com/?prompt=%s",
    "icon": "ChatGPT.icns",
    "enabled_by_default": true
  }
}
```

字段说明：

- `name`：Alfred 中展示的站点名称
- `url`：站点 URL 模板，`%s` 会被替换为 URL 编码后的 prompt
- `icon`：图标文件名，对应 `icons/`
- `enabled_by_default`：是否默认加入“同时打开”

URL 规则：

- 如果 `url` 中包含 `%s`，脚本会直接替换
- 如果 `url` 不包含 `%s`，脚本会自动追加 `prompt=` 参数
- 运行时还会附加 `autosend` 参数

修改 `platforms.json` 后重新打包：

```bash
make
```

### 方式 2：在 Alfred 中覆盖站点 URL 和开关

安装 workflow 后，`info.plist` 会写入默认变量，运行时脚本优先读取这些 Alfred 变量。

主要变量包括：

- `enable_gemini=1`
- `enable_chatgpt=1`
- `enable_kimi=0`
- `enable_deepseek=0`
- `enable_claude=0`
- `url_gemini=https://gemini.google.com/app?prompt=%s`
- `url_chatgpt=https://chatgpt.com/?prompt=%s`
- `url_kimi=https://kimi.moonshot.cn/?p=%s`
- `url_deepseek=https://chatgpt.com/?q=%s`
- `url_claude=https://claude.ai/new?prompt=%s`
- `autosend=1`

适用场景：

- 只想在自己机器上临时替换某个站点地址
- 不想改仓库内容，只想调整多开默认集合
- 需要给不同机器使用不同的站点 URL

## Chrome 自动注入说明

本仓库只负责把 prompt 放进 URL 并打开页面，不直接操作网页输入框。

如果你希望打开页面后自动把 prompt 注入到 ChatGPT、Gemini、Claude 等页面输入框，需要同时安装并使用：

- `github.com:penwyp/universal-ai-url-prompt`

推荐配套方式：

1. 本仓库负责 Alfred 触发和 URL 分发
2. `universal-ai-url-prompt` 负责 Chrome 侧解析 URL 参数并自动注入

如果没有该 Chrome 端项目，这个 workflow 仍然可以打开目标页面，但是否能自动填充输入框，取决于目标站点本身是否支持通过 URL 参数带入 prompt。

## 构建

常用命令：

```bash
make
make plist
make lint
make clean && make
```

说明：

- `make`：生成 `info.plist`、`icon.png` 并打包 workflow
- `make plist`：只生成 `info.plist`
- `make lint`：检查 Python 脚本和 `info.plist`
- `make clean && make`：清理后完整重打包

输出文件位于：

- `dist/universal-ai-prompt-<version>.alfredworkflow`
