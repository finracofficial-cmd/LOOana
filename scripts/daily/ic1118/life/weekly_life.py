# -*- coding: utf-8 -*-
"""11/18 「よく売れる商品はなぜ売れる？長く売れ続けるものも」: 6/29〜11/15 の週（月〜日）ごとの商品別 倍率
売上＝daily_sales（gross−値引）・広告費＝daily_ad（キャンペーン名で商品に寄せる）・原価＝product_tabs の単価（売価がない商品は lifetime CSV の原価率）。近似"""
import csv, collections, datetime, json
src = open('../../../product_tabs.py', encoding='utf-8').read(); ns = {}
exec(src[src.index('COST = {'):src.index('TAB = {')], ns); COST, PRICE = ns['COST'], ns['PRICE']
LT = {r['商品']: r for r in csv.DictReader(open('../../../../data/product-lifetime-2026-10-17.csv'))}
SNAMES = sorted({r['name'] for r in csv.DictReader(open('../../../../data/daily/daily_sales.csv'))}, key=len, reverse=True)
FIX = {'ディスペンサー': '壁掛けディスペンサー', 'ネックマッサージャー2': 'ネックマッサージャー', '4WAY 取り付けOK 小型瞬間冷却ハンディファン': '4WAY', '完全遮光・形状記憶・晴雨兼用・UV日傘': '完全遮光・形状記憶'}
def prod(c):
    if c in FIX: return FIX[c]
    if c.startswith('カタログ'): return None
    base = c.rstrip('0123456789 ').rstrip('v').rstrip()
    for s in SNAMES:
        if base == s or base.startswith(s) or s.startswith(base): return s
    return c
def ltrow(p):
    return LT.get(p) or next((r for k, r in LT.items() if p in k or k in p), None)
def cogs(p, g):
    k = next((k for k in COST if k == p), None) or next((k for k in COST if k in p or p in k), None)
    if k and PRICE.get(k) and COST.get(k): return g / PRICE[k] * COST[k]
    r = ltrow(p)
    return g * float(r['原価率']) if r else None
wk = lambda d: (datetime.date.fromisoformat(d) - datetime.date(2026, 6, 29)).days // 7
W = collections.defaultdict(lambda: [0.0, 0.0, 0.0])  # (p, w) -> gross, disc, ad
for r in csv.DictReader(open('../../../../data/daily/daily_sales.csv')):
    if '2026-06-29' <= r['date'] <= '2026-11-15': v = W[(r['name'], wk(r['date']))]; v[0] += float(r['gross']); v[1] += abs(float(r['disc']))
for r in csv.DictReader(open('../../../../data/daily/daily_ad.csv')):
    p = prod(r['campaign'])
    if p and '2026-06-29' <= r['date'] <= '2026-11-15': W[(p, wk(r['date']))][2] += float(r['cost'])
NW = wk('2026-11-15') + 1
out = {}
for p in sorted({p for p, w in W}):
    ser = []
    for w in range(NW):
        g, dc, ad = W.get((p, w), [0, 0, 0])
        c = cogs(p, g)
        ser.append((w, ad, (g - dc - c) / ad if ad >= 10000 and c is not None else None, g - dc - (c or 0) - ad))
    act = [s for s in ser if s[2] is not None]
    if sum(s[1] for s in ser) < 100000: continue
    good = [s for s in act if s[2] >= 1.25]
    run = best = 0
    for s in ser:
        if s[2] is not None and s[2] >= 1.25: run += 1; best = max(best, run)
        elif s[2] is not None: run = 0
    r = ltrow(p)
    out[p] = dict(first=act[0][0] if act else None, active=len(act), good=len(good), longest=best, profit=round(sum(s[3] for s in ser)),
                  ad=round(sum(s[1] for s in ser)), b12=round(sum((s[2] or 0) * s[1] for s in act[:2]) / max(1, sum(s[1] for s in act[:2])), 2),
                  b_rest=round(sum((s[2] or 0) * s[1] for s in act[2:]) / max(1, sum(s[1] for s in act[2:])), 2) if len(act) > 2 else None,
                  season=r['季節'] if r else '', cat=r['カテゴリ'] if r else '', demo=r['実演性(2高/1中/0低)'] if r else '', alt=r['安価な代替(1あり)'] if r else '',
                  series=[None if s[2] is None else round(s[2], 2) for s in ser])
json.dump(out, open('weekly_life.json', 'w'), ensure_ascii=False, indent=0)
print(f'週 0＝6/29〜7/5 … 週 {NW-1}＝11/9〜15。広告費10万円以上の商品。「続いた週」＝倍率1.25以上の週が続いた最長')
for p, o in sorted(out.items(), key=lambda x: -x[1]['longest']):
    print(f"{p[:16]:<16} 開始週{o['first']:>2}・出した週{o['active']:>2}・1.25以上{o['good']:>2}週・続いた最長{o['longest']:>2}週・最初2週{o['b12']}→その後{o['b_rest']}・利益{o['profit']:>+11,}・{o['season']}/{o['cat']}/実演{o['demo']}/代替{o['alt']}")
