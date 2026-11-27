# -*- coding: utf-8 -*-
"""2026-11-27(金) をCSVへ追記。11/28 04時台に取得。広告費はキャンペーン合算（data_query fresh・1日ずつ・暫定。scripts/daily/o1127/meta_camp_1126_1127_raw.txt）。
数字は取得ファイル（o1127/*_raw.json・会話の記録からそのまま保存）から読む。このスクリプトに売上の数字は書かない。
当日の変更（ユーザー・budget-snapshots 2026-11-27a〜d・EVENTS・Meta の変更履歴）: 00:17 W固定 -sab 10,400→8,500・ガラス主力 18,000→21,000・4-in-1 9,600→11,000／14:18 伸縮ワックス洗車ブラシ 停止／14:42 2WAY防眩サンバイザー 出稿（8,000）／21:52 クリア仕上げガラスクロス 出稿（8,000）。21:52 のあと予算の変更・停止は 0件（変更履歴・11/28 04:35 まで）。
VIP特典の無料優先配送（gross 0円）は売上行に入れない。有料の優先配送 2件（1,580円）。
返品: なし（全店の returns 0・返品の行なし）。
広告費ありで売上0: カタログ全部（テスト）・伸縮ワックス洗車ブラシ（14:18 の停止まで）・2WAY防眩サンバイザー・クリア仕上げガラスクロス。広告なしで売れた商品: 高見えレザーヘッドレストフック・充電式ダブルミスト卓上加湿器・すき間収納シートポケット。
バリエーション別原価: ナノ 白緑（ピュアホワイト・セージグリーン）／黒桃（マットブラック・ベイビーピンク）・フック 黒（ブラック）／茶灰（ブラウン・グレー）・ディスペンサー 3本／2本・すき間ポケット 標準（ベージュ・ブラック・ブラウン）／赤（レッド）。"""
import csv, json, re, collections
D='2026-11-27'; O='scripts/daily/o1127/'
nm=lambda t: re.sub(r'【[^】]*】','',t).replace('LOOTY','',1).strip()
raw=json.load(open(O+'sales_1127_raw.json'))['rows']
RET=[(nm(t),int(g),int(q),int(r)) for t,g,dc,q,r in raw if int(r)]   # 返品の行（商品の行はマイナス・商品名なしの行は同額のプラス）
assert RET==[], RET   # 11/27 は返品なし
RETQ=0
SALES=[(nm(t),int(g),-int(dc),int(q)) for t,g,dc,q,_ in raw if int(g)]
VIP_GIFT_QTY=sum(int(r[3]) for r in raw if r[0].startswith('VIP特典'))
st=json.load(open(O+'store_1127_raw.json'))['rows'][0]
STORE_GROSS,STORE_DISC,STORE_ITEMS,STORE_RET,STORE_ORDERS=int(st[0]),-int(st[1]),int(st[2]),int(st[3]),int(st[4]); assert STORE_RET==0
assert sum(g for _,g,_,_ in SALES)==STORE_GROSS and sum(d for _,_,d,_ in SALES)==STORE_DISC
assert all(g%q==0 and (g//q==790 if n=='優先配送' else g//q in (3980,4980,5980,6980,7980,8980)) for n,g,_,q in SALES), SALES
assert sum(q for *_,q in SALES)+VIP_GIFT_QTY-RETQ==STORE_ITEMS, (sum(q for *_,q in SALES),VIP_GIFT_QTY,RETQ,STORE_ITEMS)   # net_items_sold は返品の1個を引いた数
var=collections.defaultdict(dict)
for t,v,g,_ in json.load(open(O+'var_1127_raw.json'))['rows']:
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
for v,g in var.get('すき間収納シートポケット',{}).items():   # 色で原価が違う（レッドだけ 956・ほかは 760）
    assert v.split(' / ')[0] in ('ベージュ','ブラック','ブラウン','レッド'), v; VAR.append(('すき間収納シートポケット','赤' if v.startswith('レッド') else '標準',g))
for p in ('防風あったか裏起毛パンツ','クリア仕上げガラスクロス'): assert p not in var, ('バリエーション別原価の商品が売れた: 追記の形を足す', p)
AD={}
for l in open(O+'meta_camp_1126_1127_raw.txt'):
    if l.startswith(D+','):
        p=l.strip().split(',')
        if int(p[2]): AD[p[1]]=int(p[2])
b=json.load(open(O+'bands_vip_1127_raw.json'))['data']; BANDS=(b['all']['count'],b['b7']['count'],b['b8']['count'],b['b10']['count'])
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
