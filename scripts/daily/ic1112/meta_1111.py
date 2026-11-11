"""Meta キャンペーン×日（11/4〜11/11）: 保存済みの data_query 実測から、表示単価・クリック率・着地単価を日別・商品別に並べる（読み取りのみ）。
各日付は、その日を2日目に含む（＝確定後に取り直した）ファイルを優先する。11/11だけ暫定。"""
import glob, collections
rows = {}
for f in sorted(glob.glob('scripts/daily/o11*/meta_camp_*_raw.txt')):
    for ln in open(f):
        if ln.startswith('#') or not ln.strip() or not ln.startswith('2026-'): continue   # 注記行・見出し行は読まない
        p = ln.strip().split(',')
        d, n = p[0], p[1]
        v = [0.0 if x in ('null', '') else float(x) for x in p[2:8]]
        rows[(d, n)] = v          # 後のファイル（確定値）で上書き
D = ['2026-11-%02d' % i for i in range(4, 12)]
print('日別（アカウント合計）: 日付 広告費 表示 クリック 着地(LPV) 購入 ｜ 表示1000回単価 クリック率 着地1件の費用 着地→購入')
tot = {}
for d in D:
    c = [sum(v[i] for (dd, n), v in rows.items() if dd == d) for i in range(6)]
    tot[d] = c
    print(d[5:], round(c[0]), round(c[1]), round(c[2]), round(c[3]), round(c[5]), '｜', round(c[0] / c[1] * 1000), '%.2f%%' % (c[2] / c[1] * 100), round(c[0] / c[3], 1), '%.2f%%' % (c[5] / c[3] * 100))
b = [sum(tot[d][i] for d in D[1:7]) for i in range(6)]
print('6日計(11/5-10)', '｜', round(b[0] / b[1] * 1000), '%.2f%%' % (b[2] / b[1] * 100), round(b[0] / b[3], 1), '%.2f%%' % (b[5] / b[3] * 100))
print('\n商品別 11/11 と 6日(11/5-10): 商品 広告費(11/11) ｜ 表示単価 6日→11/11 ｜ クリック率 ｜ 着地1件の費用 ｜ 着地→Meta購入')
names = sorted({n for (d, n) in rows if d == '2026-11-11'}, key=lambda n: -rows[('2026-11-11', n)][0])
for n in names:
    t = rows[('2026-11-11', n)]
    s = [sum(rows.get((d, n), [0] * 6)[i] for d in D[1:7]) for i in range(6)]
    def f(v):
        if not v[1] or not v[3]: return None
        return (v[0] / v[1] * 1000, v[2] / v[1] * 100, v[0] / v[3], v[5] / v[3] * 100)
    a, c = f(s), f(t)
    if not c: continue
    if a: print(f'  {n[:14]}: {t[0]:,.0f} ｜ {a[0]:,.0f}→{c[0]:,.0f}（{(c[0]/a[0]-1)*100:+.0f}%）｜ {a[1]:.2f}→{c[1]:.2f}% ｜ {a[2]:.0f}→{c[2]:.0f}（{(c[2]/a[2]-1)*100:+.0f}%）｜ {a[3]:.1f}→{c[3]:.1f}%')
    else: print(f'  {n[:14]}: {t[0]:,.0f} ｜ —→{c[0]:,.0f} ｜ —→{c[1]:.2f}% ｜ —→{c[2]:.0f} ｜ —→{c[3]:.1f}%（6日の実績なし）')
