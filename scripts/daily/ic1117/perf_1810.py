# -*- coding: utf-8 -*-
"""11/17(火) 18:1x 「本日の効率が悪目ですね今時点の」（perf_1115.py を 0〜17時台に切り直したもの）
0〜17時台を過去21日（10/26〜11/15）の同じ時刻と比べる。来訪＝広告費 × 着地÷広告費（CPM・クリック率・着地率をまとめたもの）× 来訪÷着地 に分ける。
今日の Meta の表示・クリックは取り込み前なので、CPM・クリック率は今日の分を出せない。日中の数字なので予算の判定には使わない
入力（すべて 18:1x 取得）: store_sales_0017.json・store_sess_0017.json・meta_acct_0017.txt・meta_camp_0017.txt・sales_prod_0017.txt"""
import json, math, collections, statistics as st, datetime
D = __file__.rsplit('/', 1)[0] + '/'
T = '2026-11-17'
SS = {r[0]: (int(r[1]) + int(r[2]), int(r[3]), int(r[1])) for r in json.load(open(D + 'store_sales_0017.json'))['rows']}
SE = {r[0]: [int(x) for x in r[1:]] for r in json.load(open(D + 'store_sess_0017.json'))['rows']}
MA = {}
for l in open(D + 'meta_acct_0017.txt'):
    if l[0] != '#': p = l.strip().split(','); MA[p[0]] = [int(x) for x in p[1:]]
P = sorted(d for d in SS if d < T); assert len(P) == 21 and P[0] == '2026-10-27'
wd = lambda d: '月火水木金土日'[datetime.date.fromisoformat(d).weekday()]
def band(lab, f, fm, days=P):
    t = f(T); xs = [f(d) for d in days]; lo = sum(x < t for x in xs)
    out = '範囲内' if min(xs) <= t <= max(xs) else ('範囲の外（下）' if t < min(xs) else '範囲の外（上）')
    print(f"  {lab}: 今日 {fm.format(t)}・過去{len(days)}日 {fm.format(min(xs))}〜{fm.format(max(xs))}（中央値 {fm.format(st.median(xs))}）・今日より低い日 {lo}/{len(days)} → {out}")
def pois_le(k, lam): return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))
print('■ 店全体（0〜17時台・過去21日の同時刻）')
band('売上（値引後）', lambda d: SS[d][0], '{:,}')
band('売上÷広告費', lambda d: SS[d][0] / MA[d][0], '{:.2f}')
band('注文', lambda d: SS[d][1], '{}')
band('来訪', lambda d: SE[d][0], '{}')
band('広告費', lambda d: MA[d][0], '{:,}')
band('着地（Meta LPV）÷広告費1万円', lambda d: MA[d][3] / MA[d][0] * 10000, '{:.0f}')
band('来訪÷着地', lambda d: SE[d][0] / MA[d][3], '{:.2f}')
band('来訪÷広告費1万円', lambda d: SE[d][0] / MA[d][0] * 10000, '{:.0f}')
band('購入率%（注文÷来訪）', lambda d: SS[d][1] / SE[d][0] * 100, '{:.2f}')
band('カート投入率%', lambda d: SE[d][1] / SE[d][0] * 100, '{:.2f}')
band('決済完了÷決済画面%', lambda d: SE[d][3] / SE[d][2] * 100, '{:.0f}')
band('客単価', lambda d: SS[d][0] / SS[d][1], '{:,.0f}')
mon = [d for d in P if wd(d) == '火' and d != '2026-11-03']; print('  火曜だけ（祝日11/3を除く・' + '・'.join(d[5:] for d in mon) + '）:')
band('来訪（火曜）', lambda d: SE[d][0], '{}', mon); band('広告費（火曜）', lambda d: MA[d][0], '{:,}', mon); band('着地÷広告費1万円（火曜）', lambda d: MA[d][3] / MA[d][0] * 10000, '{:.0f}', mon)
cvr = sum(SS[d][1] for d in P) / sum(SE[d][0] for d in P); lam = cvr * SE[T][0]
print(f"  → 注文 {SS[T][1]}（来訪{SE[T][0]}×過去21日の購入率{cvr*100:.2f}%＝期待 {lam:.1f}）・この数以下になる確率 {pois_le(SS[T][1], lam)*100:.0f}%")
# 来訪の差を分ける（中央値の日と比べる）: log(来訪) = log(広告費) + log(着地/広告費) + log(来訪/着地)
f1 = lambda d: math.log(MA[d][0]); f2 = lambda d: math.log(MA[d][3] / MA[d][0]); f3 = lambda d: math.log(SE[d][0] / MA[d][3])
m = [st.median(f(d) for d in P) for f in (f1, f2, f3)]
tot = math.log(SE[T][0]) - st.median(math.log(SE[d][0]) for d in P)
print(f"■ 来訪の差（過去21日の中央値比 {math.exp(tot)-1:+.0%}）の分け方: 広告費 {math.exp(f1(T)-m[0])-1:+.0%} ／ 着地÷広告費 {math.exp(f2(T)-m[1])-1:+.0%} ／ 来訪÷着地 {math.exp(f3(T)-m[2])-1:+.0%}")
# 過去日の CPM・クリック率（今日は取り込み前）
print('■ CPM とクリック率（0〜17時台・今日は取り込み前で出せない）:')
for d in P[-7:]:
    if MA[d][2]: print(f"  {d}({wd(d)}): CPM {MA[d][0]/MA[d][1]*1000:,.0f}・クリック率 {MA[d][2]/MA[d][1]*100:.2f}%・着地÷クリック {MA[d][3]/MA[d][2]:.2f}")
PC = [d for d in P if MA[d][2]]
xs = [MA[d][0] / MA[d][1] * 1000 for d in PC]; ys = [MA[d][2] / MA[d][1] * 100 for d in PC]
print(f"  過去21日: CPM {min(xs):,.0f}〜{max(xs):,.0f}（中央値 {st.median(xs):,.0f}）・クリック率 {min(ys):.2f}〜{max(ys):.2f}%（中央値 {st.median(ys):.2f}%）")
print('  曜日別のクリック率（過去21日・0〜17時台の平均）: ' + '・'.join(f"{w} {st.mean([MA[d][2]/MA[d][1]*100 for d in PC if wd(d)==w]):.2f}%" for w in '月火水木金土日'))
# 商品別
PO = collections.defaultdict(int); PG = collections.defaultdict(int)
for l in open(D + 'sales_prod_0017.txt'):
    if l[0] != '#': d, n, g, dc, o = l.strip().split(','); PO[(d, n)] += int(o)
MC = collections.defaultdict(lambda: [0] * 6)
for l in open(D + 'meta_camp_0017.txt'):
    if l[0] != '#': p = l.strip().split(','); MC[(p[0], p[1])] = [int(x) for x in p[2:]]
ALIAS = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '高見えレザーヘッドレストフックv2': '高見えレザーヘッドレストフック', '快適マジックインソール v3': '快適マジックインソール', '快適マジックインソールv2': '快適マジックインソール', '高見えレザーヘッドレストフックv3': '高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv4': '高見えレザーヘッドレストフック'}
P6 = [f'2026-11-{x:02d}' for x in range(10, 15)]   # 11/15・16 はキャンペーン別の時間帯の取得が膨らむので使わない
AT = collections.defaultdict(int)
for (d, c), v in MC.items():
    if d == T: AT[ALIAS.get(c, c)] += v[0]
print(f"■ 商品別（0〜17時台・今日広告費が出た全キャンペーン。期待＝11/10〜14 の同時刻の 注文÷広告費 × 今日の広告費）・広告費の合計 {sum(AT.values()):,}（アカウント {MA[T][0]:,}）")
for n in sorted(AT, key=lambda n: -AT[n]):
    a = AT[n]; o = PO.get((T, n), 0); ln = f"  {n}: {o}注文・広告費 {a:,}"
    if n.startswith('カタログ'): print(ln + '（商品に分けられない）'); continue
    a6 = sum(v[0] for (d, c), v in MC.items() if d in P6 and ALIAS.get(c, c) == n); o6 = sum(PO.get((d, n), 0) for d in P6)
    if not a6 or not o6: print(ln + '（比べる過去なし）'); continue
    lam = o6 / a6 * a; p = 1 - pois_le(o - 1, lam) if o >= lam else pois_le(o, lam)
    print(ln + f"・期待 {lam:.1f}・{'多い' if o >= lam else '少ない'}側 {p*100:.0f}%")

# 売上÷広告費 ＝ 来訪÷広告費 × 注文÷来訪 × 客単価 を中央値の日と比べて分ける
g1 = lambda d: math.log(SE[d][0] / MA[d][0]); g2 = lambda d: math.log(SS[d][1] / SE[d][0]); g3 = lambda d: math.log(SS[d][0] / SS[d][1])
mm = [st.median(f(d) for d in P) for f in (g1, g2, g3)]
tt = math.log(SS[T][0] / MA[T][0]) - st.median(math.log(SS[d][0] / MA[d][0]) for d in P)
print(f"■ 売上÷広告費の差（過去21日の中央値比 {math.exp(tt)-1:+.0%}）の分け方: 来訪÷広告費 {math.exp(g1(T)-mm[0])-1:+.0%} ／ 購入率 {math.exp(g2(T)-mm[1])-1:+.0%} ／ 客単価 {math.exp(g3(T)-mm[2])-1:+.0%}")
