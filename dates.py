# -*- coding: utf-8 -*-
"""Date extraction — deadlines only, never shipping dates."""
import re
from datetime import datetime, timezone, timedelta

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

_ISO = re.compile(r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b")
_MDY = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+"
                  r"(\d{1,2})(?:st|nd|rd|th)?,?\s*(20\d{2})?\b", re.I)
_DMY = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+"
                  r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?,?\s*"
                  r"(20\d{2})?\b", re.I)
_US = re.compile(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?:/(20\d{2}))?(?![\d/])")
_CN = re.compile(r"(?:(\d{4})\s*年\s*)?(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]")

# a deadline must be introduced by one of these
CUE = re.compile(
    r"(?:\bends?\b|\bexpir\w*\b|\bdeadline\b|\bvalid (?:until|through)\b|"
    r"\boffer ends\b|\bpromotion ends\b|\bcollect until\b|\bcloses?\b|"
    r"\buntil\b|\bthrough\b|截止|到期|活动时间|有效期|截止日期)", re.I)

# if the matched window contains these, it is very likely not an offer deadline
ANTI = re.compile(
    r"(?:free shipping|shipping|delivery|arrives|estimated|ships? by|"
    r"clinical trial|research trial|trial result|posted|updated|published|"
    r"as of|last seen|read more)", re.I)


def _mk(y, m, d):
    if not (1 <= m <= 12 and 1 <= d <= 31):
        return None
    if y is None:
        return (m, d, None)
    if 2000 <= y <= 2100:
        return (m, d, y)
    return None


def _scan(text):
    t = text or ""
    m = _ISO.search(t)
    if m:
        return _mk(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = _CN.search(t)
    if m:
        y = int(m.group(1)) if m.group(1) else None
        return _mk(y, int(m.group(2)), int(m.group(3)))
    m = _MDY.search(t)
    if m:
        y = int(m.group(3)) if m.group(3) else None
        return _mk(y, MONTHS[m.group(1).lower()[:3]], int(m.group(2)))
    m = _DMY.search(t)
    if m:
        y = int(m.group(3)) if m.group(3) else None
        return _mk(y, MONTHS[m.group(2).lower()[:3]], int(m.group(1)))
    m = _US.search(t)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        y = int(m.group(3)) if m.group(3) else None
        if a <= 12:
            return _mk(y, a, b)
        if b <= 12:
            return _mk(y, b, a)
    return None


def _resolve(mm, dd, yy, now):
    """Nearest sensible year when the text omits it."""
    if yy:
        return "%04d-%02d-%02d" % (yy, mm, dd)
    for year in (now.year, now.year + 1):
        try:
            cand = datetime(year, mm, dd, tzinfo=timezone.utc)
        except ValueError:
            return None
        if cand.date() >= (now - timedelta(days=60)).date():
            return cand.strftime("%Y-%m-%d")
    return None


def find(title, body, now=None):
    """Return YYYY-MM-DD or None. Requires a deadline cue near the date."""
    now = now or datetime.now(timezone.utc)
    for text in (title or "", body or ""):
        for cue in CUE.finditer(text):
            seg = text[max(0, cue.start() - 40): cue.start() + 120]
            if ANTI.search(seg):
                continue
            got = _scan(seg)
            if not got:
                continue
            return _resolve(got[0], got[1], got[2], now)
    return None
