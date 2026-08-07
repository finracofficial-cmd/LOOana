# -*- coding: utf-8 -*-
"""バランスケアスリッパ: 新素材D投入時点のベースライン。Meta配信指標＋Shopify実売(CSV)。"""
import csv, collections
# 【転記】Meta ad別 7/31-8/07（trace cc84f6e8...）
M=[('2026-07-31','A',4884,2238,42),('2026-07-31','B',3,3,0),
('2026-08-01','A',4693,2853,40),('2026-08-01','C',74,24,0),
('2026-08-02','A',5667,3576,65),('2026-08-02','B',16,8,0),
('2026-08-03','A',4357,2472,46),('2026-08-03','B',95,30,1),('2026-08-03','C',2,3,0),
('2026-08-04','A',4667,2330,52),('2026-08-05','A',4440,2236,37),
('2026-08-06','A',5756,3363,65),('2026-08-07','A',2468,1347,22)]
S=collections.defaultdict(lambda:[0,0])
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    if r['name']=='バランスケアスリッパ': S[r['date']][0]+=int(r['gross']); S[r['date']][1]+=int(r['disc'])
W=[m for m in M if '2026-07-31'<=m[0]<='2026-08-06']
by=collections.defaultdict(lambda:[0,0,0])
for d,n,c,i,cl in W: by[n][0]+=c; by[n][1]+=i; by[n][2]+=cl
tot=sum(v[0] for v in by.values())
print('=== 7日(7/31-8/06) 広告別 配信シェア ===')
for n,(c,i,cl) in sorted(by.items(), key=lambda x:-x[1][0]):
    print(f"  広告{n}: 消化 {c:>7,}円 ({c/tot*100:>5.1f}%)  インプ {i:>7,}  クリック {cl:>4}  外部CTR {(cl/i*100 if i else 0):>5.2f}%")
print(f"  → **MetaはAに{by['A'][0]/tot*100:.1f}%を寄せている。B・Cは7日合計{tot-by['A'][0]:,}円で事実上停止状態**")
g=sum(S[d][0] for d in S if '2026-07-31'<=d<='2026-08-06'); dc=sum(S[d][1] for d in S if '2026-07-31'<=d<='2026-08-06')
s=g-dc; q=round(g/4980); cost=q*1304; cl=sum(v[2] for v in by.values())
print()
print('=== 7日の経済性（Shopify実売 × Metaクリック） ===')
print(f"  実売 {s:,}円 / 販売数 {q} / 広告 {tot:,}円 / クリック {cl}")
print(f"  外部CTR {cl/sum(v[1] for v in by.values())*100:.2f}%   CPC {tot/cl:,.0f}円")
gm=1-cost/s
print(f"  売上/クリック {s/cl:,.0f}円   粗利/クリック {s/cl*gm:,.0f}円  vs CPC {tot/cl:,.0f}円 → 1クリックあたり利益 {s/cl*gm-tot/cl:+,.0f}円")
print(f"  MER {s/tot:.2f}  分岐 {1/gm:.2f}  余裕 {s/tot-1/gm:+.2f}  7日利益 {s-cost-tot:+,.0f}円")
print()
print('=== Dが効いた場合の感度（売上/クリックが現状維持の前提） ===')
for t in [2.00,2.20,2.50]:
    ncl=sum(v[1] for v in by.values())*t/100
    ns=s/cl*ncl
    print(f"  外部CTR {cl/sum(v[1] for v in by.values())*100:.2f}% → {t:.2f}%: クリック {cl}→{ncl:.0f}  実売 {s:,}→{ns:,.0f}  7日利益 {ns*gm-tot:+,.0f}円 ({ns*gm-tot-(s-cost-tot):+,.0f})")
