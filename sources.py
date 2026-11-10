# -*- coding: utf-8 -*-
"""GLOBAL DEAL HUNTER — data sources.

Every URL here was fetched with HTTP 200 from the box at build time
(see README "sources probed"). Each source declares how its items may enter:

  native=True    the feed IS a deal feed — items enter as-is   the TITLE must match one of these; used on keyword-search
                 feeds, where a loose query drags in anything ("gemini
                 advanced" returned Google TVs)
  native=False   a news/launch feed — must state an OFFER, and must be recent

deny_domains blocks SEO spam publishers that Google News surfaces for
"free trial" queries.
"""

CATEGORIES = {
    "ai":       "AI 订阅与工具",
    "crypto":   "Crypto 空投与积分",
    "card":     "U 卡与虚拟卡",
    "bank":     "海外银行开户奖励",
    "cloud":    "VPS 与云服务",
    "software": "软件与数字服务",
    "other":    "其他全球优惠",
}

CATEGORY_RULES = [
    ("cloud",    ["vps", "dedicated server", "cloud credit", "hosting", "kubernetes",
                  "free tier", "object storage", "cdn", "domain name", "ssl cert",
                  "colocation", "bare metal", "server"]),
    ("crypto",   ["airdrop", "testnet", "mainnet", "staking", "defi", "nft",
                  "exchange", "binance", "okx", "bybit", "coinbase", "kraken",
                  "空投", "积分", "wallet drop", "points program", "token claim"]),
    ("bank",     ["checking account", "savings account", "bank bonus", "direct deposit",
                  "account bonus", "开户奖励", "开户", "high-yield", "apy"]),
    ("card",     ["virtual card", "debit card", "credit card", "cashback", "cash back",
                  "u卡", "虚拟卡", "返现", "amex offer", "prepaid card"]),
    ("ai",       ["chatgpt", "claude", "gemini", "midjourney", "suno", "openai",
                  "anthropic", "llm", "copilot", "perplexity", "grok", "cursor",
                  "stable diffusion", "hugging face"]),
    ("software", ["app", "saas", "software", "license", "subscription", "lifetime deal",
                  "bundle", "plugin", "extension"]),
]

PRICE_RULES = [
    ("invite", ["invite only", "invite-only", "by invitation", "invitation only",
                "邀请制", "邀请码", "only invited"]),
    ("volume", ["trading volume", "trade volume", "deposit and trade", "volume requirement",
                "transaction volume", "交易量", "trading requirement", "wagering"]),
    ("topup",  ["first deposit", "minimum deposit", "top up", "top-up", "recharge",
                "需要充值", "充值", "deposit of", "fund your account"]),
    ("trial",  ["free trial", "trial", "试用", "day trial", "week trial"]),
    ("free",   ["100% free", "completely free", "free forever", "no cost", "free of charge",
                "免费", "always free", "no credit card required"]),
]

# SEO spam that shows up for "free trial" / "airdrop" news queries
DENY_DOMAINS = [
    "law.com", "universitat", "prnewswire.com", "openpr.com", "einpresswire.com",
    "marketwatch.com/press-release", "apnews.com/press-release", "techbullion.com",
    "nyweekly.com", "businessinsider.com/press", "wral.com", "telegram.me",
    "coingabbar.com", "coin gabbar", "fello ai", "bitcoin foundation",
]

SOURCES = [
    # ------------------------------------------------ deal-native (no gate)
    dict(name="Slickdeals · 综合", category="software", native=True, weight=1.0,
         url="https://slickdeals.net/newsearch.php?rss=1&searcharea=deals&searchin=first&q=free"),
    dict(name="Doctor of Credit · 银行奖励", max_age=400, category="bank", native=True, weight=1.5,
         url="https://www.doctorofcredit.com/feed/?cat=bank-account-promotions"),
    dict(name="Doctor of Credit", max_age=400, category="bank", native=True, weight=1.2,
         url="https://www.doctorofcredit.com/feed"),
    dict(name="Frequent Miler", max_age=180, category="card", native=True, weight=1.2,
         url="https://www.frequentmiler.com/feed/"),
    dict(name="LowEndBox · VPS", category="cloud", native=True, weight=1.4,
         url="https://lowendbox.com/feed/"),
    # r/deals was removed: every item is physical retail (wreaths, airfryers,
    # vacuums) and reddit 429s the box intermittently.

    # ------------------------------------------------ keyword-scoped deals
    # A query feed needs a must-match: Slickdeals search is OR-ish and happily
    # returns a TV for "gemini advanced".
    dict(name="Slickdeals · ChatGPT/OpenAI", max_age=90, category="ai", native=True, weight=1.4,
         url="https://slickdeals.net/newsearch.php?searcharea=deals&q=chatgpt&rss=1", sale=True,),
    dict(name="Slickdeals · Claude/Anthropic", max_age=150, category="ai", native=True, weight=1.4,
         url="https://slickdeals.net/newsearch.php?searcharea=deals&q=claude+ai&rss=1", sale=True,),
    dict(name="Slickdeals · AI 订阅", category="ai", native=True, weight=1.2,
         url="https://slickdeals.net/newsearch.php?searcharea=deals&q=AI+subscription&rss=1", sale=True,),
    dict(name="Slickdeals · VPN", category="software", native=True, weight=1.1,
         url="https://slickdeals.net/newsearch.php?searcharea=deals&q=vpn&rss=1", sale=True,),
    dict(name="Slickdeals · 云主机", category="cloud", native=True, weight=1.2,
         url="https://slickdeals.net/newsearch.php?searcharea=deals&q=hosting&rss=1", sale=True,),
    dict(name="Slickdeals · 免费试用", category="software", native=True, weight=1.1,
         url="https://slickdeals.net/newsearch.php?searcharea=deals&q=free+trial&rss=1", sale=True,),

    dict(name="Slickdeals · Gemini", category="ai", native=True, weight=1.2,
         url="https://slickdeals.net/newsearch.php?searcharea=deals&q=gemini+ai&rss=1", sale=True),
    dict(name="Slickdeals · 学生优惠", max_age=120, category="software", native=True, weight=1.2,
         url="https://slickdeals.net/newsearch.php?searcharea=deals&q=student+discount&rss=1", sale=True),
    dict(name="Slickdeals · 信用卡奖励", max_age=90, category="card", native=True, weight=1.3,
         url="https://slickdeals.net/newsearch.php?searcharea=deals&q=credit+card+bonus&rss=1", sale=True),
    dict(name="Slickdeals · 云服务额度", max_age=90, category="cloud", native=True, weight=1.2,
         url="https://slickdeals.net/newsearch.php?searcharea=deals&q=cloud+credits&rss=1", sale=True),
    dict(name="Google News · 免费额度", category="software", native=False, weight=1.1,
         url="https://news.google.com/rss/search?q=%22free+credits%22+OR+%22free+tier%22+launch+when:10d&hl=en-US&gl=US&ceid=US:en",
         deny=DENY_DOMAINS),

    # ------------------------------------------------ news feeds (gated)
    dict(name="Product Hunt", category="ai", native=False, weight=1.1,
         url="https://www.producthunt.com/feed"),
    dict(name="OpenAI News", category="ai", native=False, weight=1.3,
         url="https://openai.com/news/rss.xml"),
    dict(name="Google AI Blog", category="ai", native=False, weight=1.1,
         url="https://blog.google/technology/ai/rss/"),
    dict(name="Hugging Face Blog", category="ai", native=False, weight=1.0,
         url="https://huggingface.co/blog/feed.xml"),
    dict(name="Hacker News · free tier", category="cloud", native=False, weight=1.1,
         url="https://hnrss.org/newest?q=free+tier"),
    dict(name="Kraken Blog", category="crypto", native=False, weight=1.1,
         url="https://blog.kraken.com/feed"),

    # ------------------------------------------------ Google News queries
    # The only crypto-airdrop coverage that survives without a paid API:
    # airdrops.io / cryptorank / defillama all answer 403 to the box.
    dict(name="Google News · 空投", category="crypto", native=False, weight=1.2,
         url="https://news.google.com/rss/search?q=crypto+airdrop+claim+when:14d&hl=en-US&gl=US&ceid=US:en", deny=DENY_DOMAINS),
    dict(name="Binance · 活动公告", category="crypto", native=True, weight=1.2, kind="json",
         url="https://www.binance.com/bapi/composite/v1/public/cms/article/catalog/list/query?catalogId=93&pageNo=1&pageSize=20", detail_dates=True),
    dict(name="Binance · 空投公告", category="crypto", native=True, weight=1.3, kind="json",
         url="https://www.binance.com/bapi/composite/v1/public/cms/article/catalog/list/query?catalogId=128&pageNo=1&pageSize=20", detail_dates=True),
    dict(name="Google News · 空投领取", category="crypto", native=False, weight=1.3,
         url="https://news.google.com/rss/search?q=airdrop+claim+when:7d&hl=en-US&gl=US&ceid=US:en", deny=DENY_DOMAINS),
    dict(name="Google News · 空投快照", category="crypto", native=False, weight=1.2,
         url="https://news.google.com/rss/search?q=airdrop+snapshot+when:7d&hl=en-US&gl=US&ceid=US:en", deny=DENY_DOMAINS),
    dict(name="Google News · 测试网积分", category="crypto", native=False, weight=1.1,
         url="https://news.google.com/rss/search?q=testnet+points+program+when:14d&hl=en-US&gl=US&ceid=US:en", deny=DENY_DOMAINS),
    dict(name="Google News · 银行奖励 2", category="bank", native=False, weight=1.1, max_age=120,
         url="https://news.google.com/rss/search?q=bank+account+bonus+%24300+when:21d&hl=en-US&gl=US&ceid=US:en", deny=DENY_DOMAINS),
    dict(name="Google News · 空投 2", category="crypto", native=False, weight=1.2,
         url="https://news.google.com/rss/search?q=%22airdrop%22+%22how+to+qualify%22+OR+%22claim+portal%22+when:10d&hl=en-US&gl=US&ceid=US:en", deny=DENY_DOMAINS),
    dict(name="Google News · 积分空投", category="crypto", native=False, weight=1.1,
         url="https://news.google.com/rss/search?q=points+program+snapshot+token+launch+when:10d&hl=en-US&gl=US&ceid=US:en", deny=DENY_DOMAINS),
    dict(name="Google News · 测试网激励", category="crypto", native=False, weight=1.0,
         url="https://news.google.com/rss/search?q=testnet+incentive+OR+%22mainnet+launch%22+reward+when:10d&hl=en-US&gl=US&ceid=US:en", deny=DENY_DOMAINS),
    dict(name="Google News · 交易所活动", category="crypto", native=False, weight=1.1,
         url="https://news.google.com/rss/search?q=exchange+%22sign+up+bonus%22+OR+%22trading+reward%22+when:14d&hl=en-US&gl=US&ceid=US:en",
         deny=DENY_DOMAINS),
    dict(name="Google News · AI 免费额度", category="ai", native=False, weight=1.2,
         url="https://news.google.com/rss/search?q=%22AI%22+%22free+trial%22+OR+%22free+credits%22+when:14d&hl=en-US&gl=US&ceid=US:en",
         deny=DENY_DOMAINS),
    dict(name="Google News · 银行开户奖励", category="bank", native=False, weight=1.2,
         url="https://news.google.com/rss/search?q=bank+account+bonus+OR+%22sign-up+bonus%22+when:14d&hl=en-US&gl=US&ceid=US:en",
         deny=DENY_DOMAINS),
    dict(name="Google News · 虚拟卡", category="card", native=False, weight=1.1,
         url="https://news.google.com/rss/search?q=%22virtual+card%22+OR+%22crypto+card%22+cashback+when:14d&hl=en-US&gl=US&ceid=US:en",
         deny=DENY_DOMAINS),

    # ------------------------------------------------ CN
    dict(name="少数派", category="software", native=False, weight=1.0,
         url="https://sspai.com/feed"),
    dict(name="V2EX", category="software", native=False, weight=0.8,
         url="https://www.v2ex.com/index.xml"),
]
