# -*- coding: utf-8 -*-
"""11/12(木) 18:3x 「今日のパフォーマンスクッソ悪くね」
0〜17時台を、過去7日（11/5〜11/11）・木曜（10/22・10/29・11/5）・前日の同時刻と比べる。時間帯ごと（0〜8／9〜11／12〜14／15〜17時台）の推移、新しく出した広告の実績も出す。
MER=(gross−値引)÷広告費・倍率=(gross−値引−原価)÷広告費。日中の数字なので判定・予算提案には使わない（5d-2）。今日の16〜17時台の広告費・着地はまだ着地途中。
裏起毛パンツの原価は色・サイズ別の内訳を取っていないので代表原価1,338円（最大）で計算＝倍率は低めに出る。"""
import os, csv, collections, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read(); g = {}
i = src.index('COST = {'); j = src.index('TAB = {', i)
exec(src[i:j], g); COST, PRICE = g['COST'], dict(g['PRICE']); PRICE['姿勢サポートチェア'] = 5980; PRICE['優先配送'] = 790; PRICE['ムダ毛シェーバー'] = 6980; PRICE['ネックマッサージャー'] = 8980; PRICE['壁掛けディスペンサー'] = 6980
rd = lambda f: [next(csv.reader([l.strip()])) for l in open(D + f) if l.strip() and l[0] != '#']
iv = lambda x: 0 if x in ('null', '') else int(x)
S = collections.defaultdict(lambda: [0, 0]); A = collections.defaultdict(lambda: [0] * 6); ST = {}; AC = {}
for d, n, gr, ds in rd('sales_prod_0017.txt'): S[(d, n)][0] += int(gr); S[(d, n)][1] += -int(ds)
for d, n, *v in rd('meta_camp_0017.txt'): A[(d, n)] = [iv(x) for x in v]
for d, *v in rd('store_0017.txt'): ST[d] = [int(v[0]), -int(v[1])] + [int(x) for x in v[2:]]
for d, *v in rd('meta_acct_0017_1022_1104.txt'): AC[d] = [int(x) for x in v]
for d in sorted({k[0] for k in A}): AC[d] = [sum(v[i] for (dd, _), v in A.items() if dd == d) for i in range(4)]
for d in sorted({k[0] for k in S}): assert sum(v[0] for (dd, _), v in S.items() if dd == d) == ST[d][0], d   # 商品別の合計 = 店全体
T = '2026-11-12'; P7 = [d for d in sorted(ST) if '2026-11-05' <= d <= '2026-11-11']; THU = ['2026-10-22', '2026-10-29', '2026-11-05']; Y = '2026-11-11'
assert len(P7) == 7 and len(ST) == 22 and set(ST) == set(AC)
H = {}
for d, hb, *v in rd('meta_hour_1830.txt'): H[(d, int(hb[:2]))] = [iv(x) for x in v]
for d in P7 + [T]: assert abs(sum(H[(d, h)][0] for h in range(18)) - AC[d][0]) <= 15, (d, sum(H[(d, h)][0] for h in range(18)), AC[d][0])
SH = {(d, int(h)): [int(x) for x in v] for d, h, *v in rd('shop_hour_1830.txt')}   # orders,gross,disc(負),sessions,carts,checkout,completed
for d in P7 + [T]:
    assert sum(SH[(d, h)][0] for h in range(18)) == ST[d][2] and sum(SH[(d, h)][1] for h in range(18)) == ST[d][0] and sum(SH[(d, h)][3] for h in range(18)) == ST[d][3], d
net = lambda d: ST[d][0] - ST[d][1]; ad = lambda d: AC[d][0]
def units(n, gr): p = PRICE.get(n); return gr // p if p and gr % p == 0 else None
def cogs(d): return sum((units(n, gr) or 0) * COST.get(n, 0) for (dd, n), (gr, ds) in S.items() if dd == d and gr)
print('■ 店全体（0〜17時台）')
def rk(lab, f, fm):
    t = f(T); xs = [f(d) for d in P7]
    print(f"  {lab}: 今日 {fm.format(t)} ／ 過去7日 中央値{fm.format(st.median(xs))}（{fm.format(min(xs))}〜{fm.format(max(xs))}）今日より低い日{sum(x < t for x in xs)}/7 ／ 木曜 {'・'.join(fm.format(f(d)) for d in THU)} ／ 前日 {fm.format(f(Y))}")
mult = lambda d: (net(d) - cogs(d)) / ad(d)
for lab, f, fm in [('売上', net, '{:,.0f}'), ('注文', lambda d: ST[d][2], '{:.0f}'), ('広告費', ad, '{:,.0f}'), ('売上÷広告費', lambda d: net(d) / ad(d), '{:.2f}'),
                   ('来訪', lambda d: ST[d][3], '{:,.0f}'), ('購入完了÷来訪%', lambda d: ST[d][6] / ST[d][3] * 100, '{:.2f}'), ('カゴ投入率%', lambda d: ST[d][4] / ST[d][3] * 100, '{:.2f}'),
                   ('客単価', lambda d: net(d) / ST[d][2], '{:,.0f}'), ('注文1件の広告費', lambda d: ad(d) / ST[d][2], '{:,.0f}'), ('1クリック円', lambda d: AC[d][0] / AC[d][2], '{:.1f}'),
                   ('CPM', lambda d: AC[d][0] / AC[d][1] * 1000, '{:,.0f}'), ('CTR%', lambda d: AC[d][2] / AC[d][1] * 100, '{:.2f}')]:
    rk(lab, f, fm)
print(f"  倍率（11/5以降）: 今日 {mult(T):.2f} ／ 過去7日 中央値{st.median(mult(d) for d in P7):.2f}（{min(mult(d) for d in P7):.2f}〜{max(mult(d) for d in P7):.2f}）今日より低い日{sum(mult(d) < mult(T) for d in P7)}/7 ／ 前日 {mult(Y):.2f}")
print(f"  粗利−広告費（0〜17時台）: 今日 {net(T)-cogs(T)-ad(T):+,.0f} ／ 前日の同時刻 {net(Y)-cogs(Y)-ad(Y):+,.0f} ／ 過去7日 " + '・'.join(f"{d[5:]} {net(d)-cogs(d)-ad(d):+,.0f}" for d in P7))
print('  日別（0〜17時台）売上／注文／広告費／売上÷広告費／倍率／来訪／完了率%: ' + ' ｜ '.join(f"{d[5:]} {net(d):,}／{ST[d][2]}／{ad(d):,}／{net(d)/ad(d):.2f}／{mult(d):.2f}／{ST[d][3]:,}／{ST[d][6]/ST[d][3]*100:.2f}" for d in P7 + [T]))
# 終日との関係
FS = collections.defaultdict(int); FA = collections.defaultdict(float)
for x in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): FS[x['date']] += int(x['gross']) - int(x['disc'])
for x in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): FA[x['date']] += float(x['cost'])
HD = [d for d in sorted(ST) if d < T]; x = [net(d) / ad(d) for d in HD]; y = [FS[d] / FA[d] for d in HD]; df = [b - a for a, b in zip(x, y)]
print(f"\n■ 0〜17時台と終日の関係（{HD[0]}〜{HD[-1]}・{len(HD)}日）: 売上÷広告費 r={st.correlation(x, y):.2f}・終日−0〜17時台 中央値{st.median(df):+.2f}（{min(df):+.2f}〜{max(df):+.2f}）")
sh = [net(d) / FS[d] for d in HD]; print(f"  0〜17時台の売上が終日に占める割合: 中央値{st.median(sh)*100:.0f}%（{min(sh)*100:.0f}〜{max(sh)*100:.0f}%）")
print('  日別（0〜17時台 → 終日）:', '・'.join(f"{d[5:]} {a:.2f}→{b:.2f}" for d, a, b in zip(HD[-8:], x[-8:], y[-8:])))
# 時間帯ごと
print('\n■ 時間帯ごと（注文／売上／広告費／売上÷広告費／来訪／完了率%）')
BL = [('0〜8時台', range(0, 9)), ('9〜11時台', range(9, 12)), ('12〜14時台', range(12, 15)), ('15〜17時台', range(15, 18))]
def blk(d, hs):
    o = sum(SH[(d, h)][0] for h in hs); n_ = sum(SH[(d, h)][1] + SH[(d, h)][2] for h in hs); c = sum(H[(d, h)][0] for h in hs); s = sum(SH[(d, h)][3] for h in hs); cp = sum(SH[(d, h)][6] for h in hs)
    return o, n_, c, n_ / c, s, cp / s * 100
for lab, hs in BL:
    t = blk(T, hs); P = [blk(d, hs) for d in P7]
    print(f"  {lab}: 今日 {t[0]}件／{t[1]:,}／{t[2]:,}／{t[3]:.2f}／{t[4]}／{t[5]:.2f} ｜ 過去7日 中央値 {st.median(p[0] for p in P):.0f}件／{st.median(p[1] for p in P):,.0f}／{st.median(p[2] for p in P):,.0f}／{st.median(p[3] for p in P):.2f}／{st.median(p[4] for p in P):.0f}／{st.median(p[5] for p in P):.2f}（売上÷広告費 {min(p[3] for p in P):.2f}〜{max(p[3] for p in P):.2f}・今日より低い日 {sum(p[3] < t[3] for p in P)}/7） ｜ 前日 {blk(Y, hs)[0]}件／{blk(Y, hs)[3]:.2f}")
    print('     日別 売上÷広告費（注文）: ' + ' '.join(f"{d[5:]} {blk(d, hs)[3]:.2f}({blk(d, hs)[0]})" for d in P7 + [T]))
print('  今日の時間別（来訪/注文/広告費）: ' + ' '.join(f"{h}時 {SH[(T,h)][3]}/{SH[(T,h)][0]}/{H[(T,h)][0]:,}" for h in range(18)))
print('  昨日の時間別（来訪/注文/広告費）: ' + ' '.join(f"{h}時 {SH[(Y,h)][3]}/{SH[(Y,h)][0]}/{H[(Y,h)][0]:,}" for h in range(18)))
# 12〜14時台の1時間ごとの注文（8日）
print('  15〜17時台の1時間ごとの注文: ' + ' ｜ '.join(f"{d[5:]} {'/'.join(str(SH[(d,h)][0]) for h in range(15,18))}" for d in P7 + [T]))
# 商品別
print('\n■ 商品別（0〜17時台）: 今日 個数・広告費・倍率 ／ 過去7日の同時刻（広告費2,000円以上の日）倍率の中央値（範囲）・個数の中央値')
def pm(d, n):
    gr, ds = S[(d, n)]; a = A[(d, n)][0]; u = (units(n, gr) or 0) if gr else 0
    return (None if not a else (gr - ds - u * COST.get(n, 0)) / a), u, a, gr - ds - u * COST.get(n, 0) - a
OLD = ['伸縮ガラスクリーナー', 'ワイド水切りワイパー', 'W固定スマホ車載ホルダー', 'ナノガラス脱毛パッド', '伸縮ワックス洗車ブラシ', 'マグネットドアクッション', '4-in-1マルチクリーナー', '快適マジックインソール']
NEW = ['防風あったか裏起毛パンツ', 'UV歯ブラシ除菌器', 'バランスケアスリッパ', '高見えレザーヘッドレストフック', 'クリアビューレインガードフィルム']
STOP = ['すき間収納シートポケット', 'コードレスダブルミスト加湿器', '姿勢サポートチェア']
for n in OLD:
    m, u, a, p_ = pm(T, n); xs = [pm(d, n)[0] for d in P7 if pm(d, n)[2] >= 2000]; us = [pm(d, n)[1] for d in P7 if pm(d, n)[2] >= 2000]; cl = A[(T, n)]
    print(f"  {n}: {u}個・{a:,}円・{'—' if m is None else f'{m:.2f}'}（粗利−広告費 {p_:+,.0f}・クリック{cl[2]}・Metaカート{cl[4]}）／ {st.median(xs):.2f}（{min(xs):.2f}〜{max(xs):.2f}・{len(xs)}日・今日より低い日 {sum(x < m for x in xs)}）・{st.median(us):g}個 ／ 日別 " + ' '.join(f"{pm(d, n)[0]:.2f}" if pm(d, n)[2] >= 2000 else '—' for d in P7))
print(f"  カタログ全部（テスト）: {A[(T,'カタログ全部（テスト）')][0]:,}円・クリック{A[(T,'カタログ全部（テスト）')][2]}・Meta購入{A[(T,'カタログ全部（テスト）')][5]}")
print('\n■ 新しく出した／再開した広告（今日0〜17時台）')
ACC = {'防風あったか裏起毛パンツ': None, 'UV歯ブラシ除菌器': 17220, 'バランスケアスリッパ': 11028, '高見えレザーヘッドレストフック': 9744, 'クリアビューレインガードフィルム': 9546}
for n in NEW:
    m, u, a, p_ = pm(T, n); cl = A[(T, n)]
    print(f"  {n}: 広告費 {a:,}円・表示 {cl[1]:,}・クリック {cl[2]}（CTR {cl[2]/cl[1]*100:.2f}%・{a/max(cl[2],1):.0f}円/クリック）・着地 {cl[3]}・Metaカート {cl[4]}・Meta購入 {cl[5]} ｜ Shopify {u}個・売上 {S[(T,n)][0]-S[(T,n)][1]:,}・倍率 {'—' if m is None else f'{m:.2f}'}・粗利−広告費 {p_:+,.0f}" + (f" ｜ 事故停止 {ACC[n]:,}円" if ACC[n] else ''))
print('  広告セット別（今日・広告別の取得）:')
for r in rd('meta_ad_today_1830.txt'):
    if any(k in r[1] for k in ['1112複製', 'コピー', 'UV歯ブラシ', 'バランスケア', '裏起毛', 'クリアビュー']) and 'インソール' not in r[1]:
        print(f"    {r[1]}／広告{r[2]}（{r[3]}）: {iv(r[4]):,}円・表示{iv(r[5]):,}・クリック{iv(r[6])}・着地{iv(r[7])}・カート{iv(r[8])}・決済開始{iv(r[9])}・購入{iv(r[10])}")
tn = sum(S[(T, n)][0] - S[(T, n)][1] for n in NEW + STOP); ta = sum(A[(T, n)][0] for n in NEW + STOP)
tn2 = sum(S[(T, n)][0] - S[(T, n)][1] for n in NEW); ta2 = sum(A[(T, n)][0] for n in NEW)
print(f"\n■ 今日0〜17時台を分けると")
print(f"  新しく出した／再開した5商品: 売上 {tn2:,}・広告費 {ta2:,}・売上÷広告費 {tn2/ta2:.2f}")
print(f"  今日止めた3つ（すき間収納シートポケット・コードレスダブルミスト加湿器・姿勢サポートチェア）: 売上 {tn-tn2:,}・広告費 {ta-ta2:,}")
print(f"  それ以外（前からの商品＋広告なしの売上）: 売上 {net(T)-tn:,}・広告費 {ad(T)-ta:,}・売上÷広告費 {(net(T)-tn)/(ad(T)-ta):.2f} ／ 全体 {net(T)/ad(T):.2f}")
for d in P7:
    pass
print('\n■ 原価・売価が当たらなかった売上（0〜17時台）')
for d in P7 + [T]:
    miss = [(n, gr) for (dd, n), (gr, ds) in S.items() if dd == d and gr and (units(n, gr) is None or n not in COST)]
    if miss: print(' ', d[5:], miss)

print('\n■ 売上の差の内訳（0〜17時台・今日 − 過去7日の平均。商品別の差を足すと店全体の差になる）')
names = sorted({n for (d, n) in S})
avg = {n: sum(S[(d, n)][0] - S[(d, n)][1] for d in P7) / 7 for n in names}; tod = {n: S[(T, n)][0] - S[(T, n)][1] for n in names}
aavg = {n: sum(A[(d, n)][0] for d in P7) / 7 for n in names}; atod = {n: A[(T, n)][0] for n in names}
tot = sum(tod.values()) - sum(avg.values()); assert abs(sum(tod.values()) - net(T)) < 1 and abs(sum(avg.values()) - sum(net(d) for d in P7) / 7) < 1
print(f"  店全体: {sum(avg.values()):,.0f} → {sum(tod.values()):,.0f}（{tot:+,.0f}）・広告費 {sum(ad(d) for d in P7)/7:,.0f} → {ad(T):,.0f}")
for n in sorted(names, key=lambda n: tod[n] - avg[n]):
    if abs(tod[n] - avg[n]) >= 5000: print(f"  {n}: 売上 {avg[n]:,.0f} → {tod[n]:,.0f}（{tod[n]-avg[n]:+,.0f}）・広告費 {aavg[n]:,.0f} → {atod[n]:,.0f}")
NEW4 = ['ワイド水切りワイパー', 'クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', 'マグネットドアクッション']
g4 = sum(tod[n] - avg[n] for n in NEW4); print(f"  新しい4本の合計: 売上 {sum(avg[n] for n in NEW4):,.0f} → {sum(tod[n] for n in NEW4):,.0f}（{g4:+,.0f}＝店全体の差の{g4/tot*100:.0f}%）・広告費 {sum(aavg[n] for n in NEW4):,.0f} → {sum(atod[n] for n in NEW4):,.0f}")
print('  新しい4本の日別（0〜17時台）売上／広告費: ' + ' ｜ '.join(f"{d[5:]} {sum(S[(d,n)][0]-S[(d,n)][1] for n in NEW4):,}／{sum(A[(d,n)][0] for n in NEW4):,}" for d in P7 + [T]))
print('  それ以外の日別（0〜17時台）売上／広告費: ' + ' ｜ '.join(f"{d[5:]} {net(d)-sum(S[(d,n)][0]-S[(d,n)][1] for n in NEW4):,}／{ad(d)-sum(A[(d,n)][0] for n in NEW4):,}" for d in P7 + [T]))
