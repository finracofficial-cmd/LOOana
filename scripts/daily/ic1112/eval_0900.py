# -*- coding: utf-8 -*-
"""11/12(木) 09:00: 0〜8時台を、過去7日（11/5〜11/11）・木曜（10/22・10/29・11/5）・前日の同時刻と比べる。
MER=(gross−値引)÷広告費・倍率=(gross−値引−原価)÷広告費。日中の数字なので判定・予算提案には使わない（5d-2）。
今日の8時台の広告費は着地途中（過去2回の確認では直近1時間ぶんがあとから2,400〜2,600円増えた）。
裏起毛パンツの原価は色・サイズ別の内訳を取っていないので代表原価1,338円（最大）で計算＝倍率は低めに出る。"""
import os, csv, collections, statistics as st
D = os.path.dirname(os.path.abspath(__file__)) + '/'; R = D + '../../../'
src = open(R + 'scripts/product_tabs.py').read(); g = {}
i = src.index('COST = {'); j = src.index('TAB = {', i)
exec(src[i:j], g); COST, PRICE = g['COST'], dict(g['PRICE']); PRICE['姿勢サポートチェア'] = 5980; PRICE['優先配送'] = 790; PRICE['ムダ毛シェーバー'] = 6980; PRICE['ネックマッサージャー'] = 8980
rd = lambda f: [l.strip().split(',') for l in open(D + f) if l.strip() and l[0] != '#']
S = collections.defaultdict(lambda: [0, 0]); A = collections.defaultdict(lambda: [0] * 6); ST = {}; AC = {}
for d, n, gr, ds in rd('sales_prod_0008.txt'): S[(d, n)][0] += int(gr); S[(d, n)][1] += -int(ds)
for d, n, *v in rd('meta_camp_0008.txt'): A[(d, n)] = [int(x) for x in v]
for d, *v in rd('store_0008.txt'): ST[d] = [int(v[0]), -int(v[1])] + [int(x) for x in v[2:]]
for d, *v in rd('meta_acct_0008.txt'): AC[d] = [int(x) for x in v]
for d in sorted({k[0] for k in A}): AC[d] = [sum(v[i] for (dd, _), v in A.items() if dd == d) for i in range(4)]
for d in sorted({k[0] for k in S}): assert sum(v[0] for (dd, _), v in S.items() if dd == d) == ST[d][0], d   # 商品別の合計 = 店全体
T = '2026-11-12'; P7 = [d for d in sorted(ST) if '2026-11-05' <= d <= '2026-11-11']; THU = ['2026-10-22', '2026-10-29', '2026-11-05']; Y = '2026-11-11'
assert len(P7) == 7 and len(ST) == 22 and set(ST) == set(AC)
H = {}   # 時間別（Meta）: 今日の8時台と、昨日の同じ時間
for d, h, *v in rd('meta_hour_1111_1112.txt'): H[(d, int(h))] = [int(x) for x in v]
for _d in (T, Y): assert abs(sum(H[(_d, h)][0] for h in range(9)) - AC[_d][0]) <= 10, (_d, sum(H[(_d, h)][0] for h in range(9)), AC[_d][0])   # 時間別の合計とキャンペーン別の合計は端数で数円ずれる（11/11は2円）
net = lambda d: ST[d][0] - ST[d][1]; ad = lambda d: AC[d][0]
def units(n, gr): p = PRICE.get(n); return gr // p if p and gr % p == 0 else None
def cogs(d): return sum((units(n, gr) or 0) * COST.get(n, 0) for (dd, n), (gr, ds) in S.items() if dd == d and gr)
print('■ 店全体（0〜8時台）')
def rk(lab, f, fm):
    t = f(T); xs = [f(d) for d in P7]
    print(f"  {lab}: 今日 {fm.format(t)} ／ 過去7日 中央値{fm.format(st.median(xs))}（{fm.format(min(xs))}〜{fm.format(max(xs))}）今日より低い日{sum(x < t for x in xs)}/7 ／ 木曜 {'・'.join(fm.format(f(d)) for d in THU)} ／ 前日 {fm.format(f(Y))}")
for lab, f, fm in [('売上', net, '{:,.0f}'), ('注文', lambda d: ST[d][2], '{:.0f}'), ('広告費', ad, '{:,.0f}'), ('MER', lambda d: net(d) / ad(d), '{:.2f}'),
                   ('来訪', lambda d: ST[d][3], '{:.0f}'), ('注文÷来訪%', lambda d: ST[d][2] / ST[d][3] * 100, '{:.2f}'), ('購入完了した来訪÷来訪%（管理画面のCVR）', lambda d: ST[d][6] / ST[d][3] * 100, '{:.2f}'),
                   ('カゴ投入率%', lambda d: ST[d][4] / ST[d][3] * 100, '{:.2f}'), ('チェックアウト完了%', lambda d: ST[d][6] / ST[d][5] * 100, '{:.0f}'), ('客単価', lambda d: net(d) / ST[d][2], '{:,.0f}'),
                   ('来訪1件あたり広告費', lambda d: ad(d) / ST[d][3], '{:.1f}'),
                   ('CPM', lambda d: AC[d][0] / AC[d][1] * 1000, '{:,.0f}'), ('CTR%', lambda d: AC[d][2] / AC[d][1] * 100, '{:.2f}'), ('1クリックあたり広告費', lambda d: AC[d][0] / AC[d][2], '{:.0f}')]:
    rk(lab, f, fm)
mult = lambda d: (net(d) - cogs(d)) / ad(d)
print(f"  倍率（11/5以降のみ原価計算）: 今日 {mult(T):.2f} ／ 過去7日 中央値{st.median([mult(d) for d in P7]):.2f}（{min(mult(d) for d in P7):.2f}〜{max(mult(d) for d in P7):.2f}）今日より低い日{sum(mult(d) < mult(T) for d in P7)}/7 ／ 前日 {mult(Y):.2f}")
print(f"  今日の利益（0〜8時台・広告費は着地途中）: {net(T)-cogs(T)-ad(T):+,.0f} ／ 前日の同時刻 {net(Y)-cogs(Y)-ad(Y):+,.0f}")
# 8時台の広告費がまだ着地途中の場合
for add in (2400, 2600):
    print(f"  8時台の広告費があと{add:,}円増えた場合: 広告費 {ad(T)+add:,}・MER {net(T)/(ad(T)+add):.2f}・倍率 {(net(T)-cogs(T))/(ad(T)+add):.2f}")
print(f"  8時台だけの広告費: 今日 {H[(T,8)][0]:,}（取得09:0x）／ 昨日 {H[(Y,8)][0]:,}（確定後）。0〜7時台: 今日 {sum(H[(T,h)][0] for h in range(8)):,} ／ 昨日 {sum(H[(Y,h)][0] for h in range(8)):,}")
# 終日との関係
FS = collections.defaultdict(int); FA = collections.defaultdict(float)
for x in csv.DictReader(open(R + 'data/daily/daily_sales.csv')): FS[x['date']] += int(x['gross']) - int(x['disc'])
for x in csv.DictReader(open(R + 'data/daily/daily_ad.csv')): FA[x['date']] += float(x['cost'])
HD = [d for d in sorted(ST) if d < T]
x = [net(d) / ad(d) for d in HD]; y = [FS[d] / FA[d] for d in HD]
df = [b - a for a, b in zip(x, y)]
print(f"\n■ 0〜8時台と終日の関係（{HD[0]}〜{HD[-1]}・{len(HD)}日）: 店全体MER r={st.correlation(x, y):.2f}・終日MER−0〜8時台MER 中央値{st.median(df):+.2f}（{min(df):+.2f}〜{max(df):+.2f}）")
sh = [net(d) / FS[d] for d in HD]; so = [ST[d][2] for d in HD]
print(f"  0〜8時台の売上が終日に占める割合: 中央値{st.median(sh)*100:.0f}%（{min(sh)*100:.0f}〜{max(sh)*100:.0f}%）")
print('  日別（0〜8時台MER → 終日MER）:', '・'.join(f"{d[5:]} {a:.2f}→{b:.2f}" for d, a, b in zip(HD[-8:], x[-8:], y[-8:])))
print('\n■ 昨日と今日（同じ0〜8時台）')
for lab, f, fm in [('来訪', lambda d: ST[d][3], '{:,}'), ('注文', lambda d: ST[d][2], '{:,}'), ('購入完了した来訪', lambda d: ST[d][6], '{:,}'), ('注文÷来訪%', lambda d: ST[d][2] / ST[d][3] * 100, '{:.2f}'),
                   ('購入完了した来訪÷来訪%', lambda d: ST[d][6] / ST[d][3] * 100, '{:.2f}'), ('売上', net, '{:,}'), ('客単価', lambda d: net(d) / ST[d][2], '{:,.0f}'), ('広告費', ad, '{:,}'),
                   ('Metaのクリック', lambda d: AC[d][2], '{:,}'), ('Metaの表示', lambda d: AC[d][1], '{:,}')]:
    a, b = f(Y), f(T); print(f"  {lab}: 昨日 {fm.format(a)} → 今日 {fm.format(b)}（{(b/a-1)*100:+.0f}%）")
SHh = {(d, int(h)): [int(x) for x in v] for d, h, *v in rd('shop_hour_1111_1112.txt')}
print('  時間別（来訪／注文）: ' + ' '.join(f"{h}時 {SHh[(Y,h)][3]}/{SHh[(Y,h)][0]}→{SHh[(T,h)][3]}/{SHh[(T,h)][0]}" for h in range(9)))
print(f"  昨日の終日: 来訪 {sum(SHh[(Y,h)][3] for h in range(24)):,}・注文 {sum(SHh[(Y,h)][0] for h in range(24))}・購入完了した来訪 {sum(SHh[(Y,h)][6] for h in range(24))}・CVR {sum(SHh[(Y,h)][6] for h in range(24))/sum(SHh[(Y,h)][3] for h in range(24))*100:.2f}%")
print(f"  昨日の9時台以降: 来訪 {sum(SHh[(Y,h)][3] for h in range(9,24)):,}・注文 {sum(SHh[(Y,h)][0] for h in range(9,24))}・注文÷来訪 {sum(SHh[(Y,h)][0] for h in range(9,24))/sum(SHh[(Y,h)][3] for h in range(9,24))*100:.2f}%")
print('\n■ 商品別（0〜8時台）: 今日 個数・広告費・倍率 ／ 過去7日の同時刻 倍率の中央値（範囲）・個数の中央値・広告費の中央値')
def pm(d, n):
    gr, ds = S[(d, n)]; a = A[(d, n)][0]; u = (units(n, gr) or 0) if gr else 0
    return (None if not a else (gr - ds - u * COST.get(n, 0)) / a), u, a
for n in ['伸縮ガラスクリーナー', 'ワイド水切りワイパー', 'W固定スマホ車載ホルダー', 'クリアビューレインガードフィルム', '伸縮ワックス洗車ブラシ', 'ナノガラス脱毛パッド', '4-in-1マルチクリーナー',
          'マグネットドアクッション', '快適マジックインソール', '防風あったか裏起毛パンツ', 'すき間収納シートポケット']:
    m, u, a = pm(T, n); xs = [pm(d, n)[0] for d in P7 if pm(d, n)[2] >= 2000]; us = [pm(d, n)[1] for d in P7 if pm(d, n)[2] >= 2000]; as_ = [pm(d, n)[2] for d in P7 if pm(d, n)[2] >= 2000]
    cl = A[(T, n)]
    print(f"  {n}: {u}個・{a:,}円・{'—' if m is None else f'{m:.2f}'}（クリック{cl[2]}・Metaカート{cl[4]}・Meta購入{cl[5]}）／ {f'{st.median(xs):.2f}（{min(xs):.2f}〜{max(xs):.2f}・{len(xs)}日）・{st.median(us):g}個・{st.median(as_):,.0f}円' if xs else '—'}")
print('  カタログ:', f"{A[(T,'カタログ全部（テスト）')][0]:,}円", '／ 加湿器（停止前の残り）:', f"{A[(T,'コードレスダブルミスト加湿器')][0]:,}円")
print('\n■ 原価・売価が当たらなかった売上（0〜8時台）')
for d in P7 + [T]:
    miss = [(n, gr) for (dd, n), (gr, ds) in S.items() if dd == d and gr and (units(n, gr) is None or n not in COST)]
    if miss: print(' ', d[5:], miss)
