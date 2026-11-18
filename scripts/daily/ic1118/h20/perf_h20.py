# -*- coding: utf-8 -*-
"""11/18 21:4x 「広告追加した商品のパフォわるい？きょう」: 0〜20時台を、過去7日（11/11〜17）の同じ時刻と比べる（商品別・広告費が出た全キャンペーン）
期待注文＝過去7日の 注文÷広告費 × 今日の広告費（過去が2日以上ある商品だけ）。日中の数字なので予算の判定には使わない"""
import collections, math
num = lambda x: float(x)
T = collections.defaultdict(lambda: [0.0] * 5); TA = []; P = collections.defaultdict(float); PD = collections.defaultdict(set); S = collections.defaultdict(lambda: [0.0, 0.0])
AL = {'スマートノーズEMS美顔器v2': 'スマートノーズEMS美顔器', '携帯電動シェーバーv2': '携帯電動シェーバー', '快適マジックインソール v3': '快適マジックインソール', '快適マジックインソールv2': '快適マジックインソール',
      '高見えレザーヘッドレストフックv2': '高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv4': '高見えレザーヘッドレストフック', '高見えレザーヘッドレストフックv5': '高見えレザーヘッドレストフック', 'ポータブルヒートシーラーv2': 'ポータブルヒートシーラー'}
for l in open('raw.txt'):
    if l[0] == '#': continue
    p = l.strip().split(',')
    if p[0] == 'T':
        c = AL.get(p[1], p[1]); v = [num(x) for x in p[3:]]
        for i in range(5): T[c][i] += v[i]
        TA.append((c, p[2], v))
    elif p[0] == 'P':
        c = AL.get(p[2], p[2]); P[(c, 'ad')] += num(p[3]); PD[c].add(p[1])
    else:
        S[(p[1], p[2])][0] += num(p[3]) + num(p[4]); S[(p[1], p[2])][1] += num(p[5])
pois = lambda k, lam: sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(int(k) + 1))
ADDED = {'マグネットドアクッション', 'ワイド水切りワイパー', '伸縮ガラスクリーナー', 'スマートノーズEMS美顔器', '携帯電動シェーバー', 'W固定スマホ車載ホルダー'}
print('商品（★＝同じ広告セットに広告を2本以上出している）: 今日の注文・広告費・売上÷広告費 ／ 期待注文（過去7日の同時刻）・偶然か')
rows = []
for c, v in T.items():
    if v[0] < 1000: continue
    o = S[('2026-11-18', c)][1]; net = S[('2026-11-18', c)][0]
    ds = sorted(PD.get(c, ()))
    po = sum(S[(d, c)][1] for d in ds); pa = P[(c, 'ad')]
    if c.startswith('カタログ'): rows.append((c, v[0], f'  {c}: 広告費 {v[0]:,.0f}（商品に分けられない）')); continue
    if len(ds) >= 2 and pa > 0 and po > 0:
        lam = po / pa * v[0]; lo = pois(o, lam); hi = 1 - pois(o - 1, lam) if o > 0 else 1
        side = '少ない側' if o < lam else '多い側'; p = lo if o < lam else hi
        verdict = '偶然では起きにくい' if p < 0.025 else ('偶然でも起きるが端' if p < 0.1 else '偶然の範囲内')
        rows.append((c, v[0], f"  {'★' if c in ADDED else '  '}{c[:16]:<16} {o:.0f}件・{v[0]:,.0f}円・{net/v[0]:.2f} ／ 期待 {lam:.1f}件（過去{len(ds)}日）・{side} {p:.0%} → {verdict}"))
    else:
        rows.append((c, v[0], f"  {'★' if c in ADDED else '  '}{c[:16]:<16} {o:.0f}件・{v[0]:,.0f}円・{net/v[0]:.2f} ／ 比べる過去なし（今日始めた・再開）"))
for r in sorted(rows, key=lambda x: -x[1]): print(r[2])
print('■ 広告を2本出している商品の、広告ごとの今日（Meta 計上・0〜20時台）')
for c in sorted(ADDED):
    ads = [(a, v) for cc, a, v in TA if cc == c and v[0] > 0]
    tot = sum(v[0] for a, v in ads)
    print(f'  {c[:14]}: ' + '／'.join(f'{a} 取り分{v[0]/tot:.0%}・CPM {v[0]/v[1]*1000:,.0f}・クリック率 {v[2]/v[1]*100:.2f}%・購入 {v[4]:.0f}' for a, v in ads))
