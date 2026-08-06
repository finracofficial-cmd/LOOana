# -*- coding: utf-8 -*-
"""判定日の執行・数量割引KPI・突合。注文数はShopify実測（2026-08-07取得・合計でassert）"""
import pickle
R=pickle.load(open('/tmp/rep0807.pkl','rb'))
# Shopify GROUP BY product_title, SHOW orders（7/31-8/06）— summaryMetric 1,473 で検算【転記・検算済】
O7={'ナノガラス脱毛パッド':317,'4WAY':151,'害虫ブロッカー':131,'形状記憶日傘':132,'接触冷感UVパーカー':122,
'完全遮光・形状記憶':89,'ムダ毛シェーバー':64,'5WAY腰掛けファン':60,'卓上冷感クーラー':43,'偏光・調光サングラス':60,
'W固定スマホ車載ホルダー':53,'3WAYサーキュレーター':21,'瞬間冷感ポンチョ':24,'接触冷感UVアームカバー':33,
'携帯電動シェーバー':27,'完全遮光・接触冷感UVハット':22,'健康サンダル':17,'姿勢サポートチェア':13,
'バランスケアスリッパ':9,'UV歯ブラシ除菌器':5,'壁掛けディスペンサー':5,'優先配送':65,'湯上がりガーゼワンピース':3,
'リカバリーサンダル':2,'ジェットウォッシャー':2,'瞬間冷却ハンディファン':1,'スマートノーズEMS美顔器':1,'2WAYシートボックス':1}
assert sum(O7.values())==1473, sum(O7.values())
COST=R['COST']; PRICE=R['PRICE']
print('=== 7日 CPA(注文)＝Shopify注文ベース vs 分岐CPA ===')
print(f"{'商品':16}{'注文':>6}{'点/注文':>8}{'広告':>10}{'CPA':>8}{'分岐CPA':>9}{'差':>9}")
out=[]
for n,o in sorted(O7.items(), key=lambda x:-R['N7'].get(x[0],0)):
    a=R['A7'].get(n,0); q=R['Q7'].get(n,0); s=R['N7'].get(n,0); c=R['K7'].get(n,0)
    if a<1000 or o==0: continue
    cpa=a/o; gmu=(s-c)/q if q else 0; be=gmu*(q/o)
    out.append((n,o,q/o,a,cpa,be,be-cpa))
    print(f"{n[:16]:16}{o:>6}{q/o:>8.2f}{a:>10,.0f}{cpa:>8,.0f}{be:>9,.0f}{be-cpa:>+9,.0f}")
print()
q1=sum(R['Q1'].values())-R['Q1'].get('優先配送',0); q7=sum(R['Q7'].values())-R['Q7'].get('優先配送',0)
print('=== 数量割引KPI（点数/注文） ===')
print(f"  8/06: 商品点数 {q1} ÷ 全店注文 157 = {q1/157:.3f}")
print(f"  7日 : 商品点数 {q7} ÷ 全店注文(商品別合計-優先配送) = 参考")
print(f"  優先配送アタッチ率 8/06: 3/157 = {3/157*100:.2f}%   7日: 65注文")
print()
print('=== 8/7の判定（宣言済み基準で執行） ===')
g=[x for x in out if x[0]=='害虫ブロッカー'][0]
print(f"  害虫ブロッカー: 基準 7日CPA(注文) < 3,113円 → 実測 {g[4]:,.0f}円 → {'✅ 合格' if g[4]<3113 else '❌ 不合格'}")
h=[x for x in out if x[0]=='完全遮光・接触冷感UVハット'][0]
print(f"  完全遮光・接触冷感UVハット: 基準 CPA < 4,569円 → 実測 {h[4]:,.0f}円 → {'✅ 合格' if h[4]<4569 else '❌ 不合格'}")
c=[x for x in out if x[0]=='姿勢サポートチェア'][0]
print(f"  姿勢サポートチェア（中間）: CPA {c[4]:,.0f}円 vs 分岐 {c[5]:,.0f}円 → {'✅' if c[4]<c[5] else '❌'}（本判定8/11）")
