# -*- coding: utf-8 -*-
"""2026-08-31 の事後分析。「あまりに悪すぎた」のか、どこが悪かったのかを実測で確定させる。"""
import csv, collections, datetime, statistics, math
COST={'ナノガラス脱毛パッド':None,'W固定スマホ車載ホルダー':1069,'快適マジックインソール':677,'ムダ毛シェーバー':2798,
'ナノバブルシャワーヘッド':2255,'バランスケアスリッパ':1304,'むくみ取りかっさ':1120,'姿勢サポートチェア':1811,
'完全遮光・接触冷感UVハット':1411,'2WAYシートボックス':1943,'偏光・調光サングラス':893,'ビジュアル耳かき':1655,
'3D足臭リセットブラシ':609,'携帯電動シェーバー':1743,'4WAY':1730,'形状記憶日傘':1309,'優先配送':0,'1秒折り畳みチェア':1584,
'高吸水・速乾ヘアドライタオル':985,'湯上がりガーゼワンピース':1968,'壁掛けディスペンサー':None,'接触冷感UVパーカー':1434,
'ジェットウォッシャー':1259,'瞬間冷感ポンチョ':987,'接触冷感UVアームカバー':784,'完全遮光・形状記憶':1309}
PRICE={'ナノガラス脱毛パッド':3980,'W固定スマホ車載ホルダー':3980,'快適マジックインソール':3980,'ムダ毛シェーバー':6980,
'ナノバブルシャワーヘッド':6980,'バランスケアスリッパ':4980,'むくみ取りかっさ':3980,'姿勢サポートチェア':5980,
'完全遮光・接触冷感UVハット':4980,'2WAYシートボックス':4980,'偏光・調光サングラス':3980,'ビジュアル耳かき':4980}
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open('data/daily/daily_sales.csv',encoding='utf-8')):
    S[r['date']][r['name']][0]+=int(r['gross']); S[r['date']][r['name']][1]+=int(r['disc'])
VG=collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
for r in csv.DictReader(open('data/daily/daily_variant.csv',encoding='utf-8')):
    VG[r['name']][r['date']][r['cost_group']]+=int(r['gross'])
AD=collections.defaultdict(float); ADC=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_ad.csv',encoding='utf-8')):
    AD[r['date']]+=float(r['cost']); ADC[r['date']][r['campaign']]+=float(r['cost'])
VARC={'ナノガラス脱毛パッド':(757,740),'壁掛けディスペンサー':(2528,1981)}
def daycost(d):
    tot=0
    for n,(g,_) in S[d].items():
        if n in VARC:
            for grp,gg in VG[n].get(d,{}).items():
                tot += round(gg/3980)*(VARC[n][0] if grp=='白緑' else VARC[n][1])
        elif COST.get(n) is not None and n in PRICE and g:
            tot += round(g/PRICE[n])*COST[n]
        elif n=='優先配送': pass
    return tot
WD=['月','火','水','木','金','土','日']
days=sorted(d for d in S if d>='2026-08-01')
print('=== 8月の日次（実売 / 広告 / 利益 / MER）===')
print(f'{"日付":11} {"曜":3} {"実売":>10} {"広告費":>10} {"原価":>9} {"利益":>10} {"利益率":>7} {"MER":>6}')
prof={}
for d in days:
    s=sum(v[0]-v[1] for v in S[d].values()); a=AD[d]; k=daycost(d); p=s-k-a
    prof[d]=(s,a,k,p)
    mk='  ← 昨日' if d=='2026-08-31' else ''
    print(f'{d:11} {WD[datetime.date.fromisoformat(d).weekday()]:3} {s:>10,} {a:>10,.0f} {k:>9,} {p:>+10,.0f} {p/s:>7.1%} {s/a:>6.2f}{mk}')
s,a,k,p=prof['2026-08-31']
print('\n=== ① 8/31 は「観測範囲で最悪」か ===')
allp=[prof[d][3] for d in days if d!='2026-08-31']
alls=[prof[d][0] for d in days if d!='2026-08-31']
allm=[prof[d][0]/prof[d][1] for d in days if d!='2026-08-31']
for lbl,v,base in [('実売',s,alls),('利益',p,allp),('MER',s/a,allm)]:
    below=sum(1 for x in base if x<=v)
    print(f'  {lbl:5} {v:>10,.2f} → 8月{len(base)}日中 {below}日 が同等以下'
          f'  (平均 {statistics.mean(base):,.2f} / z = {(v-statistics.mean(base))/statistics.pstdev(base):+.2f})')
mons=[d for d in days if datetime.date.fromisoformat(d).weekday()==0 and d!='2026-08-31']
print(f'\n=== ② 月曜どうし ===')
for d in mons+['2026-08-31']:
    ss,aa,kk,pp=prof[d]; mk='  ← 昨日' if d=='2026-08-31' else ''
    print(f'  {d}  実売 {ss:>9,}  広告 {aa:>9,.0f}  利益 {pp:>+9,.0f}  MER {ss/aa:.2f}{mk}')
mb=[prof[d] for d in mons]
print(f'  月曜平均: 実売 {statistics.mean([x[0] for x in mb]):,.0f} / 利益 {statistics.mean([x[3] for x in mb]):+,.0f} / '
      f'MER {statistics.mean([x[0]/x[1] for x in mb]):.2f}')
print(f'  → 8/31は 実売 {s/statistics.mean([x[0] for x in mb])-1:+.1%} / 利益 {p/statistics.mean([x[3] for x in mb])-1:+.1%} / '
      f'MER {(s/a)/statistics.mean([x[0]/x[1] for x in mb])-1:+.1%}')
print('\n=== ③ 17:00に出した見込み幅は当たったか ===')
print(f'  17:00の断面MER 1.73 → 見込み幅 1.61〜1.91（r=+0.79・ブレ±8.5%）')
print(f'  終日の実測 MER {s/a:.2f} → **幅の中に入った**')
print('\n=== ④ 3日移動平均利益（非常ブレーキ 130,000円）===')
for i,d in enumerate(days):
    if i<2: continue
    m3=statistics.mean([prof[days[j]][3] for j in (i-2,i-1,i)])
    if d>='2026-08-25': print(f'  {d} {m3:>9,.0f}  {"🚨発動水準" if m3<130000 else "✅"}')

# ---------- 追加: どこが折れたのか ----------
print('\n=== ⑤ 8/31 を3要素に割る（クリック × CVR × 客単価）===')
ORD={'2026-08-17':98,'2026-08-18':89,'2026-08-19':106,'2026-08-20':113,'2026-08-21':110,'2026-08-22':98,
'2026-08-23':106,'2026-08-24':100,'2026-08-25':99,'2026-08-26':105,'2026-08-27':130,'2026-08-28':85,
'2026-08-29':115,'2026-08-30':114,'2026-08-31':84}
ITM={'2026-08-17':117,'2026-08-18':108,'2026-08-19':122,'2026-08-20':138,'2026-08-21':121,'2026-08-22':109,
'2026-08-23':121,'2026-08-24':130,'2026-08-25':117,'2026-08-26':125,'2026-08-27':149,'2026-08-28':96,
'2026-08-29':137,'2026-08-30':133,'2026-08-31':91}
CLK={'2026-08-17':3224,'2026-08-18':3175,'2026-08-19':2811,'2026-08-20':3073,'2026-08-21':2818,'2026-08-22':2901,
'2026-08-23':2994,'2026-08-24':2889,'2026-08-25':3023,'2026-08-26':2519,'2026-08-27':2947,'2026-08-28':2823,
'2026-08-29':3349,'2026-08-30':3159,'2026-08-31':2599}
print(f'{"日付":11} {"曜":3} {"クリック":>7} {"CVR":>7} {"客単価":>8} {"点数/注文":>9} {"CPC":>6} {"実売":>10}')
D=sorted(CLK)
for d in D:
    s=prof[d][0]; o=ORD[d]
    print(f'{d:11} {WD[datetime.date.fromisoformat(d).weekday()]:3} {CLK[d]:>7,} {o/CLK[d]:>7.2%} {s/o:>8,.0f} '
          f'{ITM[d]/o:>9.3f} {prof[d][1]/CLK[d]:>6.0f} {s:>10,}')
base=[d for d in D if d!='2026-08-31']
def z(v,arr): return (v-statistics.mean(arr))/statistics.pstdev(arr)
t='2026-08-31'
print(f'\n  8/31 の各要素を14日分布に置く:')
for lbl,v,arr in [('クリック', CLK[t], [CLK[d] for d in base]),
                  ('CVR', ORD[t]/CLK[t], [ORD[d]/CLK[d] for d in base]),
                  ('客単価', prof[t][0]/ORD[t], [prof[d][0]/ORD[d] for d in base]),
                  ('点数/注文', ITM[t]/ORD[t], [ITM[d]/ORD[d] for d in base]),
                  ('CPC', prof[t][1]/CLK[t], [prof[d][1]/CLK[d] for d in base])]:
    m,sd=statistics.mean(arr),statistics.pstdev(arr)
    below=sum(1 for x in arr if x<=v)
    print(f'    {lbl:9} {v:>9,.3f}  平均 {m:>9,.3f}  z = {z(v,arr):+5.2f}  14日中{below}日が同等以下'
          + ('  ← 最低' if below==0 else ''))
print('\n  【先週月曜 8/24 との分解】')
a,b='2026-08-24','2026-08-31'
rc=CLK[b]/CLK[a]; rv=(ORD[b]/CLK[b])/(ORD[a]/CLK[a]); ra=(prof[b][0]/ORD[b])/(prof[a][0]/ORD[a])
print(f'    クリック {CLK[a]:,} → {CLK[b]:,}  {rc-1:+.1%}')
print(f'    CVR     {ORD[a]/CLK[a]:.2%} → {ORD[b]/CLK[b]:.2%}  {rv-1:+.1%}')
print(f'    客単価   {prof[a][0]/ORD[a]:,.0f} → {prof[b][0]/ORD[b]:,.0f}  {ra-1:+.1%}')
print(f'    掛け算  {rc*rv*ra-1:+.1%}  ／ 実売の実際 {prof[b][0]/prof[a][0]-1:+.1%}  ← 一致すれば分解は正しい')
print('\n=== ⑥ 夕方以降(17:00-24:00)は戻ったか ===')
AH=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open('data/raw/hourly_ad_jst.csv',encoding='utf-8')):
    AH[r['date']][int(r['hour_jst'])]=[int(r['cost']),int(r['clicks'])]
ev=[]
for d in sorted(AH):
    if 23 not in AH[d]: continue
    c=sum(AH[d][h][0] for h in range(17,24))
    s=prof[d][0]-sum(0 for _ in [0])  # 夕方売上は終日−17:00断面が要るので今日のみ実測
print(f'  8/31: 17:00断面 実売230,352 / 広告132,916  →  終日 実売{prof[t][0]:,} / 広告{prof[t][1]:,.0f}')
ec=prof[t][1]-132916; es=prof[t][0]-230352
print(f'  夕方以降(17-24時): 実売 {es:,} / 広告 {ec:,.0f} → MER {es/ec:.2f}')
print(f'  ※終日MER {prof[t][0]/prof[t][1]:.2f} を押し上げた。17:00時点の1.73から着地1.77へ')
