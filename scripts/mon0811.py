# -*- coding: utf-8 -*-
import csv,collections,datetime,statistics,pickle
R=pickle.load(open('/tmp/rep0811.pkl','rb'))
S=collections.defaultdict(float); A=collections.defaultdict(float)
PS=collections.defaultdict(lambda: collections.defaultdict(float))
PA=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_sales.csv')):
    v=float(r['gross'])-float(r['disc']); S[r['date']]+=v; PS[r['name']][r['date']]+=v
for r in csv.DictReader(open('data/daily/daily_ad.csv')):
    A[r['date']]+=float(r['cost']); PA[r['campaign']][r['date']]+=float(r['cost'])
HOL={'2026-07-20'}; WD='月火水木金土日'
# ① 8/10（月）を除いた「平常月曜」平均で評価する（8/10自身を基準に入れない）
mon=[d for d in S if d<'2026-08-10' and d>='2026-07-11'
     and datetime.date.fromisoformat(d).weekday()==0 and d not in HOL]
mavg=statistics.mean([S[d] for d in mon])
print(f"■ 8/10(月) 実売 {S['2026-08-10']:,.0f}円")
print(f"  平常月曜平均（{', '.join(mon)}）= {mavg:,.0f}円  → 対同曜日 {S['2026-08-10']/mavg*100:.1f}%")
print(f"  直近7日平均 {sum(S[d] for d in R['D7'])/7:,.0f}円  → 対7日平均 {S['2026-08-10']/(sum(S[d] for d in R['D7'])/7)*100:.1f}%")
print("\n■ 直近10日の推移（実売／広告／MER／利益は7日窓の原価率で近似せず、日次は実売とMERのみ）")
for d in sorted(S)[-10:]:
    dt=datetime.date.fromisoformat(d); mark='(祝)' if d in HOL else ''
    print(f"  {d}({WD[dt.weekday()]}){mark}  実売 {S[d]:>10,.0f}  広告 {A[d]:>9,.0f}  MER {S[d]/A[d]:>5.2f}")
print("\n■ 3日移動平均 実売（非常ブレーキは利益ベースなので参考）")
ds=sorted(S)
for i in range(len(ds)-5,len(ds)):
    w=ds[i-2:i+1]; print(f"  {ds[i]}  {sum(S[x] for x in w)/3:>11,.0f}")
print("\n■ 日傘2種の日次MER（分岐: 短1.36 / 長1.36 ※原価1309・売価4980）")
for n,c in [('形状記憶日傘','形状記憶日傘'),('完全遮光・形状記憶','完全遮光・形状記憶・晴雨兼用・UV日傘')]:
    print(f"  --- {n} ---")
    for d in sorted(S)[-6:]:
        s=PS[n].get(d,0); a=PA[c].get(d,0)
        if a==0: continue
        m=s/a; print(f"    {d}  実売 {s:>9,.0f}  広告 {a:>8,.0f}  MER {m:>5.2f}  {'🚨分岐割れ' if m<1.36 else ''}")
print("\n■ 8/10 消化率（実効予算＝8/10朝時点の設定。8/10中の変更なし）")
BUD={'ナノガラス脱毛パッド':80000,'W固定スマホ車載ホルダー':32500,'形状記憶日傘':35000,
'4WAY 取り付けOK 小型瞬間冷却ハンディファン':28000,'害虫ブロッカー':45000,'接触冷感UVパーカー':30000,
'カタログ全部（テスト）':23000,'ムダ毛シェーバー':20000,'完全遮光・形状記憶・晴雨兼用・UV日傘':21000,
'偏光・調光サングラス':22000,'5WAY腰掛けファン':16250,'完全遮光・接触冷感UVハット':12000,
'2WAYシートボックス':15000,'姿勢サポートチェア':10000,'携帯電動シェーバー':8250,'瞬間冷感ポンチョ':9000,
'接触冷感UVアームカバー':8000,'卓上冷感クーラー':7500,'バランスケアスリッパ':5000}
tb=0
for c,b in sorted(BUD.items(),key=lambda x:-x[1]):
    sp=PA[c].get('2026-08-10',0); tb+=b
    flag='🔺天井' if sp/b>=1.0 else ('⚠️低消化' if sp/b<0.85 else '')
    print(f"  {c[:26]:26} 予算 {b:>7,}  消化 {sp:>8,.0f}  {sp/b*100:>5.1f}%  {flag}")
print(f"  {'合計':26} 予算 {tb:>7,}  消化 {A['2026-08-10']:>8,.0f}  {A['2026-08-10']/tb*100:>5.1f}%")
