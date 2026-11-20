# -*- coding: utf-8 -*-
"""11/21 「単価あげたい 複数売りとか、なにするべき」
30日（10/22〜11/20）の注文を、同じ商品の個数・別の商品との組み合わせで分ける。
入力（どれも Shopify の問い合わせ結果そのまま）: product_totals_1022_1120_raw.json・multi_lines_1022_1120_raw.json・nodisc_multi_orders_raw.json・ge3_orders_raw.json・
mixed_orders_raw.json・weekly_0831_1120_raw.json・product_totals_0629_1120_raw.json・data/daily/daily_order_bands.csv・/tmp/rep1120w.pkl（scripts/daily/w1120.py が作る。売価・原価・30日の広告費）"""
import json, os, csv, pickle, math
from collections import defaultdict, Counter
D0 = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(D0, '..', '..', '..', '..')
J = lambda f: json.load(open(os.path.join(D0, f)))
pt = J('product_totals_1022_1120_raw.json')['rows']; ml = J('multi_lines_1022_1120_raw.json')['rows']; g3 = J('ge3_orders_raw.json')['rows']; nd = J('nodisc_multi_orders_raw.json')['rows']
mx = J('mixed_orders_raw.json')['data']['nodes']; wk = J('weekly_0831_1120_raw.json')['rows']; pa = J('product_totals_0629_1120_raw.json')['rows']
W = pickle.load(open('/tmp/rep1120w.pkl', 'rb')); PRICE, COST, A30, N30, K30, Q30 = W['PRICE'], W['COST'], W['A30'], W['N30'], W['K30'], W['Q30']
assert W['D30'][0] == '2026-10-22' and W['D30'][-1] == '2026-11-20'
NOTREAL = {'15420006727922', '15412971831538', '8934499582194', ''}   # VIP特典（2つ）・優先配送
def short(title):
    c = [k for k in PRICE if k in title]; return max(c, key=len) if c else title[:14]
NAME = {r[0]: short(r[1]) for r in pt + pa if r[0]}
L = []
def P(*x):
    t = ' '.join(str(i) for i in x); print(t); L.append(t)
# 店全体の注文数（日別ファイル）
orders = ge7 = 0
for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'daily', 'daily_order_bands.csv'))):
    if '2026-10-22' <= r['date'] <= '2026-11-20': orders += int(r['orders']); ge7 += int(r['ge7000'])
# 同じ商品を2個以上（注文×商品）
q = defaultdict(int); byp = defaultdict(list)
for o, p, n, g, d in ml: q[o] += int(n); byp[p].append(int(n))
A = set(q)
real = lambda o: [(l['product']['id'].split('/')[-1], l['quantity']) for l in o['lineItems']['nodes'] if l['product'] and l['product']['id'].split('/')[-1] not in NOTREAL]
mixed = [o for o in mx if len({p for p, _ in real(o)}) >= 2]
mixed_ids = {o['id'].split('/')[-1] for o in mixed}
B = {o for o, n, g, d in nd} - A                                   # 1個ずつ・値引きなし
assert B <= mixed_ids, B - mixed_ids
multi_orders = A | B
same_only = A - mixed_ids
P('■ 30日（10/22〜11/20）の注文 {:,}件・7,000円以上 {}件（{:.1f}%）'.format(orders, ge7, ge7 / orders * 100))
P('  商品を2個以上買った注文: {}件（{:.1f}%）'.format(len(multi_orders), len(multi_orders) / orders * 100))
P('    同じ商品だけを2個以上: {}件（{:.1f}%）'.format(len(same_only), len(same_only) / orders * 100))
P('    別の商品を組み合わせた注文: {}件（{:.1f}%）'.format(len(mixed), len(mixed) / orders * 100))
c = Counter(min(int(n), 4) for o, p, n, g, d in ml); P('  同じ商品の個数（注文×商品 {}行）: 2個 {}・3個 {}・4個以上 {}'.format(len(ml), c[2], c[3], c[4]))
odd = [(o, NAME.get(p, p), n, g, d) for o, p, n, g, d in ml if abs(-float(d) / float(g) - (0.10 if int(n) == 2 else 0.15)) > 0.001]
P('  値引きが 2個10%・3個以上15% でない行: {}（値引き0＝別々にカートへ入れた {}・1,000円多い＝クーポン {}・ほか {}）'.format(len(odd), sum(1 for x in odd if float(x[4]) == 0), sum(1 for x in odd if abs(-float(x[4]) - (0.10 if int(x[2]) == 2 else 0.15) * float(x[3]) - 1000) < 1), sum(1 for x in odd if float(x[4]) != 0 and abs(-float(x[4]) - (0.10 if int(x[2]) == 2 else 0.15) * float(x[3]) - 1000) >= 1)))
P('  1個の行に値引きが付いた注文（決済後のおすすめ・クーポンなど）: 0件（問い合わせ結果が0行）')
P('')
P('■ 商品別（30日・注文20件以上）: 注文 n・個数÷注文・2個以上の割合（偶然の幅）・3個以上・売価・原価・2個目で増える粗利（2個10%OFF）・30日の倍率')
rows = []
for pid, title, o, n, g, d in pt:
    if pid in NOTREAL or int(o) < 20: continue
    nm = NAME[pid]; o, n = int(o), int(n); m2 = len(byp[pid]); m3 = sum(1 for x in byp[pid] if x >= 3); pr = round(float(g) / n); co = K30[nm] / Q30[nm] if Q30.get(nm) else COST.get(nm)
    se = math.sqrt(m2 / o * (1 - m2 / o) / o); ad = A30.get(W['MAP'].get(nm, nm), A30.get(nm, 0)); bai = (N30[nm] - K30[nm]) / ad if ad else None
    rows.append((nm, o, n / o, m2 / o, se, m3 / o, pr, co, 0.8 * pr - co, bai, ad))
for nm, o, upo, s2, se, s3, pr, co, inc, bai, ad in sorted(rows, key=lambda r: -r[3]):
    P('  {}: n={}・{:.2f}・{:.0f}%（±{:.0f}）・{:.0f}%・{:,}円・{:,.0f}円・+{:,.0f}円・{}'.format(nm, o, upo, s2 * 100, 1.96 * se * 100, s3 * 100, pr, co, inc, '倍率 {:.2f}'.format(bai) if bai else '広告なし'))
P('')
P('■ 1注文あたり（30日・その商品の実売と原価 ÷ その商品が入った注文数）: 実売・粗利・広告費')
for nm, o, upo, s2, se, s3, pr, co, inc, bai, ad in sorted(rows, key=lambda r: -(N30[r[0]] - K30[r[0]]) / r[1]):
    P('  {}: 実売 {:,.0f}円・粗利 {:,.0f}円・広告費 {}'.format(nm, N30[nm] / o, (N30[nm] - K30[nm]) / o, '{:,.0f}円'.format(ad / o) if ad else '—'))
P('')
P('■ 別の商品の組み合わせ（{}件）'.format(len(mixed)))
pc = Counter()
for o in mixed:
    ps = sorted({NAME.get(p, p) for p, _ in real(o)})
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)): pc[(ps[i], ps[j])] += 1
for (a, b), n in pc.most_common(12): P('  {} ＋ {}: {}件'.format(a, b, n))
CAR = ('ガラスクリーナー', '洗車ブラシ', 'ワイパー', '車載', 'ドアクッション', 'ヘッドレストフック', 'レインガード', 'ドアポケット', 'シートポケット', 'シートボックス', '4-in-1')
car = sum(1 for o in mixed if all(any(k in NAME.get(p, p) for k in CAR) for p, _ in real(o)))
P('  うち、全部が車・掃除の用品（{}）: {}件'.format('・'.join(CAR), car))
inm = Counter(NAME.get(p, p) for o in mixed for p in {p for p, _ in real(o)})
P('  組み合わせに入った回数: ' + '・'.join('{} {}'.format(k, v) for k, v in inm.most_common(8)))
P('')
P('■ 週ごと（VIP特典・優先配送の行を除く）: 個数÷注文・値引き÷総額')
for w, o, n, g, d in wk: P('  {}の週: 注文 {}・{:.2f}・{:.1f}%'.format(w[5:10], o, int(n) / int(o), -float(d) / float(g) * 100))
P('')
P('■ 6/29〜11/20・注文200件以上の商品の 個数÷注文（同じ枠・同じ割引で売っている）')
al = sorted(((NAME[r[0]], int(r[2]), int(r[3]) / int(r[2])) for r in pa if r[0] not in NOTREAL and int(r[2]) >= 200), key=lambda x: -x[2])
P('  ' + '・'.join('{} {:.2f}（{:,}）'.format(a, u, n) for a, n, u in al))
P('')
P('■ 2個以上の割合が +5ポイント上がったら（広告費は同じ・2個10%OFFのまま）')
tot = 0
for nm, o, upo, s2, se, s3, pr, co, inc, bai, ad in sorted(rows, key=lambda r: -r[1])[:8]:
    v = o / 30 * 0.05 * inc; tot += v; P('  {}: 1日 {:.1f}注文 × 5% × {:,.0f}円 ＝ +{:,.0f}円/日'.format(nm, o / 30, inc, v))
P('  上の8商品の合計: +{:,.0f}円/日'.format(tot))
P('')
P('■ 割引を深くした場合に、同じ利益になるために必要な「2個を選ぶ人」の増え方（3,980円の商品）')
for nm in ('伸縮ガラスクリーナー', 'ナノガラス脱毛パッド', 'W固定スマホ車載ホルダー', '快適マジックインソール', '高見えレザーヘッドレストフック'):
    r = [x for x in rows if x[0] == nm][0]; pr, co = r[6], r[7]; base = 0.8 * pr - co
    P('  {}: 今（10%）+{:,.0f}円 ／ 15%OFF なら +{:,.0f}円＝{:.2f}倍必要 ／ 20%OFF なら +{:,.0f}円＝{:.2f}倍必要'.format(nm, base, 0.7 * pr - co, base / (0.7 * pr - co), 0.6 * pr - co, base / (0.6 * pr - co)))
P('  ※ 2個とも割り引く今の形での計算。1個で買うつもりだった人が2個に変えたときに増える粗利＝2個の粗利−1個の粗利')
open(os.path.join(D0, 'aov_1121.txt'), 'w').write('\n'.join(L) + '\n')
