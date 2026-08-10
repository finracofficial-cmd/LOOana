import csv,collections,statistics,datetime
S=collections.defaultdict(float); A=collections.defaultdict(float)
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    S[r['date']]+=float(r['gross'])-float(r['disc'])
for r in csv.DictReader(open('data/daily/daily_ad.csv')):
    A[r['date']]+=float(r['cost'])
days=sorted(S)
print(f"CSVカバー: {days[0]} 〜 {days[-1]}（{len(days)}日）")
HOL={'2026-07-20'}  # 海の日
WD='月火水木金土日'
def idx(window,label):
    g=collections.defaultdict(list)
    for d in window:
        if d in HOL: continue
        w=datetime.date.fromisoformat(d).weekday()
        g[w].append(S[d])
    allv=[v for l in g.values() for v in l]
    m=statistics.mean(allv)
    print(f"\n■ 曜日指数 {label}（祝日7/20除外・売上=gross−値引・全体平均={m:,.0f}円=100）")
    rows=[]
    for w in range(7):
        a=statistics.mean(g[w]); rows.append((WD[w],a,a/m*100,len(g[w])))
    for w,a,i,n in sorted(rows,key=lambda x:-x[2]):
        print(f"  {w}曜  {a:>10,.0f}円   指数 {i:>5.1f}   n={n}")
    return {r[0]:r[2] for r in rows}

w30=[d for d in days if d>='2026-07-11']
wall=days
i30=idx(w30,'直近30日 7/11-8/09')
iall=idx(wall,f'全期間 {days[0]}-{days[-1]}')

print("\n■ 「休み明け」= 日曜→月曜 の落差（週ごと・実測）")
print("  週    日曜売上      月曜売上     落差      月/日")
for d in days:
    dt=datetime.date.fromisoformat(d)
    if dt.weekday()!=6: continue
    nx=(dt+datetime.timedelta(days=1)).isoformat()
    if nx not in S: continue
    tag=' ※祝日翌日' if d in HOL else ''
    print(f"  {d}  {S[d]:>10,.0f}  {S[nx]:>10,.0f}  {S[nx]-S[d]:>+10,.0f}  {S[nx]/S[d]*100:>5.1f}%{tag}")

print("\n■ 三連休明け（2026-07-20 海の日=月 → 7/21 火）")
for d in ['2026-07-18','2026-07-19','2026-07-20','2026-07-21','2026-07-22']:
    dt=datetime.date.fromisoformat(d)
    base=i30[WD[dt.weekday()]]
    print(f"  {d}({WD[dt.weekday()]})  売上 {S[d]:>10,.0f}   指数 {S[d]/statistics.mean([S[x] for x in w30 if x not in HOL])*100:>5.1f}  (その曜日の平常指数 {base:.1f})")

print("\n■ MERも曜日で動くか（直近30日・祝日除外）")
g=collections.defaultdict(lambda:[0,0])
for d in w30:
    if d in HOL: continue
    w=datetime.date.fromisoformat(d).weekday()
    g[w][0]+=S[d]; g[w][1]+=A[d]
tot=[sum(g[w][0] for w in g),sum(g[w][1] for w in g)]
print(f"  全体MER {tot[0]/tot[1]:.3f}")
for w in range(7):
    print(f"  {WD[w]}曜  売上 {g[w][0]:>11,.0f}  広告 {g[w][1]:>10,.0f}  MER {g[w][0]/g[w][1]:.3f}  (対全体 {g[w][0]/g[w][1]/(tot[0]/tot[1])*100:>5.1f}%)")
