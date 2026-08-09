# -*- coding: utf-8 -*-
"""8/10 判定: ①バランスケアスリッパ 新素材D 第1関門 ②接触冷感UVアームカバー 本判定"""
import pickle
R=pickle.load(open('/tmp/rep0810.pkl','rb'))
# 【転記】Meta ad別 8/07-8/09 バランスケア（後段で取得）
print('=== ② 接触冷感UVアームカバー 本判定（8/10） ===')
n='接触冷感UVアームカバー'; s=R['N7'][n]; c=R['K7'][n]; a=R['A7'][n]; q=R['Q7'][n]
o=28  # 【転記】Shopify 8/03-09 orders
gm=1-c/s
print(f"  7日(8/03-09): 実売 {s:,} / 広告 {a:,.0f} / 販売数 {q} / 注文 {o}")
print(f"  MER {s/a:.2f}（分岐 {1/gm:.2f}） 余裕 {s/a-1/gm:+.2f}  7日利益 {s-c-a:+,.0f}円")
print(f"  CPA(注文) {a/o:,.0f}円 vs 分岐CPA {(s-c)/o:,.0f}円")
print(f"  前日利益 {R['N1'][n]-R['K1'][n]-R['A1'].get(n,0):+,.0f}円")
prev=-1953
print(f"  推移: 8,000円化前 7日利益 {prev:+,}円 → 8/08時点 +8,014円 → 今回 {s-c-a:+,.0f}円")
print(f"  → 宣言: 黒字化していれば据え置き → {'✅ 据え置き' if s-c-a>0 else '❌ 減額'}")

print()
print('=== ① バランスケアスリッパ 新素材D 第1関門（8/10） ===')
# 【転記】Meta ad別 8/07-09（trace 2c3cafab...）
D=[('2026-08-07','A',2706,1534,24),('2026-08-07','D',1878,873,16),
   ('2026-08-08','A',149,123,1),('2026-08-08','D',5223,2446,52),
   ('2026-08-09','A',27,23,0),('2026-08-09','D',6440,3964,70)]
print(f"{'日付':12}{'広告':>4}{'消化':>8}{'インプ':>7}{'CL':>4}{'CTR':>7}")
for d,n,c,i,cl in D: print(f"{d:12}{n:>4}{c:>8,}{i:>7,}{cl:>4}{(cl/i*100 if i else 0):>6.2f}%")
dc=sum(x[2] for x in D if x[1]=='D'); ac=sum(x[2] for x in D if x[1]=='A')
di=sum(x[3] for x in D if x[1]=='D'); ai=sum(x[3] for x in D if x[1]=='A')
dcl=sum(x[4] for x in D if x[1]=='D'); acl=sum(x[4] for x in D if x[1]=='A')
print()
print(f"  D 3日累計: 消化 {dc:,}円  シェア {dc/(dc+ac)*100:.1f}%  CTR {dcl/di*100:.2f}%")
print(f"  A 3日累計: 消化 {ac:,}円  シェア {ac/(dc+ac)*100:.1f}%  CTR {(acl/ai*100 if ai else 0):.2f}%")
print(f"\n  第1関門の基準: Dの3日累計消化 < 1,500円 なら『Metaが選ばなかった』で終了")
print(f"  実測 {dc:,}円 → {'❌ 終了' if dc<1500 else '✅ 通過（Metaは D を選んだ）'}")
print(f"  → MetaはAをほぼ止めてDへ全振り（8/09時点でAは27円=0.4%）")
R2=pickle.load(open('/tmp/rep0810.pkl','rb'))
n='バランスケアスリッパ'; s=R2['N7'][n]; c=R2['K7'][n]; a=R2['A7'][n]
cl7=359+dcl+acl
print(f"\n  第2関門(8/14)の基準: 広告セット全体の外部CTR ≥ 2.00% かつ 売上/クリック ≥ 163円")
print(f"  現時点の参考値: 直近3日CTR {(dcl+acl)/(di+ai)*100:.2f}%  7日利益 {s-c-a:+,.0f}円  MER {s/a:.2f}（分岐 {1/(1-c/s):.2f}）")
