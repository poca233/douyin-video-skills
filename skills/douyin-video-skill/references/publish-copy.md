# Publish Copy for douyin-video-skill

## Short title
Douyin Video Skill

## Chinese title
抖音视频搜索筛选与文案提取修正 Skill

## One-line pitch
从抖音搜索结果里自动筛选合适视频，校验当前视频是否正确，再提取并修正视频文案。

## Short description
适用于抖音二次创作、竞品分析、素材采集。支持：
- 自定义搜索词
- 登录后网页搜索与筛选
- 结果视频锁定与标题一致性校验
- 视频文案提取
- 文案修正与三份文件落盘

## Full description
这是一个面向抖音素材采集与文本提取的完整工作流 skill。

它解决的不只是“给我一个分享链接，然后提文案”，而是更前面的真实工作流：
1. 打开抖音并复用登录态
2. 搜索自定义关键词
3. 按筛选参数选择候选视频
4. 点进视频后校验“当前弹层标题 == 目标搜索结果标题”
5. 用稳定视频链接提取文案
6. 对 ASR 结果进行语义修正
7. 输出原始稿、修正版、修正说明

特别适合：
- 抖音二次创作前的素材采集
- 竞品视频文案拆解
- 训练 analyst / planner 使用统一流程
- 需要稳定、可复盘、可落盘的文案提取流程

## Key selling points
- 不把“复制链接”当唯一依赖
- 优先使用 modal_id 组装稳定视频链接
- 内置标题一致性校验，避免点错视频还继续提取
- 支持自定义搜索词和筛选参数
- 提取后自动输出 transcript-raw / transcript-clean / transcript-fixes
- 可单独发布，内置视频提取与文案修正能力

## Suggested tags
- douyin
- video
- transcript
- playwright
- scraping
- asr
- content-research
- creator-tools

## Release notes snippet
v1.0.0
- 内置抖音视频下载与文案提取能力
- 支持搜索结果筛选参数与自定义搜索词
- 新增标题一致性校验（当前弹层标题 == 目标搜索结果标题）
- 新增文案修正与落盘流程
