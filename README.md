# GLOBAL DEAL HUNTER · 全球羊毛情报中心

一个真实运行的全球优惠情报站：**采集 → 分类 → 打分 → 核链 → 静态看板**。
它不是一个提示词 demo —— `/workspace/deal-hunter` 里的代码每跑一轮都往 SQLite 里写真实数据。

## 它到底做了什么

| 阶段 | 文件 | 说明 |
|---|---|---|
| 采集 | `collect.py` | 21 个 RSS/Atom 源，每轮约 2700 条原始条目 |
| 分类 | `classify.py` | 类别 / 价格类型 / 地区 / 风险 / 价值，纯正则、可解释 |
| 截止日 | `dates.py` | 必须命中「ends / 截止 / until」等提示词，并排除 shipping、clinical trial |
| 核链 | `verify.py` | 逐条访问官方链接，记录 HTTP 状态与最终 URL |
| 导出 | `export.py` | 生成纯静态 `site/`，无后端 |
| 看板 | `index.html` | 单页，分类 tab + 搜索 + 截止倒数 |

## 铁律（照着需求里最实在的那句话来的）

1. **不编**。字段抽不到就留空，页面上显示「—」。
2. **价格不是优惠**。`$59.99` 不会被算成价值，只有 "get $20 back" 这种奖励措辞才算。
3. **区分五种价格类型**：完全免费 / 免费试用 / 需充值 / 需交易量 / 需邀请，另有折扣与未标注。
4. **核过才叫核过**。`verify_status=200` 才显示 ✓，403/404/超时显示「!code」或「未核」。
5. **截止日期必须有语义提示**，从正文里随便捞出来的日期不算数。

## 用法

    python3 collect.py             # 抓一轮，写 hunter.db
    python3 verify.py --limit 200  # 核一遍链接
    python3 export.py site         # 导出静态站
    python3 -m http.server 8099 -d site   # 本地预览

## 自动化

Box 上没有 cron 常驻进程，所以是双层设计：

- **box 内**：`run_cycle.sh` 串起 collect → verify → export，可被任意调度器调用。
- **GitHub Actions**：`.github/workflows/collect.yml` 每 2 小时跑一次（与需求里的「每 2 小时」一致），
  把 `hunter.db` 提交回仓库并发布 GitHub Pages —— box 休眠时站点仍然是活的。

## 数据源（全部实测可达）

Deal 原生源：Slickdeals(free)、Doctor of Credit(银行奖励)、Frequent Miler、LowEndBox、r/deals。
信号源：OpenAI News、Google AI Blog、Hugging Face Blog、Product Hunt、Hacker News(free tier)、
CoinDesk、The Block、Blockworks、CoinTelegraph、Decrypt、CryptoSlate、Bitcoin Magazine、
少数派、V2EX。

实测不可用（已剔除，不当成"已实现"）：Reddit 的 `.json` 接口 403、`.rss` 间歇 429；
mydealz / dealabs RSS 404；airdrops.io 与 cryptorank 403；smzdm feed 只有 1.7KB 空壳。

## 已知边界（不假装）

- **没有 LLM 参与判断**。分类是正则，宁可漏也不乱标；「待核实」由 `verify_status` 表达。
- **只抓标题 + 摘要**，不抓正文页，所以「参与步骤」「实际价值」多数为空 —— 这是诚实的空。
- **U 卡 / 海外银行** 只有 Doctor of Credit 与 Frequent Miler 两个英文源，覆盖偏美国。
