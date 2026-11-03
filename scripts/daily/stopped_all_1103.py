import csv,collections,re,datetime as dt
src=open('scripts/product_tabs.py',encoding='utf-8').read()
ns={}
exec(re.search(r"COST = \{.*?\}\nPRICE = \{.*?\}\n",src,re.S).group(0),ns)
exec(re.search(r"CAMP = \{.*?\}\n",src,re.S).group(0),ns)
COST,PRICE,CAMP=ns['COST'],ns['PRICE'],ns['CAMP']
S=collections.defaultdict(lambda:collections.defaultdict(lambda:[0,0]))
for r in csv.DictReader(open('data/daily/daily_sales.csv')): S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
A=collections.defaultdict(lambda:collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_ad.csv')): A[r['campaign']][r['date']]+=float(r['cost'])
ACTIVE_CAMPS={'マグネットドアクッション','伸縮ワックス洗車ブラシ','ポータブルヒートシーラー','伸縮ガラスクリーナー','4-in-1マルチクリーナー','快適マジックインソール','W固定スマホ車載ホルダー','ナノガラス脱毛パッド','カタログ全部（テスト）','姿勢サポートチェア'}
SUMMER={'害虫ブロッカー','4WAY','形状記憶日傘','完全遮光・形状記憶','接触冷感UVパーカー','5WAY腰掛けファン','偏光・調光サングラス','3WAYサーキュレーター','接触冷感UVアームカバー','健康サンダル','瞬間冷感ポンチョ','卓上冷感クーラー','瞬間冷却ハンディファン','完全遮光・接触冷感UVハット','湯上がりガーゼワンピース'}
def price(n,d):
    if n=='ムダ毛シェーバー': return 6980 if d>='2026-07-27' else 5980
    return PRICE.get(n)
out=[]
for n in S:
    camp=CAMP.get(n,n)
    if camp in ACTIVE_CAMPS or n not in COST: continue
    ad=A.get(camp,{})
    days=sorted(d for d,v in ad.items() if v>0)
    if not days: continue
    last=days[-1]; ld=dt.date.fromisoformat(last)
    def win(d0,d1):
        g=dc=k=0; a=0; bad=0
        for d,(gg,dd) in S[n].items():
            if d0<=d<=d1:
                p=price(n,d)
                if not p: bad=1; continue
                q=gg//p; g+=gg; dc+=dd; k+=q*COST[n]
        a=sum(v for d,v in ad.items() if d0<=d<=d1)
        return g-dc,k,a,bad
    s28=(ld-dt.timedelta(days=27)).isoformat()
    n28,k28,a28,b=win(s28,last)
    mon={}
    for m in ['07','08','09','10']:
        nn,kk,aa,_=win(f'2026-{m}-01',f'2026-{m}-31')
        mon[m]=(round((nn-kk)/aa,2) if aa>3000 else None, round(aa))
    tn,tk,ta,_=win('2026-06-29','2026-11-02')
    # organic sales after stop
    on,ok,_,_=win((ld+dt.timedelta(days=1)).isoformat(),'2026-11-02')
    out.append((n,last,round(a28),round((n28-k28)/a28,2) if a28 else None,round(n28-k28-a28),mon,round(ta),round((tn-tk)/ta,2),round(tn-tk-ta),on,PRICE.get(n),COST[n]))
out.sort(key=lambda r:-(r[3] or 0))
print('商品 | 最終出稿 | 最後28日 広告/倍率/利益 | 月別倍率(広告) 7・8・9・10月 | 6/29〜累計 広告/倍率/利益 | 停止後の売上 | 売価/原価')
for r in out:
    n,last,a28,m28,p28,mon,ta,tm,tp,on,pr,c=r
    ms=' '.join(f"{k}月{v[0] if v[0] is not None else '—'}({v[1]//1000}k)" for k,v in mon.items())
    print(f"{'☀' if n in SUMMER else ' '}{n} | {last} | {a28:,}/{m28}/{p28:+,} | {ms} | {ta:,}/{tm}/{tp:+,} | {on:,} | {pr}/{c}")
