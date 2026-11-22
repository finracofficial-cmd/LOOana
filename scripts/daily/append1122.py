# -*- coding: utf-8 -*-
"""2026-11-22(日・3連休の中日) をCSVへ追記。11/23 00時台に取得。広告費はキャンペーン合算（data_query fresh・1日ずつ・暫定。scripts/daily/o1122/meta_camp_1121_1122_raw.txt）。
数字は取得ファイル（o1122/*_raw.json・会話の記録からそのまま保存）から読む。このスクリプトに売上の数字は書かない。
当日の変更（ユーザー・budget-snapshots 2026-11-22a〜c）: 00時台 4-in-1 9,600→11,000・ノーズ v2 12,000→15,000・ドア 9,600→12,000／14:4x コードレス毛玉クリーナーv2 開始 8,000／15時台 UV歯ブラシ除菌器 v2 開始 8,000。
VIP特典の無料優先配送（gross 0円）は売上行に入れない。有料の優先配送 1件（790円）。返品なし。
広告費ありで売上0: カタログ全部（テスト）・フック v5・UV歯ブラシ除菌器 v2。広告なしで売れた商品: 壁掛けディスペンサー 1個（2本セット）・ファスナー修理キット 1個・高見えレザードアポケット 1個。
バリエーション別原価: ナノ 白緑（ピュアホワイト・セージグリーン）／黒桃（マットブラック・ベイビーピンク）・フック 黒（ブラック）／茶灰（ブラウン・グレー）・ディスペンサー 3本／2本。"""
import csv, json, re, collections
D='2026-11-22'; O='scripts/daily/o1122/'
nm=lambda t: re.sub(r'【[^】]*】','',t).replace('LOOTY','',1).strip()
raw=json.load(open(O+'sales_1122_raw.json'))['rows']
assert not any(int(r[4]) for r in raw), '返品あり'
SALES=[(nm(t),int(g),-int(dc),int(q)) for t,g,dc,q,_ in raw if int(g)]
VIP_GIFT_QTY=sum(int(r[3]) for r in raw if r[0].startswith('VIP特典'))
st=json.load(open(O+'store_1122_raw.json'))['rows'][0]
STORE_GROSS,STORE_DISC,STORE_ITEMS,STORE_RET,STORE_ORDERS=int(st[0]),-int(st[1]),int(st[2]),int(st[3]),int(st[4]); assert STORE_RET==0
assert sum(g for _,g,_,_ in SALES)==STORE_GROSS and sum(d for _,_,d,_ in SALES)==STORE_DISC
assert all(g%q==0 and (g//q==790 if n=='優先配送' else g//q in (3980,4980,5980,6980,7980,8980)) for n,g,_,q in SALES), SALES
assert sum(q for *_,q in SALES)+VIP_GIFT_QTY==STORE_ITEMS, (sum(q for *_,q in SALES),VIP_GIFT_QTY,STORE_ITEMS)
var=collections.defaultdict(dict)
for t,v,g,_ in json.load(open(O+'var_1122_raw.json'))['rows']:
    if int(g): var[nm(t)][v]=int(g)
assert {n:sum(v.values()) for n,v in var.items()}=={n:g for n,g,_,_ in SALES}, 'バリエーション別の合計が商品別と一致しない'
GRP={'ナノガラス脱毛パッド':{'ピュアホワイト':'白緑','セージグリーン':'白緑','マットブラック':'黒桃','ピンク':'黒桃','ローズピンク':'黒桃','ベイビーピンク':'黒桃'},'高見えレザーヘッドレストフック':{'ブラック':'黒','ブラウン':'茶灰','グレー':'茶灰'}}
VAR=[]
for p,m in GRP.items():
    acc=collections.OrderedDict()
    for v,g in var.get(p,{}).items(): acc[m[v]]=acc.get(m[v],0)+g
    VAR+=[(p,k,g) for k,g in acc.items()]
for v,g in var.get('壁掛けディスペンサー',{}).items():   # セットの本数で原価が違う（3本／2本）
    k=[x for x in ('3本','2本') if x+'セット' in v]; assert len(k)==1, v; VAR.append(('壁掛けディスペンサー',k[0],g))
for p in ('防風あったか裏起毛パンツ','すき間収納シートポケット'): assert p not in var, ('バリエーション別原価の商品が売れた: 追記の形を足す', p)
AD={}
for l in open(O+'meta_camp_1121_1122_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
b=json.load(open(O+'bands_vip_1122_raw.json'))['data']; BANDS=(b['all']['count'],b['b7']['count'],b['b8']['count'],b['b10']['count'])
assert all(b[k]['precision']=='EXACT' for k in ('all','b7','b8','b10')) and BANDS[0]==STORE_ORDERS, BANDS
ACCT=sum(AD.values())
existing=open('data/daily/daily_sales.csv').read(); assert f'\n{D},' not in existing, f'{D} 既に追記済み'
with open('data/daily/daily_sales.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,g,d]) for n,g,d,_ in SALES]
with open('data/daily/daily_ad.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,c]) for n,c in AD.items()]
with open('data/daily/daily_variant.csv','a',newline='') as f:
    w=csv.writer(f); [w.writerow([D,n,v,g]) for n,v,g in VAR]
with open('data/daily/daily_order_bands.csv','a',newline='\n') as f:
    f.write(','.join([D]+[str(x) for x in BANDS])+'\n')
net=STORE_GROSS-STORE_DISC
print('appended',D,'実売',net,'総額',STORE_GROSS,'値引',STORE_DISC,'広告',ACCT,'MER',round(net/ACCT,2),'注文',STORE_ORDERS,'個数',sum(q for *_,q in SALES),'VIP行',VIP_GIFT_QTY,'帯',BANDS)
print('VAR',VAR); print('広告キャンペーン', sorted(AD))
