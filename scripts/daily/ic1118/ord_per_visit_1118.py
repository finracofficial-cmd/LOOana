# -*- coding: utf-8 -*-
"""11/18 「来訪あたりの注文が高い理由を分析」
30日（10/19〜11/17）・広告費3万円以上の18商品で、来訪あたりの注文を ①段ごと（カート÷来訪・決済画面÷カート・購入完了÷決済画面・その商品を含む注文÷そのページからの購入完了）に分け、
②商品の性質（売価・元値に対する売価・出品してからの日数・レビュー件数・クリック率・CPM・ページのくり返しタイマーの有無）との順位相関（スピアマン）を見る。18商品なので |ρ|≧0.47 でおおむね偶然では起きにくい（片側5%）。
入力: ic1118/landing_30d_raw.txt・ic1118/meta_camp_30d_raw.txt・o1117/ord30_raw.json・ic1118/template_features.json・下の PROD（graphql 11/18 取得: templateSuffix・createdAt・reviews.rating_count・price・compareAtPrice）"""
import json, collections, statistics as st, datetime
D = 'scripts/daily/'
PROD = {  # 商品: (templateSuffix, createdAt, レビュー件数, 売価, 元値)
 'ナノバブルシャワーヘッド': ('shower-head', '2026-03-02', 13, 6980, 36280), '壁掛けディスペンサー': ('dis', '2026-03-20', 13, 6980, 14890), '姿勢サポートチェア': ('chair', '2026-04-12', 12, 5980, 16625),
 'ナノガラス脱毛パッド': ('datumoupad', '2026-05-10', 12, 3980, 9980), 'スマートノーズEMS美顔器': ('nosemassage', '2026-06-15', 8, 6980, 19800), 'W固定スマホ車載ホルダー': ('carholder', '2026-07-31', 5, 3980, 9980),
 '快適マジックインソール': ('insole', '2026-08-11', 4, 3980, 9980), '4-in-1マルチクリーナー': ('souziki', '2026-09-03', 4, 6980, 15980), '伸縮ガラスクリーナー': ('clenerrr', '2026-09-07', 4, 3980, 9980),
 '高見えレザーヘッドレストフック': ('carhook', '2026-09-09', 4, 3980, 9980), 'ポータブルヒートシーラー': ('carstorage', '2026-10-11', 3, 3980, 12800), 'コードレスダブルミスト加湿器': ('codelesskashituki', '2026-10-20', 3, 4980, 14800),
 '高見えレザードアポケット': ('letherdoorpocket', '2026-10-22', 2, 3980, 9980), '伸縮ワックス洗車ブラシ': ('carclener', '2026-10-22', 2, 4980, 12890), 'マグネットドアクッション': ('car-seion', '2026-10-31', 2, 3980, 9980),
 'ワイド水切りワイパー': ('mizukiri', '2026-11-04', 2, 3980, 9980), 'クリアビューレインガードフィルム': ('hassui', '2026-11-05', 2, 3980, 12800), '3WAY着る電気ブランケット': ('dennnetsu', '2026-11-13', 2, 5980, 12880)}
AL = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール', '快適マジックインソールv2': '快適マジックインソール',
      '高見えレザーヘッドレストフックv2': '高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv4': '高見えレザーヘッドレストフック', 'ディスペンサー': '壁掛けディスペンサー'}
M = collections.defaultdict(lambda: [0] * 6)
for l in open(D + 'ic1118/meta_camp_30d_raw.txt'):
    if l[0] == '#': continue
    p = l.strip().split(','); n = AL.get(p[0], p[0]); M[n] = [a + int(b) for a, b in zip(M[n], p[1:])]
L = {}
for l in open(D + 'ic1118/landing_30d_raw.txt'):
    if l[0] == '#': continue
    p = l.strip().split(','); L[p[0]] = [int(x) for x in p[2:]]
O = {}
for t, v in json.load(open(D + 'o1117/ord30_raw.json'))['rows']: O[t] = O.get(t, 0) + int(v)
TF = json.load(open(D + 'ic1118/template_features.json'))
T0 = datetime.date(2026, 11, 17)
rows = []
for n, (suf, cr, rv, pr, ca) in PROD.items():
    s, c, k, x = L[n]; m = M[n]; o = O[n]
    rows.append(dict(n=n, ord_ses=o / s, cart=c / s, chk=k / c, done=x / k, other=o / x, price=pr, disc=pr / ca, age=(T0 - datetime.date.fromisoformat(cr)).days,
                     rev=rv, ctr=m[2] / m[1], cpm=m[0] / m[1] * 1000, timer=1 if TF[suf]['loop_timer'] else 0, ses=s, o=o))
med = {k: st.median(r[k] for r in rows) for k in ('ord_ses', 'cart', 'chk', 'done', 'other')}
print('■ 来訪あたりの注文の段ごとの分け方（30日・中央値との比）。来訪あたりの注文 ＝ カート÷来訪 × 決済画面÷カート × 購入完了÷決済画面 × その商品を含む注文÷そのページからの購入完了')
print('  中央値: ' + '・'.join(f'{k} {v*100:.1f}%' for k, v in med.items()))
for r in sorted(rows, key=lambda r: -r['ord_ses']):
    print(f"  {r['n']}: 来訪あたりの注文 {r['ord_ses']*100:.2f}%（{r['ord_ses']/med['ord_ses']-1:+.0%}）｜カート {r['cart']/med['cart']-1:+.0%}・決済画面 {r['chk']/med['chk']-1:+.0%}・購入完了 {r['done']/med['done']-1:+.0%}・ほかのページからの注文 {r['other']/med['other']-1:+.0%}｜売価 {r['price']:,}・出品から {r['age']}日・レビュー {r['rev']}・来訪 {r['ses']:,}")
import math
def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); rk = [0] * len(v); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]: j += 1
        for t in range(i, j + 1): rk[o[t]] = (i + j) / 2
        i = j + 1
    return rk
def sp(a, b):
    ra, rb = rank(a), rank(b); ma, mb = st.mean(ra), st.mean(rb)
    return sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
y = [math.log(r['ord_ses']) for r in rows]
lv = st.pvariance(y)
print('■ 段ごとの効き（来訪あたりの注文の対数の差を、どの段の差が説明するか・合計100%）')
for k, lab in (('cart', 'カート÷来訪'), ('chk', '決済画面÷カート'), ('done', '購入完了÷決済画面'), ('other', 'ほかのページからの注文')):
    x = [math.log(r[k]) for r in rows]; mx, my = st.mean(x), st.mean(y)
    print(f'  {lab}: {sum((a-mx)*(b-my) for a, b in zip(x, y))/len(x)/lv*100:+.0f}%')
print('■ 商品の性質との順位相関（来訪あたりの注文と・18商品・|ρ|≧0.47 でおおむね偶然では起きにくい）')
for k, lab in (('price', '売価'), ('disc', '売価÷元値（小さいほど大きな割引表示）'), ('age', '出品からの日数'), ('rev', 'レビュー件数'), ('ctr', '広告のクリック率'), ('cpm', 'CPM'), ('timer', 'くり返しタイマーあり')):
    print(f"  {lab}: ρ = {sp([r[k] for r in rows], [r['ord_ses'] for r in rows]):+.2f}")
    if k != 'timer':
        print(f"    　カート÷来訪とは ρ = {sp([r[k] for r in rows], [r['cart'] for r in rows]):+.2f}")
g = [r for r in rows if r['price'] == 3980]; h = [r for r in rows if r['price'] > 3980]
print(f"■ 売価別: 3,980円 {len(g)}商品 来訪あたりの注文の中央値 {st.median(r['ord_ses'] for r in g)*100:.2f}%／4,980円以上 {len(h)}商品 {st.median(r['ord_ses'] for r in h)*100:.2f}%")
y1 = [r for r in rows if r['age'] <= 40]; y2 = [r for r in rows if r['age'] > 40]
print(f"■ 出品から40日以内 {len(y1)}商品 {st.median(r['ord_ses'] for r in y1)*100:.2f}%／それより前 {len(y2)}商品 {st.median(r['ord_ses'] for r in y2)*100:.2f}%")
print('■ 購入完了÷決済画面（決済で最後まで進む割合）との順位相関')
for k, lab in (('price', '売価'), ('age', '出品からの日数'), ('rev', 'レビュー件数')):
    print(f"  {lab}: ρ = {sp([r[k] for r in rows], [r['done'] for r in rows]):+.2f}")
print(f"■ 出品からの日数とレビュー件数の順位相関 ρ = {sp([r['age'] for r in rows], [r['rev'] for r in rows]):+.2f}（古い商品ほどレビューが多い）・出品からの日数と売価 ρ = {sp([r['age'] for r in rows], [r['price'] for r in rows]):+.2f}")
