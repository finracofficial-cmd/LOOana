# -*- coding: utf-8 -*-
"""v2 に「シンプル判定」シートを先頭extraとして追加した v3 を作る（データはCSV実測から計算）"""
import json, csv, collections, copy
B='/home/user/LOOana/data/daily/'
COST={'4WAY':1730,'害虫ブロッカー':867,'形状記憶日傘':1309,'完全遮光・形状記憶':1309,'卓上冷感クーラー':1996,
'接触冷感UVパーカー':1434,'5WAY腰掛けファン':1848,'偏光・調光サングラス':893,'3WAYサーキュレーター':2485,
'接触冷感UVアームカバー':784,'健康サンダル':1162,'瞬間冷感ポンチョ':987,'ムダ毛シェーバー':2798,
'携帯電動シェーバー':1743,'バランスケアスリッパ':1304,'UV歯ブラシ除菌器':3240,'ナノガラス脱毛パッド':751,'壁掛けディスペンサー':2318}
PRICE={'4WAY':4980,'害虫ブロッカー':3980,'形状記憶日傘':4980,'完全遮光・形状記憶':4980,'卓上冷感クーラー':5980,
'接触冷感UVパーカー':3980,'5WAY腰掛けファン':4980,'偏光・調光サングラス':3980,'3WAYサーキュレーター':5980,
'接触冷感UVアームカバー':3980,'健康サンダル':4980,'瞬間冷感ポンチョ':3980,'ムダ毛シェーバー':6980,
'携帯電動シェーバー':4980,'バランスケアスリッパ':4980,'UV歯ブラシ除菌器':8980,'ナノガラス脱毛パッド':3980,'壁掛けディスペンサー':6980}
MAP={'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
'3WAYサーキュレーター':'3WAYサーキュレーター扇風機','壁掛けディスペンサー':'ディスペンサー'}
BR={'4WAY':(1.57,3.48),'害虫ブロッカー':(1.31,2.43),'形状記憶日傘':(1.37,2.63),'完全遮光・形状記憶':(1.37,2.64),
'卓上冷感クーラー':(1.53,3.28),'接触冷感UVパーカー':(1.58,3.55),'5WAY腰掛けファン':(1.66,3.94),
'偏光・調光サングラス':(1.30,2.38),'3WAYサーキュレーター':(1.76,4.60),'接触冷感UVアームカバー':(1.25,2.23),
'健康サンダル':(1.32,2.47),'瞬間冷感ポンチョ':(1.36,2.60),'ムダ毛シェーバー':(1.77,4.67),
'携帯電動シェーバー':(1.54,3.33),'バランスケアスリッパ':(1.37,2.63),'UV歯ブラシ除菌器':(1.58,3.55),
'ナノガラス脱毛パッド':(1.24,2.18),'壁掛けディスペンサー':(1.56,3.44)}
ACT={'4WAY':'7/31判定: 増分MER−0.72＜分岐 → 70,000へ戻す方向',
'害虫ブロッカー':'需要減衰（販売数−33%）。72,000へ縮小済み。8/6判定（1日利益≥59,703円）。秋物の後継選定を並行',
'形状記憶日傘':'健全。P-1解除後の増額候補（Δ+36,030円/日で測定可能）',
'ナノガラス脱毛パッド':'7/30に76,000へ増額済み。8/2判定',
'接触冷感UVパーカー':'増額成功（増分MER+4.21）。34,000維持',
'卓上冷感クーラー':'7/31判定: 増分MER+0.28＜分岐 → 24,000へ戻す方向',
'完全遮光・形状記憶':'7/28に34,000へ復元済み。7/31判定で維持を確認',
'5WAY腰掛けファン':'16,250維持。CVR−36%を監視。増額はP-1解除後にΔ+13,238円/日（→30,000）で',
'ムダ毛シェーバー':'P-1解除後の増額第1候補（Δ+5,496円/日で測定可能 → 18,500）',
'瞬間冷感ポンチョ':'8/1判定。P-1発動中は未測定の増額禁止 → 13,000据置',
'偏光・調光サングラス':'LP改修（期限8/1・未着手）。8/5にCVR≥3.2%で判定',
'接触冷感UVアームカバー':'8/5判定（余裕≥+0.8）',
'3WAYサーキュレーター':'増分MER−2.66＝増額失敗。8/2に13,000へ戻す判定を提案中',
'UV歯ブラシ除菌器':'減額が成功（CVR+85%）。10,000維持。何もしない',
'健康サンダル':'CPM+27%（D4）。8/2判定を提案中（7日MER≥1.50かつ7日利益>0、割れたら6,500へ半減）',
'携帯電動シェーバー':'広告では直らない（余裕+0.17）。値上げ+1,000円を検討。8/5判定（7日MER≥1.90）',
'壁掛けディスペンサー':'8/4判定: LP後CVR≥2.5%未達なら停止。0520類似5%セット（CPA9,198円）の個別停止も選択肢',
'バランスケアスリッパ':'半減が成功（増分+1.90）。5,000維持。監視のみ'}
S=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0])); A=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open(B+'daily_sales.csv',encoding='utf-8')):
    S[r['name']][r['date']][0]+=int(r['gross']); S[r['name']][r['date']][1]+=int(r['disc'])
for r in csv.DictReader(open(B+'daily_ad.csv',encoding='utf-8')):
    A[r['campaign']][r['date']]+=float(r['cost'])
BD=collections.defaultdict(lambda: collections.defaultdict(int))
for r in csv.DictReader(open('/home/user/LOOana/data/budget-snapshots.csv',encoding='utf-8')):
    BD[r['campaign']][r['snapshot_date']]+=int(r['daily_budget'])
D7=['2026-07-%02d'%x for x in range(23,30)]; D3=D7[-3:]; D1=D7[-1:]
def qty(n,d):
    g=S[n][d][0]
    if not g: return 0
    if n=='ムダ毛シェーバー':      # 7/27に5,980→6,980へ値上げ（日付対応の売価）
        if d<'2026-07-27': return round(g/5980)
        if g%6980==0: return g//6980
        for b in range(g//6980+1):
            if (g-b*6980)%5980==0: return (g-b*6980)//5980+b
    return round(g/PRICE[n])
def blk(n,ds):
    g=sum(S[n][d][0] for d in ds); dc=sum(S[n][d][1] for d in ds); s=g-dc
    q=sum(qty(n,d) for d in ds); c=q*COST[n]; a=sum(A[MAP.get(n,n)].get(d,0) for d in ds)
    return s,c,a,s-c-a
rows=[]
for n in BR:
    s7,c7,a7,p7=blk(n,D7); s3,c3,a3,p3=blk(n,D3); s1,c1,a1,p1=blk(n,D1)
    if a7==0: continue
    br,tg=BR[n]
    m7=s7/a7; m3=s3/a3 if a3 else 0; m1=s1/a1 if a1 else 0
    b7=sum(BD[MAP.get(n,n)].get(d,0) for d in D7); use=a7/b7 if b7 else 0
    if m7<br or p7<0: st,pr='🚨 縮小・停止',0
    elif m3<br or m7<br+0.3 or m3<br+0.3: st,pr='🔧 改善',1
    elif m7>=tg and use>=0.95: st,pr='🚀 伸ばす候補',2
    else: st,pr='✅ 維持',3
    rows.append((pr,-a7,[n,round(m7,2),round(m3,2),round(m1,2),br,tg,p7,p3,round(p1),round(use,3),st,ACT[n]]))
rows.sort()
d=json.load(open('/home/user/LOOana/data/report-data-2026-07-30-v2.json',encoding='utf-8'))
d=copy.deepcopy(d)
d['date']=d['date'].replace('【v2・訂正反映版】','【v3】')
simple=dict(name='シンプル判定', title='シンプル判定 — 7日の効率で判断・3日で警戒・悪ければ改善（分岐MER=赤字ライン／目標MER=利益率35%ライン）。詳細な根拠は後ろのシートと商品タブ',
 header=['商品','7日MER','3日MER','前日MER','分岐','目標','7日利益','3日利益','前日利益','消化率','状態','今やること（1行）'],
 widths=[24,8,8,8,7,7,11,11,11,8,13,72], money=[7,8,9], pct=[10], dec2=[2,3,4,5,6],
 rows=[r[2] for r in rows],
 notes=['状態の決め方: 🚨=7日MERが分岐割れ or 7日利益マイナス ／ 🔧=3日MERが分岐割れ or 7日・3日MERが分岐+0.3未満（弱含み） ／ 🚀=7日MER≥目標 かつ 消化率≥95%（増額はP-1解除後） ／ ✅=それ以外',
        '判断は7日で行い、3日は警戒シグナル、前日は監視のみ（単日で意思決定しない）。',
        '現在 P-1発動中（全店の週次MERが単週−11.9%）＝実測の増分MERが目標超えでない増額は禁止。解除条件は提案中（2週連続改善 or 単週+5%改善）。'])
d['extra']=[simple]+d['extra']
json.dump(d,open('/home/user/LOOana/data/report-data-2026-07-30-v3.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('v3 json ok /', len(rows), '商品')
for r in rows: print(' ', r[2][10], r[2][0])
