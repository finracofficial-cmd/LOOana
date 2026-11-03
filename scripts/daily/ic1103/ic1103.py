import json,re,datetime as dt,math,statistics as st
import os; D=os.path.dirname(os.path.abspath(__file__))+'/'
sales=json.load(open(D+'sales_1018_1029.json'))+json.load(open(D+'sales_1030_1103.json'))
sess=json.load(open(D+'sess_1018_1029.json'))+json.load(open(D+'sess_1030_1103.json'))
oc=json.load(open(D+'ordcount09.json'))
def jst(ts): return dt.datetime.strptime(ts,'%Y-%m-%dT%H:%M:%SZ')+dt.timedelta(hours=9)
S={}  # day -> hour -> (orders,gross,disc)
for ts,o,g,d in sales:
    t=jst(ts); S.setdefault(t.date(),{})[t.hour]=(int(o),int(g),-int(d))
V={}
for ts,s,c,r,co in sess:
    t=jst(ts); V.setdefault(t.date(),{})[t.hour]=(int(s),int(c),int(r),int(co))
M={}
for line in open(D+'meta_hourly.txt'):
    line=line.strip()
    if not line: continue
    m=re.match(r'(\S+),"(\d\d):00:00 - .*?",(.*)',line); d=dt.date.fromisoformat(m.group(1)); h=int(m.group(2))
    vals=[0 if x=='null' else int(x) for x in m.group(3).split(',')]
    M.setdefault(d,{})[h]=vals  # cost,imp,clk,lpv,atc,pur
days=sorted(S)
WD='月火水木金土日'
def cut(day,H):
    o=sum(S[day].get(h,(0,0,0))[0] for h in range(H)); g=sum(S[day].get(h,(0,0,0))[1] for h in range(H)); d=sum(S[day].get(h,(0,0,0))[2] for h in range(H))
    s=[sum(V[day].get(h,(0,0,0,0))[i] for h in range(H)) for i in range(4)]
    m=[sum(M.get(day,{}).get(h,[0]*6)[i] for h in range(H)) for i in range(6)]
    return o,g-d,s,m
# consistency: 0-8時台 orders from hourly == ordersCount
for day in days:
    k='d'+day.strftime('%m%d')
    if k in oc:
        o=cut(day,9)[0]; assert o==oc[k],(day,o,oc[k])
print('assert OK: 0-8時台の時間別合計 == ordersCount (17日すべて)')
H=8
print(f'\n=== 0〜{H-1}時台カット（{H}:00 JST）===')
print('日付 曜 | 注文 実売 1注文 | 来訪 カート 到達 完了 | 広告 表示 クリック LPV CPM CTR 1LPV | 注文/来訪 来訪/千円')
rows={}
for day in days:
    o,net,s,m=cut(day,H); rows[day]=(o,net,s,m)
    aov=net/o if o else 0
    cpm=m[0]/m[1]*1000 if m[1] else 0; ctr=m[2]/m[1] if m[1] else 0; cpl=m[0]/m[3] if m[3] else 0
    print(f"{day.strftime('%m/%d')} {WD[day.weekday()]} | {o:3d} {net:8,} {aov:6,.0f} | {s[0]:4d} {s[1]:3d} {s[2]:3d} {s[3]:3d} | {m[0]:7,} {m[1]:6,} {m[2]:4d} {m[3]:4d} {cpm:5,.0f} {ctr:5.2%} {cpl:5.1f} | {o/s[0]:.2%} {s[0]/m[0]*1000:5.1f}")
today=days[-1]; past=days[:-1]
o_t=rows[today][0]; o_p=[rows[d][0] for d in past]
print(f"\n{H}:00時点 注文 今日{o_t} 過去16日 範囲{min(o_p)}-{max(o_p)} 中央値{st.median(o_p)} 今日より少ない日 {sum(1 for x in o_p if x<o_t)}日 同数 {sum(1 for x in o_p if x==o_t)}日")
wk=[d for d in past if d.weekday()>=5]
print('週末の同時刻 注文:',[(d.strftime('%m/%d')+WD[d.weekday()],rows[d][0]) for d in wk])
n_t=rows[today][1]; n_p=[rows[d][1] for d in past]
print(f"{H}:00時点 実売 今日{n_t:,} 過去16日 範囲{min(n_p):,}-{max(n_p):,} 中央値{st.median(n_p):,.0f} 今日より少ない日 {sum(1 for x in n_p if x<n_t)}日")
# 9:00 cut orders too
o9={d:cut(d,9)[0] for d in days}; p9=[o9[d] for d in past]
print(f"9:00時点 注文 今日{o9[today]} 過去16日 範囲{min(p9)}-{max(p9)} 中央値{st.median(p9)} 今日より少ない日 {sum(1 for x in p9 if x<o9[today])}日 同数 {sum(1 for x in p9 if x==o9[today])}日")
# full day
full={d:(sum(v[0] for v in S[d].values()), sum(v[1]-v[2] for v in S[d].values())) for d in past}
xs=[o9[d] for d in past]; ys=[full[d][0] for d in past]
r=st.correlation(xs,ys); print(f"\n9:00時点の注文 vs 終日注文（16日）: r={r:.2f} 説明力r²={r*r:.0%}")
sh=[o9[d]/full[d][0] for d in past]; print(f"9:00時点の注文が終日に占める割合 範囲{min(sh):.0%}-{max(sh):.0%} 中央値{st.median(sh):.0%}")
for d in past: print(f"  {d.strftime('%m/%d')}{WD[d.weekday()]} 9時{o9[d]:3d} → 終日{full[d][0]:3d}件 {full[d][1]:,}円")
# chance test: orders per visit at H cut, today vs pooled past
s_t=rows[today][2][0]; S_p=sum(rows[d][2][0] for d in past); O_p=sum(rows[d][0] for d in past)
p=O_p/S_p; exp=p*s_t; sd=math.sqrt(s_t*p*(1-p)); z=(o_t-exp)/sd
print(f"\n注文/来訪 {H}:00時点: 過去16日プール {O_p}/{S_p}={p:.2%} → 今日の来訪{s_t}なら期待{exp:.1f}件 実績{o_t}件 z={z:+.2f}")
# last 3 days + Sundays detail Meta 0-7
print('\n配信（0〜7時台）: 11/3 vs 直近')
for d in [dt.date(2026,10,25),dt.date(2026,11,1),dt.date(2026,11,2),today]:
    m=rows[d][3]; s=rows[d][2]
    print(f"  {d.strftime('%m/%d')}{WD[d.weekday()]} 広告{m[0]:,} 表示{m[1]:,} CPM{m[0]/m[1]*1000:,.0f} CTR{m[2]/m[1]:.2%} LPV{m[3]} 1LPV{m[0]/m[3]:.1f}円 Meta購入{m[5]} | Shopify来訪{s[0]} 注文{rows[d][0]} 実売{rows[d][1]:,}")
# campaigns 0-8
C={}
for line in open(D+'meta_camp.txt'):
    p_=line.strip().split(','); 
    if len(p_)<8: continue
    d=p_[0]; vals=[0 if x=='null' else int(x) for x in p_[2:]]; C.setdefault(d,{})[p_[1]]=vals
print('\nキャンペーン別 0〜8時台 広告費 / LPV / Meta購入（11/3 vs 11/2 vs 11/1）')
for k in sorted(C['2026-11-03'],key=lambda k:-C['2026-11-03'][k][0]):
    a=C['2026-11-03'][k]; b=C['2026-11-02'].get(k,[0]*6); c=C['2026-11-01'].get(k,[0]*6)
    print(f"  {k}: {a[0]:,}/{a[3]}/{a[5]} | {b[0]:,}/{b[3]}/{b[5]} | {c[0]:,}/{c[3]}/{c[5]}")
tot=lambda d:[sum(v[i] for v in C[d].values()) for i in range(6)]
for d in ['2026-10-25','2026-11-01','2026-11-02','2026-11-03']:
    t=tot(d); print(f"  合計 {d[5:]}: 広告{t[0]:,} LPV{t[3]} カート{t[4]} Meta購入{t[5]}")
