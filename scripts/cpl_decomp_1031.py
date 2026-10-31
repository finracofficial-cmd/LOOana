# Meta 実測（Supermetrics fresh）: 0〜20時台 A=10/24-28, B=10/29-31（キャンペーン別）／配置別は終日（Bの10/31は途中まで）
A={"4-in-1":(34981,14387,612,586),"車載":(145918,66033,2280,2188),"カタログ":(36746,10613,346,336),"加湿器":(34556,8360,328,314),"ディスペンサー":(326,109,4,4),"ナノ":(340291,284435,4441,4213),"ナノバブル":(14443,9324,215,204),"スリッパ":(8193,4092,97,95),"シーラー":(65683,16784,934,884),"クリーナー":(166270,57389,2094,1994),"洗車ブラシ":(62458,16062,780,750),"チェア":(12362,5633,173,162),"インソール":(132108,85153,1478,1405),"ドアポケット":(16630,3996,130,125),"フック":(38827,6584,247,234)}
B={"2WAY":(5687,2443,42,42),"4-in-1":(21756,8860,261,242),"車載":(80987,35021,1009,942),"ブランケット":(754,268,3,3),"カタログ":(24553,5694,199,190),"ナノ":(126611,93195,1321,1246),"シーラー":(40818,9887,536,498),"ドアクッション":(3288,1000,40,36),"クリーナー":(100498,31454,1108,1036),"洗車ブラシ":(59864,13261,586,548),"健康サンダル":(5000,1939,35,36),"チェア":(36438,15423,417,397),"インソール":(57379,32572,608,556),"フック":(21908,3028,105,100)}
def agg(D): return [sum(v[i] for v in D.values()) for i in range(4)]
def m(v): c,i,o,l=v; return dict(CPM=c/i*1000, CTR=o/i*100, LPVpc=l/o*100, CPL=c/l)
ta,tb=agg(A),agg(B); ma,mb=m(ta),m(tb)
print('全体 A',ta,{k:round(x,2) for k,x in ma.items()}); print('全体 B',tb,{k:round(x,2) for k,x in mb.items()})
print('全体の変化: CPM %+.1f%% / 外部CTR %+.1f%% / LPV÷クリック %+.1f%% → 1来訪単価 %+.1f%%'%((mb['CPM']/ma['CPM']-1)*100,(mb['CTR']/ma['CTR']-1)*100,(mb['LPVpc']/ma['LPVpc']-1)*100,(mb['CPL']/ma['CPL']-1)*100))
common=[k for k in B if k in A]
# 構成効果: Bの商品別消化を、Aの商品別1来訪単価で買えた場合（新商品は実績値）
lpv_mix=sum(B[k][0]/m(A[k])['CPL'] for k in common)+sum(B[k][3] for k in B if k not in A)
print('Bの消化 %d・実LPV %d・単価 %.1f'%(tb[0],tb[3],mb['CPL']))
print('構成だけ変わった場合（商品別単価はAのまま）: LPV %d・単価 %.1f'%(lpv_mix,tb[0]/lpv_mix))
print('→ 単価の上昇 %.1f円のうち 構成の変化 %.1f円 / 商品ごとの単価上昇 %.1f円'%(mb['CPL']-ma['CPL'], tb[0]/lpv_mix-ma['CPL'], mb['CPL']-tb[0]/lpv_mix))
print()
print('%-8s %7s %7s | %6s %6s %6s | %6s %6s %7s | 失ったLPV'%('商品','費A','費B','CPM_A','CPM_B','変化','CTR_A','CTR_B','単価A→B'))
rows=[]
for k in sorted(common,key=lambda k:-B[k][0]):
    a,b=m(A[k]),m(B[k]); lost=B[k][0]/a['CPL']-B[k][3]
    rows.append((k,lost))
    print('%-8s %7d %7d | %6d %6d %+5.0f%% | %5.2f%% %5.2f%% %+5.0f%% | %3.0f→%3.0f %+4.0f%% | %+5.0f'%(k,A[k][0],B[k][0],a['CPM'],b['CPM'],(b['CPM']/a['CPM']-1)*100,a['CTR'],b['CTR'],(b['CTR']/a['CTR']-1)*100,a['CPL'],b['CPL'],(b['CPL']/a['CPL']-1)*100,lost))
print('失ったLPV合計（商品ごとの単価上昇分）', round(sum(l for _,l in rows)))
# 商品内の単価上昇を CPM要因 と CTR(+LPV率)要因 に分ける（対数で按分）
import math
cpm_part=0; ctr_part=0
for k in common:
    a,b=m(A[k]),m(B[k]); w=B[k][0]
    lc=math.log(b['CPM']/a['CPM']); lt=-math.log((b['CTR']*b['LPVpc'])/(a['CTR']*a['LPVpc']))
    cpm_part+=w*lc; ctr_part+=w*lt
s=cpm_part+ctr_part
print('商品内の単価上昇の内訳（消化で加重・対数）: CPM要因 %.0f%% / クリック率・着地率要因 %.0f%%'%(cpm_part/s*100, ctr_part/s*100))
