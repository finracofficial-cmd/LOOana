#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-06 カテゴリ別・商品別アクション一覧
7日=7/30-8/05。売上/個数/注文=Shopify実測、広告費/CTR/CVR分母=Meta実測。"""
import pickle, json, collections, csv
SC='/tmp/claude-0/-home-user-LOOana/42be2ed9-9967-56df-ab9c-75166f45bbc9/scratchpad/'
d=pickle.load(open(SC+'rep0806.pkl','rb')); aux=json.load(open(SC+'aux0806.json',encoding='utf-8'))
b=json.load(open(SC+'b0806.json',encoding='utf-8'))
N7,K7,Q7=d['N7'],d['K7'],d['Q7']; BR,TG=d['BR'],d['TG']; D7=d['D7']
ORD7=aux['ORD7']; W2=aux['W2']
MAP={'4WAY':'4WAY 取り付けOK 小型瞬間冷却ハンディファン','完全遮光・形状記憶':'完全遮光・形状記憶・晴雨兼用・UV日傘',
'3WAYサーキュレーター':'3WAYサーキュレーター扇風機','壁掛けディスペンサー':'ディスペンサー'}
AD=collections.defaultdict(lambda: collections.defaultdict(float))
for r in csv.DictReader(open('data/daily/daily_ad.csv',encoding='utf-8')):
    AD[r['campaign']][r['date']]+=float(r['cost'])
A=lambda n: sum(AD[MAP.get(n,n)].get(x,0) for x in D7)
# 現日予算（本日ユーザー実施分を反映・害虫はMeta直接読みで確認済み）
BUD={'4WAY':50000,'3WAYサーキュレーター':16000,'卓上冷感クーラー':17000,'5WAY腰掛けファン':16250,
'瞬間冷却ハンディファン':0,'形状記憶日傘':35000,'完全遮光・形状記憶':28000,'偏光・調光サングラス':22000,
'完全遮光・接触冷感UVハット':8000,'接触冷感UVパーカー':30000,'接触冷感UVアームカバー':17000,'瞬間冷感ポンチョ':9000,
'害虫ブロッカー':45000,'ナノガラス脱毛パッド':80000,'ムダ毛シェーバー':20000,'携帯電動シェーバー':11000,
'健康サンダル':13000,'バランスケアスリッパ':5000,'リカバリーサンダル':0,'W固定スマホ車載ホルダー':15000,
'姿勢サポートチェア':10000,'壁掛けディスペンサー':0,'UV歯ブラシ除菌器':0,'湯上がりガーゼワンピース':0,
'ジェットウォッシャー':0,'スマートノーズEMS美顔器':0,'優先配送':0}
CAT=[('🌀 送風機器（ファン）',['4WAY','5WAY腰掛けファン','卓上冷感クーラー','3WAYサーキュレーター','瞬間冷却ハンディファン'],'カテゴリMER −48% / CVR −40%・リーチ+71%で1人あたり購入率−53% ＝ 買う人が買い終えた。今季は回復しない'),
('☀️ 日差し・UV',['形状記憶日傘','完全遮光・形状記憶','偏光・調光サングラス','完全遮光・接触冷感UVハット'],'カテゴリMER −25% / CTR −3%（興味は無傷）・CVR −11% ＝ 素材では直らない。価格・訴求で延命'),
('👕 冷感アパレル',['接触冷感UVパーカー','接触冷感UVアームカバー','瞬間冷感ポンチョ'],'カテゴリMER −6% / CTR +7% / CVR +5% ＝ 全カテゴリ中もっとも健全。複数枚買う消耗品なので枯れない'),
('🦟 虫',['害虫ブロッカー'],'カテゴリMER −21% / CTR −25% だが CVR −1% ＝ 買う気の人は変わらず買う。新CRが効く唯一のパターン'),
('✨ ムダ毛・脱毛（通年）',['ナノガラス脱毛パッド','ムダ毛シェーバー','携帯電動シェーバー'],'カテゴリMER +20% / CVR +10% ＝ 利益効率0.93で全カテゴリ最上位。ここが本丸'),
('🦶 足（通年）',['健康サンダル','バランスケアスリッパ','リカバリーサンダル'],'カテゴリMER −33% / CTR +16%・CVR −33% ＝ 季節ではなく商品固有（クリックの質）'),
('🚗 車（通年）',['W固定スマホ車載ホルダー'],'CVR 6.06%で店内1位・CPA分岐の45%。新カテゴリで最も伸びしろがある'),
('💺 姿勢・ケア（通年）',['姿勢サポートチェア','ジェットウォッシャー','スマートノーズEMS美顔器'],'姿勢チェアは値下げ再開のテスト中。他2品は広告なしの自然流入'),
('🧼 衛生（通年・停止中）',['壁掛けディスペンサー','UV歯ブラシ除菌器'],'2品とも刈り取り完了で停止済み。再開は10月以降＋新素材＋小予算＋カート追加率7.5%回復の4条件'),
('📦 その他',['湯上がりガーゼワンピース','優先配送'],'広告なし。優先配送は原価0で売上=利益'),
]
rows=[]
for c,ns,note in CAT:
    for n in ns:
        s=N7.get(n,0); k=K7.get(n,0); a=A(n); p=s-k-a; q=Q7.get(n,0); o=ORD7.get(n,0)
        mer=s/a if a>1000 else None; br=BR.get(n); tg=TG.get(n)
        cpa=a/o if o else None; be=((s/q)-(k/q))*(q/o) if (q and o) else None
        cl=W2.get(n,[None]*6)[4] if n in W2 else None
        cvr=o/cl if cl else None
        rows.append(dict(cat=c,n=n,s=s,k=k,a=a,p=p,q=q,o=o,mer=mer,br=br,tg=tg,cpa=cpa,be=be,cvr=cvr,bud=BUD.get(n,0)))
print('='*132)
for c,ns,note in CAT:
    rs=[r for r in rows if r['cat']==c]
    tb=sum(r['bud'] for r in rs); tp=sum(r['p'] for r in rs)
    print(f'\n{c}   日予算 {tb:,}円 ／ 7日利益 {tp:+,}円')
    print(f'  {note}')
    print(f"  {'商品':<22}{'日予算':>8}{'7日売上':>10}{'7日利益':>10}{'MER':>6}{'分岐':>6}{'余裕':>7}{'CPA注文':>8}{'分岐CPA':>8}{'CVR':>7}")
    for r in rs:
        f=lambda v,fmt,d='—': (fmt.format(v) if v is not None else d)
        print(f"  {r['n']:<22}{r['bud']:>8,}{r['s']:>10,}{r['p']:>+10,}{f(r['mer'],'{:6.2f}')}{f(r['br'],'{:6.2f}')}"
              f"{f((r['mer']-r['br']) if (r['mer'] and r['br']) else None,'{:+7.2f}')}{f(r['cpa'],'{:8,.0f}')}{f(r['be'],'{:8,.0f}')}{f(r['cvr'],'{:6.2%}')}")
json.dump(rows,open(SC+'act0806.json','w'),ensure_ascii=False)
print()
print('='*132)
print(f"全店 日予算 {sum(r['bud'] for r in rows):,}円 ／ 7日利益（商品計） {sum(r['p'] for r in rows):+,}円 ＋ カタログ23,000円/日（7日 +49,892円・Meta計上）")
