# -*- coding: utf-8 -*-
"""11/18 「全部均等に下がってるのが気になる。アプローチしてる層の問題？」
11/17 の Meta の配置別・年齢性別ごとの カート（Meta ATC）÷着地 を 11/10〜16 と比べ、
①配信先の構成が変わった分（今日の着地の内訳 × 7日の率）と ②同じ層の中で下がった分 に分ける。Shopify の端末別も並べる。入力: o1117/audience_1117_raw.txt"""
import collections, math
D = __file__.rsplit('/', 1)[0] + '/'
X = collections.defaultdict(dict)
for l in open(D + 'audience_1117_raw.txt'):
    if l[0] == '#': continue
    p = l.strip().split(','); X[(p[0], p[1])][p[2]] = [int(x) for x in p[3:]]
for dim, lab in (('place', '配置'), ('age', '年齢・性別')):
    a7, a17 = X[('P7', dim)], X[('P17', dim)]
    c7 = sum(v[0] for v in a7.values()); c17 = sum(v[0] for v in a17.values())
    L7 = sum(v[3] for v in a7.values()); T7 = sum(v[4] for v in a7.values()); P7 = sum(v[5] for v in a7.values())
    L17 = sum(v[3] for v in a17.values()); T17 = sum(v[4] for v in a17.values()); P17 = sum(v[5] for v in a17.values())
    exp = sum(a17[k][3] * a7[k][4] / a7[k][3] for k in a17 if a7.get(k, [0] * 6)[3])
    expp = sum(a17[k][3] * a7[k][5] / a7[k][3] for k in a17 if a7.get(k, [0] * 6)[3])
    print(f'■ {lab}（Meta）: カート÷着地 7日 {T7/L7*100:.1f}% → 11/17 {T17/L17*100:.1f}%（{T17/L17/(T7/L7)-1:+.0%}）')
    print(f'  ①構成が変わった分: 11/17 の着地の内訳に7日の率を当てると {exp/L17*100:.1f}%（7日比 {exp/L17/(T7/L7)-1:+.0%}）')
    print(f'  ②同じ層の中で下がった分: 実際 {T17} ／ ①の期待 {exp:.1f}（{T17/exp-1:+.0%}）。購入（Meta）も 実際 {P17} ／ 期待 {expp:.1f}（{P17/expp-1:+.0%}）')
    for k in sorted(a17, key=lambda k: -a17[k][0]):
        v7, v = a7[k], a17[k]
        if v[0] < 3000: continue
        print(f"   {k}: 広告費の割合 {v7[0]/c7*100:.0f}%→{v[0]/c17*100:.0f}%・カート÷着地 {v7[4]/v7[3]*100:.1f}%→{v[4]/v[3]*100:.1f}%（着地{v[3]}・カート{v[4]}）")
b, t = X[('B', 'device')], X[('T', 'device')]
print('■ 端末（Shopify・11/3〜16 → 11/17）')
for k in t:
    print(f"  {k}: 来訪の割合 {b[k][0]/sum(v[0] for v in b.values())*100:.0f}%→{t[k][0]/sum(v[0] for v in t.values())*100:.0f}%・カート÷来訪 {b[k][1]/b[k][0]*100:.2f}%→{t[k][1]/t[k][0]*100:.2f}%")
