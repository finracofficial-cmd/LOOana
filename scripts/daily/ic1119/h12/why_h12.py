# -*- coding: utf-8 -*-
"""11/19 12:5x 「なんで今日のパフォーマンスが悪いのかを詳しく」: 0〜11時台を過去21日（10/29〜11/18）の同じ時刻と比べる。
①店全体: 注文÷広告費 を CPM・着地÷表示・カート÷着地・注文÷カート に分ける ②商品別: 過去7日（11/12〜18）の同時刻の 注文÷広告費 × 今日の広告費 と比べる（ポアソン）
③CPM: 過去7日の同時刻との差を「どの商品にお金を使ったか（配分）」と「同じ商品の中での値上がり」に分ける。日中の数字なので予算の判断には使わない"""
import collections, math, statistics as st
O = {}; A = {}; C = collections.defaultdict(dict); P = {}; T = {}; TS = 0
for l in open('raw.txt'):
    if l[0] == '#': continue
    p = l.strip().split(',')
    if p[0] == 'O': O[p[1]] = int(p[2])
    elif p[0] == 'A': A[p[1]] = [int(x) for x in p[2:]]
    elif p[0] == 'C': C[p[1]][p[2]] = [int(x) for x in p[3:]]
    elif p[0] == 'P': P[p[1]] = int(p[2])
    elif p[0] == 'T': T[p[1]] = (int(p[2]), int(p[3]))
    elif p[0] == 'TS': TS = sum(int(x) for x in p[1].split('+'))
for d in C: A[d] = [sum(v[i] for v in C[d].values()) for i in range(5)]
TD = '2026-11-19'; past = [d for d in sorted(O) if d < TD]; assert len(past) == 21 and set(past) <= set(A)
assert sum(o for o, q in T.values()) == O[TD] == 24
def met(d):
    c, i, lpv, atc, pu = A[d]; o = O[d]
    return collections.OrderedDict([('注文', o), ('広告費', c), ('注文÷広告費1万円', o / c * 1e4), ('CPM', c / i * 1000), ('着地÷表示%', lpv / i * 100),
                                    ('着地÷広告費1万円', lpv / c * 1e4), ('カート÷着地%（Meta）', atc / lpv * 100), ('注文÷カート%', o / atc * 100), ('注文÷着地%', o / lpv * 100)])
print(f'■ 店全体 0〜11時台（今日 と 過去21日 10/29〜11/18 の同じ時刻）・今日の売上（値引後の小計）{TS:,}・売上÷広告費 {TS/A[TD][0]:.2f}')
for k, v in met(TD).items():
    xs = [met(d)[k] for d in past]; lo = sum(x < v for x in xs)
    out = '範囲の外（下）' if v < min(xs) else ('範囲の外（上）' if v > max(xs) else '範囲内')
    print(f'  {k}: 今日 {v:,.2f}・過去 {min(xs):,.2f}〜{max(xs):,.2f}（中央値 {st.median(xs):,.2f}）・今日より低い日 {lo}/21 → {out}')
print('■ 日ごと（同じ時刻）: 注文・広告費・注文÷広告費1万円・CPM・着地÷表示・注文÷着地')
for d in past[-10:] + [TD]:
    m = met(d); print(f"  {d[5:]}: {m['注文']}件・{m['広告費']:,}・{m['注文÷広告費1万円']:.2f}・CPM {m['CPM']:,.0f}・{m['着地÷表示%']:.2f}%・{m['注文÷着地%']:.2f}%")
# ② 商品別
AL = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール', '快適マジックインソールv2': '快適マジックインソール',
      '高見えレザーヘッドレストフックv2': '高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv4': '高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv5': '高見えレザーヘッドレストフック',
      'ポータブルヒートシーラーv2': 'ポータブルヒートシーラー', 'ディスペンサーv2': '壁掛けディスペンサー'}
def ple(k, l): return sum(math.exp(-l + i * math.log(l) - math.lgamma(i + 1)) for i in range(k + 1)) if l > 0 else 1.0
W7 = [d for d in past if d >= '2026-11-12']; PA = collections.defaultdict(float); TA = collections.defaultdict(float); PD = collections.defaultdict(set)
for d in W7:
    for c, v in C[d].items(): PA[AL.get(c, c)] += v[0]; PD[AL.get(c, c)].add(d)
for c, v in C[TD].items(): TA[AL.get(c, c)] += v[0]
print('■ 商品別 0〜11時台（期待＝11/12〜18 の同時刻の 注文÷広告費 × 今日の広告費）')
exp_tot = 0; act_tot = 0
for n in sorted(TA, key=lambda n: -TA[n]):
    a = TA[n]; o, q = T.get(n, (0, 0))
    if n.startswith('カタログ'): print(f'  {n}: 広告費 {a:,.0f}（商品に分けられない）'); continue
    if len(PD[n]) < 3 or P.get(n, 0) < 3: print(f'  {n}: {o}注文（{q}個）・広告費 {a:,.0f}（比べる過去が短い）'); continue
    lam = P[n] / PA[n] * a; pr = ple(o, lam) if o < lam else 1 - ple(o - 1, lam); exp_tot += lam; act_tot += o
    v = '偶然では起きにくい' if pr < 0.025 else ('端' if pr < 0.16 else '範囲内')
    print(f"  {n}: {o}注文（{q}個）・広告費 {a:,.0f}・期待 {lam:.1f}・{'少ない' if o < lam else '多い'}側 {pr:.0%} → {v}")
pr = ple(act_tot, exp_tot); print(f'  比べられる商品の合計: {act_tot}注文・期待 {exp_tot:.1f}・この数以下 {pr:.0%}')
print('  広告なしで売れた: ' + '・'.join(f'{n} {o}' for n, (o, q) in T.items() if n not in TA and o))
# ③ CPM: 過去7日の同時刻 → 今日。表示÷広告費（ipy）＝Σ 広告費の割合 × その商品の ipy。配分の分 と 商品の中の分
pc = collections.defaultdict(lambda: [0.0, 0.0])
for d in W7:
    for c, v in C[d].items(): pc[c][0] += v[0]; pc[c][1] += v[1]
ptc = sum(v[0] for v in pc.values()); pti = sum(v[1] for v in pc.values()); ttc, tti = A[TD][0], A[TD][1]
ipy_p = pti / ptc; ipy_t = tti / ttc; mix = 0; within = 0; rows = []
for c, v in C[TD].items():
    wt = v[0] / ttc; it = v[1] / v[0]
    if c in pc and pc[c][0] > 5000: ip = pc[c][1] / pc[c][0]; wp = pc[c][0] / ptc
    else: ip = it; wp = 0
    mix += (wt - wp) * ip; within += wt * (it - ip); rows.append((c, wp, wt, 1000 / ip, 1000 / it))
for c, v in pc.items():
    if c not in C[TD] or pc[c][0] <= 5000:
        if c in C[TD]: continue
        mix += (0 - v[0] / ptc) * (v[1] / v[0])
print(f'■ CPM の中身（0〜11時台）: 過去7日 {1000/ipy_p:,.0f} → 今日 {1000/ipy_t:,.0f}（{ipy_p/ipy_t-1:+.1%}）。表示÷広告費の差 {ipy_t-ipy_p:+.4f} ＝ 配分の分 {mix:+.4f} ＋ 同じ商品の中の分 {within:+.4f}（残り {ipy_t-ipy_p-mix-within:+.4f}）')
print(f'  → 配分だけ変わったら CPM {1000/(ipy_p+mix):,.0f}・同じ商品の中だけ変わったら CPM {1000/(ipy_p+within):,.0f}')
for c, wp, wt, cp, ct in sorted(rows, key=lambda r: -r[2]):
    print(f"  {c}: 広告費の割合 {wp:.0%} → {wt:.0%}・CPM {'—' if wp == 0 else f'{cp:,.0f}'} → {ct:,.0f}" + ('' if wp == 0 else f'（{ct/cp-1:+.0%}）'))
gone = [(c, v[0] / ptc, v[0] / v[1] * 1000) for c, v in pc.items() if c not in C[TD] and v[0] / ptc >= 0.01]
print('  過去7日にあって今日ない: ' + '・'.join(f'{c} {w:.0%}（CPM {m:,.0f}）' for c, w, m in sorted(gone, key=lambda x: -x[1])))
