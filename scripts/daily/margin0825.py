# -*- coding: utf-8 -*-
"""利益率の改善が「新商品の広告効率」で説明できるかを検証する。実測のみ・毎回ゼロから積み直す。"""
import csv, collections, datetime, runpy
g = runpy.run_path('scripts/daily/w0824.py')
Sd, ADd, MAP = g['S'], g['AD'], g['MAP']
COST, PRICE = dict(g['COST']), dict(g['PRICE'])
COST['ナノガラス脱毛パッド'] = (855*757 + 373*740)/1228          # 30日実測ミックスの加重平均【近似】
COST['壁掛けディスペンサー'] = (41*2528 + 13*1981)/54
PRICE['壁掛けディスペンサー'] = 363920/54
INV = {v: k for k, v in MAP.items()}

# ---- 出稿開始日でコホートを機械的に決める（手で分類しない）----
first = {}
for cp, v in ADd.items():
    ds = sorted(d for d, c in v.items() if c > 0)
    if ds: first[INV.get(cp, cp)] = ds[0]
NEW = {n for n, d in first.items() if d >= '2026-08-01' and n != 'カタログ全部（テスト）'}
SEA = {'4WAY','3WAYサーキュレーター','卓上冷感クーラー','5WAY腰掛けファン','瞬間冷却ハンディファン','接触冷感UVパーカー',
'接触冷感UVアームカバー','瞬間冷感ポンチョ','完全遮光・接触冷感UVハット','形状記憶日傘','完全遮光・形状記憶',
'偏光・調光サングラス','害虫ブロッカー','湯上がりガーゼワンピース'}
ALLN = {n for n in Sd if n}
NEW -= SEA                       # 季節物に入るものは季節物として扱う（二重計上しない）
OLD = ALLN - NEW - SEA
print('■ コホート（出稿開始日で機械分類）')
print(f'  新商品({len(NEW)}): ' + '・'.join(f'{n}[{first.get(n,"—")}]' for n in sorted(NEW, key=lambda x: first.get(x,''))))
print(f'  既存通年({len(OLD)}): ' + '・'.join(sorted(OLD)))
print(f'  季節物({len(SEA & ALLN)}): ' + '・'.join(sorted(SEA & ALLN)))

def blk(days, names):
    s = c = a = 0
    for n in names:
        gg = sum(Sd[n][d][0] for d in days if d in Sd[n]); dc = sum(Sd[n][d][1] for d in days if d in Sd[n])
        if gg:
            s += gg - dc
            if n in PRICE and n in COST: c += gg/PRICE[n]*COST[n]
        a += sum(ADd[MAP.get(n, n)].get(d, 0) for d in days)
    return s, c, a, s - c - a

end = datetime.date(2026, 8, 24); WK = []
for i in range(5):
    a = end - datetime.timedelta(days=7*i+6)
    WK.append((f"{a.strftime('%m/%d')}-{(a+datetime.timedelta(days=6)).strftime('%m/%d')}",
               [(a+datetime.timedelta(days=j)).isoformat() for j in range(7)]))
WK.reverse()
CAT = lambda days: sum(ADd['カタログ全部（テスト）'].get(d, 0) for d in days)

print('\n■ 全店の週次分解（利益率 = 1 − 原価率 − 広告費率）')
print(f'  {"週":<12}{"実売":>12}{"利益":>12}{"利益率":>8}{"原価率":>8}{"広告費率":>9}{"MER":>7}')
prev = None
for lbl, days in WK:
    s, c, a, p = blk(days, ALLN); a += CAT(days); p -= CAT(days)
    print(f'  {lbl:<12}{s:>12,.0f}{p:>+12,.0f}{p/s:>8.1%}{c/s:>8.1%}{a/s:>9.1%}{s/a:>7.2f}')
    prev = (c/s, a/s, p/s)

print('\n■ コホート別（週次）')
for tag, names in [('新商品', NEW), ('既存通年', OLD), ('季節物', SEA & ALLN)]:
    print(f'\n  ▼ {tag}')
    print(f'  {"週":<12}{"実売":>12}{"広告費":>11}{"利益":>12}{"利益率":>8}{"MER":>7}{"全店利益への寄与":>16}')
    for lbl, days in WK:
        s, c, a, p = blk(days, names)
        ts, tc, ta, tp = blk(days, ALLN); tp -= CAT(days)
        if s == 0 and a == 0:
            print(f'  {lbl:<12}{"—":>12}{"—":>11}{"—":>12}{"—":>8}{"—":>7}{"—":>16}'); continue
        print(f'  {lbl:<12}{s:>12,.0f}{a:>11,.0f}{p:>+12,.0f}'
              f'{(p/s if s else 0):>8.1%}{(s/a if a else 0):>7.2f}{p/tp if tp else 0:>16.1%}')

# ---- 直近2週の利益率変化を要因分解する ----
print('\n■ ★直近2週の利益率変化を要因に分ける')
(l1, d1), (l2, d2) = WK[-2], WK[-1]
s1, c1, a1, p1 = blk(d1, ALLN); a1 += CAT(d1); p1 -= CAT(d1)
s2, c2, a2, p2 = blk(d2, ALLN); a2 += CAT(d2); p2 -= CAT(d2)
print(f'  {l1} 利益率 {p1/s1:.1%} → {l2} {p2/s2:.1%}（{p2/s2-p1/s1:+.1f}pt）')
print(f'    うち 原価率の寄与   {-(c2/s2-c1/s1)*100:+.2f}pt（{c1/s1:.1%} → {c2/s2:.1%}）')
print(f'    うち 広告費率の寄与 {-(a2/s2-a1/s1)*100:+.2f}pt（{a1/s1:.1%} → {a2/s2:.1%}）')
print('    → 利益率は「原価率」と「広告費率」の2つだけで決まる。どちらが動いたかが答え')

# 広告費率の変化を、さらにコホート別の「広告費の配分」で見る
print(f'\n  ▼ 広告費の配分（誰に出しているか）')
print(f'  {"コホート":<10}{l1:>16}{l2:>16}{"差":>10}')
for tag, names in [('新商品', NEW), ('既存通年', OLD), ('季節物', SEA & ALLN)]:
    _, _, x1, _ = blk(d1, names); _, _, x2, _ = blk(d2, names)
    print(f'  {tag:<10}{x1/a1:>15.1%}{x2/a2:>16.1%}{(x2/a2-x1/a1)*100:>+9.1f}pt')
print(f'  {"カタログ":<10}{CAT(d1)/a1:>15.1%}{CAT(d2)/a2:>16.1%}{(CAT(d2)/a2-CAT(d1)/a1)*100:>+9.1f}pt')
