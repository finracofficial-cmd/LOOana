# ムダ毛シェーバー・バランスケアスリッパの週別（CPM・店比・クリック率・1クリック・購入/クリック）と、
# スリッパの最近の再開（10/26〜27・11/12）が過去の効率から見て偶然の範囲か（Meta 購入数・ポアソン）
# 入力: scripts/daily/ic1118/life/meta_weekly_raw.txt（data_query 11/18 取得の生データ）
import math
from collections import defaultdict
RAW='scripts/daily/ic1118/life/meta_weekly_raw.txt'
rows=[l.strip().split(',') for l in open(RAW) if l.strip() and not l.startswith('#')]
num=lambda x: 0.0 if x=='null' else float(x)
tot=defaultdict(lambda:[0.0,0.0])
for w,c,cost,imp,*_ in rows: tot[w][0]+=num(cost); tot[w][1]+=num(imp)
def table(name):
    print(f'■ {name}（週＝月〜日）')
    out=[]
    for w,c,cost,imp,reach,freq,lc,lpv,atc,pur in rows:
        if c!=name: continue
        cost,imp,lc,atc,pur=map(num,(cost,imp,lc,atc,pur))
        s=tot[w][0]/tot[w][1]*1000; m=cost/imp*1000
        print(f'  {w} 広告費{cost:>8,.0f} CPM{m:>6,.0f}（店{s:>6,.0f}・{m/s:4.2f}倍） クリック率{lc/imp*100:5.2f}% 1クリック{cost/lc:>5,.0f}円 カート/クリック{atc/lc*100:5.1f}% 購入/クリック{pur/lc*100:4.1f}% 購入{pur:>3.0f}')
        out.append((w,cost,pur))
    return out
sh=table('ムダ毛シェーバー'); sl=table('バランスケアスリッパ'); table('ナノガラス脱毛パッド')
# スリッパ: 9/22〜10/19（週39〜42）の 1購入あたり広告費で、再開2回の広告費から期待される購入数
base=[(c,p) for w,c,p in sl if w in ('2026|39','2026|40','2026|41','2026|42')]
cpa=sum(c for c,_ in base)/sum(p for _,p in base)
re=[(c,p) for w,c,p in sl if w in ('2026|44','2026|46')]
cost=sum(c for c,_ in re); obs=sum(p for _,p in re); lam=cost/cpa
pl=sum(math.exp(-lam)*lam**k/math.factorial(k) for k in range(int(obs)+1))
print(f'\n■ スリッパ再開2回（10/26〜27・11/12）: 広告費 {cost:,.0f}・Meta 購入 {obs:.0f}')
print(f'  9/22〜10/19 の 1購入あたり {cpa:,.0f} 円なら期待 {lam:.1f} 件。{obs:.0f}件以下になる確率 {pl*100:.0f}%')
