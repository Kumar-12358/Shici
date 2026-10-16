# 诗词自动化 · 云端部署（关机也能每天发）

你之前用 WorkBuddy 里的自动化发「早安诗词」，但它只在 WorkBuddy 运行时才触发——你一关机 / 关 WorkBuddy 就不发了。现在把这套逻辑搬到一个免费托管平台（GitHub）上，由它的服务器每天**北京时间 9:00** 自动发，**你的电脑关着也照发**。

## 这套东西包含什么
- `poems.json`：内置 18 首李白诗（你之前已发过的 4 首记在 history 里，不会重发）。
- `daily_poem.py`：选诗 + 写正文 + 推送到微信的脚本，不依赖 WorkBuddy。
- `history.json`：已发记录，用来避免重复。
- `.github/workflows/daily.yml`：定时任务配置（每天北京 9:00）。

## 你只要做 4 步（都在网页上点，不用敲命令）
1. **注册 GitHub**：打开 github.com，用邮箱注册一个免费账号。
2. **新建仓库**：点右上角 `+` → New repository，名字随便起（如 `morning-poem`），Public 或 Private 都行。
3. **上传文件**：进仓库后把**整个 cloud 文件夹**拖到上传区（含隐藏的 `.github` 文件夹也要一起传），提交。
   - ⚠️ 本目录默认没有 `config.json`，保持没有就行——千万不要上传任何含你 token 的文件。
4. **填密钥**：仓库里点 `Settings` → 左侧 `Secrets and variables` → `Actions` → `New repository secret`：
   - Name 填：`PUSHPLUS_TOKEN`
   - Secret 填：你之前用的 PushPlus token（就在 `poem-morning/config.json` 的 `"token"` 那一行）。
   - 点 Add secret。

## 启动 & 测试
- 默认每天**北京时间 9:00** 自动发（GitHub 服务器偶尔会晚几分钟，正常）。
- 想立刻验证：进仓库 `Actions` 标签 → 左侧 `每日李白诗推送` → `Run workflow` 手动跑一次，几分钟后微信服务号里就能看到。

## 以后想改
- **加诗 / 换诗**：编辑 `poems.json`，按现有格式加一首（`title` / `work` / `lines` / `plain` / `time` / `background`），提交即可。
- **推到 ClawBot 而非服务号**：把 `daily_poem.py` 里的 `"channel": "wechat"` 改成 `"channel": "clawbot"` 再提交。

## 注意事项
- GitHub Actions 免费额度对个人足够（每天 1 次，几乎不占额度）。
- 历史记录用 artifact 保存，默认保留 90 天；过期后只是重新从头循环，不影响收发。
- token 只存在 GitHub 密钥里，不要写进代码或发到别处。

## 本地预览（可选，不推送）
```bash
python daily_poem.py --dry-run
```
