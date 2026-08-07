# -*- coding: utf-8 -*-
"""害虫ブロッカー: 今削るべきか。CSV実測から日次・窓別に積み直す。"""
import csv, collections, datetime
B='data/daily/'
S=collections.defaultdict(lambda:[0,0]); AD=collections.defaultdict(float)
for r in csv.DictReader(open(B+'daily_sales.csv')):
    if r['name']=='害虫ブロッカー': S[r['date']][0]+=int(r['gross']); S[r['date']][1]+=int(r['disc'])
for r in csv.DictReader(open(B+'daily_ad.csv')):
    if r['campaign']=='害虫ブロッカー': AD[r['date']]+=float(r['cost'])
PRICE,COST=3980,867
WD=['月','火','水','木','金','土','日']
days=sorted(S)
print(f"{'日付':12}{'曜':>3}{'実売':>10}{'個':>5}{'広告':>9}{'利益':>9}{'MER':>6}{'1円利益':>8}")
for d in days[-10:]:
    g,dc=S[d]; q=round(g/PRICE); s=g-dc; c=q*COST; a=AD[d]; p=s-c-a
    gm=1-c/s; mer=s/a
    print(f"{d:12}{WD[datetime.date(*map(int,d.split('-'))).weekday()]:>3}{s:>10,}{q:>5}{a:>9,.0f}{p:>9,.0f}{mer:>6.2f}{mer*gm-1:>+8.3f}")
def win(ds):
    g=sum(S[d][0] for d in ds); dc=sum(S[d][1] for d in ds); q=round(g/PRICE)
    s=g-dc; c=q*COST; a=sum(AD[d] for d in ds); gm=1-c/s
    return s,c,a,s-c-a,s/a,1/gm,gm
print()
print(f"{'窓':10}{'実売':>10}{'広告':>10}{'利益':>10}{'MER':>6}{'分岐':>6}{'余裕':>7}{'1円利益':>8}")
for lbl,ds in [('前日',days[-1:]),('3日',days[-3:]),('7日',days[-7:]),('前週7日',days[-14:-7])]:
    s,c,a,p,mer,be,gm=win(ds)
    print(f"{lbl:10}{s:>10,}{a:>10,.0f}{p:>10,.0f}{mer:>6.2f}{be:>6.2f}{mer-be:>+7.2f}{mer*gm-1:>+8.3f}")
print()
s,c,a,p,mer,be,gm=win(days[-7:])
print('=== 削減1円あたりの利益変化 = 1 − 限界MER × 粗利率 ===')
print(f"  粗利率 {gm:.4f}  平均MER {mer:.3f}  分岐 {be:.3f}")
for lbl,mm in [('実測 限界MER 下限 1.90（8/1減額のP1/P2）',1.90),('実測 限界MER 上限 2.04',2.04),('概算 平均×0.7',mer*0.7),('概算 平均×0.6',mer*0.6)]:
    print(f"  {lbl:38} → {1-mm*gm:+.3f}円 / 1円削減   ({'削ると利益減' if 1-mm*gm<0 else '削ると利益増'})")
print()
for cut in [7500,10000,15000]:
    print(f"  本体を−{cut:,}円/日した場合（限界MER1.90想定）: 利益 {(1-1.90*gm)*cut:+,.0f}円/日 = {(1-1.90*gm)*cut*7:+,.0f}円/週")
