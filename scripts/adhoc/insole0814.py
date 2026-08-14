# -*- coding: utf-8 -*-
"""快適マジックインソール: 3,980円 → 2,980円 への値下げを実測から評価する。
Shopify: 商品別day実測（8/11配信開始〜8/14 09:50 JST途中）
Meta   : キャンペーン別day実測
"""
COST = 677
P0, P1 = 3980, 2980
BUDGET = 12000  # campaign_and_resource_get 直読（adset 52554797282612, 2026-08-14）
SH = {'2026-08-11':(7960,796,2,1),'2026-08-12':(43780,1592,11,9),
      '2026-08-13':(35820,2388,9,6),'2026-08-14':(11940,0,3,3)}   # (gross, disc, items, orders)
MT = {'2026-08-11':(2779,1203,43),'2026-08-12':(10153,3851,113),
      '2026-08-13':(12695,6210,196),'2026-08-14':(7819,3871,131)}  # (cost, imp, clicks)
def zone(p):
    r = COST/p
    return r, 1/(1-r), 1/(0.70-r), 1/(1-r-0.35)     # 原価率, 分岐MER, 必要MER(30%), 目標MER(35%)
for p in (P0,P1):
    r,b,n30,t35 = zone(p)
    print(f'売価{p:,}円  原価{COST}円  原価率 {r:>5.1%}  粗利/個 {p-COST:>5,}円  '
          f'分岐MER {b:.3f}  必要MER(30%) {n30:.3f}  目標MER(35%) {t35:.3f}')
print()
print('=== 今の実測（8/11配信開始〜8/14 09:50時点） ===')
hdr=f"{'日付':<12}{'広告費':>8}{'消化%':>7}{'imp':>7}{'CPM':>7}{'click':>6}{'CTR':>7}{'注文':>5}{'CVR':>7}{'個':>4}{'実売':>8}{'MER':>6}{'CPA':>7}{'利益':>8}"
print(hdr)
for d in sorted(SH):
    g,dc,it,od = SH[d]; c,imp,clk = MT[d]
    q=g//P0; assert g%P0==0,(d,g)
    net=g-dc; prof=net-q*COST-c
    print(f"{d:<12}{c:>8,}{c/BUDGET*100:>6.0f}%{imp:>7,}{c/imp*1000:>7,.0f}{clk:>6}{clk/imp:>7.2%}"
          f"{od:>5}{od/clk:>7.2%}{q:>4}{net:>8,}{net/c:>6.2f}{c/od:>7,.0f}{prof:>+8,}")
G=sum(v[0] for v in SH.values()); DC=sum(v[1] for v in SH.values())
Q=G//P0; OD=sum(v[3] for v in SH.values()); IT=sum(v[2] for v in SH.values())
C=sum(v[0] for v in MT.values()); IMP=sum(v[1] for v in MT.values()); CLK=sum(v[2] for v in MT.values())
NET=G-DC; PROF=NET-Q*COST-C; IPO=Q/OD; DR=DC/G
print(f"\n合計  広告{C:,}  実売{NET:,}  {Q}個 / {OD}注文  点数/注文 {IPO:.2f}  値引率 {DR:.2%}")
print(f"      MER {NET/C:.2f}（分岐{zone(P0)[1]:.2f} / 必要{zone(P0)[2]:.2f} / 目標{zone(P0)[3]:.2f}）")
print(f"      CPM {C/IMP*1000:,.0f}円  CTR {CLK/IMP:.2%}  CVR {OD/CLK:.2%}  CPA {C/OD:,.0f}円")
print(f"      分岐CPA = 粗利/注文 = {(P0-COST):,}×{IPO:.2f} = {(P0-COST)*IPO:,.0f}円  → 余裕 {(P0-COST)*IPO-C/OD:+,.0f}円/注文")
print(f"      利益 {PROF:+,}円  利益率 {PROF/NET:.1%}")
print()
print('=== 2,980円にしたら（広告費・数量そのままの場合） ===')
g1=Q*P1; dc1=g1*DR; net1=g1-dc1; prof1=net1-Q*COST-C
print(f"  実売 {net1:,.0f}円  利益 {prof1:+,.0f}円  利益率 {prof1/net1:.1%}  MER {net1/C:.2f}")
print(f"  → 今より {prof1-PROF:+,.0f}円 / {len(SH)}日 ＝ {(prof1-PROF)/len(SH):+,.0f}円/日 ＝ 週 {(prof1-PROF)/len(SH)*7:+,.0f}円")
need = (PROF + C) / (P1*(1-DR) - COST)   # q*(実売単価-原価) = 利益 + 広告費
print(f"\n  今の利益に並ぶのに必要な販売数 = {need:.1f}個（今 {Q}個）→ **+{need/Q-1:.1%}** の数量増が必要")
print(f"  分岐CPA は {(P0-COST)*IPO:,.0f}円 → {(P1-COST)*IPO:,.0f}円（{((P1-COST)/(P0-COST)-1):+.1%}）")
print()
print('=== 実測の価格弾力性（店内の価格帯別CVR。2026-08-12に全商品から算出） ===')
E=[(3980,0.0406),(4980,0.0381),(6480,0.0270),(8980,0.0053)]
for p,c in E: print(f'  {p:,}円 → CVR {c:.2%}')
import math
(p_a,c_a),(p_b,c_b)=E[0],E[1]
el=(math.log(c_b)-math.log(c_a))/(math.log(p_b)-math.log(p_a))
print(f"  3,980⇄4,980区間の弾力性 = {el:+.2f}（価格1%でCVR{el:.2f}%）")
lift=(P1/P0)**el-1
print(f"  → 2,980円へ {P1/P0-1:.1%} 下げたときのCVR上昇の見込み = {lift:+.1%}")
print(f"  必要な +{need/Q-1:.1%} に対し、見込みは +{lift:.1%} ＝ {(need/Q-1)/lift:.1f}倍 足りない")
