#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-06 「広告効率の悪化は夏／需要減退か」の決定的検定
売上・個数・注文=Shopify実測 / 広告費=Meta実測（daily CSV）"""
import csv, collections
from datetime import date, timedelta
B='data/daily/'
SEASON={'4WAY','卓上冷感クーラー','5WAY腰掛けファン','瞬間冷却ハンディファン','3WAYサーキュレーター',
'接触冷感UVパーカー','接触冷感UVアームカバー','瞬間冷感ポンチョ','完全遮光・接触冷感UVハット',
'形状記憶日傘','完全遮光・形状記憶','偏光・調光サングラス','害虫ブロッカー'}
MAP={'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
'3WAYサーキュレーター':'3WAYサーキュレーター扇風機','壁掛けディスペンサー':'ディスペンサー'}
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open(B+'daily_sales.csv',encoding='utf-8')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B+'daily_ad.csv',encoding='utf-8')):
    AD[r['campaign']][r['date']]+=float(r['cost'])
def days(s): d0=date.fromisoformat(s); return [(d0+timedelta(i)).isoformat() for i in range(7)]
W=[('6/29-7/05','2026-06-29'),('7/06-7/12','2026-07-06'),('7/13-7/19','2026-07-13'),
   ('7/20-7/26','2026-07-20'),('7/27-8/02','2026-07-27'),('7/30-8/05','2026-07-30')]
def seg(ds,which):
    s=a=0
    for n,v in S.items():
        if n=='' : continue
        inseg = (n in SEASON) if which=='季節' else (n not in SEASON)
        if not inseg: continue
        s+=sum(v[d][0]-v[d][1] for d in ds if d in v); a+=sum(AD[MAP.get(n,n)].get(d,0) for d in ds)
    return s,a
print('='*106)
print('検定A 同じ予算水準の週どうしで比べる（予算過多の影響を消す）')
print('='*106)
print(f"{'週':12}{'全店売上':>12}{'全店広告費':>12}{'MER':>7}{'前週比':>9}")
prev=None
for lab,st in W[:-1]:
    ds=days(st); s=sum(sum(v[d][0]-v[d][1] for d in ds if d in v) for v in S.values())
    a=sum(sum(AD[c].get(d,0) for c in AD) for d in ds)
    print(f'{lab:12}{s:12,}{a:12,.0f}{s/a:7.3f}{(f"{s/a/prev-1:+.1%}" if prev else "—"):>9}')
    prev=s/a
ds=days('2026-07-30'); s2=sum(sum(v[d][0]-v[d][1] for d in ds if d in v) for v in S.values())
a2=sum(sum(AD[c].get(d,0) for c in AD) for d in ds)
ds1=days('2026-07-06'); s1=sum(sum(v[d][0]-v[d][1] for d in ds1 if d in v) for v in S.values())
a1=sum(sum(AD[c].get(d,0) for c in AD) for d in ds1)
print(f'{"7/30-8/05":12}{s2:12,}{a2:12,.0f}{s2/a2:7.3f}')
print()
print(f'  ★ 広告費がほぼ同じ2週を直接比較:')
print(f'     7/06-7/12  広告費 {a1:,.0f}円  MER {s1/a1:.3f}')
print(f'     7/30-8/05  広告費 {a2:,.0f}円  MER {s2/a2:.3f}   （広告費 {a2/a1-1:+.1%} なのに MER {s2/a2/(s1/a1)-1:+.1%}）')
print(f'  → 同じ金額を使って、4週間で売上が {s2/s1-1:+.1%}。**予算過多では説明できない純粋な効率低下。**')

print()
print('='*106)
print('検定B その効率低下は「夏物」か「通年」か（同じ2週で分けて見る）')
print('='*106)
print(f"{'週':12}{'季節 売上':>12}{'季節 広告':>11}{'季節MER':>8}{'通年 売上':>12}{'通年 広告':>11}{'通年MER':>8}")
rows=[]
for lab,st in [('7/06-7/12','2026-07-06'),('7/13-7/19','2026-07-13'),('7/20-7/26','2026-07-20'),
               ('7/27-8/02','2026-07-27'),('7/30-8/05','2026-07-30')]:
    ds=days(st); ss,sa=seg(ds,'季節'); ys,ya=seg(ds,'通年')
    print(f'{lab:12}{ss:12,}{sa:11,.0f}{ss/sa:8.3f}{ys:12,}{ya:11,.0f}{ys/ya:8.3f}')
    rows.append((lab,ss,sa,ys,ya))
a,b=rows[0],rows[-1]
print()
print(f'  季節商品 MER {a[1]/a[2]:.3f} → {b[1]/b[2]:.3f}  ({(b[1]/b[2])/(a[1]/a[2])-1:+.1%})')
print(f'  通年商品 MER {a[3]/a[4]:.3f} → {b[3]/b[4]:.3f}  ({(b[3]/b[4])/(a[3]/a[4])-1:+.1%})')
print()
print('='*106)
print('検定C ブランド需要そのものは縮んでいるか（広告に依存しない指標・Shopify実測）')
print('='*106)
BR=[('6/29週',9561,918,1555,43,5711.84),('7/06週',8397,841,1416,48,5658.94),
    ('7/13週',9370,811,1487,64,5858.55),('7/20週',12942,946,1781,86,5788.99),
    ('7/27週',13900,816,1564,72,5581.45)]
print(f"{'週':10}{'direct':>9}{'search':>8}{'顧客数':>8}{'リピーター':>9}{'リピート率':>10}{'客単価':>9}")
for l,d_,se,c,r,aov in BR:
    print(f'{l:10}{d_:9,}{se:8,}{c:8,}{r:9,}{r/c*100:9.2f}%{aov:9,.0f}')
print()
print(f'  direct流入 9,561 → 13,900（{13900/9561-1:+.1%}）／ リピート率 2.77% → 4.60%（+66%）')
print('  → 需要が本当に縮んでいるなら、広告に依存しないdirect流入とリピートが最初に落ちる。増えている。')

print()
print('='*106)
print('検定D 予算をそろえた比較（季節商品・7/20週 vs 7/27週は広告費がほぼ同じ）')
print('='*106)
d20=days('2026-07-20'); d27=days('2026-07-27')
s20,a20=seg(d20,'季節'); s27,a27=seg(d27,'季節')
y20,ay20=seg(d20,'通年'); y27,ay27=seg(d27,'通年')
print(f'  季節: 7/20週 広告{a20:,.0f} MER {s20/a20:.3f} → 7/27週 広告{a27:,.0f}（{a27/a20-1:+.1%}）MER {s27/a27:.3f}（{(s27/a27)/(s20/a20)-1:+.1%}）')
print(f'  通年: 7/20週 広告{ay20:,.0f} MER {y20/ay20:.3f} → 7/27週 広告{ay27:,.0f}（{ay27/ay20-1:+.1%}）MER {y27/ay27:.3f}（{(y27/ay27)/(y20/ay20)-1:+.1%}）')
print('  → 広告費をほぼ動かしていない週どうしで、季節だけが −21%。予算の影響ではない。')

print()
print('='*106)
print('検定E 季節商品を1つずつ — どれが、いつから落ちたか（週次MER・Shopify実測）')
print('='*106)
WW=[('7/06','2026-07-06'),('7/13','2026-07-13'),('7/20','2026-07-20'),('7/27','2026-07-27'),('7/30','2026-07-30')]
print(f"{'商品':<22}"+''.join(f'{l:>8}' for l,_ in WW)+f"{'7/13→直近':>11}{'残週':>6}")
SEASONW={'4WAY':4,'卓上冷感クーラー':4,'5WAY腰掛けファン':4,'3WAYサーキュレーター':4,
'接触冷感UVパーカー':5,'接触冷感UVアームカバー':5,'瞬間冷感ポンチョ':5,'完全遮光・接触冷感UVハット':5,
'形状記憶日傘':6,'完全遮光・形状記憶':6,'偏光・調光サングラス':6,'害虫ブロッカー':8}
res=[]
for n in SEASONW:
    ms=[]
    for l,st in WW:
        ds=days(st); s=sum(S[n][d][0]-S[n][d][1] for d in ds if d in S[n]); a=sum(AD[MAP.get(n,n)].get(d,0) for d in ds)
        ms.append(s/a if a>1000 else None)
    base=ms[1] if ms[1] else ms[0]
    chg=(ms[-1]/base-1) if (ms[-1] and base) else None
    res.append((n,ms,chg))
for n,ms,chg in sorted(res,key=lambda x:(x[2] if x[2] is not None else 9)):
    print(f'{n:<22}'+''.join(f'{(m if m else 0):8.2f}' for m in ms)+f'{(f"{chg:+.1%}" if chg is not None else "—"):>11}{SEASONW[n]:>6}')
print()
print('  通年商品（対照群）')
for n in ['ナノガラス脱毛パッド','ムダ毛シェーバー','W固定スマホ車載ホルダー','携帯電動シェーバー']:
    ms=[]
    for l,st in WW:
        ds=days(st); s=sum(S[n][d][0]-S[n][d][1] for d in ds if d in S[n]); a=sum(AD[MAP.get(n,n)].get(d,0) for d in ds)
        ms.append(s/a if a>1000 else None)
    base=ms[1] if ms[1] else ms[0]
    chg=(ms[-1]/base-1) if (ms[-1] and base) else None
    print(f'  {n:<20}'+''.join(f'{(m if m else 0):8.2f}' for m in ms)+f'{(f"{chg:+.1%}" if chg is not None else "—"):>11}')
