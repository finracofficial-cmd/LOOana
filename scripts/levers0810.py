# -*- coding: utf-8 -*-
"""利益率を上げる打ち手を、実測から大きさ順に並べる。7日 8/03-09 基準。"""
import pickle
R=pickle.load(open('/tmp/rep0810.pkl','rb'))
s=sum(R['N7'].values()); c=sum(R['K7'].values()); a=R['ACCT7']; p=s-c-a
print(f"現状(7日): 実売 {s:,} / 原価 {c:,} / 広告 {a:,.0f} / 利益 {p:,.0f} / 利益率 {p/s*100:.2f}%")
print()
LV=[]
# ① 赤字商品の停止（稼働中のみ）
red=[(n,R['N7'][n]-R['K7'][n]-R['A7'].get(n,0),R['A7'].get(n,0)) for n in R['N7']
     if R['A7'].get(n,0)>3000 and R['N7'][n]-R['K7'][n]-R['A7'].get(n,0)<0
     and n not in ('健康サンダル','UV歯ブラシ除菌器','3WAYサーキュレーター')]
LV.append(('① 稼働中の赤字商品を止める', -sum(x[1] for x in red), ' / '.join(f'{x[0]}({x[1]:+,.0f})' for x in red)))
# ② 余裕がマイナス〜+0.2の商品を−25%（限界MER=平均×0.7想定）
thin=[]
for n in R['N7']:
    ad=R['A7'].get(n,0)
    if ad<3000: continue
    sn=R['N7'][n]; kn=R['K7'][n]; gm=1-kn/sn; mer=sn/ad; yo=mer-1/gm
    if 0<=yo<0.25:
        gain=(1-mer*0.7*gm)*ad*0.25
        thin.append((n,gain,ad))
LV.append(('② 余裕+0.25未満を−25%', sum(x[1] for x in thin), ' / '.join(f'{x[0]}({x[1]:+,.0f})' for x in thin)))
# ③ 優先配送のアタッチ率（原価0＝全額利益）
ORD7=1441+0
pri=R['N7'].get('優先配送',0); att=249/1441
for tgt in [0.10,0.15]:
    LV.append((f'③ 優先配送アタッチ率 {att*100:.1f}%→{tgt*100:.0f}%', (tgt-att)*1441*536, f'1件536円×注文数。原価0なので全額利益'))
# ④ 原価率 −1pt
LV.append(('④ 原価率 −1.0pt（CJ再交渉）', s*0.01, f'原価 {c:,}→{c-s*0.01:,.0f}'))
# ⑤ 点数/注文を7日平均→W-4水準へ
LV.append(('⑤ 点数/注文 1.20→1.27（数量割引の記載効果）', s*0.0287*0.712, '売上+2.87%×粗利率71.2%'))
# ⑥ UVハット増額（余裕+1.60・追加1円は限界MER=平均×0.7）
n='完全遮光・接触冷感UVハット'; sn=R['N7'][n]; kn=R['K7'][n]; ad=R['A7'][n]; gm=1-kn/sn; mer=sn/ad
LV.append(('⑥ UVハット 8,000→12,000（+50%）', (mer*0.7*gm-1)*4000*7, f'追加1円あたり +{mer*0.7*gm-1:.3f}円'))
LV.sort(key=lambda x:-x[1])
print(f"{'打ち手':40}{'週あたり利益':>14}{'利益率':>9}")
for n,v,m in LV:
    print(f"{n:40}{v:>+14,.0f}{v/s*100:>+8.2f}pt")
    print(f"{'':40}{m}")
print()
tot=sum(x[1] for x in LV if not x[0].startswith('③ 優先配送アタッチ率 17.3'))
print(f"  ※③は2案あるので片方のみ採用。全部合わせると 週 +{sum(x[1] for x in LV[:6]):,.0f}円 規模")
