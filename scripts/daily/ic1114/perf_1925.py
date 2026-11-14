# -*- coding: utf-8 -*-
"""11/14(土) 19:2x ユーザー「急に売れなくなってきた」
①0〜18時台 ②夕方16〜18時台 ③19時台（途中）を、過去21日（10/24〜11/13）の同じ時刻と比べる。
偶然かどうかは件数から（注文はポアソン）。日中の数字なので予算の判定には使わない"""
import json, math, collections, statistics as st
D = 'scripts/daily/ic1114/'
T = '2026-11-14'
def J(f): return json.load(open(D + f))['rows']
SS = {r[0]: (int(r[1]) + int(r[2]), int(r[3])) for r in J('store_sales_0018.json')}          # 0〜18時台 売上（値引後）・注文
SE = {r[0]: [int(x) for x in r[1:]] for r in J('store_sess_0018.json')}                         # 0〜18時台 来訪・カート・決済画面・決済完了
E3 = {r[0]: [int(x) for x in r[1:]] for r in J('store_sess_1618.json')}                         # 16〜18時台
MA = {}
for l in open(D + 'meta_acct_0018.txt'):
    if l[0] != '#': p = l.strip().split(','); MA[p[0]] = [int(x) for x in p[1:]]             # 広告費・表示・クリック・着地・カート・購入
MH = collections.defaultdict(lambda: [0] * 6)
for l in open(D + 'meta_hour_1219.txt'):
    if l[0] == '#': continue
    d, h, *v = l.strip().replace('"', '').split(','); h = int(h[:2])
    MH[d, h] = [int(x) if x != 'null' else 0 for x in v]
OH = collections.defaultdict(lambda: (0, 0))
for d, h, o, g in J('sales_hour_1024_1114.json'): OH[d, int(h)] = (int(o), int(g))           # 時間帯別 注文・売上（値引前）
P = sorted(d for d in SS if d < T); assert len(P) == 21 and P[0] == '2026-10-24'
# 照合: 時間帯別の注文を 0〜18時台で足すと日別の注文と一致する
for d in P + [T]: assert sum(OH[d, h][0] for h in range(19)) == SS[d][1], d

def band(lab, f, fm):
    t = f(T); xs = [f(d) for d in P]; lo = sum(x < t for x in xs)
    out = '範囲内' if min(xs) <= t <= max(xs) else ('過去21日の範囲の外（下）' if t < min(xs) else '過去21日の範囲の外（上）')
    print(f"  {lab}: 今日 {fm.format(t)}・過去21日 {fm.format(min(xs))}〜{fm.format(max(xs))}（中央値 {fm.format(st.median(xs))}）・今日より低い日 {lo}/21 → {out}")
def pois_le(k, lam): return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))

print('■ ① 店全体（0〜18時台・過去21日の同時刻）')
band('売上÷広告費', lambda d: SS[d][0] / MA[d][0], '{:.2f}')
band('広告費', lambda d: MA[d][0], '{:,}')
band('注文', lambda d: SS[d][1], '{}')
band('来訪', lambda d: SE[d][0], '{}')
band('購入率%（注文÷来訪）', lambda d: SS[d][1] / SE[d][0] * 100, '{:.2f}')
band('カート投入率%', lambda d: SE[d][1] / SE[d][0] * 100, '{:.2f}')
band('決済完了÷決済画面%', lambda d: SE[d][3] / SE[d][2] * 100, '{:.0f}')
band('客単価', lambda d: SS[d][0] / SS[d][1], '{:,.0f}')
band('クリック率%（Meta）', lambda d: MA[d][2] / MA[d][1] * 100, '{:.2f}')
band('CPM（Meta）', lambda d: MA[d][0] / MA[d][1] * 1000, '{:,.0f}')
cvr = sum(SS[d][1] for d in P) / sum(SE[d][0] for d in P); lam = cvr * SE[T][0]
print(f"  → 注文 {SS[T][1]}（来訪{SE[T][0]}×過去21日の購入率{cvr*100:.2f}%＝期待 {lam:.1f}）・この数以下になる確率 {pois_le(SS[T][1], lam)*100:.0f}%")

print('\n■ ② 夕方（16〜18時台・過去21日の同時刻）')
o3 = lambda d: sum(OH[d, h][0] for h in (16, 17, 18)); g3 = lambda d: sum(OH[d, h][1] for h in (16, 17, 18))
m3 = lambda d, i: sum(MH[d, h][i] for h in (16, 17, 18))
band('注文', o3, '{}')
band('来訪', lambda d: E3[d][0], '{}')
band('購入率%（注文÷来訪）', lambda d: o3(d) / E3[d][0] * 100, '{:.2f}')
band('カート投入率%', lambda d: E3[d][1] / E3[d][0] * 100, '{:.2f}')
band('広告費', lambda d: m3(d, 0), '{:,}')
band('売上（値引前）÷広告費', lambda d: g3(d) / m3(d, 0), '{:.2f}')
band('広告費1万円あたりの注文', lambda d: o3(d) / m3(d, 0) * 1e4, '{:.2f}')
band('クリック率%（Meta）', lambda d: m3(d, 2) / m3(d, 1) * 100, '{:.2f}')
band('CPM（Meta）', lambda d: m3(d, 0) / m3(d, 1) * 1000, '{:,.0f}')
cv3 = sum(o3(d) for d in P) / sum(E3[d][0] for d in P); l3 = cv3 * E3[T][0]
print(f"  → 注文 {o3(T)}（来訪{E3[T][0]}×過去21日の夕方の購入率{cv3*100:.2f}%＝期待 {l3:.1f}）・この数以下になる確率 {pois_le(o3(T), l3)*100:.0f}%")
print('  直近の夕方の注文: ' + '・'.join(f'{d[5:]} {o3(d)}' for d in P[-5:] + [T]))

print('\n■ ③ 今日の1時間ごとの注文（Shopify）と来訪')
TH = {int(r[0]): [int(x) for x in r[1:]] for r in J('sess_hour_1114_1925.json')}
print('  ' + '・'.join(f'{h}時 {OH[T, h][0]}件/{TH[h][0]}人' for h in range(9, 20)))
avg = {h: st.mean(OH[d, h][0] for d in P) for h in range(24)}
print('  過去21日の平均: ' + '・'.join(f'{h}時 {avg[h]:.1f}' for h in range(9, 20)))
mins = 24; lam19 = avg[19] * mins / 60
print(f'  19時台は {mins}分時点で0件。過去21日の19時台は平均{avg[19]:.1f}件/時 → {mins}分なら期待 {lam19:.1f}件・0件になる確率 {math.exp(-lam19)*100:.0f}%')

print('\n■ ④ 人がサイトに着いているか（18時台）')
SH = collections.defaultdict(int)
for d, h, s, *_ in json.load(open(D + 'sess_hourly_1015_1113.json'))['rows']: SH[d, int(h)] = int(s)
rat = [SH[d, 18] / MH[d, 18][2] for d in P if MH[d, 18][2]]
lpv = [MH[d, 18][3] / MH[d, 18][2] for d in P if MH[d, 18][2]]
print(f"  Shopify来訪÷Metaクリック: 今日 {TH[18][0]/MH[T,18][2]:.2f}・過去21日 {min(rat):.2f}〜{max(rat):.2f}")
print(f"  Meta着地÷Metaクリック: 今日 {MH[T,18][3]/MH[T,18][2]:.0%}・過去21日 {min(lpv):.0%}〜{max(lpv):.0%}")
