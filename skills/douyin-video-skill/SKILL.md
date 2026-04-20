---
name: douyin-video-skill
description: "抖音视频搜索、筛选、选定、链接获取、文案提取与文案修正工作流。用于： (1) 在抖音网页中登录后搜索自定义关键词，(2) 按筛选参数从搜索结果中选择合适视频，(3) 优先从页面 modal_id 或视频页 URL 构造稳定视频链接，必要时再尝试分享按钮复制链接，(4) 使用本 skill 内置脚本下载视频并提取语音文案，(5) 对 ASR 结果进行基于标题、标签、上下文和领域常识的合理修正，并输出原始稿、修正版、修正说明。适用于抖音二次创作前的素材采集、竞品研究、视频文案提取与清洗场景；可独立发布，不依赖外部 douyin-video skill。"
---

# 抖音视频搜索 → 提取 → 修正 工作流

这个 skill 是给 `workspace-douyin-analyst` 用的**完整工作流 skill**。

它吸收了现有 `skills/douyin-video` 的后半段能力（下载视频、提取文案），并补上前半段：
- 打开抖音
- 复用登录态
- 搜索自定义关键词
- 按规则筛选结果
- 锁定目标视频
- 获取稳定视频链接
- 提取文案
- 修正文案
- 强制落盘

## 核心原则

### 1. 不把“复制链接”当成唯一依赖
PC 端抖音页面的分享浮层不稳定，按钮可能：
- 只有悬停才出现
- 在播放器浮层里不易点中
- DOM 结构经常变化

**优先顺序：**
1. 直接读取当前页面 URL 中的 `modal_id`
2. 组装为 `https://www.iesdouyin.com/share/video/<videoId>`
3. 若页面结构稳定，再尝试分享按钮/复制链接

### 2. 先校验“当前视频”再提取
搜索结果页点开视频后，抖音弹层里的当前视频有时会切到别的结果。

**必须增加校验：**
- 搜索结果卡片标题
- 当前弹层视频标题 / 当前 `modal_id`
- 若二者不一致，不要继续提取；先重新锁定目标

### 3. 文案提取后必须修正
ASR 常见问题：
- 同音错字
- 连词错误
- 重复词
- 断句错误
- 领域术语误识别

修正时必须结合：
- 视频标题
- 话题标签
- 前后句上下文
- 领域常识（如无人机、赛事、培训、器材术语）

## 推荐目录结构

```text
skills/douyin-video-skill/
├── SKILL.md
├── scripts/
│   ├── douyin_downloader.py
│   ├── run_pipeline.py
│   ├── title_match_check.py
│   └── transcript_cleanup.py
└── references/
    ├── filter-rules.md
    └── publish-copy.md
```

## 内置能力与依赖

这个 skill 已经**吸收并内置**了原 `douyin-video` 里对新 skill 有用的内容：
- 分享链接解析
- 无水印视频下载
- 音频提取
- ASR 文案提取

因此，**单独发布时不再依赖外部 `douyin-video` skill**。

仍建议配合：
- `skills/playwright-cli`：浏览器打开、登录态复用、搜索、点击结果、读取页面参数

## 一键执行入口

```bash
python3 skills/douyin-video-skill/scripts/run_pipeline.py \
  --keyword "青少年无人机" \
  --pick-index 1 \
  --must-include 青少年 \
  --must-include 无人机 \
  --content-type-hint 培训 \
  --content-type-hint 科普 \
  --account-hint 教育 \
  --headed \
  --persistent
```

这个总控脚本会串起来：
- 打开抖音并复用登录态
- 搜索关键词
- 解析候选项并按参数筛选
- 点开目标视频
- 校验“当前弹层标题 == 目标搜索结果标题”
- 提取文案
- 修正文案
- 落盘 meta / source-link / transcript 系列文件

若你要发布到平台，可参考：
- `references/publish-copy.md`

## 推荐执行步骤

### A. 打开并复用登录态
使用 `playwright-cli`：

```bash
playwright-cli -s=douyinflow open https://www.douyin.com/ --headed --persistent
```

若未登录，允许用户手动完成登录。

### B. 搜索自定义关键词
例：

```bash
playwright-cli -s=douyinflow fill <search-box-ref> "青少年无人机"
playwright-cli -s=douyinflow click <search-button-ref>
```

### C. 根据筛选参数选视频
先读取 `references/filter-rules.md`。

至少考虑：
- `keyword`: 搜索词（自定义）
- `pickIndex`: 选第几个符合条件的结果（默认 1）
- `mustInclude`: 标题必须包含的词
- `excludeWords`: 标题/账号中要排除的词
- `minLikes`: 最低点赞量（可选）
- `preferRecentDays`: 优先最近多少天（可选）
- `durationMinSec`: 最短时长（可选）
- `durationMaxSec`: 最长时长（可选）
- `contentTypeHints`: 如 培训 / 科普 / 赛事 / 推荐 / 选购
- `accountHints`: 优先官方机构 / 教练 / 教育号 / 个人分享

### D. 进入视频后先做“标题一致性校验”
先记录：
- 目标搜索结果标题 `targetTitle`
- 当前页面 `modal_id`
- 当前弹层标题 `modalTitle`

**硬性校验规则：**
> 当前弹层标题 == 目标搜索结果标题
> 否则不能继续提取

执行：

```bash
python3 skills/douyin-video-skill/scripts/title_match_check.py \
  --expected "目标搜索结果标题" \
  --actual "当前弹层标题"
```

若脚本退出码非 0，必须停止提取并重新锁定目标视频。

### E. 通过校验后锁定 videoId
优先读取：

```js
new URL(location.href).searchParams.get('modal_id')
```

再组装：

```text
https://www.iesdouyin.com/share/video/<videoId>
```

### F. 调用本 skill 内置提取器提取文案

```bash
API_KEY="..." python3 skills/douyin-video-skill/scripts/douyin_downloader.py \
  --link "https://www.iesdouyin.com/share/video/<videoId>" \
  --action extract \
  --output ./output
```

### G. 落盘原始稿 / 修正版 / 修正说明
原始提取结果默认只有 `transcript.md`。

拿到原始文案后，必须再调用：

```bash
python3 skills/douyin-video-skill/scripts/transcript_cleanup.py \
  --title "视频标题" \
  --raw ./output/<videoId>/transcript.md \
  --outdir ./output/<videoId>
```

输出：
- `transcript-raw.md`
- `transcript-clean.md`
- `transcript-fixes.md`

## 参数约定

建议把一次任务的参数整理成：

```json
{
  "keyword": "青少年无人机",
  "pickIndex": 1,
  "mustInclude": ["青少年", "无人机"],
  "excludeWords": ["直播", "游戏直播", "纯广告"],
  "minLikes": 0,
  "preferRecentDays": 365,
  "durationMinSec": 15,
  "durationMaxSec": 120,
  "contentTypeHints": ["培训", "推荐", "科普"],
  "accountHints": ["教练", "教育", "俱乐部", "培训"]
}
```

## 这次实测暴露出的两个关键问题

### 问题 1：点开搜索结果后，当前视频可能不是你以为的那条
实测中，搜索结果点中了一条视频，但后续当前弹层的视频 `modal_id` 发生了变化，最终提取到的是另一条内容。

**改进要求（已固化为必须执行）：**
- 点开结果后，立即记录目标卡片标题
- 再读取当前页面 `modal_id`
- 再读取当前弹层标题
- 执行标题校验：**当前弹层标题 == 目标搜索结果标题**
- 若不一致，停止后续提取并重新锁定目标

### 问题 2：ASR 文案能提出来，但会有明显误识别
实测文案中出现了：
- 同音错字（如“靠挫力”应接近“抗挫力”）
- 语序不自然
- 重复词
- 对白角色混乱

**改进要求：**
- 提取后必须进入“文案修正”步骤
- 只修正高概率明显错误
- 不确定的地方保留并标注“待确认”

## 遇到过的实际问题

1. 抖音搜索结果页经常触发滑块验证，需要用户手动过一次
2. 分享按钮在 PC 页播放器浮层里不稳定，点击成本高
3. App 分享短链更稳定；对部分网页直链不稳定
4. `playwright-cli` 的 element ref 每次快照都会变，不能硬编码复用旧 ref
5. Python 依赖需要提前安装：
   - `requests`
   - `ffmpeg-python`
6. 当前弹层标题与目标搜索结果标题可能不一致，不能跳过校验直接提取

## 环境要求

### 1. `douyin-video` 已安装
路径：
```text
/Users/liyunzeng/.openclaw/workspace-douyin-analyst/skills/douyin-video
```

### 2. `playwright-cli` 可用
验证：
```bash
playwright-cli --version
```

### 3. API Key
当前 `douyin-video` 实际读取的是：
```bash
API_KEY
```
建议放在：
```bash
~/.openclaw/.env
```

### 4. FFmpeg
```bash
brew install ffmpeg
```

## 输出要求

每次完整执行后，最终目录建议为：

```text
output/<videoId>/
├── meta.json
├── source-link.txt
├── transcript.md
├── transcript-raw.md
├── transcript-clean.md
└── transcript-fixes.md
```

其中：
- `meta.json`：标题、关键词、视频ID、筛选参数、提取时间
- `source-link.txt`：最终用于提取的链接
- `transcript.md`：原始 skill 产物
- `transcript-raw.md`：保留原始转写
- `transcript-clean.md`：修正版文案
- `transcript-fixes.md`：修正记录与待确认项

## 不要做的事

- 不要把分享按钮点击成功作为唯一成功条件
- 不要直接信任 ASR 文案用于分析
- 不要在未校验标题一致性前就进入提取
- 不要把搜索 ref、点击 ref 写死成固定编号
- 不要改动小红书团队相关 skill 或规范
