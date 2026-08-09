# -*- coding: utf-8 -*-
"""どれを動かすと一番効くか。7日8/03-09実測。限界MER=平均×0.7（実測レンジ0.6-0.8の中央）"""
import pickle, csv
R=pickle.load(open('/tmp/rep0810.pkl','rb'))
BUD={}
for r in csv.DictReader(open('data/budget-snapshots.csv')):
    if r['snapshot_date']=='2026-08-09': BUD[r['campaign']]=BUD.get(r['campaign'],0)+int(r['daily_budget'])
rows=[]
for n in R['N7']:
    a=R['A7'].get(n,0)
    if a<10000: continue
    s=R['N7'][n]; k=R['K7'][n]; gm=1-k/s; mer=s/a; be=1/gm; p=s-k-a
    mm=mer*0.7
    cut25=(1-mm*gm)*a*0.25          # −25%で増える利益（週）
    stop=-p                          # 全停止で増える利益（週）＝現在の利益を失う
    b=BUD.get(R['MAP'].get(n,n)) or BUD.get(n)
    rows.append((n,b,a,p,mer,be,mer-be,cut25,stop))
print('=== 動かしたときの週次利益の変化（プラス＝改善） ===')
print(f"{'商品':22}{'日予算':>8}{'7日広告':>9}{'7日利益':>10}{'MER':>6}{'余裕':>7}{'−25%で':>9}{'全停止で':>10}")
for r in sorted(rows,key=lambda x:-x[7]):
    print(f"{r[0][:22]:22}{(f'{r[1]:,}' if r[1] else '—'):>8}{r[2]:>9,.0f}{r[3]:>10,.0f}{r[4]:>6.2f}{r[6]:>+7.2f}{r[7]:>+9,.0f}{r[8]:>+10,.0f}")
print()
print('=== 増額したときの週次利益の変化（+25%・限界MER=平均×0.7） ===')
up=[]
for n,b,a,p,mer,be,yo,c25,st in rows:
    s=R['N7'][n]; k=R['K7'][n]; gm=1-k/s
    up.append((n,(mer*0.7*gm-1)*a*0.25,yo))
for n,v,yo in sorted(up,key=lambda x:-x[1])[:6]:
    print(f"  {n[:24]:24} 余裕{yo:+.2f}  +25%で {v:>+9,.0f}円/週")
