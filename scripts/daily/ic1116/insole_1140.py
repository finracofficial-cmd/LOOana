"""インソール: 今日0〜11時台の注文（同じ時刻で切った過去21日と比較）と、旧キャンペーンの日別推移。
入力: ic1116/insole_hourly_1140.json（Shopify sales・product_title CONTAINS 'インソール'・TIMESERIES hour・UTC）
      o1115/ad_level_1026_1115.txt（Meta 広告別）・data/daily/daily_sales.csv / daily_ad.csv
"""
import json,csv,datetime as dt,collections
D='scripts/daily/'
H=json.load(open(D+'ic1116/insole_hourly_1140.json'))
cut=12  # JST 0:00〜11:59
o=collections.Counter(); g=collections.Counter()
for t,n,v in H:
    j=dt.datetime.strptime(t,'%Y-%m-%dT%H:%M:%SZ')+dt.timedelta(hours=9)
    if j.hour<cut: o[j.date().isoformat()]+=int(n); g[j.date().isoformat()]+=int(v)
days=[(dt.date(2026,10,26)+dt.timedelta(d)).isoformat() for d in range(21)]
past=[o[d] for d in days]
today=o['2026-11-16']
print('今日 0〜11時台: 注文',today,'・売上',g['2026-11-16'],'（',g['2026-11-16']//3980,'個）')
print('過去21日（10/26〜11/15）同じ時刻まで: 注文',sorted(past),' 中央値',sorted(past)[10],' 最小',min(past),' 最大',max(past))
print('21日のうち今日より少ない日',sum(p<today for p in past),'・同じ日',sum(p==today for p in past),'・多い日',sum(p>today for p in past))
# 旧キャンペーンの日別
AD=collections.defaultdict(lambda:[0,0,0])
for l in open(D+'o1115/ad_level_1026_1115.txt',encoding='utf-8'):
    if l.startswith('#') or 'インソール' not in l: continue
    d,c,a,ad,cost,imp,lc=l.strip().split(',')
    x=AD[d]; x[0]+=float(cost); x[1]+=int(imp); x[2]+=int(lc)
S={}; 
for r in csv.DictReader(open('data/daily/daily_sales.csv',encoding='utf-8')):
    if r['name']=='快適マジックインソール': S[r['date']]=(int(r['gross']),int(r['disc']))
C={r['date']:float(r['cost']) for r in csv.DictReader(open('data/daily/daily_ad.csv',encoding='utf-8')) if r['campaign']=='快適マジックインソール'}
print('\n日付 広告費 表示 クリック率 CPM 個数 倍率（売上−値引−原価677×個数）÷広告費')
for d in sorted(AD):
    cost,imp,lc=AD[d]; gs,di=S.get(d,(0,0)); n=gs//3980; c=C.get(d,cost)
    m=(gs-di-677*n)/c if c else 0
    print(d, round(c), imp, f'{lc/imp*100:.2f}%', round(cost/imp*1000), n, f'{m:.2f}')
def win(a,b):
    ds=[d for d in sorted(AD) if a<=d<=b]
    c=sum(C[d] for d in ds); gs=sum(S[d][0] for d in ds); di=sum(S[d][1] for d in ds); n=gs//3980
    imp=sum(AD[d][1] for d in ds); lc=sum(AD[d][2] for d in ds)
    print(a,'〜',b,'広告費',round(c),'個数',n,'倍率',f'{(gs-di-677*n)/c:.2f}','クリック率',f'{lc/imp*100:.2f}%','CPM',round(c/imp*1000))
win('2026-10-26','2026-11-01'); win('2026-11-02','2026-11-08'); win('2026-11-09','2026-11-15')
