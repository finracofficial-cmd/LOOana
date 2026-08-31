# -*- coding: utf-8 -*-
"""2026-08-31: 「待つしかないのか」— いま季節の崖のどこにいるのかを実測で置く。"""
import csv, collections, datetime, pickle

R = pickle.load(open('/tmp/rep0830w.pkl', 'rb'))
SEA = {'4WAY','3WAYサーキュレーター','卓上冷感クーラー','5WAY腰掛けファン','瞬間冷却ハンディファン','接触冷感UVパーカー',
       '接触冷感UVアームカバー','瞬間冷感ポンチョ','完全遮光・接触冷感UVハット','形状記憶日傘','完全遮光・形状記憶',
       '偏光・調光サングラス','害虫ブロッカー','湯上がりガーゼワンピース'}

print('=== ① 直近7日(8/24-30)の利益を 季節物 / 通年 に割る ===')
rows = []
for n in set(R['N7']) | set(R['A7']):
    s = R['N7'].get(n, 0); k = R['K7'].get(n, 0); a = R['A7'].get(n, 0)
    if not s and not a: continue
    rows.append((n, s - k - a, n in SEA))
rows.sort(key=lambda x: -x[1])
sea = sum(p for _, p, s in rows if s); yr = sum(p for _, p, s in rows if not s)
for n, p, s in rows:
    if abs(p) >= 10000: print(f'  {"🌞季節" if s else "  通年"} {n:26} {p:>+10,.0f}')
print(f'\n  季節物 計 {sea:>+10,.0f} 円  ({sea/(sea+yr):.1%})')
print(f'  通年   計 {yr:>+10,.0f} 円  ({yr/(sea+yr):.1%})')
print(f'  ★季節物はもう全体の {sea/(sea+yr):.0%} しかない。**夏の崖はほぼ過ぎている**')

print('\n=== ② 1日あたり利益の推移（週・日〜土）===')
S = collections.defaultdict(lambda: [0, 0])
for r in csv.DictReader(open('data/daily/daily_sales.csv', encoding='utf-8')):
    S[r['date']][0] += int(r['gross']); S[r['date']][1] += int(r['disc'])
AD = collections.defaultdict(float)
for r in csv.DictReader(open('data/daily/daily_ad.csv', encoding='utf-8')):
    AD[r['date']] += float(r['cost'])
GM = 0.7306
wk = collections.defaultdict(lambda: [0, 0, 0])
for d in sorted(S):
    if d < '2026-07-12' or d > '2026-08-30': continue
    dt = datetime.date.fromisoformat(d); st = (dt - datetime.timedelta(days=(dt.weekday()+1) % 7)).isoformat()
    wk[st][0] += S[d][0]-S[d][1]; wk[st][1] += AD[d]; wk[st][2] += 1
print(f'{"週初":12} {"日数":>4} {"1日利益":>11} {"1日広告費":>11} {"MER":>6}')
prev = None
for w in sorted(wk):
    s, a, n = wk[w]
    if n < 7: continue
    p = (s*GM - a)/n
    arrow = '' if prev is None else (f'  {p/prev-1:+.0%}')
    print(f'{w:12} {n:>4} {p:>11,.0f} {a/n:>11,.0f} {s/a:>6.2f}{arrow}')
    prev = p
print('\n  ★底は 8/16週。そこから 2週連続で上がっている')
print(f'  目標18万/日・最低10万/日 に対して、直近週は {prev:,.0f}円/日')
