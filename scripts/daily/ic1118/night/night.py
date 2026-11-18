# -*- coding: utf-8 -*-
"""11/18 「最近夜売れない。なんでだ？」夜（18〜23時台）と昼（0〜17時台）を週ごとに比べる。
売上÷広告費 ＝ 着地÷広告費 × 来訪÷着地 × 注文÷来訪 × 客単価。注文の時刻と広告の時刻は同じ人とは限らない（夜に見て翌朝買う等）点に注意"""
import collections, csv, datetime, math
num = lambda x: 0 if x == 'null' else float(x)
D = collections.defaultdict(dict)
for l in open('raw.txt'):
    if l[0] == '#': continue
    k, d, *v = l.strip().split(','); D[k][d] = [num(x) for x in v]
days = sorted(D['SN'])
AD = collections.defaultdict(float)
for r in csv.DictReader(open('../../../../data/daily/daily_ad.csv')): AD[r['date']] += float(r['cost'])
for d in days:  # 昼＋夜＝日次CSV（11/17 は CSV が 00時台の暫定のため差が出る）
    s = D['MN'][d][0] + D['MD'][d][0]
    print(f'  確かめ {d}: 時間別 {s:,.0f} ／ 日次CSV {AD[d]:,.0f}（{s/AD[d]-1:+.2%}）') if abs(s / AD[d] - 1) > 0.002 else None
WEEKS = [('10/21〜27', '2026-10-21', '2026-10-27'), ('10/28〜11/3', '2026-10-28', '2026-11-03'), ('11/4〜10', '2026-11-04', '2026-11-10'), ('11/11〜17', '2026-11-11', '2026-11-17')]
def agg(k, a, b, n): return [sum(D[k][d][i] for d in days if a <= d <= b) for i in range(n)]
print('週・夜（18〜23時台）／昼（0〜17時台）: 広告費の割合・売上÷広告費・注文・着地÷広告費1万円・来訪÷着地・カート÷来訪・注文÷来訪・客単価')
for lab, a, b in WEEKS:
    out = []
    for t in 'ND':
        s = agg('S' + t, a, b, 3); e = agg('E' + t, a, b, 4); m = agg('M' + t, a, b, 6)
        net = s[0] + s[1]; out.append((m[0], net / m[0], s[2], m[3] / m[0] * 1e4, e[0] / m[3], e[1] / e[0] * 100, s[2] / e[0] * 100, net / s[2]))
    tot = out[0][0] + out[1][0]
    print(f'  {lab}: 夜 {out[0][0]/tot:.0%}・{out[0][1]:.2f}・{out[0][2]:.0f}件・{out[0][3]:.0f}・{out[0][4]:.2f}・{out[0][5]:.2f}%・{out[0][6]:.2f}%・{out[0][7]:,.0f}  ／ 昼 {out[1][1]:.2f}・{out[1][2]:.0f}件・{out[1][3]:.0f}・{out[1][4]:.2f}・{out[1][5]:.2f}%・{out[1][6]:.2f}%・{out[1][7]:,.0f}  ／ 夜÷昼の売上÷広告費 {out[0][1]/out[1][1]:.2f}')
# 夜の売上÷広告費の日別（ばらつきと、直近7日がどこにいるか）
print('■ 夜の売上÷広告費（日別）と 夜÷昼')
xs = []
for d in days:
    n = (D['SN'][d][0] + D['SN'][d][1]) / D['MN'][d][0]; dd = (D['SD'][d][0] + D['SD'][d][1]) / D['MD'][d][0]
    xs.append((d, n, n / dd, D['SN'][d][2]))
    print(f"  {d[5:]}({'月火水木金土日'[datetime.date.fromisoformat(d).weekday()]}): 夜 {n:.2f}（{D['SN'][d][2]:.0f}件）・昼 {dd:.2f}・夜÷昼 {n/dd:.2f}")
r_old = [x[2] for x in xs if x[0] < '2026-11-11']; r_new = [x[2] for x in xs if x[0] >= '2026-11-11']
m, s = sum(r_old) / len(r_old), (sum((x - sum(r_old) / len(r_old)) ** 2 for x in r_old) / (len(r_old) - 1)) ** .5
print(f'  夜÷昼: 10/21〜11/10 平均 {m:.2f}（日ごとの標準偏差 {s:.2f}）／ 11/11〜17 平均 {sum(r_new)/len(r_new):.2f} → 7日平均のずれ {(sum(r_new)/len(r_new)-m)/(s/len(r_new)**.5):+.1f}σ')
# 夜の注文を、夜の来訪×10/21〜11/10 の夜の注文÷来訪 で期待と比べる
on = sum(D['SN'][d][2] for d in days if d >= '2026-11-11'); en = sum(D['EN'][d][0] for d in days if d >= '2026-11-11')
rate = sum(D['SN'][d][2] for d in days if d < '2026-11-11') / sum(D['EN'][d][0] for d in days if d < '2026-11-11')
lam = rate * en; p = sum(math.exp(-lam) * lam ** k / math.factorial(k) for k in range(int(on) + 1))
print(f'  夜の注文 11/11〜17: {on:.0f}件 ／ 来訪 {en:.0f}×それまでの夜の注文÷来訪 {rate*100:.2f}% ＝ 期待 {lam:.1f}（この数以下 {p:.1%}）')
