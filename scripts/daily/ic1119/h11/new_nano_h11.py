# -*- coding: utf-8 -*-
"""11/19 11時 「昨日出した新規広告の調子悪い？／ナノガラスはどんな感じ？」。11/18 終日（data/daily・o1118 の広告別）＋ 11/19 0〜10時台（raw.txt）。
日中の数字なので予算の判断には使わない（基準 5 の2日目の判定は 11/20 朝に 11/19 終日で）"""
import csv, collections
R = collections.defaultdict(list)
for l in open('raw.txt'):
    if l[0] != '#': p = l.strip().split(','); R[p[0]].append(p[1:])
COST = {'高見えレザーヘッドレストフック': 732, 'ポータブルヒートシーラー': 1119, '壁掛けディスペンサー': 2604}
CAMP = {'高見えレザーヘッドレストフック': '高見えレザーヘッドレストフックv5', 'ポータブルヒートシーラー': 'ポータブルヒートシーラーv2', '壁掛けディスペンサー': 'ディスペンサーv2'}
PRICE = {'高見えレザーヘッドレストフック': 3980, 'ポータブルヒートシーラー': 3980, '壁掛けディスペンサー': 6980}
S18 = collections.defaultdict(lambda: [0, 0])
for r in csv.DictReader(open('../../../../data/daily/daily_sales.csv')):
    if r['date'] == '2026-11-18': S18[r['name']] = [int(r['gross']), int(r['disc'])]
A18 = {}; 
for l in open('../../o1118/meta_camp_1117_1118_raw.txt'):
    if l.startswith('2026-11-18,'): p = l.strip().split(','); A18[p[1]] = [int(x) for x in p[2:]]
M19 = {p[0]: [int(x) for x in p[2:]] for p in R['M']}
S19 = {p[0]: [int(x) for x in p[1:]] for p in R['S']}
for n, c in CAMP.items():
    a18 = A18.get(c, [0] * 6); m19 = M19.get(c, [0] * 6)
    g18, d18 = S18[n]; q18 = g18 // PRICE[n]; g19, d19, o19, q19 = S19.get(n, [0, 0, 0, 0])
    ad = a18[0] + m19[0]; net = g18 - d18 + g19 - d19; q = q18 + q19
    print(f'{n}（{c}）: 11/18 広告 {a18[0]:,}・クリック率 {a18[2]/a18[1]:.2%}・CPM {a18[0]/a18[1]*1000:,.0f}・Meta カート {a18[4]}・{q18}個 ／ '
          f'11/19 0〜10時台 広告 {m19[0]:,}・クリック率 {m19[2]/m19[1]:.2%}・CPM {m19[0]/m19[1]*1000:,.0f}・Meta カート {m19[4]}・{q19}個（{o19}注文） ／ '
          f'通算 広告 {ad:,}・{q}個・倍率 {(net-q*COST[n])/ad:.2f}（途中）・基準6の線 {(PRICE[n]-COST[n])*3:,}')
N = [(d, int(o)) for d, o in R['N']]; past = [o for d, o in N if d < '2026-11-19']; t = N[-1][1]
assert len(past) == 21
print(f'ナノ 0〜10時台の注文: 今日 {t}・過去21日（10/29〜11/18）最小 {min(past)}・最大 {max(past)}・今日より少ない日 {sum(o < t for o in past)}・同じ日 {sum(o == t for o in past)}・中央値 {sorted(past)[10]}')
m = M19['ナノガラス脱毛パッド']; print(f'ナノ Meta 今日: 広告 {m[0]:,}（日予算 21,000）・クリック率 {m[2]/m[1]:.2%}・カート {m[4]}・購入 {m[5]}')
# シーラー v2: 前のキャンペーン（10/12〜11/10・relaunch/cand_1118.txt）の倍率なら、この広告費で何個売れるか（1個の粗利 3,980−1,119。値引きは無視）
import math
def ple(k, l): return sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
for lab, m in (('前のキャンペーン通算 1.48', 1.48), ('前のキャンペーン最後の3日 1.19', 1.19)):
    lam = 10750 * m / (3980 - 1119)
    print(f'シーラー v2: {lab} なら 10,750円で 期待 {lam:.1f}個 → 1個以下の確率 {ple(1, lam):.1%}')
