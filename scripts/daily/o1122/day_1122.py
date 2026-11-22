# -*- coding: utf-8 -*-
"""11/23 定例: 11/22 の ①前日（11/21）との売上の差の中身 ②時間帯別（朝 0〜10・午後 11〜16・夜 17〜23） ③夜÷昼 ④VIP特典の行。入力は o1122 の取得ファイル（前日の注文数と日別の来訪は o1121）"""
import collections, math, os, json
D = os.path.dirname(os.path.abspath(__file__)) + '/'
OB = collections.defaultdict(list)
for l in open(D + 'orders_by_product_1121_1122.txt'):
    if l[0] == '#': continue
    d, n, o, g, dc, q = l.strip().split(','); OB[d].append((n, int(o), int(g), int(dc), int(q)))
ORD = {'2026-11-21': json.load(open(D + '../o1121/bands_1121_raw.json'))['data']['all']['count'], '2026-11-22': json.load(open(D + 'bands_vip_1122_raw.json'))['data']['all']['count']}
out = []
def day(d):
    rows = OB[d]; g = sum(r[2] for r in rows); dc = sum(r[3] for r in rows); q = sum(r[4] for r in rows if r[0] != '優先配送'); o = ORD[d]
    hi = [(r[0], r[4], r[2]) for r in rows if r[0] != '優先配送' and r[2] // r[4] > 3980]
    return dict(o=o, gross=g, disc=dc, net=g - dc, q=q, aov=(g - dc) / o, upo=q / o, unit=(g - sum(r[2] for r in rows if r[0] == '優先配送')) / q, dr=dc / g, hi_q=sum(x[1] for x in hi), hi_g=sum(x[2] for x in hi),
                lo_q=q - sum(x[1] for x in hi), lo_g=sum(r[2] for r in rows if r[0] != '優先配送' and r[2] // r[4] == 3980), ship=sum(r[2] for r in rows if r[0] == '優先配送'), hi=hi)
a, b = day('2026-11-21'), day('2026-11-22')
out.append('■ ① 11/21 → 11/22 の売上の差')
out.append(f"  注文 {a['o']} → {b['o']}・売上（値引後） {a['net']:,} → {b['net']:,}（{b['net']-a['net']:+,}・{b['net']/a['net']-1:+.1%}）")
out.append(f"  1注文の売上 {a['aov']:,.0f} → {b['aov']:,.0f}（{b['aov']-a['aov']:+,.0f}・{b['aov']/a['aov']-1:+.1%}）")
out.append(f"    1注文の個数 {a['upo']:.2f} → {b['upo']:.2f}（{b['upo']/a['upo']-1:+.1%}）・1個の値段（値引前） {a['unit']:,.0f} → {b['unit']:,.0f}（{b['unit']/a['unit']-1:+.1%}）・値引きの割合 {a['dr']:.1%} → {b['dr']:.1%}")
out.append(f"  3,980円の商品: {a['lo_q']}個 {a['lo_g']:,} → {b['lo_q']}個 {b['lo_g']:,}（{b['lo_g']-a['lo_g']:+,}）")
out.append(f"  4,980円以上の商品: {a['hi_q']}個 {a['hi_g']:,} → {b['hi_q']}個 {b['hi_g']:,}（{b['hi_g']-a['hi_g']:+,}）")
out.append('    11/21: ' + '・'.join(f'{n} {q}個' for n, q, g in a['hi']) + ' ／ 11/22: ' + '・'.join(f'{n} {q}個' for n, q, g in b['hi']))
out.append(f"  有料の優先配送 {a['ship']:,} → {b['ship']:,}・値引き {a['disc']:,} → {b['disc']:,}（{-(b['disc']-a['disc']):+,}）")
chk = (b['lo_g'] - a['lo_g']) + (b['hi_g'] - a['hi_g']) + (b['ship'] - a['ship']) - (b['disc'] - a['disc']); assert chk == b['net'] - a['net'], chk
V = {}; T = {}; MH = {}
ADT = sum(int(l.split(',')[2]) for l in open(D + 'meta_camp_1121_1122_raw.txt') if l.startswith('2026-11-22,'))   # 11/22 の広告費（暫定・キャンペーン合算）
for l in open(D + 'hourly_1122_raw.txt'):
    if l[0] == '#': continue
    p = l.strip().split(',')
    {'V': V, 'T': T, 'MH': MH}[p[0]][int(p[1])] = [int(x) for x in p[2:]]
assert sum(v[0] for v in V.values()) == b['o'] and sum(v[1] for v in V.values()) == b['gross'] and abs(sum(v[0] for v in MH.values()) - ADT) < 30   # 時間別の合計とキャンペーン合算は1円単位の丸めで数円ずれる
def ple(k, l): return sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1))
S = json.load(open(D + 'sess_daily_1004_1122.json'))['rows']; base = [r for r in S if '2026-10-23' <= r[0] <= '2026-11-21']; cvr = sum(int(r[4]) for r in base) / sum(int(r[1]) for r in base); cart = sum(int(r[2]) for r in base) / sum(int(r[1]) for r in base)
out.append(f'■ ② 11/22 の時間帯別（ふだん＝10/23〜11/21 の終日: カート率 {cart:.2%}・買う率 {cvr:.2%}）')
for lab, hs in (('朝 0〜10時台', range(0, 11)), ('午後 11〜16時台', range(11, 17)), ('夜 17〜23時台', range(17, 24)), ('終日', range(0, 24))):
    s = sum(T[h][0] for h in hs); c = sum(T[h][1] for h in hs); dn = sum(T[h][3] for h in hs); o = sum(V[h][0] for h in hs if h in V); net = sum(V[h][1] - V[h][2] for h in hs if h in V); ad = sum(MH[h][0] for h in hs); imp = sum(MH[h][1] for h in hs)
    e = s * cvr; pr = f'{dn}件以下 {ple(dn, e):.1%}' if dn < e else f'{dn}件以上 {1 - ple(dn - 1, e):.1%}'
    out.append(f'  {lab}: 来訪 {s}・カート率 {c/s:.1%}・購入 {dn}（{dn/s:.2%}・見込み {e:.1f}・{pr}）｜注文 {o}・売上 {net:,}・広告費 {ad:,}・売上÷広告費 {net/ad:.2f}・CPM {ad/imp*1000:,.0f}')
nt = range(18, 24); dy = range(0, 18)
f = lambda hs: (sum(V[h][1] - V[h][2] for h in hs if h in V), sum(MH[h][0] for h in hs), sum(V[h][0] for h in hs if h in V))
n_, d_ = f(nt), f(dy); r = (n_[0] / n_[1]) / (d_[0] / d_[1])
out.append(f'■ ③ 夜（18〜23時台）÷昼: 夜 売上 {n_[0]:,}・広告 {n_[1]:,}（{n_[1]/ADT:.0%}）・{n_[0]/n_[1]:.2f}・注文 {n_[2]} ／ 昼 {d_[0]:,}・{d_[1]:,}・{d_[0]/d_[1]:.2f}・注文 {d_[2]} → 夜÷昼 {r:.2f}（10/21〜11/10 平均 0.98・標準偏差 0.18 → {(r-0.98)/0.18:+.1f}σ）。11/21 は 1.21・11/20 は 1.43・11/19 は 1.19（o1121/day_1121.txt から転記）')
rows = [l.strip().split(',') for l in open(D + 'vip_line_1122_raw.txt') if not l.startswith('# ')]
no = [r for r in rows if r[4] == '0']
out.append(f'■ ④ VIP特典の行（11/22・対象の注文 {len(rows)}件）: 行あり {len(rows)-len(no)}・行なし {len(no)}' + ('（' + '・'.join(r[0] + ' ' + r[5] for r in no) + '）' if no else '') + '。11/21 は 16件中 行なし 3・11/20 は 12件中 行なし 1・11/19 14:37〜24:00 は 8件中 行なし 2・変更の前は 22件中 行なし 2（前日までの数字は o1121/day_1121.txt から転記）')
src = json.load(open(D + 'sess_source_1122_raw.json'))['rows']
out.append('■ ⑤ 来訪の入口（11/22）: ' + '・'.join(f'{r[0]} 来訪 {r[1]}・カート {r[2]}・購入 {r[4]}（{int(r[4])/int(r[1]):.2%}）' for r in src))
open(D + 'day_1122.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
