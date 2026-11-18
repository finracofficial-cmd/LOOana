# -*- coding: utf-8 -*-
"""2026-11-18(水) をCSVへ追記。11/19 00時台に取得。広告費はキャンペーン合算（data_query fresh・1日ずつ・暫定。scripts/daily/o1118/meta_camp_1117_1118_raw.txt）。
当日の予算・広告の変更（ユーザー・Meta直読で確認。budget-snapshots 2026-11-18a〜g）: 00時台 ブラシ・ブランケット停止／ガラス sabu 22,000→19,000／W 10,000→8,000・W -sab 13,000→10,400／
マルチクリップ 10,000→12,000／ナノ 18,000→21,000（18a）・ドア 9,600→12,000（18b）／11時台 グローブ停止→再開（18c・18d）・フック v5 開始 8,000（18d）／
シーラー v2 開始 8,000（18e・夜に旧動画の広告Bへ差し替え）／グローブ停止（18f・11/19 00時台の直読でキャンペーン PAUSED）／23時台 ディスペンサー v2 開始 8,000（18g）。
VIP特典の無料優先配送12件（gross 0円）は売上行に入れない。有料の優先配送2件（1,580円）。返品なし。
広告費ありで売上0: カタログ全部（テスト）・3WAY着る電気ブランケット（157）・伸縮ワックス洗車ブラシ（12）。広告なしで売れた商品: 高見えレザードアポケット 2・3D足臭リセットブラシ 1・コードレスダブルミスト加湿器 2。
バリエーション別原価: ナノ 白緑（ピュアホワイト7）／黒桃（マットブラック2）・フック 黒（ブラック2）・ディスペンサー 3本（1）。"""
import csv, json, re, collections
D='2026-11-18'
PRICE={'裏起毛タッチ防寒グローブ':3980,'伸縮ガラスクリーナー':3980,'ナノガラス脱毛パッド':3980,'ワイド水切りワイパー':3980,'W固定スマホ車載ホルダー':3980,'マグネットドアクッション':3980,
 '快適マジックインソール':3980,'4-in-1マルチクリーナー':6980,'スマートノーズEMS美顔器':6980,'携帯電動シェーバー':4980,'360°マルチクリップ車載スマホホルダー':3980,
 'コードレスダブルミスト加湿器':4980,'高見えレザードアポケット':3980,'高見えレザーヘッドレストフック':3980,'壁掛けディスペンサー':6980,'3D足臭リセットブラシ':3980,
 'ポータブルヒートシーラー':3980,'優先配送':790}
STORE_GROSS, STORE_DISC, STORE_ORDERS, STORE_ITEMS = 382840, 14929, 64, 101
VIP_GIFT_QTY, RETURNED_QTY = 12, 0
SALES=[('伸縮ガラスクリーナー',63680,2388),('ワイド水切りワイパー',47760,1592),('W固定スマホ車載ホルダー',39800,1791),('快適マジックインソール',35820,3582),
 ('ナノガラス脱毛パッド',35820,796),('4-in-1マルチクリーナー',34900,1396),('スマートノーズEMS美顔器',27920,0),('360°マルチクリップ車載スマホホルダー',15920,0),
 ('マグネットドアクッション',15920,0),('携帯電動シェーバー',14940,0),('コードレスダブルミスト加湿器',9960,996),('高見えレザードアポケット',7960,796),
 ('裏起毛タッチ防寒グローブ',7960,796),('高見えレザーヘッドレストフック',7960,796),('壁掛けディスペンサー',6980,0),('3D足臭リセットブラシ',3980,0),
 ('ポータブルヒートシーラー',3980,0),('優先配送',1580,0)]
VAR=[('ナノガラス脱毛パッド','白緑',27860),('ナノガラス脱毛パッド','黒桃',7960),('高見えレザーヘッドレストフック','黒',7960),('壁掛けディスペンサー','3本',6980)]
def nm(t):
    s=re.sub(r'【[^】]*】','',t).strip(); s=re.sub(r'^(LOOTY|LOTTY)\s*','',s).strip()
    return {'コードレスパワーミスト加湿器':'コードレスダブルミスト加湿器'}.get(s,s)
O='scripts/daily/o1118/'
_raw=json.load(open(O+'sales_1118_raw.json'))['rows']
_rs={nm(t):(int(g),-int(dc)) for t,g,dc,_,_ in _raw if int(g)}
assert _rs=={n:(g,dc) for n,g,dc in SALES}, ('取得ファイルと一致しない', _rs)
assert not any(int(r) for *_,r in _raw), '返品あり'
_st=json.load(open(O+'store_1118_raw.json'))['rows'][0]
assert (int(_st[0]),-int(_st[1]),int(_st[2]),int(_st[3]),int(_st[4]))==(STORE_GROSS,STORE_DISC,STORE_ITEMS,0,STORE_ORDERS), _st
assert sum(int(r[3]) for r in _raw if r[0].startswith('VIP特典'))==VIP_GIFT_QTY
_var=collections.defaultdict(dict)
for t,v,g,_ in json.load(open(O+'var_1118_raw.json'))['rows']:
    if int(g): _var[nm(t)][v]=int(g)
assert _var['ナノガラス脱毛パッド']=={'ピュアホワイト':27860,'マットブラック':7960}, _var['ナノガラス脱毛パッド']
assert _var['高見えレザーヘッドレストフック']=={'ブラック':7960}
assert _var['壁掛けディスペンサー']=={'透明（Transparent）　3本セット':6980}, _var['壁掛けディスペンサー']
assert {n:sum(v.values()) for n,v in _var.items()}=={n:g for n,g,_ in SALES}, 'バリエーション別の合計が商品別と一致しない'
AD={}
for l in open(O+'meta_camp_1117_1118_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
_b=json.load(open(O+'bands_1118_raw.json'))['result']['data']
BANDS=(_b['all']['count'],_b['b7']['count'],_b['b8']['count'],_b['b10']['count']); assert BANDS==(64,14,5,5), BANDS
ACCT=sum(AD.values()); assert ACCT==197755, ACCT
existing=open('data/daily/daily_sales.csv').read()
assert f'\n{D},' not in existing, f'{D} 既に追記済み'
assert sum(g for _,g,_ in SALES)==STORE_GROSS, sum(g for _,g,_ in SALES)
assert sum(d for _,_,d in SALES)==STORE_DISC, sum(d for _,_,d in SALES)
assert all(g%PRICE[n]==0 for n,g,_ in SALES)
qty=sum(g//PRICE[n] for n,g,_ in SALES)
assert qty==89 and qty+VIP_GIFT_QTY==STORE_ITEMS+RETURNED_QTY, qty
for p in ('ナノガラス脱毛パッド','高見えレザーヘッドレストフック','壁掛けディスペンサー'):
    assert sum(a for m,a,_ in SALES if m==p)==sum(a for m,_,a in VAR if m==p)
assert BANDS[0]==STORE_ORDERS
with open('data/daily/daily_sales.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,g,d]) for n,g,d in SALES]
with open('data/daily/daily_ad.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,c]) for n,c in AD.items()]
with open('data/daily/daily_variant.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,v,g]) for n,v,g in VAR]
with open('data/daily/daily_order_bands.csv','a',newline='\n') as f:
    f.write(','.join([D]+[str(x) for x in BANDS])+'\n')
net=STORE_GROSS-STORE_DISC
print('appended',D,'実売',net,'広告',ACCT,'MER',round(net/ACCT,2),'注文',STORE_ORDERS, '広告キャンペーン', sorted(AD))
