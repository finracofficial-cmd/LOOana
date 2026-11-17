# -*- coding: utf-8 -*-
"""11/18 「商品を出してたくさん売れるのと売れないものの違いって何？ノーズとかめっちゃ売れてるじゃん？」
直近30日（10/19〜11/17）に広告費が3万円以上の商品について、倍率＝(売上−原価)÷広告費 を6つに分けて、店全体の値と比べる。
  倍率 ＝ 表示÷広告費（CPMの逆）× クリック÷表示 × 来訪÷クリック × 注文÷来訪 × 売上÷注文 × 粗利率
  売上・原価・広告費は w1117.py（/tmp/rep1117w.pkl・実測の積み直し）、表示・クリックは Meta、来訪はその商品ページから入った来訪（Shopify）、注文はその商品を含む注文（o1117/ord30_raw.json）
  注: 来訪は「その商品ページから入った人」、注文は「その商品を含む注文」なので、ほかのページから入って買った分も注文に入る（近似）。v2・v3 は元の商品に足す
入力: ic1118/meta_camp_30d_raw.txt・ic1118/landing_30d_raw.txt・o1117/ord30_raw.json"""
import pickle, json, math, collections, statistics as st
R = pickle.load(open('/tmp/rep1117w.pkl', 'rb'))
D = 'scripts/daily/'
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
rows = []
for n in L:
    a = R['A30'].get(n, 0); s = R['N30'].get(n, 0); k = R['K30'].get(n, 0); q = R['Q30'].get(n, 0)
    m = M.get(n); o = O.get(n, 0)
    if not m or a < 30000 or not o: continue
    cost, imp, clk = m[0], m[1], m[2]; ses = L[n][0]
    f = dict(n=n, a=a, s=s, k=k, q=q, o=o, mult=(s - k) / a, profit=s - k - a,
             imp_per_yen=imp / cost * 1000, ctr=clk / imp, ses_clk=ses / clk, ord_ses=o / ses, aov=s / o, margin=(s - k) / s, cart=L[n][1] / ses)
    rows.append(f)
keys = [('imp_per_yen', '表示/1000円（CPMの逆）'), ('ctr', 'クリック率'), ('ses_clk', '来訪÷クリック'), ('ord_ses', '注文÷来訪'), ('aov', '1注文の売上'), ('margin', '粗利率')]
med = {k: st.median(r[k] for r in rows) for k, _ in keys}
print(f'■ 30日（10/19〜11/17）・広告費3万円以上の {len(rows)} 商品。各要素は全商品の中央値との比（+は良い）。倍率 ＝ 6つの掛け算')
print('  中央値: ' + '・'.join(f"{lab} {med[k]*100:.2f}%" if k in ('ctr', 'ord_ses', 'margin') else f"{lab} {med[k]:,.2f}" for k, lab in keys))
for r in sorted(rows, key=lambda r: -r['mult']):
    parts = '・'.join(f"{lab.split('（')[0]} {r[k]/med[k]-1:+.0%}" for k, lab in keys)
    print(f"  {r['n']}: 倍率 {r['mult']:.2f}・利益 {r['profit']:+,.0f}・広告 {r['a']:,.0f}・{r['o']}注文｜{parts}｜カート÷来訪 {r['cart']*100:.1f}%")
# どの要素が倍率の差をいちばん説明するか（対数の分散の分け方: 各要素と倍率の対数の共分散 ÷ 倍率の対数の分散）
lm = [math.log(r['mult']) for r in rows if r['mult'] > 0]; rr = [r for r in rows if r['mult'] > 0]
vm = st.pvariance(lm); mm = st.mean(lm)
print('■ 商品どうしの倍率の差は、どの要素の差から来ているか（対数で分けた割合・合計100%）')
for k, lab in keys:
    x = [math.log(r[k]) for r in rr]; mx = st.mean(x)
    cov = sum((a - mx) * (b - mm) for a, b in zip(x, lm)) / len(x)
    print(f'  {lab}: {cov/vm*100:+.0f}%')
