# -*- coding: utf-8 -*-
"""前の日のスクリプトから次の日のスクリプトを作るための道具（日付の文字だけを1日進める）。
使い方（Python から）: from shift_day import shift, rep
  shift(text, {'1126','1125','1124'})  … MMDD・MM/DD・MM-DD（2026-MM-DD を含む）の形で、集合にある日だけを +1日。1回の走査で置き換えるので二重には進まない
  rep(text, a, b, n)                   … a を b に置き換える。ちょうど n 回でなければ止まる（黙って外さないため）
週の区切り（「11/18〜24」の 24 など）・曜日・その日だけの数字は進まないので、rep で直す"""
import re, datetime
def shift(s, days, year=2026):
    def f(m):
        mm, sep, dd = m.group(1), m.group(2), m.group(3)
        if mm + dd not in days: return m.group(0)
        d = datetime.date(year, int(mm), int(dd)) + datetime.timedelta(1)
        return f'{d.month:02d}{sep}{d.day:02d}'
    return re.sub(r'(?<!\d)(1[0-2]|0[1-9])([-/]?)([0-3]\d)(?!\d)', f, s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:60], s.count(a), n)
    return s.replace(b, b) if a == b else s.replace(a, b)
