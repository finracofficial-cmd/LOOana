import json,datetime
# Meta: Supermetrics data_query 実測 (act_1124340806289175, 8/3-8/9, Asia/Tokyo, 時間帯別)
META=[[0,83811,34677,946],[1,49493,20322,587],[2,33651,13486,370],[3,25889,9832,303],[4,32379,11237,385],
[5,67785,23212,790],[6,124039,47137,1494],[7,199779,75561,2247],[8,222446,81883,2440],[9,202797,77165,2250],
[10,183023,74631,2176],[11,157648,64616,1756],[12,190864,80091,2173],[13,150580,58977,1711],[14,132937,53385,1429],
[15,130297,53665,1458],[16,126127,50101,1417],[17,137237,54963,1556],[18,140712,57077,1519],[19,154192,63451,1659],
[20,201383,85592,2292],[21,206480,90737,2384],[22,186692,85097,2133],[23,141322,62823,1606]]
R=json.load(open('data/raw/hourly_20260727_20260809.json'))
d={}
for ts,v in R['rows']:
    t=datetime.datetime.strptime(ts,'%Y-%m-%dT%H:%M:%SZ')+datetime.timedelta(hours=9)
    d[t]=int(v)
days=[datetime.date(2026,8,3)+datetime.timedelta(days=i) for i in range(7)]
sh={h:sum(d.get(datetime.datetime(x.year,x.month,x.day,h),0) for x in days) for h in range(24)}
TS,TC=sum(sh.values()),sum(m[1] for m in META)
print(f"■ 7日(8/3-8/9) Shopify gross {TS:,}円 / Meta広告費 {TC:,}円 / 全体MER {TS/TC:.2f}\n")
print("JST     広告費   費用シェア   売上   売上シェア   同時間MER   CPM     CTR")
rows=[]
for h,c,imp,clk in META:
    mer=sh[h]/c
    rows.append((h,c,sh[h],mer))
    print(f"{h:>2}時  {c:>8,}  {c/TC*100:>5.2f}%  {sh[h]:>8,}  {sh[h]/TS*100:>5.2f}%   {mer:>5.2f}   {c/imp*1000:>6,.0f}  {clk/imp*100:>4.2f}%")
night=[r for r in rows if r[0] in (0,1,2,3,4,5)]
nc=sum(r[1] for r in night); ns=sum(r[2] for r in night)
print(f"\n■ 深夜0-5時(6時間): 広告費 {nc:,}円 ({nc/TC*100:.1f}%) / 売上 {ns:,}円 ({ns/TS*100:.1f}%) / MER {ns/nc:.2f} (全体 {TS/TC:.2f})")
peak=[r for r in rows if r[0] in (7,8,9,20,21,22)]
pc=sum(r[1] for r in peak); ps=sum(r[2] for r in peak)
print(f"■ ピーク7-9/20-22時(6時間): 広告費 {pc:,}円 ({pc/TC*100:.1f}%) / 売上 {ps:,}円 ({ps/TS*100:.1f}%) / MER {ps/pc:.2f}")
print(f"\n※ 同時間MERは「その時間の広告費」÷「その時間の売上」。クリックから購入までのラグを無視した近似のため、")
print(f"  深夜は前夜のクリックの刈り取りが入り実力より高く、早朝は低く出る。順位の目安としてのみ読む。")
