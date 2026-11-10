# GLOBAL DEAL HUNTER · 全球羊毛情报中心

一个真实运行的全球优惠情报站：**采集 → 分类 → 打分 → 核链 → 静态看板**。
不是一个提示词 demo —— `/workspace/deal-hunter` 的代码每 2 小时往 SQLite 写真实数据，
再把静态站发到 GitHub Pages。

- 站点：https://wenjianmin24-pixel.github.io/deal-hunter/
- 仓库：https://github.com/wenjianmin24-pixel/deal-hunter

## 流水线

| 阶段 | 文件 | 说明 |
|---|---|---|
| 采集 | `collect.py` | 29 个源，每轮约 2900 条原始条目；RSS/Atom + Binance CMS JSON |
| 分类 | `classify.py` | 类别 / 价格类型 / 领取条件 / 地区 / 风险 / 价值，纯正则、可解释 |
| 截止日 | `dates.py` | 必须命中 ends/截止/until 等提示词，并排除 shipping、clinical trial |
| 核链 | `verify.py` | 逐条访问官方链接，记录状态与最终 URL，区分 ok / blocked / dead |
| 导出 | `export.py` | 生成纯静态 `site/`，无后端 |
| 看板 | `index.html` | 单页，分类 tab + 搜索 + 条件行 + 截止日 |

## 铁律

1. **不编**。抽不到就留空，页面显示「—」。
2. **价格不是优惠**。`$59.99` 不算价值，只有「get $20 back」这类奖励措辞才算。
3. **区分代价**：完全免费 / 免费试用 / 需充值 / 需存款 / 需消费 / 需交易量 / 需邀请 / 折扣。
   一个「$300 bonus，但要工资直存」的条目不是免费。
4. **核过才叫核过**。2xx 才 ✓；403/429 是「站点拒绝自动访问」，不等于活动失效，单列；404/410 才是死链。
5. **截止日期必须有语义提示**，正文里随便捞的日期不算数。
6. **数据新鲜度按源区分**：银行奖励 400 天仍可领，Slickdeals 报价一周就死。

## 用法

    python3 collect.py                     # 抓一轮，写 hunter.db
    python3 verify.py --limit 80 --all     # 核链接
    python3 export.py site                 # 导出静态站
    python3 -m http.server 8099 -d site    # 本地预览（仅 box 内可达）

## 自动化

box 上没有 cron 守护进程、也没有 `crontab` 二进制，所以调度交给 GitHub Actions：

- `.github/workflows/hunt.yml`：`cron: "11 */2 * * *"` + 手动 dispatch + push 触发。
- 每次跑 collect → verify(80) → export → 把 `hunter.db` 提交回 main → 发布 Pages。
- box 休眠、关机都不影响；站点和数据都在 GitHub 上。

## 数据源（全部实测可达）

**Deal 原生源**：Slickdeals（综合/免费试用/ChatGPT/Claude/AI 订阅/VPN/云主机/Gemini/学生优惠/信用卡/云额度 共 11 个关键词 feed）、
Doctor of Credit ×2、Frequent Miler、LowEndBox、
**Binance CMS API** ×2（空投公告 catalogId=128、活动公告 catalogId=93，RSS 端点 405/301，JSON 可用）。

**新闻/信号源**：Google News（空投/积分空投/测试网激励/交易所活动/AI 免费额度/银行开户/虚拟卡/免费额度）、
Product Hunt、OpenAI News、Google AI Blog、Hugging Face、HN free tier、
Kraken Blog、AMBCrypto、BeInCrypto、U.Today、少数派、V2EX。

**实测不可用（已剔除，不当成"已实现"）**：Reddit `.json` 403、`.rss` 间歇 429；
airdrops.io / cryptorank.io / defillama 空投页 403；mydealz / dealabs / ozbargain / dealnews RSS 404；
coinbase blog 403；binance 公告 RSS 端点 405（改用 CMS JSON）。

## 已知边界（不假装）

- **没有 LLM 参与判断**。分类是正则，宁可漏也不乱标；质量靠「留空」而不是靠猜。
- **只读标题 + 摘要（RSS 里的 content/description）**，不抓正文页。
  所以「参与步骤」「精确价值」多数为空 —— 这是诚实的空，不是没做。
- **条件是关键词推断**，页面上的「条件：」行来自原文措辞，未逐条人工核对（tooltip 已写明）。
- **地区覆盖偏美国**。U 卡/海外银行只有 DoC 与 Frequent Miler 两个英文源。
- **空投没有付费数据源**。Binance 官方公告 + Google News 检索是目前唯一免费可达的路径，
  所以「今天所有新空投」做不到，只能做到「今天被公开报道/官方公告的空投」。
- **核链只是可达性**。链接 200 不等于活动还活着，最终要人点进去看细则。
