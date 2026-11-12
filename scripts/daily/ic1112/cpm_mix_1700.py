# -*- coding: utf-8 -*-
"""11/12(木) 17:0x アカウント全体のCPMが 10/22〜10/28 → 11/10〜11/11 で上がった分を、「出している広告セットの入れ替わり」と「同じ広告セットの中での上昇」に分ける。
入力: cpc_adset_daily_1022_1111_raw.txt（Meta fresh・終日）。両方の期間に出ている広告セットは前の期間のCPMを当てはめ、後の期間だけの広告セットは実際のCPMのまま（＝入れ替わりの側に入る）。"""
import os, csv, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'
iv = lambda x: 0 if x in ('null', '') else int(x)
A = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
P1 = [f'2026-10-{d}' for d in range(22, 29)]; P2 = ['2026-11-10', '2026-11-11']
for l in open(D + 'cpc_adset_daily_1022_1111_raw.txt'):
    if not l.startswith('2026-'): continue
    d, cp, s, c, i, r, k = next(csv.reader([l.strip()]))
    p = 'a' if d in P1 else 'b' if d in P2 else None
    if p:
        for j, v in enumerate((c, i, k)): A[p][s][j] += iv(v)
a = {s: v for s, v in A['a'].items() if v[1] > 0}; b = {s: v for s, v in A['b'].items() if v[1] > 0}
T = lambda t: [sum(v[j] for v in t.values()) for j in range(3)]
(ca, ia, ka), (cb, ib, kb) = T(a), T(b)
common = [s for s in b if s in a and a[s][0] >= 20000 and b[s][0] >= 5000]
imix = sum((b[s][0] / (a[s][0] / a[s][1])) if s in common else b[s][1] for s in b)
print(f"アカウント全体のCPM: 10/22〜10/28 {ca/ia*1000:,.0f} → 11/10〜11/11 {cb/ib*1000:,.0f}（{(cb/ib/(ca/ia)-1)*100:+.0f}%）")
print(f"  広告セットごとのCPMが前の期間のままで、配分だけ今の形だった場合: {cb/imix*1000:,.0f} ＝ 入れ替わりの分 {cb/imix*1000-ca/ia*1000:+,.0f}／同じ広告セットの中の上昇 {cb/ib*1000-cb/imix*1000:+,.0f}")
print('  広告費の割合とCPM（前 → 後）:')
for s in sorted(set(a) | set(b), key=lambda s: -(b.get(s, [0])[0])):
    x, y = a.get(s), b.get(s)
    if (x and x[0] / ca > 0.03) or (y and y[0] / cb > 0.03):
        print(f"    {s}: 割合 {0 if not x else x[0]/ca*100:.0f}→{0 if not y else y[0]/cb*100:.0f}%・CPM {'—' if not x else f'{x[0]/x[1]*1000:,.0f}'}→{'—' if not y else f'{y[0]/y[1]*1000:,.0f}'}")
nano = [s for s in a if 'ナノガラス' in s]
print(f"  ナノガラス脱毛パッド（全セット）の割合: {sum(a[s][0] for s in nano)/ca*100:.0f}% → {sum(b[s][0] for s in b if 'ナノガラス' in s)/cb*100:.0f}%・CPM {sum(a[s][0] for s in nano)/sum(a[s][1] for s in nano)*1000:,.0f}")
