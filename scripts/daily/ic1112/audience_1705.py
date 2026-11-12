# -*- coding: utf-8 -*-
"""11/12(木) 17:0x 「年齢層が低いユーザー向けの商品を出すのも大事？車用品はその種類だけでCPMが高くなりがち？」
夏（7月）と今（11/5〜11/11）で、広告費がどの性別・年齢に使われたかを比べる。入力: audience_1705_raw.json（Meta・7月はキャンペーン×年齢×性別で広告費2万円超の行だけ／今はキャンペーン×性別）・multi_1630_raw.json（今の年齢×性別）・q5_1745_raw.json（今のキャンペーン×年齢）。"""
import os, csv, json, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'; iv = lambda x: 0 if x in ('null', '') else int(x)
R1 = json.load(open(D + 'audience_1705_raw.json')); R2 = json.load(open(D + 'multi_1630_raw.json')); R3 = json.load(open(D + 'q5_1745_raw.json'))
J = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0, 0]))
for r in R1['july_camp_age_gender']['rows']:
    c, a, s, co, im, cl, pu = next(csv.reader([r]))
    for j, v in enumerate((co, im, cl, pu)): J[c][(s, a)][j] += iv(v)
tj = sum(v[0] for c in J.values() for v in c.values())
print(f"■ 7月（広告費2万円超の行の合計 {tj:,}円＝7月の広告費 15,244,458円の{tj/15244458*100:.0f}%）")
AG = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
def share(tbl, tot, lab):
    f = sum(v[0] for k, v in tbl.items() if k[0] == 'female'); m = sum(v[0] for k, v in tbl.items() if k[0] == 'male')
    print(f"  {lab}: 女性 {f/tot*100:.0f}%・男性 {m/tot*100:.0f}%｜年齢別（女性／男性の広告費の割合%）: " + ' '.join(f"{a} {tbl.get(('female', a), [0])[0]/tot*100:.0f}/{tbl.get(('male', a), [0])[0]/tot*100:.0f}" for a in AG))
allj = collections.defaultdict(lambda: [0, 0, 0, 0])
for c in J.values():
    for k, v in c.items():
        for j in range(4): allj[k][j] += v[j]
share(allj, tj, '7月・全体')
now = collections.defaultdict(lambda: [0, 0, 0, 0])
for key in ('age_gender_1105_1109', 'age_gender_1110_1111'):
    for r in R2[key]['rows']:
        a, s, co, im, cl, pu, pv = r.split(',')
        if s in ('male', 'female') and a != 'Unknown':
            for j, v in enumerate((co, im, cl, pu)): now[(s, a)][j] += iv(v)
tn = sum(v[0] for v in now.values()); share(now, tn, '今（11/5〜11/11）・全体')
print('  CPM（女性／男性）: 7月 ' + ' '.join(f"{a} {allj[('female',a)][0]/allj[('female',a)][1]*1000:,.0f}/{allj[('male',a)][0]/allj[('male',a)][1]*1000:,.0f}" for a in AG) + ' ｜ 今 ' + ' '.join(f"{a} {now[('female',a)][0]/now[('female',a)][1]*1000:,.0f}/{now[('male',a)][0]/now[('male',a)][1]*1000:,.0f}" for a in AG))
print('  購入1件の広告費（女性／男性）: 7月 ' + ' '.join(f"{a} {allj[('female',a)][0]/allj[('female',a)][3]:,.0f}/{allj[('male',a)][0]/max(allj[('male',a)][3],1):,.0f}" for a in AG) + ' ｜ 今 ' + ' '.join(f"{a} {now[('female',a)][0]/now[('female',a)][3]:,.0f}/{now[('male',a)][0]/now[('male',a)][3]:,.0f}" for a in AG))
print('\n■ 7月の広告費上位（広告費・女性の割合・45歳以上の割合・CPM・購入1件の広告費）')
for c in sorted(J, key=lambda c: -sum(v[0] for v in J[c].values()))[:8]:
    v = J[c]; s = sum(x[0] for x in v.values()); i = sum(x[1] for x in v.values()); p = sum(x[3] for x in v.values())
    print(f"  {c}: {s/10000:,.0f}万・女性 {sum(x[0] for k, x in v.items() if k[0]=='female')/s*100:.0f}%・45歳以上 {sum(x[0] for k, x in v.items() if k[1] in ('45-54','55-64','65+'))/s*100:.0f}%・CPM {s/i*1000:,.0f}・{s/p:,.0f}円")
print('\n■ 今（11/5〜11/11）の広告費上位（広告費・女性の割合・45歳以上の割合・CPM・購入1件の広告費）')
G = collections.defaultdict(dict)
for r in R1['camp_gender_1105_1111']['rows']:
    c, s, co, im, cl, pu = next(csv.reader([r])); G[c][s] = [iv(co), iv(im), iv(cl), iv(pu)]
CA = collections.defaultdict(dict)
for r in R3['camp_age_1105_1111']['rows']:
    c, a, co, im, cl, pu = next(csv.reader([r]))
    if a != 'Unknown': CA[c][a] = [iv(co), iv(im), iv(cl), iv(pu)]
for c in sorted(G, key=lambda c: -sum(v[0] for v in G[c].values()))[:12]:
    v = G[c]; s = sum(x[0] for x in v.values()); i = sum(x[1] for x in v.values()); p = sum(x[3] for x in v.values()); a45 = sum(CA[c].get(a, [0])[0] for a in ('45-54', '55-64', '65+')) / sum(x[0] for x in CA[c].values())
    print(f"  {c}: {s/10000:,.1f}万・女性 {v.get('female', [0])[0]/s*100:.0f}%・45歳以上 {a45*100:.0f}%・CPM {s/i*1000:,.0f}・{s/max(p,1):,.0f}円")
tg = {s: sum(v.get(s, [0])[0] for v in G.values()) for s in ('female', 'male')}
print(f"  男性45歳以上に使った割合: 7月 {sum(allj[('male',a)][0] for a in ('45-54','55-64','65+'))/tj*100:.0f}% → 今 {sum(now[('male',a)][0] for a in ('45-54','55-64','65+'))/tn*100:.0f}%／女性25〜64歳: 7月 {sum(allj[('female',a)][0] for a in ('25-34','35-44','45-54','55-64'))/tj*100:.0f}% → 今 {sum(now[('female',a)][0] for a in ('25-34','35-44','45-54','55-64'))/tn*100:.0f}%")
