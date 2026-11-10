# -*- coding: utf-8 -*-
"""Classification — conservative, boundary-aware.

First-pass lesson: loose substring matching turned "clinical trial" into a free
trial, "free shipping" into a free product, and a speaker review into a deal.
English rules now use word boundaries; the keyword gate for news feeds too.
"""
import re

# ------------------------------------------------------------- price type
# The brief's core distinction is not "is it free" but "what does claiming it
# cost me". Ordered strictest first: the first rule that matches wins, so a
# "$300 bonus, direct deposit required" is labelled deposit, not free.
INVITE = re.compile(r"(?:\binvite[- ]only\b|\bby invitation\b|\binvitation only\b|"
                     r"\binvite friends\b|\breferral tournament\b|\brefer friends\b|"
                     r"\baffiliate (?:program|rewards?)\b|\brefer-a-friend\b|"
                    r"\bonly invited\b|仅限邀请|邀请码|邀请制)", re.I)
VOLUME = re.compile(r"(?:\btrading volume\b|\bvolume requirement\b|\bwagering\b|"
                     r"\btrading competition\b|\btrade (?:to|and) (?:share|earn)\b|"
                     r"\bspot taker\b|\bfutures tournament\b|\bvolume-based\b|"
                    r"\bturnover requirement\b|\btrade volume\b|交易量)", re.I)
TOPUP = re.compile(r"(?:\bfirst deposit\b|\bminimum deposit\b|\btop[ -]?up\b|"
                   r"\brecharge\b|\bdeposit of\b|\bfund your account\b|"
                   r"首充|充值|需充值|先充值)", re.I)
DEPOSIT = re.compile(r"(?:\bdirect deposit\b|\bpayroll deposit\b|\bqualifying deposit\b|"
                     r"\bdeposit (?:of )?\$\d|\bdirect-deposit\b|工资直存|需要存款)", re.I)
SPEND = re.compile(r"(?:\bspend\s+\$?\d|\bget\s+\$\d[\d,]*\s*(?:back|in credit)\b|"
                   r"\bwith\s+(?:a\s+)?\$\d[\d,]*\s+purchase\b|"
                   r"\bon\s+\$\d[\d,]*\s+(?:or more\s+)?purchases?\b|"
                   r"\bminimum spend\b|\bstatement credit\b|"
                   r"\b(?:purchase|spend)\s+\$\d[\d,]*\s*(?:&|and)\s*(?:get|receive)\b|"
                   r"消费满|满\d+减\d+)", re.I)
TRIAL = re.compile(r"(?:\bfree trial\b|\b\d{1,2}[- ]day (?:free )?trial\b|"
                   r"\b\d{1,2}[- ]week (?:free )?trial\b|\btrial period\b|"
                   r"\bfree for \d+ (?:days?|months?)\b|"
                   r"\b试用\b|\b体验版\b)", re.I)
FREE = re.compile(r"(?:\bfree forever\b|\bcompletely free\b|\b100% ?free\b|"
                  r"\balways free\b|\bno credit card required\b|\bfree of charge\b|"
                  r"\bfree tier\b|\bfree plan\b|\bfree credits?\b|\bgiveaway\b|"
                  r"\bfreebie\b|\bno cost\b|\bnow free\b|\bfree year\b|"
                  r"\bfree (?:of charge|access|license|licence)\b|"
                  r"免费领取|免费送|免费使用|免费额度|永久免费)", re.I)
DISCOUNT = re.compile(r"(?:\d{1,2}(?:\.\d+)?\s*%\s*(?:off|discount)|"
                      r"\$\s?\d[\d,]*\s*off\b|\bBOGO\b|\bbuy one get one\b|"
                      r"\bcash ?back\b|\bfee[- ]free\b|\bno annual fee\b|"
                      r"\bpromo code\b|\bcoupon\b|\bdiscount\b|"
                      r"立减|返现|优惠券|折扣)", re.I)

ORDER = [("invite", INVITE), ("volume", VOLUME), ("topup", TOPUP),
         ("deposit", DEPOSIT), ("spend", SPEND), ("trial", TRIAL),
         ("free", FREE), ("discount", DISCOUNT)]


def price_type(title, body):
    """Title first: the headline states the terms, the body is usually promo copy
    that mentions every currency figure on the page."""
    for text in (title or "", body or ""):
        if not text:
            continue
        for name, rx in ORDER:
            if rx.search(text):
                return name
    return "unknown"


# ---------------------------------------------------------------- category
CAT_RULES = [
    ("cloud", re.compile(r"(?:\bvps\b|\bdroplet\b|\bdedicated server\b|\bbare metal\b|"
                         r"\bcloud (?:credit|credits|hosting|compute)\b|\bfree tier\b|"
                         r"\bobject storage\b|\bkubernetes\b|\bcolocation\b|"
                         r"\bhosting\b|\b域名\b|\b云服务器\b|\b服务器\b)", re.I)),
    ("crypto", re.compile(r"(?:\bairdrop\b|\btestnet\b|\bmainnet\b|\bstaking\b|\bdefi\b|"
                          r"\bnft\b|\bbinance\b|\bokx\b|\bbybit\b|\bcoinbase\b|"
                          r"\bkraken\b|\bpoints program\b|\bwallet\b|\bmemecoin\b|"
                          r"空投|\b积分\b|\btoken\b|\bblockchain\b)", re.I)),
    ("bank", re.compile(r"(?:\bchecking account\b|\bsavings account\b|\bbank bonus\b|"
                        r"\bdirect deposit\b|\baccount bonus\b|\bhigh[- ]yield\b|"
                        r"\bapy\b|开户奖励|开户|\bbank\b)", re.I)),
    ("card", re.compile(r"(?:\bvirtual card\b|\bdebit card\b|\bcredit card\b|"
                        r"\bcash ?back\b|\bamex offer\b|\bprepaid card\b|\bu卡\b|"
                        r"虚拟卡|返现)", re.I)),
    ("ai", re.compile(r"(?:\bchatgpt\b|\bclaude\b|\bgemini\b|\bmidjourney\b|\bsuno\b|"
                      r"\bgoogle ai (?:pro|ultra|premium)\b|\bai pro plan\b|"
                      r"\b(?:chatgpt|claude|gemini) (?:plus|pro|team)\b|"
                      r"\bopenai\b|\banthropic\b|\bllm\b|\bcopilot\b|\bperplexity\b|"
                      r"\bgrok\b|\bcursor\b|\bstable diffusion\b|\bhugging ?face\b|"
                      r"\bfine-?tun\w*\b|\bgpt-?\d\b|\bAI (?:agent|model|tool)\b)", re.I)),
    ("software", re.compile(r"(?:\bsaas\b|\bsoftware\b|\blicen[cs]e\b|\blifetime deal\b|"
                            r"\bbundle\b|\bplugin\b|\bextension\b|\bsubscription\b|"
                            r"\bapp store\b|\bmac app\b|\bwindows app\b|"
                            r"\bvpn\b|\bantivirus\b|\bsecurity (?:suite|bundle)\b|"
                            r"\bpassword manager\b|\badblock\w*\b|\bnorton\b|"
                            r"\bmcafee\b|\bbitdefender\b|\bsurfshark\b|\bnordvpn\b|"
                            r"\bipvanish\b|\bmalwarebytes\b|\b1password\b)", re.I)),
]


def category(title, body, default):
    """Title wins over body: a bank post mentioning 'token' is still a bank post."""
    for text in (title or "", body or ""):
        if not text:
            continue
        for name, rx in CAT_RULES:
            if rx.search(text):
                return name
    return default


# ----------------------------------------------------------------- region
REGION_RULES = [
    ("美国", re.compile(r"(?:\bunited states\b|\bu\.?s\.? only\b|\busa only\b|"
                        r"\bus residents\b|\bin the us\b|\[us\]|美国)", re.I)),
    ("中国大陆", re.compile(r"(?:\bmainland china\b|中国大陆|国内用户)", re.I)),
    ("香港", re.compile(r"(?:\bhong kong\b|香港)", re.I)),
    ("新加坡", re.compile(r"(?:\bsingapore\b|新加坡)", re.I)),
    ("英国", re.compile(r"(?:\bunited kingdom\b|\buk only\b|\[uk\]|英国)", re.I)),
    ("欧盟", re.compile(r"(?:\beurope\b|\beu only\b|\beea\b|欧元区)", re.I)),
    ("全球", re.compile(r"(?:\bworldwide\b|\bglobal\b|\ball countries\b|"
                        r"\bany country\b|全球)", re.I)),
]


def region(title, body):
    hits = []
    for text in (title or "", body or ""):
        for name, rx in REGION_RULES:
            if name not in hits and rx.search(text):
                hits.append(name)
    return " / ".join(hits)


# ------------------------------------------------------------------ value
# Only reward phrasing becomes a value; a bare price is never a saving.
# "$300 Checking Bonus" is a reward; "$19.97" in a product title is not.
REWARD = [
    re.compile(r"(?:\$|USD\s?)(\d[\d,]*(?:\.\d+)?)\s*(?:in\s+)?(?:bonus|cash ?back|"
               r"back|credit|credits|statement credit|reward|sign[- ]?up bonus|"
               r"welcome bonus|refund)", re.I),
    # "$300 Checking Bonus" — a qualifier may sit between the figure and the noun
    re.compile(r"\$(\d[\d,]*(?:\.\d+)?)\s+(?:[A-Za-z-]+\s+){0,3}"
               r"(?:bonus|credit|reward|cash ?back)", re.I),
    re.compile(r"(?:earn|get|receive|claim|grab|bag|snag|score)\s+(?:up\s+to\s+)?"
               r"\$(\d[\d,]*(?:\.\d+)?)", re.I),
    re.compile(r"(?:\$|USD\s?)(\d[\d,]*(?:\.\d+)?)\s*in\s+"
               r"(?:credits?|value|usage)", re.I),
    re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*(?:美元|美金)?\s*(?:返现|返利|奖励|红包|立减)"),
]
PCT = re.compile(r"(\d{1,2}(?:\.\d+)?)\s*%\s*(?:off|discount|折扣)", re.I)


def value(title, body):
    """Only reward phrasing becomes a value; a bare price is never a saving.
    "$300 Checking Bonus" is a reward; "$19.97" in a product title is not."""
    for text in (title or "", body or ""):
        if not text:
            continue
        for rx in REWARD:
            m = rx.search(text)
            if m:
                try:
                    v = float(m.group(1).replace(",", ""))
                except ValueError:
                    continue
                if 0 < v <= 100000:
                    return "$%g" % v, v
        m = PCT.search(text)
        if m:
            try:
                p = float(m.group(1))
            except ValueError:
                continue
            if 0 < p <= 100:
                return "%g%% off" % p, None
    return "", None


# ------------------------------------------------------------------- risk
RISK_RULES = [
    ("需要 KYC / 实名", re.compile(r"(?:\bkyc\b|\bverify your identity\b|"
                                   r"\bidentity verification\b|实名)", re.I)),
    ("仅限新用户 / 首充", re.compile(r"(?:\bnew customer\b|\bnew user\b|\bnew account\b|"
                                    r"\bfirst deposit\b|新用户|首充)", re.I)),
    ("地区受限", re.compile(r"(?:\bonly available in\b|\bnot available in\b|"
                            r"\brestricted to\b|\bonly for\b|仅限)", re.I)),
    ("限量 / 先到先得", re.compile(r"(?:\bwhile supplies last\b|\blimited to the first\b|"
                                  r"数量有限|先到先得)", re.I)),
    ("推广 / 联盟链接", re.compile(r"(?:\baffiliate\b|\breferral\b|\bpromo code\b|推广)", re.I)),
    ("需交易量 / 投注要求", re.compile(r"(?:\bwagering\b|\btrading volume\b|交易量)", re.I)),
]


def risks(title, body):
    out = []
    for text in (title or "", body or ""):
        for name, rx in RISK_RULES:
            if name not in out and rx.search(text):
                out.append(name)
    return " · ".join(out)



# ------------------------------------------------ gate for news feeds
# A news item is only a deal if it states an OFFER, not merely uses "free".
# First pass let in "free tier graveyard" and "DALLE in beta": discussion, not
# something a reader can claim.
OFFER = [re.compile(p, re.I) for p in [
    r"\$\s?\d[\d,]*\s*(?:back|off|cash ?back|statement credit|credit|bonus)",
    r"\b(?:rewards?|prizes?|bonus pool)\s+up to\b",
    r"\bup to\s+\$?\d[\d,]*\s*(?:USDC|USDT|BNB|in rewards)\b",
    r"\b(?:share|split)\s+(?:of\s+)?\$?\d[\d,]*\s*(?:USDC|USDT|BNB)\b",
    r"\d{1,2}(?:\.\d+)?\s*%\s*(?:off|discount)",
    r"(?:get|earn|receive|claim|grab|snag)\s+\$?\d[\d,]*",
    r"\bfree trial\b", r"\bfree tier\b", r"\bfree plan\b", r"\bfree credits?\b",
    r"\bfree forever\b", r"\bcompletely free\b", r"\b100% ?free\b",
    r"\bno credit card required\b", r"\bgiveaway\b", r"\bfreebie\b",
    r"\bcoupon\b", r"\bpromo code\b", r"\bdiscount code\b",
    r"\bairdrop\b", r"\btestnet\b", r"\bpoints program\b",
    r"\bsign[- ]?up bonus\b", r"\bwelcome bonus\b",
    r"\breferral (?:bonus|reward|code)\b", r"\brefer a friend\b",
    r"\blifetime deal\b", r"\bnow free\b", r"\bgoes free\b", r"\bmade free\b",
    r"\bopen[- ]?sourced\b",
    r"免费领取", r"免费送", r"免费额度", r"免费使用", r"限时免费", r"永久免费",
    r"优惠券", r"折扣码", r"返现", r"空投", r"注册送", r"签到送", r"立减",
]]

# editorial / discussion markers disqualify an item even when it says "free"
NOISE = [re.compile(p, re.I) for p in [
    r"^\s*ask hn", r"^\s*show hn", r"^\s*tell hn", r"\bgraveyard\b",
    r"\bopinion\b", r"\beditorial\b", r"\bhands[- ]on\b",
    r"\b(?:why|how) (?:we|i) \b", r"\bwhat (?:we|i) learned\b",
    r"^\s*\[?(?:分享|问与答|讨论|闲聊|酷工作)", r"\bclinical trial\b",
    r"\btrial results?\b", r"\bdead\b.*\bfree tier\b",
    # airdrop bookkeeping, not a claimable offer: past-tense distribution news
    r"\bhas completed\b", r"\bcompletes (?:\d+\w*|second|third|fourth)\b",
    r"\bhas (?:now )?concluded\b", r"\bdistribution (?:to|is complete|complete)\b",
    r"\bsnapshot (?:is )?(?:taken|over|completed)\b", r"\bclaim period (?:has )?ended\b",
]]


def passes_gate_noise(title):
    """True when the title carries no editorial or closed-offer marker."""
    return not any(rx.search(title or "") for rx in NOISE)


def passes_gate(title, body=""):
    if any(rx.search(title or "") for rx in NOISE):
        return False
    text = (title or "") + " " + (body or "")
    return any(rx.search(text) for rx in OFFER)


# ------------------------------------------------------------ scope filter
# The feed "Slickdeals q=free" is mostly furniture, socket sets and boots, and
# r/deals is entirely consumer goods. The brief covers subscriptions, airdrops,
# cards, bank bonuses, cloud credit and software — so an item must name one of
# those to enter at all. "Free shipping" is a shipping term, not a price.
DIGITAL_MARK = re.compile(r"(?:\bsoftware\b|\blichen?[cs]e\b|\bsubscription\b|\bvpn\b|"
                          r"\bsaas\b|\bhosting\b|\bvps\b|\bdomain name\b|"
                          r"\bcloud (?:hosting|credits?|compute|storage|server)\b|"
                          r"\bstreaming\b|\bdownload code\b|"
                          r"\bchatgpt\b|\bclaude\b|\bgemini (?:advanced|pro|ultra)\b|"
                          r"\bopenai\b|\banthropic\b|\bcopilot\b|\bperplexity\b|"
                          r"\bmidjourney\b|\bcursor\b|\bsuno\b|"
                          r"\bai (?:subscription|assistant|agent|tools?|credits?)\b|"
                          r"\b(?:google|microsoft|apple|meta|amazon|verizon|t-mobile)\s+ai\b|"
                          r"\bai (?:pro|plus|premium|max)\b|\bcoursera\b|\budemy\b|"
                          r"\bairdrop\b|\bchecking (?:account|bonus)\b|"
                          r"\bsavings (?:account|bonus)\b|\bbank (?:bonus|account|promo)\b|"
                          r"\bvirtual card\b|\bcrypto (?:card|exchange|bonus)\b|"
                          r"\bexchange (?:bonus|promo|reward)\b|\bbitcoin\b|"
                          r"\b(?:microsoft|office ?365|adobe|norton|mcafee|bitdefender)\b|"
                          r"\b(?:netflix|spotify|youtube premium|disney\+|hulu)\b|"
                          r"\b(?:antivirus|password manager|online course|e-?learning)\b|"
                          r"\bhodler\b|\blaunchpool\b|\blaunchpad\b|"
                          r"\btrading competition\b|\breferral tournament\b|"
                          r"\baffiliate\b|\bearn campaign\b|\bappreciation campaign\b|"
                          r"\bspot taker\b|\bdeposit (?:campaign|promotion)\b|"
                          r"云服务器|服务器租用|会员|订阅|软件|域名|加速器)", re.I)

# A product listing that only names a brand in passing is still a product.
PHYS_MARK = re.compile(r"(?:\bfree shipping\b|\+\s*free\s+(?:shipping|s/h)\b|"
                       r"\bshipped and sold by\b|\bsold by\b|\bin[- ]store\b|"
                       r"\bwall touch screen\b|\bdigital calendar\b|"
                       r"\bsoundtrack\b|\bebook\b|\bkindle\b|\bpoints\b.*\bcanada\b)", re.I)
STRONG_SERVICE = re.compile(r"(?:\bsubscription\b|\bhosting\b|\bvps\b|\bvpn\b|"
                            r"\bchecking\b|\bsavings\b|\bairdrop\b|\bgift ?card\b|"
                            r"\blicen[cs]e\b|\bsoftware\b|\bcredits?\b)", re.I)

SWEEP = re.compile(r"(?:\bsweepstakes\b|\bdaily entry\b|\benter to win\b|\blottery\b|"
                   r"\bgiveaway\b|\bbonus entries\b|\bwin (?:a|an|the)\b|抽奖)", re.I)

# Price commentary is not an offer: "Aster Drops 3.26% Amid Airdrop" is market
# news about a token, not a way to claim one.
MARKET_NEWS = re.compile(r"(?:\bdrops? \d+(?:\.\d+)?%|\bsurges?\b|\bplunges?\b|"
                         r"\bsell-?off\b|\bmarket cap\b|\bamid\b)", re.I)

# Hardware that merely mentions an AI service is still hardware.
HARDWARE = re.compile(r"(?:\brouter\b|\bglasses\b|\bheadphones?\b|\bearbuds?\b|"
                      r"\bcamera\b|\bmonitor\b|\bkeyboard\b|\bmouse\b|"
                      r"\bssd\b|\bhard drive\b|\bconsole\b|\bspeaker\b|"
                      r"\btablet\b|\blaptop\b|\bphone\b|\bprojector\b|"
                      r"\bchromebook\b|\bsmart ?tv\b|\bqled\b|\bsoundbar\b|"
                      r"\bfire tv\b|\be-?reader\b|\bwatch\b|\bvacuum\b|"
                      r"\bheadset\b|\bwebcam\b|\bprinter\b|"
                      r"\bkindle\b|\bhardcover\b|\bpaperback\b|\btextbook\b|"
                      r"\btouch ?screen\b|\bdigital calendar\b|\b\d+(?:\.\d+)? ?inch\b)", re.I)

EDITORIAL = re.compile(r"(?:\binterview\b|\breview\b|\bopinion\b|\bhands[- ]on\b|"
                       r"\bis this\b|\bwhy (?:we|i|you)\b|\bhow to\b|\bwhat is\b|"
                       r"\bguide to\b|\btutorial\b|\bexplained\b|\bdeep ?dive\b|"
                       r"\bpodcast\b|\bwebinar recap\b|\babout those\b|\bshould you (?:buy|get)\b|"
                       r"\bis coming soon\b|\bhere are the\b|专访|评测|盘点|"
                       # roundup listicles: "PNC Bank Promotions: $100, $400..." is a
                       # directory page, not one claimable offer
                       r"\bpromotions?\s*:|\b\d+\s+best\b|"
                       r"\bbest\s+(?:bank|credit|checking|savings|vpn|hosting|deal)\b|"
                       r"\btop\s+\d+\s+(?:bank|card|deal|vpn))", re.I)


def in_scope(title, body=""):
    """Returns (keep, reason). Editorial pieces, lotteries and physical retail
    are out; everything else must name a digital/financial product."""
    t = (title or "").strip()
    if len(t) < 14:
        return False, "title too vague"
    if SWEEP.search(t):
        return False, "sweepstakes"
    if MARKET_NEWS.search(t):
        return False, "market news"
    # "No Subscription" on a wall screen is a selling point for the gadget, not
    # a subscription deal — the escape hatch must not fire on a negation.
    if HARDWARE.search(t) and not (re.search(r"\bsubscription\b|\bcredit", t, re.I)
                                   and not re.search(r"\bno subscription\b", t, re.I)):
        return False, "hardware"
    # A named single offer survives the editorial rule even when its headline
    # reads like a how-to ("Live Oak is offering a $300 savings bonus — here's
    # how to get it"); a listicle or a "Promotions:" directory page does not.
    if EDITORIAL.search(t) and not re.search(r"\bairdrop\b", t, re.I):
        concrete = re.search(r"\$\s?\d[\d,]*", t) and \
                   re.search(r"\b(?:bonus|offer|promotion|credit|reward|trial|"
                             r"subscription|plan|deal)\b", t, re.I)
        listicle = re.search(r"\b\d+\s+best\b|\bbest\s+(?:bank|credit|checking|"
                             r"savings|vpn|hosting|deal)\b|\btop\s+\d+\b|"
                             r"\bpromotions?\s*:", t, re.I)
        if not (concrete and not listicle):
            return False, "editorial"
    if not DIGITAL_MARK.search(t):
        return False, "not a digital/finance offer"
    if (PHYS_MARK.search(t) or PHYS_MARK.search(body or ""))             and not STRONG_SERVICE.search(t):
        return False, "physical goods"
    return True, ""
