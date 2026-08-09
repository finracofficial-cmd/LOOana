import json,datetime,collections,os
# 実測: Shopify run-analytics-query の返り値をそのまま貼付（転記ではなくクエリ結果のコピー）
RAW=json.load(open('/home/user/LOOana/data/raw/hourly_20260727_20260809.json'))
rows=RAW['rows']
# UTC hour -> JST
d={}
for ts,v in rows:
    t=datetime.datetime.strptime(ts,'%Y-%m-%dT%H:%M:%SZ')+datetime.timedelta(hours=9)
    d[t]=int(v)
start=datetime.datetime(2026,7,27,0)
end=datetime.datetime(2026,8,9,23)
# 欠損時間は売上ゼロで埋める
full={}
t=start
while t<=end:
    full[t]=d.get(t,0)
    t+=datetime.timedelta(hours=1)
assert len(full)==14*24, len(full)
assert sum(full.values())==sum(d.values()), (sum(full.values()),sum(d.values()))
tot=sum(full.values())

byh=collections.defaultdict(list)
for t,v in full.items(): byh[t.hour].append(v)
daily=collections.defaultdict(int)
for t,v in full.items(): daily[t.date()]+=v

print(f"■ 14日(JST 7/27-8/9) 合計 gross {tot:,}円 / 1日平均 {tot/14:,.0f}円\n")
print("JST時間帯   平均売上    日商シェア   累積シェア")
cum=0
for h in range(24):
    avg=sum(byh[h])/14
    sh=sum(byh[h])/tot*100
    cum+=sh
    mark=' ←今ここ' if h in (0,1,2) else ''
    print(f"{h:>2}時台   {avg:>9,.0f}円   {sh:>6.2f}%   {cum:>6.2f}%{mark}")

n=sum(sum(byh[h]) for h in (0,1))/14
print(f"\n■ 深夜0-1時台(2時間)の平均 = {n:,.0f}円 / 日商シェア {n/(tot/14)*100:.2f}%")
z=[(h,sum(1 for v in byh[h] if v==0)) for h in range(24)]
print("  ゼロ売上だった日数(14日中):", {h:c for h,c in z if c>0})

# 0-1時台の日別実績
print("\n■ 0時台+1時台 の日別実績(14日)")
for dt in sorted(daily):
    a=full[datetime.datetime(dt.year,dt.month,dt.day,0)]
    b=full[datetime.datetime(dt.year,dt.month,dt.day,1)]
    print(f"  {dt} ({'日月火水木金土'[(dt.weekday()+1)%7]})  0時 {a:>7,}  1時 {b:>7,}  計 {a+b:>7,}  日商 {daily[dt]:>9,}  シェア {(a+b)/daily[dt]*100:>5.2f}%")
