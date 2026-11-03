import json,datetime as dt,collections
import os; D=os.path.dirname(os.path.abspath(__file__))+'/'
ID={'ナノ':'6982162094208','車載':'52550574686812','インソール':'52554797283012','クリーナー':'52565416390612','フック':'52565971537612','シーラー':'52575808822812','洗車ブラシ':'52579156021612','4-in-1':'52564932932612','チェア':'6950740700608','ドアクッション':'52581799551412','カタログ':'6966272711008','流入元なし':''}
MN={'ナノ':'ナノガラス脱毛パッド','車載':'W固定スマホ車載ホルダー','インソール':'快適マジックインソール','クリーナー':'伸縮ガラスクリーナー','フック':'高見えレザーヘッドレストフック','シーラー':'ポータブルヒートシーラー','洗車ブラシ':'伸縮ワックス洗車ブラシ','4-in-1':'4-in-1マルチクリーナー','チェア':'姿勢サポートチェア','ドアクッション':'マグネットドアクッション','カタログ':'カタログ全部（テスト）'}
def wk(d): x=dt.date.fromisoformat(d); return (x-dt.timedelta(days=x.weekday())).strftime('%m/%d')
W=['09/28','10/05','10/12','10/19','10/26']
S=collections.defaultdict(lambda:[0,0,0])
for d,c,s,ca,co in json.load(open(D+'shop_camp_daily.json')):
    k=(c,wk(d)); S[k][0]+=int(s); S[k][1]+=int(ca); S[k][2]+=int(co)
M=collections.defaultdict(lambda:[0]*6)
for line in open(D+'meta_camp_daily.txt'):
    p=line.strip().split(',')
    if len(p)<8: continue
    v=[0 if x=='null' else int(x) for x in p[2:]]; k=(p[1],wk(p[0]))
    for i in range(6): M[k][i]+=v[i]
# sanity: Meta weekly totals vs account-level weekly from earlier table
for w in W: print(w,'Meta合計(キャンペーン積上げ)',sum(v[0] for (n,ww),v in M.items() if ww==w))
print('\n=== キャンペーン別 週次: 来訪 / カート率 / 完了率(完了÷来訪) | 広告 / CPM / CTR / 1LPV / 実CPA(広告÷Shopify完了) ===')
for name,cid in ID.items():
    print(name)
    for w in W:
        s,ca,co=S[(cid,w)]; m=M.get((MN.get(name,'—'),w),[0]*6)
        if s==0 and m[0]==0: continue
        sh=f"来訪{s:5d} カート{ca/s:5.1%} 完了{co/s:5.2%}" if s else "来訪 0"
        mt=f"広告{m[0]:8,} CPM{m[0]/m[1]*1000:6,.0f} CTR{m[2]/m[1]:5.2%} 1LPV{m[0]/m[3]:6.1f} 実CPA{(m[0]/co if co else 0):7,.0f}" if m[1] else ''
        print(f"  {w}  {sh} | {mt}")
# mix vs within for cart rate (attributed sessions only, campaigns in ID)
def tot(w,ids): 
    s=sum(S[(c,w)][0] for c in ids); ca=sum(S[(c,w)][1] for c in ids); co=sum(S[(c,w)][2] for c in ids); return s,ca,co
ids=list(ID.values())
for a,b in [('09/28','10/26'),('10/19','10/26')]:
    sa,caa,coa=tot(a,ids); sb,cab,cob=tot(b,ids)
    # within: b-week rates with a-week session mix
    mix_ca=sum(S[(c,a)][0]/sa*(S[(c,b)][1]/S[(c,b)][0]) for c in ids if S[(c,b)][0] and S[(c,a)][0])
    mix_co=sum(S[(c,a)][0]/sa*(S[(c,b)][2]/S[(c,b)][0]) for c in ids if S[(c,b)][0] and S[(c,a)][0])
    print(f"\n{a}週→{b}週 カート率 {caa/sa:.2%}→{cab/sb:.2%}（{b}の各商品の率に{a}の来訪構成を当てると {mix_ca:.2%}） 完了率 {coa/sa:.2%}→{cob/sb:.2%}（構成固定 {mix_co:.2%}）")
    print('  来訪シェア変化:',', '.join(f"{n} {S[(c,a)][0]/sa:.0%}→{S[(c,b)][0]/sb:.0%}" for n,c in ID.items() if abs(S[(c,a)][0]/sa-S[(c,b)][0]/sb)>=0.02))
