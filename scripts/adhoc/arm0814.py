# -*- coding: utf-8 -*-
"""接触冷感UVアームカバー: 窓集計ではなく「今時点」＝日次の生の並びで見る。
Shopify: 商品別 day 実測（gross/discounts/net_items_sold/orders）
Meta   : 広告(ad)別 day 実測（cost/impressions/outbound_clicks/frequency/reach）
CVR = Shopify注文 ÷ Metaアウトバウンドクリック（SKILL既定）
"""
PRICE, COST = 3980, 784
# --- Shopify 実測（ShopifyQL day別・2026-08-14 09:38 JST 取得。discountsは絶対値に直す）
SH = {  # date: (gross, disc, items, orders)
'2026-07-31':(15920,0,4,4),
'2026-08-01':(15920,0,4,4),'2026-08-02':(31840,0,8,8),'2026-08-03':(27860,796,7,6),
'2026-08-04':(19900,0,5,5),'2026-08-05':(7960,796,2,1),'2026-08-06':(27860,1791,7,5),
'2026-08-07':(3980,0,1,1),'2026-08-08':(11940,0,3,3),'2026-08-09':(27860,0,7,7),
'2026-08-10':(19900,796,5,4),'2026-08-11':(7960,0,2,2),'2026-08-12':(11940,796,3,2),
'2026-08-13':(11940,0,3,3),'2026-08-14':(7960,796,2,1)}
# --- Meta 実測（ad別。8/14は09:38時点の途中経過）
MT = {  # date: {ad: (cost, imp, clicks, freq, reach)}
'2026-08-01':{'A':(1806,804,20,1.0551,762),'B':(18558,5896,163,1.0947,5386)},
'2026-08-02':{'A':(5690,2607,65,1.0777,2419),'B':(12819,3563,123,1.1329,3145)},
'2026-08-03':{'A':(4081,1471,34,1.0690,1376),'B':(10770,2725,81,1.1228,2427)},
'2026-08-04':{'A':(6043,2447,32,1.1062,2212),'B':(9372,2186,67,1.1397,1918)},
'2026-08-05':{'A':(4684,1627,21,1.0732,1516),'B':(11356,2773,89,1.1181,2480)},
'2026-08-06':{'A':(1503,521,13,1.0337,504),'B':(12431,3145,91,1.0808,2910)},
'2026-08-07':{'A':(665,388,7,1.0292,377),'B':(7482,1752,51,1.1557,1516)},
'2026-08-08':{'A':(573,219,8,1.0379,211),'B':(6603,1471,48,1.1421,1288)},
'2026-08-09':{'A':(1283,426,8,1.0095,422),'B':(8052,1873,55,1.1428,1639)},
'2026-08-10':{'A':(1136,435,9,1.0985,396),'B':(6202,1335,39,1.1680,1143)},
'2026-08-11':{'A':(794,316,7,1.0429,303),'B':(8252,1799,53,1.1705,1537)},
'2026-08-12':{'A':(691,249,4,1.1067,225),'B':(6267,1442,47,1.1292,1277)},
'2026-08-13':{'A':(382,106,0,1.0291,103),'B':(7226,1675,65,1.1879,1410)},
'2026-08-14':{'A':(72,45,2,1.1250,40),'B':(2307,439,17,1.0975,400)}}
BUDGET = 8000   # campaign_and_resource_get 直読（2026-08-14, adset 52530576110212）
BREAK  = 1/(1-COST/PRICE)          # 分岐MER
TGT35  = 1/(1-COST/PRICE-0.35)     # 目標MER(利益率35%)
NEED30 = 1/(0.70-COST/PRICE)       # 必要MER(利益率30%)
import datetime
WD='月火水木金土日'
print(f'原価率 {COST/PRICE:.1%}  分岐MER {BREAK:.2f}  必要MER(30%) {NEED30:.2f}  目標MER(35%) {TGT35:.2f}  日予算 {BUDGET:,}円')
print()
hdr=f"{'日付':<12}{'曜':<3}{'広告費':>8}{'消化%':>7}{'imp':>7}{'CPM':>7}{'click':>6}{'CTR':>7}{'注文':>5}{'CVR':>7}{'個':>4}{'実売':>8}{'MER':>6}{'利益':>8}{'頻度':>6}"
print(hdr); print('-'*len(hdr)*1)
rows=[]
for d in sorted(MT):
    g,dc,it,od = SH.get(d,(0,0,0,0))
    cost=sum(v[0] for v in MT[d].values()); imp=sum(v[1] for v in MT[d].values())
    clk=sum(v[2] for v in MT[d].values()); rch=sum(v[4] for v in MT[d].values())
    q=g//PRICE; assert g%PRICE==0,(d,g)
    net=g-dc; prof=net-q*COST-cost
    mer=net/cost if cost else 0
    cpm=cost/imp*1000 if imp else 0; ctr=clk/imp if imp else 0
    cvr=od/clk if clk else 0
    wd=WD[datetime.date(*map(int,d.split('-'))).weekday()]
    rows.append((d,cost,net,q,od,prof,mer,clk,imp))
    print(f"{d:<12}{wd:<3}{cost:>8,}{cost/BUDGET*100:>6.0f}%{imp:>7,}{cpm:>7,.0f}{clk:>6}{ctr:>7.2%}{od:>5}{cvr:>7.1%}{q:>4}{net:>8,}{mer:>6.2f}{prof:>8,}{max(v[3] for v in MT[d].values()):>6.2f}")
print()
def blk(lbl, ds):
    c=sum(r[1] for r in rows if r[0] in ds); n=sum(r[2] for r in rows if r[0] in ds)
    q=sum(r[3] for r in rows if r[0] in ds); o=sum(r[4] for r in rows if r[0] in ds)
    p=sum(r[5] for r in rows if r[0] in ds); ck=sum(r[7] for r in rows if r[0] in ds)
    print(f"{lbl}: 広告{c:>7,}  実売{n:>7,}  MER {n/c:.2f}  個{q:>3}  注文{o:>3}  CVR {o/ck:.2%}  利益{p:>+8,}  利益率 {p/n:>6.1%}  1日あたり広告{c/len(ds):>6,.0f}")
hi=[f'2026-08-{i:02d}' for i in range(1,7)]      # 予算がまだ大きかった時期
lo=[f'2026-08-{i:02d}' for i in range(7,14)]     # 8,000円/日に絞ってからの完全日
blk('予算〜2万円期 8/01-06',hi)
blk('予算8千円期 8/07-13',lo)
print()
# 広告(CR)別の配信シェア: 直近7日
print('広告別の消化シェア（直近の完全日 8/07-13）')
tot=sum(MT[d][a][0] for d in lo for a in MT[d])
for a in ['A','B']:
    c=sum(MT[d][a][0] for d in lo); i=sum(MT[d][a][1] for d in lo); k=sum(MT[d][a][2] for d in lo)
    print(f"  {a}: {c:>7,}円 ({c/tot:>5.1%})  imp{i:>7,}  CPM {c/i*1000:>6,.0f}  CTR {k/i:>6.2%}")
print()
print('本日 8/14 09:38時点 vs 直近7日の同日平均（1日フル）')
d='2026-08-14'; g,dc,it,od=SH[d]; c=sum(v[0] for v in MT[d].values())
print(f"  実売 {g-dc:,}円 / 注文 {od} / 個 {g//PRICE} / 広告 {c:,}円 / 利益 {(g-dc)-(g//PRICE)*COST-c:+,}円 / MER {(g-dc)/c:.2f}")
