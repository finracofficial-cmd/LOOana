import csv,datetime as dt,collections,re,io,contextlib
from openpyxl import load_workbook
# --- daily P&L from report 収益 sheet (10/13-11/02) ---
wb=load_workbook('data/reports/report-2026-11-03.xlsx',read_only=True,data_only=True); ws=wb['収益']
PL={}
for r in ws.iter_rows(values_only=True):
    if isinstance(r[0],str) and re.match(r'2026-\d\d-\d\d',r[0]) and isinstance(r[2],(int,float)): PL[r[0]]=dict(s=r[2],k=r[3],a=r[4],p=r[5])
# sessions daily
SE={}
for d,s,c,rc,co in [["2026-09-28","3841","236","220","116"],["2026-09-29","3426","201","186","93"],["2026-09-30","3277","224","205","110"],["2026-10-01","4124","254","239","139"],["2026-10-02","3619","239","224","112"],["2026-10-03","3578","220","203","111"],["2026-10-04","4506","270","243","126"],["2026-10-05","3394","215","192","101"],["2026-10-06","3904","229","213","122"],["2026-10-07","3692","193","187","97"],["2026-10-08","3531","209","185","91"],["2026-10-09","3220","185","176","84"],["2026-10-10","3686","234","223","128"],["2026-10-11","3163","209","194","109"],["2026-10-12","3794","242","218","112"],["2026-10-13","3141","186","164","98"],["2026-10-14","3501","188","162","87"],["2026-10-15","3231","199","181","99"],["2026-10-16","2914","163","147","85"],["2026-10-17","3531","207","204","106"],["2026-10-18","3863","203","183","106"],["2026-10-19","3094","198","177","91"],["2026-10-20","3176","162","143","77"],["2026-10-21","3223","198","184","99"],["2026-10-22","3471","214","206","113"],["2026-10-23","3055","188","177","101"],["2026-10-24","3561","188","171","105"],["2026-10-25","4376","256","230","125"],["2026-10-26","3923","220","205","90"],["2026-10-27","3198","189","174","94"],["2026-10-28","3703","187","168","83"],["2026-10-29","3259","161","151","81"],["2026-10-30","2651","150","127","71"],["2026-10-31","2660","152","133","69"],["2026-11-01","2916","192","178","110"],["2026-11-02","2801","147","134","73"]]:
    SE[d]=list(map(int,(s,c,rc,co)))
ME={}
for line in """2026-09-28,254409,117800,3594,3354,293,114
2026-09-29,233594,103628,3172,2949,260,95
2026-09-30,250966,102552,3006,2793,262,112
2026-10-01,294151,135887,3736,3229,303,142
2026-10-02,253193,118890,3306,2887,304,119
2026-10-03,233639,115690,3245,3023,265,113
2026-10-04,294013,153075,4135,3890,378,124
2026-10-05,225927,113357,3003,2806,300,100
2026-10-06,275694,140039,3501,3276,297,121
2026-10-07,251230,128333,3300,3075,237,95
2026-10-08,246062,127970,3065,2662,464,87
2026-10-09,249934,137997,2836,2580,321,87
2026-10-10,261251,146644,3261,3015,357,123
2026-10-11,260532,130440,2755,2443,355,111
2026-10-12,273825,154152,3288,2876,414,108
2026-10-13,228212,130811,2636,2562,297,103
2026-10-14,261069,137021,3117,3014,298,88
2026-10-15,241645,127264,2967,2781,322,99
2026-10-16,236470,131021,2597,2427,261,83
2026-10-17,238175,144958,3250,3078,352,113
2026-10-18,263353,164808,3575,3399,300,105
2026-10-19,232120,135568,2785,2633,323,94
2026-10-20,248516,138116,2830,2689,230,76
2026-10-21,243239,138375,2904,2753,337,100
2026-10-22,275758,151693,3098,2892,332,108
2026-10-23,263841,135871,2755,2582,308,101
2026-10-24,263907,134327,3241,3100,312,106
2026-10-25,304710,166459,3979,3833,397,122
2026-10-26,258792,150408,3595,3454,358,92
2026-10-27,235206,132509,2868,2688,298,90
2026-10-28,232677,114590,2725,2598,281,81
2026-10-29,253717,123573,2676,2510,242,83
2026-10-30,205839,84225,2181,2051,248,70
2026-10-31,203524,84740,2296,2222,222,69
2026-11-01,230113,88443,2558,2465,328,109
2026-11-02,216333,87103,2522,2394,202,73""".splitlines():
    p=line.split(','); ME[p[0]]=list(map(int,p[1:]))
OB={r['date']:int(r['orders']) for r in csv.DictReader(open('data/daily/daily_order_bands.csv'))}
# product-level daily
src=open('scripts/product_tabs.py',encoding='utf-8').read()
ns={}; exec(src[:src.index('# Shopify商品名 → Metaキャンペーン名')].split('import csv')[0]+ 'pass', ns)  # just to be safe, re-exec dict defs below
m=re.search(r"COST = \{.*?\}\nPRICE = \{.*?\}\n",src,re.S); exec(m.group(0),ns); COST,PRICE=ns['COST'],ns['PRICE']
m2=re.search(r"CAMP = \{.*?\}\n",src,re.S); exec(m2.group(0),ns); CAMP=ns['CAMP']
SA=collections.defaultdict(lambda:collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open('data/daily/daily_sales.csv')): SA[r['name']][r['date']][0]+=int(r['gross']); SA[r['name']][r['date']][1]+=int(r['disc'])
AD=collections.defaultdict(dict)
for r in csv.DictReader(open('data/daily/daily_ad.csv')): AD[r['campaign']][r['date']]=AD[r['campaign']].get(r['date'],0)+float(r['cost'])
def week(d0):
    d=dt.date.fromisoformat(d0); return (d-dt.timedelta(days=d.weekday())).strftime('%m/%d')
weeks=['09/28','10/05','10/12','10/19','10/26']
print('週(月〜日) | 実売 広告 来訪 LPV | CPM 1LPV 来訪/広告千円 注文 注文/来訪 1注文 カート率 完了率 | 実売÷広告 | 利益(収益シートがある週のみ)')
for w in weeks:
    ds=[d for d in SE if week(d)==w]
    s=sum(PL[d]['s'] for d in ds if d in PL) if all(d in PL for d in ds) else None
    st=sum(ME[d][0] for d in ds); se=sum(SE[d][0] for d in ds); lpv=sum(ME[d][3] for d in ds); im=sum(ME[d][1] for d in ds)
    o=sum(OB[d] for d in ds); ca=sum(SE[d][1] for d in ds); rc=sum(SE[d][2] for d in ds); co=sum(SE[d][3] for d in ds)
    # 実売 from daily_sales for all weeks
    sv=sum(v[0]-v[1] for n in SA for d,v in SA[n].items() if d in ds)
    p=sum(PL[d]['p'] for d in ds) if all(d in PL for d in ds) else None
    ptxt=(f"{p:+,.0f} ({p/sv:.1%})") if p is not None else '—'
    print(f"{w} {len(ds)}日 | {sv:,} {st:,} {se:,} {lpv:,} | {st/im*1000:,.0f} {st/lpv:.1f} {se/st*1000:.1f} {o} {o/se:.2%} {sv/o:,.0f} {ca/se:.2%} {co/rc:.0%} | {sv/st:.2f} | {ptxt}")
# product weekly profit (approx cost via PRICE/COST; nano/dispenser blended)
print('\n商品別 週利益（実売−原価−広告。原価=個数×単価、ナノ等は加重平均で近似）')
prods=[n for n in SA if any(d>='2026-09-28' for d in SA[n])]
rows=[]
for n in prods:
    if n.startswith('カタログ') or PRICE.get(n) is None or n not in COST: continue
    pr=PRICE[n]; out=[]
    for w in weeks:
        ds=[d for d in SE if week(d)==w]
        g=sum(SA[n][d][0] for d in ds if d in SA[n]); dc=sum(SA[n][d][1] for d in ds if d in SA[n]); q=g//pr
        a=sum(AD[CAMP.get(n,n)].get(d,0) for d in ds)
        out.append((g-dc-q*COST[n]-a,q,a))
    if sum(x[2] for x in out)>20000: rows.append((n,out))
rows.sort(key=lambda r:-r[1][-1][0])
print('商品 | '+' | '.join(weeks)+'   (利益 / 個 / 広告)')
for n,out in rows: print(n[:14].ljust(14),'|',' | '.join(f"{p:+,.0f}/{q}/{a:,.0f}" for p,q,a in out))
tot=[sum(o[i][0] for n,o in rows) for i in range(5)]; print('合計(表の商品)   |',' | '.join(f"{t:+,.0f}" for t in tot))
