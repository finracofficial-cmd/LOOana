import json,re,datetime as dt,math,statistics as st,os
D=os.path.dirname(os.path.abspath(__file__))+'/'
sales=json.load(open(D+'sales_1018_1029.json'))+json.load(open(D+'sales_1030_1103.json'))
sess=json.load(open(D+'sess_1018_1029.json'))+json.load(open(D+'sess_1030_1103.json'))
# today's fresh rows override
today_s={r[0]:r for r in json.load(open(D+'sales_1103.json'))}; today_v={r[0]:r for r in json.load(open(D+'sess_1103.json'))}
sales=[today_s.get(r[0],r) for r in sales]+[r for k,r in today_s.items() if k not in {x[0] for x in sales}]
sess=[today_v.get(r[0],r) for r in sess]+[r for k,r in today_v.items() if k not in {x[0] for x in sess}]
oc=json.load(open(D+'ordcount12.json'))
def jst(ts): return dt.datetime.strptime(ts,'%Y-%m-%dT%H:%M:%SZ')+dt.timedelta(hours=9)
S={};V={};M={}
for ts,o,g,d in sales: t=jst(ts); S.setdefault(t.date(),{})[t.hour]=(int(o),int(g),-int(d))
for ts,s,c,r,co in sess: t=jst(ts); V.setdefault(t.date(),{})[t.hour]=(int(s),int(c),int(r),int(co))
for fn in ('meta_hourly.txt','meta_hourly_0911.txt'):
    for line in open(D+fn):
        m=re.match(r'(\S+),"(\d\d):00:00 - .*?",(.*)',line.strip())
        if not m: continue
        M.setdefault(dt.date.fromisoformat(m.group(1)),{})[int(m.group(2))]=[0 if x=='null' else int(x) for x in m.group(3).split(',')]
days=sorted(S); today=days[-1]; past=days[:-1]; WD='月火水木金土日'
def cut(day,H,HM=None):
    HM=HM or H
    o=sum(S[day].get(h,(0,0,0))[0] for h in range(H)); net=sum(S[day].get(h,(0,0,0))[1]-S[day].get(h,(0,0,0))[2] for h in range(H))
    s=[sum(V[day].get(h,(0,0,0,0))[i] for h in range(H)) for i in range(4)]
    m=[sum(M.get(day,{}).get(h,[0]*6)[i] for h in range(HM)) for i in range(6)]
    return o,net,s,m
for day in days:
    k='d'+day.strftime('%m%d'); assert cut(day,12)[0]==oc[k],(day,cut(day,12)[0],oc[k])
print('assert OK: 0〜11時台の時間別合計 == ordersCount(12:00) 17日すべて')
print('\n=== 12:00カット（Shopify 0〜11時台 / Meta 0〜10時台）===')
print('日付 曜 | 注文 実売 1注文 | 来訪 カート 到達 完了 注文/来訪 | 広告 CPM CTR 1LPV Meta購入')
R={}
for day in days:
    o,net,s,m=cut(day,12,11); R[day]=(o,net,s,m)
    print(f"{day.strftime('%m/%d')} {WD[day.weekday()]} | {o:3d} {net:8,} {net/o:6,.0f} | {s[0]:5d} {s[1]:3d} {s[2]:3d} {s[3]:3d} {o/s[0]:.2%} | {m[0]:7,} {m[0]/m[1]*1000:5,.0f} {m[2]/m[1]:5.2%} {m[0]/m[3]:5.1f} {m[5]:3d}")
o_t=R[today][0]; o_p=[R[d][0] for d in past]
print(f"\n12:00 注文 今日{o_t} 過去16日 範囲{min(o_p)}-{max(o_p)} 中央値{st.median(o_p)} 今日より少ない{sum(1 for x in o_p if x<o_t)}日 同数{sum(1 for x in o_p if x==o_t)}日")
print('週末:',[(d.strftime('%m/%d')+WD[d.weekday()],R[d][0]) for d in past if d.weekday()>=5])
n_t=R[today][1]; n_p=[R[d][1] for d in past]; print(f"12:00 実売 今日{n_t:,} 範囲{min(n_p):,}-{max(n_p):,} 中央値{st.median(n_p):,.0f} 少ない{sum(1 for x in n_p if x<n_t)}日")
full={d:sum(v[0] for v in S[d].values()) for d in past}
print('同じ12:00=32件前後だった日の終日:',[(d.strftime('%m/%d'),R[d][0],full[d]) for d in past if 30<=R[d][0]<=33])
xs=[R[d][0] for d in past]; ys=[full[d] for d in past]; r=st.correlation(xs,ys); print(f"12:00注文 vs 終日注文 r={r:.2f} r²={r*r:.0%}; 12:00の占める割合 中央値{st.median([R[d][0]/full[d] for d in past]):.0%}")
s_t=R[today][2][0]; Sp=sum(R[d][2][0] for d in past); Op=sum(R[d][0] for d in past); p=Op/Sp; e=p*s_t; z=(o_t-e)/math.sqrt(s_t*p*(1-p))
print(f"注文/来訪 12:00: 過去16日 {Op}/{Sp}={p:.2%} → 来訪{s_t}なら期待{e:.1f}件、実績{o_t} z={z:+.2f}")
# last 3 days + Sundays funnel
print('\nファネル 0〜11時台: 来訪→カート→到達→完了')
for d in [dt.date(2026,10,25),dt.date(2026,11,1),dt.date(2026,11,2),today]:
    s=R[d][2]; print(f"  {d.strftime('%m/%d')}{WD[d.weekday()]} 来訪{s[0]} カート{s[1]}({s[1]/s[0]:.1%}) 到達{s[2]}({s[2]/s[1]:.0%}) 完了{s[3]}({s[3]/s[2]:.0%}) 注文{R[d][0]} 1注文{R[d][1]/R[d][0]:,.0f}")
# campaigns 0-11
C={}
for line in open(D+'meta_camp_0011.txt'):
    p_=line.strip().split(',')
    if len(p_)<8: continue
    C.setdefault(p_[0],{})[p_[1]]=[0 if x=='null' else int(x) for x in p_[2:]]
print('\nキャンペーン別 0〜11時台 広告/LPV/Meta購入  11/3 | 11/2 | 11/1')
for k in sorted(C['2026-11-03'],key=lambda k:-C['2026-11-03'][k][0]):
    a=C['2026-11-03'][k]; b=C['2026-11-02'].get(k,[0]*6); c=C['2026-11-01'].get(k,[0]*6)
    print(f"  {k}: {a[0]:,}/{a[3]}/{a[5]} | {b[0]:,}/{b[3]}/{b[5]} | {c[0]:,}/{c[3]}/{c[5]}")
for d in ['2026-11-01','2026-11-02','2026-11-03']:
    t=[sum(v[i] for v in C[d].values()) for i in range(6)]; print(f"  合計 {d[5:]}: 広告{t[0]:,} LPV{t[3]} カート{t[4]} Meta購入{t[5]}")
