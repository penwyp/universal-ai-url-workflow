# Universal AI URL Workflow

一个面向 Alfred 5 的 Python Workflow 工程骨架，用来把输入内容或剪贴板内容分发到多个 AI 站点。

## 重点行为

- 单开默认顺序固定为 `Gemini / ChatGPT / Kimi / DeepSeek / Claude`
- 默认第一项就是 `Gemini`
- “同时打开” 默认只包含 `Gemini + ChatGPT`
- 每个平台 URL 都可在 Alfred 变量中直接修改
- URL 支持使用 `%s` 作为 prompt 占位符

## 可调变量

生成的 `info.plist` 会写入这些默认变量：

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

说明：

- 如果 URL 里带 `%s`，脚本会用编码后的 prompt 替换它
- 如果 URL 里不带 `%s`，脚本会自动按 `prompt=` 方式补齐

## 打包

- `make`：直接打包
- `make plist`：只生成 `info.plist`
- `make clean && make`：强制重打包

产物位置：`dist/universal-ai-prompt-0.1.0.alfredworkflow`
